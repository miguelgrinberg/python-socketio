class Namespace(object):
    """Base class for class-based namespaces.

    A class-based namespace is a class that contains all the event handlers
    for a Socket.IO namespace. The event handlers are methods of the class
    with the prefix ``on_``, such as ``on_connect``, ``on_disconnect``,
    ``on_message``, ``on_json``, and so on.

    :param namespace: The Socket.IO namespace to be used with all the event
                      handlers defined in this class. If this argument is
                      omitted, the default namespace is used.
    """
    def __init__(self, namespace=None):
        self.name = namespace or '/'
        self.server = None
        self.interceptors = []
        self.ignore_interceptors = []

    def _set_server(self, server):
        self.server = server

    def emit(self, event, data=None, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Emit a custom event to one or more connected clients.

        The only difference with the :func:`socketio.Server.emit` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.emit(event, data=data, room=room, skip_sid=skip_sid,
                                namespace=namespace or self.name,
                                callback=callback)

    def send(self, data, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Send a message to one or more connected clients.

        The only difference with the :func:`socketio.Server.send` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.send(data, room=room, skip_sid=skip_sid,
                                namespace=namespace or self.name,
                                callback=callback)

    def enter_room(self, sid, room, namespace=None):
        """Enter a room.

        The only difference with the :func:`socketio.Server.enter_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.enter_room(sid, room,
                                      namespace=namespace or self.name)

    def leave_room(self, sid, room, namespace=None):
        """Leave a room.

        The only difference with the :func:`socketio.Server.leave_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.leave_room(sid, room,
                                      namespace=namespace or self.name)

    def close_room(self, room, namespace=None):
        """Close a room.

        The only difference with the :func:`socketio.Server.close_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.close_room(room,
                                      namespace=namespace or self.name)

    def rooms(self, sid, namespace=None):
        """Return the rooms a client is in.

        The only difference with the :func:`socketio.Server.rooms` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.rooms(sid, namespace=namespace or self.name)

    def disconnect(self, sid, namespace=None):
        """Disconnect a client.

        The only difference with the :func:`socketio.Server.disconnect` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.disconnect(sid,
                                      namespace=namespace or self.name)

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
                return attr

    @staticmethod
    def event_name(name):
        """Decorator to overwrite event names:

            @Namespace.event_name("event name with spaces")
            def foo(self, sid, data):
                return "received: %s" % data

        Ensure that you only add well-behaving decorators after this one
        (meaning such that preserve attributes) because you'll loose them
        otherwise.
        """
        def wrapper(handler):
            handler._sio_event_name = name
            return handler
        return wrapper
