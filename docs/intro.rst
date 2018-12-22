.. socketio documentation master file, created by
   sphinx-quickstart on Sat Jun 13 23:41:23 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
===============

What is Socket.IO?
------------------

Socket.IO is a transport protocol that enables real-time bidirectional
event-based communication between clients (typically, though not always,
web browsers) and a server. The official implementations of the client
and server components are written in JavaScript. This package provides
Python implementations of both, each with standard and asyncio variants.

Client Examples
---------------

The example that follows shows a simple Python client:

.. code:: python

    import socketio

    sio = socketio.Client()

    @sio.on('connect')
    def on_connect():
        print('connection established')

    @sio.on('my message')
    def on_message(data):
        print('message received with ', data)
        sio.emit('my response', {'response': 'my response'})

    @sio.on('disconnect')
    def on_disconnect():
        print('disconnected from server')

    sio.connect('http://localhost:5000')
    sio.wait()

Client Features
---------------

- Can connect to other Socket.IO complaint servers besides the one in
  this package.
- Compatible with Python 2.7 and 3.5+.
- Two versions of the client, one for standard Python and another for
  asyncio.
- Uses an event-based architecture implemented with decorators that
  hides the details of the protocol.
- Implements HTTP long-polling and WebSocket transports.
- Automatically reconnects to the server if the connection is dropped.

Server Examples
---------------

The following application is a basic server example that uses the Eventlet
asynchronous server:

.. code:: python

    import engineio
    import eventlet

    sio = socketio.Server()
    app = socketio.WSGIApp(eio, static_files={
        '/': {'content_type': 'text/html', 'filename': 'index.html'}
    })

    @sio.on('connect')
    def connect(sid, environ):
        print('connect ', sid)

    @sio.on('my message')
    def message(sid, data):
        print('message ', data)

    @sio.on('disconnect')
    def disconnect(sid):
        print('disconnect ', sid)

    if __name__ == '__main__':
        eventlet.wsgi.server(eventlet.listen(('', 5000)), app)

Below is a similar application, coded for ``asyncio`` (Python 3.5+ only) and the
Uvicorn web server:

.. code:: python

    from aiohttp import web
    import socketio

    sio = socketio.AsyncServer()
    app = web.Application()
    sio.attach(app)

    async def index(request):
        """Serve the client-side application."""
        with open('index.html') as f:
            return web.Response(text=f.read(), content_type='text/html')

    @sio.on('connect', namespace='/chat')
    def connect(sid, environ):
        print("connect ", sid)

    @sio.on('chat message', namespace='/chat')
    async def message(sid, data):
        print("message ", data)
        await sio.emit('reply', room=sid)

    @sio.on('disconnect', namespace='/chat')
    def disconnect(sid):
        print('disconnect ', sid)

    app.router.add_static('/static', 'static')
    app.router.add_get('/', index)

    if __name__ == '__main__':
        web.run_app(app)

Server Features
---------------

- Can connect to servers running other complaint Socket.IO clients besides
  the one in this package.
- Compatible with Python 2.7 and Python 3.5+.
- Two versions of the server, one for standard Python and another for
  asyncio.
- Supports large number of clients even on modest hardware due to being
  asynchronous.
- Can be hosted on any `WSGI <https://wsgi.readthedocs.io/en/latest/index.html>`_ and
  `ASGI <https://asgi.readthedocs.io/en/latest/>`_ web servers includind
  `Gunicorn <https://gunicorn.org/>`_, `Uvicorn <https://github.com/encode/uvicorn>`_,
  `eventlet <http://eventlet.net/>`_ and `gevent <http://gevent.org>`_.
- Can be integrated with WSGI applications written in frameworks such as Flask, Django,
  etc.
- Can be integrated with `aiohttp <http://aiohttp.readthedocs.io/>`_,
  `sanic <http://sanic.readthedocs.io/>`_ and `tornado <http://www.tornadoweb.org/>`_
  ``asyncio`` applications.
- Broadcasting of messages to all connected clients, or to subsets of them
  assigned to "rooms".
- Optional support for multiple servers, connected through a messaging queue
  such as Redis or RabbitMQ.
- Send messages to clients from external processes, such as Celery workers or
  auxiliary scripts.
- Event-based architecture implemented with decorators that hides the details
  of the protocol.
- Support for HTTP long-polling and WebSocket transports.
- Support for XHR2 and XHR browsers.
- Support for text and binary messages.
- Support for gzip and deflate HTTP compression.
- Configurable CORS responses, to avoid cross-origin problems with browsers.
