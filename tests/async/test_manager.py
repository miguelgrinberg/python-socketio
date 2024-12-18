from unittest import mock

from socketio import async_manager
from socketio import packet


class TestAsyncManager:
    def setup_method(self):
        id = 0

        def generate_id():
            nonlocal id
            id += 1
            return str(id)

        mock_server = mock.MagicMock()
        mock_server._send_packet = mock.AsyncMock()
        mock_server._send_eio_packet = mock.AsyncMock()
        mock_server.eio.generate_id = generate_id
        mock_server.packet_class = packet.Packet
        self.bm = async_manager.AsyncManager()
        self.bm.set_server(mock_server)
        self.bm.initialize()

    async def test_connect(self):
        sid = await self.bm.connect('123', '/foo')
        assert None in self.bm.rooms['/foo']
        assert sid in self.bm.rooms['/foo']
        assert sid in self.bm.rooms['/foo'][None]
        assert sid in self.bm.rooms['/foo'][sid]
        assert dict(self.bm.rooms['/foo'][None]) == {sid: '123'}
        assert dict(self.bm.rooms['/foo'][sid]) == {sid: '123'}
        assert self.bm.sid_from_eio_sid('123', '/foo') == sid

    async def test_pre_disconnect(self):
        sid1 = await self.bm.connect('123', '/foo')
        sid2 = await self.bm.connect('456', '/foo')
        assert self.bm.is_connected(sid1, '/foo')
        assert self.bm.pre_disconnect(sid1, '/foo') == '123'
        assert self.bm.pending_disconnect == {'/foo': [sid1]}
        assert not self.bm.is_connected(sid1, '/foo')
        assert self.bm.pre_disconnect(sid2, '/foo') == '456'
        assert self.bm.pending_disconnect == {'/foo': [sid1, sid2]}
        assert not self.bm.is_connected(sid2, '/foo')
        await self.bm.disconnect(sid1, '/foo')
        assert self.bm.pending_disconnect == {'/foo': [sid2]}
        await self.bm.disconnect(sid2, '/foo')
        assert self.bm.pending_disconnect == {}

    async def test_disconnect(self):
        sid1 = await self.bm.connect('123', '/foo')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        await self.bm.enter_room(sid2, '/foo', 'baz')
        await self.bm.disconnect(sid1, '/foo')
        assert dict(self.bm.rooms['/foo'][None]) == {sid2: '456'}
        assert dict(self.bm.rooms['/foo'][sid2]) == {sid2: '456'}
        assert dict(self.bm.rooms['/foo']['baz']) == {sid2: '456'}

    async def test_disconnect_default_namespace(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('123', '/foo')
        sid3 = await self.bm.connect('456', '/')
        sid4 = await self.bm.connect('456', '/foo')
        assert self.bm.is_connected(sid1, '/')
        assert self.bm.is_connected(sid2, '/foo')
        assert not self.bm.is_connected(sid2, '/')
        assert not self.bm.is_connected(sid1, '/foo')
        await self.bm.disconnect(sid1, '/')
        assert not self.bm.is_connected(sid1, '/')
        assert self.bm.is_connected(sid2, '/foo')
        await self.bm.disconnect(sid2, '/foo')
        assert not self.bm.is_connected(sid2, '/foo')
        assert dict(self.bm.rooms['/'][None]) == {sid3: '456'}
        assert dict(self.bm.rooms['/'][sid3]) == {sid3: '456'}
        assert dict(self.bm.rooms['/foo'][None]) == {sid4: '456'}
        assert dict(self.bm.rooms['/foo'][sid4]) == {sid4: '456'}

    async def test_disconnect_twice(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('123', '/foo')
        sid3 = await self.bm.connect('456', '/')
        sid4 = await self.bm.connect('456', '/foo')
        await self.bm.disconnect(sid1, '/')
        await self.bm.disconnect(sid2, '/foo')
        await self.bm.disconnect(sid1, '/')
        await self.bm.disconnect(sid2, '/foo')
        assert dict(self.bm.rooms['/'][None]) == {sid3: '456'}
        assert dict(self.bm.rooms['/'][sid3]) == {sid3: '456'}
        assert dict(self.bm.rooms['/foo'][None]) == {sid4: '456'}
        assert dict(self.bm.rooms['/foo'][sid4]) == {sid4: '456'}

    async def test_disconnect_all(self):
        sid1 = await self.bm.connect('123', '/foo')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        await self.bm.enter_room(sid2, '/foo', 'baz')
        await self.bm.disconnect(sid1, '/foo')
        await self.bm.disconnect(sid2, '/foo')
        assert self.bm.rooms == {}

    async def test_disconnect_with_callbacks(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('123', '/foo')
        sid3 = await self.bm.connect('456', '/foo')
        self.bm._generate_ack_id(sid1, 'f')
        self.bm._generate_ack_id(sid2, 'g')
        self.bm._generate_ack_id(sid3, 'h')
        await self.bm.disconnect(sid2, '/foo')
        assert sid2 not in self.bm.callbacks
        await self.bm.disconnect(sid1, '/')
        assert sid1 not in self.bm.callbacks
        assert sid3 in self.bm.callbacks

    async def test_trigger_sync_callback(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('123', '/foo')
        cb = mock.MagicMock()
        id1 = self.bm._generate_ack_id(sid1, cb)
        id2 = self.bm._generate_ack_id(sid2, cb)
        await self.bm.trigger_callback(sid1, id1, ['foo'])
        await self.bm.trigger_callback(sid2, id2, ['bar', 'baz'])
        assert cb.call_count == 2
        cb.assert_any_call('foo')
        cb.assert_any_call('bar', 'baz')

    async def test_trigger_async_callback(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('123', '/foo')
        cb = mock.AsyncMock()
        id1 = self.bm._generate_ack_id(sid1, cb)
        id2 = self.bm._generate_ack_id(sid2, cb)
        await self.bm.trigger_callback(sid1, id1, ['foo'])
        await self.bm.trigger_callback(sid2, id2, ['bar', 'baz'])
        assert cb.await_count == 2
        cb.assert_any_await('foo')
        cb.assert_any_await('bar', 'baz')

    async def test_invalid_callback(self):
        sid = await self.bm.connect('123', '/')
        cb = mock.MagicMock()
        id = self.bm._generate_ack_id(sid, cb)

        # these should not raise an exception
        await self.bm.trigger_callback('xxx', id, ['foo'])
        await self.bm.trigger_callback(sid, id + 1, ['foo'])
        assert cb.call_count == 0

    async def test_get_namespaces(self):
        assert list(self.bm.get_namespaces()) == []
        await self.bm.connect('123', '/')
        await self.bm.connect('123', '/foo')
        namespaces = list(self.bm.get_namespaces())
        assert len(namespaces) == 2
        assert '/' in namespaces
        assert '/foo' in namespaces

    async def test_get_participants(self):
        sid1 = await self.bm.connect('123', '/')
        sid2 = await self.bm.connect('456', '/')
        sid3 = await self.bm.connect('789', '/')
        await self.bm.disconnect(sid3, '/')
        assert sid3 not in self.bm.rooms['/'][None]
        participants = list(self.bm.get_participants('/', None))
        assert len(participants) == 2
        assert (sid1, '123') in participants
        assert (sid2, '456') in participants
        assert (sid3, '789') not in participants

    async def test_leave_invalid_room(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.leave_room(sid, '/foo', 'baz')
        await self.bm.leave_room(sid, '/bar', 'baz')

    async def test_no_room(self):
        rooms = self.bm.get_rooms('123', '/foo')
        assert [] == rooms

    async def test_close_room(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.connect('456', '/foo')
        await self.bm.connect('789', '/foo')
        await self.bm.enter_room(sid, '/foo', 'bar')
        await self.bm.enter_room(sid, '/foo', 'bar')
        await self.bm.close_room('bar', '/foo')
        assert 'bar' not in self.bm.rooms['/foo']

    async def test_close_invalid_room(self):
        self.bm.close_room('bar', '/foo')

    async def test_rooms(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid, '/foo', 'bar')
        r = self.bm.get_rooms(sid, '/foo')
        assert len(r) == 2
        assert sid in r
        assert 'bar' in r

    async def test_emit_to_sid(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.connect('456', '/foo')
        await self.bm.emit(
            'my event', {'foo': 'bar'}, namespace='/foo', to=sid
        )
        assert self.bm.server._send_eio_packet.await_count == 1
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_to_room(self):
        sid1 = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid2, '/foo', 'bar')
        await self.bm.connect('789', '/foo')
        await self.bm.emit(
            'my event', {'foo': 'bar'}, namespace='/foo', room='bar'
        )
        assert self.bm.server._send_eio_packet.await_count == 2
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        assert self.bm.server._send_eio_packet.await_args_list[1][0][0] \
            == '456'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert self.bm.server._send_eio_packet.await_args_list[1][0][1] \
            == pkt
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_to_rooms(self):
        sid1 = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid2, '/foo', 'bar')
        await self.bm.enter_room(sid2, '/foo', 'baz')
        sid3 = await self.bm.connect('789', '/foo')
        await self.bm.enter_room(sid3, '/foo', 'baz')
        await self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo',
                           room=['bar', 'baz'])
        assert self.bm.server._send_eio_packet.await_count == 3
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        assert self.bm.server._send_eio_packet.await_args_list[1][0][0] \
            == '456'
        assert self.bm.server._send_eio_packet.await_args_list[2][0][0] \
            == '789'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert self.bm.server._send_eio_packet.await_args_list[1][0][1] \
            == pkt
        assert self.bm.server._send_eio_packet.await_args_list[2][0][1] \
            == pkt
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_to_all(self):
        sid1 = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid2, '/foo', 'bar')
        await self.bm.connect('789', '/foo')
        await self.bm.connect('abc', '/bar')
        await self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo')
        assert self.bm.server._send_eio_packet.await_count == 3
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        assert self.bm.server._send_eio_packet.await_args_list[1][0][0] \
            == '456'
        assert self.bm.server._send_eio_packet.await_args_list[2][0][0] \
            == '789'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert self.bm.server._send_eio_packet.await_args_list[1][0][1] \
            == pkt
        assert self.bm.server._send_eio_packet.await_args_list[2][0][1] \
            == pkt
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_to_all_skip_one(self):
        sid1 = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid2, '/foo', 'bar')
        await self.bm.connect('789', '/foo')
        await self.bm.connect('abc', '/bar')
        await self.bm.emit(
            'my event', {'foo': 'bar'}, namespace='/foo', skip_sid=sid2
        )
        assert self.bm.server._send_eio_packet.await_count == 2
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        assert self.bm.server._send_eio_packet.await_args_list[1][0][0] \
            == '789'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert self.bm.server._send_eio_packet.await_args_list[1][0][1] \
            == pkt
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_to_all_skip_two(self):
        sid1 = await self.bm.connect('123', '/foo')
        await self.bm.enter_room(sid1, '/foo', 'bar')
        sid2 = await self.bm.connect('456', '/foo')
        await self.bm.enter_room(sid2, '/foo', 'bar')
        sid3 = await self.bm.connect('789', '/foo')
        await self.bm.connect('abc', '/bar')
        await self.bm.emit(
            'my event',
            {'foo': 'bar'},
            namespace='/foo',
            skip_sid=[sid1, sid3],
        )
        assert self.bm.server._send_eio_packet.await_count == 1
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '456'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42/foo,["my event",{"foo":"bar"}]'

    async def test_emit_with_callback(self):
        sid = await self.bm.connect('123', '/foo')
        self.bm._generate_ack_id = mock.MagicMock()
        self.bm._generate_ack_id.return_value = 11
        await self.bm.emit(
            'my event', {'foo': 'bar'}, namespace='/foo', callback='cb'
        )
        self.bm._generate_ack_id.assert_called_once_with(sid, 'cb')
        assert self.bm.server._send_packet.await_count == 1
        assert self.bm.server._send_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_packet.await_args_list[0][0][1]
        assert pkt.encode() == '2/foo,11["my event",{"foo":"bar"}]'

    async def test_emit_to_invalid_room(self):
        await self.bm.emit('my event', {'foo': 'bar'}, namespace='/',
                           room='123')

    async def test_emit_to_invalid_namespace(self):
        await self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo')

    async def test_emit_with_tuple(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.emit(
            'my event', ('foo', 'bar'), namespace='/foo', room=sid
        )
        assert self.bm.server._send_eio_packet.await_count == 1
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42/foo,["my event","foo","bar"]'

    async def test_emit_with_list(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.emit(
            'my event', ['foo', 'bar'], namespace='/foo', room=sid
        )
        assert self.bm.server._send_eio_packet.await_count == 1
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42/foo,["my event",["foo","bar"]]'

    async def test_emit_with_none(self):
        sid = await self.bm.connect('123', '/foo')
        await self.bm.emit(
            'my event', None, namespace='/foo', room=sid
        )
        assert self.bm.server._send_eio_packet.await_count == 1
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '42/foo,["my event"]'

    async def test_emit_binary(self):
        sid = await self.bm.connect('123', '/')
        await self.bm.emit(
            'my event', b'my binary data', namespace='/', room=sid
        )
        assert self.bm.server._send_eio_packet.await_count == 2
        assert self.bm.server._send_eio_packet.await_args_list[0][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[0][0][1]
        assert pkt.encode() == '451-["my event",{"_placeholder":true,"num":0}]'
        assert self.bm.server._send_eio_packet.await_args_list[1][0][0] \
            == '123'
        pkt = self.bm.server._send_eio_packet.await_args_list[1][0][1]
        assert pkt.encode() == b'my binary data'
