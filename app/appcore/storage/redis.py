from typing import List

from appcore.helpers.singleton import Singleton
from appcore.storage.base_storage import BaseStorage


@Singleton
class Redis(BaseStorage):
    def __init__(self) -> None:
        super(Redis, self).__init__()
        from appcore.services.factory import Factory
        self._config = dict(Factory().get_config().items('redis'))
        self.DB_NAME = self._config['db']
        self._client = self._connect_to_redis()

    def _connect_to_redis(self):
        import redis
        return redis.Redis(**self._config)

    def set(self, table: str = None, record: dict = None):
        if table:
            return self._client.hset(table, tuple(record.keys())[0], tuple(record.values())[0])
        else:
            return self._client.set(tuple(record.keys())[0], tuple(record.values())[0])

    def search(self, table: str, query: dict) -> List[dict]:
        yield ({key: self.get('', key)} for key in self._client.keys(query['pattern']))

    def get(self, table: str = None, key: str = None) -> List[dict]:
        if table:
            if key:
                return self._client.hget(table, key)
            else:
                return self._client.hgetall(table)
        else:
            return self._client.get(key)

    def delete(self, table: str, key: str):
        return self._client.delete(key)

    def is_connected(self):
        return self._client.keys() is not None
