#!/usr/bin/env python
import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
    '/': 'latency.html',
    '/static': 'static',
})


@sio.event
async def ping_from_client(sid):
    await sio.emit('pong_from_server', room=sid)


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
