The Socket.IO Client
====================

This package contains two Socket.IO clients:

- The :func:`socketio.Client` class creates a client compatible with the
  standard Python library.
- The :func:`socketio.AsyncClient` class creates a client compatible with
  the ``asyncio`` package.

The methods in the two clients are the same, with the only difference that in
the ``asyncio`` client most methods are implemented as coroutines.

Installation
------------

To install the standard Python client along with its dependencies, use the
following command::

    pip install "python-socketio[client]"

If instead you plan on using the ``asyncio`` client, then use this::

    pip install "python-socketio[asyncio_client]"

Creating a Client Instance
--------------------------

To instantiate an Socket.IO client, simply create an instance of the
appropriate client class::

    import socketio

    # standard Python
    sio = socketio.Client()

    # asyncio
    sio = socketio.AsyncClient()

Defining Event Handlers
-----------------------

The Socket.IO protocol is event based. When a server wants to communicate with
a client it *emits* an event. Each event has a name, and a list of
arguments. The client registers event handler functions with the
:func:`socketio.Client.event` or :func:`socketio.Client.on` decorators::

    @sio.event
    def message(data):
        print('I received a message!')

    @sio.on('my message')
    def on_message(data):
        print('I received a message!')

In the first example the event name is obtained from the name of the
handler function. The second example is slightly more verbose, but it
allows the event name to be different than the function name or to include
characters that are illegal in function names, such as spaces.

For the ``asyncio`` client, event handlers can be regular functions as above,
or can also be coroutines::

    @sio.event
    async def message(data):
        print('I received a message!')

The ``connect`` and ``disconnect`` events are special; they are invoked
automatically when a client connects or disconnects from the server::

    @sio.event
    def connect():
        print("I'm connected!")

    @sio.event
    def disconnect():
        print("I'm disconnected!")

Note that the ``disconnect`` handler is invoked for application initiated
disconnects, server initiated disconnects, or accidental disconnects, for 
example due to networking failures. In the case of an accidental
disconnection, the client is going to attempt to reconnect immediately after
invoking the disconnect handler. As soon as the connection is re-established
the connect handler will be invoked once again.

If the server includes arguments with an event, those are passed to the
handler function as arguments.

Connecting to a Server
----------------------

The connection to a server is established by calling the ``connect()``
method::

    sio.connect('http://localhost:5000')

In the case of the ``asyncio`` client, the method is a coroutine::

    await sio.connect('http://localhost:5000')

Upon connection, the server assigns the client a unique session identifier.
The applicaction can find this identifier in the ``sid`` attribute::

    print('my sid is', sio.sid)

Emitting Events
---------------

The client can emit an event to the server using the ``emit()`` method::

    sio.emit('my message', {'foo': 'bar'})

Or in the case of ``asyncio``, as a coroutine::

    await sio.emit('my message', {'foo': 'bar'})

The single argument provided to the method is the data that is passed on
to the server. The data can be of type ``str``, ``bytes``, ``dict``,
``list`` or ``tuple``. When sending a ``tuple``, the elements in it need to
be of any of the other four allowed types. The elements of the tuple will be
passed as multiple arguments to the server-side event handler function.

The ``emit()`` method can be invoked inside an event handler as a response
to a server event, or in any other part of the application, including in
background tasks.

Event Callbacks
---------------

When a server emits an event to a client, it can optionally provide a
callback function, to be invoked as a way of acknowledgment that the server
has processed the event. While this is entirely managed by the server, the
client can provide a list of return values that are to be passed on to the
callback function set up by the server. This is achieves simply by returning
the desired values from the handler function::

    @sio.event
    def my_event(sid, data):
        # handle the message
        return "OK", 123

Likewise, the client can request a callback function to be invoked after the
server has processed an event. The :func:`socketio.Server.emit` method has an
optional ``callback`` argument that can be set to a callable. If this
argument is given, the callable will be invoked after the server has processed
the event, and any values returned by the server handler will be passed as
arguments to this function.

Namespaces
----------

