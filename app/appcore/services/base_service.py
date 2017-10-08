from appcore.helpers.singleton import Singleton
from appcore.services.bootstrap import Bootstrap


@Singleton
class BaseService(object):
    def __init__(self):
        self._date_parameters = ['start_date', 'end_date', 'date']
        app = Bootstrap()
        self.__dict__.update(app.__dict__)
