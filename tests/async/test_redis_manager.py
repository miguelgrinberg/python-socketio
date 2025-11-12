import asyncio
import pytest
import redis
import valkey
import types

from socketio import async_redis_manager
from socketio.async_redis_manager import AsyncRedisManager


class TestAsyncRedisManager:
    def test_redis_not_installed(self):
        saved_redis = async_redis_manager.aioredis
        async_redis_manager.aioredis = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('redis://')
        assert AsyncRedisManager('unix:///var/sock/redis.sock') is not None

        async_redis_manager.aioredis = saved_redis

    def test_valkey_not_installed(self):
        saved_valkey = async_redis_manager.aiovalkey
        async_redis_manager.aiovalkey = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('valkey://')
        assert AsyncRedisManager('unix:///var/sock/redis.sock') is not None

        async_redis_manager.aiovalkey = saved_valkey

    def test_redis_valkey_not_installed(self):
        saved_redis = async_redis_manager.aioredis
        async_redis_manager.aioredis = None
        saved_valkey = async_redis_manager.aiovalkey
        async_redis_manager.aiovalkey = None

        with pytest.raises(RuntimeError):
            AsyncRedisManager('redis://')
        with pytest.raises(RuntimeError):
            AsyncRedisManager('valkey://')
        with pytest.raises(RuntimeError):
            AsyncRedisManager('unix:///var/sock/redis.sock')

        async_redis_manager.aioredis = saved_redis
        async_redis_manager.aiovalkey = saved_valkey

    def test_bad_url(self):
        with pytest.raises(ValueError):
            AsyncRedisManager('http://localhost:6379')

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
            assert isinstance(c.redis, valkey.asyncio.Valkey)

        async_redis_manager.aioredis = saved_redis


class _FakePubSub:
    def __init__(self, chan_bytes, script):
        self._chan = chan_bytes
        self._script = list(script)
        self._unsubscribed = False

    async def subscribe(self, channel):
        return True

    async def unsubscribe(self, channel):
        self._unsubscribed = True
        return True

    async def listen(self):
        while self._script:
            step = self._script.pop(0)
            if step == "timeout":
                raise TimeoutError("simulated timeout")
            if step == "msg":
                yield {
                    "type": "message",
                    "channel": self._chan,
                    "data": b"ok",
                }
        while True:
            await asyncio.sleep(3600)


class _FakeRedis:
    def __init__(self, **opts):
        self._opts = opts
        self._scripts = []

    @classmethod
    def from_url(cls, url, **kwargs):
        obj = cls(**kwargs)
        return obj

    def pubsub(self, ignore_subscribe_messages=True):
        script = self._scripts.pop(0) if self._scripts else ["msg"]
        return _FakePubSub(b"socketio", script)


class _FakeSentinel:
    class Sentinel:
        def __init__(self, *a, **kw):
            pass

        def master_for(self, *a, **kw):
            return _FakeRedis()


def _fake_valkey_module():
    mod = types.SimpleNamespace()
    mod.__name__ = "valkey.asyncio"
    mod.Redis = _FakeRedis
    mod.sentinel = _FakeSentinel
    return mod


class _TestManager(AsyncRedisManager):
    """AsyncRedisManager that uses our fake 'valkey' module and scripts."""

    def __init__(self, scripts, **kw):
        # scripts is a list of lists, e.g. [["timeout"], ["msg"]]
        self._scripts = scripts
        super().__init__(url="valkey://localhost/0", **kw)

    def _get_redis_module_and_error(self):
        fake = _fake_valkey_module()
        return fake, RuntimeError

    def _redis_connect(self):
        module, _ = self._get_redis_module_and_error()
        self.redis = module.Redis.from_url(
            self.redis_url, **(self.redis_options or {})
        )
        self.redis._scripts = self._scripts
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)


@pytest.mark.asyncio
async def test_listen_reconnects_after_timeout_and_yields():
    """First TimeoutError -> reconnect + resubscribe -> yield next message."""
    mgr = _TestManager(scripts=[["timeout"], ["msg"]])
    agen = mgr._listen()

    got = await asyncio.wait_for(agen.__anext__(), timeout=2.5)
    assert got == b"ok"

    await agen.aclose()
    assert mgr.pubsub._unsubscribed is True


@pytest.mark.asyncio
async def test_listen_aclose_unsubscribes():
    """Closing the async generator must unsubscribe the pub/sub."""
    mgr = _TestManager(scripts=[["msg"]])
    agen = mgr._listen()

    _ = await asyncio.wait_for(agen.__anext__(), timeout=1.0)
    await agen.aclose()
    assert mgr.pubsub._unsubscribed is True
