from sanic import Sanic
from sanic.response import html

import socketio

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


@app.route('/')
def index(request):
    with open('latency.html') as f:
        return html(f.read())


@sio.on('ping_from_client')
async def ping(sid):
    await sio.emit('pong_from_server', room=sid)

app.static('/static', './static')


if __name__ == '__main__':
    app.run()
