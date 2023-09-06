Socket.IO Async Simple Client Examples
======================================

This directory contains example Socket.IO clients that work with the
`asyncio` package of the Python standard library, built with the simplified
client.

latency_client.py
-----------------

In this application the client sends *ping* messages to the server, which are
responded by the server with a *pong*. The client measures the time it takes
for each of these exchanges.

This is an ideal application to measure the performance of the different
asynchronous modes supported by the Socket.IO server.

fiddle_client.py
----------------

This is an extemely simple application based on the JavaScript example of the
same name.

Running the Examples
--------------------

These examples work with the server examples of the same name. First run one
of the ``latency.py`` or ``fiddle.py`` versions from one of the
``examples/server`` subdirectories. On another terminal, then start the
corresponding client::

    $ python latency_client.py
    $ python fiddle_client.py
