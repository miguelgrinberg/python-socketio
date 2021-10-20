import asyncio
import pickle

try:
    import aioredis
except ImportError:
    aioredis = None

from .asyncio_pubsub_manager import AsyncPubSubManager


class AsyncRedisManager(AsyncPubSubManager):  # pragma: no cover
    """Redis based client manager for asyncio servers.

    This class implements a Redis backend for event sharing across multiple
    processes.

    To use a Redis backend, initialize the :class:`AsyncServer` instance as
    follows::

        url = 'redis://hostname:port/0'
        server = socketio.AsyncServer(
            client_manager=socketio.AsyncRedisManager(url))

    :param url: The connection URL for the Redis server. For a default Redis
                store running on the same host, use ``redis://``.  To use an
                SSL connection, use ``rediss://``.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set to ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    :param redis_options: additional keyword arguments to be passed to
                          ``aioredis.from_url()``.
    """
    name = 'aioredis'

    def __init__(self, url='redis://localhost:6379/0', channel='socketio',
                 write_only=False, logger=None, redis_options={}):
        if aioredis is None:
            raise RuntimeError('Redis package is not installed '
                               '(Run "pip install aioredis" in your '
                               'virtualenv).')
        if not hasattr(aioredis.Redis, 'from_url'):
            raise RuntimeError('Version 2 of aioredis package is required.')
        self.redis = aioredis.Redis.from_url(url, **redis_options)
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        super().__init__(channel=channel, write_only=write_only, logger=logger)

    async def _publish(self, data):
        return await self.redis.publish(self.channel, pickle.dumps(data))

    async def _listen(self):
        retry_sleep = 1
        while True:
            try:
                await self.pubsub.subscribe(self.channel)
                retry_sleep = 1
                async for message in self.pubsub.listen():
                    yield message['data']
            except aioredis.exceptions.RedisError:
                self._get_logger().error('Cannot receive from redis... '
                             'retrying in {} secs'.format(retry_sleep))
                await asyncio.sleep(retry_sleep)
                retry_sleep *= 2
                if retry_sleep > 60:
                    retry_sleep = 60

