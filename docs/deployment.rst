Deployment
==========

The following sections describe a variety of deployment strategies for
Socket.IO servers.

aiohttp
-------

`Aiohttp <http://aiohttp.readthedocs.io/>`_ is a framework with support for HTTP
and WebSocket, based on asyncio. Support for this framework is limited to Python
3.5 and newer.

Instances of class ``socketio.AsyncServer`` will automatically use aiohttp
for asynchronous operations if the library is installed. To request its use
explicitly, the ``async_mode`` option can be given in the constructor::

    sio = socketio.AsyncServer(async_mode='aiohttp')

A server configured for aiohttp must be attached to an existing application::

    app = web.Application()
    sio.attach(app)

The aiohttp application can define regular routes that will coexist with the
Socket.IO server. A typical pattern is to add routes that serve a client
application and any associated static files.

The aiohttp application is then executed in the usual manner::

    if __name__ == '__main__':
        web.run_app(app)

Tornado
-------

`Tornado <http://www.tornadoweb.org//>`_ is a web framework with support
for HTTP and WebSocket. Support for this framework requires Python 3.5 and
newer. Only Tornado version 5 and newer are supported, thanks to its tight
integration with asyncio.

Instances of class ``socketio.AsyncServer`` will automatically use tornado
for asynchronous operations if the library is installed. To request its use
explicitly, the ``async_mode`` option can be given in the constructor::

    sio = socketio.AsyncServer(async_mode='tornado')

A server configured for tornado must include a request handler for
Engine.IO::

    app = tornado.web.Application(
        [
            (r"/socketio.io/", socketio.get_tornado_handler(sio)),
        ],
        # ... other application options
    )

The tornado application can define other routes that will coexist with the
Socket.IO server. A typical pattern is to add routes that serve a client
application and any associated static files.

The tornado application is then executed in the usual manner::

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

Sanic
-----

`Sanic <http://sanic.readthedocs.io/>`_ is a very efficient asynchronous web
server for Python 3.5 and newer.

Instances of class ``socketio.AsyncServer`` will automatically use Sanic for
asynchronous operations if the framework is installed. To request its use
explicitly, the ``async_mode`` option can be given in the constructor::

    sio = socketio.AsyncServer(async_mode='sanic')

A server configured for aiohttp must be attached to an existing application::

    app = web.Application()
    sio.attach(app)

The Sanic application can define regular routes that will coexist with the
Socket.IO server. A typical pattern is to add routes that serve a client
application and any associated static files.

The Sanic application is then executed in the usual manner::

    if __name__ == '__main__':
        app.run()

Uvicorn, Daphne, and other ASGI servers
---------------------------------------

The ``socketio.ASGIApp`` class is an ASGI compatible application that can
forward Socket.IO traffic to an ``socketio.AsyncServer`` instance::

   sio = socketio.AsyncServer(async_mode='asgi')
   app = socketio.ASGIApp(sio)

The application can then be deployed with any ASGI compatible web server.

Eventlet
--------

`Eventlet <http://eventlet.net/>`_ is a high performance concurrent networking
library for Python 2 and 3 that uses coroutines, enabling code to be written in
the same style used with the blocking standard library functions. An Socket.IO
server deployed with eventlet has access to the long-polling and WebSocket
transports.

Instances of class ``socketio.Server`` will automatically use eventlet for
asynchronous operations if the library is installed. To request its use
explicitly, the ``async_mode`` option can be given in the constructor::

    sio = socketio.Server(async_mode='eventlet')

A server configured for eventlet is deployed as a regular WSGI application,
using the provided ``socketio.Middleware``::

    app = socketio.Middleware(sio)
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

Using Gunicorn with Eventlet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative to running the eventlet WSGI server as above is to use
`gunicorn <gunicorn.org>`_, a fully featured pure Python web server. The
command to launch the application under gunicorn is shown below::

    $ gunicorn -k eventlet -w 1 module:app

Due to limitations in its load balancing algorithm, gunicorn can only be used
with one worker process, so the ``-w`` option cannot be set to a value higher
than 1. A single eventlet worker can handle a large number of concurrent
clients, each handled by a greenlet.

Eventlet provides a ``monkey_patch()`` function that replaces all the blocking
functions in the standard library with equivalent asynchronous versions. While
python-socketio does not require monkey patching, other libraries such as
database drivers are likely to require it.

Gevent
------

`Gevent <http://gevent.org/>`_ is another asynchronous framework based on
coroutines, very similar to eventlet. An Socket.IO server deployed with
gevent has access to the long-polling transport. If project
`gevent-websocket <https://bitbucket.org/Jeffrey/gevent-websocket/>`_ is
installed, the WebSocket transport is also available.

