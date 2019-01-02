The Socket.IO Server
====================

This package contains two Socket.IO clients:

- The :func:`socketio.Server` class creates a server compatible with the
  Python standard library.
- The :func:`socketio.AsyncServer` class creates a server compatible with
  the ``asyncio`` package.

The methods in the two clients are the same, with the only difference that in
the ``asyncio`` client most methods are implemented as coroutines.

Installation
------------

To install the Socket.IO server along with its dependencies, use the following
command::

    pip install python-socketio

In addition to the server, you will need to select an asynchronous framework
or server to use along with it. The list of supported packages is covered
in the :ref:`deployment-strategies` section.

Creating a Server Instance
--------------------------

A Socket.IO server is an instance of class :class:`socketio.Server`. This
instance can be transformed into a standard WSGI application by wrapping it
with the :class:`socketio.WSGIApp` class::

   import socketio

   # create a Socket.IO server
   sio = socketio.Server()

   # wrap with a WSGI application
   app = socketio.WSGIApp(sio)

For asyncio based servers, the :class:`socketio.AsyncServer` class provides
the same functionality, but in a coroutine friendly format. If desired, The
:class:`socketio.ASGIApp` class can transform the server into a standard
ASGI application::

    # create a Socket.IO server
    sio = socketio.AsyncServer()

    # wrap with ASGI application
    app = socketio.ASGIApp(sio)

The WSGI and ASGI application wrappers support serving static files, which is
a convenient way to deliver JavaScript based Socket.IO clients to the web
browser::

   app = socketio.ASGIApp(sio, static_files={
      '/': {'content_type': 'text/html', 'filename': 'latency.html'},
      '/static/style.css': {'content_type': 'text/css',
                            'filename': 'static/style.css'},
   })

The dictionary provided with the ``static_files`` argument has static file
endpoints as keys. For each of these endpoints, a dictionary with the file's
content type and local filename is given.

These wrappers can also act as middlewares, forwarding any traffic that is not
intended to Socket.IO server to another application. This allows Socket.IO
servers to integrate easily into existing WSGI or ASGI applications::

   from wsgi import app  # a Flask, Django, etc. application

   app = socketio.WSGIApp(sio, app)

Defining Event Handlers
-----------------------

The Socket.IO protocol is event based. When a client wants to communicate with
the server it *emits* an event. Each event has a name, and a list of
arguments. The server registers event handler functions with the
:func:`socketio.Server.on` decorator::

    @sio.on('my custom event')
    def my_custom_event(sid, data):
        pass

For asyncio servers, event handlers can optionally be given as coroutines::

    @sio.on('my custom event')
    async def my_custom_event(sid, data):
        pass

The ``sid`` argument is the Socket.IO session id, a unique identifier of each
client connection. All the events sent by a given client will have the same
``sid`` value.

The ``connect`` and ``disconnect`` are special; they are invoked automatically
when a client connects or disconnects from the server::

    @sio.on('connect')
    def connect(sid, environ):
        print('connect ', sid)

    @sio.on('disconnect')
    def disconnect(sid):
        print('disconnect ', sid)

The ``connect`` event is an ideal place to perform user authentication, and
any necessary mapping between user entities in the application and the ``sid``
that was assigned to the client. The ``environ`` argument is a dictionary in
standard WSGI format containing the request information, including HTTP
headers. After inspecting the request, the connect event handler can return
``False`` to reject the connection with the client.

Emitting Events
---------------

Socket.IO is a bidirectional protocol, so at any time the server can send an
event to its connected clients. The :func:`socketio.Server.emit` method is
used for this task::

   sio.emit('my event', {'data': 'foobar'})

Sometimes the server may want to send an event just to a particular client.
This can be achieved by adding a ``room`` argument to the emit call::

   sio.emit('my event', {'data': 'foobar'}, room=user_sid)

The :func:`socketio.Server.emit` method takes an event name, a message payload
of type ``str``, ``bytes``, ``list``, ``dict`` or ``tuple``, and the recipient
room. When sending a ``tuple``, the elements in it need to be of any of the
other four allowed types. The elements of the tuple will be passed as multiple
arguments to the client-side event handler function. The ``room`` argument is
used to identify the client that should receive the event, and is set to the
``sid`` value assigned to that client's connection with the server. When
omitted, the event is broadcasted to all connected clients.

Event Callbacks
---------------

When a client sends an event to the server, it can optionally provide a
callback function, to be invoked as a way of acknowledgment that the server
has processed the event. While this is entirely managed by the client, the
server can provide a list of values that are to be passed on to the callback
function, simply by returning them from the handler function::

    @sio.on('my event', namespace='/chat')
    def my_event_handler(sid, data):
        # handle the message
        return "OK", 123

