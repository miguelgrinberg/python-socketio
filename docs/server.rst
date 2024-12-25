The Socket.IO Server
====================

This package contains two Socket.IO servers:

- The :func:`socketio.Server` class creates a server compatible with the
  Python standard library.
- The :func:`socketio.AsyncServer` class creates a server compatible with
  the ``asyncio`` package.

The methods in the two servers are the same, with the only difference that in
the ``asyncio`` server most methods are implemented as coroutines.

Installation
------------

To install the Socket.IO server along with its dependencies, use the following
command::

    pip install python-socketio

If you plan to build an asynchronous web server based on the ``asyncio``
package, then you can install this package and some additional dependencies
that are needed with::

    pip install "python-socketio[asyncio]"

Creating a Server Instance
--------------------------

A Socket.IO server is an instance of class :class:`socketio.Server`::

    import socketio

    # create a Socket.IO server
    sio = socketio.Server()

For asyncio based servers, the :class:`socketio.AsyncServer` class provides
the same functionality, but in a coroutine friendly format::

    import socketio

    # create a Socket.IO server
    sio = socketio.AsyncServer()

Running the Server
------------------

To run the Socket.IO application it is necessary to configure a web server to
receive incoming requests from clients and forward them to the Socket.IO
server instance. To simplify this task, several integrations are available,
including support for the `WSGI <https://wsgi.readthedocs.io/en/latest/what.html>`_
and `ASGI <https://asgi.readthedocs.io/en/latest/>`_ standards.

Running as a WSGI Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the Socket.IO server as a WSGI application wrap the server
instance with the :class:`socketio.WSGIApp` class::

    # wrap with a WSGI application
    app = socketio.WSGIApp(sio)

The resulting WSGI application can be executed with supported WSGI servers
such as `Werkzeug <https://werkzeug.palletsprojects.com>`_ for development and
`Gunicorn <https://gunicorn.org/>`_ for production.

When combining Socket.IO with a web application written with a WSGI framework
such as Flask or Django, the ``WSGIApp`` class can wrap both applications
together and route traffic to them::

    from mywebapp import app  # a Flask, Django, etc. application
    app = socketio.WSGIApp(sio, app)

Running as an ASGI Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To configure the Socket.IO server as an ASGI application wrap the server
instance with the :class:`socketio.ASGIApp` class::

    # wrap with ASGI application
    app = socketio.ASGIApp(sio)

The resulting ASGI application can be executed with an ASGI compliant web
server, for example `Uvicorn <https://www.uvicorn.org/>`_.

Socket.IO can also be combined with a web application written with an ASGI
web framework such as FastAPI. In that case, the ``ASGIApp`` class can wrap
both applications together and route traffic to them::

    from mywebapp import app  # a FastAPI or other ASGI application
    app = socketio.ASGIApp(sio, app)

Serving Static Files
~~~~~~~~~~~~~~~~~~~~

The Socket.IO server can be configured to serve static files to clients. This
is particularly useful to deliver HTML, CSS and JavaScript files to clients
when this package is used without a companion web framework.

Static files are configured with a Python dictionary in which each key/value
pair is a static file mapping rule. In its simplest form, this dictionary has
one or more static file URLs as keys, and the corresponding files in the server
as values::

    static_files = {
        '/': 'latency.html',
        '/static/socket.io.js': 'static/socket.io.js',
        '/static/style.css': 'static/style.css',
    }

With this example configuration, when the server receives a request for ``/``
(the root URL) it will return the contents of the file ``latency.html`` in the
current directory, and will assign a content type based on the file extension,
in this case ``text/html``.

Files with the ``.html``, ``.css``, ``.js``, ``.json``, ``.jpg``, ``.png``,
``.gif`` and ``.txt`` file extensions are automatically recognized and
assigned the correct content type. For files with other file extensions or
with no file extension, the ``application/octet-stream`` content type is used
as a default.

If desired, an explicit content type for a static file can be given as follows::

    static_files = {
        '/': {'filename': 'latency.html', 'content_type': 'text/plain'},
    }

It is also possible to configure an entire directory in a single rule, so that
all the files in it are served as static files::

    static_files = {
        '/static': './public',
    }

