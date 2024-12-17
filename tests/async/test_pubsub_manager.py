import asyncio
import functools
from unittest import mock

import pytest

from socketio import async_manager
from socketio import async_pubsub_manager
from socketio import packet


class TestAsyncPubSubManager:
    def setup_method(self):
        id = 0

        def generate_id():
            nonlocal id
            id += 1
            return str(id)

        mock_server = mock.MagicMock()
        mock_server.eio.generate_id = generate_id
        mock_server.packet_class = packet.Packet
        mock_server._send_packet = mock.AsyncMock()
        mock_server._send_eio_packet = mock.AsyncMock()
        mock_server.disconnect = mock.AsyncMock()
        self.pm = async_pubsub_manager.AsyncPubSubManager()
        self.pm._publish = mock.AsyncMock()
        self.pm.set_server(mock_server)
        self.pm.host_id = '123456'
        self.pm.initialize()

    async def test_default_init(self):
        assert self.pm.channel == 'socketio'
        self.pm.server.start_background_task.assert_called_once_with(
            self.pm._thread
        )

    async def test_custom_init(self):
        pubsub = async_pubsub_manager.AsyncPubSubManager(channel='foo')
        assert pubsub.channel == 'foo'
        assert len(pubsub.host_id) == 32

    async def test_write_only_init(self):
        mock_server = mock.MagicMock()
        pm = async_pubsub_manager.AsyncPubSubManager(write_only=True)
        pm.set_server(mock_server)
        pm.initialize()
        assert pm.channel == 'socketio'
        assert len(pm.host_id) == 32
        assert pm.server.start_background_task.call_count == 0

    async def test_emit(self):
        await self.pm.emit('foo', 'bar')
        self.pm._publish.assert_awaited_once_with(
            {
                'method': 'emit',
                'event': 'foo',
                'data': 'bar',
                'namespace': '/',
                'room': None,
                'skip_sid': None,
                'callback': None,
                'host_id': '123456',
            }
        )

    async def test_emit_with_to(self):
        sid = 'room-mate'
        await self.pm.emit('foo', 'bar', to=sid)
        self.pm._publish.assert_awaited_once_with(
            {
                'method': 'emit',
                'event': 'foo',
                'data': 'bar',
                'namespace': '/',
                'room': sid,
                'skip_sid': None,
                'callback': None,
                'host_id': '123456',
            }
        )

    async def test_emit_with_namespace(self):
        await self.pm.emit('foo', 'bar', namespace='/baz')
        self.pm._publish.assert_awaited_once_with(
            {
                'method': 'emit',
                'event': 'foo',
                'data': 'bar',
                'namespace': '/baz',
                'room': None,
                'skip_sid': None,
                'callback': None,
                'host_id': '123456',
            }
        )

    async def test_emit_with_room(self):
        await self.pm.emit('foo', 'bar', room='baz')
        self.pm._publish.assert_awaited_once_with(
            {
                'method': 'emit',
                'event': 'foo',
                'data': 'bar',
                'namespace': '/',
                'room': 'baz',
                'skip_sid': None,
                'callback': None,
                'host_id': '123456',
            }
        )

    async def test_emit_with_skip_sid(self):
        await self.pm.emit('foo', 'bar', skip_sid='baz')
        self.pm._publish.assert_awaited_once_with(
            {
                'method': 'emit',
                'event': 'foo',
                'data': 'bar',
                'namespace': '/',
                'room': None,
                'skip_sid': 'baz',
                'callback': None,
                'host_id': '123456',
            }
        )

    async def test_emit_with_callback(self):
        with mock.patch.object(
            self.pm, '_generate_ack_id', return_value='123'
        ):
            await self.pm.emit('foo', 'bar', room='baz', callback='cb')
            self.pm._publish.assert_awaited_once_with(
                {
                    'method': 'emit',
                    'event': 'foo',
                    'data': 'bar',
                    'namespace': '/',
                    'room': 'baz',
                    'skip_sid': None,
                    'callback': ('baz', '/', '123'),
                    'host_id': '123456',
                }
            )

    async def test_emit_with_callback_without_server(self):
        standalone_pm = async_pubsub_manager.AsyncPubSubManager()
        with pytest.raises(RuntimeError):
            await standalone_pm.emit('foo', 'bar', callback='cb')

    async def test_emit_with_callback_missing_room(self):
        with mock.patch.object(
            self.pm, '_generate_ack_id', return_value='123'
        ):
            with pytest.raises(ValueError):
                await self.pm.emit('foo', 'bar', callback='cb')

    async def test_emit_with_ignore_queue(self):
        sid = await self.pm.connect('123', '/')
        await self.pm.emit(
            'foo', 'bar', room=sid, namespace='/', ignore_queue=True
        )
        self.pm._publish.assert_not_awaited()
        assert self.pm.server._send_eio_packet.await_count == 1
        assert self.pm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.pm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42["foo","bar"]'

    async def test_can_disconnect(self):
        sid = await self.pm.connect('123', '/')
        assert await self.pm.can_disconnect(sid, '/') is True
        await self.pm.can_disconnect(sid, '/foo')
        self.pm._publish.assert_awaited_once_with(
            {'method': 'disconnect', 'sid': sid, 'namespace': '/foo',
             'host_id': '123456'}
        )

    async def test_disconnect(self):
        await self.pm.disconnect('foo', '/')
        self.pm._publish.assert_awaited_once_with(
            {'method': 'disconnect', 'sid': 'foo', 'namespace': '/',
             'host_id': '123456'}
        )

    async def test_disconnect_ignore_queue(self):
        sid = await self.pm.connect('123', '/')
        self.pm.pre_disconnect(sid, '/')
        await self.pm.disconnect(sid, '/', ignore_queue=True)
        self.pm._publish.assert_not_awaited()
        assert self.pm.is_connected(sid, '/') is False

    async def test_enter_room(self):
        sid = await self.pm.connect('123', '/')
        await self.pm.enter_room(sid, '/', 'foo')
        await self.pm.enter_room('456', '/', 'foo')
        assert sid in self.pm.rooms['/']['foo']
        assert self.pm.rooms['/']['foo'][sid] == '123'
        self.pm._publish.assert_awaited_once_with(
            {'method': 'enter_room', 'sid': '456', 'room': 'foo',
             'namespace': '/', 'host_id': '123456'}
        )

    async def test_leave_room(self):
        sid = await self.pm.connect('123', '/')
        await self.pm.leave_room(sid, '/', 'foo')
        await self.pm.leave_room('456', '/', 'foo')
        assert 'foo' not in self.pm.rooms['/']
        self.pm._publish.assert_awaited_once_with(
            {'method': 'leave_room', 'sid': '456', 'room': 'foo',
             'namespace': '/', 'host_id': '123456'}
        )

    async def test_close_room(self):
        await self.pm.close_room('foo')
        self.pm._publish.assert_awaited_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/',
             'host_id': '123456'}
        )

    async def test_close_room_with_namespace(self):
        await self.pm.close_room('foo', '/bar')
        self.pm._publish.assert_awaited_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/bar',
             'host_id': '123456'}
        )

    async def test_handle_emit(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit({'event': 'foo', 'data': 'bar'})
            super_emit.assert_awaited_once_with(
                'foo',
                'bar',
                namespace=None,
                room=None,
                skip_sid=None,
                callback=None,
            )

    async def test_handle_emit_with_namespace(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit(
                {'event': 'foo', 'data': 'bar', 'namespace': '/baz'}
            )
            super_emit.assert_awaited_once_with(
                'foo',
                'bar',
                namespace='/baz',
                room=None,
                skip_sid=None,
                callback=None,
            )

    async def test_handle_emit_with_room(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit(
                {'event': 'foo', 'data': 'bar', 'room': 'baz'}
            )
            super_emit.assert_awaited_once_with(
                'foo',
                'bar',
                namespace=None,
                room='baz',
                skip_sid=None,
                callback=None,
            )

    async def test_handle_emit_with_skip_sid(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit(
                {'event': 'foo', 'data': 'bar', 'skip_sid': '123'}
            )
            super_emit.assert_awaited_once_with(
                'foo',
                'bar',
                namespace=None,
                room=None,
                skip_sid='123',
                callback=None,
            )

    async def test_handle_emit_with_remote_callback(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit(
                {
                    'event': 'foo',
                    'data': 'bar',
                    'namespace': '/baz',
                    'callback': ('sid', '/baz', 123),
                    'host_id': 'x',
                }
            )
            assert super_emit.await_count == 1
            assert super_emit.await_args[0] == ('foo', 'bar')
            assert super_emit.await_args[1]['namespace'] == '/baz'
            assert super_emit.await_args[1]['room'] is None
            assert super_emit.await_args[1]['skip_sid'] is None
            assert isinstance(
                super_emit.await_args[1]['callback'], functools.partial
            )
            await super_emit.await_args[1]['callback']('one', 2, 'three')
            self.pm._publish.assert_awaited_once_with(
                {
                    'method': 'callback',
                    'host_id': 'x',
                    'sid': 'sid',
                    'namespace': '/baz',
                    'id': 123,
                    'args': ('one', 2, 'three'),
                }
            )

    async def test_handle_emit_with_local_callback(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'emit'
        ) as super_emit:
            await self.pm._handle_emit(
                {
                    'event': 'foo',
                    'data': 'bar',
                    'namespace': '/baz',
                    'callback': ('sid', '/baz', 123),
                    'host_id': self.pm.host_id,
                }
            )
            assert super_emit.await_count == 1
            assert super_emit.await_args[0] == ('foo', 'bar')
            assert super_emit.await_args[1]['namespace'] == '/baz'
            assert super_emit.await_args[1]['room'] is None
            assert super_emit.await_args[1]['skip_sid'] is None
            assert isinstance(
                super_emit.await_args[1]['callback'], functools.partial
            )
            await super_emit.await_args[1]['callback']('one', 2, 'three')
            self.pm._publish.assert_not_awaited()

    async def test_handle_callback(self):
        host_id = self.pm.host_id
        with mock.patch.object(
            self.pm, 'trigger_callback'
        ) as trigger:
            await self.pm._handle_callback(
                {
                    'method': 'callback',
                    'host_id': host_id,
                    'sid': 'sid',
                    'namespace': '/',
                    'id': 123,
                    'args': ('one', 2),
                }
            )
            trigger.assert_awaited_once_with('sid', 123, ('one', 2))

    async def test_handle_callback_bad_host_id(self):
        with mock.patch.object(
            self.pm, 'trigger_callback'
        ) as trigger:
            await self.pm._handle_callback(
                {
                    'method': 'callback',
                    'host_id': 'bad',
                    'sid': 'sid',
                    'namespace': '/',
                    'id': 123,
                    'args': ('one', 2),
                }
            )
            assert trigger.await_count == 0

    async def test_handle_callback_missing_args(self):
        host_id = self.pm.host_id
        with mock.patch.object(
            self.pm, 'trigger_callback'
        ) as trigger:
            await self.pm._handle_callback(
                {
                    'method': 'callback',
                    'host_id': host_id,
                    'sid': 'sid',
                    'namespace': '/',
                    'id': 123,
                }
            )
            await self.pm._handle_callback(
                {
                    'method': 'callback',
                    'host_id': host_id,
                    'sid': 'sid',
                    'namespace': '/',
                }
            )
            await self.pm._handle_callback(
                {'method': 'callback', 'host_id': host_id, 'sid': 'sid'}
            )
            await self.pm._handle_callback(
                {'method': 'callback', 'host_id': host_id}
            )
            assert trigger.await_count == 0

    async def test_handle_disconnect(self):
        await self.pm._handle_disconnect(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'}
        )
        self.pm.server.disconnect.assert_awaited_once_with(
            sid='123', namespace='/foo', ignore_queue=True
        )

    async def test_handle_enter_room(self):
        sid = await self.pm.connect('123', '/')
        with mock.patch.object(
            async_manager.AsyncManager, 'enter_room'
        ) as super_enter_room:
            await self.pm._handle_enter_room(
                {'method': 'enter_room', 'sid': sid, 'namespace': '/',
                 'room': 'foo'}
            )
            await self.pm._handle_enter_room(
                {'method': 'enter_room', 'sid': '456', 'namespace': '/',
                 'room': 'foo'}
            )
            super_enter_room.assert_awaited_once_with(sid, '/', 'foo')

    async def test_handle_leave_room(self):
        sid = await self.pm.connect('123', '/')
        with mock.patch.object(
            async_manager.AsyncManager, 'leave_room'
        ) as super_leave_room:
            await self.pm._handle_leave_room(
                {'method': 'leave_room', 'sid': sid, 'namespace': '/',
                 'room': 'foo'}
            )
            await self.pm._handle_leave_room(
                {'method': 'leave_room', 'sid': '456', 'namespace': '/',
                 'room': 'foo'}
            )
            super_leave_room.assert_awaited_once_with(sid, '/', 'foo')

    async def test_handle_close_room(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'close_room'
        ) as super_close_room:
            await self.pm._handle_close_room(
                {'method': 'close_room', 'room': 'foo'}
            )
            super_close_room.assert_awaited_once_with(
                room='foo', namespace=None
            )

    async def test_handle_close_room_with_namespace(self):
        with mock.patch.object(
            async_manager.AsyncManager, 'close_room'
        ) as super_close_room:
            await self.pm._handle_close_room(
                {
                    'method': 'close_room',
                    'room': 'foo',
                    'namespace': '/bar',
                }
            )
            super_close_room.assert_awaited_once_with(
                room='foo', namespace='/bar'
            )

    async def test_background_thread(self):
        self.pm._handle_emit = mock.AsyncMock()
        self.pm._handle_callback = mock.AsyncMock()
        self.pm._handle_disconnect = mock.AsyncMock()
        self.pm._handle_enter_room = mock.AsyncMock()
        self.pm._handle_leave_room = mock.AsyncMock()
        self.pm._handle_close_room = mock.AsyncMock()
        host_id = self.pm.host_id

        async def messages():
            import pickle

            yield {'method': 'emit', 'value': 'foo', 'host_id': 'x'}
            yield {'missing': 'method', 'host_id': 'x'}
            yield '{"method": "callback", "value": "bar", "host_id": "x"}'
            yield {'method': 'disconnect', 'sid': '123', 'namespace': '/foo',
                   'host_id': 'x'}
            yield {'method': 'bogus', 'host_id': 'x'}
            yield pickle.dumps({'method': 'close_room', 'value': 'baz',
                                'host_id': 'x'})
            yield {'method': 'enter_room', 'sid': '123', 'namespace': '/foo',
                   'room': 'room', 'host_id': 'x'}
            yield {'method': 'leave_room', 'sid': '123', 'namespace': '/foo',
                   'room': 'room', 'host_id': 'x'}
            yield 'bad json'
            yield b'bad pickled'

            # these should not publish anything on the queue, as they come from
            # the same host
            yield {'method': 'emit', 'value': 'foo', 'host_id': host_id}
            yield {'method': 'callback', 'value': 'bar', 'host_id': host_id}
            yield {'method': 'disconnect', 'sid': '123', 'namespace': '/foo',
                   'host_id': host_id}
            yield pickle.dumps({'method': 'close_room', 'value': 'baz',
                                'host_id': host_id})

        self.pm._listen = messages
        await self.pm._thread()

        self.pm._handle_emit.assert_awaited_once_with(
            {'method': 'emit', 'value': 'foo', 'host_id': 'x'}
        )
        self.pm._handle_callback.assert_any_await(
            {'method': 'callback', 'value': 'bar', 'host_id': 'x'}
        )
        self.pm._handle_callback.assert_any_await(
            {'method': 'callback', 'value': 'bar', 'host_id': host_id}
        )
        self.pm._handle_disconnect.assert_awaited_once_with(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo',
             'host_id': 'x'}
        )
        self.pm._handle_enter_room.assert_awaited_once_with(
            {'method': 'enter_room', 'sid': '123', 'namespace': '/foo',
             'room': 'room', 'host_id': 'x'}
        )
        self.pm._handle_leave_room.assert_awaited_once_with(
            {'method': 'leave_room', 'sid': '123', 'namespace': '/foo',
             'room': 'room', 'host_id': 'x'}
        )
        self.pm._handle_close_room.assert_awaited_once_with(
            {'method': 'close_room', 'value': 'baz', 'host_id': 'x'}
        )

    async def test_background_thread_exception(self):
        self.pm._handle_emit = mock.AsyncMock(side_effect=[
            ValueError(), asyncio.CancelledError])

        async def messages():
            yield {'method': 'emit', 'value': 'foo', 'host_id': 'x'}
            yield {'method': 'emit', 'value': 'bar', 'host_id': 'x'}

        self.pm._listen = messages
        await self.pm._thread()

        self.pm._handle_emit.assert_any_await(
            {'method': 'emit', 'value': 'foo', 'host_id': 'x'}
        )
        self.pm._handle_emit.assert_awaited_with(
            {'method': 'emit', 'value': 'bar', 'host_id': 'x'}
        )
