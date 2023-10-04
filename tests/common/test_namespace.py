import unittest
from unittest import mock

from socketio import namespace


class TestNamespace(unittest.TestCase):
    def test_connect_event(self):
        result = {}

        class MyNamespace(namespace.Namespace):
            def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.trigger_event('connect', 'sid', {'foo': 'bar'})
        assert result['result'] == ('sid', {'foo': 'bar'})

    def test_disconnect_event(self):
        result = {}

        class MyNamespace(namespace.Namespace):
            def on_disconnect(self, sid):
                result['result'] = sid

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.trigger_event('disconnect', 'sid')
        assert result['result'] == 'sid'

    def test_event(self):
        result = {}

        class MyNamespace(namespace.Namespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.trigger_event('custom_message', 'sid', {'data': 'data'})
        assert result['result'] == ('sid', {'data': 'data'})

    def test_event_not_found(self):
        result = {}

        class MyNamespace(namespace.Namespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.trigger_event('another_custom_message', 'sid', {'data': 'data'})
        assert result == {}

    def test_emit(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.emit('ev', data='data', to='room', skip_sid='skip', callback='cb')
        ns.server.emit.assert_called_with(
            'ev',
            data='data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        ns.emit(
            'ev',
            data='data',
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )
        ns.server.emit.assert_called_with(
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
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.send(data='data', to='room', skip_sid='skip', callback='cb')
        ns.server.send.assert_called_with(
            'data',
            to='room',
            room=None,
            skip_sid='skip',
            namespace='/foo',
            callback='cb',
            ignore_queue=False,
        )
        ns.send(
            data='data',
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )
        ns.server.send.assert_called_with(
            'data',
            to=None,
            room='room',
            skip_sid='skip',
            namespace='/bar',
            callback='cb',
            ignore_queue=True,
        )

    def test_call(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.call('ev', data='data', to='sid')
        ns.server.call.assert_called_with(
            'ev',
            data='data',
            to='sid',
            sid=None,
            namespace='/foo',
            timeout=None,
            ignore_queue=False,
        )
        ns.call(
            'ev',
            data='data',
            sid='sid',
            namespace='/bar',
            timeout=45,
            ignore_queue=True,
        )
        ns.server.call.assert_called_with(
            'ev',
            data='data',
            to=None,
            sid='sid',
            namespace='/bar',
            timeout=45,
            ignore_queue=True,
        )

    def test_enter_room(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.enter_room('sid', 'room')
        ns.server.enter_room.assert_called_with(
            'sid', 'room', namespace='/foo'
        )
        ns.enter_room('sid', 'room', namespace='/bar')
        ns.server.enter_room.assert_called_with(
            'sid', 'room', namespace='/bar'
        )

    def test_leave_room(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.leave_room('sid', 'room')
        ns.server.leave_room.assert_called_with(
            'sid', 'room', namespace='/foo'
        )
        ns.leave_room('sid', 'room', namespace='/bar')
        ns.server.leave_room.assert_called_with(
            'sid', 'room', namespace='/bar'
        )

    def test_close_room(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.close_room('room')
        ns.server.close_room.assert_called_with('room', namespace='/foo')
        ns.close_room('room', namespace='/bar')
        ns.server.close_room.assert_called_with('room', namespace='/bar')

    def test_rooms(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.rooms('sid')
        ns.server.rooms.assert_called_with('sid', namespace='/foo')
        ns.rooms('sid', namespace='/bar')
        ns.server.rooms.assert_called_with('sid', namespace='/bar')

    def test_session(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.get_session('sid')
        ns.server.get_session.assert_called_with('sid', namespace='/foo')
        ns.get_session('sid', namespace='/bar')
        ns.server.get_session.assert_called_with('sid', namespace='/bar')
        ns.save_session('sid', {'a': 'b'})
        ns.server.save_session.assert_called_with(
            'sid', {'a': 'b'}, namespace='/foo'
        )
        ns.save_session('sid', {'a': 'b'}, namespace='/bar')
        ns.server.save_session.assert_called_with(
            'sid', {'a': 'b'}, namespace='/bar'
        )
        ns.session('sid')
        ns.server.session.assert_called_with('sid', namespace='/foo')
        ns.session('sid', namespace='/bar')
        ns.server.session.assert_called_with('sid', namespace='/bar')

    def test_disconnect(self):
        ns = namespace.Namespace('/foo')
        ns._set_server(mock.MagicMock())
        ns.disconnect('sid')
        ns.server.disconnect.assert_called_with('sid', namespace='/foo')
        ns.disconnect('sid', namespace='/bar')
        ns.server.disconnect.assert_called_with('sid', namespace='/bar')

    def test_event_not_found_client(self):
        result = {}

        class MyNamespace(namespace.ClientNamespace):
            def on_custom_message(self, sid, data):
                result['result'] = (sid, data)

        ns = MyNamespace('/foo')
        ns._set_client(mock.MagicMock())
        ns.trigger_event('another_custom_message', 'sid', {'data': 'data'})
        assert result == {}

    def test_emit_client(self):
        ns = namespace.ClientNamespace('/foo')
        ns._set_client(mock.MagicMock())
        ns.emit('ev', data='data', callback='cb')
        ns.client.emit.assert_called_with(
            'ev', data='data', namespace='/foo', callback='cb'
        )
        ns.emit('ev', data='data', namespace='/bar', callback='cb')
        ns.client.emit.assert_called_with(
            'ev', data='data', namespace='/bar', callback='cb'
        )

    def test_send_client(self):
        ns = namespace.ClientNamespace('/foo')
        ns._set_client(mock.MagicMock())
        ns.send(data='data', callback='cb')
        ns.client.send.assert_called_with(
            'data', namespace='/foo', callback='cb'
        )
        ns.send(data='data', namespace='/bar', callback='cb')
        ns.client.send.assert_called_with(
            'data', namespace='/bar', callback='cb'
        )

    def test_call_client(self):
        ns = namespace.ClientNamespace('/foo')
        ns._set_client(mock.MagicMock())
        ns.call('ev', data='data')
        ns.client.call.assert_called_with(
            'ev', data='data', namespace='/foo', timeout=None)
        ns.call('ev', data='data', namespace='/bar', timeout=45)
        ns.client.call.assert_called_with(
            'ev', data='data', namespace='/bar', timeout=45
        )

    def test_disconnect_client(self):
        ns = namespace.ClientNamespace('/foo')
        ns._set_client(mock.MagicMock())
        ns.disconnect()
        ns.client.disconnect.assert_called_with()