In this example any files with URLs starting with ``/static`` will be served
directly from the ``public`` folder in the current directory, so for example,
the URL ``/static/index.html`` will return local file ``./public/index.html``
and the URL ``/static/css/styles.css`` will return local file
``./public/css/styles.css``.

If a URL that ends in a ``/`` is requested, then a default filename of
``index.html`` is appended to it. In the previous example, a request for the
``/static/`` URL would return local file ``./public/index.html``. The default
filename to serve for slash-ending URLs can be set in the static files
dictionary with an empty key::

    static_files = {
        '/static': './public',
        '': 'image.gif',
    }

With this configuration, a request for ``/static/`` would return
local file ``./public/image.gif``. A non-standard content type can also be
specified if needed::

    static_files = {
        '/static': './public',
        '': {'filename': 'image.gif', 'content_type': 'text/plain'},
    }

The static file configuration dictionary is given as the ``static_files``
argument to the ``socketio.WSGIApp`` or ``socketio.ASGIApp`` classes::

    # for standard WSGI applications
    sio = socketio.Server()
    app = socketio.WSGIApp(sio, static_files=static_files)

    # for asyncio-based ASGI applications
    sio = socketio.AsyncServer()
    app = socketio.ASGIApp(sio, static_files=static_files)

The routing precedence in these two classes is as follows:

- First, the path is checked against the Socket.IO endpoint.
- Next, the path is checked against the static file configuration, if present.
- If the path did not match the Socket.IO endpoint or any static file, control
  is passed to the secondary application if configured, else a 404 error is
  returned.

Note: static file serving is intended for development use only, and as such
it lacks important features such as caching. Do not use in a production
environment.

Events
------

The Socket.IO protocol is event based. When a client wants to communicate with
the server, or the server wants to communicate with one or more clients, they
*emit* an event to the other party. Each event has a name, and an optional list
of arguments.

Listening to Events
~~~~~~~~~~~~~~~~~~~

To receive events from clients, the server application must register event
handler functions. These functions are invoked when the corresponding events
are emitted by clients. To register a handler for an event, the
:func:`socketio.Server.event` or :func:`socketio.Server.on` decorators are used::

    @sio.event
    def my_event(sid, data):
        pass

    @sio.on('my custom event')
    def another_event(sid, data):
        pass

In the first example the event name is obtained from the name of the handler
function. The second example is slightly more verbose, but it allows the event
name to be different than the function name or to include characters that are
illegal in function names, such as spaces.

For asyncio servers, event handlers can optionally be given as coroutines::

    @sio.event
    async def my_event(sid, data):
        pass

The ``sid`` argument that is passed to all handlers is the Socket.IO session
id, a unique identifier that Socket.IO assigns to each client connection. All
the events sent by a given client will have the same ``sid`` value.

Connect and Disconnect Events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``connect`` and ``disconnect`` events are special; they are invoked
automatically when a client connects or disconnects from the server::

    @sio.event
    def connect(sid, environ, auth):
        print('connect ', sid)

    @sio.event
    def disconnect(sid, reason):
        print('disconnect ', sid, reason)

The ``connect`` event is an ideal place to perform user authentication, and
any necessary mapping between user entities in the application and the ``sid``
that was assigned to the client.

In addition to the ``sid``, the connect handler receives ``environ`` as an
argument, with the request information in standard WSGI format, including HTTP
headers. The connect handler also receives the ``auth`` argument with any
authentication details passed by the client, or ``None`` if the client did not
pass any authentication.

After inspecting the arguments, the connect event handler can return ``False``
to reject the connection with the client. Sometimes it is useful to pass data
back to the client being rejected. In that case instead of returning ``False``
a :class:`socketio.exceptions.ConnectionRefusedError` exception can be raised,
and all of its arguments will be sent to the client with the rejection
message::

    @sio.event
    def connect(sid, environ, auth):
        raise ConnectionRefusedError('authentication failed')

The disconnect handler receives the ``sid`` assigned to the client and a
``reason``, which provides the cause of the disconnection::

    @sio.event
    def disconnect(sid, reason):
        if reason == sio.reason.CLIENT_DISCONNECT:
            print('the client disconnected')
        elif reason == sio.reason.SERVER_DISCONNECT:
            print('the server disconnected the client')
        else:
            print('disconnect reason:', reason)