The Socket.IO protocol supports multiple logical connections, all multiplexed
on the same physical connection. Clients can open multiple connections by
specifying a different *namespace* on each. Namespaces use a path syntax
starting with a forward slash. A list of namespaces can be given by the client
in the ``connect()`` call. For example, this example creates two logical
connections, the default one plus a second connection under the ``/chat``
namespace::

    sio.connect('http://localhost:5000', namespaces=['/chat'])

To define event handlers on a namespace, the ``namespace`` argument must be
added to the corresponding decorator::

    @sio.event(namespace='/chat')
    def my_custom_event(sid, data):
        pass

    @sio.on('connect', namespace='/chat')
    def on_connect():
        print("I'm connected to the /chat namespace!")

Likewise, the client can emit an event to the server on a namespace by
providing its in the ``emit()`` call::

    sio.emit('my message', {'foo': 'bar'}, namespace='/chat')

If the ``namespaces`` argument of the ``connect()`` call isn't given, any
namespaces used in event handlers are automatically connected.

Class-Based Namespaces
----------------------

As an alternative to the decorator-based event handlers, the event handlers
that belong to a namespace can be created as methods of a subclass of 
:class:`socketio.ClientNamespace`::

    class MyCustomNamespace(socketio.ClientNamespace):
        def on_connect(self):
            pass

        def on_disconnect(self):
            pass

        def on_my_event(self, data):
            self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/chat'))

For asyncio based severs, namespaces must inherit from
:class:`socketio.AsyncClientNamespace`, and can define event handlers as
coroutines if desired::

    class MyCustomNamespace(socketio.AsyncClientNamespace):
        def on_connect(self):
            pass

        def on_disconnect(self):
            pass

        async def on_my_event(self, data):
            await self.emit('my_response', data)

    sio.register_namespace(MyCustomNamespace('/chat'))

When class-based namespaces are used, any events received by the client are
dispatched to a method named as the event name with the ``on_`` prefix. For
example, event ``my_event`` will be handled by a method named ``on_my_event``.
If an event is received for which there is no corresponding method defined in
the namespace class, then the event is ignored. All event names used in
class-based namespaces must use characters that are legal in method names.

As a convenience to methods defined in a class-based namespace, the namespace
instance includes versions of several of the methods in the 
:class:`socketio.Client` and :class:`socketio.AsyncClient` classes that
default to the proper namespace when the ``namespace`` argument is not given.

In the case that an event has a handler in a class-based namespace, and also a
decorator-based function handler, only the standalone function handler is
invoked.

Disconnecting from the Server
-----------------------------

At any time the client can request to be disconnected from the server by
invoking the ``disconnect()`` method::

    sio.disconnect()

For the ``asyncio`` client this is a coroutine::

    await sio.disconnect()

Managing Background Tasks
-------------------------

When a client connection to the server is established, a few background
tasks will be spawned to keep the connection alive and handle incoming
events. The application running on the main thread is free to do any
work, as this is not going to prevent the functioning of the Socket.IO
client.

If the application does not have anything to do in the main thread and
just wants to wait until the connection with the server ends, it can call
the ``wait()`` method::

    sio.wait()

Or in the ``asyncio`` version::

    await sio.wait()

For the convenience of the application, a helper function is provided to
start a custom background task::

    def my_background_task(my_argument)
        # do some background work here!
        pass

    sio.start_background_task(my_background_task, 123)

The arguments passed to this method are the background function and any
positional or keyword arguments to invoke the function with. 

Here is the ``asyncio`` version::

    async def my_background_task(my_argument)
        # do some background work here!
        pass

    sio.start_background_task(my_background_task, 123)

Note that this function is not a coroutine, since it does not wait for the
background function to end. The background function must be a coroutine.

The ``sleep()`` method is a second convenince function that is provided for
the benefit of applications working with background tasks of their own::

    sio.sleep(2)

Or for ``asyncio``::

    await sio.sleep(2)

The single argument passed to the method is the number of seconds to sleep
for.
