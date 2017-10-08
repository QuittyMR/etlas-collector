import pickle
from datetime import datetime

import rq

from appcore.helpers import constants, errors, Singleton
from appcore.services.base_service import BaseService
from appcore.services.factory import Factory


@Singleton
class ExecutionService(BaseService):
    def __init__(self):
        super(ExecutionService, self).__init__()
        self._queue = rq.Queue(constants.WORKER_QUEUE, connection=Factory().get_storage_client('redis')._client)

    def request_execution(self, platform_id: str, settings: dict, **kwargs):
        try:
            client = Factory().get_platform(platform_id, settings)
            return self._queue.enqueue(
                f=client.run,
                job_id='::'.join([datetime.now().isoformat(), kwargs.get('_id', 'manual'), platform_id])
            ).get_id()

        except AttributeError:
            raise errors.MissingPlatformError
        except TypeError as e:
            raise errors.PlatformInstantiationError(*e.args)

    def _get_job(self, job_id: str):
        """
        :rtype: rq.job.Job
        """
        return self._queue.fetch_job(job_id)

    def get_job_data(self, job_id: str, is_full: bool = False) -> dict:
        job_data = self._get_job(job_id)
        if job_data:
            job_data = job_data.to_dict(include_meta=True)
            job_data['meta'] = pickle.loads(job_data['meta'])
            del job_data['data']

            if not is_full:
                job_data = self._drop_intermediate_storage(job_data)

            return job_data
        else:
            raise NameError('Missing job')

    def _drop_intermediate_storage(self, job_data):
        for parameter in ['original', 'processed']:
            if parameter in job_data['meta']:
                del job_data['meta'][parameter]
        return job_data