See the The :attr:`socketio.Server.reason` attribute for a list of possible
disconnection reasons.

Catch-All Event Handlers
~~~~~~~~~~~~~~~~~~~~~~~~

A "catch-all" event handler is invoked for any events that do not have an
event handler. You can define a catch-all handler using ``'*'`` as event name::

   @sio.on('*')
   def any_event(event, sid, data):
        pass

Asyncio servers can also use a coroutine::

   @sio.on('*')
   async def any_event(event, sid, data):
       pass

A catch-all event handler receives the event name as a first argument. The
remaining arguments are the same as for a regular event handler.

Note that the ``connect`` and ``disconnect`` events have to be defined
explicitly and are not invoked on a catch-all event handler.

Emitting Events to Clients
~~~~~~~~~~~~~~~~~~~~~~~~~~

Socket.IO is a bidirectional protocol, so at any time the server can send an
event to its connected clients. The :func:`socketio.Server.emit` method is
used for this task::

   sio.emit('my event', {'data': 'foobar'})

The first argument is the event name, followed by an optional data payload of
type ``str``, ``bytes``, ``list``, ``dict`` or ``tuple``. When sending a
``list``, ``dict`` or ``tuple``, the elements are also constrained to the same
data types. When a ``tuple`` is sent, the elements of the tuple will be passed
as multiple arguments to the client-side event handler function.

The above example will send the event to all the clients are connected.
Sometimes the server may want to send an event just to one particular client.
This can be achieved by adding a ``to`` argument to the emit call, with the
``sid`` of the client::

   sio.emit('my event', {'data': 'foobar'}, to=user_sid)

The ``to`` argument is used to identify the client that should receive the
event, and is set to the ``sid`` value assigned to that client's connection
with the server. When ``to`` is omitted, the event is broadcasted to all
connected clients.

Acknowledging Events
~~~~~~~~~~~~~~~~~~~~

When a client sends an event to the server, it can optionally request to
receive acknowledgment from the server. The sending of acknowledgements is
automatically managed by the Socket.IO server, but the event handler function
can provide a list of values that are to be passed on to the client with the
acknowledgement simply by returning them::

    @sio.event
    def my_event(sid, data):
        # handle the message
        return "OK", 123  # <-- client will have these as acknowledgement

Requesting Client Acknowledgements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similar to how clients can request acknowledgements from the server, when the
server is emitting to a single client it can also ask the client to acknowledge
the event, and optionally return one or more values as a response.

The Socket.IO server supports two ways of working with client acknowledgements.
The most convenient method is to replace :func:`socketio.Server.emit` with
:func:`socketio.Server.call`. The ``call()`` method will emit the event, and
then wait until the client sends an acknowledgement, returning any values
provided by the client::

    response = sio.call('my event', {'data': 'foobar'}, to=user_sid)

A much more primitive acknowledgement solution uses callback functions. The
:func:`socketio.Server.emit` method has an optional ``callback`` argument that
can be set to a callable. If this argument is given, the callable will be
invoked after the client has processed the event, and any values returned by
the client will be passed as arguments to this function::

    def my_callback():
        print("callback invoked!")

    sio.emit('my event', {'data': 'foobar'}, to=user_sid, callback=my_callback)

Rooms
-----

To make it easy for the server to emit events to groups of related clients,
the application can put its clients into "rooms", and then address messages to
these rooms.

In previous examples, the ``to`` argument of the :func:`socketio.SocketIO.emit`
method was used to designate a specific client as the recipient of the event.
The ``to`` argument can also be given the name of a room, and then all the
clients that are in that room will receive the event.

The application can create as many rooms as needed and manage which clients are
in them using the :func:`socketio.Server.enter_room` and
:func:`socketio.Server.leave_room` methods. Clients can be in as many
rooms as needed and can be moved between rooms when necessary.

::

    @sio.event
    def begin_chat(sid):
        sio.enter_room(sid, 'chat_users')

    @sio.event
    def exit_chat(sid):
        sio.leave_room(sid, 'chat_users')

