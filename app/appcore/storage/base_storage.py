from abc import abstractmethod
from typing import List

from appcore.helpers.singleton import Singleton


@Singleton
class BaseStorage(object):
    @abstractmethod
    def DB_NAME(self):
        pass

    @abstractmethod
    def get(self, table: str, key: str = None) -> List[dict]:
        """
        Get by particular primary key, or all content if no key is provided
        """

    @abstractmethod
    def set(self, table: str, record: dict):
        """
        Set a new record in storage.
        Replace should get its own implementation-dependent method.
        """

    @abstractmethod
    def update(self, table: str, key: str, updates: dict):
        """
        Update existing key
        """

    @abstractmethod
    def search(self, table: str, query: dict) -> List[dict]:
        """
        Will parse the query dict into an implementation-specific query and return the results
        """

    @abstractmethod
    def delete(self, table: str, key: str) -> None:
        """
        Deletes a single record
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Runs a basic query ensuring the storage service is operative
        """
