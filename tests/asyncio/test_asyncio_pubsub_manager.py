import asyncio
import functools
import sys
import unittest

import six
if six.PY3:
    from unittest import mock
else:
    import mock

from socketio import asyncio_manager
from socketio import asyncio_pubsub_manager


def AsyncMock(*args, **kwargs):
    """Return a mock asynchronous function."""
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


def _run(coro):
    """Run the given coroutine."""
    return asyncio.get_event_loop().run_until_complete(coro)


@unittest.skipIf(sys.version_info < (3, 5), 'only for Python 3.5+')
class TestAsyncPubSubManager(unittest.TestCase):
    def setUp(self):
        mock_server = mock.MagicMock()
        mock_server._emit_internal = AsyncMock()
        mock_server.disconnect = AsyncMock()
        self.pm = asyncio_pubsub_manager.AsyncPubSubManager()
        self.pm._publish = AsyncMock()
        self.pm.set_server(mock_server)
        self.pm.host_id = '123456'
        self.pm.initialize()

    def test_default_init(self):
        self.assertEqual(self.pm.channel, 'socketio')
        self.pm.server.start_background_task.assert_called_once_with(
            self.pm._thread)

    def test_custom_init(self):
        pubsub = asyncio_pubsub_manager.AsyncPubSubManager(channel='foo')
        self.assertEqual(pubsub.channel, 'foo')
        self.assertEqual(len(pubsub.host_id), 32)

    def test_write_only_init(self):
        mock_server = mock.MagicMock()
        pm = asyncio_pubsub_manager.AsyncPubSubManager(write_only=True)
        pm.set_server(mock_server)
        pm.initialize()
        self.assertEqual(pm.channel, 'socketio')
        self.assertEqual(len(pm.host_id), 32)
        self.assertEqual(pm.server.start_background_task.call_count, 0)

    def test_emit(self):
        _run(self.pm.emit('foo', 'bar'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': None, 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_namespace(self):
        _run(self.pm.emit('foo', 'bar', namespace='/baz'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/baz', 'room': None, 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_room(self):
        _run(self.pm.emit('foo', 'bar', room='baz'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': 'baz', 'skip_sid': None,
             'callback': None, 'host_id': '123456'})

    def test_emit_with_skip_sid(self):
        _run(self.pm.emit('foo', 'bar', skip_sid='baz'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'emit', 'event': 'foo', 'data': 'bar',
             'namespace': '/', 'room': None, 'skip_sid': 'baz',
             'callback': None, 'host_id': '123456'})

    def test_emit_with_callback(self):
        with mock.patch.object(self.pm, '_generate_ack_id',
                               return_value='123'):
            _run(self.pm.emit('foo', 'bar', room='baz', callback='cb'))
            self.pm._publish.mock.assert_called_once_with(
                {'method': 'emit', 'event': 'foo', 'data': 'bar',
                 'namespace': '/', 'room': 'baz', 'skip_sid': None,
                 'callback': ('baz', '/', '123'), 'host_id': '123456'})

    def test_emit_with_callback_without_server(self):
        standalone_pm = asyncio_pubsub_manager.AsyncPubSubManager()
        self.assertRaises(RuntimeError, _run,
                          standalone_pm.emit('foo', 'bar', callback='cb'))

    def test_emit_with_callback_missing_room(self):
        with mock.patch.object(self.pm, '_generate_ack_id',
                               return_value='123'):
            self.assertRaises(ValueError, _run,
                              self.pm.emit('foo', 'bar', callback='cb'))

    def test_emit_with_ignore_queue(self):
        self.pm.connect('123', '/')
        _run(self.pm.emit('foo', 'bar', room='123', namespace='/',
                          ignore_queue=True))
        self.pm._publish.mock.assert_not_called()
        self.pm.server._emit_internal.mock.assert_called_once_with(
            '123', 'foo', 'bar', '/', None)

    def test_can_disconnect(self):
        self.pm.connect('123', '/')
        self.assertTrue(_run(self.pm.can_disconnect('123', '/')))
        _run(self.pm.can_disconnect('123', '/foo'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'})

    def test_close_room(self):
        _run(self.pm.close_room('foo'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/'})

    def test_close_room_with_namespace(self):
        _run(self.pm.close_room('foo', '/bar'))
        self.pm._publish.mock.assert_called_once_with(
            {'method': 'close_room', 'room': 'foo', 'namespace': '/bar'})

    def test_handle_emit(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'emit',
                               new=AsyncMock()) as super_emit:
            _run(self.pm._handle_emit({'event': 'foo', 'data': 'bar'}))
            super_emit.mock.assert_called_once_with(
                self.pm, 'foo', 'bar', namespace=None, room=None,
                skip_sid=None, callback=None)

    def test_handle_emit_with_namespace(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'emit',
                               new=AsyncMock()) as super_emit:
            _run(self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                       'namespace': '/baz'}))
            super_emit.mock.assert_called_once_with(
                self.pm, 'foo', 'bar', namespace='/baz', room=None,
                skip_sid=None, callback=None)

    def test_handle_emit_with_room(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'emit',
                               new=AsyncMock()) as super_emit:
            _run(self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                       'room': 'baz'}))
            super_emit.mock.assert_called_once_with(
                self.pm, 'foo', 'bar', namespace=None, room='baz',
                skip_sid=None, callback=None)

    def test_handle_emit_with_skip_sid(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'emit',
                               new=AsyncMock()) as super_emit:
            _run(self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                       'skip_sid': '123'}))
            super_emit.mock.assert_called_once_with(
                self.pm, 'foo', 'bar', namespace=None, room=None,
                skip_sid='123', callback=None)

    def test_handle_emit_with_callback(self):
        host_id = self.pm.host_id
        with mock.patch.object(asyncio_manager.AsyncManager, 'emit',
                               new=AsyncMock()) as super_emit:
            _run(self.pm._handle_emit({'event': 'foo', 'data': 'bar',
                                       'namespace': '/baz',
                                       'callback': ('sid', '/baz', 123),
                                       'host_id': '123456'}))
            self.assertEqual(super_emit.mock.call_count, 1)
            self.assertEqual(super_emit.mock.call_args[0],
                             (self.pm, 'foo', 'bar'))
            self.assertEqual(super_emit.mock.call_args[1]['namespace'], '/baz')
            self.assertIsNone(super_emit.mock.call_args[1]['room'])
            self.assertIsNone(super_emit.mock.call_args[1]['skip_sid'])
            self.assertIsInstance(super_emit.mock.call_args[1]['callback'],
                                  functools.partial)
            _run(super_emit.mock.call_args[1]['callback']('one', 2, 'three'))
            self.pm._publish.mock.assert_called_once_with(
                {'method': 'callback', 'host_id': host_id, 'sid': 'sid',
                 'namespace': '/baz', 'id': 123, 'args': ('one', 2, 'three')})

    def test_handle_callback(self):
        host_id = self.pm.host_id
        with mock.patch.object(self.pm, 'trigger_callback',
                               new=AsyncMock()) as trigger:
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': host_id, 'sid': 'sid',
                                           'namespace': '/', 'id': 123,
                                           'args': ('one', 2)}))
            trigger.mock.assert_called_once_with('sid', '/', 123, ('one', 2))

    def test_handle_callback_bad_host_id(self):
        with mock.patch.object(self.pm, 'trigger_callback',
                               new=AsyncMock()) as trigger:
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': 'bad', 'sid': 'sid',
                                           'namespace': '/', 'id': 123,
                                           'args': ('one', 2)}))
            self.assertEqual(trigger.mock.call_count, 0)

    def test_handle_callback_missing_args(self):
        host_id = self.pm.host_id
        with mock.patch.object(self.pm, 'trigger_callback',
                               new=AsyncMock()) as trigger:
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': host_id, 'sid': 'sid',
                                           'namespace': '/', 'id': 123}))
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': host_id, 'sid': 'sid',
                                           'namespace': '/'}))
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': host_id, 'sid': 'sid'}))
            _run(self.pm._handle_callback({'method': 'callback',
                                           'host_id': host_id}))
            self.assertEqual(trigger.mock.call_count, 0)

    def test_handle_disconnect(self):
        _run(self.pm._handle_disconnect({'method': 'disconnect', 'sid': '123',
                                         'namespace': '/foo'}))
        self.pm.server.disconnect.mock.assert_called_once_with(
            sid='123', namespace='/foo', ignore_queue=True)

    def test_handle_close_room(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'close_room',
                               new=AsyncMock()) as super_close_room:
            _run(self.pm._handle_close_room({'method': 'close_room',
                                             'room': 'foo'}))
            super_close_room.mock.assert_called_once_with(
                self.pm, room='foo', namespace=None)

    def test_handle_close_room_with_namespace(self):
        with mock.patch.object(asyncio_manager.AsyncManager, 'close_room',
                               new=AsyncMock()) as super_close_room:
            _run(self.pm._handle_close_room({'method': 'close_room',
                                             'room': 'foo',
                                             'namespace': '/bar'}))
            super_close_room.mock.assert_called_once_with(
                self.pm, room='foo', namespace='/bar')

    def test_background_thread(self):
        self.pm._handle_emit = AsyncMock()
        self.pm._handle_callback = AsyncMock()
        self.pm._handle_disconnect = AsyncMock()
        self.pm._handle_close_room = AsyncMock()

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

        self.pm._listen = AsyncMock(side_effect=list(messages()))
        try:
            _run(self.pm._thread())
        except StopIteration:
            pass

        self.pm._handle_emit.mock.assert_called_once_with(
            {'method': 'emit', 'value': 'foo'})
        self.pm._handle_callback.mock.assert_called_once_with(
            {'method': 'callback', 'value': 'bar'})
        self.pm._handle_disconnect.mock.assert_called_once_with(
            {'method': 'disconnect', 'sid': '123', 'namespace': '/foo'})
        self.pm._handle_close_room.mock.assert_called_once_with(
            {'method': 'close_room', 'value': 'baz'})
