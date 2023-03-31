import asyncio
from datetime import datetime
import functools
import os
import socket
import time
from urllib.parse import parse_qs
from .admin import EventBuffer

HOSTNAME = socket.gethostname()
PID = os.getpid()


class InstrumentedAsyncServer:
    def __init__(self, sio, auth=None, namespace='/admin', read_only=False,
                 server_id=None, mode='development'):
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
        self.admin_queue = []
        self.event_buffer = EventBuffer()

        # monkey-patch the server to report metrics to the admin UI
        self.instrument()

        # start thread that emits "server_stats" every 2 seconds
        self.stop_stats_event = sio.eio.create_event()
        self.stats_task = None

    def instrument(self):
        self.sio.on('connect', self.admin_connect,
                    namespace=self.admin_namespace)

        if self.mode == 'development':
            if not self.read_only:
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
            self.sio.manager.__enter_room = self.sio.manager.enter_room
            self.sio.manager.enter_room = self._enter_room

            # report leave rooms
            self.sio.manager.__leave_room = self.sio.manager.leave_room
            self.sio.manager.leave_room = self._leave_room

            # report emit events
            self.sio.__emit_internal = self.sio._emit_internal
            self.sio._emit_internal = self._emit_internal

            # report receive events
            self.sio.__handle_event_internal = self.sio._handle_event_internal
            self.sio._handle_event_internal = self._handle_event_internal

        # report engine.io connections
        self.sio.eio.on('connect', self._handle_eio_connect)
        self.sio.eio.on('disconnect', self._handle_eio_disconnect)

        # report polling packets
        from engineio.asyncio_socket import AsyncSocket
        self.sio.eio.__ok = self.sio.eio._ok
        self.sio.eio._ok = self._eio_http_response
        AsyncSocket.__handle_post_request = functools.partialmethod(
            self._eio_handle_post_request)

        # report websocket packets
        AsyncSocket.__websocket_handler = AsyncSocket._websocket_handler
        AsyncSocket._websocket_handler = functools.partialmethod(
            self._eio_websocket_handler)

    async def admin_connect(self, sid, environ, client_auth):
        authenticated = True
        if self.auth:
            if asyncio.iscoroutinefunction(self.auth):
                authenticated = await self.auth(client_auth)
            else:
                authenticated = self.auth(client_auth)
        if not authenticated:
            raise ConnectionRefusedError('Invalid credentials')

        async def config(sid):
            await self.sio.sleep(0.1)

            # supported features
            features = ['EMIT', 'JOIN', 'LEAVE', 'DISCONNECT', 'MJOIN',
                        'MLEAVE', 'MDISCONNECT', 'AGGREGATED_EVENTS']
            if self.mode == 'development':
                features.append('ALL_EVENTS')
            await self.sio.emit('config', {'supportedFeatures': features},
                                to=sid, namespace=self.admin_namespace)

            # send current sockets
            if self.mode == 'development':
                all_sockets = []
                for nsp in self.sio.manager.get_namespaces():
                    for sid, eio_sid in self.sio.manager.get_participants(
                            nsp, None):
                        all_sockets.append(
                            self.serialize_socket(sid, nsp, eio_sid))
                await self.sio.emit('all_sockets', all_sockets, to=sid,
                                    namespace=self.admin_namespace)

        self.sio.start_background_task(config, sid)
        if self.stats_task is None:
            self.stats_task = self.sio.start_background_task(
                self._emit_server_stats)

    async def admin_emit(self, _, namespace, room_filter, event, *data):
        await self.sio.emit(event, data, to=room_filter, namespace=namespace)

    def admin_enter_room(self, _, namespace, room, room_filter=None):
        print(namespace, room, room_filter)
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            self.sio.enter_room(sid, room, namespace=namespace)

    def admin_leave_room(self, _, namespace, room, room_filter=None):
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            self.sio.leave_room(sid, room, namespace=namespace)

    async def admin_disconnect(self, _, namespace, close, room_filter=None):
        for sid, _ in self.sio.manager.get_participants(
                namespace, room_filter):
            await self.sio.disconnect(sid, namespace=namespace)

    async def shutdown(self):
        self.stop_stats_event.set()
        await asyncio.gather(self.stats_task)

    async def _connect(self, eio_sid, namespace):
        sid = await self.sio.manager.__connect(eio_sid, namespace)
        t = time.time()
        self.sio.manager._timestamps[sid] = t
        serialized_socket = self.serialize_socket(sid, namespace, eio_sid)
        await self.sio.emit('socket_connected', (
            serialized_socket,
            datetime.utcfromtimestamp(t).isoformat() + 'Z',
        ), namespace=self.admin_namespace)

        async def check_for_upgrade():
            for _ in range(5):
                await self.sio.sleep(5)
                if self.sio.eio._get_socket(eio_sid).upgraded:
                    await self.sio.emit('socket_updated', {
                        'id': sid,
                        'nsp': namespace,
                        'transport': 'websocket',
                    }, namespace=self.admin_namespace)
                    break

        if serialized_socket['transport'] == 'polling':
            self.sio.start_background_task(check_for_upgrade)
        return sid

    async def _disconnect(self, sid, namespace, **kwargs):
        del self.sio.manager._timestamps[sid]
        await self.sio.emit('socket_disconnected', (
            namespace,
            sid,
            'N/A',
            datetime.utcnow().isoformat() + 'Z',
        ), namespace=self.admin_namespace)
        return await self.sio.manager.__disconnect(sid, namespace, **kwargs)

    def _enter_room(self, sid, namespace, room, eio_sid=None):
        ret = self.sio.manager.__enter_room(sid, namespace, room, eio_sid)
        if room:
            self.admin_queue.append(('room_joined', (
                namespace,
                room,
                sid,
                datetime.utcnow().isoformat() + 'Z',
            )))
        return ret

    def _leave_room(self, sid, namespace, room):
        if room:
            self.admin_queue.append(('room_left', (
                namespace,
                room,
                sid,
                datetime.utcnow().isoformat() + 'Z',
            )))
        return self.sio.manager.__leave_room(sid, namespace, room)

    async def _emit_internal(self, eio_sid, event, data, namespace=None,
                             id=None):
        ret = await self.sio.__emit_internal(eio_sid, event, data,
                                             namespace=namespace, id=id)
        if namespace != self.admin_namespace:
            sid = self.sio.manager.sid_from_eio_sid(eio_sid, namespace)
            await self.sio.emit('event_sent', (
                namespace,
                sid,
                [event] + list(data) if isinstance(data, tuple) else [data],
                datetime.utcnow().isoformat() + 'Z',
            ), namespace=self.admin_namespace)
        return ret

    async def _handle_event_internal(self, server, sid, eio_sid, data,
                                     namespace, id):
        ret = await self.sio.__handle_event_internal(server, sid, eio_sid,
                                                     data, namespace, id)
        await self.sio.emit('event_received', (
            namespace,
            sid,
            data,
            datetime.utcnow().isoformat() + 'Z',
        ), namespace=self.admin_namespace)
        return ret

    async def _handle_eio_connect(self, eio_sid, environ):
        self.event_buffer.push('rawConnection')
        return await self.sio._handle_eio_connect(eio_sid, environ)

    async def _handle_eio_disconnect(self, eio_sid):
        self.event_buffer.push('rawDisconnection')
        return await self.sio._handle_eio_disconnect(eio_sid)

    def _eio_http_response(self, packets=None, headers=None, jsonp_index=None):
        ret = self.sio.eio.__ok(packets=packets, headers=headers,
                                jsonp_index=jsonp_index)
        self.event_buffer.push('packetsOut')
        self.event_buffer.push('bytesOut', len(ret['response']))
        return ret

    async def _eio_handle_post_request(self, socket, environ):
        ret = await socket.__handle_post_request(environ)
        self.event_buffer.push('packetsIn')
        self.event_buffer.push(
            'bytesIn', int(environ.get('CONTENT_LENGTH', 0)))
        return ret

    async def _eio_websocket_handler(self, socket, ws):
        async def _send(ws, data):
            self.event_buffer.push('packetsOut')
            self.event_buffer.push('bytesOut', len(data))
            return await ws.__send(data)

        async def _wait(ws):
            ret = await ws.__wait()
            self.event_buffer.push('packetsIn')
            self.event_buffer.push('bytesIn', len(ret))
            return ret

        ws.__send = ws.send
        ws.send = functools.partial(_send, ws)
        ws.__wait = ws.wait
        ws.wait = functools.partial(_wait, ws)
        return await socket.__websocket_handler(ws)

    async def _emit_server_stats(self):
        start_time = time.time()
        namespaces = list(self.sio.handlers.keys())
        namespaces.sort()
        while not self.stop_stats_event.is_set():
            await self.sio.sleep(2)
            await self.sio.emit('server_stats', {
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
                        nsp, {None: []})[None])
                } for nsp in namespaces],
            }, namespace=self.admin_namespace)
            while self.admin_queue:
                event, args = self.admin_queue.pop(0)
                await self.sio.emit(event, args,
                                    namespace=self.admin_namespace)

    def serialize_socket(self, sid, namespace, eio_sid=None):
        if eio_sid is None:
            eio_sid = self.sio.manager.eio_sid_from_sid(sid)
        socket = self.sio.eio._get_socket(eio_sid)
        environ = self.sio.environ.get(eio_sid, {})
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
                'issued': self.sio.manager._timestamps[sid] * 1000,
                'time': datetime.utcfromtimestamp(
                    self.sio.manager._timestamps[sid]).isoformat() + 'Z',
            },
            'rooms': self.sio.manager.get_rooms(sid, namespace),
        }
