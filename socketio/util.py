def _copy_sio_properties(from_func, to_func):
    """Copies all properties starting with ``'_sio'`` from one function to
    another."""
    for key in dir(from_func):
        if key.startswith('_sio'):
            setattr(to_func, key, getattr(from_func, key))

def _apply_middlewares(middlewares, event, namespace, handler):
    """Wraps the given handler with a wrapper that executes middlewares
    before and after the real event handler."""
    if not middlewares:
        return handler

    def wrapped(*args):
        _middlewares = []
        for middleware in middlewares:
            if isinstance(middleware, type):
                _middlewares.append(middleware())
            else:
                _middlewares.append(middleware)

        for middleware in _middlewares:
            if hasattr(middleware, 'before_event'):
                result = middleware.before_event(event, namespace, args)
                if result is not None:
                    return result

        result = handler(*args)
        if result is None:
            data = []
        elif isinstance(result, tuple):
            data = list(result)
        else:
            data = [result]

        for middleware in reversed(_middlewares):
            if hasattr(middleware, 'after_event'):
                result = middleware.after_event(event, namespace, data)
                if result is not None:
                    return result

        return tuple(data)

    return wrapped

def apply_middleware(middleware):
    """Returns a decorator for event handlers that adds the given
    middleware to the handler decorated with it.

    :param middleware: The middleware to add

    Note that you must not add third-party decorators after the ones
    provided by this library because you'll otherwise loose metadata
    that this decorators create. You can add them before instead.
    """
    def wrapper(handler):
        if not hasattr(handler, '_sio_middlewares'):
            handler._sio_middlewares = []
        handler._sio_middlewares.append(middleware)
        return handler
    return wrapper
