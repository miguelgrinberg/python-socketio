import threading
import time
from socketserver import ThreadingMixIn
from wsgiref.simple_server import make_server, WSGIServer, WSGIRequestHandler
import requests
import socketio


class SocketIOWebServer:
    """A simple web server used for running Socket.IO servers in tests.

    :param sio: a Socket.IO server instance.

    Note 1: This class is not production-ready and is intended for testing.
    Note 2: This class only supports the "threading" async_mode, with WebSocket
    support provided by the simple-websocket package.
    """
    def __init__(self, sio):
        if sio.async_mode != 'threading':
            raise ValueError('The async_mode must be "threading"')

        def http_app(environ, start_response):
            start_response('200 OK', [('Content-Type', 'text/plain')])
            return [b'OK']

        self.sio = sio
        self.app = socketio.WSGIApp(sio, http_app)
        self.httpd = None
        self.thread = None

    def start(self, port=8900):
        """Start the web server.

        :param port: the port to listen on. Defaults to 8900.

        The server is started in a background thread.
        """
        class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
            pass

        class WebSocketRequestHandler(WSGIRequestHandler):
            def get_environ(self):
                env = super().get_environ()

                # pass the raw socket to the WSGI app so that it can be used
                # by WebSocket connections (hack copied from gunicorn)
                env['gunicorn.socket'] = self.connection
                return env

        self.httpd = make_server('', port, self._app_wrapper,
                                 ThreadingWSGIServer, WebSocketRequestHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()

        # wait for the server to start
        while True:
            try:
                r = requests.get(f'http://localhost:{port}/')
                r.raise_for_status()
                if r.text == 'OK':
                    break
            except:
                time.sleep(0.1)

    def stop(self):
        """Stop the web server."""
        self.sio.shutdown()
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join()
        self.httpd = None
        self.thread = None

    def _app_wrapper(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except StopIteration:
            # end the WebSocket request without sending a response
            # (this is a hack that was copied from gunicorn's threaded worker)
            start_response('200 OK', [])
            return []
