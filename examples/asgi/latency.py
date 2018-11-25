import uvicorn

import socketio

sio = socketio.AsyncServer(async_mode='asgi')
app = socketio.ASGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'latency.html'},
    '/static/style.css': {'content_type': 'text/css',
                          'filename': 'static/style.css'},
})


@sio.on('ping_from_client')
async def ping(sid):
    await sio.emit('pong_from_server', room=sid)


if __name__ == '__main__':
    uvicorn.run(app, '127.0.0.1', 5000)
