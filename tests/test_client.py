import json
import logging
import sys
import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from engineio import exceptions as engineio_exceptions
from engineio import packet as engineio_packet
if six.PY3:
    from socketio import asyncio_namespace
else:
    asyncio_namespace = None
from socketio import client
from socketio import exceptions
from socketio import namespace
from socketio import packet


class TestClient(unittest.TestCase):
    def test_is_asyncio_based(self):
        c = client.Client()
        self.assertEqual(c.is_asyncio_based(), False)

    @mock.patch('socketio.client.Client._engineio_client_class')
    def test_create(self, engineio_client_class):
        c = client.Client(reconnection=False, reconnection_attempts=123,
                          reconnection_delay=5, reconnection_delay_max=10,
                          randomization_factor=0.2, binary=True, foo='bar')
        self.assertEqual(c.reconnection, False)
        self.assertEqual(c.reconnection_attempts, 123)
        self.assertEqual(c.reconnection_delay, 5)
        self.assertEqual(c.reconnection_delay_max, 10)
        self.assertEqual(c.randomization_factor, 0.2)
        self.assertEqual(c.binary, True)
        engineio_client_class().assert_called_once_with(foo='bar')
        self.assertEqual(c.connection_url, None)
        self.assertEqual(c.connection_headers, None)
        self.assertEqual(c.connection_transports, None)
        self.assertEqual(c.connection_namespaces, None)
        self.assertEqual(c.socketio_path, None)

        self.assertEqual(c.namespaces, [])
        self.assertEqual(c.handlers, {})
        self.assertEqual(c.namespace_handlers, {})
        self.assertEqual(c.callbacks, {})
        self.assertEqual(c._binary_packet, None)
        self.assertEqual(c._reconnect_task, None)

    def test_custon_json(self):
        client.Client()
        self.assertEqual(packet.Packet.json, json)
        self.assertEqual(engineio_packet.Packet.json, json)
        client.Client(json='foo')
        self.assertEqual(packet.Packet.json, 'foo')
        self.assertEqual(engineio_packet.Packet.json, 'foo')
        packet.Packet.json = json

    def test_logger(self):
        c = client.Client(logger=False)
        self.assertEqual(c.logger.getEffectiveLevel(), logging.ERROR)
        c.logger.setLevel(logging.NOTSET)
        c = client.Client(logger=True)
        self.assertEqual(c.logger.getEffectiveLevel(), logging.INFO)
        c.logger.setLevel(logging.WARNING)
        c = client.Client(logger=True)
        self.assertEqual(c.logger.getEffectiveLevel(), logging.WARNING)
        c.logger.setLevel(logging.NOTSET)
        my_logger = logging.Logger('foo')
        c = client.Client(logger=my_logger)
        self.assertEqual(c.logger, my_logger)

    @mock.patch('socketio.client.Client._engineio_client_class')
    def test_engineio_logger(self, engineio_client_class):
        client.Client(engineio_logger='foo')
        engineio_client_class().assert_called_once_with(logger='foo')

    def test_on_event(self):
        c = client.Client()

        @c.on('connect')
        def foo():
            pass

        def bar():
            pass
        c.on('disconnect', bar)
        c.on('disconnect', bar, namespace='/foo')

        self.assertEqual(c.handlers['/']['connect'], foo)
        self.assertEqual(c.handlers['/']['disconnect'], bar)
        self.assertEqual(c.handlers['/foo']['disconnect'], bar)

    def test_namespace_handler(self):
        class MyNamespace(namespace.ClientNamespace):
            pass

        c = client.Client()
        n = MyNamespace('/foo')
        c.register_namespace(n)
        self.assertEqual(c.namespace_handlers['/foo'], n)

    def test_namespace_handler_wrong_class(self):
        class MyNamespace(object):
            def __init__(self, n):
                pass

        c = client.Client()
        n = MyNamespace('/foo')
        self.assertRaises(ValueError, c.register_namespace, n)

    @unittest.skipIf(sys.version_info < (3, 0), 'only for Python 3')
    def test_namespace_handler_wrong_async(self):
        class MyNamespace(asyncio_namespace.AsyncClientNamespace):
            pass

        c = client.Client()
        n = MyNamespace('/foo')
        self.assertRaises(ValueError, c.register_namespace, n)

    def test_connect(self):
        c = client.Client()
        c.eio.connect = mock.MagicMock()
        c.connect('url', headers='headers', transports='transports',
                  namespaces=['/foo', '/', '/bar'], socketio_path='path')
        self.assertEqual(c.connection_url, 'url')
        self.assertEqual(c.connection_headers, 'headers')
        self.assertEqual(c.connection_transports, 'transports')
        self.assertEqual(c.connection_namespaces, ['/foo', '/', '/bar'])
        self.assertEqual(c.socketio_path, 'path')
        self.assertEqual(c.namespaces, ['/foo', '/bar'])
        c.eio.connect.assert_called_once_with(
            'url', headers='headers', transports='transports',
            engineio_path='path')

    def test_connect_default_namespaces(self):
        c = client.Client()
        c.eio.connect = mock.MagicMock()
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        c.connect('url', headers='headers', transports='transports',
                  socketio_path='path')
        self.assertEqual(c.connection_url, 'url')
        self.assertEqual(c.connection_headers, 'headers')
        self.assertEqual(c.connection_transports, 'transports')
        self.assertEqual(c.connection_namespaces, None)
        self.assertEqual(c.socketio_path, 'path')
        self.assertEqual(c.namespaces, ['/foo'])
        c.eio.connect.assert_called_once_with(
            'url', headers='headers', transports='transports',
            engineio_path='path')

    def test_connect_error(self):
        c = client.Client()
        c.eio.connect = mock.MagicMock(
            side_effect=engineio_exceptions.ConnectionError('foo'))
        c.on('foo', mock.MagicMock(), namespace='/foo')
        c.on('bar', mock.MagicMock(), namespace='/')
        self.assertRaises(
            exceptions.ConnectionError, c.connect, 'url', headers='headers',
            transports='transports', socketio_path='path')

    def test_wait_no_reconnect(self):
        c = client.Client()
        c.eio.wait = mock.MagicMock()
        c.sleep = mock.MagicMock()
        c._reconnect_task = None
        c.wait()
        c.eio.wait.assert_called_once_with()
        c.sleep.assert_called_once_with(1)

    def test_wait_reconnect_failed(self):
        c = client.Client()
        c.eio.wait = mock.MagicMock()
        c.sleep = mock.MagicMock()
        c._reconnect_task = mock.MagicMock()
        states = ['disconnected']

        def fake_join():
            c.eio.state = states.pop(0)

        c._reconnect_task.join = fake_join
        c.wait()
        c.eio.wait.assert_called_once_with()
        c.sleep.assert_called_once_with(1)

    def test_wait_reconnect_successful(self):
        c = client.Client()
        c.eio.wait = mock.MagicMock()
        c.sleep = mock.MagicMock()
        c._reconnect_task = mock.MagicMock()
        states = ['connected', 'disconnected']

        def fake_join():
            c.eio.state = states.pop(0)

        c._reconnect_task.join = fake_join
        c.wait()
        self.assertEqual(c.eio.wait.call_count, 2)
        self.assertEqual(c.sleep.call_count, 2)

    def test_emit_no_arguments(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c.emit('foo')
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo'], id=None, binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_one_argument(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c.emit('foo', 'bar')
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo', 'bar'], id=None,
                                        binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_one_argument_list(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c.emit('foo', ['bar', 'baz'])
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo', ['bar', 'baz']], id=None,
                                        binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_two_arguments(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c.emit('foo', ('bar', 'baz'))
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo', 'bar', 'baz'], id=None,
                                        binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_namespace(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c.emit('foo', namespace='/foo')
        expected_packet = packet.Packet(packet.EVENT, namespace='/foo',
                                        data=['foo'], id=None, binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_with_callback(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.emit('foo', callback='cb')
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo'], id=123, binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())
        c._generate_ack_id.assert_called_once_with('/', 'cb')

    def test_emit_namespace_with_callback(self):
        c = client.Client()
        c._send_packet = mock.MagicMock()
        c._generate_ack_id = mock.MagicMock(return_value=123)
        c.emit('foo', namespace='/foo', callback='cb')
        expected_packet = packet.Packet(packet.EVENT, namespace='/foo',
                                        data=['foo'], id=123, binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())
        c._generate_ack_id.assert_called_once_with('/foo', 'cb')

    def test_emit_binary(self):
        c = client.Client(binary=True)
        c._send_packet = mock.MagicMock()
        c.emit('foo', b'bar')
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo', b'bar'], id=None,
                                        binary=True)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_emit_not_binary(self):
        c = client.Client(binary=False)
        c._send_packet = mock.MagicMock()
        c.emit('foo', 'bar')
        expected_packet = packet.Packet(packet.EVENT, namespace='/',
                                        data=['foo', 'bar'], id=None,
                                        binary=False)
        self.assertEqual(c._send_packet.call_count, 1)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_send(self):
        c = client.Client()
        c.emit = mock.MagicMock()
        c.send('data', 'namespace', 'callback')
        c.emit.assert_called_once_with(
            'message', data='data', namespace='namespace',
            callback='callback')

    def test_send_with_defaults(self):
        c = client.Client()
        c.emit = mock.MagicMock()
        c.send('data')
        c.emit.assert_called_once_with(
            'message', data='data', namespace=None, callback=None)

    def test_disconnect(self):
        c = client.Client()
        c._trigger_event = mock.MagicMock()
        c._send_packet = mock.MagicMock()
        c.disconnect()
        c._trigger_event.assert_called_once_with('disconnect', namespace='/')
        self.assertEqual(c._send_packet.call_count, 1)
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_disconnect_namespaces(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = mock.MagicMock()
        c._send_packet = mock.MagicMock()
        c.disconnect()
        self.assertEqual(c._trigger_event.call_args_list, [
            mock.call('disconnect', namespace='/foo'),
            mock.call('disconnect', namespace='/bar'),
            mock.call('disconnect', namespace='/')
        ])
        self.assertEqual(c._send_packet.call_count, 3)
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/foo')
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/bar')
        self.assertEqual(c._send_packet.call_args_list[1][0][0].encode(),
                         expected_packet.encode())
        expected_packet = packet.Packet(packet.DISCONNECT, namespace='/')
        self.assertEqual(c._send_packet.call_args_list[2][0][0].encode(),
                         expected_packet.encode())

    def test_transport(self):
        c = client.Client()
        c.eio.transport = mock.MagicMock(return_value='foo')
        self.assertEqual(c.transport(), 'foo')
        c.eio.transport.assert_called_once_with()

    def test_start_background_task(self):
        c = client.Client()
        c.eio.start_background_task = mock.MagicMock(return_value='foo')
        self.assertEqual(c.start_background_task('foo', 'bar', baz='baz'),
                         'foo')
        c.eio.start_background_task.assert_called_once_with('foo', 'bar',
                                                            baz='baz')

    def test_sleep(self):
        c = client.Client()
        c.eio.sleep = mock.MagicMock()
        c.sleep(1.23)
        c.eio.sleep.assert_called_once_with(1.23)

    def test_send_packet(self):
        c = client.Client()
        c.eio.send = mock.MagicMock()
        c._send_packet(packet.Packet(packet.EVENT, 'foo', binary=False))
        c.eio.send.assert_called_once_with('2"foo"', binary=False)

    def test_send_packet_binary(self):
        c = client.Client()
        c.eio.send = mock.MagicMock()
        c._send_packet(packet.Packet(packet.EVENT, b'foo', binary=True))
        self.assertTrue(c.eio.send.call_args_list == [
            mock.call('51-{"_placeholder":true,"num":0}', binary=False),
            mock.call(b'foo', binary=True)
        ] or c.eio.send.call_args_list == [
            mock.call('51-{"num":0,"_placeholder":true}', binary=False),
            mock.call(b'foo', binary=True)
        ])

    @unittest.skipIf(sys.version_info < (3, 0), 'only for Python 3')
    def test_send_packet_default_binary_py3(self):
        c = client.Client()
        c.eio.send = mock.MagicMock()
        c._send_packet(packet.Packet(packet.EVENT, 'foo'))
        c.eio.send.assert_called_once_with('2"foo"', binary=False)

    @unittest.skipIf(sys.version_info >= (3, 0), 'only for Python 2')
    def test_send_packet_default_binary_py2(self):
        c = client.Client()
        c.eio.send = mock.MagicMock()
        c._send_packet(packet.Packet(packet.EVENT, 'foo'))
        self.assertTrue(c.eio.send.call_args_list == [
            mock.call('51-{"_placeholder":true,"num":0}', binary=False),
            mock.call(b'foo', binary=True)
        ] or c.eio.send.call_args_list == [
            mock.call('51-{"num":0,"_placeholder":true}', binary=False),
            mock.call(b'foo', binary=True)
        ])

    def test_generate_ack_id(self):
        c = client.Client()
        self.assertEqual(c._generate_ack_id('/', 'cb'), 1)
        self.assertEqual(c._generate_ack_id('/', 'cb'), 2)
        self.assertEqual(c._generate_ack_id('/', 'cb'), 3)
        self.assertEqual(c._generate_ack_id('/foo', 'cb'), 1)
        self.assertEqual(c._generate_ack_id('/bar', 'cb'), 1)
        self.assertEqual(c._generate_ack_id('/', 'cb'), 4)
        self.assertEqual(c._generate_ack_id('/bar', 'cb'), 2)

    def test_handle_connect(self):
        c = client.Client()
        c._trigger_event = mock.MagicMock()
        c._send_packet = mock.MagicMock()
        c._handle_connect('/')
        c._trigger_event.assert_called_once_with('connect', namespace='/')
        c._send_packet.assert_not_called()

    def test_handle_connect_with_namespaces(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = mock.MagicMock()
        c._send_packet = mock.MagicMock()
        c._handle_connect('/')
        c._trigger_event.assert_called_once_with('connect', namespace='/')
        self.assertEqual(c._send_packet.call_count, 2)
        expected_packet = packet.Packet(packet.CONNECT, namespace='/foo')
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())
        expected_packet = packet.Packet(packet.CONNECT, namespace='/bar')
        self.assertEqual(c._send_packet.call_args_list[1][0][0].encode(),
                         expected_packet.encode())

    def test_handle_connect_namespace(self):
        c = client.Client()
        c.namespaces = ['/foo']
        c._trigger_event = mock.MagicMock()
        c._send_packet = mock.MagicMock()
        c._handle_connect('/foo')
        c._handle_connect('/bar')
        self.assertEqual(c._trigger_event.call_args_list, [
            mock.call('connect', namespace='/foo'),
            mock.call('connect', namespace='/bar')
        ])
        c._send_packet.assert_not_called()
        self.assertEqual(c.namespaces, ['/foo', '/bar'])

    def test_handle_disconnect(self):
        c = client.Client()
        c._trigger_event = mock.MagicMock()
        c._handle_disconnect('/')
        c._trigger_event.assert_called_once_with('disconnect', namespace='/')

    def test_handle_disconnect_namespace(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = mock.MagicMock()
        c._handle_disconnect('/foo')
        c._trigger_event.assert_called_once_with('disconnect',
                                                 namespace='/foo')
        self.assertEqual(c.namespaces, ['/bar'])

    def test_handle_disconnect_unknown_namespace(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = mock.MagicMock()
        c._handle_disconnect('/baz')
        c._trigger_event.assert_called_once_with('disconnect',
                                                 namespace='/baz')
        self.assertEqual(c.namespaces, ['/foo', '/bar'])

    def test_handle_event(self):
        c = client.Client()
        c._trigger_event = mock.MagicMock()
        c._handle_event('/', None, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_called_once_with('foo', '/', ('bar', 'baz'))

    def test_handle_event_with_id_no_arguments(self):
        c = client.Client(binary=True)
        c._trigger_event = mock.MagicMock(return_value=None)
        c._send_packet = mock.MagicMock()
        c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_called_once_with('foo', '/', ('bar', 'baz'))
        self.assertEqual(c._send_packet.call_count, 1)
        expected_packet = packet.Packet(packet.ACK, namespace='/', id=123,
                                        data=[], binary=None)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_handle_event_with_id_one_argument(self):
        c = client.Client(binary=True)
        c._trigger_event = mock.MagicMock(return_value='ret')
        c._send_packet = mock.MagicMock()
        c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_called_once_with('foo', '/', ('bar', 'baz'))
        self.assertEqual(c._send_packet.call_count, 1)
        expected_packet = packet.Packet(packet.ACK, namespace='/', id=123,
                                        data=['ret'], binary=None)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_handle_event_with_id_one_list_argument(self):
        c = client.Client(binary=True)
        c._trigger_event = mock.MagicMock(return_value=['a', 'b'])
        c._send_packet = mock.MagicMock()
        c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_called_once_with('foo', '/', ('bar', 'baz'))
        self.assertEqual(c._send_packet.call_count, 1)
        expected_packet = packet.Packet(packet.ACK, namespace='/', id=123,
                                        data=[['a', 'b']], binary=None)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_handle_event_with_id_two_arguments(self):
        c = client.Client(binary=True)
        c._trigger_event = mock.MagicMock(return_value=('a', 'b'))
        c._send_packet = mock.MagicMock()
        c._handle_event('/', 123, ['foo', ('bar', 'baz')])
        c._trigger_event.assert_called_once_with('foo', '/', ('bar', 'baz'))
        self.assertEqual(c._send_packet.call_count, 1)
        expected_packet = packet.Packet(packet.ACK, namespace='/', id=123,
                                        data=['a', 'b'], binary=None)
        self.assertEqual(c._send_packet.call_args_list[0][0][0].encode(),
                         expected_packet.encode())

    def test_handle_ack(self):
        c = client.Client()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        c._handle_ack('/foo', 123, ['bar', 'baz'])
        mock_cb.assert_called_once_with('bar', 'baz')
        self.assertNotIn(123, c.callbacks['/foo'])

    def test_handle_ack_not_found(self):
        c = client.Client()
        mock_cb = mock.MagicMock()
        c.callbacks['/foo'] = {123: mock_cb}
        c._handle_ack('/foo', 124, ['bar', 'baz'])
        mock_cb.assert_not_called()
        self.assertIn(123, c.callbacks['/foo'])

    def test_handle_error(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._handle_error('/bar')
        self.assertEqual(c.namespaces, ['/foo'])

    def test_handle_error_unknown_namespace(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._handle_error('/baz')
        self.assertEqual(c.namespaces, ['/foo', '/bar'])

    def test_trigger_event(self):
        c = client.Client()
        handler = mock.MagicMock()
        c.on('foo', handler)
        c._trigger_event('foo', '/', 1, '2')
        handler.assert_called_once_with(1, '2')

    def test_trigger_event_namespace(self):
        c = client.Client()
        handler = mock.MagicMock()
        c.on('foo', handler, namespace='/bar')
        c._trigger_event('foo', '/bar', 1, '2')
        handler.assert_called_once_with(1, '2')

    def test_trigger_event_class_namespace(self):
        c = client.Client()
        result = []

        class MyNamespace(namespace.ClientNamespace):
            def on_foo(self, a, b):
                result.append(a)
                result.append(b)

        c.register_namespace(MyNamespace('/'))
        c._trigger_event('foo', '/', 1, '2')
        self.assertEqual(result, [1, '2'])

    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect(self, random):
        c = client.Client()
        c._reconnect_task = 'foo'
        c.sleep = mock.MagicMock()
        c.connect = mock.MagicMock(
            side_effect=[ValueError, exceptions.ConnectionError, None])
        c._handle_reconnect()
        self.assertEqual(c.sleep.call_count, 3)
        self.assertEqual(c.sleep.call_args_list, [
            mock.call(1.5),
            mock.call(1.5),
            mock.call(4.0)
        ])
        self.assertEqual(c._reconnect_task, None)

    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_max_delay(self, random):
        c = client.Client(reconnection_delay_max=3)
        c._reconnect_task = 'foo'
        c.sleep = mock.MagicMock()
        c.connect = mock.MagicMock(
            side_effect=[ValueError, exceptions.ConnectionError, None])
        c._handle_reconnect()
        self.assertEqual(c.sleep.call_count, 3)
        self.assertEqual(c.sleep.call_args_list, [
            mock.call(1.5),
            mock.call(1.5),
            mock.call(3.0)
        ])
        self.assertEqual(c._reconnect_task, None)

    @mock.patch('socketio.client.random.random', side_effect=[1, 0, 0.5])
    def test_handle_reconnect_max_attempts(self, random):
        c = client.Client(reconnection_attempts=2)
        c._reconnect_task = 'foo'
        c.sleep = mock.MagicMock()
        c.connect = mock.MagicMock(
            side_effect=[ValueError, exceptions.ConnectionError, None])
        c._handle_reconnect()
        self.assertEqual(c.sleep.call_count, 2)
        self.assertEqual(c.sleep.call_args_list, [
            mock.call(1.5),
            mock.call(1.5)
        ])
        self.assertEqual(c._reconnect_task, 'foo')

    def test_handle_eio_message(self):
        c = client.Client()
        c._handle_connect = mock.MagicMock()
        c._handle_disconnect = mock.MagicMock()
        c._handle_event = mock.MagicMock()
        c._handle_ack = mock.MagicMock()
        c._handle_error = mock.MagicMock()

        c._handle_eio_message('0')
        c._handle_connect.assert_called_with(None)
        c._handle_eio_message('0/foo')
        c._handle_connect.assert_called_with('/foo')
        c._handle_eio_message('1')
        c._handle_disconnect.assert_called_with(None)
        c._handle_eio_message('1/foo')
        c._handle_disconnect.assert_called_with('/foo')
        c._handle_eio_message('2["foo"]')
        c._handle_event.assert_called_with(None, None, ['foo'])
        c._handle_eio_message('3/foo,["bar"]')
        c._handle_ack.assert_called_with('/foo', None, ['bar'])
        c._handle_eio_message('4')
        c._handle_error.assert_called_with(None)
        c._handle_eio_message('4/foo')
        c._handle_error.assert_called_with('/foo')
        c._handle_eio_message('51-{"_placeholder":true,"num":0}')
        self.assertEqual(c._binary_packet.packet_type, packet.BINARY_EVENT)
        c._handle_eio_message(b'foo')
        c._handle_event.assert_called_with(None, None, b'foo')
        c._handle_eio_message('62-/foo,{"1":{"_placeholder":true,"num":1},'
                              '"2":{"_placeholder":true,"num":0}}')
        self.assertEqual(c._binary_packet.packet_type, packet.BINARY_ACK)
        c._handle_eio_message(b'bar')
        c._handle_eio_message(b'foo')
        c._handle_ack.assert_called_with('/foo', None, {'1': b'foo',
                                                        '2': b'bar'})
        self.assertRaises(ValueError, c._handle_eio_message, '9')

    def test_eio_disconnect(self):
        c = client.Client()
        c._trigger_event = mock.MagicMock()
        c._handle_eio_disconnect()
        c._trigger_event.assert_called_once_with('disconnect', namespace='/')

    def test_eio_disconnect_namespaces(self):
        c = client.Client()
        c.namespaces = ['/foo', '/bar']
        c._trigger_event = mock.MagicMock()
        c._handle_eio_disconnect()
        c._trigger_event.assert_any_call('disconnect', namespace='/foo')
        c._trigger_event.assert_any_call('disconnect', namespace='/bar')
        c._trigger_event.assert_any_call('disconnect', namespace='/')

    def test_eio_disconnect_reconnect(self):
        c = client.Client(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        c._handle_eio_disconnect()
        c.start_background_task.assert_called_once_with(c._handle_reconnect)

    def test_eio_disconnect_self_disconnect(self):
        c = client.Client(reconnection=True)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'disconnected'
        c._handle_eio_disconnect()
        c.start_background_task.assert_not_called()

    def test_eio_disconnect_no_reconnect(self):
        c = client.Client(reconnection=False)
        c.start_background_task = mock.MagicMock()
        c.eio.state = 'connected'
        c._handle_eio_disconnect()
        c.start_background_task.assert_not_called()
