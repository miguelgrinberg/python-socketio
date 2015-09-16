import logging

import engineio
import six

from . import base_manager
from . import packet


class Server(object):
    """A Socket.IO server.

    This class implements a fully compliant Socket.IO web server with support
    for websocket and long-polling transports.

    :param client_manager: The client manager instance that will manage the
                           client list. By default the client list is stored
                           in an in-memory structure, which prevents the use
                           of multiple worker processes.
    :param logger: To enable logging set to ``True`` or pass a logger object to
                   use. To disable logging set to ``False``.
    :param binary: ``True`` to support binary payloads, ``False`` to treat all
                   payloads as text. On Python 2, if this is set to ``True``,
                   ``unicode`` values are treated as text, and ``str`` and
                   ``bytes`` values are treated as binary.  This option has no
                   effect on Python 3, where text and binary payloads are
                   always automatically discovered.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have ``dumps`` and ``loads``
                 functions that are compatible with the standard library
                 versions.
    :param kwargs: Connection parameters for the underlying Engine.IO server.

    The Engine.IO configuration supports the following settings:

    :param async_mode: The library used for asynchronous operations. Valid
                       options are "threading", "eventlet" and "gevent". If
                       this argument is not given, "eventlet" is tried first,
                       then "gevent", and finally "threading". The websocket
                       transport is only supported in "eventlet" mode.
    :param ping_timeout: The time in seconds that the client waits for the
                         server to respond before disconnecting.
    :param ping_interval: The interval in seconds at which the client pings
                          the server.
    :param max_http_buffer_size: The maximum size of a message when using the
                                 polling transport.
    :param allow_upgrades: Whether to allow transport upgrades or not.
    :param http_compression: Whether to compress packages when using the
                             polling transport.
    :param compression_threshold: Only compress messages when their byte size
                                  is greater than this value.
    :param cookie: Name of the HTTP cookie that contains the client session
                   id. If set to ``None``, a cookie is not sent to the client.
    :param cors_allowed_origins: List of origins that are allowed to connect
                                 to this server. All origins are allowed by
                                 default.
    :param cors_credentials: Whether credentials (cookies, authentication) are
                             allowed in requests to this server.
    :param engineio_logger: To enable Engine.IO logging set to ``True`` or pass
                            a logger object to use. To disable logging set to
                            ``False``.
    """
    def __init__(self, client_manager=None, logger=False, binary=False,
                 json=None, **kwargs):
        if client_manager is None:
            client_manager = base_manager.BaseManager(self)
        self.manager = client_manager
        engineio_options = kwargs
        engineio_logger = engineio_options.pop('engineio_logger', None)
        if engineio_logger is not None:
            engineio_options['logger'] = engineio_logger
        if json is not None:
            packet.Packet.json = json
            engineio_options['json'] = json
        self.eio = engineio.Server(**engineio_options)
        self.eio.on('connect', self._handle_eio_connect)
        self.eio.on('message', self._handle_eio_message)
        self.eio.on('disconnect', self._handle_eio_disconnect)
        self.binary = binary

        self.environ = {}
        self.handlers = {}

        self._binary_packet = None
        self._attachment_count = 0
        self._attachments = []

        if not isinstance(logger, bool):
            self.logger = logger
        else:
            self.logger = logging.getLogger('socketio')
            if not logging.root.handlers and \
                    self.logger.level == logging.NOTSET:
                if logger:
                    self.logger.setLevel(logging.INFO)
                else:
                    self.logger.setLevel(logging.ERROR)
                self.logger.addHandler(logging.StreamHandler())

    def on(self, event, handler=None, namespace=None):
        """Register an event handler.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param handler: The function that should be invoked to handle the
                        event. When this parameter is not given, the method
                        acts as a decorator for the handler function.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the handler is associated with
                          the default namespace.

        Example usage::

            # as a decorator:
            @socket_io.on('connect', namespace='/chat')
            def connect_handler(sid, environ):
                print('Connection request')
                if environ['REMOTE_ADDR'] in blacklisted:
                    return False  # reject

            # as a method:
            def message_handler(sid, msg):
                print('Received message: ', msg)
                eio.send(sid, 'response')
            socket_io.on('message', namespace='/chat', message_handler)

        The handler function receives the ``sid`` (session ID) for the
        client as first argument. The ``'connect'`` event handler receives the
        WSGI environment as a second argument, and can return ``False`` to
        reject the connection. The ``'message'`` handler and handlers for
        custom event names receive the message payload as a second argument.
        Any values returned from a message handler will be passed to the
        client's acknowledgement callback function if it exists. The
        ``'disconnect'`` handler does not take a second argument.
        """
        namespace = namespace or '/'

        def set_handler(handler):
            if namespace not in self.handlers:
                self.handlers[namespace] = {}
            self.handlers[namespace][event] = handler
            return handler

        if handler is None:
            return set_handler
        set_handler(handler)

    def emit(self, event, data=None, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Emit a custom event to one or more connected clients.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. If a
                     ``list`` or ``dict``, the data will be serialized as JSON.
        :param room: The recipient of the message. This can be set to the
                     session ID of a client to address that client's room, or
                     to any custom room created by the application, If this
                     argument is omitted the event is broadcasted to all
                     connected clients.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        """
        namespace = namespace or '/'
        self.logger.info('emitting event "%s" to %s [%s]', event,
                         room or 'all', namespace)
        self.manager.emit(event, data, namespace, room, skip_sid, callback)

    def send(self, data, room=None, skip_sid=None, namespace=None,
             callback=None):
        """Send a message to one or more connected clients.

        This function emits an event with the name ``'message'``. Use
        :func:`emit` to issue custom event names.

        :param data: The data to send to the client or clients. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. If a
                     ``list`` or ``dict``, the data will be serialized as JSON.
        :param room: The recipient of the message. This can be set to the
                     session ID of a client to address that client's room, or
                     to any custom room created by the application, If this
                     argument is omitted the event is broadcasted to all
                     connected clients.
        :param skip_sid: The session ID of a client to skip when broadcasting
                         to a room or to all clients. This can be used to
                         prevent a message from being sent to the sender.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the client has received the message. The arguments
                         that will be passed to the function are those provided
                         by the client. Callback functions can only be used
                         when addressing an individual client.
        """
        self.emit('message', data, room, skip_sid, namespace, callback)

    def enter_room(self, sid, room, namespace=None):
        """Enter a room.

        This function adds the client to a room. The :func:`emit` and
        :func:`send` functions can optionally broadcast events to all the
        clients in a room.

        :param sid: Session ID of the client.
        :param room: Room name. If the room does not exist it is created.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        self.logger.info('%s is entering room %s [%s]', sid, room, namespace)
        self.manager.enter_room(sid, namespace, room)

    def leave_room(self, sid, room, namespace=None):
        """Leave a room.

        This function removes the client from a room.

        :param sid: Session ID of the client.
        :param room: Room name.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        self.logger.info('%s is leaving room %s [%s]', sid, room, namespace)
        self.manager.leave_room(sid, namespace, room)

    def close_room(self, room, namespace=None):
        """Close a room.

        This function removes all the clients from the given room.

        :param room: Room name.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        self.logger.info('room %s is closing [%s]', room, namespace)
        self.manager.close_room(namespace, room)

    def rooms(self, sid, namespace=None):
        """Return the rooms a client is in.

        :param sid: Session ID of the client.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        return self.manager.get_rooms(sid, namespace)

    def disconnect(self, sid, namespace=None):
        """Disconnect a client.

        :param sid: Session ID of the client.
        :param namespace: The Socket.IO namespace to disconnect. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        self.logger.info('Disconnecting %s [%s]', sid, namespace)
        self._send_packet(sid, packet.Packet(packet.DISCONNECT,
                                             namespace=namespace))
        self._trigger_event('disconnect', namespace, sid)
        self.manager.disconnect(sid, namespace=namespace)

    def transport(self, sid):
        """Return the name of the transport used by the client.

        The two possible values returned by this function are ``'polling'``
        and ``'websocket'``.

        :param sid: The session of the client.
        """
        return self.eio.transport(sid)

    def handle_request(self, environ, start_response):
        """Handle an HTTP request from the client.

        This is the entry point of the Socket.IO application, using the same
        interface as a WSGI application. For the typical usage, this function
        is invoked by the :class:`Middleware` instance, but it can be invoked
        directly when the middleware is not used.

        :param environ: The WSGI environment.
        :param start_response: The WSGI ``start_response`` function.

        This function returns the HTTP response body to deliver to the client
        as a byte sequence.
        """
        return self.eio.handle_request(environ, start_response)

    def _emit_internal(self, sid, event, data, namespace=None, id=None):
        """Send a message to a client."""
        if six.PY2 and not self.binary:
            binary = False  # pragma: nocover
        else:
            binary = None
        self._send_packet(sid, packet.Packet(packet.EVENT, namespace=namespace,
                                             data=[event, data], id=id,
                                             binary=binary))

    def _send_packet(self, sid, pkt):
        """Send a Socket.IO packet to a client."""
        encoded_packet = pkt.encode()
        if isinstance(encoded_packet, list):
            binary = False
            for ep in encoded_packet:
                self.eio.send(sid, ep, binary=binary)
                binary = True
        else:
            self.eio.send(sid, encoded_packet, binary=False)

    def _handle_connect(self, sid, namespace):
        """Handle a client connection request."""
        namespace = namespace or '/'
        self.manager.connect(sid, namespace)
        if self._trigger_event('connect', namespace, sid,
                               self.environ[sid]) is False:
            self.manager.disconnect(sid, namespace)
            self._send_packet(sid, packet.Packet(packet.ERROR,
                                                 namespace=namespace))
        else:
            self._send_packet(sid, packet.Packet(packet.CONNECT,
                                                 namespace=namespace))

    def _handle_disconnect(self, sid, namespace):
        """Handle a client disconnect."""
        namespace = namespace or '/'
        if namespace == '/':
            namespace_list = list(self.manager.get_namespaces())
        else:
            namespace_list = [namespace]
        for n in namespace_list:
            if n != '/' and self.manager.is_connected(sid, n):
                self._trigger_event('disconnect', n, sid)
                self.manager.disconnect(sid, n)
        if namespace == '/' and self.manager.is_connected(sid, namespace):
            self._trigger_event('disconnect', '/', sid)
            self.manager.disconnect(sid, '/')
            if sid in self.environ:
                del self.environ[sid]

    def _handle_event(self, sid, namespace, id, data):
        """Handle an incoming client event."""
        namespace = namespace or '/'
        self.logger.info('received event "%s" from %s [%s]', data[0], sid,
                         namespace)
        r = self._trigger_event(data[0], namespace, sid, *data[1:])
        if id is not None:
            # send ACK packet with the response returned by the handler
            if isinstance(r, tuple):
                data = list(r)
            elif isinstance(r, list):
                data = r
            else:
                data = [r]
            if six.PY2 and not self.binary:
                binary = False  # pragma: nocover
            else:
                binary = None
            self._send_packet(sid, packet.Packet(packet.ACK,
                                                 namespace=namespace,
                                                 id=id, data=data,
                                                 binary=binary))

    def _handle_ack(self, sid, namespace, id, data):
        """Handle ACK packets from the client."""
        namespace = namespace or '/'
        self.logger.info('received ack from %s [%s]', sid, namespace)
        self.manager.trigger_callback(sid, namespace, id, data)

    def _trigger_event(self, event, namespace, *args):
        """Invoke an application event handler."""
        if namespace in self.handlers and event in self.handlers[namespace]:
            return self.handlers[namespace][event](*args)

    def _handle_eio_connect(self, sid, environ):
        """Handle the Engine.IO connection event."""
        self.environ[sid] = environ
        self._handle_connect(sid, '/')

    def _handle_eio_message(self, sid, data):
        """Dispatch Engine.IO messages."""
        if self._attachment_count > 0:
            self._attachments.append(data)
            self._attachment_count -= 1

            if self._attachment_count == 0:
                self._binary_packet.reconstruct_binary(self._attachments)
                if self._binary_packet.packet_type == packet.BINARY_EVENT:
                    self._handle_event(sid, self._binary_packet.namespace,
                                       self._binary_packet.id,
                                       self._binary_packet.data)
                else:
                    self._handle_ack(sid, self._binary_packet.namespace,
                                     self._binary_packet.id,
                                     self._binary_packet.data)
                self._binary_packet = None
                self._attachments = []
        else:
            pkt = packet.Packet(encoded_packet=data)
            if pkt.packet_type == packet.CONNECT:
                self._handle_connect(sid, pkt.namespace)
            elif pkt.packet_type == packet.DISCONNECT:
                self._handle_disconnect(sid, pkt.namespace)
            elif pkt.packet_type == packet.EVENT:
                self._handle_event(sid, pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.ACK:
                self._handle_ack(sid, pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.BINARY_EVENT or \
                    pkt.packet_type == packet.BINARY_ACK:
                self._binary_packet = pkt
                self._attachments = []
                self._attachment_count = pkt.attachment_count
            elif pkt.packet_type == packet.ERROR:
                raise ValueError('Unexpected ERROR packet.')
            else:
                raise ValueError('Unknown packet type.')

    def _handle_eio_disconnect(self, sid):
        """Handle Engine.IO disconnect event."""
        self._handle_disconnect(sid, '/')
