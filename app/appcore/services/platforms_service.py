import importlib
import inspect
import os

from appcore.helpers.singleton import Singleton
from appcore.helpers.strings import StringUtils
from appcore.services.base_service import BaseService
from appcore.services.factory import Factory


@Singleton
class PlatformsService(BaseService):
    def get_platforms(self) -> dict:
        platforms_path = Factory().get_config().get('platforms', 'class_storage')
        platforms = {}

        for filename in os.listdir(platforms_path):
            is_platform = all([
                os.path.isfile(os.path.join(platforms_path, filename)),
                not (filename.startswith('base_') or filename.startswith('_'))
            ])

            if is_platform:
                name = filename.replace('.py', '')
                class_name = StringUtils.snake_to_camel(name)

                platform_module = getattr(importlib.import_module('platforms.' + name, package='app'), class_name)
                inspection = self._reflect_platform_settings(platform_module)

                platforms[name] = {
                    'display_name': class_name,
                    'settings': inspection
                }

        return platforms

    def _reflect_platform_settings(self, platform_module) -> dict:
        """
        :return: types and defaults for all of the platform's required settings
        """
        inspection = inspect.getfullargspec(platform_module.__init__)

        if inspection.defaults:
            defaults = dict(zip(reversed(inspection.args), reversed(inspection.defaults)))
        else:
            defaults = {}

        inspection = inspection.annotations

        for parameter in inspection.keys():
            inspection[parameter] = {
                'type': inspection[parameter].__name__,
                'default': defaults.get(parameter, None)
            }

        return inspection
