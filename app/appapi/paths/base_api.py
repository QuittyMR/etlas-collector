import json
from abc import ABCMeta, abstractmethod

from bottle import response
from six import add_metaclass

from appcore.helpers.singleton import Singleton
from appcore.services.factory import Factory

@Singleton
@add_metaclass(ABCMeta)
class BaseApi(object):
    """
    Every API path class should inherit from this interface-class, and imported in paths/__init__.py .
    Each public method you define there will become an api route in the path returned by _path() .
    The docstring for each method should contain only a comma-separated list of the methods supported by the route.   
    Missing or erroneous methods will be discarded (method will be regarded as 'GET' if no methods are found)
    """
    @abstractmethod
    def _path(self):
        """
        URL subpath for the routes contained in this file. 
        Example: http://www.domain.com/<_path>/...
        """

    def _dict_reply(self, status_code: int, message=None):
        if 200 <= status_code < 400:
            reply = {'status': 'Success'}
        else:
            reply = {'status': 'Failed'}
            print(message)

        if message:
            reply['message'] = message

        response.status = status_code
        response.content_type = 'application/json'
        return json.dumps(reply)

    def _csv_reply(self, data):
        response.content_type = 'text/csv'
        response.add_header('Content-Disposition', 'attachment')
        return Factory().get_storage_service().get_csv(data)
