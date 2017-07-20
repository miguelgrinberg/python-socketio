import sys
import unittest

if sys.version_info >= (3, 5):
    from socketio import asyncio_redis_manager


@unittest.skipIf(sys.version_info < (3, 5), 'only for Python 3.5+')
class TestAsyncRedisManager(unittest.TestCase):
    def test_default_url(self):
        self.assertEqual(asyncio_redis_manager._parse_redis_url('redis://'),
                         ('localhost', 6379, None, 0))

    def test_only_host_url(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://redis.host'),
            ('redis.host', 6379, None, 0))

    def test_no_db_url(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://redis.host:123/1'),
            ('redis.host', 123, None, 1))

    def test_no_port_url(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://redis.host/1'),
            ('redis.host', 6379, None, 1))

    def test_password(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://:pw@redis.host/1'),
            ('redis.host', 6379, 'pw', 1))

    def test_no_host_url(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://:123/1'),
            ('localhost', 123, None, 1))

    def test_no_host_password_url(self):
        self.assertEqual(
            asyncio_redis_manager._parse_redis_url('redis://:pw@:123/1'),
            ('localhost', 123, 'pw', 1))

    def test_bad_port_url(self):
        self.assertRaises(ValueError, asyncio_redis_manager._parse_redis_url,
                          'redis://localhost:abc/1')

    def test_bad_db_url(self):
        self.assertRaises(ValueError, asyncio_redis_manager._parse_redis_url,
                          'redis://localhost:abc/z')

    def test_bad_scheme_url(self):
        self.assertRaises(ValueError, asyncio_redis_manager._parse_redis_url,
                          'http://redis.host:123/1')
