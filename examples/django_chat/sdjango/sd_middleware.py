import urllib
import engineio


class SdMiddleware(engineio.Middleware):
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
        super().__init__(socketio_app, wsgi_app, socketio_path)

    def __call__(self, environ, start_response):
        if 'gunicorn.socket' in environ:
            # gunicorn saves the socket under environ['gunicorn.socket'], while
            # eventlet saves it under environ['eventlet.input']. Eventlet also
            # stores the socket inside a wrapper class, while gunicon writes it
            # directly into the environment. To give eventlet's WebSocket
            # module access to this socket when running under gunicorn, here we
            # copy the socket to the eventlet format.
            class Input(object):
                def __init__(self, socket):
                    self.socket = socket

                def get_socket(self):
                    return self.socket

            environ['eventlet.input'] = Input(environ['gunicorn.socket'])

        path = environ['PATH_INFO']
        if path is not None and \
                path.startswith('/{0}/'.format(self.engineio_path)):

            query = urllib.parse.parse_qs(environ.get('QUERY_STRING', ''))
            sid = query.get('sid', None)

            if sid is None:
                self.wsgi_app(environ, start_response)
            
            engineio_res = self.engineio_app.handle_request(environ, start_response)
            return engineio_res

        elif self.wsgi_app is not None:
            return self.wsgi_app(environ, start_response)
        else:
            start_response("404 Not Found", [('Content-type', 'text/plain')])
            return ['Not Found']
