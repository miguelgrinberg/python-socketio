import logging

from . import manager
from . import base_namespace
from . import packet

default_logger = logging.getLogger('socketio.server')


class BaseServer:
    reserved_events = ['connect', 'disconnect']

    def __init__(self, client_manager=None, logger=False, serializer='default',
                 json=None, async_handlers=True, always_connect=False,
                 namespaces=None, **kwargs):
        engineio_options = kwargs
        engineio_logger = engineio_options.pop('engineio_logger', None)
        if engineio_logger is not None:
            engineio_options['logger'] = engineio_logger
        if serializer == 'default':
            self.packet_class = packet.Packet
        elif serializer == 'msgpack':
            from . import msgpack_packet
            self.packet_class = msgpack_packet.MsgPackPacket
        else:
            self.packet_class = serializer
        if json is not None:
            self.packet_class.json = json
            engineio_options['json'] = json
        engineio_options['async_handlers'] = False
        self.eio = self._engineio_server_class()(**engineio_options)
        self.eio.on('connect', self._handle_eio_connect)
        self.eio.on('message', self._handle_eio_message)
        self.eio.on('disconnect', self._handle_eio_disconnect)

        self.environ = {}
        self.handlers = {}
        self.namespace_handlers = {}
        self.not_handled = object()

        self._binary_packet = {}

        if not isinstance(logger, bool):
            self.logger = logger
        else:
            self.logger = default_logger
            if self.logger.level == logging.NOTSET:
                if logger:
                    self.logger.setLevel(logging.INFO)
                else:
                    self.logger.setLevel(logging.ERROR)
                self.logger.addHandler(logging.StreamHandler())

        if client_manager is None:
            client_manager = manager.Manager()
        self.manager = client_manager
        self.manager.set_server(self)
        self.manager_initialized = False

        self.async_handlers = async_handlers
        self.always_connect = always_connect
        self.namespaces = namespaces or ['/']

        self.async_mode = self.eio.async_mode

    def is_asyncio_based(self):
        return False

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
            @sio.on('connect', namespace='/chat')
            def connect_handler(sid, environ):
                print('Connection request')
                if environ['REMOTE_ADDR'] in blacklisted:
                    return False  # reject

            # as a method:
            def message_handler(sid, msg):
                print('Received message: ', msg)
                sio.send(sid, 'response')
            socket_io.on('message', namespace='/chat', handler=message_handler)

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

    def event(self, *args, **kwargs):
        """Decorator to register an event handler.

        This is a simplified version of the ``on()`` method that takes the
        event name from the decorated function.

        Example usage::

            @sio.event
            def my_event(data):
                print('Received data: ', data)

        The above example is equivalent to::

            @sio.on('my_event')
            def my_event(data):
                print('Received data: ', data)

        A custom namespace can be given as an argument to the decorator::

            @sio.event(namespace='/test')
            def my_event(data):
                print('Received data: ', data)
        """
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # the decorator was invoked without arguments
            # args[0] is the decorated function
            return self.on(args[0].__name__)(args[0])
        else:
            # the decorator was invoked with arguments
            def set_handler(handler):
                return self.on(handler.__name__, *args, **kwargs)(handler)

            return set_handler

    def register_namespace(self, namespace_handler):
        """Register a namespace handler object.

        :param namespace_handler: An instance of a :class:`Namespace`
                                  subclass that handles all the event traffic
                                  for a namespace.
        """
        if not isinstance(namespace_handler,
                          base_namespace.BaseServerNamespace):
            raise ValueError('Not a namespace instance')
        if self.is_asyncio_based() != namespace_handler.is_asyncio_based():
            raise ValueError('Not a valid namespace class for this server')
        namespace_handler._set_server(self)
        self.namespace_handlers[namespace_handler.namespace] = \
            namespace_handler

    def rooms(self, sid, namespace=None):
        """Return the rooms a client is in.

        :param sid: Session ID of the client.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the default namespace is used.
        """
        namespace = namespace or '/'
        return self.manager.get_rooms(sid, namespace)

    def transport(self, sid):
        """Return the name of the transport used by the client.

        The two possible values returned by this function are ``'polling'``
        and ``'websocket'``.

        :param sid: The session of the client.
        """
        return self.eio.transport(sid)

    def get_environ(self, sid, namespace=None):
        """Return the WSGI environ dictionary for a client.

        :param sid: The session of the client.
        :param namespace: The Socket.IO namespace. If this argument is omitted
                          the default namespace is used.
        """
        eio_sid = self.manager.eio_sid_from_sid(sid, namespace or '/')
        return self.environ.get(eio_sid)

    def _handle_eio_connect(self):  # pragma: no cover
        raise NotImplementedError()

    def _handle_eio_message(self, data):  # pragma: no cover
        raise NotImplementedError()

    def _handle_eio_disconnect(self):  # pragma: no cover
        raise NotImplementedError()

    def _engineio_server_class(self):  # pragma: no cover
        raise NotImplementedError('Must be implemented in subclasses')
