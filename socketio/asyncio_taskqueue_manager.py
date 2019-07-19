import asyncio
import json
import pickle

import six
from socketio.asyncio_manager import AsyncManager


class AsyncTaskQueueManager(AsyncManager):
    name = 'asynctaskqueue'

    def __init__(self, channel='socketio', write_only=False, logger=None):
        super().__init__()
        self.channel = channel
        self.write_only = write_only
        self.logger = logger
        self.tasks = {}

    def register_task(self, task_queue):
        self.tasks[task_queue] = asyncio.create_task(self._task(task_queue))
        self._get_logger().info('Starting async listening task for %s',
                                task_queue)

    def cancel_task(self, task_queue):
        self.tasks[task_queue].cancel()
        self._get_logger().info('Canceled async listening task for %s',
                                task_queue)
        del self.tasks[task_queue]

    async def emit(self, event, data, task_queue, namespace=None, room=None,
                   **kwargs):
        """Emit a message to a task queue

        Note: this method is a coroutine.
        """
        await self._publish(
            task_queue,
            {
                'event': event, 'data': data,
                'namespace': namespace or '/', 'room': room
            }
        )

    async def _publish(self, task_queue, data):
        """Publish a message on the Socket.IO channel.

        This method needs to be implemented by the different subclasses that
        support task queue backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')  # pragma: no cover

    async def _listen(self, task_queue):
        """Return the next message published on the Socket.IO channel,
        blocking until a message is available.

        This method needs to be implemented by the different subclasses that
        support task queue backends.
        """
        raise NotImplementedError('This method must be implemented in a '
                                  'subclass.')  # pragma: no cover

    async def _handle_emit(self, message):
        await super().emit(message['event'], message['data'],
                           namespace=message.get('namespace'),
                           room=message.get('room'))

    async def _task(self, task_queue):
        while True:
            try:
                message = await self._listen(task_queue)
            except asyncio.CancelledError:
                self._get_logger().debug('Task queue %s canceled', task_queue)
                raise
            except Exception:
                self._get_logger().exception('Unexpected error in task queue '
                                             'listener')
                break
            data = None
            if isinstance(message, dict):
                data = message
            else:
                if isinstance(message, six.binary_type):  # pragma: no cover
                    try:
                        data = pickle.loads(message)
                    except:
                        pass
                if data is None:
                    try:
                        data = json.loads(message)
                    except:
                        pass
            if data:
                await self._handle_emit(data)
