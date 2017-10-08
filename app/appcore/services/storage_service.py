import csv
from typing import List

from appcore.helpers.singleton import Singleton
from appcore.services.base_service import BaseService


@Singleton
class StorageService(BaseService):

    def get_csv(self, data: List[dict]) -> str:
        if len(data) == 0:
            return ''

        output = csv.StringIO()
        writer = csv.DictWriter(output, data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        output.seek(0)

        return output.read()
