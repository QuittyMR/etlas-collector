import pickle

from appcore.services import Factory
from platforms.base_platform import BasePlatform
from platforms.helpers.mysql_connection import MysqlConnection


class CountryMapUpdate(BasePlatform):
    API_URL = 'my.sql.server'

    DB_SETTINGS = {
        'hostname': API_URL,
        'username': 'db_user',
        'password': 'db_pass',
        'db': 'db_schema',
        'table': 'countries'
    }

    def _run(self):
        country_map = self._fetch()
        self._store(country_map)
        return True

    def _fetch(self):
        self.update('pull', 'started')
        with MysqlConnection(**self.DB_SETTINGS) as connection:
            countries = connection.execute(
                'select country_name, country_code from ' + self.DB_SETTINGS['table']
            ).fetchall()

        self.update('pull', 'completed')

        country_map = {country[0].lower(): country[1].lower() for country in countries}
        return country_map

    def _store(self, country_map):
        self.update('store', 'attempted')
        Factory().get_storage_client('redis').set('maps', record={'country': pickle.dumps(country_map)})
