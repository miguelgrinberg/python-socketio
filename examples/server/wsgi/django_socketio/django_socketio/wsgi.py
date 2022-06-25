"""
WSGI config for django_socketio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import socketio

from socketio_app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_socketio.settings')

django_app = get_wsgi_application()
application = socketio.WSGIApp(sio, django_app)
