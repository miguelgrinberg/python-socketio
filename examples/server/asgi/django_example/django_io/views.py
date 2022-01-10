from django.shortcuts import render
import json
import os
from .models import Message
from .serializers import message_serializer
from asgiref.sync import sync_to_async
import socketio
from dotenv import load_dotenv
load_dotenv()

mgr = socketio.AsyncRedisManager(os.getenv('REDIS_URL'))
sio = socketio.AsyncServer(async_mode="asgi", client_manager=mgr, cors_allowed_origins="*")
# Create your views here.

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
@sio.on('mess')
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
