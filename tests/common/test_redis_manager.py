import pytest

from socketio.redis_manager import parse_redis_sentinel_url


class TestPubSubManager:
    def test_sentinel_url_parser(self):
        with pytest.raises(ValueError):
            parse_redis_sentinel_url('redis://localhost:6379/0')

        assert parse_redis_sentinel_url(
            'redis+sentinel://localhost:6379'
        ) == (
            [('localhost', 6379)],
            None,
            {}
        )
        assert parse_redis_sentinel_url(
            'redis+sentinel://192.168.0.1:6379,192.168.0.2:6379/'
        ) == (
            [('192.168.0.1', 6379), ('192.168.0.2', 6379)],
            None,
            {}
        )
        assert parse_redis_sentinel_url(
            'redis+sentinel://h1:6379,h2:6379/0'
        ) == (
            [('h1', 6379), ('h2', 6379)],
            None,
            {'db': 0}
        )
        assert parse_redis_sentinel_url(
            'redis+sentinel://user:password@h1:6379,h2:6379,h1:6380/0/myredis'
        ) == (
            [('h1', 6379), ('h2', 6379), ('h1', 6380)],
            'myredis',
            {'username': 'user', 'password': 'password', 'db': 0}
        )