Likewise, the server can request a callback function to be invoked after a
client has processed an event. The :func:`socketio.Server.emit` method has an
optional ``callback`` argument that can be set to a callable. If this
argument is given, the callable will be invoked after the client has processed
the event, and any values returned by the client will be passed as arguments
to this function. Using callback functions when broadcasting to multiple
clients is not recommended, as the callback function will be invoked once for
each client that received the message.

Namespaces
----------

The Socket.IO protocol supports multiple logical connections, all multiplexed
on the same physical connection. Clients can open multiple connections by
specifying a different *namespace* on each. A namespace is given by the client
as a pathname following the hostname and port. For example, connecting to
*http://example.com:8000/chat* would open a connection to the namespace
*/chat*.

Each namespace is handled independently from the others, with separate session
IDs (``sid``\ s), event handlers and rooms. It is important that applications
that use multiple namespaces specify the correct namespace when setting up
their event handlers and rooms, using the optional ``namespace`` argument
available in all the methods in the :class:`socketio.Server` class::

    @sio.on('my custom event', namespace='/chat')
    def my_custom_event(sid, data):
        pass

When emitting an event, the ``namespace`` optional argument is used to specify
which namespace to send it on. When the ``namespace`` argument is omitted, the
default Socket.IO namespace, which is named ``/``, is used.

Class-Based Namespaces
----------------------

As an alternative to the decorator-based event handlers, the event handlers
that belong to a namespace can be created as methods of a subclass of 
:class:`socketio.Namespace`::

    class MyCustomNamespace(socketio.Namespace):
        def on_connect(self, sid, environ):
            pass

        def on_disconnect(self, sid):
            pass

        def on_my_event(self, sid, data):
            self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/test'))

For asyncio based severs, namespaces must inherit from
:class:`socketio.AsyncNamespace`, and can define event handlers as coroutines
if desired::

    class MyCustomNamespace(socketio.AsyncNamespace):
        def on_connect(self, sid, environ):
            pass

        def on_disconnect(self, sid):
            pass

        async def on_my_event(self, sid, data):
            await self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/test'))

When class-based namespaces are used, any events received by the server are
dispatched to a method named as the event name with the ``on_`` prefix. For
example, event ``my_event`` will be handled by a method named ``on_my_event``.
If an event is received for which there is no corresponding method defined in
the namespace class, then the event is ignored. All event names used in
class-based namespaces must use characters that are legal in method names.

As a convenience to methods defined in a class-based namespace, the namespace
instance includes versions of several of the methods in the 
:class:`socketio.Server` and :class:`socketio.AsyncServer` classes that default
to the proper namespace when the ``namespace`` argument is not given.

In the case that an event has a handler in a class-based namespace, and also a
decorator-based function handler, only the standalone function handler is
invoked.

It is important to note that class-based namespaces are singletons. This means
that a single instance of a namespace class is used for all clients, and
consequently, a namespace instance cannot be used to store client specific
information.

Rooms
-----

To make it easy for the server to emit events to groups of related clients,
the application can put its clients into "rooms", and then address messages to
these rooms.

In the previous section the ``room`` argument of the
:func:`socketio.SocketIO.emit` method was used to designate a specific
client as the recipient of the event. This is because upon connection, a
personal room for each client is created and named with the ``sid`` assigned
to the connection. The application is then free to create additional rooms and
manage which clients are in them using the :func:`socketio.Server.enter_room`
and :func:`socketio.Server.leave_room` methods. Clients can be in as many
rooms as needed and can be moved between rooms as often as necessary. 

::

   @sio.on('chat')
   def begin_chat(sid):
      sio.enter_room(sid, 'chat_users')

    @sio.on('exit_chat')
    def exit_chat(sid):
        sio.leave_room(sid, 'chat_users')

In chat applications it is often desired that an event is broadcasted to all
the members of the room except one, which is the originator of the event such
as a chat message. The :func:`socketio.Server.emit` method provides an
optional ``skip_sid`` argument to indicate a client that should be skipped
during the broadcast.

::

    @sio.on('my message')
    def message(sid, data):
        sio.emit('my reply', data, room='chat_users', skip_sid=sid)

User Sessions
-------------

The server can maintain application-specific information in a user session
dedicated to each connected client. Applications can use the user session to
write any details about the user that need to be preserved throughout the life
of the connection, such as usernames or user ids.

The ``save_session()`` and ``get_session()`` methods are used to store and
retrieve information in the user session::

    @sio.on('connect')
    def on_connect(sid, environ):
        username = authenticate_user(environ)
        sio.save_session(sid, {'username': username})

    @sio.on('message')
    def on_message(sid, data):
        session = sio.get_session(sid)
        print('message from ', session['username'])

