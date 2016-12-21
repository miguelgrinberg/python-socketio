.. socketio documentation master file, created by
   sphinx-quickstart on Sat Jun 13 23:41:23 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

socketio documentation
======================

:ref:`genindex` | :ref:`modindex` | :ref:`search`

This project implements a Socket.IO server that can run standalone or
integrated with a Python WSGI application. The following are some of its
features:

- Fully compatible with the 
  `Javascript <https://github.com/Automattic/socket.io-client>`_,
  `Swift <https://github.com/socketio/socket.io-client-swift>`_,
  `C++ <https://github.com/socketio/socket.io-client-cpp>`_ and
  `Java <https://github.com/socketio/socket.io-client-java>`_ official
  Socket.IO clients, plus any third party clients that comply with the
  Socket.IO specification.
- Compatible with Python 2.7 and Python 3.3+.
- Supports large number of clients even on modest hardware when used with an
  asynchronous server based on `eventlet <http://eventlet.net/>`_ or
  `gevent <http://gevent.org/>`_. For development and testing, any WSGI
  complaint multi-threaded server can be used.
- Includes a WSGI middleware that integrates Socket.IO traffic with standard
  WSGI applications.
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

What is Socket.IO?
------------------

Socket.IO is a transport protocol that enables real-time bidirectional
event-based communication between clients (typically web browsers) and a
server. The original implementations of the client and server components are
written in JavaScript.

Getting Started
---------------

The Socket.IO server can be installed with pip::

    pip install python-socketio

The following is a basic example of a Socket.IO server that uses Flask to
deploy the client code to the browser::

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
        app = socketio.Middleware(sio, app)

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

Rooms
-----

Because Socket.IO is a bidirectional protocol, the server can send messages to
any connected client at any time. To make it easy to address groups of clients,
the application can put clients into rooms, and then address messages to the
entire room.

When clients first connect, they are assigned to their own rooms, named with
the session ID (the ``sid`` argument passed to all event handlers). The
application is free to create additional rooms and manage which clients are in
them using the :func:`socketio.Server.enter_room` and
:func:`socketio.Server.leave_room` methods. Clients can be in as many rooms as
needed and can be moved between rooms as often as necessary. The individual
rooms assigned to clients when they connect are not special in any way, the
application is free to add or remove clients from them, though once it does
that it will lose the ability to address individual clients.

::

    @sio.on('enter room')
    def enter_room(sid, data):
        sio.enter_room(sid, data['room'])

    @sio.on('enter room')
    def leave_room(sid, data):
        sio.leave_room(sid, data['room'])

The :func:`socketio.Server.emit` method takes an event name, a message payload
of type ``str``, ``bytes``, ``list``, ``dict`` or ``tuple``, and the recipient
room. When sending a ``tuple``, the elements in it need to be of any of the
other four allowed types. The elements of the tuple will be passed as multiple
arguments to the client-side callback function. To address an individual
client, the ``sid`` of that client should be given as room (assuming the
application did not alter these initial rooms). To address all connected
clients, the ``room`` argument should be omitted.

::

    @sio.on('my message')
    def message(sid, data):
        print('message ', data)
        sio.emit('my reply', data, room='my room')

Often when broadcasting a message to group of users in a room, it is desirable
that the sender does not receive its own message. The
:func:`socketio.Server.emit` method provides an optional ``skip_sid`` argument
to specify a client that should be skipped during the broadcast.

::

    @sio.on('my message')
    def message(sid, data):
        print('message ', data)
        sio.emit('my reply', data, room='my room', skip_sid=sid)

Responses
---------

When a client sends an event to the server, it can optionally provide a
callback function, to be invoked with a response provided by the server. The
server can provide a response simply by returning it from the corresponding
event handler.

::

    @sio.on('my event', namespace='/chat')
    def my_event_handler(sid, data):
        # handle the message
        return "OK", 123

The event handler can return a single value, or a tuple with several values.
The callback function on the client side will be invoked with these returned
values as arguments.

Callbacks
---------

The server can also request a response to an event sent to a client. The
:func:`socketio.Server.emit` method has an optional ``callback`` argument that
can be set to a callable. When this argument is given, the callable will be
invoked with the arguments returned by the client as a response.

Using callback functions when broadcasting to multiple clients is not
recommended, as the callback function will be invoked once for each client
that received the message.

Namespaces
----------

The Socket.IO protocol supports multiple logical connections, all multiplexed
on the same physical connection. Clients can open multiple connections by
specifying a different *namespace* on each. A namespace is given by the client
as a pathname following the hostname and port. For example, connecting to
*http://example.com:8000/chat* would open a connection to the namespace
*/chat*.

Each namespace is handled independently from the others, with separate session
IDs (``sid``s), event handlers and rooms. It is important that applications
that use multiple namespaces specify the correct namespace when setting up
their event handlers and rooms, using the optional ``namespace`` argument
available in all the methods in the :class:`socketio.Server` class.

When the ``namespace`` argument is omitted, set to ``None`` or to ``'/'``, a
default namespace is used.

Class-Based Namespaces
----------------------

As an alternative to the decorator-based event handlers, the event handlers
that belong to a namespace can be created as methods of a subclass of 
:class:`socketio.Namespace`::

    class MyCustomNamespace(socketio.Namespace):
        def on_connect(sid, environ):
            pass

        def on_disconnect(sid):
            pass

        def on_my_event(sid, data):
            self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/test'))

