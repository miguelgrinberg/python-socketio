def apply_middleware(middleware):
    """Returns a decorator for event handlers that adds the given
    middleware to the handler decorated with it.

    :param middleware: The middleware to add

    Ensure that you only add well-behaving decorators after this one
    (meaning such that preserve attributes) because you'll loose them
    otherwise.
    """
    def wrapper(handler):
        if not hasattr(handler, '_sio_middlewares'):
            handler._sio_middlewares = []
        handler._sio_middlewares.append(middleware)
        return handler
    return wrapper
