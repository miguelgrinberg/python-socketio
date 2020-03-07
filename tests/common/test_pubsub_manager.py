import functools
import unittest
import logging

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import base_manager
from socketio import pubsub_manager


class TestBaseManager(unittest.TestCase):
    def setUp(self):
        mock_server = mock.MagicMock()
        self.pm = pubsub_manager.PubSubManager()
        self.pm._publish = mock.MagicMock()
        self.pm.set_server(mock_server)
        self.pm.host_id = '123456'
        self.pm.initialize()

    def test_default_init(self):
        self.assertEqual(self.pm.channel, 'socketio')
        self.pm.server.start_background_task.assert_called_once_with(
            self.pm._thread)

    def test_custom_init(self):
        pubsub = pubsub_manager.PubSubManager(channel='foo')
        self.assertEqual(pubsub.channel, 'foo')
        self.assertEqual(len(pubsub.host_id), 32)

    def test_write_only_init(self):
        mock_server = mock.MagicMock()
        pm = pubsub_manager.PubSubManager(write_only=True)
        pm.set_server(mock_server)
        pm.initialize()
        self.assertEqual(pm.channel, 'socketio')
        self.assertEqual(len(pm.host_id), 32)
        self.assertEqual(pm.server.start_background_task.call_count, 0)

    def test_write_only_default_logger(self):
        pm = pubsub_manager.PubSubManager(write_only=True)
        pm.initialize()
        self.assertEqual(pm.channel, 'socketio')
        self.assertEqual(len(pm.host_id), 32)
        self.assertEqual(pm._get_logger(), logging.getLogger('socketio'))

    def test_write_only_with_provided_logger(self):
        test_logger = logging.getLogger('new_logger')
        pm = pubsub_manager.PubSubManager(write_only=True,
                                          logger=test_logger)
        pm.initialize()
        self.assertEqual(pm.channel, 'socketio')
        self.assertEqual(len(pm.host_id), 32)
        self.assertEqual(pm._get_logger(), test_logger)

    def test_emit(self):
        self.pm.emit('foo', 'bar')
        self.pm._publish.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': None, 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_namespace(self):
        self.pm.emit('foo', 'bar', namespace='/baz')
        self.pm._publish.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/baz', 'room': None, 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_room(self):
        self.pm.emit('foo', 'bar', room='baz')
        self.pm._publish.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': 'baz', 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_skip_sid(self):
        self.pm.emit('foo', 'bar', skip_sid='baz')
        self.pm._publish.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': None, 'skip_sid': 'baz',
             'callback': None, 'host_id': '123456'})

    def test_emit_with_callback(self):
        with mock.patch.object(self.pm, '_generate_ack_id',
                               return_value='123'):
            self.pm.emit('foo', 'bar', room='baz', callback='cb')
            self.pm._publish.assert_called_once_with(
                {'method': 'emit', 'event': 'foo', 'data': 'bar',
                 'namespace': '/', 'room': 'baz', 'skip_sid': None,
                 'callback': ('baz', '/', '123'), 'host_id': '123456'})

    def test_emit_with_callback_without_server(self):
        standalone_pm = pubsub_manager.PubSubManager()
        self.assertRaises(RuntimeError, standalone_pm.emit, 'foo', 'bar',
                          callback='cb')

    def test_emit_with_callback_missing_room(self):
        with mock.patch.object(self.pm, '_generate_ack_id',
                               return_value='123'):
            self.assertRaises(ValueError, self.pm.emit, 'foo', 'bar',
                              callback='cb')

    def test_emit_with_ignore_queue(self):
        self.pm.connect('123', '/')
        self.pm.emit('foo', 'bar', room='123', namespace='/',
                     ignore_queue=True)
        self.pm._publish.assert_not_called()
        self.pm.server._emit_internal.assert_called_once_with('123', 'foo',
                                                              'bar', '/', None)

    def test_disconnect(self):
        self.pm.disconnect('123', '/foo')
        self.pm._publish.assert_called_once_with(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'})

    def test_close_room(self):
        self.pm.close_room('foo')
        self.pm._publish.assert_called_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/'})

    def test_close_room_with_namespace(self):
        self.pm.close_room('foo', '/bar')
        self.pm._publish.assert_called_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/bar'})

    def test_handle_emit(self):
        with mock.patch.object(base_manager.BaseManager, 'emit') as super_emit:
            self.pm._handle_emit({'event': 'foo', 'data': 'bar'})
            super_emit.assert_called_once_with('foo', 'bar', namespace=None,
                                               room=None, skip_sid=None,
                                               callback=None)

    def test_handle_emit_with_namespace(self):
        with mock.patch.object(base_manager.BaseManager, 'emit') as super_emit:
            self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                  'namespace': '/baz'})
            super_emit.assert_called_once_with('foo', 'bar', namespace='/baz',
                                               room=None, skip_sid=None,
                                               callback=None)

    def test_handle_emit_with_room(self):
        with mock.patch.object(base_manager.BaseManager, 'emit') as super_emit:
            self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                  'room': 'baz'})
            super_emit.assert_called_once_with('foo', 'bar', namespace=None,
                                               room='baz', skip_sid=None,
                                               callback=None)

    def test_handle_emit_with_skip_sid(self):
        with mock.patch.object(base_manager.BaseManager, 'emit') as super_emit:
            self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                  'skip_sid': '123'})
            super_emit.assert_called_once_with('foo', 'bar', namespace=None,
                                               room=None, skip_sid='123',
                                               callback=None)

    def test_handle_emit_with_callback(self):
        host_id = self.pm.host_id
        with mock.patch.object(base_manager.BaseManager, 'emit') as super_emit:
            self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                  'namespace': '/baz',
                                  'callback': ('sid', '/baz', 123),
                                  'host_id': host_id})
            self.assertEqual(super_emit.call_count, 1)
            self.assertEqual(super_emit.call_args[0], ('foo', 'bar'))
            self.assertEqual(super_emit.call_args[1]['namespace'], '/baz')
            self.assertIsNone(super_emit.call_args[1]['room'])
            self.assertIsNone(super_emit.call_args[1]['skip_sid'])
            self.assertIsInstance(super_emit.call_args[1]['callback'],
                                  functools.partial)
            super_emit.call_args[1]['callback']('one', 2, 'three')
            self.pm._publish.assert_called_once_with(
                {'method': 'callback', 'host_id': host_id, 'sid': 'sid',
                 'namespace': '/baz', 'id': 123, 'args': ('one', 2, 'three')})

    def test_handle_callback(self):
        host_id = self.pm.host_id
        with mock.patch.object(self.pm, 'trigger_callback') as trigger:
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': host_id, 'sid': 'sid',
                                      'namespace': '/', 'id': 123,
                                      'args': ('one', 2)})
            trigger.assert_called_once_with('sid', '/', 123, ('one', 2))

    def test_handle_callback_bad_host_id(self):
        with mock.patch.object(self.pm, 'trigger_callback') as trigger:
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': 'bad', 'sid': 'sid',
                                      'namespace': '/', 'id': 123,
                                      'args': ('one', 2)})
            self.assertEqual(trigger.call_count, 0)

    def test_handle_callback_missing_args(self):
        host_id = self.pm.host_id
        with mock.patch.object(self.pm, 'trigger_callback') as trigger:
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': host_id, 'sid': 'sid',
                                      'namespace': '/', 'id': 123})
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': host_id, 'sid': 'sid',
                                      'namespace': '/'})
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': host_id, 'sid': 'sid'})
            self.pm._handle_callback({'method': 'callback',
                                      'host_id': host_id})
            self.assertEqual(trigger.call_count, 0)

    def test_handle_disconnect(self):
        self.pm._handle_disconnect({'method': 'disconnect', 'sid': '123',
                                    'namespace': '/foo'})
        self.pm.server.disconnect.assert_called_once_with(sid='123',
                                                          namespace='/foo',
                                                          ignore_queue=True)

    def test_handle_close_room(self):
        with mock.patch.object(base_manager.BaseManager, 'close_room') \
                as super_close_room:
            self.pm._handle_close_room({'method': 'close_room',
                                        'room': 'foo'})
            super_close_room.assert_called_once_with(room='foo',
                                                     namespace=None)

    def test_handle_close_room_with_namespace(self):
        with mock.patch.object(base_manager.BaseManager, 'close_room') \
                as super_close_room:
            self.pm._handle_close_room({'method': 'close_room',
                                        'room': 'foo', 'namespace': '/bar'})
            super_close_room.assert_called_once_with(room='foo',
                                                     namespace='/bar')

    def test_background_thread(self):
        self.pm._handle_emit = mock.MagicMock()
        self.pm._handle_callback = mock.MagicMock()
        self.pm._handle_disconnect = mock.MagicMock()
        self.pm._handle_close_room = mock.MagicMock()

        def messages():
            import pickle
            yield {'method': 'emit', 'value': 'foo'}
            yield {'missing': 'method'}
            yield '{"method": "callback", "value": "bar"}'
            yield {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'}
            yield {'method': 'bogus'}
            yield pickle.dumps({'method': 'close_room', 'value': 'baz'})
            yield 'bad json'
            yield b'bad pickled'

        self.pm._listen = mock.MagicMock(side_effect=messages)
        try:
            self.pm._thread()
        except StopIteration:
            pass

        self.pm._handle_emit.assert_called_once_with(
            {'method': 'emit', 'value': 'foo'})
        self.pm._handle_callback.assert_called_once_with(
            {'method': 'callback', 'value': 'bar'})
        self.pm._handle_disconnect.assert_called_once_with(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'})
        self.pm._handle_close_room.assert_called_once_with(
            {'method': 'close_room', 'value': 'baz'})
