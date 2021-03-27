#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
    '/': 'fiddle.html',
    '/static': 'static',
})


@sio.event
async def connect(sid, environ, auth):
    print(f'connected auth={auth} sid={sid}')
    await sio.emit('hello', (1, 2, {'hello': 'you'}), to=sid)


@sio.event
def disconnect(sid):
    print('disconnected', sid)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
