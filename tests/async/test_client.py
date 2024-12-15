import asyncio
from unittest import mock

import pytest

from socketio import async_client
from socketio import async_namespace
from engineio import exceptions as engineio_exceptions
from socketio import exceptions
from socketio import packet


class TestAsyncClient:
    async def test_is_asyncio_based(self):
        c = async_client.AsyncClient()
        assert c.is_asyncio_based()

    async def test_connect(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        await c.connect(
            'url',
            headers='headers',
            auth='auth',
            transports='transports',
            namespaces=['/foo', '/', '/bar'],
            socketio_path='path',
            wait=False,
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_auth == 'auth'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo', '/', '/bar']
        assert c.socketio_path == 'path'
        c.eio.connect.assert_awaited_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    async def test_connect_functions(self):
        async def headers():
            return 'headers'

        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        await c.connect(
            lambda: 'url',
            headers=headers,
            auth='auth',
            transports='transports',
            namespaces=['/foo', '/', '/bar'],
            socketio_path='path',
            wait=False,
        )
        c.eio.connect.assert_awaited_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    async def test_connect_one_namespace(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        await c.connect(
            'url',
            headers='headers',
            transports='transports',
            namespaces='/foo',
            socketio_path='path',
            wait=False,
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/foo']
        assert c.socketio_path == 'path'
        c.eio.connect.assert_awaited_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    async def test_connect_default_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        c.on('baz', mock.MagicMock(), namespace='*')
        await c.connect(
            'url',
            headers='headers',
            transports='transports',
            socketio_path='path',
            wait=False,
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/', '/foo'] or \
            c.connection_namespaces == ['/foo', '/']
        assert c.socketio_path == 'path'
        c.eio.connect.assert_awaited_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    async def test_connect_no_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        await c.connect(
            'url',
            headers='headers',
            transports='transports',
            socketio_path='path',
            wait=False,
        )
        assert c.connection_url == 'url'
        assert c.connection_headers == 'headers'
        assert c.connection_transports == 'transports'
        assert c.connection_namespaces == ['/']
        assert c.socketio_path == 'path'
        c.eio.connect.assert_awaited_once_with(
            'url',
            headers='headers',
            transports='transports',
            engineio_path='path',
        )

    async def test_connect_error(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock(
            side_effect=engineio_exceptions.ConnectionError('foo')
        )
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        with pytest.raises(exceptions.ConnectionError):
            await c.connect(
                'url',
                headers='headers',
                transports='transports',
                socketio_path='path',
                wait=False,
            )

    async def test_connect_twice(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        await c.connect(
            'url',
            wait=False,
        )
        with pytest.raises(exceptions.ConnectionError):
            await c.connect(
                'url',
                wait=False,
            )

    async def test_connect_wait_single_namespace(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        c._connect_event = mock.MagicMock()

        async def mock_connect():
            c.namespaces = {'/': '123'}
            return True

        c._connect_event.wait = mock_connect
        await c.connect(
            'url',
            wait=True,
            wait_timeout=0.01,
        )
        assert c.connected is True

    async def test_connect_wait_two_namespaces(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
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
        await c.connect(
            'url',
            namespaces=['/foo', '/bar'],
            wait=True,
            wait_timeout=0.01,
        )
        assert c.connected is True
        assert c.namespaces == {'/bar': '123', '/foo': '456'}

    async def test_connect_timeout(self):
        c = async_client.AsyncClient()
        c.eio.connect = mock.AsyncMock()
        c.disconnect = mock.AsyncMock()
        with pytest.raises(exceptions.ConnectionError):
            await c.connect(
                'url',
                wait=True,
                wait_timeout=0.01,
            )
        c.disconnect.assert_awaited_once_with()

    async def test_wait_no_reconnect(self):
        c = async_client.AsyncClient()
        c.eio.wait = mock.AsyncMock()
        c.sleep = mock.AsyncMock()
        c._reconnect_task = None
        await c.wait()
        c.eio.wait.assert_awaited_once_with()
        c.sleep.assert_awaited_once_with(1)

    async def test_wait_reconnect_failed(self):
        c = async_client.AsyncClient()
        c.eio.wait = mock.AsyncMock()
        c.sleep = mock.AsyncMock()
        states = ['disconnected']

        async def fake_wait():
            c.eio.state = states.pop(0)

        c._reconnect_task = fake_wait()
        await c.wait()
        c.eio.wait.assert_awaited_once_with()
        c.sleep.assert_awaited_once_with(1)

    async def test_wait_reconnect_successful(self):
        c = async_client.AsyncClient()
        c.eio.wait = mock.AsyncMock()
        c.sleep = mock.AsyncMock()
        states = ['connected', 'disconnected']

        async def fake_wait():
            c.eio.state = states.pop(0)
            c._reconnect_task = fake_wait()

        c._reconnect_task = fake_wait()
        await c.wait()
        assert c.eio.wait.await_count == 2
        assert c.sleep.await_count == 2

    async def test_emit_no_arguments(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo')
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=None)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_one_argument(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', 'bar')
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
        )
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_one_argument_list(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', ['bar', 'baz'])
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', ['bar', 'baz']],
            id=None,
        )
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_two_arguments(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', ('bar', 'baz'))
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar', 'baz'],
            id=None,
        )
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', namespace='/foo')
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=None)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        with pytest.raises(exceptions.BadNamespaceError):
            await c.emit('foo', namespace='/bar')

    async def test_emit_with_callback(self):
        c = async_client.AsyncClient()
        c._send_packet = mock.AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.namespaces = {'/': '1'}
        await c.emit('foo', callback='cb')
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/', 'cb')

    async def test_emit_namespace_with_callback(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._send_packet = mock.AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        await c.emit('foo', namespace='/foo', callback='cb')
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/foo', data=['foo'], id=123)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c._generate_ack_id.assert_called_once_with('/foo', 'cb')

    async def test_emit_binary(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', b'bar')
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', b'bar'],
            id=None,
        )
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_emit_not_binary(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c._send_packet = mock.AsyncMock()
        await c.emit('foo', 'bar')
        expected_packet = packet.Packet(
            packet.EVENT,
            namespace='/',
            data=['foo', 'bar'],
            id=None,
        )
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_send(self):
        c = async_client.AsyncClient()
        c.emit = mock.AsyncMock()
        await c.send('data', 'namespace', 'callback')
        c.emit.assert_awaited_once_with(
            'message', data='data', namespace='namespace', callback='callback'
        )

    async def test_send_with_defaults(self):
        c = async_client.AsyncClient()
        c.emit = mock.AsyncMock()
        await c.send('data')
        c.emit.assert_awaited_once_with(
            'message', data='data', namespace=None, callback=None
        )

    async def test_call(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}

        async def fake_event_wait():
            c._generate_ack_id.call_args_list[0][0][1]('foo', 321)

        c._send_packet = mock.AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        assert await c.call('foo') == ('foo', 321)
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_call_with_timeout(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}

        async def fake_event_wait():
            await asyncio.sleep(1)

        c._send_packet = mock.AsyncMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.eio = mock.MagicMock()
        c.eio.create_event.return_value.wait = fake_event_wait
        with pytest.raises(exceptions.TimeoutError):
            await c.call('foo', timeout=0.01)
        expected_packet = packet.Packet(
            packet.EVENT, namespace='/', data=['foo'], id=123)
        assert c._send_packet.await_count == 1
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/': '1'}
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = mock.AsyncMock()
        c.eio.state = 'connected'
        await c.disconnect()
        assert c.connected
        assert c._trigger_event.await_count == 0
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c.eio.disconnect.assert_awaited_once_with(abort=True)

    async def test_disconnect_namespaces(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = mock.AsyncMock()
        c.eio.state = 'connected'
        await c.disconnect()
        assert c._trigger_event.await_count == 0
        assert c._send_packet.await_count == 2
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/foo')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/bar')
        assert (
            c._send_packet.await_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    async def test_start_background_task(self):
        c = async_client.AsyncClient()
        c.eio.start_background_task = mock.MagicMock(return_value='foo')
        assert c.start_background_task('foo', 'bar', baz='baz') == 'foo'
        c.eio.start_background_task.assert_called_once_with(
            'foo', 'bar', baz='baz'
        )

    async def test_sleep(self):
        c = async_client.AsyncClient()
        c.eio.sleep = mock.AsyncMock()
        await c.sleep(1.23)
        c.eio.sleep.assert_awaited_once_with(1.23)

    async def test_send_packet(self):
        c = async_client.AsyncClient()
        c.eio.send = mock.AsyncMock()
        await c._send_packet(packet.Packet(packet.EVENT, 'foo'))
        c.eio.send.assert_awaited_once_with('2"foo"')

    async def test_send_packet_binary(self):
        c = async_client.AsyncClient()
        c.eio.send = mock.AsyncMock()
        await c._send_packet(packet.Packet(packet.EVENT, b'foo'))
        assert c.eio.send.await_args_list == [
            mock.call('51-{"_placeholder":true,"num":0}'),
            mock.call(b'foo'),
        ] or c.eio.send.await_args_list == [
            mock.call('51-{"num":0,"_placeholder":true}'),
            mock.call(b'foo'),
        ]

    async def test_send_packet_default_binary(self):
        c = async_client.AsyncClient()
        c.eio.send = mock.AsyncMock()
        await c._send_packet(packet.Packet(packet.EVENT, 'foo'))
        c.eio.send.assert_awaited_once_with('2"foo"')

    async def test_handle_connect(self):
        c = async_client.AsyncClient()
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        await c._handle_connect('/', {'sid': '123'})
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with('connect', namespace='/')
        c._send_packet.assert_not_awaited()

    async def test_handle_connect_with_namespaces(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        await c._handle_connect('/', {'sid': '3'})
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with('connect', namespace='/')
        assert c.namespaces == {'/': '3', '/foo': '1', '/bar': '2'}

    async def test_handle_connect_namespace(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/foo': '1'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        await c._handle_connect('/foo', {'sid': '123'})
        await c._handle_connect('/bar', {'sid': '2'})
        assert c._trigger_event.await_count == 1
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with(
            'connect', namespace='/bar')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}

    async def test_handle_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._trigger_event = mock.AsyncMock()
        await c._handle_disconnect('/')
        c._trigger_event.assert_any_await(
            'disconnect', '/', c.reason.SERVER_DISCONNECT
        )
        c._trigger_event.assert_any_await('__disconnect_final', '/')
        assert not c.connected
        await c._handle_disconnect('/')
        assert c._trigger_event.await_count == 2

    async def test_handle_disconnect_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = mock.AsyncMock()
        await c._handle_disconnect('/foo')
        c._trigger_event.assert_any_await('disconnect', '/foo',
                                          c.reason.SERVER_DISCONNECT)
        c._trigger_event.assert_any_await('__disconnect_final', '/foo')
        assert c.namespaces == {'/bar': '2'}
        assert c.connected
        await c._handle_disconnect('/bar')
        c._trigger_event.assert_any_await('disconnect', '/bar',
                                          c.reason.SERVER_DISCONNECT)
        c._trigger_event.assert_any_await('__disconnect_final', '/bar')
        assert c.namespaces == {}
        assert not c.connected

    async def test_handle_disconnect_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = mock.AsyncMock()
        await c._handle_disconnect('/baz')
        c._trigger_event.assert_any_await('disconnect', '/baz',
                                          c.reason.SERVER_DISCONNECT)
        c._trigger_event.assert_any_await('__disconnect_final', '/baz')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected

    async def test_handle_disconnect_default_namespaces(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = mock.AsyncMock()
        await c._handle_disconnect('/')
        c._trigger_event.assert_any_await('disconnect', '/',
                                          c.reason.SERVER_DISCONNECT)
        c._trigger_event.assert_any_await('__disconnect_final', '/')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected

    async def test_handle_event(self):
        c = async_client.AsyncClient()
        c._trigger_event = mock.AsyncMock()
        await c._handle_event('/', None, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_awaited_once_with(
            'foo', '/', ('bar', 'baz')
        )

    async def test_handle_event_with_id_no_arguments(self):
        c = async_client.AsyncClient()
        c._trigger_event = mock.AsyncMock(return_value=None)
        c._send_packet = mock.AsyncMock()
        await c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_awaited_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[])
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_event_with_id_one_argument(self):
        c = async_client.AsyncClient()
        c._trigger_event = mock.AsyncMock(return_value='ret')
        c._send_packet = mock.AsyncMock()
        await c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_awaited_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['ret'])
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_event_with_id_one_list_argument(self):
        c = async_client.AsyncClient()
        c._trigger_event = mock.AsyncMock(return_value=['a', 'b'])
        c._send_packet = mock.AsyncMock()
        await c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_awaited_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=[['a', 'b']])
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_event_with_id_two_arguments(self):
        c = async_client.AsyncClient()
        c._trigger_event = mock.AsyncMock(return_value=('a', 'b'))
        c._send_packet = mock.AsyncMock()
        await c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_awaited_once_with(
            'foo', '/', ('bar', 'baz')
        )
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(
            packet.ACK, namespace='/', id=123, data=['a', 'b'])
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_ack(self):
        c = async_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        await c._handle_ack('/foo', 123, ['bar', 'baz'])
        mock_cb.assert_called_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    async def test_handle_ack_async(self):
        c = async_client.AsyncClient()
        mock_cb = mock.AsyncMock()
        c.callbacks['/foo'] = {123: mock_cb}
        await c._handle_ack('/foo', 123, ['bar', 'baz'])
        mock_cb.assert_awaited_once_with('bar', 'baz')
        assert 123 not in c.callbacks['/foo']

    async def test_handle_ack_not_found(self):
        c = async_client.AsyncClient()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        await c._handle_ack('/foo', 124, ['bar', 'baz'])
        mock_cb.assert_not_called()
        assert 123 in c.callbacks['/foo']

    async def test_handle_error(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        await c._handle_error('/', 'error')
        assert c.namespaces == {}
        assert not c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with(
            'connect_error', '/', 'error'
        )

    async def test_handle_error_with_no_arguments(self):
        c = async_client.AsyncClient()
        c.connected = True
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        c.namespaces = {'/foo': '1', '/bar': '2'}
        await c._handle_error('/', None)
        assert c.namespaces == {}
        assert not c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with('connect_error', '/')

    async def test_handle_error_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        await c._handle_error('/bar', ['error', 'message'])
        assert c.namespaces == {'/foo': '1'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with(
            'connect_error', '/bar', 'error', 'message'
        )

    async def test_handle_error_namespace_with_no_arguments(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        c._trigger_event = mock.AsyncMock()
        await c._handle_error('/bar', None)
        assert c.namespaces == {'/foo': '1'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()
        c._trigger_event.assert_awaited_once_with('connect_error', '/bar')

    async def test_handle_error_unknown_namespace(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._connect_event = mock.MagicMock()
        await c._handle_error('/baz', 'error')
        assert c.namespaces == {'/foo': '1', '/bar': '2'}
        assert c.connected
        c._connect_event.set.assert_called_once_with()

    async def test_trigger_event(self):
        c = async_client.AsyncClient()
        handler = mock.MagicMock()
        catchall_handler = mock.MagicMock()
        c.on('foo', handler)
        c.on('*', catchall_handler)
        await c._trigger_event('foo', '/', 1, '2')
        await c._trigger_event('bar', '/', 1, '2', 3)
        await c._trigger_event('connect', '/')  # should not trigger
        handler.assert_called_once_with(1, '2')
        catchall_handler.assert_called_once_with('bar', 1, '2', 3)

    async def test_trigger_event_namespace(self):
        c = async_client.AsyncClient()
        handler = mock.AsyncMock()
        catchall_handler = mock.AsyncMock()
        c.on('foo', handler, namespace='/bar')
        c.on('*', catchall_handler, namespace='/bar')
        await c._trigger_event('foo', '/bar', 1, '2')
        await c._trigger_event('bar', '/bar', 1, '2', 3)
        handler.assert_awaited_once_with(1, '2')
        catchall_handler.assert_awaited_once_with('bar', 1, '2', 3)

    async def test_trigger_legacy_disconnect_event(self):
        c = async_client.AsyncClient()

        @c.on('disconnect')
        def baz():
            return 'baz'

        r = await c._trigger_event('disconnect', '/', 'foo')
        assert r == 'baz'

    async def test_trigger_legacy_disconnect_event_async(self):
        c = async_client.AsyncClient()

        @c.on('disconnect')
        async def baz():
            return 'baz'

        r = await c._trigger_event('disconnect', '/', 'foo')
        assert r == 'baz'

    async def test_trigger_event_class_namespace(self):
        c = async_client.AsyncClient()
        result = []

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        await c._trigger_event('foo', '/', 1, '2')
        assert result == [1, '2']

    async def test_trigger_event_with_catchall_class_namespace(self):
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
        await c._trigger_event('connect', '/foo')
        assert result['result'] == ('/foo',)
        await c._trigger_event('foo', '/foo', 'a')
        assert result['result'] == ('/foo', 'a')
        await c._trigger_event('bar', '/foo')
        assert result['result'] == 'bar/foo'
        await c._trigger_event('baz', '/foo', 'a', 'b')
        assert result['result'] == ('/foo', 'a', 'b')
        await c._trigger_event('disconnect', '/foo')
        assert result['result'] == ('disconnect', '/foo')

    async def test_trigger_event_unknown_namespace(self):
        c = async_client.AsyncClient()
        result = []

        class MyNamespace(async_namespace.AsyncClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        await c._trigger_event('foo', '/bar', 1, '2')
        assert result == []

    @mock.patch(
        'asyncio.wait_for',
        new_callable=mock.AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    async def test_handle_reconnect(self, random, wait_for):
        c = async_client.AsyncClient()
        c._reconnect_task = 'foo'
        c.connect = mock.AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        await c._handle_reconnect()
        assert wait_for.await_count == 3
        assert [x[0][1] for x in asyncio.wait_for.await_args_list] == [
            1.5,
            1.5,
            4.0,
        ]
        assert c._reconnect_task is None

    @mock.patch(
        'asyncio.wait_for',
        new_callable=mock.AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    async def test_handle_reconnect_max_delay(self, random, wait_for):
        c = async_client.AsyncClient(reconnection_delay_max=3)
        c._reconnect_task = 'foo'
        c.connect = mock.AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        await c._handle_reconnect()
        assert wait_for.await_count == 3
        assert [x[0][1] for x in asyncio.wait_for.await_args_list] == [
            1.5,
            1.5,
            3.0,
        ]
        assert c._reconnect_task is None

    @mock.patch(
        'asyncio.wait_for',
        new_callable=mock.AsyncMock,
        side_effect=asyncio.TimeoutError,
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    async def test_handle_reconnect_max_attempts(self, random, wait_for):
        c = async_client.AsyncClient(reconnection_attempts=2, logger=True)
        c.connection_namespaces = ['/']
        c._reconnect_task = 'foo'
        c._trigger_event = mock.AsyncMock()
        c.connect = mock.AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        await c._handle_reconnect()
        assert wait_for.await_count == 2
        assert [x[0][1] for x in asyncio.wait_for.await_args_list] == [
            1.5,
            1.5,
        ]
        assert c._reconnect_task == 'foo'
        c._trigger_event.assert_awaited_once_with('__disconnect_final',
                                                  namespace='/')

    @mock.patch(
        'asyncio.wait_for',
        new_callable=mock.AsyncMock,
        side_effect=[asyncio.TimeoutError, None],
    )
    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    async def test_handle_reconnect_aborted(self, random, wait_for):
        c = async_client.AsyncClient(logger=True)
        c.connection_namespaces = ['/']
        c._reconnect_task = 'foo'
        c._trigger_event = mock.AsyncMock()
        c.connect = mock.AsyncMock(
            side_effect=[ValueError, exceptions.ConnectionError, None]
        )
        await c._handle_reconnect()
        assert wait_for.await_count == 2
        assert [x[0][1] for x in asyncio.wait_for.await_args_list] == [
            1.5,
            1.5,
        ]
        assert c._reconnect_task == 'foo'
        c._trigger_event.assert_awaited_once_with('__disconnect_final',
                                                  namespace='/')

    async def test_shutdown_disconnect(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/': '1'}
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = mock.AsyncMock()
        c.eio.state = 'connected'
        await c.shutdown()
        assert c._trigger_event.await_count == 0
        assert c._send_packet.await_count == 1
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        c.eio.disconnect.assert_awaited_once_with(abort=True)

    async def test_shutdown_disconnect_namespaces(self):
        c = async_client.AsyncClient()
        c.connected = True
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c._trigger_event = mock.AsyncMock()
        c._send_packet = mock.AsyncMock()
        c.eio = mock.MagicMock()
        c.eio.disconnect = mock.AsyncMock()
        c.eio.state = 'connected'
        await c.shutdown()
        assert c._trigger_event.await_count == 0
        assert c._send_packet.await_count == 2
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/foo')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/bar')
        assert (
            c._send_packet.await_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    async def test_shutdown_reconnect(self, random):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/']
        c._reconnect_task = mock.AsyncMock()()
        c._trigger_event = mock.AsyncMock()
        c.connect = mock.AsyncMock(side_effect=exceptions.ConnectionError)

        async def r():
            task = c.start_background_task(c._handle_reconnect)
            await asyncio.sleep(0.1)
            await c.shutdown()
            await task

        await r()
        c._trigger_event.assert_awaited_once_with('__disconnect_final',
                                                  namespace='/')

    async def test_handle_eio_connect(self):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/', '/foo']
        c.connection_auth = 'auth'
        c._send_packet = mock.AsyncMock()
        c.eio.sid = 'foo'
        assert c.sid is None
        await c._handle_eio_connect()
        assert c.sid == 'foo'
        assert c._send_packet.await_count == 2
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/foo')
        assert (
            c._send_packet.await_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_eio_connect_function(self):
        c = async_client.AsyncClient()
        c.connection_namespaces = ['/', '/foo']
        c.connection_auth = lambda: 'auth'
        c._send_packet = mock.AsyncMock()
        c.eio.sid = 'foo'
        assert c.sid is None
        await c._handle_eio_connect()
        assert c.sid == 'foo'
        assert c._send_packet.await_count == 2
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/')
        assert (
            c._send_packet.await_args_list[0][0][0].encode()
            == expected_packet.encode()
        )
        expected_packet = packet.Packet(
            packet.CONNECT, data='auth', namespace='/foo')
        assert (
            c._send_packet.await_args_list[1][0][0].encode()
            == expected_packet.encode()
        )

    async def test_handle_eio_message(self):
        c = async_client.AsyncClient()
        c._handle_connect = mock.AsyncMock()
        c._handle_disconnect = mock.AsyncMock()
        c._handle_event = mock.AsyncMock()
        c._handle_ack = mock.AsyncMock()
        c._handle_error = mock.AsyncMock()

        await c._handle_eio_message('0{"sid":"123"}')
        c._handle_connect.assert_awaited_with(None, {'sid': '123'})
        await c._handle_eio_message('0/foo,{"sid":"123"}')
        c._handle_connect.assert_awaited_with('/foo', {'sid': '123'})
        await c._handle_eio_message('1')
        c._handle_disconnect.assert_awaited_with(None)
        await c._handle_eio_message('1/foo')
        c._handle_disconnect.assert_awaited_with('/foo')
        await c._handle_eio_message('2["foo"]')
        c._handle_event.assert_awaited_with(None, None, ['foo'])
        await c._handle_eio_message('3/foo,["bar"]')
        c._handle_ack.assert_awaited_with('/foo', None, ['bar'])
        await c._handle_eio_message('4')
        c._handle_error.assert_awaited_with(None, None)
        await c._handle_eio_message('4"foo"')
        c._handle_error.assert_awaited_with(None, 'foo')
        await c._handle_eio_message('4["foo"]')
        c._handle_error.assert_awaited_with(None, ['foo'])
        await c._handle_eio_message('4/foo')
        c._handle_error.assert_awaited_with('/foo', None)
        await c._handle_eio_message('4/foo,["foo","bar"]')
        c._handle_error.assert_awaited_with('/foo', ['foo', 'bar'])
        await c._handle_eio_message('51-{"_placeholder":true,"num":0}')
        assert c._binary_packet.packet_type == packet.BINARY_EVENT
        await c._handle_eio_message(b'foo')
        c._handle_event.assert_awaited_with(None, None, b'foo')
        await c._handle_eio_message(
            '62-/foo,{"1":{"_placeholder":true,"num":1},'
            '"2":{"_placeholder":true,"num":0}}'
        )
        assert c._binary_packet.packet_type == packet.BINARY_ACK
        await c._handle_eio_message(b'bar')
        await c._handle_eio_message(b'foo')
        c._handle_ack.assert_awaited_with(
            '/foo', None, {'1': b'foo', '2': b'bar'}
        )
        with pytest.raises(ValueError):
            await c._handle_eio_message('9')

    async def test_eio_disconnect(self):
        c = async_client.AsyncClient()
        c.namespaces = {'/': '1'}
        c.connected = True
        c._trigger_event = mock.AsyncMock()
        c.start_background_task = mock.MagicMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        await c._handle_eio_disconnect('foo')
        c._trigger_event.assert_awaited_once_with('disconnect', '/', 'foo')
        assert c.sid is None
        assert not c.connected

    async def test_eio_disconnect_namespaces(self):
        c = async_client.AsyncClient(reconnection=False)
        c.namespaces = {'/foo': '1', '/bar': '2'}
        c.connected = True
        c._trigger_event = mock.AsyncMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        await c._handle_eio_disconnect(c.reason.CLIENT_DISCONNECT)
        c._trigger_event.assert_any_await('disconnect', '/foo',
                                          c.reason.CLIENT_DISCONNECT)
        c._trigger_event.assert_any_await('disconnect', '/bar',
                                          c.reason.CLIENT_DISCONNECT)
        c._trigger_event.asserT_any_await('disconnect', '/',
                                          c.reason.CLIENT_DISCONNECT)
        assert c.sid is None
        assert not c.connected

    async def test_eio_disconnect_reconnect(self):
        c = async_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        await c._handle_eio_disconnect(c.reason.CLIENT_DISCONNECT)
        c.start_background_task.assert_called_once_with(c._handle_reconnect)

    async def test_eio_disconnect_self_disconnect(self):
        c = async_client.AsyncClient(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'disconnected'
        await c._handle_eio_disconnect(c.reason.CLIENT_DISCONNECT)
        c.start_background_task.assert_not_called()

    async def test_eio_disconnect_no_reconnect(self):
        c = async_client.AsyncClient(reconnection=False)
        c.namespaces = {'/': '1'}
        c.connected = True
        c._trigger_event = mock.AsyncMock()
        c.start_background_task = mock.MagicMock()
        c.sid = 'foo'
        c.eio.state = 'connected'
        await c._handle_eio_disconnect(c.reason.TRANSPORT_ERROR)
        c._trigger_event.assert_any_await('disconnect', '/',
                                          c.reason.TRANSPORT_ERROR)
        c._trigger_event.assert_any_await('__disconnect_final', '/')
        assert c.sid is None
        assert not c.connected
        c.start_background_task.assert_not_called()
