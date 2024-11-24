from unittest import mock
import pytest
from socketio import SimpleClient
from socketio.exceptions import SocketIOError, TimeoutError, DisconnectedError


class TestSimpleClient:
    def test_constructor(self):
        client = SimpleClient(1, '2', a='3', b=4)
        assert client.client_args == (1, '2')
        assert client.client_kwargs == {'a': '3', 'b': 4}
        assert client.client is None
        assert client.input_buffer == []
        assert not client.connected

    def test_connect(self):
        client = SimpleClient(123, a='b')
        with mock.patch('socketio.simple_client.Client') as mock_client:
            client.connect('url', headers='h', auth='a', transports='t',
                           namespace='n', socketio_path='s', wait_timeout='w')
            mock_client.assert_called_once_with(123, a='b')
            assert client.client == mock_client()
            mock_client().connect.assert_called_once_with(
                'url', headers='h', auth='a', transports='t',
                namespaces=['n'], socketio_path='s', wait_timeout='w')
            mock_client().event.call_count == 3
            mock_client().on.assert_called_once_with('*', namespace='n')
            assert client.namespace == 'n'
            assert not client.input_event.is_set()

    def test_connect_context_manager(self):
        with SimpleClient(123, a='b') as client:
            with mock.patch('socketio.simple_client.Client') as mock_client:
                client.connect('url', headers='h', auth='a', transports='t',
                               namespace='n', socketio_path='s',
                               wait_timeout='w')
                mock_client.assert_called_once_with(123, a='b')
                assert client.client == mock_client()
                mock_client().connect.assert_called_once_with(
                    'url', headers='h', auth='a', transports='t',
                    namespaces=['n'], socketio_path='s', wait_timeout='w')
                mock_client().event.call_count == 3
                mock_client().on.assert_called_once_with('*', namespace='n')
                assert client.namespace == 'n'
                assert not client.input_event.is_set()

    def test_connect_twice(self):
        client = SimpleClient(123, a='b')
        client.client = mock.MagicMock()
        client.connected = True

        with pytest.raises(RuntimeError):
            client.connect('url')

    def test_properties(self):
        client = SimpleClient()
        client.client = mock.MagicMock(transport='websocket')
        client.client.get_sid.return_value = 'sid'
        client.connected_event.set()
        client.connected = True

        assert client.sid == 'sid'
        assert client.transport == 'websocket'

    def test_emit(self):
        client = SimpleClient()
        client.client = mock.MagicMock()
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        client.emit('foo', 'bar')
        client.client.emit.assert_called_once_with('foo', 'bar',
                                                   namespace='/ns')

    def test_emit_disconnected(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            client.emit('foo', 'bar')

    def test_emit_retries(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.emit.side_effect = [SocketIOError(), None]

        client.emit('foo', 'bar')
        client.client.emit.assert_called_with('foo', 'bar', namespace='/')

    def test_call(self):
        client = SimpleClient()
        client.client = mock.MagicMock()
        client.client.call.return_value = 'result'
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        assert client.call('foo', 'bar') == 'result'
        client.client.call.assert_called_once_with('foo', 'bar',
                                                   namespace='/ns', timeout=60)

    def test_call_disconnected(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            client.call('foo', 'bar')

    def test_call_retries(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.call.side_effect = [SocketIOError(), 'result']

        assert client.call('foo', 'bar') == 'result'
        client.client.call.assert_called_with('foo', 'bar', namespace='/',
                                              timeout=60)

    def test_receive_with_input_buffer(self):
        client = SimpleClient()
        client.input_buffer = ['foo', 'bar']
        assert client.receive() == 'foo'
        assert client.receive() == 'bar'

    def test_receive_without_input_buffer(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = True
        client.input_event = mock.MagicMock()

        def fake_wait(timeout=None):
            client.input_buffer = ['foo']
            return True

        client.input_event.wait = fake_wait
        assert client.receive() == 'foo'

    def test_receive_with_timeout(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = True
        with pytest.raises(TimeoutError):
            client.receive(timeout=0.01)

    def test_receive_disconnected(self):
        client = SimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            client.receive()

    def test_disconnect(self):
        client = SimpleClient()
        mc = mock.MagicMock()
        client.client = mc
        client.connected = True
        client.disconnect()
        client.disconnect()
        mc.disconnect.assert_called_once_with()
        assert client.client is None
