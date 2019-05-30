#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
    '/': 'latency.html',
    '/static': 'static',
})


@sio.on('ping_from_client')
async def ping(sid):
    await sio.emit('pong_from_server', room=sid)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
