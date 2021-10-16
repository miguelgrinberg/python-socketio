import asyncio
import pickle
from urllib.parse import urlparse

try:
    import aioredis
except ImportError:
    aioredis = None

from .asyncio_pubsub_manager import AsyncPubSubManager


class AsyncRedisManager(AsyncPubSubManager):  # pragma: no cover
    """Redis based client manager for asyncio servers.

    This class implements a Redis backend for event sharing across multiple
    processes. Only kept here as one more example of how to build a custom
    backend, since the kombu backend is perfectly adequate to support a Redis
    message queue.

    To use a Redis backend, initialize the :class:`Server` instance as
    follows::

        server = socketio.Server(client_manager=socketio.AsyncRedisManager(
            'redis://hostname:port/0'))

    :param url: The connection URL for the Redis server. For a default Redis
                store running on the same host, use ``redis://``.  To use an
                SSL connection, use ``rediss://``.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set to ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """
    name = 'aioredis'

    def __init__(self, url='redis://localhost:6379/0', channel='socketio',
                 write_only=False, logger=None, redis_options={}):
        if aioredis is None:
            raise RuntimeError('Redis package is not installed '
                               '(Run "pip install aioredis" in your '
                               'virtualenv).')
        self.redis = aioredis.from_url(url, **redis_options)
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        super().__init__(channel=channel, write_only=write_only, logger=logger)

    async def _publish(self, data):
        retry = True
        while True:
            try:
                return await self.redis.publish(self.channel, pickle.dumps(data))
            except redis.exceptions.RedisError:
                if retry:
                    self._get_logger().error('Cannot publish to redis... retrying')
                    retry = False
                else:
                    self._get_logger().error('Cannot publish to redis... giving up')
                    break

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
        await self.pubsub.unsubscribe(self.channel)