In chat applications it is often desired that an event is broadcasted to all
the members of the room except one, which is the originator of the event such
as a chat message. The :func:`socketio.Server.emit` method provides an
optional ``skip_sid`` argument to indicate a client that should be skipped
during the broadcast.

::

    @sio.event
    def my_message(sid, data):
        sio.emit('my reply', data, room='chat_users', skip_sid=sid)

Namespaces
----------

The Socket.IO protocol supports multiple logical connections, all multiplexed
on the same physical connection. Clients can open multiple connections by
specifying a different *namespace* on each. A namespace is given by the client
as a pathname following the hostname and port. For example, connecting to
*http://example.com:8000/chat* would open a connection to the namespace
*/chat*.

Each namespace works independently from the others, with separate session
IDs (``sid``\ s), event handlers and rooms. Namespaces can be defined directly
in the event handler functions, or they can also be created as classes.

Decorator-Based Namespaces
~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorator-based namespaces are regular event handlers that include the
``namespace`` argument in their decorator::

    @sio.event(namespace='/chat')
    def my_custom_event(sid, data):
        pass

    @sio.on('my custom event', namespace='/chat')
    def my_custom_event(sid, data):
        pass

When emitting an event, the ``namespace`` optional argument is used to specify
which namespace to send it on. When the ``namespace`` argument is omitted, the
default Socket.IO namespace, which is named ``/``, is used.

It is important that applications that use multiple namespaces specify the
correct namespace when setting up their event handlers and rooms using the
optional ``namespace`` argument. This argument must also be specified when
emitting events under a namespace. Most methods in the :class:`socketio.Server`
class have the optional ``namespace`` argument.

Class-Based Namespaces
~~~~~~~~~~~~~~~~~~~~~~

As an alternative to the decorator-based namespaces, the event handlers that
belong to a namespace can be created as methods in a subclass of
:class:`socketio.Namespace`::

    class MyCustomNamespace(socketio.Namespace):
        def on_connect(self, sid, environ):
            pass

        def on_disconnect(self, sid, reason):
            pass

        def on_my_event(self, sid, data):
            self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/test'))

For asyncio based servers, namespaces must inherit from
:class:`socketio.AsyncNamespace`, and can define event handlers as coroutines
if desired::

    class MyCustomNamespace(socketio.AsyncNamespace):
        def on_connect(self, sid, environ):
            pass

        def on_disconnect(self, sid, reason):
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

Catch-All Namespaces
~~~~~~~~~~~~~~~~~~~~

Similarily to catch-all event handlers, a "catch-all" namespace can be used
when defining event handlers for any connected namespaces that do not have an
explicitly defined event handler. As with catch-all events, ``'*'`` is used in
place of a namespace::

   @sio.on('my_event', namespace='*')
   def my_event_any_namespace(namespace, sid, data):
       pass

For these events, the namespace is passed as first argument, followed by the
regular arguments of the event.

A catch-all class-based namespace handler can be defined by passing ``'*'`` as
the namespace during registration::

    sio.register_namespace(MyCustomNamespace('*'))

A "catch-all" handler for all events on all namespaces can be defined as
follows::

   @sio.on('*', namespace='*')
   def any_event_any_namespace(event, namespace, sid, data):
       pass

Event handlers with catch-all events and namespaces receive the event name and
the namespace as first and second arguments.

User Sessions
-------------

The server can maintain application-specific information in a user session
dedicated to each connected client. Applications can use the user session to
write any details about the user that need to be preserved throughout the life
of the connection, such as usernames or user ids.

The ``save_session()`` and ``get_session()`` methods are used to store and
retrieve information in the user session::

    @sio.event
    def connect(sid, environ):
        username = authenticate_user(environ)
        sio.save_session(sid, {'username': username})

    @sio.event
    def message(sid, data):
        session = sio.get_session(sid)
        print('message from ', session['username'])

For the ``asyncio`` server, these methods are coroutines::

    @sio.event
    async def connect(sid, environ):
        username = authenticate_user(environ)
        await sio.save_session(sid, {'username': username})

    @sio.event
    async def message(sid, data):
        session = await sio.get_session(sid)
        print('message from ', session['username'])

