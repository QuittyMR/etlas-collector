from appcore.helpers import constants
from appcore.helpers.singleton import Singleton
from appcore.helpers.strings import StringUtils
from appcore.services.base_service import BaseService
from appcore.storage.base_storage import BaseStorage


@Singleton
class Factory(BaseService):
    def get_config(self):
        """
        Instantiated at Bootstrap
        :rtype: backports.configparser.ConfigParser
        """
        return self._config

    def get_logger(self):
        """
        Instantiated at Bootstrap
        :rtype: logging.Logger
        """
        return self.logger

    def get_storage_service(self):
        from appcore.services.storage_service import StorageService
        return StorageService()

    def get_storage_client(self, client_type) -> BaseStorage:
        from appcore.storage import Redis
        client_types = {
            'redis': Redis
        }
        return client_types[client_type]()

    def get_execution_service(self):
        """
        :rtype: appcore.services.execution_service.ExecutionService
        """
        from appcore.services.execution_service import ExecutionService
        return ExecutionService()

    def get_platform_service(self):
        """
        :rtype: appcore.services.platforms_service.PlatformsService
        """
        from appcore.services.platforms_service import PlatformsService
        return PlatformsService()

    def get_platform(self, platform_id: str, platform_settings: dict):
        """
        :rtype: platforms.base_platform.BasePlatform
        """
        import importlib
        from copy import deepcopy

        adjusted_settings = deepcopy(platform_settings)

        for date_parameter in constants.DATE_PARAMETERS:
            if date_parameter in platform_settings:
                from appcore.helpers.dates import DateConverter
                adjusted_settings[date_parameter] = DateConverter.description_to_date(platform_settings[date_parameter])

        client = getattr(
            importlib.import_module('platforms.' + platform_id, package='app'),
            StringUtils.snake_to_camel(platform_id)
        )(**adjusted_settings)
        return client
