import asyncio

import uvicorn
from uvicorn.loops.auto import auto_loop_setup

import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'app.html'},
})


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('my response', {'data': 'Server generated event'},
                       namespace='/test')


@sio.on('my event', namespace='/test')
async def test_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, room=sid,
                   namespace='/test')


@sio.on('my broadcast event', namespace='/test')
async def test_broadcast_message(sid, message):
    await sio.emit('my response', {'data': message['data']}, namespace='/test')


@sio.on('join', namespace='/test')
async def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Entered room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('leave', namespace='/test')
async def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/test')
    await sio.emit('my response', {'data': 'Left room: ' + message['room']},
                   room=sid, namespace='/test')


@sio.on('close room', namespace='/test')
async def close(sid, message):
    await sio.emit('my response',
                   {'data': 'Room ' + message['room'] + ' is closing.'},
                   room=message['room'], namespace='/test')
    await sio.close_room(message['room'], namespace='/test')


@sio.on('my room event', namespace='/test')
async def send_room_message(sid, message):
    await sio.emit('my response', {'data': message['data']},
                   room=message['room'], namespace='/test')


@sio.on('disconnect request', namespace='/test')
async def disconnect_request(sid):
    await sio.disconnect(sid, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(sid, environ):
    await sio.emit('my response', {'data': 'Connected', 'count': 0}, room=sid,
                   namespace='/test')


@sio.on('disconnect', namespace='/test')
def test_disconnect(sid):
    print('Client disconnected')


if __name__ == '__main__':
    loop = auto_loop_setup()
    sio.start_background_task(background_task)
    uvicorn.run(app, '127.0.0.1', 5000, loop=loop)
