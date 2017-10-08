from typing import List

from pymongo import MongoClient
from pymongo.database import Database

from appcore.helpers.singleton import Singleton
from appcore.storage.base_storage import BaseStorage


@Singleton
class Mongo(BaseStorage):
    DB_NAME = 'etlas'
    QUERIES = {
        'active and scheduled': {
            'schedule': {
                '$ne': None
            },
            'is_active': True
        }
    }

    def __init__(self) -> None:
        super(Mongo, self).__init__()
        from appcore.services.factory import Factory
        self._client = self._connect_to_mongo(dict(Factory().get_config().items('mongo')))

    def _connect_to_mongo(self, config: dict) -> Database:
        return MongoClient(**config).get_database(self.DB_NAME)

    def get(self, table: str, key: str = None) -> List[dict]:
        if key:
            return list(self._client[table].find({'_id': key}))
        else:
            return list(self._client[table].find())

    def set(self, table: str, record: dict):
        return self._client[table].insert_one(record)

    def update(self, table: str, key: str, updates: dict):
        """
        :param updates: only supports complete top-level members
        """
        return self._client[table].update_one({'_id': key}, {'$set': updates}, upsert=False)

    def search(self, table: str, query: dict = None):
        return list(self._client[table].find(query))

    def delete(self, table: str, key: str):
        return self._client[table].delete_one({'_id': key}).raw_result['n'] == 1

    def is_connected(self):
        return self._client.collection_names(False) is not None
