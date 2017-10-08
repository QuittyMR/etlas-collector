from bottle import Bottle, static_file, response

from appapi.paths import *
from appcore.helpers.singleton import Singleton
from appcore.models.errors import MissingRouteData
from appcore.services.base_service import BaseService


@Singleton
class App(object):
    def __init__(self):
        """
        BaseService adds caching, logging and configuration.
        Refer to BaseApi for instructions on adding routes to your API. 
        """
        self._methods = 'OPTIONS,GET,POST,PUT,DELETE'
        self.app = BaseService()
        self._allowed_domain = self.app._config.get('cors', 'allowed_domain')
        self._api_sources = BaseApi.__subclasses__()

    def run(self):
        server = Bottle()

        # Route UI and static content
        server.route('/<filepath:path>', callback=self._serve_static)
        server.route('/', callback=lambda: self._serve_static('/index.html'))

        # CORS
        server.add_hook('after_request', self._add_cors_headers)
        server.route('/<any:path>', method='OPTIONS', callback=self._add_cors_headers)

        for source in self._api_sources:
            self._register_routes(server, source)

        server.run(**dict(self.app._config.items('server')))

    def _register_routes(self, server, source):
        """
        Registers all public methods as routes
        :param server: server instance 
        :param source: subclass of BaseApi 
        """
        api = source()

        for route_name in [member for member in dir(api) if not member.startswith('_')]:
            route = api.__getattribute__(route_name)

            try:
                doc_tag_methods = map(str.strip, route.__doc__.upper().split(','))
            except AttributeError:
                raise MissingRouteData(source.__name__)

            methods = [method for method in doc_tag_methods if method in self._methods]
            server.route('/{path}/{route}'.format(path=api._path(), route=route_name), method=methods, callback=route)

    def _serve_static(self, filepath):
        return static_file(filepath, './dist/')

    def _add_cors_headers(self, *args, **kwargs):
        response.headers['Access-Control-Allow-Origin'] = self._allowed_domain
        response.headers['Access-Control-Allow-Methods'] = self._methods
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type'
