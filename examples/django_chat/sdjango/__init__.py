import logging
import inspect

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.wsgi import get_wsgi_application

try:
    # Django version >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django version < 1.9
    from django.utils.importlib import import_module

from django.conf.urls import patterns, url, include


LOADING_SOCKETIO = False

def autodiscover():
    """
    Auto-discover INSTALLED_APPS sockets.py modules and fail silently when
    not present. NOTE: socketio_autodiscover was inspired/copied from
    django.contrib.admin autodiscover
    """
    global LOADING_SOCKETIO
    if LOADING_SOCKETIO:
        return
    LOADING_SOCKETIO = True

    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:

        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('sockets', app_path)
        except ImportError:
            continue

        import_module("%s.sockets" % app)

    LOADING_SOCKETIO = False


class namespace:

    """This is a event handler keeper for socketio event

    used as a decorators
    """

    handler_container = {}
    server = None

    def __init__(self, name=''):
        if not name.startswith('/'):
            self.name = '/'+name
        self.name = name

    def __call__(self, handler):
        instance = handler(self.name)

        if self.name not in namespace.handler_container:
            namespace.handler_container[self.name] = []

        methods = inspect.getmembers(instance, predicate=inspect.ismethod)

        namespace.handler_container[self.name].append(instance)

        for key, value in methods:
            if key.startswith('on_'):
                namespace.handler_container[self.name].append(value)

        return True

    @classmethod
    def insert_in_server(cls, server):
        """a special method to dynamic add event for socketio server
        """
        namespace.server = server

        for name, handlers in namespace.handler_container.items():

            instance = handlers.pop(0)
            instance.initialize()

            for obj in handlers:
                event_name = obj.__name__.replace('on_', '').replace('_', ' ')
                server.on(event_name, obj, name)

        namespace.handler_container = {} # reset to empty dict


@csrf_exempt
def socketio(request):
    try:
        request.environ['django_request'] = request
    except:
        logging.getLogger("socketio").error("Exception while handling socketio connection", exc_info=True)
    return HttpResponse(200)

urls = patterns("", (r'', socketio))
