import pickle
from os import path

import requests

from appcore.services import Factory
from platforms.base_platform import BasePlatform


class CurrencyMapUpdate(BasePlatform):
    MULTIPLIER = 0.95
    # Reliable and limited
    API_URL = 'http://api.fixer.io'
    ACTION_REQUEST = 'latest'

    # Versatile and fishy
    SECONDARY_API_URL = 'http://free.currencyconverterapi.com'
    SECONDARY_ACTION_REQUEST = 'api/v3/convert'

    def __init__(self, currencies: list):
        super().__init__()
        self._currencies = currencies

    def _run(self):
        currency_map = self._fetch()
        self._store(currency_map)
        return True

    def _fetch(self):
        self.update('pull', 'started')
        currency_map = self._get_conversion_rates(self._currencies)
        self.update('pull', 'completed')
        return currency_map

    def _get_conversion_rates(self, currencies: list) -> dict:
        arguments = {
            'base': 'USD'
        }

        conversion_rates = requests.request(
            method='GET',
            url=path.join(self.API_URL, self.ACTION_REQUEST),
            params=arguments
        ).json()['rates']

        for currency in filter(lambda currency: currency not in conversion_rates.keys(), currencies):
            conversion_rates[currency.lower()] = self._get_secondary_conversion_rate(currency)

        lowercase = {key.lower(): value * self.MULTIPLIER for key, value in conversion_rates.items()}
        lowercase['usd'] = 1.0

        return lowercase

    def _get_secondary_conversion_rate(self, currency: str) -> float:
        conversion_key = 'USD_' + currency
        arguments = {
            'q': conversion_key,
            'compact': 'ultra'
        }

        return float(requests.request(
            method='GET',
            url=path.join(self.SECONDARY_API_URL, self.SECONDARY_ACTION_REQUEST),
            params=arguments
        ).json()[conversion_key])

    def _store(self, country_map):
        self.update('store', 'attempted')
        Factory().get_storage_client('redis').set('maps', record={'currency': pickle.dumps(country_map)})
        self.update('store', 'completed')
