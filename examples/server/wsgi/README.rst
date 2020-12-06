Socket.IO WSGI Examples
=======================

This directory contains example Socket.IO applications that work together with
WSGI frameworks. These examples use Flask or Django to serve the client
application to the web browser, but they should be easily adapted to use other
WSGI compliant frameworks.

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

django_example
--------------

This is a version of the "app.py" application described above, that is based
on the Django web framework.

fiddle.py
---------

This is a very simple application based on a JavaScript example of the same
name.

Running the Examples
--------------------

To run these examples, create a virtual environment, install the requirements
and then run one of the following::

    $ python app.py

::

    $ python latency.py

::

    $ cd django_example
    $ ./manage.py runserver

::

    $ python fiddle

You can then access the application from your web browser at
``http://localhost:5000`` (``app.py``, ``latency.py`` and ``fiddle.py``) or
``http://localhost:8000`` (``django_example``).

Near the top of the ``app.py``, ``latency.py`` and ``fiddle.py`` source files
there is a ``async_mode`` variable that can be edited to swich to the other
asynchornous modes. Accepted values for ``async_mode`` are ``'threading'``,
``'eventlet'`` and ``'gevent'``. For ``django_example``, the async mode can be
set in the ``django_example/socketio_app/views.py`` module.

Note 1: when using the ``'eventlet'`` mode, the eventlet package must be
installed in the virtual environment::

    $ pip install eventlet

Note 2: when using the ``'gevent'`` mode, the gevent and gevent-websocket
packages must be installed in the virtual environment::

    $ pip install gevent gevent-websocket
