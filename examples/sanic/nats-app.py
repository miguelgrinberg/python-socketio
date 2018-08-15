import asyncio

from sanic import Sanic
from sanic.response import html

import socketio

# --- NATS PubSub Manager ---

import nats
from nats.aio.client import Client as NATS
from socketio.asyncio_pubsub_manager import AsyncPubSubManager

import json

class AsyncNatsManager(AsyncPubSubManager):
    name = 'asyncionats'

    def __init__(self,
                 servers=None,
                 channel='socketio',
                 write_only=False,
                 loop=asyncio.get_event_loop(),
                 ):

        if servers is None:
            servers = ["nats://127.0.0.1:4222"]
        self.servers = servers
        self.queue = asyncio.Queue()

        # Establish single connection to NATS for the client.
        self.nc = None
        super().__init__(channel=channel, write_only=write_only)

    async def _publish(self, data):
        print("Socket.io <<- NATS     :", data)

        # Send the client events through NATS
        if self.nc is None:
            self.nc = NATS()
            await self.nc.connect(servers=self.servers)

        # Skip broadcasted messages that were received from NATS.
        if data['event'] != 'event':
            payload = json.dumps(data['data']).encode()
            await self.nc.publish("socketio.{}".format(data['event']), payload)

    async def _listen(self):
        if self.nc is None:
            self.nc = NATS()
            await self.nc.connect(servers=self.servers)

            # Close over the socketio to be able to emit within
            # the NATS callback.
            sio = self
            async def message_handler(msg):
                nonlocal sio

                print("NATS      ->> Socket.io:", msg.data.decode())

                data = json.loads(msg.data.decode())

                # Broadcast the bare message received via NATS as a Socket.io event
                await sio.emit('nats', data, namespace='/test')

                await self.queue.put(data)
            await self.nc.subscribe(self.channel, cb=message_handler)
        return await self.queue.get()

# --- Sanic + Socket.io based Application with attached PubSub Manager ---

app = Sanic()
mgr = AsyncNatsManager()
sio = socketio.AsyncServer(client_manager=mgr, async_mode='sanic')
sio.attach(app)

@app.route('/')
async def index(request):
    with open('nats.html') as f:
        return html(f.read())

@sio.on('event', namespace='/test')
async def test_message(sid, message):
    await sio.emit('response', {'data': message['data']}, room=sid,
                   namespace='/test')

@sio.on('nats', namespace='/test')
async def test_nats_message(sid, message):
    await sio.emit('response', {'data': message['data']}, room=sid,
                   namespace='/test')

@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    print("Client connected", sid)
    await sio.emit('response', {'data': 'Connected', 'count': 0}, room=sid,
                   namespace='/test')

@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')

if __name__ == '__main__':
    app.run()
