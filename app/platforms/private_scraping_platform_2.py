from datetime import datetime
from hashlib import md5

import requests
from pandas import DataFrame

from .base_platform import BasePlatform


class PrivateScrapingPlatform2(BasePlatform):
    API_URL = 'http://api.url'
    ACTION_REPORT = 'routePage.php'

    def __init__(self, username: str, password: str, start_date: datetime, end_date: datetime, storage: dict):
        super().__init__()
        STORAGE_OPTIONS = {
            'mysql': self._store_mysql,
            'mail': self._send_mail
        }
        self._username = username
        self._password = md5(password.encode()).hexdigest()
        self.start_date = start_date
        self.end_date = end_date
        self._store = STORAGE_OPTIONS[storage['type']]
        self._storage_settings = storage['settings']

    def _run(self):
        data = self._fetch()
        data = self._process(data)
        self._store(data, self._storage_settings)
        return True

    def _fetch(self):
        self._login()
        data = self._get_data()
        self.update('original', data.to_csv())
        return data

    def _process(self, data: DataFrame):
        country_map = self.get_conversion_map('country', fallback='__')
        data['tracking_channel'] = 'NA'
        data['impressions'] = -1
        data['network_name'] = 'privateNetwork'

        self.update('processing', 'verifying channels')
        data['channel'] = self._regex(column=data['channel'], pattern=r'^(\d{4}-\d{4})$', fallback='9999-9999')

        self.update('processing', 'extracting countries')
        data['country'] = self._regex(
            column=data['country'],
            pattern=r'^.*> (.*)$',
            fallback='__'
        ).map(country_map)

        data.rename(columns={
            'total_price': 'spend',
            'total_leads': 'postbacks'
        }, inplace=True)

        self.update('processing', 'completed')
        return data

    def _login(self):
        self.update('login', 'started')
        data = {
            'si_mail': self._username,
            'si_password': self._password,
            'signin': 'Sign In'
        }

        self._cookies = requests.request(
            method='POST',
            url=self.API_URL,
            data=data,
            allow_redirects=False
        ).cookies

        if not self._cookies.get('PHPSESSID'):
            self.update('login', 'failed')
            raise Exception('cookie not returned')

        self.update('login', 'completed')

    def _get_data(self):
        self.update('data retrieval', 'started')
        data_columns = [
            'source_date',
            'channel',
            'country',
            'chrome_leads',
            'firefox_leads',
            'ie_leads',
            'other_leads',
            'total_leads',
            'average_price',
            'total_price'
        ]

        params = {
            'iDisplayStart': '0',
            'iDisplayLength': '1000',
            'date_from': self.start_date.date().isoformat(),
            'date_to': self.end_date.date().isoformat(),
            'global_time_zone': '0',
            'channels': '',
            'countries': '',
            'columns': ','.join([
                'date_earned',
                'channel',
                'country',
                'fired_s2s',
                'price'
            ])
        }

        request_url = '/'.join([self.API_URL, self.ACTION_REPORT])
        response = requests.request('GET', url=request_url, params=params, cookies=self._cookies)

        try:
            data = DataFrame.from_records(response.json()['aaData'], columns=data_columns, coerce_float=True)
            return data[data['source_date'] != 'Total']
        except:
            self.update('data retrieval', 'failed')
            raise Exception('No valid JSON')
