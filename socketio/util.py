def _simple_decorator(decorator):
    """This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @_simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.

    Also preserves all properties starting with ``'_sio'``.
    """
    def copy_attrs(a, b):
        """Copies attributes from a to b."""
        for attr_name in ('__name__', '__doc__'):
            if hasattr(a, attr_name):
                setattr(b, attr_name, getattr(a, attr_name))
        if hasattr(a, '__dict__') and hasattr(b, '__dict__'):
            b.__dict__.update(a.__dict__)

    def new_decorator(f):
        g = decorator(f)
        copy_attrs(f, g)
        return g

    # Now a few lines needed to make _simple_decorator itself
    # be a well-behaved decorator.
    copy_attrs(decorator, new_decorator)
    return new_decorator


def apply_middleware(middleware):
    """Returns a decorator for event handlers that adds the given
    middleware to the handler decorated with it.

    :param middleware: The middleware to add

    Ensure that you only add well-behaving decorators after this one
    (meaning such that preserve attributes) because you'll loose them
    otherwise.
    """
    @_simple_decorator
    def wrapper(handler):
        if not hasattr(handler, '_sio_middlewares'):
            handler._sio_middlewares = []
        handler._sio_middlewares.append(middleware)
        return handler
    return wrapper