The session can also be manipulated with the `session()` context manager::

    @sio.event
    def connect(sid, environ):
        username = authenticate_user(environ)
        with sio.session(sid) as session:
            session['username'] = username

    @sio.event
    def message(sid, data):
        with sio.session(sid) as session:
            print('message from ', session['username'])

For the ``asyncio`` server, an asynchronous context manager is used::

    @sio.event
    async def connect(sid, environ):
        username = authenticate_user(environ)
        async with sio.session(sid) as session:
            session['username'] = username

    @sio.event
    async def message(sid, data):
        async with sio.session(sid) as session:
            print('message from ', session['username'])

The ``get_session()``, ``save_session()`` and ``session()`` methods take an
optional ``namespace`` argument. If this argument isn't provided, the session
is attached to the default namespace.

Note: the contents of the user session are destroyed when the client
disconnects. In particular, user session contents are not preserved when a
client reconnects after an unexpected disconnection from the server.

Cross-Origin Controls
---------------------

For security reasons, this server enforces a same-origin policy by default. In
practical terms, this means the following:

- If an incoming HTTP or WebSocket request includes the ``Origin`` header,
  this header must match the scheme and host of the connection URL. In case
  of a mismatch, a 400 status code response is returned and the connection is
  rejected.
- No restrictions are imposed on incoming requests that do not include the
  ``Origin`` header.

If necessary, the ``cors_allowed_origins`` option can be used to allow other
origins. This argument can be set to a string to set a single allowed origin, or
to a list to allow multiple origins. A special value of ``'*'`` can be used to
instruct the server to allow all origins, but this should be done with care, as
this could make the server vulnerable to Cross-Site Request Forgery (CSRF)
attacks.

Monitoring and Administration
-----------------------------

The Socket.IO server can be configured to accept connections from the official
`Socket.IO Admin UI <https://socket.io/docs/v4/admin-ui/>`_. This tool provides
real-time information about currently connected clients, rooms in use and
events being emitted. It also allows an administrator to manually emit events,
change room assignments and disconnect clients. The hosted version of this tool
is available at `https://admin.socket.io <https://admin.socket.io>`_. 

Given that enabling this feature can affect the performance of the server, it
is disabled by default. To enable it, call the
:func:`instrument() <socketio.Server.instrument>` method. For example::

    import os
    import socketio

    sio = socketio.Server(cors_allowed_origins=[
        'http://localhost:5000',
        'https://admin.socket.io',
    ])
    sio.instrument(auth={
        'username': 'admin',
        'password': os.environ['ADMIN_PASSWORD'],
    })

This configures the server to accept connections from the hosted Admin UI
client. Administrators can then open https://admin.socket.io in their web
browsers and log in with username ``admin`` and the password given by the
``ADMIN_PASSWORD`` environment variable. To ensure the Admin UI front end is
allowed to connect, CORS is also configured.

Consult the reference documentation to learn about additional configuration
options that are available.

Debugging and Troubleshooting
-----------------------------

To help you debug issues, the server can be configured to output logs to the
terminal::

    import socketio

    # standard Python
    sio = socketio.Server(logger=True, engineio_logger=True)

    # asyncio
    sio = socketio.AsyncServer(logger=True, engineio_logger=True)

The ``logger`` argument controls logging related to the Socket.IO protocol,
while ``engineio_logger`` controls logs that originate in the low-level
Engine.IO transport. These arguments can be set to ``True`` to output logs to
``stderr``, or to an object compatible with Python's ``logging`` package
where the logs should be emitted to. A value of ``False`` disables logging.

Logging can help identify the cause of connection problems, 400 responses,
bad performance and other issues.

Concurrency and Web Server Integration
--------------------------------------

The Socket.IO server can be configured with different concurrency models
depending on the needs of the application and the web server that is used. The
concurrency model is given by the ``async_mode`` argument in the server. For
example::

    sio = socketio.Server(async_mode='threading')

The following sub-sections describe the available concurrency options for
synchronous and asynchronous servers.

Standard Modes
~~~~~~~~~~~~~~

- ``threading``: the server will use Python threads for concurrency and will
  run on any multi-threaded WSGI server. This is the default mode when no other
  concurrency libraries are installed.
