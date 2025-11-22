import pytest
import redis
import valkey

from socketio import redis_manager
from socketio.redis_manager import RedisManager, parse_redis_sentinel_url


class TestPubSubManager:
    def test_redis_not_installed(self):
        saved_redis = redis_manager.redis
        redis_manager.redis = None

        with pytest.raises(RuntimeError):
            RedisManager('redis://')._redis_connect()
        assert RedisManager('unix:///var/sock/redis.sock') is not None

        redis_manager.redis = saved_redis

    def test_valkey_not_installed(self):
        saved_valkey = redis_manager.valkey
        redis_manager.valkey = None

        with pytest.raises(RuntimeError):
            RedisManager('valkey://')._redis_connect()
        assert RedisManager('unix:///var/sock/redis.sock') is not None

        redis_manager.valkey = saved_valkey

    def test_redis_valkey_not_installed(self):
        saved_redis = redis_manager.redis
        redis_manager.redis = None
        saved_valkey = redis_manager.valkey
        redis_manager.valkey = None

        with pytest.raises(RuntimeError):
            RedisManager('redis://')._redis_connect()
        with pytest.raises(RuntimeError):
            RedisManager('valkey://')._redis_connect()
        with pytest.raises(RuntimeError):
            RedisManager('unix:///var/sock/redis.sock')._redis_connect()

        redis_manager.redis = saved_redis
        redis_manager.valkey = saved_valkey

    def test_bad_url(self):
        with pytest.raises(ValueError):
            RedisManager('http://localhost:6379')._redis_connect()

    def test_redis_connect(self):
        urls = [
            'redis://localhost:6379',
            'redis://localhost:6379/0',
            'redis://:password@localhost:6379',
            'redis://:password@localhost:6379/0',
            'redis://user:password@localhost:6379',
            'redis://user:password@localhost:6379/0',

            'rediss://localhost:6379',
            'rediss://localhost:6379/0',
            'rediss://:password@localhost:6379',
            'rediss://:password@localhost:6379/0',
            'rediss://user:password@localhost:6379',
            'rediss://user:password@localhost:6379/0',

            'unix:///var/sock/redis.sock',
            'unix:///var/sock/redis.sock?db=0',
            'unix://user@/var/sock/redis.sock',
            'unix://user@/var/sock/redis.sock?db=0',

            'redis+sentinel://192.168.0.1:6379,192.168.0.2:6379/'
        ]
        for url in urls:
            c = RedisManager(url)
            assert c.redis is None
            c._redis_connect()
            assert isinstance(c.redis, redis.Redis)

    def test_valkey_connect(self):
        saved_redis = redis_manager.redis
        redis_manager.redis = None

        urls = [
            'valkey://localhost:6379',
            'valkey://localhost:6379/0',
            'valkey://:password@localhost:6379',
            'valkey://:password@localhost:6379/0',
            'valkey://user:password@localhost:6379',
            'valkey://user:password@localhost:6379/0',

            'valkeys://localhost:6379',
            'valkeys://localhost:6379/0',
            'valkeys://:password@localhost:6379',
            'valkeys://:password@localhost:6379/0',
            'valkeys://user:password@localhost:6379',
            'valkeys://user:password@localhost:6379/0',

            'unix:///var/sock/redis.sock',
            'unix:///var/sock/redis.sock?db=0',
            'unix://user@/var/sock/redis.sock',
            'unix://user@/var/sock/redis.sock?db=0',

            'valkey+sentinel://192.168.0.1:6379,192.168.0.2:6379/'
        ]
        for url in urls:
            c = RedisManager(url)
            assert c.redis is None
            c._redis_connect()
            assert isinstance(c.redis, valkey.Valkey)

        redis_manager.redis = saved_redis

    @pytest.mark.parametrize('rtype', ['redis', 'valkey'])
    def test_sentinel_url_parser(self, rtype):
        with pytest.raises(ValueError):
            parse_redis_sentinel_url(f'{rtype}://localhost:6379/0')

        assert parse_redis_sentinel_url(
            f'{rtype}+sentinel://localhost:6379'
        ) == (
            [('localhost', 6379)],
            None,
            {}
        )
        assert parse_redis_sentinel_url(
            f'{rtype}+sentinel://192.168.0.1:6379,192.168.0.2:6379/'
        ) == (
            [('192.168.0.1', 6379), ('192.168.0.2', 6379)],
            None,
            {}
        )
        assert parse_redis_sentinel_url(
            f'{rtype}+sentinel://h1:6379,h2:6379/0'
        ) == (
            [('h1', 6379), ('h2', 6379)],
            None,
            {'db': 0}
        )
        assert parse_redis_sentinel_url(
            f'{rtype}+sentinel://'
            'user:password@h1:6379,h2:6379,h1:6380/0/myredis'
        ) == (
            [('h1', 6379), ('h2', 6379), ('h1', 6380)],
            'myredis',
            {'username': 'user', 'password': 'password', 'db': 0}
        )
