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
        self.namespace = namespace or '/'
        self.server = None

    def _set_server(self, server):
        self.server = server

    def is_asyncio_based(self):
        return False

    def trigger_event(self, event, *args):
        """Dispatch an event to the proper handler method.

        In the most common usage, this method is not overloaded by subclasses,
        as it performs the routing of events to methods. However, this
        method can be overriden if special dispatching rules are needed, or if
        having a single method that catches all events is desired.
        """
        handler_name = 'on_' + event
        if hasattr(self, handler_name):
            return getattr(self, handler_name)(*args)

    def emit(self, event, data=None, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Emit a custom event to one or more connected clients.

        The only difference with the :func:`socketio.Server.emit` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.emit(event, data=data, room=room, skip_sid=skip_sid,
                                namespace=namespace or self.namespace,
                                callback=callback)

    def send(self, data, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Send a message to one or more connected clients.

        The only difference with the :func:`socketio.Server.send` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.send(data, room=room, skip_sid=skip_sid,
                                namespace=namespace or self.namespace,
                                callback=callback)

    def enter_room(self, sid, room, namespace=None):
        """Enter a room.

        The only difference with the :func:`socketio.Server.enter_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.enter_room(sid, room,
                                      namespace=namespace or self.namespace)

    def leave_room(self, sid, room, namespace=None):
        """Leave a room.

        The only difference with the :func:`socketio.Server.leave_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.leave_room(sid, room,
                                      namespace=namespace or self.namespace)

    def close_room(self, room, namespace=None):
        """Close a room.

        The only difference with the :func:`socketio.Server.close_room` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.close_room(room,
                                      namespace=namespace or self.namespace)

    def rooms(self, sid, namespace=None):
        """Return the rooms a client is in.

        The only difference with the :func:`socketio.Server.rooms` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.rooms(sid, namespace=namespace or self.namespace)

    def disconnect(self, sid, namespace=None):
        """Disconnect a client.

        The only difference with the :func:`socketio.Server.disconnect` method
        is that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.disconnect(sid,
                                      namespace=namespace or self.namespace)
