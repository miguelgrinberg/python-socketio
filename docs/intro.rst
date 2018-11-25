.. socketio documentation master file, created by
   sphinx-quickstart on Sat Jun 13 23:41:23 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting Started
===============

What is Socket.IO?
------------------

Socket.IO is a transport protocol that enables real-time bidirectional
event-based communication between clients (typically web browsers or
smartphones) and a server. There are Socket.IO clients and servers implemented
in a variety of languages, including JavaScript, Python, C++, Swift, C# and
PHP.

Features
--------

- Fully compatible with the 
  `Javascript <https://github.com/Automattic/socket.io-client>`_,
  `Swift <https://github.com/socketio/socket.io-client-swift>`_,
  `C++ <https://github.com/socketio/socket.io-client-cpp>`_ and
  `Java <https://github.com/socketio/socket.io-client-java>`_ official
  Socket.IO clients, plus any third party clients that comply with the
  Socket.IO specification.
- Compatible with Python 2.7 and Python 3.3+.
- Supports large number of clients even on modest hardware due to being
  asynchronous, even when asyncio is not used.
- Compatible with `aiohttp <http://aiohttp.readthedocs.io/>`_,
  `sanic <http://sanic.readthedocs.io/>`_,
  `tornado <http://www.tornadoweb.org/>`_,
  `eventlet <http://eventlet.net/>`_,
  `gevent <http://gevent.org>`_,
  or any `WSGI <https://wsgi.readthedocs.io/en/latest/index.html>`_ or
  `ASGI <https://asgi.readthedocs.io/en/latest/>`_ compatible server.
- Includes WSGI and ASGI middlewares that integrate Socket.IO traffic with
  other web applications.
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

Examples
--------

The Socket.IO server can be installed with pip::

    pip install python-socketio

The following is a basic example of a Socket.IO server that uses the
`aiohttp <http://aiohttp.readthedocs.io/>`_ framework for asyncio (Python 3.5+
only):

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

And below is a similar example, but using Flask and Eventlet. This example is
compatible with Python 2.7 and 3.3+::

    import socketio
    import eventlet
    from flask import Flask, render_template

    sio = socketio.Server()
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Serve the client-side application."""
        return render_template('index.html')

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
        # wrap Flask application with socketio's middleware
        app = socketio.WSGIApp(sio, app)

        # deploy as an eventlet WSGI server
        eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

The client-side application must include the
`socket.io-client <https://github.com/Automattic/socket.io-client>`_ library
(versions 1.3.5 or newer recommended).

Each time a client connects to the server the ``connect`` event handler is
invoked with the ``sid`` (session ID) assigned to the connection and the WSGI
environment dictionary. The server can inspect authentication or other headers
to decide if the client is allowed to connect. To reject a client the handler
must return ``False``.

When the client sends an event to the server, the appropriate event handler is
invoked with the ``sid`` and the message, which can be a single or multiple
arguments. The application can define as many events as needed and associate
them with event handlers. An event is defined simply by a name.

When a connection with a client is broken, the ``disconnect`` event is called,
allowing the application to perform cleanup.
