python-socketio
===============

.. image:: https://travis-ci.org/miguelgrinberg/python-socketio.svg?branch=master
    :target: https://travis-ci.org/miguelgrinberg/python-socketio

Python implementation of the `Socket.IO`_ realtime server.

Features
--------

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

Example
-------

The following application uses Flask to serve the HTML/Javascript to the
client:

.. code:: python

    import socketio
    import eventlet
    import eventlet.wsgi
    from flask import Flask, render_template

    sio = socketio.Server()
    app = Flask(__name__)

    @app.route('/')
    def index():
        """Serve the client-side application."""
        return render_template('index.html')

    @sio.on('connect', namespace='/chat')
    def connect(sid, environ):
        print("connect ", sid)

    @sio.on('chat message', namespace='/chat')
    def message(sid, data):
        print("message ", data)
        sio.emit('reply', room=sid)

    @sio.on('disconnect', namespace='/chat')
    def disconnect(sid):
        print('disconnect ', sid)

    if __name__ == '__main__':
        # wrap Flask application with engineio's middleware
        app = socketio.Middleware(sio, app)

        # deploy as an eventlet WSGI server
        eventlet.wsgi.server(eventlet.listen(('', 8000)), app)

Resources
---------

-  `Documentation`_
-  `PyPI`_

.. _Socket.IO: https://github.com/Automattic/socket.io
.. _socket.io-client: https://github.com/Automattic/socket.io-client
.. _Eventlet: http://eventlet.net/
.. _Documentation: http://pythonhosted.org/python-socketio
.. _PyPI: https://pypi.python.org/pypi/python-socketio
