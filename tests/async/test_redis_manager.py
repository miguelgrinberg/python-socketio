import pytest
import redis
import valkey

from socketio import async_redis_manager
from socketio.async_redis_manager import AsyncRedisManager


class TestAsyncRedisManager:
    def test_redis_not_installed(self):
        saved_redis = async_redis_manager.aioredis
        async_redis_manager.aioredis = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('redis://')._redis_connect()
        assert AsyncRedisManager('unix:///var/sock/redis.sock') is not None

        async_redis_manager.aioredis = saved_redis

    def test_valkey_not_installed(self):
        saved_valkey = async_redis_manager.aiovalkey
        async_redis_manager.aiovalkey = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('valkey://')._redis_connect()
        assert AsyncRedisManager('unix:///var/sock/redis.sock') is not None

        async_redis_manager.aiovalkey = saved_valkey

    def test_redis_valkey_not_installed(self):
        saved_redis = async_redis_manager.aioredis
        async_redis_manager.aioredis = None
        saved_valkey = async_redis_manager.aiovalkey
        async_redis_manager.aiovalkey = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('redis://')._redis_connect()
        with pytest.raises(RuntimeError):
            AsyncRedisManager('valkey://')._redis_connect()
        with pytest.raises(RuntimeError):
            AsyncRedisManager('unix:///var/sock/redis.sock')._redis_connect()

        async_redis_manager.aioredis = saved_redis
        async_redis_manager.aiovalkey = saved_valkey

    def test_bad_url(self):
        with pytest.raises(ValueError):
            AsyncRedisManager('http://localhost:6379')._redis_connect()

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
            c = AsyncRedisManager(url)
            assert c.redis is None
            c._redis_connect()
            assert isinstance(c.redis, redis.asyncio.Redis)

    def test_valkey_connect(self):
        saved_redis = async_redis_manager.aioredis
        async_redis_manager.aioredis = None

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
            c = AsyncRedisManager(url)
            assert c.redis is None
            c._redis_connect()
            assert isinstance(c.redis, valkey.asyncio.Valkey)

        async_redis_manager.aioredis = saved_redis
