class AppError(Exception):
    @property
    def default_message(self):
        raise NotImplementedError

    def __init__(self, message: str = '') -> None:
        super(AppError, self).__init__(message)
        self._message = message

    def __str__(self):
        message = self.default_message
        if self._message:
            message += ':  ' + self._message
        return '{message}\n\n'.format(message=message)


class FailedParsingDate(AppError):
    default_message = "Failed trying to parse the date. Please check your language"


class MissingPlatformError(AppError):
    default_message = 'Requested platform could not be found'


class PlatformInstantiationError(AppError):
    default_message = 'Could not instantiate platform with given settings'
