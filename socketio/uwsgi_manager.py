import logging
import pickle

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

    :param url: The connection URL (only for compatibility).
                To use the default signal number, use ``uwsgi:0``.
    :param channel: The channel name on which the server sends and receives
                    notifications.
    :param write_only: If set ot ``True``, only initialize to emit events. The
                       default of ``False`` initializes the class for emitting
                       and receiving.
    """
    name = 'uwsgi'

    def __init__(self, url='uwsgi:0', channel='socketio', write_only=True,
                 logger=None):
        self._check_configuration()
        self.signum = self._sig_number(url)
        uwsgi.register_signal(self.signum, 'workers', self._enqueue)
        super(UWSGIManager, self).__init__(channel=channel,
                                           write_only=True,
                                           logger=logger)

    @staticmethod
    def _check_configuration():
        if uwsgi is None:
            raise RuntimeError('You are not running under uWSGI')
        try:
            uwsgi.queue_last()
        except AttributeError:
            raise RuntimeError('uWSGI queue must be enabled with '
                               'option --queue 1')

    @staticmethod
    def _sig_number(url):
        if ':' in url:
            try:
                sig = int(url.split(':')[1])
            except ValueError:
                logger.warning('Bad URL format %s, uWSGI signal '
                               'is listening on default (0)' % url)
            else:
                return sig
        return 0

    def _publish(self, data):
        logger.warning('publish from worker %s' % uwsgi.worker_id())
        uwsgi.queue_push(pickle.dumps(data))
        uwsgi.signal(self.signum)

    def _enqueue(self, signum):
        logger.warning('emit from worker %s' % uwsgi.worker_id())
        self._internal_emit(uwsgi.queue_last())

    def _internal_emit(self, data):
        data = pickle.loads(data)
        if data and 'method' in data:
            if data['method'] == 'emit':
                self._handle_emit(data)
            elif data['method'] == 'callback':
                self._handle_callback(data)
            elif data['method'] == 'disconnect':
                self._handle_disconnect(data)
            elif data['method'] == 'close_room':
                self._handle_close_room(data)

    def _listen(self):
        pass
