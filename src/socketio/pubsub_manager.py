from functools import partial
import uuid

from engineio import json
import pickle

from .manager import Manager


class PubSubManager(Manager):
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
    name = 'pubsub'

    def __init__(self, channel='socketio', write_only=False, logger=None):
        super().__init__()
        self.channel = channel
        self.write_only = write_only
        self.host_id = uuid.uuid4().hex
        self.logger = logger

    def initialize(self):
        super().initialize()
        if not self.write_only:
            self.thread = self.server.start_background_task(self._thread)
        self._get_logger().info(self.name + ' backend initialized.')

    def emit(self, event, data, namespace=None, room=None, skip_sid=None,
             callback=None, to=None, **kwargs):
        """Emit a message to a single client, a room, or all the clients
        connected to the namespace.

        This method takes care or propagating the message to all the servers
        that are connected through the message queue.

        The parameters are the same as in :meth:`.Server.emit`.
        """
        room = to or room
        if kwargs.get('ignore_queue'):
            return super().emit(
                event, data, namespace=namespace, room=room, skip_sid=skip_sid,
                callback=callback)
        namespace = namespace or '/'
        if callback is not None:
            if self.server is None:
                raise RuntimeError('Callbacks can only be issued from the '
                                   'context of a server.')
            if room is None:
                raise ValueError('Cannot use callback without a room set.')
            id = self._generate_ack_id(room, callback)
            callback = (room, namespace, id)
        else:
            callback = None
        message = {'method': 'emit', 'event': event, 'data': data,
                   'namespace': namespace, 'room': room,
                   'skip_sid': skip_sid, 'callback': callback,
                   'host_id': self.host_id}
        self._handle_emit(message)  # handle in this host
        self._publish(message)  # notify other hosts

    def can_disconnect(self, sid, namespace):
        if self.is_connected(sid, namespace):
            # client is in this server, so we can disconnect directly
            return super().can_disconnect(sid, namespace)
        else:
            # client is in another server, so we post request to the queue
            message = {'method': 'disconnect', 'sid': sid,
                       'namespace': namespace or '/', 'host_id': self.host_id}
            self._handle_disconnect(message)  # handle in this host
            self._publish(message)  # notify other hosts

    def disconnect(self, sid, namespace=None, **kwargs):
        if kwargs.get('ignore_queue'):
            return super().disconnect(sid, namespace=namespace)
        message = {'method': 'disconnect', 'sid': sid,
                   'namespace': namespace or '/', 'host_id': self.host_id}
        self._handle_disconnect(message)  # handle in this host
        self._publish(message)  # notify other hosts

    def enter_room(self, sid, namespace, room, eio_sid=None):
        if self.is_connected(sid, namespace):
            # client is in this server, so we can add to the room directly
            return super().enter_room(sid, namespace, room, eio_sid=eio_sid)
        else:
            message = {'method': 'enter_room', 'sid': sid, 'room': room,
                       'namespace': namespace or '/', 'host_id': self.host_id}
            self._publish(message)  # notify other hosts

    def leave_room(self, sid, namespace, room):
        if self.is_connected(sid, namespace):
            # client is in this server, so we can remove from the room directly
            return super().leave_room(sid, namespace, room)
        else:
            message = {'method': 'leave_room', 'sid': sid, 'room': room,
                       'namespace': namespace or '/', 'host_id': self.host_id}
            self._publish(message)  # notify other hosts

    def close_room(self, room, namespace=None):
        message = {'method': 'close_room', 'room': room,
                   'namespace': namespace or '/', 'host_id': self.host_id}
        self._handle_close_room(message)  # handle in this host
        self._publish(message)  # notify other hosts

    def _publish(self, data):
        """Publish a message on the Socket.IO channel.

        This method needs to be implemented by the different subclasses that
        support pub/sub backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')  # pragma: no cover

    def _listen(self):
        """Return the next message published on the Socket.IO channel,
        blocking until a message is available.

        This method needs to be implemented by the different subclasses that
        support pub/sub backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')  # pragma: no cover

    def _handle_emit(self, message):
        # Events with callbacks are very tricky to handle across hosts
        # Here in the receiving end we set up a local callback that preserves
        # the callback host and id from the sender
        remote_callback = message.get('callback')
        remote_host_id = message.get('host_id')
        if remote_callback is not None and len(remote_callback) == 3:
            callback = partial(self._return_callback, remote_host_id,
                               *remote_callback)
        else:
            callback = None
        super().emit(message['event'], message['data'],
                     namespace=message.get('namespace'),
                     room=message.get('room'),
                     skip_sid=message.get('skip_sid'), callback=callback)

    def _handle_callback(self, message):
        if self.host_id == message.get('host_id'):
            try:
                sid = message['sid']
                id = message['id']
                args = message['args']
            except KeyError:
                return
            self.trigger_callback(sid, id, args)

    def _return_callback(self, host_id, sid, namespace, callback_id, *args):
        # When an event callback is received, the callback is returned back
        # to the sender, which is identified by the host_id
        if host_id == self.host_id:
            self.trigger_callback(sid, callback_id, args)
        else:
            self._publish({'method': 'callback', 'host_id': host_id,
                           'sid': sid, 'namespace': namespace,
                           'id': callback_id, 'args': args})

    def _handle_disconnect(self, message):
        self.server.disconnect(sid=message.get('sid'),
                               namespace=message.get('namespace'),
                               ignore_queue=True)

    def _handle_enter_room(self, message):
        sid = message.get('sid')
        namespace = message.get('namespace')
        if self.is_connected(sid, namespace):
            super().enter_room(sid, namespace, message.get('room'))

    def _handle_leave_room(self, message):
        sid = message.get('sid')
        namespace = message.get('namespace')
        if self.is_connected(sid, namespace):
            super().leave_room(sid, namespace, message.get('room'))

    def _handle_close_room(self, message):
        super().close_room(room=message.get('room'),
                           namespace=message.get('namespace'))

    def _thread(self):
        while True:
            try:
                for message in self._listen():
                    data = None
                    if isinstance(message, dict):
                        data = message
                    else:
                        if isinstance(message, bytes):  # pragma: no cover
                            try:
                                data = pickle.loads(message)
                            except:
                                pass
                        if data is None:
                            try:
                                data = json.loads(message)
                            except:
                                pass
                    if data and 'method' in data:
                        self._get_logger().debug('pubsub message: {}'.format(
                            data['method']))
                        try:
                            if data['method'] == 'callback':
                                self._handle_callback(data)
                            elif data.get('host_id') != self.host_id:
                                if data['method'] == 'emit':
                                    self._handle_emit(data)
                                elif data['method'] == 'disconnect':
                                    self._handle_disconnect(data)
                                elif data['method'] == 'enter_room':
                                    self._handle_enter_room(data)
                                elif data['method'] == 'leave_room':
                                    self._handle_leave_room(data)
                                elif data['method'] == 'close_room':
                                    self._handle_close_room(data)
                        except Exception:
                            self.server.logger.exception(
                                'Handler error in pubsub listening thread')
                self.server.logger.error('pubsub listen() exited unexpectedly')
                break  # loop should never exit except in unit tests!
            except Exception:  # pragma: no cover
                self.server.logger.exception('Unexpected Error in pubsub '
                                             'listening thread')
