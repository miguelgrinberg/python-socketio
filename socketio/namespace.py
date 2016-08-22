import types

from . import util


class Namespace(object):
    """A container for a set of event handlers for a specific namespace.

    A method of this class named ``on_xxx`` is considered as the event handler
    for the event ``'xxx'`` in the namespace this class is registered to.

    There are also the following methods available that insert the current
    namespace automatically when none is given before they call their matching
    method of the ``Server`` instance:

    ``emit``, ``send``, ``enter_room``, ``leave_room``, ``close_room``,
    ``rooms``, ``disconnect``

    Example:

        from socketio import Namespace, Server

        class ChatNamespace(Namespace):
            def on_msg(self, sid, msg):
                # self.server references to the socketio.Server object
                data = "[%s]: %s" \
                       % (self.server.environ[sid].get("REMOTE_ADDR"), msg)
                # Note that we don't pass namespace="/chat" to the emit method.
                # It is done automatically for us.
                self.emit("msg", data, skip_sid=sid)
                return "received your message: %s" % msg

            # Here we set the event name explicitly by decorator.
            @Namespace.event_name("event name with spaces")
            def foo(self, sid):
                # ...

        sio = socketio.Server()
        sio.register_namespace("/chat", ChatNamespace)
    """

    def __init__(self, name, server):
        self.name = name
        self.server = server
        self.middlewares = []

        # wrap methods of Server object
        def get_wrapped_method(func_name):
            def wrapped_func(self, *args, **kwargs):
                """If namespace is None, it is automatically set to this
                object's one before the original method is called.
                """
                if kwargs.get('namespace') is None:
                    kwargs['namespace'] = self.name
                return getattr(self.server, func_name)(*args, **kwargs)
            return types.MethodType(wrapped_func, self)
        for func_name in ('emit', 'send', 'enter_room', 'leave_room',
                          'close_room', 'rooms', 'disconnect'):
            setattr(self, func_name, get_wrapped_method(func_name))

    def _get_event_handler(self, event_name):
        """Returns the event handler for given ``event`` in this namespace or
        ``None``, if none exists.

        :param event: The event name the handler is required for.
        """
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, '_sio_event_name'):
                _event_name = getattr(attr, '_sio_event_name')
            elif attr_name.startswith('on_'):
                _event_name = attr_name[3:]
            else:
                continue
            if _event_name == event_name:
                extra_middlewares = getattr(attr, '_sio_middlewares', [])
                return util._apply_middlewares(
                    self.middlewares + extra_middlewares, event_name,
                    self.name, attr)

    @staticmethod
    def event_name(name):
        """Decorator to overwrite event names:

            @Namespace.event_name("event name with spaces")
            def foo(self, sid, data):
                return "received: %s" % data

        Note that you must not add third-party decorators after the ones
        provided by this library because you'll otherwise loose metadata
        that this decorators create. You can add them before instead.
        """
        def wrapper(handler):
            def wrapped_handler(*args, **kwargs):
                return handler(*args, **kwargs)
            util._copy_sio_properties(handler, wrapped_handler)
            wrapped_handler._sio_event_name = name
            return wrapped_handler
        return wrapper
