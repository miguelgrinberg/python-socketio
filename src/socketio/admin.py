from datetime import datetime
import functools
import os
import socket
import time
from urllib.parse import parse_qs
from .exceptions import ConnectionRefusedError

HOSTNAME = socket.gethostname()
PID = os.getpid()


class EventBuffer:
    def __init__(self):
        self.buffer = {}

    def push(self, type, count=1):
        timestamp = int(time.time()) * 1000
        key = '{};{}'.format(timestamp, type)
        if key not in self.buffer:
            self.buffer[key] = {
                'timestamp': timestamp,
                'type': type,
                'count': count,
            }
        else:
            self.buffer[key]['count'] += count

    def get_and_clear(self):
        buffer = self.buffer
        self.buffer = {}
        return [value for value in buffer.values()]


class InstrumentedServer:
    def __init__(self, sio, auth=None, mode='development', read_only=False,
                 server_id=None, namespace='/admin', server_stats_interval=2):
        """Instrument the Socket.IO server for monitoring with the `Socket.IO
        Admin UI <https://socket.io/docs/v4/admin-ui/>`_.
        """
        if auth is None:
            raise ValueError('auth must be specified')
        self.sio = sio
        self.auth = auth
        self.admin_namespace = namespace
        self.read_only = read_only
        self.server_id = server_id or (
            self.sio.manager.host_id if hasattr(self.sio.manager, 'host_id')
            else HOSTNAME
        )
        self.mode = mode
        self.server_stats_interval = server_stats_interval
        self.event_buffer = EventBuffer()

        # task that emits "server_stats" every 2 seconds
        self.stop_stats_event = None
        self.stats_task = None

        # monkey-patch the server to report metrics to the admin UI
        self.instrument()

    def instrument(self):
        self.sio.on('connect', self.admin_connect,
                    namespace=self.admin_namespace)

        if self.mode == 'development':
            if not self.read_only:  # pragma: no branch
                self.sio.on('emit', self.admin_emit,
                            namespace=self.admin_namespace)
                self.sio.on('join', self.admin_enter_room,
                            namespace=self.admin_namespace)
                self.sio.on('leave', self.admin_leave_room,
                            namespace=self.admin_namespace)
                self.sio.on('_disconnect', self.admin_disconnect,
                            namespace=self.admin_namespace)

            # track socket connection times
            self.sio.manager._timestamps = {}

            # report socket.io connections
            self.sio.manager.__connect = self.sio.manager.connect
            self.sio.manager.connect = self._connect

            # report socket.io disconnection
            self.sio.manager.__disconnect = self.sio.manager.disconnect
            self.sio.manager.disconnect = self._disconnect

            # report join rooms
            self.sio.manager.__basic_enter_room = \
                self.sio.manager.basic_enter_room
            self.sio.manager.basic_enter_room = self._basic_enter_room

            # report leave rooms
            self.sio.manager.__basic_leave_room = \
                self.sio.manager.basic_leave_room
            self.sio.manager.basic_leave_room = self._basic_leave_room

            # report emit events
            self.sio.manager.__emit = self.sio.manager.emit
            self.sio.manager.emit = self._emit

            # report receive events
            self.sio.__handle_event_internal = self.sio._handle_event_internal
            self.sio._handle_event_internal = self._handle_event_internal

        # report engine.io connections
        self.sio.eio.on('connect', self._handle_eio_connect)
        self.sio.eio.on('disconnect', self._handle_eio_disconnect)

        # report polling packets
        from engineio.socket import Socket
        self.sio.eio.__ok = self.sio.eio._ok
        self.sio.eio._ok = self._eio_http_response
        Socket.__handle_post_request = Socket.handle_post_request
        Socket.handle_post_request = functools.partialmethod(
            self.__class__._eio_handle_post_request, self)

        # report websocket packets
        Socket.__websocket_handler = Socket._websocket_handler
        Socket._websocket_handler = functools.partialmethod(
            self.__class__._eio_websocket_handler, self)

        # report connected sockets with each ping
        if self.mode == 'development':
            Socket.__send_ping = Socket._send_ping
            Socket._send_ping = functools.partialmethod(
                self.__class__._eio_send_ping, self)

    def uninstrument(self):  # pragma: no cover
        if self.mode == 'development':
            self.sio.manager.connect = self.sio.manager.__connect
            self.sio.manager.disconnect = self.sio.manager.__disconnect
            self.sio.manager.basic_enter_room = \
                self.sio.manager.__basic_enter_room
            self.sio.manager.basic_leave_room = \
                self.sio.manager.__basic_leave_room
            self.sio.manager.emit = self.sio.manager.__emit
            self.sio._handle_event_internal = self.sio.__handle_event_internal
        self.sio.eio._ok = self.sio.eio.__ok

        from engineio.socket import Socket
        Socket.handle_post_request = Socket.__handle_post_request
        Socket._websocket_handler = Socket.__websocket_handler
        if self.mode == 'development':
            Socket._send_ping = Socket.__send_ping

    def admin_connect(self, sid, environ, client_auth):
        if self.auth:
            authenticated = False
            if isinstance(self.auth, dict):
                authenticated = client_auth == self.auth
            elif isinstance(self.auth, list):
                authenticated = client_auth in self.auth
            else:
                authenticated = self.auth(client_auth)
            if not authenticated:
                raise ConnectionRefusedError('authentication failed')

        def config(sid):
            self.sio.sleep(0.1)

            # supported features
            features = ['AGGREGATED_EVENTS']
            if not self.read_only:
                features += ['EMIT', 'JOIN', 'LEAVE', 'DISCONNECT', 'MJOIN',
                             'MLEAVE', 'MDISCONNECT']
            if self.mode == 'development':
                features.append('ALL_EVENTS')
            self.sio.emit('config', {'supportedFeatures': features},
                          to=sid, namespace=self.admin_namespace)

            # send current sockets
            if self.mode == 'development':
                all_sockets = []
                for nsp in self.sio.manager.get_namespaces():
                    for sid, eio_sid in self.sio.manager.get_participants(
                            nsp, None):
                        all_sockets.append(
                            self.serialize_socket(sid, nsp, eio_sid))
                self.sio.emit('all_sockets', all_sockets, to=sid,
                              namespace=self.admin_namespace)

        self.sio.start_background_task(config, sid)

    def admin_emit(self, _, namespace, room_filter, event, *data):
        self.sio.emit(event, data, to=room_filter, namespace=namespace)

    def admin_enter_room(self, _, namespace, room, room_filter=None):
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            self.sio.enter_room(sid, room, namespace=namespace)

    def admin_leave_room(self, _, namespace, room, room_filter=None):
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            self.sio.leave_room(sid, room, namespace=namespace)

    def admin_disconnect(self, _, namespace, close, room_filter=None):
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            self.sio.disconnect(sid, namespace=namespace)

    def shutdown(self):
        if self.stats_task:  # pragma: no branch
            self.stop_stats_event.set()
            self.stats_task.join()

    def _connect(self, eio_sid, namespace):
        sid = self.sio.manager.__connect(eio_sid, namespace)
        t = time.time()
        self.sio.manager._timestamps[sid] = t
        serialized_socket = self.serialize_socket(sid, namespace, eio_sid)
        self.sio.emit('socket_connected', (
            serialized_socket,
            datetime.utcfromtimestamp(t).isoformat() + 'Z',
        ), namespace=self.admin_namespace)
        return sid

    def _disconnect(self, sid, namespace, **kwargs):
        del self.sio.manager._timestamps[sid]
        self.sio.emit('socket_disconnected', (
            namespace,
            sid,
            'N/A',
            datetime.utcnow().isoformat() + 'Z',
        ), namespace=self.admin_namespace)
        return self.sio.manager.__disconnect(sid, namespace, **kwargs)

    def _check_for_upgrade(self, eio_sid, sid, namespace):  # pragma: no cover
        for _ in range(5):
            self.sio.sleep(5)
            try:
                if self.sio.eio._get_socket(eio_sid).upgraded:
                    self.sio.emit('socket_updated', {
                        'id': sid,
                        'nsp': namespace,
                        'transport': 'websocket',
                    }, namespace=self.admin_namespace)
                    break
            except KeyError:
                pass

    def _basic_enter_room(self, sid, namespace, room, eio_sid=None):
        ret = self.sio.manager.__basic_enter_room(sid, namespace, room,
                                                  eio_sid)
        if room:
            self.sio.emit('room_joined', (
                namespace,
                room,
                sid,
                datetime.utcnow().isoformat() + 'Z',
            ), namespace=self.admin_namespace)
        return ret

    def _basic_leave_room(self, sid, namespace, room):
        if room:
            self.sio.emit('room_left', (
                namespace,
                room,
                sid,
                datetime.utcnow().isoformat() + 'Z',
            ), namespace=self.admin_namespace)
        return self.sio.manager.__basic_leave_room(sid, namespace, room)

    def _emit(self, event, data, namespace, room=None, skip_sid=None,
              callback=None, **kwargs):
        ret = self.sio.manager.__emit(event, data, namespace, room=room,
                                      skip_sid=skip_sid, callback=callback,
                                      **kwargs)
        if namespace != self.admin_namespace:
            event_data = [event] + list(data) if isinstance(data, tuple) \
                else [data]
            if not isinstance(skip_sid, list):  # pragma: no branch
                skip_sid = [skip_sid]
            for sid, _ in self.sio.manager.get_participants(namespace, room):
                if sid not in skip_sid:
                    self.sio.emit('event_sent', (
                        namespace,
                        sid,
                        event_data,
                        datetime.utcnow().isoformat() + 'Z',
                    ), namespace=self.admin_namespace)
        return ret

    def _handle_event_internal(self, server, sid, eio_sid, data, namespace,
                               id):
        ret = self.sio.__handle_event_internal(server, sid, eio_sid, data,
                                               namespace, id)
        self.sio.emit('event_received', (
            namespace,
            sid,
            data,
            datetime.utcnow().isoformat() + 'Z',
        ), namespace=self.admin_namespace)
        return ret

    def _handle_eio_connect(self, eio_sid, environ):
        if self.stop_stats_event is None:
            self.stop_stats_event = self.sio.eio.create_event()
            self.stats_task = self.sio.start_background_task(
                self._emit_server_stats)

        self.event_buffer.push('rawConnection')
        return self.sio._handle_eio_connect(eio_sid, environ)

    def _handle_eio_disconnect(self, eio_sid):
        self.event_buffer.push('rawDisconnection')
        return self.sio._handle_eio_disconnect(eio_sid)

    def _eio_http_response(self, packets=None, headers=None, jsonp_index=None):
        ret = self.sio.eio.__ok(packets=packets, headers=headers,
                                jsonp_index=jsonp_index)
        self.event_buffer.push('packetsOut')
        self.event_buffer.push('bytesOut', len(ret['response']))
        return ret

    def _eio_handle_post_request(socket, self, environ):
        ret = socket.__handle_post_request(environ)
        self.event_buffer.push('packetsIn')
        self.event_buffer.push(
            'bytesIn', int(environ.get('CONTENT_LENGTH', 0)))
        return ret

    def _eio_websocket_handler(socket, self, ws):
        def _send(ws, data, *args, **kwargs):
            self.event_buffer.push('packetsOut')
            self.event_buffer.push('bytesOut', len(data))
            return ws.__send(data, *args, **kwargs)

        def _wait(ws):
            ret = ws.__wait()
            self.event_buffer.push('packetsIn')
            self.event_buffer.push('bytesIn', len(ret or ''))
            return ret

        ws.__send = ws.send
        ws.send = functools.partial(_send, ws)
        ws.__wait = ws.wait
        ws.wait = functools.partial(_wait, ws)
        return socket.__websocket_handler(ws)

    def _eio_send_ping(socket, self):  # pragma: no cover
        eio_sid = socket.sid
        t = time.time()
        for namespace in self.sio.manager.get_namespaces():
            sid = self.sio.manager.sid_from_eio_sid(eio_sid, namespace)
            if sid:
                serialized_socket = self.serialize_socket(sid, namespace,
                                                          eio_sid)
                self.sio.emit('socket_connected', (
                    serialized_socket,
                    datetime.utcfromtimestamp(t).isoformat() + 'Z',
                ), namespace=self.admin_namespace)
        return socket.__send_ping()

    def _emit_server_stats(self):
        start_time = time.time()
        namespaces = list(self.sio.handlers.keys())
        namespaces.sort()
        while not self.stop_stats_event.is_set():
            self.sio.sleep(self.server_stats_interval)
            self.sio.emit('server_stats', {
                'serverId': self.server_id,
                'hostname': HOSTNAME,
                'pid': PID,
                'uptime': time.time() - start_time,
                'clientsCount': len(self.sio.eio.sockets),
                'pollingClientsCount': len(
                    [s for s in self.sio.eio.sockets.values()
                     if not s.upgraded]),
                'aggregatedEvents': self.event_buffer.get_and_clear(),
                'namespaces': [{
                    'name': nsp,
                    'socketsCount': len(self.sio.manager.rooms.get(
                        nsp, {None: []}).get(None, []))
                } for nsp in namespaces],
            }, namespace=self.admin_namespace)

    def serialize_socket(self, sid, namespace, eio_sid=None):
        if eio_sid is None:  # pragma: no cover
            eio_sid = self.sio.manager.eio_sid_from_sid(sid)
        socket = self.sio.eio._get_socket(eio_sid)
        environ = self.sio.environ.get(eio_sid, {})
        tm = self.sio.manager._timestamps[sid] if sid in \
            self.sio.manager._timestamps else 0
        return {
            'id': sid,
            'clientId': eio_sid,
            'transport': 'websocket' if socket.upgraded else 'polling',
            'nsp': namespace,
            'data': {},
            'handshake': {
                'address': environ.get('REMOTE_ADDR', ''),
                'headers': {k[5:].lower(): v for k, v in environ.items()
                            if k.startswith('HTTP_')},
                'query': {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
                    environ.get('QUERY_STRING', '')).items()},
                'secure': environ.get('wsgi.url_scheme', '') == 'https',
                'url': environ.get('PATH_INFO', ''),
                'issued': tm * 1000,
                'time': datetime.utcfromtimestamp(tm).isoformat() + 'Z'
                if tm else '',
            },
            'rooms': self.sio.manager.get_rooms(sid, namespace),
        }