Instances of class ``socketio.Server`` will automatically use gevent for
asynchronous operations if the library is installed and eventlet is not
installed. To request gevent to be selected explicitly, the ``async_mode``
option can be given in the constructor::

    sio = socketio.Server(async_mode='gevent')

A server configured for gevent is deployed as a regular WSGI application,
using the provided ``socketio.Middleware``::

    app = socketio.Middleware(sio)
    from gevent import pywsgi
    pywsgi.WSGIServer(('', 8000), app).serve_forever()

If the WebSocket transport is installed, then the server must be started as
follows::

    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    app = socketio.Middleware(sio)
    pywsgi.WSGIServer(('', 8000), app,
                      handler_class=WebSocketHandler).serve_forever()

Using Gunicorn with Gevent
~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative to running the gevent WSGI server as above is to use
`gunicorn <gunicorn.org>`_, a fully featured pure Python web server. The
command to launch the application under gunicorn is shown below::

    $ gunicorn -k gevent -w 1 module:app

Or to include WebSocket::

    $ gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 module: app

Same as with eventlet, due to limitations in its load balancing algorithm,
gunicorn can only be used with one worker process, so the ``-w`` option cannot
be higher than 1. A single gevent worker can handle a large number of
concurrent clients through the use of greenlets.

Gevent provides a ``monkey_patch()`` function that replaces all the blocking
functions in the standard library with equivalent asynchronous versions. While
python-socketio does not require monkey patching, other libraries such as
database drivers are likely to require it.

uWSGI
-----

When using the uWSGI server in combination with gevent, the Socket.IO server
can take advantage of uWSGI's native WebSocket support.

Instances of class ``socketio.Server`` will automatically use this option for
asynchronous operations if both gevent and uWSGI are installed and eventlet is
not installed. To request this asynchronous mode explicitly, the
``async_mode`` option can be given in the constructor::

    # gevent with uWSGI
    sio = socketio.Server(async_mode='gevent_uwsgi')

A complete explanation of the configuration and usage of the uWSGI server is
beyond the scope of this documentation. The uWSGI server is a fairly complex
package that provides a large and comprehensive set of options. It must be
compiled with WebSocket and SSL support for the WebSocket transport to be
available. As way of an introduction, the following command starts a uWSGI
server for the ``latency.py`` example on port 5000::

    $ uwsgi --http :5000 --gevent 1000 --http-websockets --master --wsgi-file latency.py --callable app

Standard Threads
----------------

While not comparable to eventlet and gevent in terms of performance,
the Socket.IO server can also be configured to work with multi-threaded web
servers that use standard Python threads. This is an ideal setup to use with
development servers such as `Werkzeug <http://werkzeug.pocoo.org>`_. Only the
long-polling transport is currently available when using standard threads.

Instances of class ``socketio.Server`` will automatically use the threading
mode if neither eventlet nor gevent are not installed. To request the
threading mode explicitly, the ``async_mode`` option can be given in the
constructor::

    sio = socketio.Server(async_mode='threading')

A server configured for threading is deployed as a regular web application,
using any WSGI complaint multi-threaded server. The example below deploys an
Socket.IO application combined with a Flask web application, using Flask's
development web server based on Werkzeug::

    sio = socketio.Server(async_mode='threading')
    app = Flask(__name__)
    app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)

    # ... Socket.IO and Flask handler functions ...

    if __name__ == '__main__':
        app.run(threaded=True)

When using the threading mode, it is important to ensure that the WSGI server
can handle multiple concurrent requests using threads, since a client can have
up to two outstanding requests at any given time. The Werkzeug server is
single-threaded by default, so the ``threaded=True`` option is required.

Note that servers that use worker processes instead of threads, such as
gunicorn, do not support a Socket.IO server configured in threading mode.

Scalability Notes
-----------------

Socket.IO is a stateful protocol, which makes horizontal scaling more
difficult. To deploy a cluster of Socket.IO processes hosted on one or
multiple servers, the following conditions must be met:

- Each Socket.IO process must be able to handle multiple requests
  concurrently. This is required because long-polling clients send two
  requests in parallel. Worker processes that can only handle one request at a
  time are not supported.
- The load balancer must be configured to always forward requests from a
  client to the same worker process. Load balancers call this *sticky
  sessions*, or *session affinity*.
- The worker processes need to communicate with each other to coordinate
  complex operations such as broadcasts. This is done through a configured
  message queue. See the section on using message queues for details.
