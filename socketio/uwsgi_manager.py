import logging
import pickle
from queue import Queue

try:
    import uwsgi
except ImportError:
    uwsgi = None

from .pubsub_manager import PubSubManager

logger = logging.getLogger('socketio')


class UWSGIManager(PubSubManager):  # pragma: no cover
    """Uwsgi based client manager.

    This class implements a UWSGI backend for event sharing across multiple
    processes.

    To use a uWSGI backend, initialize the :class:`Server` instance as
    follows::

        server = socketio.Server(client_manager=socketio.UWSGIManager())

    :param channel: The channel number on which the uWSGI Signal is propagated
                    accross processes.
    :param write_only: If set ot ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """
    name = 'uwsgi'

    def __init__(self, url='uwsgi:0', channel='socketio', write_only=False, logger=None):
        self._check_configuration()
        self.signum = self._sig_number(url)
        self.queue = Queue()  # uWSGI does not provide a a blocking queue
        super(UWSGIManager, self).__init__(channel=channel,
                                           write_only=write_only,
                                           logger=logger)

    @staticmethod
    def _check_configuration():
        if uwsgi is None:
            raise RuntimeError('You are not running under uWSGI')
        try:
            uwsgi.queue_last()
        except AttributeError:
            raise RuntimeError('uWSGI queue must be enabled with option --queue 1')

    @staticmethod
    def _sig_number(url):
        if ':' in url:
            try:
                sig = int(url.split(':')[1])
            except ValueError:
                logger.warning('Bad URL format %s, uWSGI signal is listening on default (1)' % url)
            else:
                return sig
        return 0

    def _publish(self, data):
        uwsgi.queue_push(pickle.dumps(data))
        uwsgi.signal(self.signum)

    def _enqueue(self, signum):
        self.queue.put(uwsgi.queue_last())

    def _uwsgi_listen(self):
        uwsgi.register_signal(self.signum, 'workers', self._enqueue)
        for message in iter(self.queue.get, None):
            if message is not None:
                yield message

    def _listen(self):
        for message in self._uwsgi_listen():
            yield pickle.loads(message)
