import sys
import unittest
from unittest import mock

from socketio import async_namespace
from .helpers import AsyncMock, _run


@unittest.skipIf(sys.version_info < (3, 5), 'only for Python 3.5+')
class TestAsyncNamespace(unittest.TestCase):
    def test_connect_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('connect', 'sid', {'foo': 'bar'}))
        assert result['result'] == ('sid', {'foo': 'bar'})

    def test_disconnect_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_disconnect(self, sid):
                result['result'] = sid

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('disconnect', 'sid'))
        assert result['result'] == 'sid'

    def test_sync_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        assert result['result'] == ('sid', {'data': 'data'})

    def test_async_event(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        assert result['result'] == ('sid', {'data': 'data'})

    def test_event_not_found(self):
        result = {}

        class MyNamespace(async_namespace.AsyncNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(
            ns.trigger_event('another_custom_message', 'sid', {'data': 'data'})
        )
        assert result == {}

    def test_emit(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.emit = AsyncMock()
        ns._set_server(mock_server)
        _run(
            ns.emit(
                'ev', data='data', to='room', skip_sid='skip', callback='cb'
            )
        )
        ns.server.emit.mock.assert_called_with(
            'ev',
            data='data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        _run(
            ns.emit(
                'ev',
                data='data',
                room='room',
                skip_sid='skip',
                namespace='/bar',
                callback='cb',
                ignore_queue=True,
            )
        )
        ns.server.emit.mock.assert_called_with(
            'ev',
            data='data',
            to=None,
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )

    def test_send(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.send = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.send(data='data', to='room', skip_sid='skip', callback='cb'))
        ns.server.send.mock.assert_called_with(
            'data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        _run(
            ns.send(
                data='data',
                room='room',
                skip_sid='skip',
                namespace='/bar',
                callback='cb',
                ignore_queue=True,
            )
        )
        ns.server.send.mock.assert_called_with(
            'data',
            to=None,
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )

    def test_call(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.call = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.call('ev', data='data', to='sid'))
        ns.server.call.mock.assert_called_with(
            'ev',
            data='data',
            to='sid',
            sid=None,
            namespace='/foo',
            timeout=None,
            ignore_queue=False,
        )
        _run(ns.call('ev', data='data', sid='sid', namespace='/bar',
                     timeout=45, ignore_queue=True))
        ns.server.call.mock.assert_called_with(
            'ev',
            data='data',
            to=None,
            sid='sid',
            namespace='/bar',
            timeout=45,
            ignore_queue=True,
        )

    def test_enter_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.enter_room = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.enter_room('sid', 'room'))
        ns.server.enter_room.mock.assert_called_with(
            'sid', 'room', namespace='/foo'
        )
        _run(ns.enter_room('sid', 'room', namespace='/bar'))
        ns.server.enter_room.mock.assert_called_with(
            'sid', 'room', namespace='/bar'
        )

    def test_leave_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.leave_room = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.leave_room('sid', 'room'))
        ns.server.leave_room.mock.assert_called_with(
            'sid', 'room', namespace='/foo'
        )
        _run(ns.leave_room('sid', 'room', namespace='/bar'))
        ns.server.leave_room.mock.assert_called_with(
            'sid', 'room', namespace='/bar'
        )

    def test_close_room(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.close_room = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.close_room('room'))
        ns.server.close_room.mock.assert_called_with('room', namespace='/foo')
        _run(ns.close_room('room', namespace='/bar'))
        ns.server.close_room.mock.assert_called_with('room', namespace='/bar')

    def test_rooms(self):
        ns = async_namespace.AsyncNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.rooms('sid')
        ns.server.rooms.assert_called_with('sid', namespace='/foo')
        ns.rooms('sid', namespace='/bar')
        ns.server.rooms.assert_called_with('sid', namespace='/bar')

    def test_session(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.get_session = AsyncMock()
        mock_server.save_session = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.get_session('sid'))
        ns.server.get_session.mock.assert_called_with('sid', namespace='/foo')
        _run(ns.get_session('sid', namespace='/bar'))
        ns.server.get_session.mock.assert_called_with('sid', namespace='/bar')
        _run(ns.save_session('sid', {'a': 'b'}))
        ns.server.save_session.mock.assert_called_with(
            'sid', {'a': 'b'}, namespace='/foo'
        )
        _run(ns.save_session('sid', {'a': 'b'}, namespace='/bar'))
        ns.server.save_session.mock.assert_called_with(
            'sid', {'a': 'b'}, namespace='/bar'
        )
        ns.session('sid')
        ns.server.session.assert_called_with('sid', namespace='/foo')
        ns.session('sid', namespace='/bar')
        ns.server.session.assert_called_with('sid', namespace='/bar')

    def test_disconnect(self):
        ns = async_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.disconnect = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.disconnect('sid'))
        ns.server.disconnect.mock.assert_called_with('sid', namespace='/foo')
        _run(ns.disconnect('sid', namespace='/bar'))
        ns.server.disconnect.mock.assert_called_with('sid', namespace='/bar')

    def test_sync_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        assert result['result'] == ('sid', {'data': 'data'})

    def test_async_event_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        assert result['result'] == ('sid', {'data': 'data'})

    def test_event_not_found_client(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            async def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        _run(
            ns.trigger_event('another_custom_message', 'sid', {'data': 'data'})
        )
        assert result == {}

    def test_emit_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.emit = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.emit('ev', data='data', callback='cb'))
        ns.client.emit.mock.assert_called_with(
            'ev', data='data', namespace='/foo', callback='cb'
        )
        _run(ns.emit('ev', data='data', namespace='/bar', callback='cb'))
        ns.client.emit.mock.assert_called_with(
            'ev', data='data', namespace='/bar', callback='cb'
        )

    def test_send_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.send = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.send(data='data', callback='cb'))
        ns.client.send.mock.assert_called_with(
            'data', namespace='/foo', callback='cb'
        )
        _run(ns.send(data='data', namespace='/bar', callback='cb'))
        ns.client.send.mock.assert_called_with(
            'data', namespace='/bar', callback='cb'
        )

    def test_call_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.call = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.call('ev', data='data'))
        ns.client.call.mock.assert_called_with(
            'ev', data='data', namespace='/foo', timeout=None
        )
        _run(ns.call('ev', data='data', namespace='/bar', timeout=45))
        ns.client.call.mock.assert_called_with(
            'ev', data='data', namespace='/bar', timeout=45
        )

    def test_disconnect_client(self):
        ns = async_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.disconnect = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.disconnect())
        ns.client.disconnect.mock.assert_called_with()