- ``gevent``: the server will use greenlets through the
  `gevent <http://www.gevent.org/>`_ library for concurrency. A web server that
  is compatible with ``gevent`` is required.
- ``gevent_uwsgi``: a variation of the ``gevent`` mode that is designed to work
  with the `uWSGI <https://uwsgi-docs.readthedocs.io/en/latest/>`_ web server.
- ``eventlet``: the server will use greenlets through the
  `eventlet <http://eventlet.net/>`_ library for concurrency. A web server that
  is compatible with ``eventlet`` is required. Use of ``eventlet`` is not
  recommended due to this project being in maintenance mode.

Asyncio Modes
~~~~~~~~~~~~~

The asynchronous options are all based on the
`asyncio <https://docs.python.org/3/library/asyncio.html>`_ package of the
Python standard library, with minor variations depending on the web server
platform that is used.

- ``asgi``: use of any
  `ASGI <https://asgi.readthedocs.io/en/latest/>`_ web server is required.
- ``aiohttp``: use of the `aiohttp <http://aiohttp.readthedocs.io/>`_ web
  framework and server is required.
- ``tornado``: use of the `Tornado <http://www.tornadoweb.org/>`_ web framework
  and server is required.
- ``sanic``: use of the `Sanic <http://sanic.readthedocs.io/>`_ web framework
  and server is required. When using Sanic, it is recommended to use the
  ``asgi`` mode instead.

.. _deployment-strategies:

Deployment Strategies
---------------------

The following sections describe a variety of deployment strategies for
Socket.IO servers.

Gunicorn
~~~~~~~~

The simplest deployment strategy for the Socket.IO server is to use the popular
`Gunicorn <http://gunicorn.org>`_ web server in multi-threaded mode. The
Socket.IO server must be wrapped by the :class:`socketio.WSGIApp` class, so
that it is compatible with the WSGI protocol::

    sio = socketio.Server(async_mode='threading')
    app = socketio.WSGIApp(sio)

If desired, the ``socketio.WSGIApp`` class can forward any traffic that is not
Socket.IO to another WSGI application, making it possible to deploy a standard
WSGI web application built with frameworks such as Flask or Django and the
Socket.IO server as a bundle::

   sio = socketio.Server(async_mode='threading')
   app = socketio.WSGIApp(sio, other_wsgi_app)

The example that follows shows how to start a Socket.IO application using
Gunicorn's threaded worker class::

    $ gunicorn --workers 1 --threads 100 --bind 127.0.0.1:5000 module:app

With the above configuration the server will be able to handle close to 100
concurrent clients.

It is also possible to use more than one worker process, but this has two
additional requirements:

- The clients must connect directly over WebSocket. The long-polling transport
  is incompatible with the way Gunicorn load balances requests among workers.
  To disable long-polling in the server, add ``transports=['websocket']`` in
  the server constructor. Clients will have a similar option to initiate the
  connection with WebSocket.
- The :func:`socketio.Server` instances in each worker must be configured with
  a message queue to allow the workers to communicate with each other. See the
  :ref:`using-a-message-queue` section for more information.

When using multiple workers, the approximate number of connections the server
will be able to accept can be calculated as the number of workers multiplied by
the number of threads per worker.

Note that Gunicorn can also be used alongside ``uvicorn``, ``gevent`` and
``eventlet``. These options are discussed under the appropriate sections below.

