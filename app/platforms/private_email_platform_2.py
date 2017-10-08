from datetime import datetime
from io import StringIO

from pandas import DataFrame, read_csv, to_datetime

from platforms.base_platform import BasePlatform


class PrivatePlatform2(BasePlatform):
    MAIL_CONFIG = {
        'host': 'imap.gmail.com',
        'user': 'emailUser',
        'password': 'emailPass',
        'sender': 'mailSender',
        'subject': 'mail subject'
    }
    MULTIPLIER = 0.88

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
        self._is_mac = 'mac' in storage['settings']['table']

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

    def _process(self, data: DataFrame):
        data.rename(columns={
            'Type Tag': 'channel',
            'Gross Rev': 'gross_earnings',
            'Searches': 'searches',
            'Days': 'source_date',
            'Country': 'country'
        }, inplace=True)

        data['network_name'] = 'privateNetwork'
        data['revenue_type'] = 'Search'
        data['product'] = self._product
        data['product_id'] = self._product_id

        self.update('processing', 'filtering campaigns')
        data = data[data['channel'].str.contains('rvmc', case=False) == self._is_mac]

        self.update('processing', 'setting multiplier of ' + str(self.MULTIPLIER))
        data['net_earnings'] = data['gross_earnings'].astype(float) * self.MULTIPLIER

        if not self._is_mac:
            self._ppc_processing(data)

        self.update('processing', 'converting dates')
        data['source_date'] = to_datetime(data['source_date'], format='%m/%d/%Y').astype(str)

        self.update('processing', 'normalizing countries')
        data['country'] = data['country'].str.lower()

        self.update('processing', 'completed')
        return data

    def _extract_data(self, message):
        return read_csv(StringIO(message.get_payload(decode=True).decode()))

    def _ppc_processing(self, data):
        # TODO: Change column names in table and get rid of this
        data.rename(columns={
            'gross_earnings': 'gross_revenue',
            'net_earnings': 'net_revenue'
        }, inplace=True)
        data['campaign'] = data['Feed'] + '::' + data['channel']

        self.update('processing', 'extracting channels')
        data['channel'] = self._regex(column=data['channel'], pattern=r'^.*_?(\d{8})$', fallback='99999999')
        data['channel'] = data['channel'].str.slice(0, 4) + '-' + data['channel'].str.slice(4)
