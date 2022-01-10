"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django_asgi_app = get_asgi_application()


#its important to make all other imports below this comment
import socketio
from django_io.views import sio
from dotenv import load_dotenv
load_dotenv()



application = socketio.ASGIApp(sio, django_asgi_app)