Uvicorn (and other ASGI web servers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When working with an asynchronous Socket.IO server, the easiest deployment
strategy is to use an ASGI web server such as
`Uvicorn <https://www.uvicorn.org/>`_.

The ``socketio.ASGIApp`` class is an ASGI compatible application that can
forward Socket.IO traffic to a ``socketio.AsyncServer`` instance::

   sio = socketio.AsyncServer(async_mode='asgi')
   app = socketio.ASGIApp(sio)

If desired, the ``socketio.ASGIApp`` class can forward any traffic that is not
Socket.IO to another ASGI application, making it possible to deploy a standard
ASGI web application built with a framework such as FastAPI and the Socket.IO
server as a bundle::

   sio = socketio.AsyncServer(async_mode='asgi')
   app = socketio.ASGIApp(sio, other_asgi_app)

The following example starts the application with Uvicorn::

    uvicorn --port 5000 module:app

Uvicorn can also be used through its Gunicorn worker::

    gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:5000

See the Gunicorn section above for information on how to use Gunicorn with
multiple workers.

Hypercorn, Daphne, and other ASGI servers
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

To use an ASGI web server other than Uvicorn, configure the application for
ASGI as shown above for Uvicorn, then follow the documentation of your chosen
web server to start the application.

Aiohttp
~~~~~~~

Another option for deploying an asynchronous Socket.IO server is to use the
`Aiohttp <http://aiohttp.readthedocs.io/>`_ web framework and server. Instances
of class ``socketio.AsyncServer`` will automatically use Aiohttp
if the library is installed. To request its use explicitly, the ``async_mode``
option can be given in the constructor::

    sio = socketio.AsyncServer(async_mode='aiohttp')

A server configured for Aiohttp must be attached to an existing application::

    app = web.Application()
    sio.attach(app)

The Aiohttp application can define regular routes that will coexist with the
Socket.IO server. A typical pattern is to add routes that serve a client
application and any associated static files.

The Aiohttp application is then executed in the usual manner::

    if __name__ == '__main__':
        web.run_app(app)

Gevent
~~~~~~

When a multi-threaded web server is unable to satisfy the concurrency and
scalability requirements of the application, an option to try is
`Gevent <http://www.gevent.org>`_. Gevent is a coroutine-based concurrency library
based on greenlets, which are significantly lighter than threads.

Instances of class ``socketio.Server`` will automatically use Gevent if the
library is installed. To request gevent to be selected explicitly, the
``async_mode`` option can be given in the constructor::

    sio = socketio.Server(async_mode='gevent')

The Socket.IO server must be wrapped by the :class:`socketio.WSGIApp` class, so
that it is compatible with the WSGI protocol::

    app = socketio.WSGIApp(sio)

If desired, the ``socketio.WSGIApp`` class can forward any traffic that is not
Socket.IO to another WSGI application, making it possible to deploy a standard
WSGI web application built with frameworks such as Flask or Django and the
Socket.IO server as a bundle::

    sio = socketio.Server(async_mode='gevent')
    app = socketio.WSGIApp(sio, other_wsgi_app)

A server configured for Gevent is deployed as a regular WSGI application
using the provided ``socketio.WSGIApp``::

    from gevent import pywsgi

    pywsgi.WSGIServer(('', 8000), app).serve_forever()

Gevent with Gunicorn
!!!!!!!!!!!!!!!!!!!!

An alternative to running the gevent WSGI server as above is to use
`Gunicorn <gunicorn.org>`_ with its Gevent worker. The command to launch the
application under Gunicorn and Gevent is shown below::

    $ gunicorn -k gevent -w 1 -b 127.0.0.1:5000 module:app

See the Gunicorn section above for information on how to use Gunicorn with
multiple workers.

Gevent provides a ``monkey_patch()`` function that replaces all the blocking
functions in the standard library with equivalent asynchronous versions. While
the Socket.IO server does not require monkey patching, other libraries such as
database or message queue drivers are likely to require it.

Gevent with uWSGI
!!!!!!!!!!!!!!!!!

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

Tornado
~~~~~~~

Instances of class ``socketio.AsyncServer`` will automatically use
`Tornado <http://www.tornadoweb.org//>`_ if the library is installed. To
request its use explicitly, the ``async_mode`` option can be given in the
constructor::

    sio = socketio.AsyncServer(async_mode='tornado')

A server configured for Tornado must include a request handler for
Socket.IO::

    app = tornado.web.Application(
        [
            (r"/socket.io/", socketio.get_tornado_handler(sio)),
        ],
        # ... other application options
    )

The Tornado application can define other routes that will coexist with the
Socket.IO server. A typical pattern is to add routes that serve a client
application and any associated static files.

The Tornado application is then executed in the usual manner::

    app.listen(port)
    tornado.ioloop.IOLoop.current().start()

Eventlet
~~~~~~~~

.. note::
   Eventlet is not in active development anymore, and for that reason the
   current recommendation is to not use it for new projects.

`Eventlet <http://eventlet.net/>`_ is a high performance concurrent networking
library for Python that uses coroutines, enabling code to be written in the
same style used with the blocking standard library functions. An Socket.IO
server deployed with eventlet has access to the long-polling and WebSocket
transports.

Instances of class ``socketio.Server`` will automatically use eventlet for
asynchronous operations if the library is installed. To request its use
explicitly, the ``async_mode`` option can be given in the constructor::

    sio = socketio.Server(async_mode='eventlet')

A server configured for eventlet is deployed as a regular WSGI application
using the provided ``socketio.WSGIApp``::

    import eventlet

    app = socketio.WSGIApp(sio)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

Eventlet with Gunicorn
!!!!!!!!!!!!!!!!!!!!!!

An alternative to running the eventlet WSGI server as above is to use
`gunicorn <gunicorn.org>`_, a fully featured pure Python web server. The
command to launch the application under gunicorn is shown below::

    $ gunicorn -k eventlet -w 1 module:app

See the Gunicorn section above for information on how to use Gunicorn with
multiple workers.

Eventlet provides a ``monkey_patch()`` function that replaces all the blocking
functions in the standard library with equivalent asynchronous versions. While
python-socketio does not require monkey patching, other libraries such as
database drivers are likely to require it.

Sanic
~~~~~

.. note::
   The Sanic integration has not been updated in a long time. It is currently
   recommended that a Sanic application is deployed with the ASGI integration.

.. _using-a-message-queue:

Using a Message Queue
---------------------

When working with distributed applications, it is often necessary to access
the functionality of the Socket.IO from multiple processes. There are two
specific use cases:

- Highly available applications may want to use horizontal scaling of the
  Socket.IO server to be able to handle very large number of concurrent
  clients.
- Applications that use work queues such as
  `Celery <http://www.celeryproject.org/>`_ may need to emit an event to a
  client once a background job completes. The most convenient place to carry
  out this task is the worker process that handled this job.

As a solution to the above problems, the Socket.IO server can be configured
to connect to a message queue such as `Redis <http://redis.io/>`_ or
`RabbitMQ <https://www.rabbitmq.com/>`_, to communicate with other related
Socket.IO servers or auxiliary workers.

Redis
~~~~~

To use a Redis message queue, a Python Redis client must be installed::

    # socketio.Server class
    pip install redis

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

Kafka
~~~~~

`Apache Kafka <https://kafka.apache.org/>`_ is supported through the
`kafka-python <https://kafka-python.readthedocs.io/en/master/index.html>`_
package::

    pip install kafka-python

Access to Kafka is configured through the :class:`socketio.KafkaManager`
class::

    mgr = socketio.KafkaManager('kafka://')
    sio = socketio.Server(client_manager=mgr)

Note that Kafka currently does not support asyncio, so it cannot be used with
the :class:`socketio.AsyncServer` class.

AioPika
~~~~~~~

A RabbitMQ message queue is supported in asyncio applications through the 
`AioPika <https://aio-pika.readthedocs.io/en/latest/>`_ package::
You need to install aio_pika with pip::

    pip install aio_pika

The RabbitMQ queue is configured through the
:class:`socketio.AsyncAioPikaManager` class::

    mgr = socketio.AsyncAioPikaManager('amqp://')
    sio = socketio.AsyncServer(client_manager=mgr)

Horizontal Scaling
~~~~~~~~~~~~~~~~~~

Socket.IO is a stateful protocol, which makes horizontal scaling more
difficult. When deploying a cluster of Socket.IO processes, all processes must
connect to the message queue by passing the ``client_manager`` argument to the
server instance. This enables the workers to communicate and coordinate complex
operations such as broadcasts.

If the long-polling transport is used, then there are two additional
requirements that must be met:

- Each Socket.IO process must be able to handle multiple requests
  concurrently. This is needed because long-polling clients send two
  requests in parallel. Worker processes that can only handle one request at a
  time are not supported.
- The load balancer must be configured to always forward requests from a
  client to the same worker process, so that all requests coming from a client
  are handled by the same node. Load balancers call this *sticky sessions*, or
  *session affinity*.

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

A limitation of the write-only client manager object is that it cannot receive
callbacks when emitting. When the external process needs to receive callbacks,
using a client to connect to the server with read and write support is a better
option than a write-only client manager.
