from functools import wraps
import threading
import time
from unittest import mock
import unittest
import pytest
try:
    from engineio.async_socket import AsyncSocket as EngineIOSocket
except ImportError:
    from engineio.asyncio_socket import AsyncSocket as EngineIOSocket
import socketio
from socketio.exceptions import ConnectionError
from tests.asyncio_web_server import SocketIOWebServer
from .helpers import AsyncMock


def with_instrumented_server(auth=False, **ikwargs):
    """This decorator can be applied to test functions or methods so that they
    run with a Socket.IO server that has been instrumented for the official
    Admin UI project. The arguments passed to the decorator are passed directly
    to the ``instrument()`` method of the server.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            sio = socketio.AsyncServer(async_mode='asgi')

            @sio.event
            async def enter_room(sid, data):
                await sio.enter_room(sid, data)

            @sio.event
            async def emit(sid, event):
                await sio.emit(event, skip_sid=sid)

            @sio.event(namespace='/foo')
            def connect(sid, environ, auth):
                pass

            async def shutdown():
                await instrumented_server.shutdown()
                await sio.shutdown()

            if 'server_stats_interval' not in ikwargs:
                ikwargs['server_stats_interval'] = 0.25

            instrumented_server = sio.instrument(auth=auth, **ikwargs)
            server = SocketIOWebServer(sio, on_shutdown=shutdown)
            server.start()

            # import logging
            # logging.getLogger('engineio.client').setLevel(logging.DEBUG)
            # logging.getLogger('socketio.client').setLevel(logging.DEBUG)

            original_schedule_ping = EngineIOSocket.schedule_ping
            EngineIOSocket.schedule_ping = mock.MagicMock()

            try:
                ret = f(self, instrumented_server, *args, **kwargs)
            finally:
                server.stop()
                instrumented_server.uninstrument()

            EngineIOSocket.schedule_ping = original_schedule_ping

            # import logging
            # logging.getLogger('engineio.client').setLevel(logging.NOTSET)
            # logging.getLogger('socketio.client').setLevel(logging.NOTSET)

            return ret
        return wrapped
    return decorator


def _custom_auth(auth):
    return auth == {'foo': 'bar'}


async def _async_custom_auth(auth):
    return auth == {'foo': 'bar'}


class TestAsyncAdmin(unittest.TestCase):
    def setUp(self):
        print('threads at start:', threading.enumerate())
        self.thread_count = threading.active_count()

    def tearDown(self):
        print('threads at end:', threading.enumerate())
        assert self.thread_count == threading.active_count()

    def _expect(self, expected, admin_client):
        events = {}
        while expected:
            data = admin_client.receive(timeout=5)
            if data[0] in expected:
                if expected[data[0]] == 1:
                    events[data[0]] = data[1]
                    del expected[data[0]]
                else:
                    expected[data[0]] -= 1
        return events

    def test_missing_auth(self):
        sio = socketio.AsyncServer(async_mode='asgi')
        with pytest.raises(ValueError):
            sio.instrument()

    @with_instrumented_server(auth=False)
    def test_admin_connect_with_no_auth(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin')
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'foo': 'bar'})

    @with_instrumented_server(auth={'foo': 'bar'})
    def test_admin_connect_with_dict_auth(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'foo': 'bar'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect(
                    'http://localhost:8900', namespace='/admin',
                    auth={'foo': 'baz'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect(
                    'http://localhost:8900', namespace='/admin')

    @with_instrumented_server(auth=[{'foo': 'bar'},
                                    {'u': 'admin', 'p': 'secret'}])
    def test_admin_connect_with_list_auth(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'foo': 'bar'})
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'u': 'admin', 'p': 'secret'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin', auth={'foo': 'baz'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin')

    @with_instrumented_server(auth=_custom_auth)
    def test_admin_connect_with_function_auth(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'foo': 'bar'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin', auth={'foo': 'baz'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin')

    @with_instrumented_server(auth=_async_custom_auth)
    def test_admin_connect_with_async_function_auth(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin',
                                 auth={'foo': 'bar'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin', auth={'foo': 'baz'})
        with socketio.SimpleClient() as admin_client:
            with pytest.raises(ConnectionError):
                admin_client.connect('http://localhost:8900',
                                     namespace='/admin')

    @with_instrumented_server()
    def test_admin_connect_only_admin(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin')
            sid = admin_client.sid
            events = self._expect({'config': 1, 'all_sockets': 1,
                                  'server_stats': 2}, admin_client)

        assert 'supportedFeatures' in events['config']
        assert 'ALL_EVENTS' in events['config']['supportedFeatures']
        assert 'AGGREGATED_EVENTS' in events['config']['supportedFeatures']
        assert 'EMIT' in events['config']['supportedFeatures']
        assert len(events['all_sockets']) == 1
        assert events['all_sockets'][0]['id'] == sid
        assert events['all_sockets'][0]['rooms'] == [sid]
        assert events['server_stats']['clientsCount'] == 1
        assert events['server_stats']['pollingClientsCount'] == 0
        assert len(events['server_stats']['namespaces']) == 3
        assert {'name': '/', 'socketsCount': 0} in \
            events['server_stats']['namespaces']
        assert {'name': '/foo', 'socketsCount': 0} in \
            events['server_stats']['namespaces']
        assert {'name': '/admin', 'socketsCount': 1} in \
            events['server_stats']['namespaces']

    @with_instrumented_server()
    def test_admin_connect_with_others(self, isvr):
        with socketio.SimpleClient() as client1, \
                socketio.SimpleClient() as client2, \
                socketio.SimpleClient() as client3, \
                socketio.SimpleClient() as admin_client:
            client1.connect('http://localhost:8900')
            client1.emit('enter_room', 'room')
            sid1 = client1.sid

            saved_check_for_upgrade = isvr._check_for_upgrade
            isvr._check_for_upgrade = AsyncMock()
            client2.connect('http://localhost:8900', namespace='/foo',
                            transports=['polling'])
            sid2 = client2.sid
            isvr._check_for_upgrade = saved_check_for_upgrade

            client3.connect('http://localhost:8900', namespace='/admin')
            sid3 = client3.sid

            admin_client.connect('http://localhost:8900', namespace='/admin')
            sid = admin_client.sid
            events = self._expect({'config': 1, 'all_sockets': 1,
                                  'server_stats': 2}, admin_client)

        assert 'supportedFeatures' in events['config']
        assert 'ALL_EVENTS' in events['config']['supportedFeatures']
        assert 'AGGREGATED_EVENTS' in events['config']['supportedFeatures']
        assert 'EMIT' in events['config']['supportedFeatures']
        assert len(events['all_sockets']) == 4
        assert events['server_stats']['clientsCount'] == 4
        assert events['server_stats']['pollingClientsCount'] == 1
        assert len(events['server_stats']['namespaces']) == 3
        assert {'name': '/', 'socketsCount': 1} in \
            events['server_stats']['namespaces']
        assert {'name': '/foo', 'socketsCount': 1} in \
            events['server_stats']['namespaces']
        assert {'name': '/admin', 'socketsCount': 2} in \
            events['server_stats']['namespaces']

        for socket in events['all_sockets']:
            if socket['id'] == sid:
                assert socket['rooms'] == [sid]
            elif socket['id'] == sid1:
                assert socket['rooms'] == [sid1, 'room']
            elif socket['id'] == sid2:
                assert socket['rooms'] == [sid2]
            elif socket['id'] == sid3:
                assert socket['rooms'] == [sid3]

    @with_instrumented_server(mode='production', read_only=True)
    def test_admin_connect_production(self, isvr):
        with socketio.SimpleClient() as admin_client:
            admin_client.connect('http://localhost:8900', namespace='/admin')
            events = self._expect({'config': 1, 'server_stats': 2},
                                  admin_client)

        assert 'supportedFeatures' in events['config']
        assert 'ALL_EVENTS' not in events['config']['supportedFeatures']
        assert 'AGGREGATED_EVENTS' in events['config']['supportedFeatures']
        assert 'EMIT' not in events['config']['supportedFeatures']
        assert events['server_stats']['clientsCount'] == 1
        assert events['server_stats']['pollingClientsCount'] == 0
        assert len(events['server_stats']['namespaces']) == 3
        assert {'name': '/', 'socketsCount': 0} in \
            events['server_stats']['namespaces']
        assert {'name': '/foo', 'socketsCount': 0} in \
            events['server_stats']['namespaces']
        assert {'name': '/admin', 'socketsCount': 1} in \
            events['server_stats']['namespaces']

    @with_instrumented_server()
    def test_admin_features(self, isvr):
        with socketio.SimpleClient() as client1, \
                socketio.SimpleClient() as client2, \
                socketio.SimpleClient() as admin_client:
            client1.connect('http://localhost:8900')
            client2.connect('http://localhost:8900')
            admin_client.connect('http://localhost:8900', namespace='/admin')

            # emit from admin
            admin_client.emit(
                'emit', ('/', client1.sid, 'foo', {'bar': 'baz'}, 'extra'))
            data = client1.receive(timeout=5)
            assert data == ['foo', {'bar': 'baz'}, 'extra']

            # emit from regular client
            client1.emit('emit', 'foo')
            data = client2.receive(timeout=5)
            assert data == ['foo']

            # join and leave
            admin_client.emit('join', ('/', 'room', client1.sid))
            time.sleep(0.2)
            admin_client.emit(
                'emit', ('/', 'room', 'foo', {'bar': 'baz'}))
            data = client1.receive(timeout=5)
            assert data == ['foo', {'bar': 'baz'}]
            admin_client.emit('leave', ('/', 'room'))

            # disconnect
            admin_client.emit('_disconnect', ('/', False, client1.sid))
            for _ in range(10):
                if not client1.connected:
                    break
                time.sleep(0.2)
            assert not client1.connected
