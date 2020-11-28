import asyncio
from contextlib import contextmanager
import sys
import unittest

import six

if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import asyncio_client
from socketio import asyncio_namespace
from engineio import exceptions as engineio_exceptions
from socketio import exceptions
from socketio import packet
import pytest


def AsyncMock(*args, **kwargs):
    """Return a mock asynchronous function."""
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


@contextmanager
def mock_wait_for():
    async def fake_wait_for(coro, timeout):
        await coro
        await fake_wait_for._mock(timeout)

    original_wait_for = asyncio.wait_for
    asyncio.wait_for = fake_wait_for
    fake_wait_for._mock = AsyncMock()
    yield
    asyncio.wait_for = original_wait_for


def _run(coro):
    """Run the given coroutine."""
    return asyncio.get_event_loop().run_until_complete(coro)


@unittest.skipIf(sys.version_info < (3, 5), 'only for Python 3.5+')
class TestAsyncClient(unittest.TestCase):
    def test_is_asyncio_based(self):
        c = asyncio_client.AsyncClient()
        assert c.is_asyncio_based()

    def test_connect(self):
        c = asyncio_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                namespaces=['/foo', '/', '/bar'],
                socketio_path='path',
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo', '/', '/bar']
        assert c.socketio_path == 'path'
        assert c.namespaces == ['/foo', '/bar']
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_one_namespace(self):
        c = asyncio_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                namespaces='/foo',
                socketio_path='path',
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo']
        assert c.socketio_path == 'path'
        assert c.namespaces == ['/foo']
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_default_namespaces(self):
        c = asyncio_client.AsyncClient()
        c.eio.connect = AsyncMock()
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                socketio_path='path',
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces is None
        assert c.socketio_path == 'path'
        assert c.namespaces == ['/foo']
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_error(self):
        c = asyncio_client.AsyncClient()
        c.eio.connect = AsyncMock(
            side_effect=engineio_exceptions.ConnectionError('foo')
        )
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        with pytest.raises(exceptions.ConnectionError):
            _run(
                c.connect(
                    'url',
                    headers='headers',
                    transports='transports',
                    socketio_path='path',
                )
            )

    def test_wait_no_reconnect(self):
        c = asyncio_client.AsyncClient()
        c.eio.wait = AsyncMock()
        c.sleep = AsyncMock()
        c._reconnect_task = None
        _run(c.wait())
        c.eio.wait.mock.assert_called_once_with()
        c.sleep.mock.assert_called_once_with(1)

    def test_wait_reconnect_failed(self):
        c = asyncio_client.AsyncClient()
        c.eio.wait = AsyncMock()
        c.sleep = AsyncMock()
        states = ['disconnected']

        async def fake_wait():
            c.eio.state = states.pop(0)

        c._reconnect_task = fake_wait()
        _run(c.wait())
        c.eio.wait.mock.assert_called_once_with()
        c.sleep.mock.assert_called_once_with(1)

    def test_wait_reconnect_successful(self):
        c = asyncio_client.AsyncClient()
        c.eio.wait = AsyncMock()
        c.sleep = AsyncMock()
        states = ['connected', 'disconnected']

        async def fake_wait():
            c.eio.state = states.pop(0)
            c._reconnect_task = fake_wait()

        c._reconnect_task = fake_wait()
        _run(c.wait())
        assert c.eio.wait.mock.call_count == 2
        assert c.sleep.mock.call_count == 2

    def test_emit_no_arguments(self):
        c = asyncio_client.AsyncClient()
        c._send_packet = AsyncMock()
        _run(c.emit('foo'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=None, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_one_argument(self):
        c = asyncio_client.AsyncClient()
        c._send_packet = AsyncMock()
        _run(c.emit('foo', 'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
            binary=False,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_one_argument_list(self):
        c = asyncio_client.AsyncClient()
        c._send_packet = AsyncMock()
        _run(c.emit('foo', ['bar', 'baz']))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', ['bar', 'baz']],
            id=None,
            binary=False,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_two_arguments(self):
        c = asyncio_client.AsyncClient()
        c._send_packet = AsyncMock()
        _run(c.emit('foo', ('bar', 'baz')))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar', 'baz'],
            id=None,
            binary=False,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_namespace(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo']
        c._send_packet = AsyncMock()
        _run(c.emit('foo', namespace='/foo'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=None, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_unknown_namespace(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo']
        with pytest.raises(exceptions.BadNamespaceError):
            _run(c.emit('foo', namespace='/bar'))

    def test_emit_with_callback(self):
        c = asyncio_client.AsyncClient()
        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        _run(c.emit('foo', callback='cb'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/', 'cb')

    def test_emit_namespace_with_callback(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo']
        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        _run(c.emit('foo', namespace='/foo', callback='cb'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=123, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/foo', 'cb')

    def test_emit_binary(self):
        c = asyncio_client.AsyncClient(binary=True)
        c._send_packet = AsyncMock()
        _run(c.emit('foo', b'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', b'bar'],
            id=None,
            binary=True,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_not_binary(self):
        c = asyncio_client.AsyncClient(binary=False)
        c._send_packet = AsyncMock()
        _run(c.emit('foo', 'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
            binary=False,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_send(self):
        c = asyncio_client.AsyncClient()
        c.emit = AsyncMock()
        _run(c.send('data', 'namespace', 'callback'))
        c.emit.mock.assert_called_once_with(
            'message', data='data', namespace='namespace', callback='callback'
        )

    def test_send_with_defaults(self):
        c = asyncio_client.AsyncClient()
        c.emit = AsyncMock()
        _run(c.send('data'))
        c.emit.mock.assert_called_once_with(
            'message', data='data', namespace=None, callback=None
        )

    def test_call(self):
        c = asyncio_client.AsyncClient()

        async def fake_event_wait():
            c._generate_ack_id.call_args_list[0][0][1]('foo', 321)

        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        assert _run(c.call('foo')) == ('foo', 321)
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_call_with_timeout(self):
        c = asyncio_client.AsyncClient()

        async def fake_event_wait():
            await asyncio.sleep(1)

        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        with pytest.raises(exceptions.TimeoutError):
            _run(c.call('foo', timeout=0.01))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123, binary=False
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_disconnect(self):
        c = asyncio_client.AsyncClient()
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.disconnect())
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c.eio.disconnect.mock.assert_called_once_with(abort=True)

    def test_disconnect_namespaces(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.disconnect())
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 3
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/foo')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/bar')
        assert (
            c._send_packet.mock.call_args_list[1][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.mock.call_args_list[2][0][0].encode()
            == expected_packet.encode()
        )

    def test_start_background_task(self):
        c = asyncio_client.AsyncClient()
        c.eio.start_background_task = mock.MagicMock(return_value='foo')
        assert c.start_background_task('foo', 'bar', baz='baz') == 'foo'
        c.eio.start_background_task.assert_called_once_with(
            'foo', 'bar', baz='baz'
        )

    def test_sleep(self):
        c = asyncio_client.AsyncClient()
        c.eio.sleep = AsyncMock()
        _run(c.sleep(1.23))
        c.eio.sleep.mock.assert_called_once_with(1.23)

    def test_send_packet(self):
        c = asyncio_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, 'foo', binary=False)))
        c.eio.send.mock.assert_called_once_with('2"foo"', binary=False)

    def test_send_packet_binary(self):
        c = asyncio_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, b'foo', binary=True)))
        assert c.eio.send.mock.call_args_list == [
            mock.call('51-{"_placeholder":true,"num":0}', binary=False),
            mock.call(b'foo', binary=True),
        ] or c.eio.send.mock.call_args_list == [
            mock.call('51-{"num":0,"_placeholder":true}', binary=False),
            mock.call(b'foo', binary=True),
        ]

    def test_send_packet_default_binary_py3(self):
        c = asyncio_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, 'foo')))
        c.eio.send.mock.assert_called_once_with('2"foo"', binary=False)

    def test_handle_connect(self):
        c = asyncio_client.AsyncClient()
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/'))
        c._trigger_event.mock.assert_called_once_with('connect', namespace='/')
        c._send_packet.mock.assert_not_called()

    def test_handle_connect_with_namespaces(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/'))
        c._trigger_event.mock.assert_called_once_with('connect', namespace='/')
        assert c._send_packet.mock.call_count == 2
        expected_packet = packet.Packet(packet.CONNECT, namespace='/foo')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(packet.CONNECT, namespace='/bar')
        assert (
            c._send_packet.mock.call_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_connect_namespace(self):
        c = asyncio_client.AsyncClient()
        c.namespaces = ['/foo']
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/foo'))
        _run(c._handle_connect('/bar'))
        assert c._trigger_event.mock.call_args_list == [
            mock.call('connect', namespace='/foo'),
            mock.call('connect', namespace='/bar'),
        ]
        c._send_packet.mock.assert_not_called()
        assert c.namespaces == ['/foo', '/bar']

    def test_handle_disconnect(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/'))
        c._trigger_event.mock.assert_called_once_with(
            'disconnect', namespace='/'
        )
        assert not c.connected
        _run(c._handle_disconnect('/'))
        assert c._trigger_event.mock.call_count == 1

    def test_handle_disconnect_namespace(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/foo'))
        c._trigger_event.mock.assert_called_once_with(
            'disconnect', namespace='/foo'
        )
        assert c.namespaces == ['/bar']
        assert c.connected

    def test_handle_disconnect_unknown_namespace(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/baz'))
        c._trigger_event.mock.assert_called_once_with(
            'disconnect', namespace='/baz'
        )
        assert c.namespaces == ['/foo', '/bar']
        assert c.connected

    def test_handle_disconnect_all_namespaces(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/'))
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/')
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/foo')
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/bar')
        assert c.namespaces == []
        assert not c.connected

    def test_handle_event(self):
        c = asyncio_client.AsyncClient()
        c._trigger_event = AsyncMock()
        _run(c._handle_event('/', None, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )

    def test_handle_event_with_id_no_arguments(self):
        c = asyncio_client.AsyncClient(binary=True)
        c._trigger_event = AsyncMock(return_value=None)
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[], binary=None
        )
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_one_argument(self):
        c = asyncio_client.AsyncClient(binary=True)
        c._trigger_event = AsyncMock(return_value='ret')
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['ret'], binary=None
        )
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_one_list_argument(self):
        c = asyncio_client.AsyncClient(binary=True)
        c._trigger_event = AsyncMock(return_value=['a', 'b'])
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[['a', 'b']], binary=None
        )
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_two_arguments(self):
        c = asyncio_client.AsyncClient(binary=True)
        c._trigger_event = AsyncMock(return_value=('a', 'b'))
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['a', 'b'], binary=None
        )
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_ack(self):
        c = asyncio_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 123, ['bar', 'baz']))
        mock_cb.assert_called_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    def test_handle_ack_async(self):
        c = asyncio_client.AsyncClient()
        mock_cb = AsyncMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 123, ['bar', 'baz']))
        mock_cb.mock.assert_called_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    def test_handle_ack_not_found(self):
        c = asyncio_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 124, ['bar', 'baz']))
        mock_cb.assert_not_called()
        assert 123 in c.callbacks['/foo']

    def test_handle_error(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c._trigger_event = AsyncMock()
        c.namespaces = ['/foo', '/bar']
        _run(c._handle_error('/', 'error'))
        assert c.namespaces == []
        assert not c.connected
        c._trigger_event.mock.assert_called_once_with(
            'connect_error', '/', 'error'
        )

    def test_handle_error_with_no_arguments(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c._trigger_event = AsyncMock()
        c.namespaces = ['/foo', '/bar']
        _run(c._handle_error('/', None))
        assert c.namespaces == []
        assert not c.connected
        c._trigger_event.mock.assert_called_once_with('connect_error', '/')

    def test_handle_error_namespace(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        _run(c._handle_error('/bar', ['error', 'message']))
        assert c.namespaces == ['/foo']
        assert c.connected
        c._trigger_event.mock.assert_called_once_with(
            'connect_error', '/bar', 'error', 'message'
        )

    def test_handle_error_namespace_with_no_arguments(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        _run(c._handle_error('/bar', None))
        assert c.namespaces == ['/foo']
        assert c.connected
        c._trigger_event.mock.assert_called_once_with('connect_error', '/bar')

    def test_handle_error_unknown_namespace(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        _run(c._handle_error('/baz', 'error'))
        assert c.namespaces == ['/foo', '/bar']
        assert c.connected

    def test_trigger_event(self):
        c = asyncio_client.AsyncClient()
        handler = mock.MagicMock()
        c.on('foo', handler)
        _run(c._trigger_event('foo', '/', 1, '2'))
        handler.assert_called_once_with(1, '2')

    def test_trigger_event_namespace(self):
        c = asyncio_client.AsyncClient()
        handler = AsyncMock()
        c.on('foo', handler, namespace='/bar')
        _run(c._trigger_event('foo', '/bar', 1, '2'))
        handler.mock.assert_called_once_with(1, '2')

    def test_trigger_event_class_namespace(self):
        c = asyncio_client.AsyncClient()
        result = []

        class MyNamespace(asyncio_namespace.AsyncClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        _run(c._trigger_event('foo', '/', 1, '2'))
        assert result == [1, '2']

    def test_trigger_event_unknown_namespace(self):
        c = asyncio_client.AsyncClient()
        result = []

        class MyNamespace(asyncio_namespace.AsyncClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        _run(c._trigger_event('foo', '/bar', 1, '2'))
        assert result == []

    @mock.patch(
        'asyncio.wait_for',
        new_callable=AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect(self, random, wait_for):
        c = asyncio_client.AsyncClient()
        c._reconnect_task = 'foo'
        c.connect = AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        _run(c._handle_reconnect())
        assert wait_for.mock.call_count == 3
        assert [x[0][1] for x in asyncio.wait_for.mock.call_args_list] == [
            1.5,
            1.5,
            4.0,
        ]
        assert c._reconnect_task is None

    @mock.patch(
        'asyncio.wait_for',
        new_callable=AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_max_delay(self, random, wait_for):
        c = asyncio_client.AsyncClient(reconnection_delay_max=3)
        c._reconnect_task = 'foo'
        c.connect = AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        _run(c._handle_reconnect())
        assert wait_for.mock.call_count == 3
        assert [x[0][1] for x in asyncio.wait_for.mock.call_args_list] == [
            1.5,
            1.5,
            3.0,
        ]
        assert c._reconnect_task is None

    @mock.patch(
        'asyncio.wait_for',
        new_callable=AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_max_attempts(self, random, wait_for):
        c = asyncio_client.AsyncClient(reconnection_attempts=2)
        c._reconnect_task = 'foo'
        c.connect = AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        _run(c._handle_reconnect())
        print(wait_for.mock.call_count)  # logging to debug #572
        print(wait_for.mock.call_args_list)
        assert wait_for.mock.call_count == 2
        assert [x[0][1] for x in asyncio.wait_for.mock.call_args_list] == [
            1.5,
            1.5,
        ]
        assert c._reconnect_task == 'foo'

    @mock.patch(
        'asyncio.wait_for',
        new_callable=AsyncMock,
        side_effect=[asyncio.TimeoutError, None],
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_aborted(self, random, wait_for):
        c = asyncio_client.AsyncClient()
        c._reconnect_task = 'foo'
        c.connect = AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        _run(c._handle_reconnect())
        assert wait_for.mock.call_count == 2
        assert [x[0][1] for x in asyncio.wait_for.mock.call_args_list] == [
            1.5,
            1.5,
        ]
        assert c._reconnect_task == 'foo'

    def test_eio_connect(self):
        c = asyncio_client.AsyncClient()
        c.eio.sid = 'foo'
        assert c.sid is None
        c._handle_eio_connect()
        assert c.sid == 'foo'

    def test_handle_eio_message(self):
        c = asyncio_client.AsyncClient()
        c._handle_connect = AsyncMock()
        c._handle_disconnect = AsyncMock()
        c._handle_event = AsyncMock()
        c._handle_ack = AsyncMock()
        c._handle_error = AsyncMock()

        _run(c._handle_eio_message('0'))
        c._handle_connect.mock.assert_called_with(None)
        _run(c._handle_eio_message('0/foo'))
        c._handle_connect.mock.assert_called_with('/foo')
        _run(c._handle_eio_message('1'))
        c._handle_disconnect.mock.assert_called_with(None)
        _run(c._handle_eio_message('1/foo'))
        c._handle_disconnect.mock.assert_called_with('/foo')
        _run(c._handle_eio_message('2["foo"]'))
        c._handle_event.mock.assert_called_with(None, None, ['foo'])
        _run(c._handle_eio_message('3/foo,["bar"]'))
        c._handle_ack.mock.assert_called_with('/foo', None, ['bar'])
        _run(c._handle_eio_message('4'))
        c._handle_error.mock.assert_called_with(None, None)
        _run(c._handle_eio_message('4"foo"'))
        c._handle_error.mock.assert_called_with(None, 'foo')
        _run(c._handle_eio_message('4["foo"]'))
        c._handle_error.mock.assert_called_with(None, ['foo'])
        _run(c._handle_eio_message('4/foo'))
        c._handle_error.mock.assert_called_with('/foo', None)
        _run(c._handle_eio_message('4/foo,["foo","bar"]'))
        c._handle_error.mock.assert_called_with('/foo', ['foo', 'bar'])
        _run(c._handle_eio_message('51-{"_placeholder":true,"num":0}'))
        assert c._binary_packet.packet_type == packet.BINARY_EVENT
        _run(c._handle_eio_message(b'foo'))
        c._handle_event.mock.assert_called_with(None, None, b'foo')
        _run(
            c._handle_eio_message(
                '62-/foo,{"1":{"_placeholder":true,"num":1},'
                '"2":{"_placeholder":true,"num":0}}'
            )
        )
        assert c._binary_packet.packet_type == packet.BINARY_ACK
        _run(c._handle_eio_message(b'bar'))
        _run(c._handle_eio_message(b'foo'))
        c._handle_ack.mock.assert_called_with(
            '/foo', None, {'1': b'foo', '2': b'bar'}
        )
        with pytest.raises(ValueError):
            _run(c._handle_eio_message('9'))

    def test_eio_disconnect(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c._trigger_event = AsyncMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c._trigger_event.mock.assert_called_once_with(
            'disconnect', namespace='/'
        )
        assert c.sid is None
        assert not c.connected

    def test_eio_disconnect_namespaces(self):
        c = asyncio_client.AsyncClient()
        c.connected = True
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = AsyncMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/foo')
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/bar')
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/')
        assert c.sid is None
        assert not c.connected

    def test_eio_disconnect_reconnect(self):
        c = asyncio_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c.start_background_task.assert_called_once_with(c._handle_reconnect)

    def test_eio_disconnect_self_disconnect(self):
        c = asyncio_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'disconnected'
        _run(c._handle_eio_disconnect())
        c.start_background_task.assert_not_called()

    def test_eio_disconnect_no_reconnect(self):
        c = asyncio_client.AsyncClient(reconnection=False)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c.start_background_task.assert_not_called()
