from datetime import datetime
from os import path

import requests
from pandas import DataFrame, date_range
from pyquery import PyQuery

from platforms.base_platform import BasePlatform
from platforms.helpers.web import WebUtils


class PrivateScrapingPlatform1(BasePlatform):
    API_URL = 'http://some.url.com'
    ACTION_LOGIN = "route/login.php"
    ACTION_REPORT = "route/members.php"

    def __init__(self, username: str, password: str, multiplier: str, product_id: str, product: str,
                 start_date: datetime, end_date: datetime, storage: dict):
        super().__init__()
        STORAGE_OPTIONS = {
            'mysql': self._store_mysql,
            'mail': self._send_mail
        }
        self._username = username
        self._password = password
        self._multiplier = multiplier
        self._product_id = product_id
        self._product = product
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
        report_links = self._get_report_links()
        data = self._get_data(report_links)
        self.update('original', data.to_csv())
        return data

    def _process(self, data: DataFrame):
        currency_map = self.get_conversion_map('currency')
        data.rename(columns={
            'Searches': 'impressions',
            'Est. Gross Rev': 'gross_earnings',
            'market': 'country',
            'Bidded Searches': 'searches',
            'datestamp': 'source_date',
            'type_tag': 'channel'
        }, inplace=True)

        data['network_name'] = 'privateNetwork'
        data['revenue_type'] = 'search'
        data['product'] = self._product
        data['product_id'] = self._product_id

        self.update('processing', 'setting multiplier of ' + self._multiplier)
        data['gross_earnings'] = data['gross_earnings'].astype(float) * float(self._multiplier)

        self.update('processing', 'normalizing countries')
        data['country'] = data['country'].replace('UK', 'GB').str.lower()

        self.update('processing', 'extracting channels')
        data = data[data['channel'].str.contains('ORGANIC') == False]
        data['channel'] = self._regex(column=data['channel'], pattern=r'^.*(\d{8})_\d{2}$', fallback='99999999')
        data['channel'] = data['channel'].str.slice(0, 4) + '-' + data['channel'].str.slice(4)

        self.update('processing', 'converting currency')
        data['gross_earnings'] = data['gross_earnings'] / data['currency_code'].map(currency_map).astype(float)

        self.update('processing', 'completed')
        return data

    def _login(self):
        self.update('login', 'started')
        data = {
            'username': self._username,
            'password': self._password,
            'Submit': 'Login'
        }

        self._cookies = requests.request(
            method='POST',
            url=path.join(self.API_URL, self.ACTION_LOGIN),
            data=data,
            allow_redirects=False
        ).cookies

        if not self._cookies.get('PHPSESSID'):
            self.update('login', 'failed')
            raise Exception('cookie not returned')

        self.update('login', 'completed')

    def _get_report_links(self):
        self.update('availability', 'started')
        arguments = {
            'period': 'DAY',
            'type': 'detail',
            'subSourceGraph': 'Go',
            'dFrom': self.start_date.date().isoformat(),
            'dTo': self.end_date.date().isoformat()
        }

        response = requests.request(
            method='GET',
            url=path.join(self.API_URL, self.ACTION_REPORT),
            params=arguments,
            cookies=self._cookies
        ).text

        links = {
            link.text.split('_')[1].split('.')[0]: link.get('href')
            for link in PyQuery(response).xhtml_to_html()('tbody')('a') if link.text
        }

        try:
            return [links[date.date().isoformat()] for date in date_range(self.start_date, self.end_date)]
        except:
            self.update('available dates', '\n'.join(links.keys()))
            self.update('availability', 'failed')
            raise Exception()

    def _get_data(self, reports: list):
        records = []

        for report in reports:
            response = requests.request(
                method='GET',
                headers={'Accept-Encoding': 'gzip'},
                url=path.join(self.API_URL, 'extranet', report),
                cookies=self._cookies
            )

            records.extend(WebUtils.archive_to_records(response.content, 'gzip'))

        return DataFrame.from_records(records)
