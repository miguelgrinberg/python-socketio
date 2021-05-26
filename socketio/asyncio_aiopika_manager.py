import asyncio
import pickle

from socketio.asyncio_pubsub_manager import AsyncPubSubManager

try:
    import aio_pika
except ImportError:
    aio_pika = None


class AsyncAioPikaManager(AsyncPubSubManager):  # pragma: no cover
    """Client manager that uses aio_pika for inter-process messaging under
    asyncio.

    This class implements a client manager backend for event sharing across
    multiple processes, using RabbitMQ

    To use a aio_pika backend, initialize the :class:`Server` instance as
    follows::

        url = 'amqp://user:password@hostname:port//'
        server = socketio.Server(client_manager=socketio.AsyncAioPikaManager(
            url))

    :param url: The connection URL for the backend messaging queue. Example
                connection URLs are ``'amqp://guest:guest@localhost:5672//'``
                for RabbitMQ.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
                    With this manager, the channel name is the exchange name
                    in rabbitmq
    :param write_only: If set to ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """

    name = 'asyncaiopika'

    def __init__(self, url='amqp://guest:guest@localhost:5672//',
                 channel='socketio', write_only=False, logger=None):
        if aio_pika is None:
            raise RuntimeError('aio_pika package is not installed '
                               '(Run "pip install aio_pika" in your '
                               'virtualenv).')
        self.url = url
        self.listener_connection = None
        self.listener_channel = None
        self.listener_exchange = None
        self.listener_queue = None
        super().__init__(channel=channel, write_only=write_only, logger=logger)

    async def _initialize(self):
        """
        initialization aio_pika connection, channel, exchange and queue

        """
        self.listener_connection = await aio_pika.connect_robust(url=self.url)
        self.listener_channel = await self.listener_connection.channel()
        self.listener_exchange = await self.listener_channel.declare_exchange(self.channel,
                                                                              aio_pika.ExchangeType.FANOUT)

        if not self.write_only:
            await self.listener_channel.set_qos(prefetch_count=1)
            self.listener_queue = await self.listener_channel.declare_queue(durable=False)
            await self.listener_queue.bind(self.listener_exchange)
        AsyncPubSubManager.initialize(self)

    def initialize(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._initialize())

    async def _publish(self, data):
        await self.listener_exchange.publish(
            aio_pika.Message(body=pickle.dumps(data),
                             delivery_mode=aio_pika.DeliveryMode.PERSISTENT),
            routing_key='*'
        )

    async def _listen(self):
        retry_sleep = 1
        while True:
            try:
                if self.listener_connection is None:
                    await self._initialize()

                async with self.listener_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        with message.process():
                            return pickle.loads(message.body)
            except Exception:
                self._get_logger().error('Cannot receive from rabbitmq... '
                                         'retrying in '
                                         '{} secs'.format(retry_sleep))
                self.listener_connection = None
                await asyncio.sleep(retry_sleep)
                retry_sleep *= 2
                if retry_sleep > 60:
                    retry_sleep = 60
