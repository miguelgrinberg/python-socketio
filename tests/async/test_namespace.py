from unittest import mock

from socketio import async_namespace


class TestAsyncNamespace:
    async def test_connect_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('connect', 'sid', {'foo': 'bar'})
        assert result['result'] == ('sid', {'foo': 'bar'})

    async def test_disconnect_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_disconnect(self, sid, reason):
                result['result'] = (sid, reason)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('disconnect', 'sid', 'foo')
        assert result['result'] == ('sid', 'foo')

    async def test_legacy_disconnect_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            def on_disconnect(self, sid):
                result['result'] = sid

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('disconnect', 'sid', 'foo')
        assert result['result'] == 'sid'

    async def test_legacy_disconnect_event_async(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_disconnect(self, sid):
                result['result'] = sid

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('disconnect', 'sid', 'foo')
        assert result['result'] == 'sid'

    async def test_sync_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('custom_message', 'sid', {'data': 'data'})
        assert result['result'] == ('sid', {'data': 'data'})

    async def test_async_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('custom_message', 'sid', {'data': 'data'})
        assert result['result'] == ('sid', {'data': 'data'})

    async def test_event_not_found(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        await ns.trigger_event('another_custom_message', 'sid',
                               {'data': 'data'})
        assert result == {}

    async def test_emit(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.emit = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.emit(
            'ev', data='data', to='room', skip_sid='skip', callback='cb'
        )
        ns.server.emit.assert_awaited_with(
            'ev',
            data='data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        await ns.emit(
            'ev',
            data='data',
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )
        ns.server.emit.assert_awaited_with(
            'ev',
            data='data',
            to=None,
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )

    async def test_send(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.send = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.send(data='data', to='room', skip_sid='skip', callback='cb')
        ns.server.send.assert_awaited_with(
            'data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        await ns.send(
            data='data',
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )
        ns.server.send.assert_awaited_with(
            'data',
            to=None,
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )

    async def test_call(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.call = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.call('ev', data='data', to='sid')
        ns.server.call.assert_awaited_with(
            'ev',
            data='data',
            to='sid',
            sid=None,
            namespace='/foo',
            timeout=None,
            ignore_queue=False,
        )
        await ns.call('ev', data='data', sid='sid', namespace='/bar',
                      timeout=45, ignore_queue=True)
        ns.server.call.assert_awaited_with(
            'ev',
            data='data',
            to=None,
            sid='sid',
            namespace='/bar',
            timeout=45,
            ignore_queue=True,
        )

    async def test_enter_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.enter_room = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.enter_room('sid', 'room')
        ns.server.enter_room.assert_awaited_with(
            'sid', 'room', namespace='/foo'
        )
        await ns.enter_room('sid', 'room', namespace='/bar')
        ns.server.enter_room.assert_awaited_with(
            'sid', 'room', namespace='/bar'
        )

    async def test_leave_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.leave_room = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.leave_room('sid', 'room')
        ns.server.leave_room.assert_awaited_with(
            'sid', 'room', namespace='/foo'
        )
        await ns.leave_room('sid', 'room', namespace='/bar')
        ns.server.leave_room.assert_awaited_with(
            'sid', 'room', namespace='/bar'
        )

    async def test_close_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.close_room = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.close_room('room')
        ns.server.close_room.assert_awaited_with('room', namespace='/foo')
        await ns.close_room('room', namespace='/bar')
        ns.server.close_room.assert_awaited_with('room', namespace='/bar')

    async def test_rooms(self):
        ns = async_namespace.AsyncNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.rooms('sid')
        ns.server.rooms.assert_called_with('sid', namespace='/foo')
        ns.rooms('sid', namespace='/bar')
        ns.server.rooms.assert_called_with('sid', namespace='/bar')

    async def test_session(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.get_session = mock.AsyncMock()
        mock_server.save_session = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.get_session('sid')
        ns.server.get_session.assert_awaited_with('sid', namespace='/foo')
        await ns.get_session('sid', namespace='/bar')
        ns.server.get_session.assert_awaited_with('sid', namespace='/bar')
        await ns.save_session('sid', {'a': 'b'})
        ns.server.save_session.assert_awaited_with(
            'sid', {'a': 'b'}, namespace='/foo'
        )
        await ns.save_session('sid', {'a': 'b'}, namespace='/bar')
        ns.server.save_session.assert_awaited_with(
            'sid', {'a': 'b'}, namespace='/bar'
        )
        ns.session('sid')
        ns.server.session.assert_called_with('sid', namespace='/foo')
        ns.session('sid', namespace='/bar')
        ns.server.session.assert_called_with('sid', namespace='/bar')

    async def test_disconnect(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.disconnect = mock.AsyncMock()
        ns._set_server(mock_server)
        await ns.disconnect('sid')
        ns.server.disconnect.assert_awaited_with('sid', namespace='/foo')
        await ns.disconnect('sid', namespace='/bar')
        ns.server.disconnect.assert_awaited_with('sid', namespace='/bar')

    async def test_disconnect_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_disconnect(self, reason):
                result['result'] = reason

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('disconnect', 'foo')
        assert result['result'] == 'foo'

    async def test_legacy_disconnect_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_disconnect(self):
                result['result'] = 'ok'

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('disconnect', 'foo')
        assert result['result'] == 'ok'

    async def test_legacy_disconnect_event_client_async(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_disconnect(self):
                result['result'] = 'ok'

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('disconnect', 'foo')
        assert result['result'] == 'ok'

    async def test_sync_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('custom_message', 'sid', {'data': 'data'})
        assert result['result'] == ('sid', {'data': 'data'})

    async def test_async_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('custom_message', 'sid', {'data': 'data'})
        assert result['result'] == ('sid', {'data': 'data'})

    async def test_event_not_found_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        await ns.trigger_event('another_custom_message', 'sid',
                               {'data': 'data'})
        assert result == {}

    async def test_emit_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.emit = mock.AsyncMock()
        ns._set_client(mock_client)
        await ns.emit('ev', data='data', callback='cb')
        ns.client.emit.assert_awaited_with(
            'ev', data='data', namespace='/foo', callback='cb'
        )
        await ns.emit('ev', data='data', namespace='/bar', callback='cb')
        ns.client.emit.assert_awaited_with(
            'ev', data='data', namespace='/bar', callback='cb'
        )

    async def test_send_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.send = mock.AsyncMock()
        ns._set_client(mock_client)
        await ns.send(data='data', callback='cb')
        ns.client.send.assert_awaited_with(
            'data', namespace='/foo', callback='cb'
        )
        await ns.send(data='data', namespace='/bar', callback='cb')
        ns.client.send.assert_awaited_with(
            'data', namespace='/bar', callback='cb'
        )

    async def test_call_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.call = mock.AsyncMock()
        ns._set_client(mock_client)
        await ns.call('ev', data='data')
        ns.client.call.assert_awaited_with(
            'ev', data='data', namespace='/foo', timeout=None
        )
        await ns.call('ev', data='data', namespace='/bar', timeout=45)
        ns.client.call.assert_awaited_with(
            'ev', data='data', namespace='/bar', timeout=45
        )

    async def test_disconnect_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.disconnect = mock.AsyncMock()
        ns._set_client(mock_client)
        await ns.disconnect()
        ns.client.disconnect.assert_awaited_with()
