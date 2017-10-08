from appapi.paths.base_api import BaseApi
from appcore.helpers.singleton import Singleton
from appcore.services.factory import Factory


@Singleton
class PlatformsApi(BaseApi):
    def _path(self):
        return 'platforms'

    def get(self):
        """
        GET
        """
        try:
            return self._dict_reply(200, Factory().get_platform_service().get_platforms())
        except Exception as e:
            print(e.args)
            return self._dict_reply(500, 'Execution threw a ' + str(e.__class__) + 'error')
