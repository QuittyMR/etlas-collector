class MissingRouteData(AttributeError):
    def __init__(self, message):
        super(MissingRouteData, self).__init__(
            'in {route}. Please refer to the BaseApi class for instructions on adding routes'.format(
                route=message)
        )
