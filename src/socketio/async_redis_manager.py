import asyncio
import contextlib
import random
from urllib.parse import urlparse

try:
    from redis import asyncio as aioredis
    from redis.exceptions import RedisError
except ImportError:  # pragma: no cover
    try:
        import aioredis
        from aioredis.exceptions import RedisError
    except ImportError:
        aioredis = None
        RedisError = None

try:
    from valkey import asyncio as aiovalkey
    from valkey.exceptions import ValkeyError
except ImportError:  # pragma: no cover
    aiovalkey = None
    ValkeyError = None

from engineio import json
from .async_pubsub_manager import AsyncPubSubManager
from .redis_manager import parse_redis_sentinel_url


class AsyncRedisManager(AsyncPubSubManager):
    """Redis based client manager for asyncio servers.

    This class implements a Redis backend for event sharing across multiple
    processes.

    To use a Redis backend, initialize the :class:`AsyncServer` instance as
    follows::

        url = 'redis://hostname:port/0'
        server = socketio.AsyncServer(
            client_manager=socketio.AsyncRedisManager(url))

    :param url: The connection URL for the Redis server. For a default Redis
                store running on the same host, use ``redis://``.  To use a
                TLS connection, use ``rediss://``. To use Redis Sentinel, use
                ``redis+sentinel://`` with a comma-separated list of hosts
                and the service name after the db in the URL path. Example:
                ``redis+sentinel://user:pw@host1:1234,host2:2345/0/myredis``.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set to ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    :param redis_options: additional keyword arguments to be passed to
                          ``Redis.from_url()`` or ``Sentinel()``.
    """

    name = "aioredis"

    def __init__(
        self,
        url="redis://localhost:6379/0",
        channel="socketio",
        write_only=False,
        logger=None,
        redis_options=None,
    ):
        if aioredis and not hasattr(
            aioredis.Redis, "from_url"
        ):  # pragma: no cover
            raise RuntimeError("Version 2 of aioredis package is required.")
        super().__init__(channel=channel, write_only=write_only, logger=logger)
        self.redis_url = url
        self.redis_options = redis_options or {}
        self._redis_connect()

    def _get_redis_module_and_error(self):
        parsed_url = urlparse(self.redis_url)
        scheme = parsed_url.scheme.split("+", 1)[0].lower()
        if scheme in ["redis", "rediss"]:
            if aioredis is None or RedisError is None:
                raise RuntimeError(
                    "Redis package is not installed "
                    '(Run "pip install redis" '
                    "in your virtualenv)."
                )
            return aioredis, RedisError
        if scheme in ["valkey", "valkeys"]:
            if aiovalkey is None or ValkeyError is None:
                raise RuntimeError(
                    "Valkey package is not installed "
                    '(Run "pip install valkey" '
                    "in your virtualenv)."
                )
            return aiovalkey, ValkeyError
        if scheme == "unix":
            if aioredis is not None and RedisError is not None:
                return aioredis, RedisError
            if aiovalkey is not None and ValkeyError is not None:
                return aiovalkey, ValkeyError
            raise RuntimeError('Install "redis" or "valkey" package.')
        raise ValueError(f"Unsupported Redis URL scheme: {scheme}")

    def _redis_connect(self):
        module, _ = self._get_redis_module_and_error()
        parsed_url = urlparse(self.redis_url)

        # Backend-aware pubsub socket defaults. Caller can override.
        is_valkey = module.__name__.startswith("valkey.")
        pubsub_defaults = {
            "decode_responses": False,
            "socket_keepalive": True,
            "retry_on_timeout": False,
        }
        if is_valkey:
            pubsub_defaults.update(
                {
                    "socket_timeout": None,  # block indefinitely
                    "socket_connect_timeout": 3,  # fail fast on bad host
                    "health_check_interval": 0,  # no PINGs on pubsub socket
                }
            )

        kwargs = {**pubsub_defaults, **(self.redis_options or {})}

        if parsed_url.scheme in {"redis+sentinel", "valkey+sentinel"}:
            sentinels, service_name, connection_kwargs = (
                parse_redis_sentinel_url(self.redis_url)
            )
            connection_kwargs.update(kwargs)
            sentinel = module.sentinel.Sentinel(sentinels, **connection_kwargs)
            self.redis = sentinel.master_for(service_name or self.channel)
        else:
            self.redis = module.Redis.from_url(self.redis_url, **kwargs)

        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)

    async def _publish(self, data):  # pragma: no cover
        retry = True
        _, error = self._get_redis_module_and_error()
        while True:
            try:
                if not retry:
                    self._redis_connect()
                return await self.redis.publish(
                    self.channel, json.dumps(data))
            except error as exc:
                if retry:
                    self._get_logger().error(
                        'Cannot publish to redis... '
                        'retrying',
                        extra={"redis_exception": str(exc)})
                    retry = False
                else:
                    self._get_logger().error(
                        'Cannot publish to redis... '
                        'giving up',
                        extra={"redis_exception": str(exc)})

                    break

    async def _redis_listen_with_retries(self):  # pragma: no cover
        """
        Stream pub/sub messages forever; auto-reconnect on transient errors.
        - Works with both Redis and Valkey (we detect the right error class).
        - Backoff: 1s -> 2 -> 4 ... capped at 60s, with ±20% jitter.
        - Any successfully received message resets the backoff to 1s.
        - On shutdown (CancelledError) we try to unsubscribe cleanly.
        """
        backoff = 1.0
        max_backoff = 60.0
        connect_needed = True
        _, BackendError = self._get_redis_module_and_error()
        backend_name = getattr(self, "name", "redis")

        while True:
            try:
                if connect_needed:
                    self._redis_connect()
                    await self.pubsub.subscribe(self.channel)
                    connect_needed = False

                async for message in self.pubsub.listen():
                    backoff = 1.0
                    yield message

            except asyncio.CancelledError:
                with contextlib.suppress(Exception):
                    await self.pubsub.unsubscribe(self.channel)
                raise

            except (BackendError, OSError, TimeoutError) as exc:
                self._get_logger().error(
                    "%s pub/sub listen error; reconnecting in %.1fs",
                    backend_name,
                    backoff,
                    extra={"backend_exception": str(exc)},
                )
                connect_needed = True

                jitter = backoff * (random.random() * 0.4 - 0.2)
                await asyncio.sleep(max(0.0, backoff + jitter))
                backoff = min(backoff * 2, max_backoff)

    @staticmethod
    def _channel_matches(expected: bytes, msg_channel) -> bool:
        if isinstance(msg_channel, bytes):
            return msg_channel == expected
        if isinstance(msg_channel, str):
            try:
                return msg_channel.encode("utf-8") == expected
            except Exception:
                return False
        return False

    async def _listen(self):  # pragma: no cover
        """Continuously listen on the pub/sub channel and yield messages."""
        expected = self.channel.encode("utf-8")
        await self.pubsub.subscribe(self.channel)

        async for message in self._redis_listen_with_retries():
            if (
                message.get("type") == "message"
                and "data" in message
                and self._channel_matches(expected, message.get("channel"))
            ):
                yield message["data"]

        await self.pubsub.unsubscribe(self.channel)
