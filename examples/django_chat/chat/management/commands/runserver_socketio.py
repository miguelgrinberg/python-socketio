from re import match
from _thread import start_new_thread
from time import sleep
from os import getpid, kill, environ
from signal import SIGINT
import six
import copy

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands.runserver import naiveip_re, DEFAULT_PORT
from django.utils.autoreload import code_changed, restart_with_reloader
from django.core.wsgi import get_wsgi_application

# from gevent import pywsgi
from sdjango import autodiscover
from sdjango import namespace
from sdjango.sd_manager import SdManager
from sdjango.sd_middleware import SdMiddleware
import socketio
import eventlet


RELOAD = False

def reload_watcher():
    global RELOAD
    while True:
        RELOAD = code_changed()
        if RELOAD:
            kill(getpid(), SIGINT)
            restart_with_reloader()
        sleep(1)

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('addrport', nargs='?', help='Optional port number, or ipaddr:port')

    def handle(self, *args, **options):
        from django.utils import translation
        from django.conf import settings

        translation.activate(settings.LANGUAGE_CODE)
        addrport = options.get('addrport', None)
        if addrport is None:
            self.addr = ''
            self.port = DEFAULT_PORT
        else:
            m = match(naiveip_re, addrport)
            if m is None:
                raise CommandError('"%s" is not a valid port number '
                                   'or address:port pair.' % options['addrport'])
            self.addr, _ipv4, ipv6, _fqdn, self.port = m.groups()

            if not self.port.isdigit():
                raise CommandError('"%s" is not a valid port number' % self.port)

            if not self.addr:
                self.addr = '127.0.0.1'
        # Make the port available here for the path:
        #   socketio_tags.socketio ->
        #   socketio_scripts.html ->
        #   io.Socket JS constructor
        # allowing the port to be set as the client-side default there.
        environ["DJANGO_SOCKETIO_PORT"] = str(self.port)

        if settings.DEBUG is True:
            start_new_thread(reload_watcher, ())

        try:
            bind = (self.addr, int(self.port))
            print("SocketIOServer running on %s:%s" % bind)
            handler = self.get_handler(*args, **options)

            # sio = socketio.Server(client_manager=SdManager(), async_mode='gevent')
            sio = socketio.Server(client_manager=SdManager(), async_mode='eventlet')
            autodiscover()
            namespace.insert_in_server(sio)

            app = get_wsgi_application()
            app = SdMiddleware(sio, handler)
            eventlet.wsgi.server(eventlet.listen(bind), app)

        except KeyboardInterrupt:
            # eventlet server will handle exception
            # server.stop()
            # if RELOAD:
            #     print("Reloading...")
            #     restart_with_reloader()
            pass

    def get_handler(self, *args, **options):
        """
        Returns the django.contrib.staticfiles handler.
        """
        handler = WSGIHandler()
        try:
            from django.contrib.staticfiles.handlers import StaticFilesHandler
        except ImportError:
            return handler
        use_static_handler = options.get('use_static_handler', True)
        insecure_serving = options.get('insecure_serving', False)
        if (settings.DEBUG and use_static_handler or
                (use_static_handler and insecure_serving)):
            handler = StaticFilesHandler(handler)
        return handler
