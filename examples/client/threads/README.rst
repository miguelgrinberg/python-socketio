Socket.IO Threading Examples
============================

This directory contains example Socket.IO clients that work with the
`threading` package of the Python standard library.

latency_client.py
-----------------

In this application the client sends *ping* messages to the server, which are
responded by the server with a *pong*. The client measures the time it takes
for each of these exchanges.

This is an ideal application to measure the performance of the different
asynchronous modes supported by the Socket.IO server.

Running the Examples
--------------------

These examples work with the server examples of the same name. First run one
of the `latency.py` versions from the `examples/server/wsgi` directory. On 
another terminal, then start the corresponding client::

    $ python latency_client.py
