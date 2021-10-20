import pickle
import time

try:
    import redis
except ImportError:
    redis = None

from .pubsub_manager import PubSubManager


class RedisManager(PubSubManager):  # pragma: no cover
    """Redis based client manager.

    This class implements a Redis backend for event sharing across multiple
    processes. Only kept here as one more example of how to build a custom
    backend, since the kombu backend is perfectly adequate to support a Redis
    message queue.

    To use a Redis backend, initialize the :class:`Server` instance as
    follows::

        url = 'redis://hostname:port/0'
        server = socketio.Server(client_manager=socketio.RedisManager(url))

    :param url: The connection URL for the Redis server. For a default Redis
                store running on the same host, use ``redis://``.  To use an
                SSL connection, use ``rediss://``.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set to ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    :param redis_options: additional keyword arguments to be passed to
                          ``Redis.from_url()``.
    """
    name = 'redis'

    def __init__(self, url='redis://localhost:6379/0', channel='socketio',
                 write_only=False, logger=None, redis_options=None):
        if redis is None:
            raise RuntimeError('Redis package is not installed '
                               '(Run "pip install redis" in your '
                               'virtualenv).')
        self.redis = redis.Redis.from_url(url, **(redis_options or {}))
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        super(RedisManager, self).__init__(channel=channel,
                                           write_only=write_only,
                                           logger=logger)

    def initialize(self):
        super(RedisManager, self).initialize()

        monkey_patched = True
        if self.server.async_mode == 'eventlet':
            from eventlet.patcher import is_monkey_patched
            monkey_patched = is_monkey_patched('socket')
        elif 'gevent' in self.server.async_mode:
            from gevent.monkey import is_module_patched
            monkey_patched = is_module_patched('socket')
        if not monkey_patched:
            raise RuntimeError(
                'Redis requires a monkey patched socket library to work '
                'with ' + self.server.async_mode)

    def _publish(self, data):
        return self.redis.publish(self.channel, pickle.dumps(data))

    def _listen(self):
        retry_sleep = 1
        while True:
            try:
                self.pubsub.subscribe(self.channel)
                retry_sleep = 1
                for message in self.pubsub.listen():
                    yield message['data']
            except redis.exceptions.RedisError:
                self._get_logger().error(
                    "Cannot receive from redis... "
                    "retrying in {} secs".format(retry_sleep)
                )
                time.sleep(retry_sleep)
                retry_sleep *= 2
                if retry_sleep > 60:
                    retry_sleep = 60
