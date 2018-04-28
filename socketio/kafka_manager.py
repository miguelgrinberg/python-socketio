import logging
import pickle
import time
import json

try:
    import kafka
except ImportError:
    kafka = None

from .pubsub_manager import PubSubManager

logger = logging.getLogger('socketio')


class KafkaManager(PubSubManager):  # pragma: no cover
    """Kafka based client manager.

    This class implements a Kafka backend for event sharing across multiple
    processes.

    To use a Kafka backend, initialize the :class:`Server` instance as
    follows::

        url = 'kafka://hostname:port/0'
        server = socketio.Server(client_manager=socketio.KafkaManager(url))

    :param url: The connection URL for the Kafka server. For a default Kafka
                store running on the same host, use ``kafka://``.
    :param channel: The channel name (topic) on which the server sends and receives
                    notifications. Must be the same in all the servers.
    :param write_only: If set ot ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """
    name = 'kafka'

    def __init__(self, url='kafka://localhost:9092/0', channel='socketio',
                 write_only=False):
        if kafka is None:
            raise RuntimeError('kafka-python package is not installed '
                               '(Run "pip install kafka-python" in your '
                               'virtualenv).')
        self.kafka_url = url
        self.producer = kafka.KafkaProducer(bootstrap_servers='localhost:9092')

        super(KafkaManager, self).__init__(channel=channel,
                                           write_only=write_only)

    def initialize(self):
        super(KafkaManager, self).initialize()
        monkey_patched = True
        if self.server.async_mode == 'eventlet':
            from eventlet.patcher import is_monkey_patched
            monkey_patched = is_monkey_patched('socket')
        elif 'gevent' in self.server.async_mode:
            from gevent.monkey import is_module_patched
            monkey_patched = is_module_patched('socket')
        if not monkey_patched:
            raise RuntimeError(
                'Kafka requires a monkey patched socket library to work '
                'with ' + self.server.async_mode)


    def _publish(self, data):
        self.producer.send(self.channel, value=pickle.dumps(data))
        self.producer.flush()


    def _kafka_listen(self):
        self.consumer = kafka.KafkaConsumer(self.channel, bootstrap_servers='localhost:9092')
        for message in self.consumer:
            yield message


    def _listen(self):
        for message in self._kafka_listen():
            if message.topic == self.channel:
                yield pickle.loads(message.value)
