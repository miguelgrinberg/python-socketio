import asyncio
from unittest import mock
import pytest

from socketio import AsyncSimpleClient
from socketio.exceptions import SocketIOError, TimeoutError, DisconnectedError


class TestAsyncAsyncSimpleClient:
    async def test_constructor(self):
        client = AsyncSimpleClient(1, '2', a='3', b=4)
        assert client.client_args == (1, '2')
        assert client.client_kwargs == {'a': '3', 'b': 4}
        assert client.client is None
        assert client.input_buffer == []
        assert not client.connected

    async def test_connect(self):
        client = AsyncSimpleClient(123, a='b')
        with mock.patch('socketio.async_simple_client.AsyncClient') \
                as mock_client:
            mock_client.return_value.connect = mock.AsyncMock()

            await client.connect('url', headers='h', auth='a', transports='t',
                                 namespace='n', socketio_path='s',
                                 wait_timeout='w')
            mock_client.assert_called_once_with(123, a='b')
            assert client.client == mock_client()
            mock_client().connect.assert_awaited_once_with(
                'url', headers='h', auth='a', transports='t',
                namespaces=['n'], socketio_path='s', wait_timeout='w')
            mock_client().event.call_count == 3
            mock_client().on.assert_called_once_with('*', namespace='n')
            assert client.namespace == 'n'
            assert not client.input_event.is_set()

    async def test_connect_context_manager(self):
        async def _t():
            async with AsyncSimpleClient(123, a='b') as client:
                with mock.patch('socketio.async_simple_client.AsyncClient') \
                        as mock_client:
                    mock_client.return_value.connect = mock.AsyncMock()

                    await client.connect('url', headers='h', auth='a',
                                         transports='t', namespace='n',
                                         socketio_path='s', wait_timeout='w')
                    mock_client.assert_called_once_with(123, a='b')
                    assert client.client == mock_client()
                    mock_client().connect.assert_awaited_once_with(
                        'url', headers='h', auth='a', transports='t',
                        namespaces=['n'], socketio_path='s', wait_timeout='w')
                    mock_client().event.call_count == 3
                    mock_client().on.assert_called_once_with(
                        '*', namespace='n')
                    assert client.namespace == 'n'
                    assert not client.input_event.is_set()

        await _t()

    async def test_connect_twice(self):
        client = AsyncSimpleClient(123, a='b')
        client.client = mock.MagicMock()
        client.connected = True

        with pytest.raises(RuntimeError):
            await client.connect('url')

    async def test_properties(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock(transport='websocket')
        client.client.get_sid.return_value = 'sid'
        client.connected_event.set()
        client.connected = True

        assert client.sid == 'sid'
        assert client.transport == 'websocket'

    async def test_emit(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock()
        client.client.emit = mock.AsyncMock()
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        await client.emit('foo', 'bar')
        client.client.emit.assert_awaited_once_with('foo', 'bar',
                                                    namespace='/ns')

    async def test_emit_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            await client.emit('foo', 'bar')

    async def test_emit_retries(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.emit = mock.AsyncMock()
        client.client.emit.side_effect = [SocketIOError(), None]

        await client.emit('foo', 'bar')
        client.client.emit.assert_awaited_with('foo', 'bar', namespace='/')

    async def test_call(self):
        client = AsyncSimpleClient()
        client.client = mock.MagicMock()
        client.client.call = mock.AsyncMock()
        client.client.call.return_value = 'result'
        client.namespace = '/ns'
        client.connected_event.set()
        client.connected = True

        assert await client.call('foo', 'bar') == 'result'
        client.client.call.assert_awaited_once_with(
            'foo', 'bar', namespace='/ns', timeout=60)

    async def test_call_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            await client.call('foo', 'bar')

    async def test_call_retries(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.client = mock.MagicMock()
        client.client.call = mock.AsyncMock()
        client.client.call.side_effect = [SocketIOError(), 'result']

        assert await client.call('foo', 'bar') == 'result'
        client.client.call.assert_awaited_with('foo', 'bar', namespace='/',
                                               timeout=60)

    async def test_receive_with_input_buffer(self):
        client = AsyncSimpleClient()
        client.input_buffer = ['foo', 'bar']
        assert await client.receive() == 'foo'
        assert await client.receive() == 'bar'

    async def test_receive_without_input_buffer(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.input_event = mock.MagicMock()

        async def fake_wait(timeout=None):
            client.input_buffer = ['foo']
            return True

        client.input_event.wait = fake_wait
        assert await client.receive() == 'foo'

    async def test_receive_with_timeout(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = True
        client.input_event = mock.MagicMock()

        async def fake_wait(timeout=None):
            await asyncio.sleep(1)

        client.input_event.wait = fake_wait
        with pytest.raises(TimeoutError):
            await client.receive(timeout=0.01)

    async def test_receive_disconnected(self):
        client = AsyncSimpleClient()
        client.connected_event.set()
        client.connected = False
        with pytest.raises(DisconnectedError):
            await client.receive()

    async def test_disconnect(self):
        client = AsyncSimpleClient()
        mc = mock.MagicMock()
        mc.disconnect = mock.AsyncMock()
        client.client = mc
        client.connected = True
        await client.disconnect()
        await client.disconnect()
        mc.disconnect.assert_awaited_once_with()
        assert client.client is None
