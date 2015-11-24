from .base_manager import BaseManager


class PubSubManager(BaseManager):
    """Manage a client list attached to a pub/sub backend.

    This is a base class that enables multiple servers to share the list of
    clients, with the servers communicating events through a pub/sub backend.
    The use of a pub/sub backend also allows any client connected to the
    backend to emit events addressed to Socket.IO clients.

    The actual backends must be implemented by subclasses, this class only
    provides a pub/sub generic framework.

    :param channel: The channel name on which the server sends and receives
                    notifications.
    """
    def __init__(self, channel='socketio'):
        super(PubSubManager, self).__init__()
        self.channel = channel

    def initialize(self, server):
        super(PubSubManager, self).initialize(server)
        self.thread = self.server.start_background_task(self._thread)
        self.server.logger.info(self.name + ' backend initialized.')

    def emit(self, event, data, namespace=None, room=None, skip_sid=None,
             callback=None):
        """Emit a message to a single client, a room, or all the clients
        connected to the namespace.

        This method takes care or propagating the message to all the servers
        that are connected through the message queue.

        The parameters are the same as in :meth:`.Server.emit`.
        """
        self._publish({'method': 'emit', 'event': event, 'data': data,
                       'namespace': namespace or '/', 'room': room,
                       'skip_sid': skip_sid, 'callback': callback})

    def close_room(self, room, namespace=None):
        self._publish({'method': 'close_room', 'room': room,
                       'namespace': namespace or '/'})

    def _publish(self, data):
        """Publish a message on the Socket.IO channel.

        This method needs to be implemented by the different subclasses that
        support pub/sub backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')

    def _listen(self):
        """Return the next message published on the Socket.IO channel,
        blocking until a message is available.

        This method needs to be implemented by the different subclasses that
        support pub/sub backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')

    def _thread(self):
        for message in self._listen():
            if 'method' in message:
                if message['method'] == 'emit':
                    super(PubSubManager, self).emit(
                        message['event'], message['data'],
                        namespace=message.get('namespace'),
                        room=message.get('room'),
                        skip_sid=message.get('skip_sid'),
                        callback=message.get('callback'))
                elif message['method'] == 'close_room':
                    super(PubSubManager, self).close_room(
                        room=message.get('room'),
                        namespace=message.get('namespace'))
