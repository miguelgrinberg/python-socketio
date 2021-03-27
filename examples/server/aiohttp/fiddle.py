from aiohttp import web

import socketio

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)


async def index(request):
    with open('fiddle.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


@sio.event
async def connect(sid, environ, auth):
    print(f'connected auth={auth} sid={sid}')
    await sio.emit('hello', (1, 2, {'hello': 'you'}), to=sid)


@sio.event
def disconnect(sid):
    print('disconnected', sid)


app.router.add_static('/static', 'static')
app.router.add_get('/', index)


if __name__ == '__main__':
    web.run_app(app)
