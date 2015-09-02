Engine.IO Examples
==================

This directory contains example Engine.IO applications.

app.py
------

A basic "kitchen sink" type application that allows the user to experiment
with most of the available features of the server.

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

To run these examples using the default ``'threading'`` mode, create a virtual
environment, install the requirements and then run::

    $ python app.py

or::

    $ python latency.py

Near the top of the ``app.py`` and ``latency.py`` source files there is a
``async_mode`` variable that can be edited to swich to the other asynchornous
modes. Accepted values for ``async_mode`` are ``'threading'``, ``'eventlet'``
and ``'gevent'``.

Note 1: when using the ``'eventlet'`` mode, the eventlet package must be
installed in the virtual environment::

    $ pip install eventlet

Note 2: when using the ``'gevent'`` mode, the gevent and gevent-websocket
packages must be installed in the virtual environment::

    $ pip install gevent gevent-websocket
