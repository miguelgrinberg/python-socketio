#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: xuyaoqiang
@contact: xuyaoqiang@gmail.com
@date: 2017-07-28 15:29
@version: 0.0.0
@license:
@copyright:

"""

from sanic import Sanic
from sanic.response import html 
import socketio


sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


class TestNamespace(socketio.AsyncNamespace):

    def on_connect(self, sid, environ):
        pass

    def on_disconnect(self, sid):
        pass


@app.route('/')
async def index(request):
    with open('index.html') as f:
        return html(f.read())


sio.register_namespace(TestNamespace('/test'))


if __name__ == '__main__':
    app.run(port=8001, debug=True)

