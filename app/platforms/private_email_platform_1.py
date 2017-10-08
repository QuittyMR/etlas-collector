from datetime import datetime
from io import StringIO

from pandas import DataFrame, read_csv

from platforms.base_platform import BasePlatform


class PrivatePlatform1(BasePlatform):
    MAIL_CONFIG = {
        'host': 'imap.gmail.com',
        'user': 'emailUser',
        'password': 'emailPass',
        'sender': 'mailSender',
        'subject': 'mail subject'
    }

    def __init__(self, date: datetime, storage: dict, product: str = 'NA', product_id: str = '9999.0'):
        super().__init__()
        STORAGE_OPTIONS = {
            'mysql': self._store_mysql
        }
        self._product_id = product_id
        self._product = product
        self.date = date
        self._store = STORAGE_OPTIONS[storage['type']]
        self._storage_settings = storage['settings']

    def _run(self):
        data = self._fetch()

        if not isinstance(data, DataFrame):
            return False

        data = self._process(data)
        self._store(data, self._storage_settings)
        return True

    def _fetch(self):
        mailbox = self._get_mailbox()
        uids = self._search_mailbox(mailbox)

        if len(uids) > 1:
            self.update('warning', 'using the latest of multiple matching messages')

        for payload in self._get_message(mailbox, max(uids)).get_payload():
            if payload.get_filename():
                mailbox.logout()
                return self._extract_data(payload)

        mailbox.logout()
        return None

    def _extract_data(self, message):
        return read_csv(StringIO(message.get_payload(decode=True).decode()))

    def _process(self, data: DataFrame):
        data.rename(columns={
            'AppID': 'channel',
            'Gross_Revenue': 'gross_earnings',
            'company_rev': 'net_earnings',
            'DATE': 'source_date',
            'CountryCode': 'country'
        }, inplace=True)

        data['network_name'] = 'privateNetwork'
        data['revenue_type'] = 'Search'
        data['product'] = self._product
        data['product_id'] = self._product_id

        self.update('processing', 'extracting channels')
        data = data[data['channel'] > 8080]
        data['channel'] = data['channel'].astype(str)
        data['channel'] = data['channel'].str.slice(0, 4) + '-' + data['channel'].str.slice(4)

        self.update('processing', 'normalizing countries')
        data['country'] = data['country'].str.lower()

        self.update('processing', 'completed')
        return data
