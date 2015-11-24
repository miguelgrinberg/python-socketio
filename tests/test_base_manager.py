import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import base_manager


class TestBaseManager(unittest.TestCase):
    def setUp(self):
        mock_server = mock.MagicMock()
        self.bm = base_manager.BaseManager()
        self.bm.initialize(mock_server)

    def test_connect(self):
        self.bm.connect('123', '/foo')
        self.assertIn(None, self.bm.rooms['/foo'])
        self.assertIn('123', self.bm.rooms['/foo'])
        self.assertIn('123', self.bm.rooms['/foo'][None])
        self.assertIn('123', self.bm.rooms['/foo']['123'])
        self.assertEqual(self.bm.rooms['/foo'], {None: {'123': True},
                                                 '123': {'123': True}})

    def test_disconnect(self):
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.enter_room('456', '/foo', 'baz')
        self.bm.disconnect('123', '/foo')
        self.bm._clean_rooms()
        self.assertEqual(self.bm.rooms['/foo'], {None: {'456': True},
                                                 '456': {'456': True},
                                                 'baz': {'456': True}})

    def test_disconnect_default_namespace(self):
        self.bm.connect('123', '/')
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/')
        self.bm.connect('456', '/foo')
        self.assertTrue(self.bm.is_connected('123', '/'))
        self.assertTrue(self.bm.is_connected('123', '/foo'))
        self.bm.disconnect('123', '/')
        self.assertFalse(self.bm.is_connected('123', '/'))
        self.assertTrue(self.bm.is_connected('123', '/foo'))
        self.bm.disconnect('123', '/foo')
        self.assertFalse(self.bm.is_connected('123', '/foo'))
        self.bm._clean_rooms()
        self.assertEqual(self.bm.rooms['/'], {None: {'456': True},
                                              '456': {'456': True}})
        self.assertEqual(self.bm.rooms['/foo'], {None: {'456': True},
                                                 '456': {'456': True}})

    def test_disconnect_twice(self):
        self.bm.connect('123', '/')
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/')
        self.bm.connect('456', '/foo')
        self.bm.disconnect('123', '/')
        self.bm.disconnect('123', '/foo')
        self.bm.disconnect('123', '/')
        self.bm.disconnect('123', '/foo')
        self.bm._clean_rooms()
        self.assertEqual(self.bm.rooms['/'], {None: {'456': True},
                                              '456': {'456': True}})
        self.assertEqual(self.bm.rooms['/foo'], {None: {'456': True},
                                                 '456': {'456': True}})

    def test_disconnect_all(self):
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.enter_room('456', '/foo', 'baz')
        self.bm.disconnect('123', '/foo')
        self.bm.disconnect('456', '/foo')
        self.bm._clean_rooms()
        self.assertEqual(self.bm.rooms, {})

    def test_disconnect_with_callbacks(self):
        self.bm.connect('123', '/')
        self.bm.connect('123', '/foo')
        self.bm._generate_ack_id('123', '/', 'f')
        self.bm._generate_ack_id('123', '/foo', 'g')
        self.bm.disconnect('123', '/foo')
        self.assertNotIn('/foo', self.bm.callbacks['123'])
        self.bm.disconnect('123', '/')
        self.assertNotIn('123', self.bm.callbacks)

    def test_trigger_callback(self):
        self.bm.connect('123', '/')
        self.bm.connect('123', '/foo')
        cb = mock.MagicMock()
        id1 = self.bm._generate_ack_id('123', '/', cb)
        id2 = self.bm._generate_ack_id('123', '/foo', cb)
        self.bm.trigger_callback('123', '/', id1, ['foo'])
        self.bm.trigger_callback('123', '/foo', id2, ['bar', 'baz'])
        self.assertEqual(cb.call_count, 2)
        cb.assert_any_call('foo')
        cb.assert_any_call('bar', 'baz')

    def test_invalid_callback(self):
        self.bm.connect('123', '/')
        cb = mock.MagicMock()
        id = self.bm._generate_ack_id('123', '/', cb)
        self.assertRaises(ValueError, self.bm.trigger_callback,
                          '124', '/', id, ['foo'])
        self.assertRaises(ValueError, self.bm.trigger_callback,
                          '123', '/foo', id, ['foo'])
        self.assertRaises(ValueError, self.bm.trigger_callback,
                          '123', '/', id + 1, ['foo'])
        self.assertEqual(cb.call_count, 0)

    def test_get_namespaces(self):
        self.assertEqual(list(self.bm.get_namespaces()), [])
        self.bm.connect('123', '/')
        self.bm.connect('123', '/foo')
        namespaces = list(self.bm.get_namespaces())
        self.assertEqual(len(namespaces), 2)
        self.assertIn('/', namespaces)
        self.assertIn('/foo', namespaces)

    def test_get_participants(self):
        self.bm.connect('123', '/')
        self.bm.connect('456', '/')
        self.bm.connect('789', '/')
        self.bm.disconnect('789', '/')
        self.assertEqual(self.bm.rooms['/'][None]['789'], False)
        participants = list(self.bm.get_participants('/', None))
        self.assertEqual(len(participants), 2)
        self.assertNotIn('789', participants)
        self.assertNotIn('789', self.bm.rooms['/'][None])

    def test_leave_invalid_room(self):
        self.bm.connect('123', '/foo')
        self.bm.leave_room('123', '/foo', 'baz')
        self.bm.leave_room('123', '/bar', 'baz')

    def test_close_room(self):
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/foo')
        self.bm.connect('789', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.close_room('bar', '/foo')
        self.assertNotIn('bar', self.bm.rooms['/foo'])

    def test_close_invalid_room(self):
        self.bm.close_room('bar', '/foo')

    def test_rooms(self):
        self.bm.connect('123', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        r = self.bm.get_rooms('123', '/foo')
        self.assertEqual(len(r), 2)
        self.assertIn('123', r)
        self.assertIn('bar', r)

    def test_emit_to_sid(self):
        self.bm.connect('123', '/foo')
        self.bm.connect('456', '/foo')
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo',
                     room='123')
        self.bm.server._emit_internal.assert_called_once_with('123',
                                                              'my event',
                                                              {'foo': 'bar'},
                                                              '/foo', None)

    def test_emit_to_room(self):
        self.bm.connect('123', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.connect('456', '/foo')
        self.bm.enter_room('456', '/foo', 'bar')
        self.bm.connect('789', '/foo')
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo',
                     room='bar')
        self.assertEqual(self.bm.server._emit_internal.call_count, 2)
        self.bm.server._emit_internal.assert_any_call('123', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)
        self.bm.server._emit_internal.assert_any_call('456', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)

    def test_emit_to_all(self):
        self.bm.connect('123', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.connect('456', '/foo')
        self.bm.enter_room('456', '/foo', 'bar')
        self.bm.connect('789', '/foo')
        self.bm.connect('abc', '/bar')
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo')
        self.assertEqual(self.bm.server._emit_internal.call_count, 3)
        self.bm.server._emit_internal.assert_any_call('123', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)
        self.bm.server._emit_internal.assert_any_call('456', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)
        self.bm.server._emit_internal.assert_any_call('789', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)

    def test_emit_to_all_skip_one(self):
        self.bm.connect('123', '/foo')
        self.bm.enter_room('123', '/foo', 'bar')
        self.bm.connect('456', '/foo')
        self.bm.enter_room('456', '/foo', 'bar')
        self.bm.connect('789', '/foo')
        self.bm.connect('abc', '/bar')
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo',
                     skip_sid='456')
        self.assertEqual(self.bm.server._emit_internal.call_count, 2)
        self.bm.server._emit_internal.assert_any_call('123', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)
        self.bm.server._emit_internal.assert_any_call('789', 'my event',
                                                      {'foo': 'bar'}, '/foo',
                                                      None)

    def test_emit_with_callback(self):
        self.bm.connect('123', '/foo')
        self.bm._generate_ack_id = mock.MagicMock()
        self.bm._generate_ack_id.return_value = 11
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo',
                     callback='cb')
        self.bm._generate_ack_id.assert_called_once_with('123', '/foo', 'cb')
        self.bm.server._emit_internal.assert_called_once_with('123',
                                                              'my event',
                                                              {'foo': 'bar'},
                                                              '/foo', 11)

    def test_emit_to_invalid_room(self):
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/', room='123')

    def test_emit_to_invalid_namespace(self):
        self.bm.emit('my event', {'foo': 'bar'}, namespace='/foo')
