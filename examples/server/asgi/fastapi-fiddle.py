#!/usr/bin/env python
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import socketio
import uvicorn

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')

sio = socketio.AsyncServer(async_mode='asgi')
combined_asgi_app = socketio.ASGIApp(sio, app)


@app.get('/')
async def index():
    return FileResponse('fiddle.html')


@app.get('/hello')
async def hello():
    return {'message': 'Hello, World!'}


@sio.event
async def connect(sid, environ, auth):
    print(f'connected auth={auth} sid={sid}')
    await sio.emit('hello', (1, 2, {'hello': 'you'}), to=sid)


@sio.event
def disconnect(sid):
    print('disconnected', sid)


if __name__ == '__main__':
    uvicorn.run(combined_asgi_app, host='127.0.0.1', port=5000)
