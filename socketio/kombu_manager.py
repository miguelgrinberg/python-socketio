import pickle

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
    """
    name = 'kombu'

    def __init__(self, url='amqp://guest:guest@localhost:5672//',
                 channel='socketio'):
        if kombu is None:
            raise RuntimeError('Kombu package is not installed '
                               '(Run "pip install kombu" in your '
                               'virtualenv).')
        self.kombu = kombu.Connection(url)
        self.queue = self.kombu.SimpleQueue(channel)
        super(KombuManager, self).__init__(channel=channel)

    def _publish(self, data):
        return self.queue.put(pickle.dumps(data))

    def _listen(self):
        listen_queue = self.kombu.SimpleQueue(self.channel)
        while True:
            message = listen_queue.get(block=True)
            message.ack()
            yield message.payload
