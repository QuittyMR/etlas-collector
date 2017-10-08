import logging
import sys

from backports.configparser import ConfigParser
from os import listdir

from appcore.helpers import constants
from appcore.helpers.singleton import Singleton


@Singleton
class Bootstrap(object):
    def __init__(self):
        self._date_parameters = ['start_date', 'end_date', 'date']
        self._config = self._populate_config()
        self.logger = self._set_up_logging()
        self._worker_pid = self._run_worker()

    def _set_up_logging(self):
        logging.basicConfig(
            stream=sys.stdout,
            level=self._config.get('logging', 'level').upper(),
            format='::'.join([
                '%(name)s',
                '%(asctime)s',
                '%(levelname)s',
                '%(module)s.%(funcName)s',
                '%(message)s'
            ])
        )
        return logging

    def _populate_config(self) -> ConfigParser:
        config = ConfigParser()
        config_path = './resources/config.ini'

        if 'resources' not in listdir('.'):
            config_path = '.' + config_path

        with open(config_path) as file_pointer:
            config.read_file(file_pointer)

        return config

    def _run_worker(self) -> int:
        from subprocess import Popen
        if self._config.get('logging', 'level').lower() == 'debug':
            print('Skipping worker triggering')
            return 0

        arguments = [
            './bin/rq',
            'worker',
            constants.WORKER_QUEUE,
            '--name',
            'jobber',
            '--url',
            'redis://{host}/{db}'.format(**dict(self._config.items('redis')))
        ]

        pid = Popen(arguments).pid
        print('Worker PID: ' + str(pid))
        return pid
