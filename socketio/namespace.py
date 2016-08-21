import types


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
        sio = socketio.Server()
        sio.register_namespace("/chat", ChatNamespace)
    """

    def __init__(self, name, server):
        self.name = name
        self.server = server

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

    def _get_handlers(self):
        """Returns a dict of event names and handlers this namespace
        provides."""
        handlers = {}
        for attr_name in dir(self):
            if attr_name.startswith('on_'):
                handlers[attr_name[3:]] = getattr(self, attr_name)
        return handlers
