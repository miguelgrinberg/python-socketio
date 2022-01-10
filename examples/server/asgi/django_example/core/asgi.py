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
from django_io.models import Message
from django_io.serializers import message_serializer
from django_io.utils import generate_short_id
from socketio.exceptions import ConnectionRefusedError
from datetime import datetime, timezone
from asgiref.sync import sync_to_async
import json
from dotenv import load_dotenv
load_dotenv()

mgr = socketio.AsyncRedisManager(os.getenv('REDIS_URL'))
sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
application = socketio.ASGIApp(sio, django_asgi_app)

# application = get_asgi_application()


#establishes a connection with the client
@sio.on("connect")
async def connect(sid, env, auth):
    if auth:
        print("SocketIO connect")
        sio.enter_room(sid, "feed")
        await sio.emit("connect", f"Connected as {sid}")

#communication with orm 
def store_and_return_message(data):
    data = json.loads(data)
    instance = Message.objects.create(
        author = data["username"],
        message = data["message"]
    )
    instance.save()
    message = message_serializer(instance)
    return message



# listening to a 'message' event from the client
@sio.on('message')
async def print_message(sid, data):
    print("Socket ID", sid)
    message = await sync_to_async(store_and_return_message, thread_sensitive=True)(data) #communicating with orm
    print(message)
    await sio.emit("new_message", message, room="feed")



@sio.on("disconnect")
async def disconnect(sid):
    print("SocketIO disconnect")


#extra events
@sio.on('left')
async def left_room(sid, data):
    sio.leave_room(sid, "feed") 
    await sio.emit("user_left", f'{data} left', room="feed")
    print(f'{sid} Left')

@sio.on("joined")
async def joined(sid, data):
    await sio.emit("user_joined", f'{data} connected', room="feed")
    print(f'{data} connected')