When class-based namespaces are used, any events received by the server are
dispatched to a method named as the event name with the ``on_`` prefix. For
example, event ``my_event`` will be handled by a method named ``on_my_event``.
If an event is received for which there is no corresponding method defined in
the namespace class, then the event is ignored. All event names used in
class-based namespaces must used characters that are legal in method names.

As a convenience to methods defined in a class-based namespace, the namespace
instance includes versions of several of the methods in the 
:class:`socketio.Server` class that default to the proper namespace when the
``namespace`` argument is not given.

In the case that an event has a handler in a class-based namespace, and also a
decorator-based function handler, only the standalone function handler is
invoked.

It is important to note that class-based namespaces are singletons. This means
that a single instance of a namespace class is used for all clients, and
consequently, a namespace instance cannot be used to store client specific
information.

Using a Message Queue
---------------------

The Socket.IO server owns the socket connections to all the clients, so it is
the only process that can emit events to them. Unfortunately this becomes a
limitation for many applications that use more than one process. A common need
is to emit events to clients from a process other than the server, for example
a `Celery <http://www.celeryproject.org/>`_ worker.

To enable these auxiliary processes to emit events, the server can be
configured to listen for externally issued events on a message queue such as
`Redis <http://redis.io/>`_ or `RabbitMQ <https://www.rabbitmq.com/>`_.
Processes that need to emit events to client then post these events to the
queue.

Another situation in which the use of a message queue is necessary is with
high traffic applications that work with large number of clients. To support
these clients, it may be necessary to horizontally scale the Socket.IO
server by splitting the client list among multiple server processes. In this
type of installation, each server processes owns the connections to a subset
of the clients. To make broadcasting work in this environment, the servers
communicate with each other through the message queue.

The message queue service needs to be installed and configured separately. One
of the options offered by this package is to use
`Kombu <http://kombu.readthedocs.org/en/latest/>`_ to access the message
queue, which means that any message queue supported by this package can be
used. Kombu can be installed with pip::

    pip install kombu

To use RabbitMQ or other AMQP protocol compatible queues, that is the only
required dependency. But for other message queues, Kombu may require
additional packages. For example, to use a Redis queue, Kombu needs the Python
package for Redis installed as well::

    pip install redis

To configure a Socket.IO server to connect to a message queue, the
``client_manager`` argument must be passed in the server creation. The
following example instructs the server to connect to a Redis service running
on the same host and on the default port::

    mgr = socketio.KombuManager('redis://')
    sio = socketio.Server(client_manager=mgr)

For a RabbitMQ queue also running on the local server with default
credentials, the configuration is as follows::

    mgr = socketio.KombuManager('amqp://')
    sio = socketio.Server(client_manager=mgr)

The URL passed to the ``KombuManager`` constructor is passed directly to
Kombu's `Connection object
<http://kombu.readthedocs.org/en/latest/userguide/connections.html>`_, so
the Kombu documentation should be consulted for information on how to
connect to the message queue appropriately.

If the use of Kombu is not desired, native Redis support is also offered
through the ``RedisManager`` class. This class takes the same arguments as
``KombuManager``, but connects directly to a Redis store using the queue's
pub/sub functionality::

    mgr = socketio.RedisManager('redis://')
    sio = socketio.Server(client_manager=mgr)

If multiple Socket.IO servers are connected to a message queue, they
automatically communicate with each other and manage a combined client list,
without any need for additional configuration. To have a process other than
a server connect to the queue to emit a message, the same ``KombuManager``
and ``RedisManager`` classes can be used as standalone object. In this case,
the ``write_only`` argument should be set to ``True`` to disable the creation
of a listening thread. For example::

    # connect to the redis queue through Kombu
    external_sio = socketio.KombuManager('redis://', write_only=True)
    
    # emit an event
    external_sio.emit('my event', data={'foo': 'bar'}, room='my room')

Note: when using a third party package to manage a message queue such as Redis
or RabbitMQ in conjunction with eventlet or gevent, it is necessary to monkey
patch the Python standard library, so that these packages access coroutine
friendly library functions and classes.

Deployment
----------

The following sections describe a variety of deployment strategies for
Socket.IO servers.

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

`Gevent <http://gevent.org>`_ is another asynchronous framework based on
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

Gevent with uWSGI
~~~~~~~~~~~~~~~~~

When using the uWSGI server in combination with gevent, the Socket.IO server
can take advantage of uWSGI's native WebSocket support.

Instances of class ``socketio.Server`` will automatically use this option for
asynchronous operations if both gevent and uWSGI are installed and eventlet is
not installed. To request this asynchoronous mode explicitly, the
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

Standard Threading Library
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Multi-process deployments
~~~~~~~~~~~~~~~~~~~~~~~~~

Socket.IO is a stateful protocol, which makes horizontal scaling more
difficult. To deploy a cluster of Socket.IO processes (hosted on one or
multiple servers), the following conditions must be met:

- Each Socket.IO process must be able to handle multiple requests, either by
  using eventlet, gevent, or standard threads. Worker processes that only
  handle one request at a time are not supported.
- The load balancer must be configured to always forward requests from a
  client to the same worker process. Load balancers call this *sticky
  sessions*, or *session affinity*.
- The worker processes communicate with each other through a message queue,
  which must be installed and configured. See the section on using message
  queues above for instructions.

API Reference
-------------

.. module:: socketio
.. autoclass:: Middleware
   :members:
.. autoclass:: Server
   :members:
.. autoclass:: Namespace
   :members:
.. autoclass:: BaseManager
   :members:
.. autoclass:: PubSubManager
   :members:
.. autoclass:: KombuManager
   :members:
.. autoclass:: RedisManager
   :members:
