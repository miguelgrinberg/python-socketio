import asyncio
import unittest
from unittest import mock

import pytest

from socketio import async_client
from socketio import async_namespace
from engineio import exceptions as engineio_exceptions
from socketio import exceptions
from socketio import packet
from .helpers import AsyncMock, _run


class TestAsyncClient(unittest.TestCase):
    def test_is_asyncio_based(self):
        c = async_client.AsyncClient()
        assert c.is_asyncio_based()

    def test_connect(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                headers='headers',
                auth='auth',
                transports='transports',
                namespaces=['/foo', '/', '/bar'],
                socketio_path='path',
                wait=False,
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_auth == 'auth'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo', '/', '/bar']
        assert c.socketio_path == 'path'
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_functions(self):
        async def headers():
            return 'headers'

        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                lambda: 'url',
                headers=headers,
                auth='auth',
                transports='transports',
                namespaces=['/foo', '/', '/bar'],
                socketio_path='path',
                wait=False,
            )
        )
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_one_namespace(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                namespaces='/foo',
                socketio_path='path',
                wait=False,
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo']
        assert c.socketio_path == 'path'
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_default_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        c.on('baz', mock.MagicMock(), namespace='*')
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                socketio_path='path',
                wait=False,
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/', '/foo'] or \
            c.connection_namespaces == ['/foo', '/']
        assert c.socketio_path == 'path'
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_no_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                headers='headers',
                transports='transports',
                socketio_path='path',
                wait=False,
            )
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/']
        assert c.socketio_path == 'path'
        c.eio.connect.mock.assert_called_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    def test_connect_error(self):
        c = async_client.AsyncClient()
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
                    wait=False,
                )
            )

    def test_connect_twice(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        _run(
            c.connect(
                'url',
                wait=False,
            )
        )
        with pytest.raises(exceptions.ConnectionError):
            _run(
                c.connect(
                    'url',
                    wait=False,
                )
            )

    def test_connect_wait_single_namespace(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        c._connect_event = mock.MagicMock()

        async def mock_connect():
            c.namespaces = {'/': '123'}
            return True

        c._connect_event.wait = mock_connect
        _run(
            c.connect(
                'url',
                wait=True,
                wait_timeout=0.01,
            )
        )
        assert c.connected is True

    def test_connect_wait_two_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        c._connect_event = mock.MagicMock()

        async def mock_connect():
            if c.namespaces == {}:
                c.namespaces = {'/bar': '123'}
                return True
            elif c.namespaces == {'/bar': '123'}:
                c.namespaces = {'/bar': '123', '/foo': '456'}
                return True
            return False

        c._connect_event.wait = mock_connect
        _run(
            c.connect(
                'url',
                namespaces=['/foo', '/bar'],
                wait=True,
                wait_timeout=0.01,
            )
        )
        assert c.connected is True
        assert c.namespaces == {'/bar': '123', '/foo': '456'}

    def test_connect_timeout(self):
        c = async_client.AsyncClient()
        c.eio.connect = AsyncMock()
        c.disconnect = AsyncMock()
        with pytest.raises(exceptions.ConnectionError):
            _run(
                c.connect(
                    'url',
                    wait=True,
                    wait_timeout=0.01,
                )
            )
        c.disconnect.mock.assert_called_once_with()

    def test_wait_no_reconnect(self):
        c = async_client.AsyncClient()
        c.eio.wait = AsyncMock()
        c.sleep = AsyncMock()
        c._reconnect_task = None
        _run(c.wait())
        c.eio.wait.mock.assert_called_once_with()
        c.sleep.mock.assert_called_once_with(1)

    def test_wait_reconnect_failed(self):
        c = async_client.AsyncClient()
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
        c = async_client.AsyncClient()
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
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=None)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_one_argument(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', 'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_one_argument_list(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', ['bar', 'baz']))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', ['bar', 'baz']],
            id=None,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_two_arguments(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', ('bar', 'baz')))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar', 'baz'],
            id=None,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', namespace='/foo'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=None)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        with pytest.raises(exceptions.BadNamespaceError):
            _run(c.emit('foo', namespace='/bar'))

    def test_emit_with_callback(self):
        c = async_client.AsyncClient()
        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.namespaces = {'/': '1'}
        _run(c.emit('foo', callback='cb'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/', 'cb')

    def test_emit_namespace_with_callback(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        _run(c.emit('foo', namespace='/foo', callback='cb'))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=123)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/foo', 'cb')

    def test_emit_binary(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', b'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', b'bar'],
            id=None,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_emit_not_binary(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = AsyncMock()
        _run(c.emit('foo', 'bar'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
        )
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_send(self):
        c = async_client.AsyncClient()
        c.emit = AsyncMock()
        _run(c.send('data', 'namespace', 'callback'))
        c.emit.mock.assert_called_once_with(
            'message', data='data', namespace='namespace', callback='callback'
        )

    def test_send_with_defaults(self):
        c = async_client.AsyncClient()
        c.emit = AsyncMock()
        _run(c.send('data'))
        c.emit.mock.assert_called_once_with(
            'message', data='data', namespace=None, callback=None
        )

    def test_call(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}

        async def fake_event_wait():
            c._generate_ack_id.call_args_list[0][0][1]('foo', 321)

        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        assert _run(c.call('foo')) == ('foo', 321)
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_call_with_timeout(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}

        async def fake_event_wait():
            await asyncio.sleep(1)

        c._send_packet = AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        with pytest.raises(exceptions.TimeoutError):
            _run(c.call('foo', timeout=0.01))
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.mock.call_count == 1
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/': '1'}
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.disconnect())
        assert c.connected
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c.eio.disconnect.mock.assert_called_once_with(abort=True)

    def test_disconnect_namespaces(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.disconnect())
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 2
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

    def test_start_background_task(self):
        c = async_client.AsyncClient()
        c.eio.start_background_task = mock.MagicMock(return_value='foo')
        assert c.start_background_task('foo', 'bar', baz='baz') == 'foo'
        c.eio.start_background_task.assert_called_once_with(
            'foo', 'bar', baz='baz'
        )

    def test_sleep(self):
        c = async_client.AsyncClient()
        c.eio.sleep = AsyncMock()
        _run(c.sleep(1.23))
        c.eio.sleep.mock.assert_called_once_with(1.23)

    def test_send_packet(self):
        c = async_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, 'foo')))
        c.eio.send.mock.assert_called_once_with('2"foo"')

    def test_send_packet_binary(self):
        c = async_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, b'foo')))
        assert c.eio.send.mock.call_args_list == [
            mock.call('51-{"_placeholder":true,"num":0}'),
            mock.call(b'foo'),
        ] or c.eio.send.mock.call_args_list == [
            mock.call('51-{"num":0,"_placeholder":true}'),
            mock.call(b'foo'),
        ]

    def test_send_packet_default_binary(self):
        c = async_client.AsyncClient()
        c.eio.send = AsyncMock()
        _run(c._send_packet(packet.Packet(packet.EVENT, 'foo')))
        c.eio.send.mock.assert_called_once_with('2"foo"')

    def test_handle_connect(self):
        c = async_client.AsyncClient()
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/', {'sid': '123'}))
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with('connect', namespace='/')
        c._send_packet.mock.assert_not_called()

    def test_handle_connect_with_namespaces(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/', {'sid': '3'}))
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with('connect', namespace='/')
        assert c.namespaces == {'/': '3', '/foo': '1', '/bar': '2'}

    def test_handle_connect_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        _run(c._handle_connect('/foo', {'sid': '123'}))
        _run(c._handle_connect('/bar', {'sid': '2'}))
        assert c._trigger_event.mock.call_count == 1
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with(
            'connect', namespace='/bar')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}

    def test_handle_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/'))
        c._trigger_event.mock.assert_any_call(
            'disconnect', namespace='/'
        )
        c._trigger_event.mock.assert_any_call(
            '__disconnect_final', namespace='/'
        )
        assert not c.connected
        _run(c._handle_disconnect('/'))
        assert c._trigger_event.mock.call_count == 2

    def test_handle_disconnect_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/foo'))
        c._trigger_event.mock.assert_any_call(
            'disconnect', namespace='/foo'
        )
        c._trigger_event.mock.assert_any_call(
            '__disconnect_final', namespace='/foo'
        )
        assert c.namespaces == {'/bar': '2'}
        assert c.connected
        _run(c._handle_disconnect('/bar'))
        c._trigger_event.mock.assert_any_call(
            'disconnect', namespace='/bar'
        )
        c._trigger_event.mock.assert_any_call(
            '__disconnect_final', namespace='/bar'
        )
        assert c.namespaces == {}
        assert not c.connected

    def test_handle_disconnect_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/baz'))
        c._trigger_event.mock.assert_any_call(
            'disconnect', namespace='/baz'
        )
        c._trigger_event.mock.assert_any_call(
            '__disconnect_final', namespace='/baz'
        )
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected

    def test_handle_disconnect_default_namespaces(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = AsyncMock()
        _run(c._handle_disconnect('/'))
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/')
        c._trigger_event.mock.assert_any_call('__disconnect_final',
                                              namespace='/')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected

    def test_handle_event(self):
        c = async_client.AsyncClient()
        c._trigger_event = AsyncMock()
        _run(c._handle_event('/', None, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )

    def test_handle_event_with_id_no_arguments(self):
        c = async_client.AsyncClient()
        c._trigger_event = AsyncMock(return_value=None)
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[])
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_one_argument(self):
        c = async_client.AsyncClient()
        c._trigger_event = AsyncMock(return_value='ret')
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['ret'])
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_one_list_argument(self):
        c = async_client.AsyncClient()
        c._trigger_event = AsyncMock(return_value=['a', 'b'])
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[['a', 'b']])
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_event_with_id_two_arguments(self):
        c = async_client.AsyncClient()
        c._trigger_event = AsyncMock(return_value=('a', 'b'))
        c._send_packet = AsyncMock()
        _run(c._handle_event('/', 123, ['foo', ('bar', 'baz')]))
        c._trigger_event.mock.assert_called_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['a', 'b'])
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_ack(self):
        c = async_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 123, ['bar', 'baz']))
        mock_cb.assert_called_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    def test_handle_ack_async(self):
        c = async_client.AsyncClient()
        mock_cb = AsyncMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 123, ['bar', 'baz']))
        mock_cb.mock.assert_called_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    def test_handle_ack_not_found(self):
        c = async_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        _run(c._handle_ack('/foo', 124, ['bar', 'baz']))
        mock_cb.assert_not_called()
        assert 123 in c.callbacks['/foo']

    def test_handle_error(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        _run(c._handle_error('/', 'error'))
        assert c.namespaces == {}
        assert not c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with(
            'connect_error', '/', 'error'
        )

    def test_handle_error_with_no_arguments(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        _run(c._handle_error('/', None))
        assert c.namespaces == {}
        assert not c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with('connect_error', '/')

    def test_handle_error_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        _run(c._handle_error('/bar', ['error', 'message']))
        assert c.namespaces == {'/foo': '1'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with(
            'connect_error', '/bar', 'error', 'message'
        )

    def test_handle_error_namespace_with_no_arguments(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = AsyncMock()
        _run(c._handle_error('/bar', None))
        assert c.namespaces == {'/foo': '1'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.mock.assert_called_once_with('connect_error', '/bar')

    def test_handle_error_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        _run(c._handle_error('/baz', 'error'))
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()

    def test_trigger_event(self):
        c = async_client.AsyncClient()
        handler = mock.MagicMock()
        catchall_handler = mock.MagicMock()
        c.on('foo', handler)
        c.on('*', catchall_handler)
        _run(c._trigger_event('foo', '/', 1, '2'))
        _run(c._trigger_event('bar', '/', 1, '2', 3))
        _run(c._trigger_event('connect', '/'))  # should not trigger
        handler.assert_called_once_with(1, '2')
        catchall_handler.assert_called_once_with('bar', 1, '2', 3)

    def test_trigger_event_namespace(self):
        c = async_client.AsyncClient()
        handler = AsyncMock()
        catchall_handler = AsyncMock()
        c.on('foo', handler, namespace='/bar')
        c.on('*', catchall_handler, namespace='/bar')
        _run(c._trigger_event('foo', '/bar', 1, '2'))
        _run(c._trigger_event('bar', '/bar', 1, '2', 3))
        handler.mock.assert_called_once_with(1, '2')
        catchall_handler.mock.assert_called_once_with('bar', 1, '2', 3)

    def test_trigger_event_class_namespace(self):
        c = async_client.AsyncClient()
        result = []

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        _run(c._trigger_event('foo', '/', 1, '2'))
        assert result == [1, '2']

    def test_trigger_event_with_catchall_class_namespace(self):
        result = {}

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_connect(self, ns):
                result['result'] = (ns,)

            def on_disconnect(self, ns):
                result['result'] = ('disconnect', ns)

            def on_foo(self, ns, data):
                result['result'] = (ns, data)

            def on_bar(self, ns):
                result['result'] = 'bar' + ns

            def on_baz(self, ns, data1, data2):
                result['result'] = (ns, data1, data2)

        c = async_client.AsyncClient()
        c.register_namespace(MyNamespace('*'))
        _run(c._trigger_event('connect', '/foo'))
        assert result['result'] == ('/foo',)
        _run(c._trigger_event('foo', '/foo', 'a'))
        assert result['result'] == ('/foo', 'a')
        _run(c._trigger_event('bar', '/foo'))
        assert result['result'] == 'bar/foo'
        _run(c._trigger_event('baz', '/foo', 'a', 'b'))
        assert result['result'] == ('/foo', 'a', 'b')
        _run(c._trigger_event('disconnect', '/foo'))
        assert result['result'] == ('disconnect', '/foo')

    def test_trigger_event_unknown_namespace(self):
        c = async_client.AsyncClient()
        result = []

        class MyNamespace(async_namespace.AsyncClientNamespace):
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
        c = async_client.AsyncClient()
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
        c = async_client.AsyncClient(reconnection_delay_max=3)
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
        c = async_client.AsyncClient(reconnection_attempts=2, logger=True)
        c.connection_namespaces = ['/']
        c._reconnect_task = 'foo'
        c._trigger_event = AsyncMock()
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
        c._trigger_event.mock.assert_called_once_with('__disconnect_final',
                                                      namespace='/')

    @mock.patch(
        'asyncio.wait_for',
        new_callable=AsyncMock,
        side_effect=[asyncio.TimeoutError, None],
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_aborted(self, random, wait_for):
        c = async_client.AsyncClient(logger=True)
        c.connection_namespaces = ['/']
        c._reconnect_task = 'foo'
        c._trigger_event = AsyncMock()
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
        c._trigger_event.mock.assert_called_once_with('__disconnect_final',
                                                      namespace='/')

    def test_shutdown_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/': '1'}
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.shutdown())
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 1
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c.eio.disconnect.mock.assert_called_once_with(abort=True)

    def test_shutdown_disconnect_namespaces(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = AsyncMock()
        c._send_packet = AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = AsyncMock()
        c.eio.state = 'connected'
        _run(c.shutdown())
        assert c._trigger_event.mock.call_count == 0
        assert c._send_packet.mock.call_count == 2
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

    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_shutdown_reconnect(self, random):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/']
        c._reconnect_task = AsyncMock()()
        c._trigger_event = AsyncMock()
        c.connect = AsyncMock(side_effect=exceptions.ConnectionError)

        async def r():
            task = c.start_background_task(c._handle_reconnect)
            await asyncio.sleep(0.1)
            await c.shutdown()
            await task

        _run(r())
        c._trigger_event.mock.assert_called_once_with('__disconnect_final',
                                                      namespace='/')

    def test_handle_eio_connect(self):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/', '/foo']
        c.connection_auth = 'auth'
        c._send_packet = AsyncMock()
        c.eio.sid = 'foo'
        assert c.sid is None
        _run(c._handle_eio_connect())
        assert c.sid == 'foo'
        assert c._send_packet.mock.call_count == 2
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/foo')
        assert (
            c._send_packet.mock.call_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_eio_connect_function(self):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/', '/foo']
        c.connection_auth = lambda: 'auth'
        c._send_packet = AsyncMock()
        c.eio.sid = 'foo'
        assert c.sid is None
        _run(c._handle_eio_connect())
        assert c.sid == 'foo'
        assert c._send_packet.mock.call_count == 2
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/')
        assert (
            c._send_packet.mock.call_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/foo')
        assert (
            c._send_packet.mock.call_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    def test_handle_eio_message(self):
        c = async_client.AsyncClient()
        c._handle_connect = AsyncMock()
        c._handle_disconnect = AsyncMock()
        c._handle_event = AsyncMock()
        c._handle_ack = AsyncMock()
        c._handle_error = AsyncMock()

        _run(c._handle_eio_message('0{"sid":"123"}'))
        c._handle_connect.mock.assert_called_with(None, {'sid': '123'})
        _run(c._handle_eio_message('0/foo,{"sid":"123"}'))
        c._handle_connect.mock.assert_called_with('/foo', {'sid': '123'})
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
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c.connected = True
        c._trigger_event = AsyncMock()
        c.start_background_task = mock.MagicMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c._trigger_event.mock.assert_called_once_with(
            'disconnect', namespace='/'
        )
        assert c.sid is None
        assert not c.connected

    def test_eio_disconnect_namespaces(self):
        c = async_client.AsyncClient(reconnection=False)
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c.connected = True
        c._trigger_event = AsyncMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/foo')
        c._trigger_event.mock.assert_any_call('disconnect', namespace='/bar')
        assert c.sid is None
        assert not c.connected

    def test_eio_disconnect_reconnect(self):
        c = async_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c.start_background_task.assert_called_once_with(c._handle_reconnect)

    def test_eio_disconnect_self_disconnect(self):
        c = async_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'disconnected'
        _run(c._handle_eio_disconnect())
        c.start_background_task.assert_not_called()

    def test_eio_disconnect_no_reconnect(self):
        c = async_client.AsyncClient(reconnection=False)
        c.namespaces = {'/': '1'}
        c.connected = True
        c._trigger_event = AsyncMock()
        c.start_background_task = mock.MagicMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        _run(c._handle_eio_disconnect())
        c._trigger_event.mock.assert_any_call(
            'disconnect', namespace='/'
        )
        c._trigger_event.mock.assert_any_call(
            '__disconnect_final', namespace='/'
        )
        assert c.sid is None
        assert not c.connected
        c.start_background_task.assert_not_called()