For the ``asyncio`` server, these methods are coroutines::


    @sio.on('connect')
    async def on_connect(sid, environ):
        username = authenticate_user(environ)
        await sio.save_session(sid, {'username': username})

    @sio.on('message')
    async def on_message(sid, data):
        session = await sio.get_session(sid)
        print('message from ', session['username'])

The session can also be manipulated with the `session()` context manager::

    @sio.on('connect')
    def on_connect(sid, environ):
        username = authenticate_user(environ)
        with sio.session(sid) as session:
            session['username'] = username

    @sio.on('message')
    def on_message(sid, data):
        with sio.session(sid) as session:
            print('message from ', session['username'])

For the ``asyncio`` server, an asynchronous context manager is used::

    @sio.on('connect')
    def on_connect(sid, environ):
        username = authenticate_user(environ)
        async with sio.session(sid) as session:
            session['username'] = username

    @sio.on('message')
    def on_message(sid, data):
        async with sio.session(sid) as session:
            print('message from ', session['username'])

The ``get_session()``, ``save_session()`` and ``session()`` methods take an
optional ``namespace`` argument. If this argument isn't provided, the session
is attached to the default namespace.

Using a Message Queue
---------------------

When working with distributed applications, it is often necessary to access
the functionality of the Socket.IO from multiple processes. There are two
specific use cases:

- Applications that use a work queues such as
  `Celery <http://www.celeryproject.org/>`_ may need to emit an event to a
  client once a background job completes. The most convenient place to carry
  out this task is the worker process that handled this job.

- Highly available applications may want to use horizontal scaling of the
  Socket.IO server to be able to handle very large number of concurrent
  clients.

As a solution to the above problems, the Socket.IO server can be configured
to connect to a message queue such as `Redis <http://redis.io/>`_ or
`RabbitMQ <https://www.rabbitmq.com/>`_, to communicate with other related
Socket.IO servers or auxiliary workers.

Redis
~~~~~

To use a Redis message queue, a Python Redis client must be installed::

    # socketio.Server class
    pip install redis

    # socketio.AsyncServer class
    pip install aioredis

The Redis queue is configured through the :class:`socketio.RedisManager` and 
:class:`socketio.AsyncRedisManager` classes. These classes connect directly to
the Redis store and use the queue's pub/sub functionality::

    # socketio.Server class
    mgr = socketio.RedisManager('redis://')
    sio = socketio.Server(client_manager=mgr)

    # socketio.AsyncServer class
    mgr = socketio.AsyncRedisManager('redis://')
    sio = socketio.AsyncServer(client_manager=mgr)

The ``client_manager`` argument instructs the server to connect to the given
message queue, and to coordinate with other processes connected to the queue.

Kombu
~~~~~

`Kombu <http://kombu.readthedocs.org/en/latest/>`_ is a Python package that
provides access to RabbitMQ and many other message queues. It can be installed
with pip::

    pip install kombu

To use RabbitMQ or other AMQP protocol compatible queues, that is the only
required dependency. But for other message queues, Kombu may require
additional packages. For example, to use a Redis queue via Kombu, the Python
package for Redis needs to be installed as well::

    pip install redis

The queue is configured through the :class:`socketio.KombuManager`::

    mgr = socketio.KombuManager('amqp://')
    sio = socketio.Server(client_manager=mgr)

The connection URL passed to the :class:`KombuManager` constructor is passed
directly to Kombu's `Connection object
<http://kombu.readthedocs.org/en/latest/userguide/connections.html>`_, so
the Kombu documentation should be consulted for information on how to build
the correct URL for a given message queue.

Note that Kombu currently does not support asyncio, so it cannot be used with
the :class:`socketio.AsyncServer` class.

Emitting from external processes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To have a process other than a server connect to the queue to emit a message,
the same client manager classes can be used as standalone objects. In this
case, the ``write_only`` argument should be set to ``True`` to disable the
creation of a listening thread, which only makes sense in a server. For
example::

    # connect to the redis queue as an external process
    external_sio = socketio.RedisManager('redis://', write_only=True)
    
    # emit an event
    external_sio.emit('my event', data={'foo': 'bar'}, room='my room')

.. _deployment-strategies:

Deployment Strategies
---------------------

The following sections describe a variety of deployment strategies for
Socket.IO servers.

Aiohttp
~~~~~~~

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
~~~~~~~

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
~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``socketio.ASGIApp`` class is an ASGI compatible application that can
forward Socket.IO traffic to an ``socketio.AsyncServer`` instance::

   sio = socketio.AsyncServer(async_mode='asgi')
   app = socketio.ASGIApp(sio)

The application can then be deployed with any ASGI compatible web server.

Eventlet
~~~~~~~~

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

Eventlet with Gunicorn
~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~

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

Gevent with Gunicorn
~~~~~~~~~~~~~~~~~~~~

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
~~~~~

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
~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~

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
