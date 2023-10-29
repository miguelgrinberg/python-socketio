import asyncio
import unittest
from unittest import mock
import pytest

from socketio import AsyncSimpleClient
from socketio.exceptions import SocketIOError, TimeoutError, DisconnectedError
from .helpers import AsyncMock, _run


class TestAsyncAsyncSimpleClient(unittest.TestCase):
    def test_constructor(self):
        client = AsyncSimpleClient(1, '2', a='3', b=4)
        assert client.client_args == (1, '2')
        assert client.client_kwargs == {'a': '3', 'b': 4}
        assert client.client is None
        assert client.input_buffer == []
        assert not client.connected

    def test_connect(self):
        client = AsyncSimpleClient(123, a='b')
        with mock.patch('socketio.async_simple_client.AsyncClient') \
                as mock_client:
            mock_client.return_value.connect = AsyncMock()

            _run(client.connect('url', headers='h', auth='a', transports='t',
                                namespace='n', socketio_path='s',
                                wait_timeout='w'))
            mock_client.assert_called_once_with(123, a='b')
            assert client.client == mock_client()
            mock_client().connect.mock.assert_called_once_with(
                'url', headers='h', auth='a', transports='t',
                namespaces=['n'], socketio_path='s', wait_timeout='w')
            mock_client().event.call_count == 3
            mock_client().on.assert_called_once_with('*', namespace='n')
            assert client.namespace == 'n'
            assert not client.input_event.is_set()

    def test_connect_context_manager(self):
        async def _t():
            async with AsyncSimpleClient(123, a='b') as client:
                with mock.patch('socketio.async_simple_client.AsyncClient') \
                        as mock_client:
                    mock_client.return_value.connect = AsyncMock()

                    await client.connect('url', headers='h', auth='a',
                                         transports='t', namespace='n',
                                         socketio_path='s', wait_timeout='w')
                    mock_client.assert_called_once_with(123, a='b')
                    assert client.client == mock_client()
                    mock_client().connect.mock.assert_called_once_with(
                        'url', headers='h', auth='a', transports='t',
                        namespaces=['n'], socketio_path='s', wait_timeout='w')
                    mock_client().event.call_count == 3
                    mock_client().on.assert_called_once_with(
                        '*', namespace='n')
                    assert client.namespace == 'n'
                    assert not client.input_event.is_set()

        _run(_t())

    def test_connect_twice(self):
        client = AsyncSimpleClient(123, a='b')
        client.client = mock.MagicMock()
        client.connected = True

        with pytest.raises(RuntimeError):
            _run(client.connect('url'))

    def test_properties(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock(transport='websocket')
        client.client.get_sid.return_value = 'sid'
        client.connected_event.set()
        client.connected = True

        assert client.sid == 'sid'
        assert client.transport == 'websocket'

    def test_emit(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock()
        client.client.emit = AsyncMock()
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        _run(client.emit('foo', 'bar'))
        client.client.emit.mock.assert_called_once_with('foo', 'bar',
                                                        namespace='/ns')

    def test_emit_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            _run(client.emit('foo', 'bar'))

    def test_emit_retries(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.emit = AsyncMock()
        client.client.emit.mock.side_effect = [SocketIOError(), None]

        _run(client.emit('foo', 'bar'))
        client.client.emit.mock.assert_called_with('foo', 'bar', namespace='/')

    def test_call(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock()
        client.client.call = AsyncMock()
        client.client.call.mock.return_value = 'result'
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        assert _run(client.call('foo', 'bar')) == 'result'
        client.client.call.mock.assert_called_once_with(
            'foo', 'bar', namespace='/ns', timeout=60)

    def test_call_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            _run(client.call('foo', 'bar'))

    def test_call_retries(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.call = AsyncMock()
        client.client.call.mock.side_effect = [SocketIOError(), 'result']

        assert _run(client.call('foo', 'bar')) == 'result'
        client.client.call.mock.assert_called_with('foo', 'bar', namespace='/',
                                                   timeout=60)

    def test_receive_with_input_buffer(self):
        client = AsyncSimpleClient()
        client.input_buffer = ['foo', 'bar']
        assert _run(client.receive()) == 'foo'
        assert _run(client.receive()) == 'bar'

    def test_receive_without_input_buffer(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.input_event = mock.MagicMock()

        async def fake_wait(timeout=None):
            client.input_buffer = ['foo']
            return True

        client.input_event.wait = fake_wait
        assert _run(client.receive()) == 'foo'

    def test_receive_with_timeout(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.input_event = mock.MagicMock()

        async def fake_wait(timeout=None):
            await asyncio.sleep(1)

        client.input_event.wait = fake_wait
        with pytest.raises(TimeoutError):
            _run(client.receive(timeout=0.01))

    def test_receive_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            _run(client.receive())

    def test_disconnect(self):
        client = AsyncSimpleClient()
        mc = mock.MagicMock()
        mc.disconnect = AsyncMock()
        client.client = mc
        client.connected = True
        _run(client.disconnect())
        _run(client.disconnect())
        mc.disconnect.mock.assert_called_once_with()
        assert client.client is None
