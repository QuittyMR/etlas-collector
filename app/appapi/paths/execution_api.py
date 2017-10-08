from bottle import request

from appapi.paths.base_api import BaseApi
from appcore.helpers import PlatformInstantiationError
from appcore.helpers.singleton import Singleton
from appcore.services.factory import Factory


# noinspection PyUnresolvedReferences
@Singleton
class ExecutionApi(BaseApi):
    def _path(self):
        return 'execution'

    def run(self):
        """
        POST
        """
        try:
            account_settings = request.json
            return self._dict_reply(200, {
                'job_id': Factory().get_execution_service().request_execution(**account_settings)
            })

        except PlatformInstantiationError as e:
            print(e.args)
            return self._dict_reply(400, 'Missing parameters in request: ' + ', '.join(e.args))
        except (ModuleNotFoundError, AssertionError):
            return self._dict_reply(400, 'Missing or invalid platform_id')
        except Exception as e:
            print(e.args)
            return self._dict_reply(500, 'Execution threw a ' + str(e.__class__) + 'error')

    def get(self):
        """
        GET
        """
        try:
            job = Factory().get_execution_service().get_job_data(
                job_id=request.GET.get('job_id'),
                is_full='full' in request.GET
            )
            return self._dict_reply(200, job)
        except NameError as e:
            return self._dict_reply(400, e.message)
        except Exception as e:
            return self._dict_reply(500, ', '.join([getattr(e, 'message', ''), ', '.join(e.args)]))
