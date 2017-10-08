from six import add_metaclass


class Singleton(object):

    def __new__(cls, *args):
        return add_metaclass(_InstanceStorage)(args[0])


class _InstanceStorage(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_InstanceStorage, cls).__call__(*args, **kwargs)

        return cls._instances[cls]

