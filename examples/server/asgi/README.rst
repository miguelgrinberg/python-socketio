Socket.IO ASGI Examples
==========================

This directory contains example Socket.IO applications that are compatible with
asyncio and the ASGI specification.

app.py
------

A basic "kitchen sink" type application that allows the user to experiment
with most of the available features of the Socket.IO server.

latency.py
----------

A port of the latency application included in the official Engine.IO
Javascript server. In this application the client sends *ping* messages to
the server, which are responded by the server with a *pong*. The client
measures the time it takes for each of these exchanges and plots these in real
time to the page.

This is an ideal application to measure the performance of the different
asynchronous modes supported by the Socket.IO server.

Running the Examples
--------------------

To run these examples, create a virtual environment, install the requirements
and then run::

    $ python app.py

or::

    $ python latency.py

You can then access the application from your web browser at
``http://localhost:5000``.
