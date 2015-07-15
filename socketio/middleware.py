import engineio


class Middleware(engineio.Middleware):
    """WSGI middleware for Socket.IO.

    This middleware dispatches traffic to a Socket.IO application, and
    optionally forwards regular HTTP traffic to a WSGI application.

    :param socketio_app: The Socket.IO server.
    :param wsgi_app: The WSGI app that receives all other traffic.
    :param socketio_path: The endpoint where the Socket.IO application should
                          be installed. The default value is appropriate for
                          most cases.

    Example usage::

        import socketio
        import eventlet
        from . import wsgi_app

        sio = socketio.Server()
        app = socketio.Middleware(sio, wsgi_app)
        eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
    """
    def __init__(self, socketio_app, wsgi_app=None, socketio_path='socket.io'):
        super(Middleware, self).__init__(socketio_app, wsgi_app, socketio_path)
