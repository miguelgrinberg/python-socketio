python-socketio
===============

.. image:: https://travis-ci.org/miguelgrinberg/python-socketio.svg?branch=master
    :target: https://travis-ci.org/miguelgrinberg/python-socketio

Python implementation of the `Socket.IO`_ realtime server.

Features
--------

-  Fully compatible with the Javascript `socket.io-client`_ library.
-  Compatible with Python 2.7 and Python 3.3+.
-  Based on `Eventlet`_, enabling large number of clients even on modest
   hardware.
-  Includes a WSGI middleware that integrates Socket.IO traffic with
   standard WSGI applications.
-  Uses an event-based architecture implemented with decorators that
   hides the details of the protocol.
-  Implements HTTP long-polling and WebSocket transports.
-  Supports XHR2 and XHR browsers as clients.
-  Supports text and binary messages.
-  Supports gzip and deflate HTTP compression.
-  Configurable CORS responses to avoid cross-origin problems with
   browsers.

Example
-------

The following application uses Flask to serve the HTML/Javascript to the
client:

::

    import socketio
    import eventlet
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
        sio.emit(sid, 'reply')

    @sio.on('disconnect', namespace='/chat')
    def disconnect(sid):
        print('disconnect ', sid)

    if __name__ == '__main__':
        # wrap Flask application with engineio's middleware
        app = socketio.Middleware(eio, app)

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