import asyncio
import pickle

from .asyncio_taskqueue_manager import AsyncTaskQueueManager

try:
    import aio_pika
except ImportError:
    aio_pika = None


class AsyncTaskQueueAioPikaManager(AsyncTaskQueueManager):
    name = 'asynctaskqueueaiopika'

    def __init__(self, url='amqp://guest:guest@localhost:5672//',
                 channel='socketio', write_only=False, logger=None):
        if aio_pika is None:
            raise RuntimeError('aio_pika package is not installed '
                               '(Run "pip install aio_pika" in your '
                               'virtualenv).')
        self.url = url
        self.publisher_connection = None
        self.publisher_channel = None
        self.publisher_exchange = None
        self.listener_connection = None
        self.listener_channel = None
        self.listener_exchange = None
        self.listener_queues = {}
        super().__init__(channel=channel, write_only=write_only, logger=logger)

    async def _connect_publisher(self):
        self.publisher_connection = await aio_pika.connect_robust(self.url)
        self.publisher_channel = await self.publisher_connection.channel()
        self.publisher_exchange = \
            await self.publisher_channel.declare_exchange(
                self.channel, aio_pika.ExchangeType.DIRECT)

    async def _connect_listener(self):
        self.listener_connection = await aio_pika.connect_robust(self.url)
        self.listener_channel = await self.listener_connection.channel()
        await self.listener_channel.set_qos(prefetch_count=1)
        self.listener_exchange = await self.listener_channel.declare_exchange(
            self.channel, aio_pika.ExchangeType.DIRECT)

    def _reset_listener(self):
        self.listener_connection = None
        self.listener_queues = {}

    async def _declare_queue(self, task_queue):
        queue = await self.listener_channel.declare_queue(durable=True)
        await queue.bind(self.listener_exchange, routing_key=task_queue)
        return queue

    async def _publish(self, task_queue, data, retry=True):
        try:
            if self.publisher_connection is None:
                await self._connect_publisher()

            await self.publisher_exchange.publish(
                aio_pika.Message(
                    body=pickle.dumps(data),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=task_queue
            )
        except (aio_pika.exceptions.AMQPChannelError,
                aio_pika.exceptions.AMQPConnectionError):
            if retry:
                self._get_logger().exception('Error while publishing event, '
                                             'retrying in 1sec')
                self.publisher_connection = None
                await asyncio.sleep(1)
                await self._publish(task_queue, data, retry=False)
            else:
                self._get_logger().exception('Error while publishing event, '
                                             'giving up')
                self.publisher_connection = None
                raise

    async def _listen(self, task_queue):
        retry_sleep = 1
        while True:
            try:
                if self.listener_connection is None:
                    await self._connect_listener()

                if task_queue not in self.listener_queues:
                    self.listener_queues[task_queue] = \
                        await self._declare_queue(task_queue)

                async with self.listener_queues[task_queue].iterator() as \
                        queue_iter:
                    async for message in queue_iter:
                        with message.process():
                            return pickle.loads(message.body)

            except (aio_pika.exceptions.AMQPChannelError,
                    aio_pika.exceptions.AMQPConnectionError):
                self._get_logger().exception('Error in listener for task queue'
                                             ' %s, retrying in %ss',
                                             task_queue, retry_sleep)
                self._reset_listener()
                await asyncio.sleep(retry_sleep)
                retry_sleep *= 2
                if retry_sleep > 60:
                    retry_sleep = 60
