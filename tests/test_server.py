import logging
import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import server


@mock.patch('engineio.Server')
class TestServer(unittest.TestCase):
    def test_create(self, eio):
        mgr = mock.MagicMock()
        s = server.Server({'foo': 'bar'}, mgr, binary=True)
        mgr.assert_called_once_with(s)
        eio.assert_called_once_with(**{'foo': 'bar'})
        self.assertEqual(s.eio.on.call_count, 3)
        self.assertEqual(s.binary, True)

    def test_on_event(self, eio):
        s = server.Server()

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
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.emit('my event', {'foo': 'bar'}, 'room', '123', namespace='/foo',
               callback='cb')
        s.manager.emit.assert_called_once_with('my event', {'foo': 'bar'},
                                               '/foo', 'room', '123', 'cb')

    def test_emit_default_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.emit('my event', {'foo': 'bar'}, 'room', '123', callback='cb')
        s.manager.emit.assert_called_once_with('my event', {'foo': 'bar'}, '/',
                                               'room', '123', 'cb')

    def test_send(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.send('foo', 'room', '123', namespace='/foo', callback='cb')
        s.manager.emit.assert_called_once_with('message', 'foo', '/foo',
                                               'room', '123', 'cb')

    def test_enter_room(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.enter_room('123', 'room', namespace='/foo')
        s.manager.enter_room.assert_called_once_with('123', '/foo', 'room')

    def test_enter_room_default_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.enter_room('123', 'room')
        s.manager.enter_room.assert_called_once_with('123', '/', 'room')

    def test_leave_room(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.leave_room('123', 'room', namespace='/foo')
        s.manager.leave_room.assert_called_once_with('123', '/foo', 'room')

    def test_leave_room_default_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.leave_room('123', 'room')
        s.manager.leave_room.assert_called_once_with('123', '/', 'room')

    def test_close_room(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.close_room('room', namespace='/foo')
        s.manager.close_room.assert_called_once_with('/foo', 'room')

    def test_close_room_default_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.close_room('room')
        s.manager.close_room.assert_called_once_with('/', 'room')

    def test_rooms(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.rooms('123', namespace='/foo')
        s.manager.get_rooms.assert_called_once_with('123', '/foo')

    def test_rooms_default_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.rooms('123')
        s.manager.get_rooms.assert_called_once_with('123', '/')

    def test_handle_request(self, eio):
        s = server.Server()
        s.handle_request('environ', 'start_response')
        s.eio.handle_request.assert_called_once_with('environ',
                                                     'start_response')

    def test_emit_internal(self, eio):
        s = server.Server()
        s._emit_internal('123', 'my event', 'my data', namespace='/foo')
        s.eio.send.assert_called_once_with('123',
                                           '2/foo,["my event","my data"]',
                                           binary=False)

    def test_emit_internal_with_callback(self, eio):
        s = server.Server()
        s._emit_internal('123', 'my event', 'my data', namespace='/foo',
                         callback='cb')
        s.eio.send.assert_called_once_with('123',
                                           '2/foo,1["my event","my data"]',
                                           binary=False)

    def test_emit_internal_default_namespace(self, eio):
        s = server.Server()
        s._emit_internal('123', 'my event', 'my data')
        s.eio.send.assert_called_once_with('123', '2["my event","my data"]',
                                           binary=False)

    def test_emit_internal_binary(self, eio):
        s = server.Server(binary=True)
        s._emit_internal('123', u'my event', b'my binary data')
        self.assertEqual(s.eio.send.call_count, 2)

    def test_handle_connect(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock()
        s.on('connect', handler)
        s._handle_eio_connect('123', 'environ')
        handler.assert_called_once_with('123', 'environ')
        s.manager.connect.assert_called_once_with('123', '/')
        s.eio.send.assert_called_once_with('123', '0', binary=False)

    def test_handle_connect_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock()
        s.on('connect', handler, namespace='/foo')
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        handler.assert_called_once_with('123', 'environ')
        s.manager.connect.assert_any_call('123', '/')
        s.manager.connect.assert_any_call('123', '/foo')
        s.eio.send.assert_any_call('123', '0/foo', binary=False)

    def test_handle_connect_rejected(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler)
        s._handle_eio_connect('123', 'environ')
        handler.assert_called_once_with('123', 'environ')
        self.assertEqual(s.manager.connect.call_count, 1)
        self.assertEqual(s.manager.disconnect.call_count, 1)
        s.eio.send.assert_called_once_with('123', '4', binary=False)

    def test_handle_connect_namespace_rejected(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock(return_value=False)
        s.on('connect', handler, namespace='/foo')
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        self.assertEqual(s.manager.connect.call_count, 2)
        self.assertEqual(s.manager.disconnect.call_count, 1)
        s.eio.send.assert_any_call('123', '4/foo', binary=False)

    def test_handle_disconnect(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_disconnect('123')
        handler.assert_called_once_with('123')
        s.manager.disconnect.assert_called_once_with('123', '/')
        self.assertEqual(s.environ, {})

    def test_handle_disconnect_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.manager.get_namespaces = mock.MagicMock(return_value=['/', '/foo'])
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        s._handle_eio_disconnect('123')
        handler.assert_called_once_with('123')
        handler_namespace.assert_called_once_with('123')
        self.assertEqual(s.environ, {})

    def test_handle_disconnect_only_namespace(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s.manager.get_namespaces = mock.MagicMock(return_value=['/', '/foo'])
        handler = mock.MagicMock()
        s.on('disconnect', handler)
        handler_namespace = mock.MagicMock()
        s.on('disconnect', handler_namespace, namespace='/foo')
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        s._handle_eio_message('123', '1/foo')
        self.assertEqual(handler.call_count, 0)
        handler_namespace.assert_called_once_with('123')
        self.assertEqual(s.environ, {'123': 'environ'})

    def test_handle_disconnect_unknown_client(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        s._handle_eio_disconnect('123')

    def test_handle_event(self, eio):
        s = server.Server()
        handler = mock.MagicMock()
        s.on('my message', handler)
        s._handle_eio_message('123', '2["my message","a","b","c"]')
        handler.assert_called_once_with('123', 'a', 'b', 'c')

    def test_handle_event_with_namespace(self, eio):
        s = server.Server()
        handler = mock.MagicMock()
        s.on('my message', handler, namespace='/foo')
        s._handle_eio_message('123', '2/foo,["my message","a","b","c"]')
        handler.assert_called_once_with('123', 'a', 'b', 'c')

    def test_handle_event_binary(self, eio):
        s = server.Server()
        handler = mock.MagicMock()
        s.on('my message', handler)
        s._handle_eio_message('123', '52-["my message","a",'
                                     '{"_placeholder":true,"num":1},'
                                     '{"_placeholder":true,"num":0}]')
        self.assertEqual(s._attachment_count, 2)
        s._handle_eio_message('123', b'foo')
        self.assertEqual(s._attachment_count, 1)
        s._handle_eio_message('123', b'bar')
        self.assertEqual(s._attachment_count, 0)
        handler.assert_called_once_with('123', 'a', b'bar', b'foo')

    def test_handle_event_binary_ack(self, eio):
        s = server.Server()
        s._handle_eio_message('123', '61-1["my message","a",'
                                     '{"_placeholder":true,"num":0}]')
        self.assertEqual(s._attachment_count, 1)
        self.assertRaises(ValueError, s._handle_eio_message, '123', b'foo')

    def test_handle_event_with_ack(self, eio):
        s = server.Server()
        handler = mock.MagicMock(return_value='foo')
        s.on('my message', handler)
        s._handle_eio_message('123', '21000["my message","foo"]')
        handler.assert_called_once_with('123', 'foo')
        s.eio.send.assert_called_once_with('123', '31000["foo"]',
                                           binary=False)

    def test_handle_event_with_ack_tuple(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock(return_value=(1, '2', True))
        s.on('my message', handler)
        s._handle_eio_message('123', '21000["my message","a","b","c"]')
        handler.assert_called_once_with('123', 'a', 'b', 'c')
        s.eio.send.assert_called_once_with('123', '31000[1,"2",true]',
                                           binary=False)

    def test_handle_event_with_ack_list(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr)
        handler = mock.MagicMock(return_value=[1, '2', True])
        s.on('my message', handler)
        s._handle_eio_message('123', '21000["my message","a","b","c"]')
        handler.assert_called_once_with('123', 'a', 'b', 'c')
        s.eio.send.assert_called_once_with('123', '31000[1,"2",true]',
                                           binary=False)

    def test_handle_event_with_ack_binary(self, eio):
        mgr = mock.MagicMock()
        s = server.Server(client_manager_class=mgr, binary=True)
        handler = mock.MagicMock(return_value=b'foo')
        s.on('my message', handler)
        s._handle_eio_message('123', '21000["my message","foo"]')
        handler.assert_any_call('123', 'foo')

    def test_handle_error_packet(self, eio):
        s = server.Server()
        self.assertRaises(ValueError, s._handle_eio_message, '123', '4')

    def test_handle_invalid_packet(self, eio):
        s = server.Server()
        self.assertRaises(ValueError, s._handle_eio_message, '123', '9')

    def test_send_with_ack(self, eio):
        s = server.Server()
        cb = mock.MagicMock()
        s._handle_eio_connect('123', 'environ')
        s._emit_internal('123', 'my event', ['foo'], callback=cb)
        s._emit_internal('123', 'my event', ['bar'], callback=cb)
        s._handle_eio_message('123', '31["foo",2]')
        cb.assert_called_once_with('foo', 2)
        self.assertIn('123', s.callbacks)
        s._handle_disconnect('123', '/')
        self.assertNotIn('123', s.callbacks)

    def test_send_with_ack_namespace(self, eio):
        s = server.Server()
        cb = mock.MagicMock()
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        s._emit_internal('123', 'my event', ['foo'], namespace='/foo',
                         callback=cb)
        s._handle_eio_message('123', '3/foo,1["foo",2]')
        cb.assert_called_once_with('foo', 2)
        self.assertIn('/foo', s.callbacks['123'])
        s._handle_eio_disconnect('123')
        self.assertNotIn('123', s.callbacks)

    def test_invalid_callback(self, eio):
        s = server.Server()
        cb = mock.MagicMock()
        s._handle_eio_connect('123', 'environ')
        s._emit_internal('123', 'my event', ['foo'], callback=cb)
        self.assertRaises(ValueError, s._handle_eio_message, '124',
                          '31["foo",2]')
        self.assertRaises(ValueError, s._handle_eio_message, '123',
                          '3/foo,1["foo",2]')
        self.assertRaises(ValueError, s._handle_eio_message, '123',
                          '32["foo",2]')

    def test_disconnect_all(self, eio):
        s = server.Server()
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        s.disconnect('123')
        s.eio.send.assert_any_call('123', '1/foo', binary=False)
        s.eio.send.assert_any_call('123', '1', binary=False)

    def test_disconnect_namespace(self, eio):
        s = server.Server()
        s._handle_eio_connect('123', 'environ')
        s._handle_eio_message('123', '0/foo')
        s.disconnect('123', namespace='/foo')
        s.eio.send.assert_any_call('123', '1/foo', binary=False)

    def test_logger(self, eio):
        s = server.Server(logger=False)
        self.assertEqual(s.logger.getEffectiveLevel(), logging.ERROR)
        s = server.Server(logger=True)
        self.assertEqual(s.logger.getEffectiveLevel(), logging.INFO)
        s = server.Server(logger='foo')
        self.assertEqual(s.logger, 'foo')
