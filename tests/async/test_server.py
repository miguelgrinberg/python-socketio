import asyncio
import logging
from unittest import mock

from engineio import json
from engineio import packet as eio_packet
import pytest

from socketio import async_server
from socketio import async_namespace
from socketio import exceptions
from socketio import namespace
from socketio import packet


@mock.patch('socketio.server.engineio.AsyncServer', **{
    'return_value.generate_id.side_effect': [str(i) for i in range(1, 10)],
    'return_value.send_packet': mock.AsyncMock()})
class TestAsyncServer:
    def teardown_method(self):
        # restore JSON encoder, in case a test changed it
        packet.Packet.json = json

    def _get_mock_manager(self):
        mgr = mock.MagicMock()
        mgr.can_disconnect = mock.AsyncMock()
        mgr.emit = mock.AsyncMock()
        mgr.enter_room = mock.AsyncMock()
        mgr.leave_room = mock.AsyncMock()
        mgr.close_room = mock.AsyncMock()
        mgr.trigger_callback = mock.AsyncMock()
        return mgr

    async def test_create(self, eio):
        eio.return_value.handle_request = mock.AsyncMock()
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(
            client_manager=mgr, async_handlers=True, foo='bar'
        )
        await s.handle_request({})
        await s.handle_request({})
        eio.assert_called_once_with(**{'foo': 'bar', 'async_handlers': False})
        assert s.manager == mgr
        assert s.eio.on.call_count == 3
        assert s.async_handlers

    async def test_attach(self, eio):
        s = async_server.AsyncServer()
        s.attach('app', 'path')
        eio.return_value.attach.assert_called_once_with('app', 'path')

    async def test_on_event(self, eio):
        s = async_server.AsyncServer()

        @s.on('connect')
        def foo():
            pass

        def bar(reason):
            pass

        s.on('disconnect', bar)
        s.on('disconnect', bar, namespace='/foo')

        assert s.handlers['/']['connect'] == foo
        assert s.handlers['/']['disconnect'] == bar
        assert s.handlers['/foo']['disconnect'] == bar

    async def test_emit(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.emit(
            'my event',
            {'foo': 'bar'},
            to='room',
            skip_sid='123',
            namespace='/foo',
            callback='cb',
        )
        s.manager.emit.assert_awaited_once_with(
            'my event',
            {'foo': 'bar'},
            '/foo',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=False,
        )
        await s.emit(
            'my event',
            {'foo': 'bar'},
            room='room',
            skip_sid='123',
            namespace='/foo',
            callback='cb',
            ignore_queue=True,
        )
        s.manager.emit.assert_awaited_with(
            'my event',
            {'foo': 'bar'},
            '/foo',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=True,
        )

    async def test_emit_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.emit(
            'my event',
            {'foo': 'bar'},
            to='room',
            skip_sid='123',
            callback='cb',
        )
        s.manager.emit.assert_awaited_once_with(
            'my event',
            {'foo': 'bar'},
            '/',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=False,
        )
        await s.emit(
            'my event',
            {'foo': 'bar'},
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=True,
        )
        s.manager.emit.assert_awaited_with(
            'my event',
            {'foo': 'bar'},
            '/',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=True,
        )

    async def test_send(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.send(
            'foo',
            to='room',
            skip_sid='123',
            namespace='/foo',
            callback='cb',
        )
        s.manager.emit.assert_awaited_once_with(
            'message',
            'foo',
            '/foo',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=False,
        )
        await s.send(
            'foo',
            room='room',
            skip_sid='123',
            namespace='/foo',
            callback='cb',
            ignore_queue=True,
        )
        s.manager.emit.assert_awaited_with(
            'message',
            'foo',
            '/foo',
            room='room',
            skip_sid='123',
            callback='cb',
            ignore_queue=True,
        )

    async def test_call(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)

        async def fake_event_wait():
            s.manager.emit.await_args_list[0][1]['callback']('foo', 321)
            return True

        s.eio.create_event.return_value.wait = fake_event_wait
        assert await s.call('foo', sid='123') == ('foo', 321)

    async def test_call_with_timeout(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)

        async def fake_event_wait():
            await asyncio.sleep(1)

        s.eio.create_event.return_value.wait = fake_event_wait
        with pytest.raises(exceptions.TimeoutError):
            await s.call('foo', sid='123', timeout=0.01)

    async def test_call_with_broadcast(self, eio):
        s = async_server.AsyncServer()
        with pytest.raises(ValueError):
            await s.call('foo')

    async def test_call_without_async_handlers(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(
            client_manager=mgr, async_handlers=False
        )
        with pytest.raises(RuntimeError):
            await s.call('foo', sid='123', timeout=12)

    async def test_enter_room(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.enter_room('123', 'room', namespace='/foo')
        s.manager.enter_room.assert_awaited_once_with('123', '/foo', 'room')

    async def test_enter_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.enter_room('123', 'room')
        s.manager.enter_room.assert_awaited_once_with('123', '/', 'room')

    async def test_leave_room(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.leave_room('123', 'room', namespace='/foo')
        s.manager.leave_room.assert_awaited_once_with('123', '/foo', 'room')

    async def test_leave_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.leave_room('123', 'room')
        s.manager.leave_room.assert_awaited_once_with('123', '/', 'room')

    async def test_close_room(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.close_room('room', namespace='/foo')
        s.manager.close_room.assert_awaited_once_with('room', '/foo')

    async def test_close_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s.close_room('room')
        s.manager.close_room.assert_awaited_once_with('room', '/')

    async def test_rooms(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        s.rooms('123', namespace='/foo')
        s.manager.get_rooms.assert_called_once_with('123', '/foo')

    async def test_rooms_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        s.rooms('123')
        s.manager.get_rooms.assert_called_once_with('123', '/')

    async def test_handle_request(self, eio):
        eio.return_value.handle_request = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s.handle_request('environ')
        s.eio.handle_request.assert_awaited_once_with('environ')

    async def test_send_packet(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s._send_packet('123', packet.Packet(
            packet.EVENT, ['my event', 'my data'], namespace='/foo'))
        s.eio.send.assert_awaited_once_with(
            '123', '2/foo,["my event","my data"]'
        )

    async def test_send_eio_packet(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s._send_eio_packet('123', eio_packet.Packet(
            eio_packet.MESSAGE, 'hello'))
        assert s.eio.send_packet.await_count == 1
        assert s.eio.send_packet.await_args_list[0][0][0] == '123'
        pkt = s.eio.send_packet.await_args_list[0][0][1]
        assert pkt.encode() == '4hello'

    async def test_transport(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.eio.transport = mock.MagicMock(return_value='polling')
        sid_foo = await s.manager.connect('123', '/foo')
        assert s.transport(sid_foo, '/foo') == 'polling'
        s.eio.transport.assert_called_once_with('123')

    async def test_handle_connect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.initialize = mock.MagicMock()
        handler = mock.MagicMock()
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with('123', '0{"sid":"1"}')
        assert s.manager.initialize.call_count == 1
        await s._handle_eio_connect('456', 'environ')
        await s._handle_eio_message('456', '0')
        assert s.manager.initialize.call_count == 1

    async def test_handle_connect_with_auth(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.initialize = mock.MagicMock()
        handler = mock.MagicMock()
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0{"token":"abc"}')
        assert s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ', {'token': 'abc'})
        s.eio.send.assert_awaited_once_with('123', '0{"sid":"1"}')
        assert s.manager.initialize.call_count == 1
        await s._handle_eio_connect('456', 'environ')
        await s._handle_eio_message('456', '0')
        assert s.manager.initialize.call_count == 1

    async def test_handle_connect_with_auth_none(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.initialize = mock.MagicMock()
        handler = mock.MagicMock(side_effect=[TypeError, None, None])
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert s.manager.is_connected('1', '/')
        handler.assert_called_with('1', 'environ', None)
        s.eio.send.assert_awaited_once_with('123', '0{"sid":"1"}')
        assert s.manager.initialize.call_count == 1
        await s._handle_eio_connect('456', 'environ')
        await s._handle_eio_message('456', '0')
        assert s.manager.initialize.call_count == 1

    async def test_handle_connect_async(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.initialize = mock.MagicMock()
        handler = mock.AsyncMock()
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert s.manager.is_connected('1', '/')
        handler.assert_awaited_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with('123', '0{"sid":"1"}')
        assert s.manager.initialize.call_count == 1
        await s._handle_eio_connect('456', 'environ')
        await s._handle_eio_message('456', '0')
        assert s.manager.initialize.call_count == 1

    async def test_handle_connect_with_default_implied_namespaces(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_message('123', '0/foo,')
        assert s.manager.is_connected('1', '/')
        assert not s.manager.is_connected('2', '/foo')

    async def test_handle_connect_with_implied_namespaces(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(namespaces=['/foo'])
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_message('123', '0/foo,')
        assert not s.manager.is_connected('1', '/')
        assert s.manager.is_connected('1', '/foo')

    async def test_handle_connect_with_all_implied_namespaces(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(namespaces='*')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_message('123', '0/foo,')
        assert s.manager.is_connected('1', '/')
        assert s.manager.is_connected('2', '/foo')

    async def test_handle_connect_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock()
        s.on('connect', handler, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with('123', '0/foo,{"sid":"1"}')

    async def test_handle_connect_always_connect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(always_connect=True)
        s.manager.initialize = mock.MagicMock()
        handler = mock.MagicMock()
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with('123', '0{"sid":"1"}')
        assert s.manager.initialize.call_count == 1
        await s._handle_eio_connect('456', 'environ')
        await s._handle_eio_message('456', '0')
        assert s.manager.initialize.call_count == 1

    async def test_handle_connect_rejected(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert not s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with(
            '123', '4{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_namespace_rejected(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert not s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_any_await(
            '123', '4/foo,{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_rejected_always_connect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(always_connect=True)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert not s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_any_await('123', '0{"sid":"1"}')
        s.eio.send.assert_any_await(
            '123', '1{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_namespace_rejected_always_connect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(always_connect=True)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert not s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_any_await('123', '0/foo,{"sid":"1"}')
        s.eio.send.assert_any_await(
            '123', '1/foo,{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_rejected_with_exception(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(
            side_effect=exceptions.ConnectionRefusedError('fail_reason')
        )
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert not s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with(
            '123', '4{"message":"fail_reason"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_rejected_with_empty_exception(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(
            side_effect=exceptions.ConnectionRefusedError()
        )
        s.on('connect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        assert not s.manager.is_connected('1', '/')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with(
            '123', '4{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_namespace_rejected_with_exception(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(
            side_effect=exceptions.ConnectionRefusedError(
                'fail_reason', 1, '2')
        )
        s.on('connect', handler, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert not s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with(
            '123', '4/foo,{"message":"fail_reason","data":[1,"2"]}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_connect_namespace_rejected_with_empty_exception(
            self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock(
            side_effect=exceptions.ConnectionRefusedError()
        )
        s.on('connect', handler, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert not s.manager.is_connected('1', '/foo')
        handler.assert_called_once_with('1', 'environ')
        s.eio.send.assert_awaited_once_with(
            '123', '4/foo,{"message":"Connection rejected by server"}')
        assert s.environ == {'123': 'environ'}

    async def test_handle_disconnect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.disconnect = mock.AsyncMock()
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_disconnect('123', 'foo')
        handler.assert_called_once_with('1', 'foo')
        s.manager.disconnect.assert_awaited_once_with(
            '1', '/', ignore_queue=True)
        assert s.environ == {}

    async def test_handle_legacy_disconnect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.disconnect = mock.AsyncMock()
        handler = mock.MagicMock(side_effect=[TypeError, None])
        s.on('disconnect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_disconnect('123', 'foo')
        handler.assert_called_with('1')
        s.manager.disconnect.assert_awaited_once_with(
            '1', '/', ignore_queue=True)
        assert s.environ == {}

    async def test_handle_legacy_disconnect_async(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.manager.disconnect = mock.AsyncMock()
        handler = mock.AsyncMock(side_effect=[TypeError, None])
        s.on('disconnect', handler)
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s._handle_eio_disconnect('123', 'foo')
        handler.assert_awaited_with('1')
        s.manager.disconnect.assert_awaited_once_with(
            '1', '/', ignore_queue=True)
        assert s.environ == {}

    async def test_handle_disconnect_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        await s._handle_eio_disconnect('123', 'foo')
        handler.assert_not_called()
        handler_namespace.assert_called_once_with('1', 'foo')
        assert s.environ == {}

    async def test_handle_disconnect_only_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        await s._handle_eio_message('123', '1/foo,')
        assert handler.call_count == 0
        handler_namespace.assert_called_once_with(
            '1', s.reason.CLIENT_DISCONNECT)
        assert s.environ == {'123': 'environ'}

    async def test_handle_disconnect_unknown_client(self, eio):
        mgr = self._get_mock_manager()
        s = async_server.AsyncServer(client_manager=mgr)
        await s._handle_eio_disconnect('123', 'foo')

    async def test_handle_event(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.AsyncMock()
        catchall_handler = mock.AsyncMock()
        s.on('msg', handler)
        s.on('*', catchall_handler)
        await s._handle_eio_message('123', '2["msg","a","b"]')
        await s._handle_eio_message('123', '2["my message","a","b","c"]')
        handler.assert_awaited_once_with(sid, 'a', 'b')
        catchall_handler.assert_awaited_once_with(
            'my message', sid, 'a', 'b', 'c')

    async def test_handle_event_with_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/foo')
        handler = mock.MagicMock()
        catchall_handler = mock.MagicMock()
        s.on('msg', handler, namespace='/foo')
        s.on('*', catchall_handler, namespace='/foo')
        await s._handle_eio_message('123', '2/foo,["msg","a","b"]')
        await s._handle_eio_message('123', '2/foo,["my message","a","b","c"]')
        handler.assert_called_once_with(sid, 'a', 'b')
        catchall_handler.assert_called_once_with(
            'my message', sid, 'a', 'b', 'c')

    async def test_handle_event_with_catchall_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid_foo = await s.manager.connect('123', '/foo')
        sid_bar = await s.manager.connect('123', '/bar')
        connect_star_handler = mock.MagicMock()
        msg_foo_handler = mock.MagicMock()
        msg_star_handler = mock.MagicMock()
        star_foo_handler = mock.MagicMock()
        star_star_handler = mock.MagicMock()
        s.on('connect', connect_star_handler, namespace='*')
        s.on('msg', msg_foo_handler, namespace='/foo')
        s.on('msg', msg_star_handler, namespace='*')
        s.on('*', star_foo_handler, namespace='/foo')
        s.on('*', star_star_handler, namespace='*')
        await s._trigger_event('connect', '/bar', sid_bar)
        await s._handle_eio_message('123', '2/foo,["msg","a","b"]')
        await s._handle_eio_message('123', '2/bar,["msg","a","b"]')
        await s._handle_eio_message('123', '2/foo,["my message","a","b","c"]')
        await s._handle_eio_message('123', '2/bar,["my message","a","b","c"]')
        await s._trigger_event('disconnect', '/bar', sid_bar,
                               s.reason.CLIENT_DISCONNECT)
        connect_star_handler.assert_called_once_with('/bar', sid_bar)
        msg_foo_handler.assert_called_once_with(sid_foo, 'a', 'b')
        msg_star_handler.assert_called_once_with('/bar', sid_bar, 'a', 'b')
        star_foo_handler.assert_called_once_with(
            'my message', sid_foo, 'a', 'b', 'c')
        star_star_handler.assert_called_once_with(
            'my message', '/bar', sid_bar, 'a', 'b', 'c')

    async def test_handle_event_with_disconnected_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        await s.manager.connect('123', '/foo')
        handler = mock.MagicMock()
        s.on('my message', handler, namespace='/bar')
        await s._handle_eio_message('123', '2/bar,["my message","a","b","c"]')
        handler.assert_not_called()

    async def test_handle_event_binary(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock()
        s.on('my message', handler)
        await s._handle_eio_message(
            '123',
            '52-["my message","a",'
            '{"_placeholder":true,"num":1},'
            '{"_placeholder":true,"num":0}]',
        )
        await s._handle_eio_message('123', b'foo')
        await s._handle_eio_message('123', b'bar')
        handler.assert_called_once_with(sid, 'a', b'bar', b'foo')

    async def test_handle_event_binary_ack(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        s.manager.trigger_callback = mock.AsyncMock()
        sid = await s.manager.connect('123', '/')
        await s._handle_eio_message(
            '123',
            '61-321["my message","a",' '{"_placeholder":true,"num":0}]',
        )
        await s._handle_eio_message('123', b'foo')
        s.manager.trigger_callback.assert_awaited_once_with(
            sid, 321, ['my message', 'a', b'foo']
        )

    async def test_handle_event_with_ack(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value='foo')
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["my message","foo"]')
        handler.assert_called_once_with(sid, 'foo')
        s.eio.send.assert_awaited_once_with(
            '123', '31000["foo"]'
        )

    async def test_handle_unknown_event_with_ack(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value='foo')
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["another message","foo"]')
        s.eio.send.assert_not_awaited()

    async def test_handle_event_with_ack_none(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value=None)
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["my message","foo"]')
        handler.assert_called_once_with(sid, 'foo')
        s.eio.send.assert_awaited_once_with('123', '31000[]')

    async def test_handle_event_with_ack_tuple(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value=(1, '2', True))
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["my message","a","b","c"]')
        handler.assert_called_once_with(sid, 'a', 'b', 'c')
        s.eio.send.assert_awaited_once_with(
            '123', '31000[1,"2",true]'
        )

    async def test_handle_event_with_ack_list(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value=[1, '2', True])
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["my message","a","b","c"]')
        handler.assert_called_once_with(sid, 'a', 'b', 'c')
        s.eio.send.assert_awaited_once_with(
            '123', '31000[[1,"2",true]]'
        )

    async def test_handle_event_with_ack_binary(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer(async_handlers=False)
        sid = await s.manager.connect('123', '/')
        handler = mock.MagicMock(return_value=b'foo')
        s.on('my message', handler)
        await s._handle_eio_message('123', '21000["my message","foo"]')
        handler.assert_any_call(sid, 'foo')

    async def test_handle_error_packet(self, eio):
        s = async_server.AsyncServer()
        with pytest.raises(ValueError):
            await s._handle_eio_message('123', '4')

    async def test_handle_invalid_packet(self, eio):
        s = async_server.AsyncServer()
        with pytest.raises(ValueError):
            await s._handle_eio_message('123', '9')

    async def test_send_with_ack(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/'] = {}
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        cb = mock.MagicMock()
        id1 = s.manager._generate_ack_id('1', cb)
        id2 = s.manager._generate_ack_id('1', cb)
        await s._send_packet('123', packet.Packet(
            packet.EVENT, ['my event', 'foo'], id=id1))
        await s._send_packet('123', packet.Packet(
            packet.EVENT, ['my event', 'bar'], id=id2))
        await s._handle_eio_message('123', '31["foo",2]')
        cb.assert_called_once_with('foo', 2)

    async def test_send_with_ack_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/foo'] = {}
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        cb = mock.MagicMock()
        id = s.manager._generate_ack_id('1', cb)
        await s._send_packet(
            '123', packet.Packet(packet.EVENT, ['my event', 'foo'],
                                 namespace='/foo', id=id)
        )
        await s._handle_eio_message('123', '3/foo,1["foo",2]')
        cb.assert_called_once_with('foo', 2)

    async def test_session(self, eio):
        fake_session = {}

        async def fake_get_session(eio_sid):
            assert eio_sid == '123'
            return fake_session

        async def fake_save_session(eio_sid, session):
            global fake_session
            assert eio_sid == '123'
            fake_session = session

        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/'] = {}
        s.handlers['/ns'] = {}
        s.eio.get_session = fake_get_session
        s.eio.save_session = fake_save_session

        async def _test():
            await s._handle_eio_connect('123', 'environ')
            await s._handle_eio_message('123', '0')
            await s._handle_eio_message('123', '0/ns')
            sid = s.manager.sid_from_eio_sid('123', '/')
            sid2 = s.manager.sid_from_eio_sid('123', '/ns')
            await s.save_session(sid, {'foo': 'bar'})
            async with s.session(sid) as session:
                assert session == {'foo': 'bar'}
                session['foo'] = 'baz'
                session['bar'] = 'foo'
            assert await s.get_session(sid) == {'foo': 'baz', 'bar': 'foo'}
            assert fake_session == {'/': {'foo': 'baz', 'bar': 'foo'}}
            async with s.session(sid2, namespace='/ns') as session:
                assert session == {}
                session['a'] = 'b'
            assert await s.get_session(sid2, namespace='/ns') == {'a': 'b'}
            assert fake_session == {
                '/': {'foo': 'baz', 'bar': 'foo'},
                '/ns': {'a': 'b'},
            }

        await _test()

    async def test_disconnect(self, eio):
        eio.return_value.send = mock.AsyncMock()
        eio.return_value.disconnect = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/'] = {}
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s.disconnect('1')
        s.eio.send.assert_any_await('123', '1')
        assert not s.manager.is_connected('1', '/')

    async def test_disconnect_ignore_queue(self, eio):
        eio.return_value.send = mock.AsyncMock()
        eio.return_value.disconnect = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/'] = {}
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s.disconnect('1', ignore_queue=True)
        s.eio.send.assert_any_await('123', '1')
        assert not s.manager.is_connected('1', '/')

    async def test_disconnect_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        eio.return_value.disconnect = mock.AsyncMock()
        s = async_server.AsyncServer()
        s.handlers['/foo'] = {}
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        await s.disconnect('1', namespace='/foo')
        s.eio.send.assert_any_await('123', '1/foo,')
        assert not s.manager.is_connected('1', '/foo')

    async def test_disconnect_twice(self, eio):
        eio.return_value.send = mock.AsyncMock()
        eio.return_value.disconnect = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0')
        await s.disconnect('1')
        calls = s.eio.send.await_count
        assert not s.manager.is_connected('1', '/')
        await s.disconnect('1')
        assert calls == s.eio.send.await_count

    async def test_disconnect_twice_namespace(self, eio):
        eio.return_value.send = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        await s.disconnect('1', namespace='/foo')
        calls = s.eio.send.await_count
        assert not s.manager.is_connected('1', '/foo')
        await s.disconnect('1', namespace='/foo')
        assert calls == s.eio.send.await_count

    async def test_namespace_handler(self, eio):
        eio.return_value.send = mock.AsyncMock()
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

            async def on_disconnect(self, sid, reason):
                result['result'] = ('disconnect', sid, reason)

            async def on_foo(self, sid, data):
                result['result'] = (sid, data)

            def on_bar(self, sid):
                result['result'] = 'bar'

            async def on_baz(self, sid, data1, data2):
                result['result'] = (data1, data2)

        s = async_server.AsyncServer(async_handlers=False)
        s.register_namespace(MyNamespace('/foo'))
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert result['result'] == ('1', 'environ')
        await s._handle_eio_message('123', '2/foo,["foo","a"]')
        assert result['result'] == ('1', 'a')
        await s._handle_eio_message('123', '2/foo,["bar"]')
        assert result['result'] == 'bar'
        await s._handle_eio_message('123', '2/foo,["baz","a","b"]')
        assert result['result'] == ('a', 'b')
        await s.disconnect('1', '/foo')
        assert result['result'] == ('disconnect', '1',
                                    s.reason.SERVER_DISCONNECT)

    async def test_catchall_namespace_handler(self, eio):
        eio.return_value.send = mock.AsyncMock()
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            def on_connect(self, ns, sid, environ):
                result['result'] = (sid, ns, environ)

            async def on_disconnect(self, ns, sid):
                result['result'] = ('disconnect', sid, ns)

            async def on_foo(self, ns, sid, data):
                result['result'] = (sid, ns, data)

            def on_bar(self, ns, sid):
                result['result'] = 'bar' + ns

            async def on_baz(self, ns, sid, data1, data2):
                result['result'] = (ns, data1, data2)

        s = async_server.AsyncServer(async_handlers=False, namespaces='*')
        s.register_namespace(MyNamespace('*'))
        await s._handle_eio_connect('123', 'environ')
        await s._handle_eio_message('123', '0/foo,')
        assert result['result'] == ('1', '/foo', 'environ')
        await s._handle_eio_message('123', '2/foo,["foo","a"]')
        assert result['result'] == ('1', '/foo', 'a')
        await s._handle_eio_message('123', '2/foo,["bar"]')
        assert result['result'] == 'bar/foo'
        await s._handle_eio_message('123', '2/foo,["baz","a","b"]')
        assert result['result'] == ('/foo', 'a', 'b')
        await s.disconnect('1', '/foo')
        assert result['result'] == ('disconnect', '1', '/foo')

    async def test_bad_namespace_handler(self, eio):
        class Dummy:
            pass

        class SyncNS(namespace.Namespace):
            pass

        s = async_server.AsyncServer()
        with pytest.raises(ValueError):
            s.register_namespace(123)
        with pytest.raises(ValueError):
            s.register_namespace(Dummy)
        with pytest.raises(ValueError):
            s.register_namespace(Dummy())
        with pytest.raises(ValueError):
            s.register_namespace(namespace.Namespace)
        with pytest.raises(ValueError):
            s.register_namespace(SyncNS())

    async def test_logger(self, eio):
        s = async_server.AsyncServer(logger=False)
        assert s.logger.getEffectiveLevel() == logging.ERROR
        s.logger.setLevel(logging.NOTSET)
        s = async_server.AsyncServer(logger=True)
        assert s.logger.getEffectiveLevel() == logging.INFO
        s.logger.setLevel(logging.WARNING)
        s = async_server.AsyncServer(logger=True)
        assert s.logger.getEffectiveLevel() == logging.WARNING
        s.logger.setLevel(logging.NOTSET)
        s = async_server.AsyncServer(logger='foo')
        assert s.logger == 'foo'

    async def test_engineio_logger(self, eio):
        async_server.AsyncServer(engineio_logger='foo')
        eio.assert_called_once_with(
            **{'logger': 'foo', 'async_handlers': False}
        )

    async def test_custom_json(self, eio):
        # Warning: this test cannot run in parallel with other tests, as it
        # changes the JSON encoding/decoding functions

        class CustomJSON:
            @staticmethod
            def dumps(*args, **kwargs):
                return '*** encoded ***'

            @staticmethod
            def loads(*args, **kwargs):
                return '+++ decoded +++'

        async_server.AsyncServer(json=CustomJSON)
        eio.assert_called_once_with(
            **{'json': CustomJSON, 'async_handlers': False}
        )

        pkt = packet.Packet(
            packet_type=packet.EVENT,
            data={'foo': 'bar'},
        )
        assert pkt.encode() == '2*** encoded ***'
        pkt2 = packet.Packet(encoded_packet=pkt.encode())
        assert pkt2.data == '+++ decoded +++'

        # restore the default JSON module
        packet.Packet.json = json

    async def test_async_handlers(self, eio):
        s = async_server.AsyncServer(async_handlers=True)
        await s.manager.connect('123', '/')
        await s._handle_eio_message('123', '2["my message","a","b","c"]')
        s.eio.start_background_task.assert_called_once_with(
            s._handle_event_internal,
            s,
            '1',
            '123',
            ['my message', 'a', 'b', 'c'],
            '/',
            None,
        )

    async def test_shutdown(self, eio):
        s = async_server.AsyncServer()
        s.eio.shutdown = mock.AsyncMock()
        await s.shutdown()
        s.eio.shutdown.assert_awaited_once_with()

    async def test_start_background_task(self, eio):
        s = async_server.AsyncServer()
        s.start_background_task('foo', 'bar', baz='baz')
        s.eio.start_background_task.assert_called_once_with(
            'foo', 'bar', baz='baz'
        )

    async def test_sleep(self, eio):
        eio.return_value.sleep = mock.AsyncMock()
        s = async_server.AsyncServer()
        await s.sleep(1.23)
        s.eio.sleep.assert_awaited_once_with(1.23)
