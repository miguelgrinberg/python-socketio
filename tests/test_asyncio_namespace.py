import sys
import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

if sys.version_info >= (3, 5):
    import asyncio
    from asyncio import coroutine
    from socketio import asyncio_namespace
else:
    # mock coroutine so that Python 2 doesn't complain
    def coroutine(f):
        return f


def AsyncMock(*args, **kwargs):
    """Return a mock asynchronous function."""
    m = mock.MagicMock(*args, **kwargs)

    @coroutine
    def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


def _run(coro):
    """Run the given coroutine."""
    return asyncio.get_event_loop().run_until_complete(coro)


@unittest.skipIf(sys.version_info < (3, 5), 'only for Python 3.5+')
class TestAsyncNamespace(unittest.TestCase):
    def test_connect_event(self):
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            @coroutine
            def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('connect', 'sid', {'foo': 'bar'}))
        self.assertEqual(result['result'], ('sid', {'foo': 'bar'}))

    def test_disconnect_event(self):
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            @coroutine
            def on_disconnect(self, sid):
                result['result'] = sid

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('disconnect', 'sid'))
        self.assertEqual(result['result'], 'sid')

    def test_sync_event(self):
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        self.assertEqual(result['result'], ('sid', {'data': 'data'}))

    def test_async_event(self):
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            @coroutine
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('custom_message', 'sid', {'data': 'data'}))
        self.assertEqual(result['result'], ('sid', {'data': 'data'}))

    def test_event_not_found(self):
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            @coroutine
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        _run(ns.trigger_event('another_custom_message', 'sid',
                              {'data': 'data'}))
        self.assertEqual(result, {})

    def test_emit(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.emit = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.emit('ev', data='data', room='room', skip_sid='skip',
                     callback='cb'))
        ns.server.emit.mock.assert_called_with(
            'ev', data='data', room='room', skip_sid='skip', namespace='/foo',
            callback='cb')
        _run(ns.emit('ev', data='data', room='room', skip_sid='skip',
                     namespace='/bar', callback='cb'))
        ns.server.emit.mock.assert_called_with(
            'ev', data='data', room='room', skip_sid='skip', namespace='/bar',
            callback='cb')

    def test_send(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.send = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.send(data='data', room='room', skip_sid='skip', callback='cb'))
        ns.server.send.mock.assert_called_with(
            'data', room='room', skip_sid='skip', namespace='/foo',
            callback='cb')
        _run(ns.send(data='data', room='room', skip_sid='skip',
                     namespace='/bar', callback='cb'))
        ns.server.send.mock.assert_called_with(
            'data', room='room', skip_sid='skip', namespace='/bar',
            callback='cb')

    def test_enter_room(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.enter_room('sid', 'room')
        ns.server.enter_room.assert_called_with('sid', 'room',
                                                namespace='/foo')
        ns.enter_room('sid', 'room', namespace='/bar')
        ns.server.enter_room.assert_called_with('sid', 'room',
                                                namespace='/bar')

    def test_leave_room(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.leave_room('sid', 'room')
        ns.server.leave_room.assert_called_with('sid', 'room',
                                                namespace='/foo')
        ns.leave_room('sid', 'room', namespace='/bar')
        ns.server.leave_room.assert_called_with('sid', 'room',
                                                namespace='/bar')

    def test_close_room(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.close_room = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.close_room('room'))
        ns.server.close_room.mock.assert_called_with('room', namespace='/foo')
        _run(ns.close_room('room', namespace='/bar'))
        ns.server.close_room.mock.assert_called_with('room', namespace='/bar')

    def test_rooms(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.rooms('sid')
        ns.server.rooms.assert_called_with('sid', namespace='/foo')
        ns.rooms('sid', namespace='/bar')
        ns.server.rooms.assert_called_with('sid', namespace='/bar')

    def test_disconnect(self):
        ns = asyncio_namespace.AsyncNamespace('/foo')
        mock_server = mock.MagicMock()
        mock_server.disconnect = AsyncMock()
        ns._set_server(mock_server)
        _run(ns.disconnect('sid'))
        ns.server.disconnect.mock.assert_called_with('sid', namespace='/foo')
        _run(ns.disconnect('sid', namespace='/bar'))
        ns.server.disconnect.mock.assert_called_with('sid', namespace='/bar')

    def test_emit_client(self):
        ns = asyncio_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.emit = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.emit('ev', data='data', callback='cb'))
        ns.client.emit.mock.assert_called_with(
            'ev', data='data', namespace='/foo', callback='cb')
        _run(ns.emit('ev', data='data', namespace='/bar', callback='cb'))
        ns.client.emit.mock.assert_called_with(
            'ev', data='data', namespace='/bar', callback='cb')

    def test_send_client(self):
        ns = asyncio_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.send = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.send(data='data', callback='cb'))
        ns.client.send.mock.assert_called_with(
            'data', namespace='/foo', callback='cb')
        _run(ns.send(data='data', namespace='/bar', callback='cb'))
        ns.client.send.mock.assert_called_with(
            'data', namespace='/bar', callback='cb')

    def test_disconnect_client(self):
        ns = asyncio_namespace.AsyncClientNamespace('/foo')
        mock_client = mock.MagicMock()
        mock_client.disconnect = AsyncMock()
        ns._set_client(mock_client)
        _run(ns.disconnect())
        ns.client.disconnect.mock.assert_called_with(namespace='/foo')
        _run(ns.disconnect(namespace='/bar'))
        ns.client.disconnect.mock.assert_called_with(namespace='/bar')
