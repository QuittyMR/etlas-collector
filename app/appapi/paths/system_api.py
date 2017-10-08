from appcore.services import Factory
from bottle import request

from appapi.paths.base_api import BaseApi
from appcore.helpers.singleton import Singleton


@Singleton
class SystemApi(BaseApi):
    def __init__(self):
        super(BaseApi, self).__init__()

    def _path(self):
        return 'system'

    def alive(self):
        """
        GET,POST
        """
        if request.method == 'GET':
            return 'Alive'
        else:
            return self._dict_reply(200, {
                'Redis': Factory().get_storage_client('redis').is_connected()
            })
