import pickle
import uuid

try:
    import kombu
except ImportError:
    kombu = None

from .pubsub_manager import PubSubManager


class KombuManager(PubSubManager):  # pragma: no cover
    """Client manager that uses kombu for inter-process messaging.

    This class implements a client manager backend for event sharing across
    multiple processes, using RabbitMQ, Redis or any other messaging mechanism
    supported by `kombu <http://kombu.readthedocs.org/en/latest/>`_.

    To use a kombu backend, initialize the :class:`Server` instance as
    follows::

        url = 'amqp://user:password@hostname:port//'
        server = socketio.Server(client_manager=socketio.KombuManager(url))

    :param url: The connection URL for the backend messaging queue. Example
                connection URLs are ``'amqp://guest:guest@localhost:5672//'``
                and ``'redis://localhost:6379/'`` for RabbitMQ and Redis
                respectively. Consult the `kombu documentation
                <http://kombu.readthedocs.org/en/latest/userguide\
                /connections.html#urls>`_ for more on how to construct
                connection URLs.
    :param channel: The channel name on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set ot ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """
    name = 'kombu'

    def __init__(self, url='amqp://guest:guest@localhost:5672//',
                 channel='socketio', write_only=False):
        if kombu is None:
            raise RuntimeError('Kombu package is not installed '
                               '(Run "pip install kombu" in your '
                               'virtualenv).')
        super(KombuManager, self).__init__(channel=channel)
        self.url = url
        self.writer_conn = kombu.Connection(self.url)
        self.writer_queue = self._queue(self.writer_conn)

    def _queue(self, conn=None):
        exchange = kombu.Exchange(self.channel, type='fanout', durable=False)
        queue = kombu.Queue(str(uuid.uuid4()), exchange)
        return queue

    def _publish(self, data):
        with self.writer_conn.SimpleQueue(self.writer_queue) as queue:
            queue.put(pickle.dumps(data))

    def _listen(self):
        reader_conn = kombu.Connection(self.url)
        reader_queue = self._queue(reader_conn)
        with reader_conn.SimpleQueue(reader_queue) as queue:
            while True:
                message = queue.get(block=True)
                message.ack()
                yield message.payload
