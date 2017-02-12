import json
import logging
import sys
import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import packet
from socketio import namespace
if sys.version_info >= (3, 5):
    import asyncio
    from asyncio import coroutine
    from socketio import asyncio_server
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
@mock.patch('socketio.server.engineio.AsyncServer')
class TestAsyncServer(unittest.TestCase):
    def tearDown(self):
        # restore JSON encoder, in case a test changed it
        packet.Packet.json = json

    def _get_mock_manager(self):
        mgr = mock.MagicMock()
        mgr.emit = AsyncMock()
        mgr.close_room = AsyncMock()
        mgr.trigger_callback = AsyncMock()
        return mgr

    def test_create(self, eio):
        eio.return_value.handle_request = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr, foo='bar')
        _run(s.handle_request({}))
        _run(s.handle_request({}))
        eio.assert_called_once_with(**{'foo': 'bar', 'async_handlers': False})
        self.assertEqual(s.manager, mgr)
        self.assertEqual(s.eio.on.call_count, 3)
        self.assertEqual(s.binary, False)
        self.assertEqual(s.async_handlers, False)

    def test_attach(self, eio):
        s = asyncio_server.AsyncServer()
        s.attach('app', 'path')
        eio.return_value.attach.assert_called_once_with('app', 'path')

    def test_on_event(self, eio):
        s = asyncio_server.AsyncServer()

        @s.on('connect')
        def foo():
            pass

        def bar():
            pass
        s.on('disconnect', bar)
        s.on('disconnect', bar, namespace='/foo')

        self.assertEqual(s.handlers['/']['connect'], foo)
        self.assertEqual(s.handlers['/']['disconnect'], bar)
        self.assertEqual(s.handlers['/foo']['disconnect'], bar)

    def test_emit(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s.emit('my event', {'foo': 'bar'}, 'room', '123',
                    namespace='/foo', callback='cb'))
        s.manager.emit.mock.assert_called_once_with(
            'my event', {'foo': 'bar'}, '/foo', 'room', '123', 'cb')

    def test_emit_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s.emit('my event', {'foo': 'bar'}, 'room', '123', callback='cb'))
        s.manager.emit.mock.assert_called_once_with('my event', {'foo': 'bar'},
                                                    '/', 'room', '123', 'cb')

    def test_send(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s.send('foo', 'room', '123', namespace='/foo', callback='cb'))
        s.manager.emit.mock.assert_called_once_with('message', 'foo', '/foo',
                                                    'room', '123', 'cb')

    def test_enter_room(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.enter_room('123', 'room', namespace='/foo')
        s.manager.enter_room.assert_called_once_with('123', '/foo', 'room')

    def test_enter_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.enter_room('123', 'room')
        s.manager.enter_room.assert_called_once_with('123', '/', 'room')

    def test_leave_room(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.leave_room('123', 'room', namespace='/foo')
        s.manager.leave_room.assert_called_once_with('123', '/foo', 'room')

    def test_leave_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.leave_room('123', 'room')
        s.manager.leave_room.assert_called_once_with('123', '/', 'room')

    def test_close_room(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s.close_room('room', namespace='/foo'))
        s.manager.close_room.mock.assert_called_once_with('room', '/foo')

    def test_close_room_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s.close_room('room'))
        s.manager.close_room.mock.assert_called_once_with('room', '/')

    def test_rooms(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.rooms('123', namespace='/foo')
        s.manager.get_rooms.assert_called_once_with('123', '/foo')

    def test_rooms_default_namespace(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.rooms('123')
        s.manager.get_rooms.assert_called_once_with('123', '/')

    def test_handle_request(self, eio):
        eio.return_value.handle_request = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s.handle_request('environ'))
        s.eio.handle_request.mock.assert_called_once_with('environ')

    def test_emit_internal(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._emit_internal('123', 'my event', 'my data', namespace='/foo'))
        s.eio.send.mock.assert_called_once_with(
            '123', '2/foo,["my event","my data"]', binary=False)

    def test_emit_internal_with_tuple(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._emit_internal('123', 'my event', ('foo', 'bar'),
                              namespace='/foo'))
        s.eio.send.mock.assert_called_once_with(
            '123', '2/foo,["my event","foo","bar"]', binary=False)

    def test_emit_internal_with_list(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._emit_internal('123', 'my event', ['foo', 'bar'],
                              namespace='/foo'))
        s.eio.send.mock.assert_called_once_with(
            '123', '2/foo,["my event",["foo","bar"]]', binary=False)

    def test_emit_internal_with_callback(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        id = s.manager._generate_ack_id('123', '/foo', 'cb')
        _run(s._emit_internal('123', 'my event', 'my data', namespace='/foo',
                              id=id))
        s.eio.send.mock.assert_called_once_with(
            '123', '2/foo,1["my event","my data"]', binary=False)

    def test_emit_internal_default_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._emit_internal('123', 'my event', 'my data'))
        s.eio.send.mock.assert_called_once_with(
            '123', '2["my event","my data"]', binary=False)

    def test_emit_internal_binary(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._emit_internal('123', u'my event', b'my binary data'))
        self.assertEqual(s.eio.send.mock.call_count, 2)

    def test_transport(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        s.eio.transport = mock.MagicMock(return_value='polling')
        _run(s._handle_eio_connect('foo', 'environ'))
        self.assertEqual(s.transport('foo'), 'polling')
        s.eio.transport.assert_called_once_with('foo')

    def test_handle_connect(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock()
        s.on('connect', handler)
        _run(s._handle_eio_connect('123', 'environ'))
        handler.assert_called_once_with('123', 'environ')
        s.manager.connect.assert_called_once_with('123', '/')
        s.eio.send.mock.assert_called_once_with('123', '0', binary=False)
        self.assertEqual(mgr.initialize.call_count, 1)
        _run(s._handle_eio_connect('456', 'environ'))
        self.assertEqual(mgr.initialize.call_count, 1)

    def test_handle_connect_async(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = AsyncMock()
        s.on('connect', handler)
        _run(s._handle_eio_connect('123', 'environ'))
        handler.mock.assert_called_once_with('123', 'environ')
        s.manager.connect.assert_called_once_with('123', '/')
        s.eio.send.mock.assert_called_once_with('123', '0', binary=False)
        self.assertEqual(mgr.initialize.call_count, 1)
        _run(s._handle_eio_connect('456', 'environ'))
        self.assertEqual(mgr.initialize.call_count, 1)

    def test_handle_connect_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock()
        s.on('connect', handler, namespace='/foo')
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        handler.assert_called_once_with('123', 'environ')
        s.manager.connect.assert_any_call('123', '/')
        s.manager.connect.assert_any_call('123', '/foo')
        s.eio.send.mock.assert_any_call('123', '0/foo', binary=False)

    def test_handle_connect_rejected(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler)
        _run(s._handle_eio_connect('123', 'environ'))
        handler.assert_called_once_with('123', 'environ')
        self.assertEqual(s.manager.connect.call_count, 1)
        self.assertEqual(s.manager.disconnect.call_count, 1)
        s.eio.send.mock.assert_called_once_with('123', '4', binary=False)

    def test_handle_connect_namespace_rejected(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler, namespace='/foo')
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        self.assertEqual(s.manager.connect.call_count, 2)
        self.assertEqual(s.manager.disconnect.call_count, 1)
        s.eio.send.mock.assert_any_call('123', '4/foo', binary=False)

    def test_handle_disconnect(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_disconnect('123'))
        handler.assert_called_once_with('123')
        s.manager.disconnect.assert_called_once_with('123', '/')
        self.assertEqual(s.environ, {})

    def test_handle_disconnect_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.manager.get_namespaces = mock.MagicMock(return_value=['/', '/foo'])
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        _run(s._handle_eio_disconnect('123'))
        handler.assert_called_once_with('123')
        handler_namespace.assert_called_once_with('123')
        self.assertEqual(s.environ, {})

    def test_handle_disconnect_only_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.manager.get_namespaces = mock.MagicMock(return_value=['/', '/foo'])
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        _run(s._handle_eio_message('123', '1/foo'))
        self.assertEqual(handler.call_count, 0)
        handler_namespace.assert_called_once_with('123')
        self.assertEqual(s.environ, {'123': 'environ'})

    def test_handle_disconnect_unknown_client(self, eio):
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        _run(s._handle_eio_disconnect('123'))

    def test_handle_event(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        handler = AsyncMock()
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '2["my message","a","b","c"]'))
        handler.mock.assert_called_once_with('123', 'a', 'b', 'c')

    def test_handle_event_with_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        handler = mock.MagicMock()
        s.on('my message', handler, namespace='/foo')
        _run(s._handle_eio_message('123', '2/foo,["my message","a","b","c"]'))
        handler.assert_called_once_with('123', 'a', 'b', 'c')

    def test_handle_event_binary(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        handler = mock.MagicMock()
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '52-["my message","a",'
                                          '{"_placeholder":true,"num":1},'
                                          '{"_placeholder":true,"num":0}]'))
        _run(s._handle_eio_message('123', b'foo'))
        _run(s._handle_eio_message('123', b'bar'))
        handler.assert_called_once_with('123', 'a', b'bar', b'foo')

    def test_handle_event_binary_ack(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        s.manager.initialize(s)
        _run(s._handle_eio_message('123', '61-321["my message","a",'
                                          '{"_placeholder":true,"num":0}]'))
        _run(s._handle_eio_message('123', b'foo'))
        mgr.trigger_callback.mock.assert_called_once_with(
            '123', '/', 321, ['my message', 'a', b'foo'])

    def test_handle_event_with_ack(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        handler = mock.MagicMock(return_value='foo')
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '21000["my message","foo"]'))
        handler.assert_called_once_with('123', 'foo')
        s.eio.send.mock.assert_called_once_with('123', '31000["foo"]',
                                                binary=False)

    def test_handle_event_with_ack_none(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        handler = mock.MagicMock(return_value=None)
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '21000["my message","foo"]'))
        handler.assert_called_once_with('123', 'foo')
        s.eio.send.mock.assert_called_once_with('123', '31000[]',
                                                binary=False)

    def test_handle_event_with_ack_tuple(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock(return_value=(1, '2', True))
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '21000["my message","a","b","c"]'))
        handler.assert_called_once_with('123', 'a', 'b', 'c')
        s.eio.send.mock.assert_called_once_with('123', '31000[1,"2",true]',
                                                binary=False)

    def test_handle_event_with_ack_list(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock(return_value=[1, '2', True])
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '21000["my message","a","b","c"]'))
        handler.assert_called_once_with('123', 'a', 'b', 'c')
        s.eio.send.mock.assert_called_once_with('123', '31000[[1,"2",true]]',
                                                binary=False)

    def test_handle_event_with_ack_binary(self, eio):
        eio.return_value.send = AsyncMock()
        mgr = self._get_mock_manager()
        s = asyncio_server.AsyncServer(client_manager=mgr)
        handler = mock.MagicMock(return_value=b'foo')
        s.on('my message', handler)
        _run(s._handle_eio_message('123', '21000["my message","foo"]'))
        handler.assert_any_call('123', 'foo')

    def test_handle_error_packet(self, eio):
        s = asyncio_server.AsyncServer()
        self.assertRaises(ValueError, _run, s._handle_eio_message('123', '4'))

    def test_handle_invalid_packet(self, eio):
        s = asyncio_server.AsyncServer()
        self.assertRaises(ValueError, _run, s._handle_eio_message('123', '9'))

    def test_send_with_ack(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        cb = mock.MagicMock()
        id1 = s.manager._generate_ack_id('123', '/', cb)
        id2 = s.manager._generate_ack_id('123', '/', cb)
        _run(s._emit_internal('123', 'my event', ['foo'], id=id1))
        _run(s._emit_internal('123', 'my event', ['bar'], id=id2))
        _run(s._handle_eio_message('123', '31["foo",2]'))
        cb.assert_called_once_with('foo', 2)

    def test_send_with_ack_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        cb = mock.MagicMock()
        id = s.manager._generate_ack_id('123', '/foo', cb)
        _run(s._emit_internal('123', 'my event', ['foo'], namespace='/foo',
                              id=id))
        _run(s._handle_eio_message('123', '3/foo,1["foo",2]'))
        cb.assert_called_once_with('foo', 2)

    def test_disconnect(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s.disconnect('123'))
        s.eio.send.mock.assert_any_call('123', '1', binary=False)

    def test_disconnect_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        _run(s.disconnect('123', namespace='/foo'))
        s.eio.send.mock.assert_any_call('123', '1/foo', binary=False)

    def test_disconnect_twice(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s.disconnect('123'))
        calls = s.eio.send.mock.call_count
        _run(s.disconnect('123'))
        self.assertEqual(calls, s.eio.send.mock.call_count)

    def test_disconnect_twice_namespace(self, eio):
        eio.return_value.send = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        _run(s.disconnect('123', namespace='/foo'))
        calls = s.eio.send.mock.call_count
        _run(s.disconnect('123', namespace='/foo'))
        self.assertEqual(calls, s.eio.send.mock.call_count)

    def test_namespace_handler(self, eio):
        eio.return_value.send = AsyncMock()
        result = {}

        class MyNamespace(asyncio_namespace.AsyncNamespace):
            def on_connect(self, sid, environ):
                result['result'] = (sid, environ)

            @coroutine
            def on_disconnect(self, sid):
                result['result'] = ('disconnect', sid)

            @coroutine
            def on_foo(self, sid, data):
                result['result'] = (sid, data)

            def on_bar(self, sid):
                result['result'] = 'bar'

            @coroutine
            def on_baz(self, sid, data1, data2):
                result['result'] = (data1, data2)

        s = asyncio_server.AsyncServer()
        s.register_namespace(MyNamespace('/foo'))
        _run(s._handle_eio_connect('123', 'environ'))
        _run(s._handle_eio_message('123', '0/foo'))
        self.assertEqual(result['result'], ('123', 'environ'))
        _run(s._handle_eio_message('123', '2/foo,["foo","a"]'))
        self.assertEqual(result['result'], ('123', 'a'))
        _run(s._handle_eio_message('123', '2/foo,["bar"]'))
        self.assertEqual(result['result'], 'bar')
        _run(s._handle_eio_message('123', '2/foo,["baz","a","b"]'))
        self.assertEqual(result['result'], ('a', 'b'))
        _run(s.disconnect('123', '/foo'))
        self.assertEqual(result['result'], ('disconnect', '123'))

    def test_bad_namespace_handler(self, eio):
        class Dummy(object):
            pass

        class SyncNS(namespace.Namespace):
            pass

        s = asyncio_server.AsyncServer()
        self.assertRaises(ValueError, s.register_namespace, 123)
        self.assertRaises(ValueError, s.register_namespace, Dummy)
        self.assertRaises(ValueError, s.register_namespace, Dummy())
        self.assertRaises(ValueError, s.register_namespace,
                          namespace.Namespace)
        self.assertRaises(ValueError, s.register_namespace, SyncNS())

    def test_logger(self, eio):
        s = asyncio_server.AsyncServer(logger=False)
        self.assertEqual(s.logger.getEffectiveLevel(), logging.ERROR)
        s.logger.setLevel(logging.NOTSET)
        s = asyncio_server.AsyncServer(logger=True)
        self.assertEqual(s.logger.getEffectiveLevel(), logging.INFO)
        s.logger.setLevel(logging.WARNING)
        s = asyncio_server.AsyncServer(logger=True)
        self.assertEqual(s.logger.getEffectiveLevel(), logging.WARNING)
        s.logger.setLevel(logging.NOTSET)
        s = asyncio_server.AsyncServer(logger='foo')
        self.assertEqual(s.logger, 'foo')

    def test_engineio_logger(self, eio):
        asyncio_server.AsyncServer(engineio_logger='foo')
        eio.assert_called_once_with(**{'logger': 'foo',
                                       'async_handlers': False})

    def test_custom_json(self, eio):
        # Warning: this test cannot run in parallel with other tests, as it
        # changes the JSON encoding/decoding functions

        class CustomJSON(object):
            @staticmethod
            def dumps(*args, **kwargs):
                return '*** encoded ***'

            @staticmethod
            def loads(*args, **kwargs):
                return '+++ decoded +++'

        asyncio_server.AsyncServer(json=CustomJSON)
        eio.assert_called_once_with(**{'json': CustomJSON,
                                       'async_handlers': False})

        pkt = packet.Packet(packet_type=packet.EVENT,
                            data={six.text_type('foo'): six.text_type('bar')})
        self.assertEqual(pkt.encode(), '2*** encoded ***')
        pkt2 = packet.Packet(encoded_packet=pkt.encode())
        self.assertEqual(pkt2.data, '+++ decoded +++')

        # restore the default JSON module
        packet.Packet.json = json

    def test_start_background_task(self, eio):
        eio.return_value.start_background_task = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s.start_background_task('foo', 'bar', baz='baz'))
        s.eio.start_background_task.mock.assert_called_once_with('foo', 'bar',
                                                                 baz='baz')

    def test_sleep(self, eio):
        eio.return_value.sleep = AsyncMock()
        s = asyncio_server.AsyncServer()
        _run(s.sleep(1.23))
        s.eio.sleep.mock.assert_called_once_with(1.23)
