def apply_interceptor(interceptor):
    """Returns a decorator for event handlers that adds the given
    interceptor to the handler decorated with it.

    :param interceptor: The interceptor to add

    Ensure that you only add well-behaving decorators after this one
    (meaning such that preserve attributes) because you'll loose them
    otherwise.
    """
    def wrapper(handler):
        if not hasattr(handler, '_sio_interceptors'):
            handler._sio_interceptors = []
        handler._sio_interceptors.append(interceptor)
        return handler
    return wrapper


def ignore_interceptor(interceptor):
    """Returns a decorator for event handlers that ignores the given
    interceptor for the handler decorated with it.

    :param interceptor: The interceptor to ignore

    Ensure that you only add well-behaving decorators after this one
    (meaning such that preserve attributes) because you'll loose them
    otherwise.
    """
    def wrapper(handler):
        if not hasattr(handler, '_sio_ignore_interceptors'):
            handler._sio_ignore_interceptors = []
        handler._sio_ignore_interceptors.append(interceptor)
        return handler
    return wrapper
