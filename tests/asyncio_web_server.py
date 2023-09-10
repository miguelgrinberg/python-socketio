import requests
import threading
import time
import uvicorn
import socketio


class SocketIOWebServer:
    """A simple web server used for running Socket.IO servers in tests.

    :param sio: a Socket.IO server instance.

    Note 1: This class is not production-ready and is intended for testing.
    Note 2: This class only supports the "asgi" async_mode.
    """
    def __init__(self, sio, on_shutdown=None):
        if sio.async_mode != 'asgi':
            raise ValueError('The async_mode must be "asgi"')

        async def http_app(scope, receive, send):
            await send({'type': 'http.response.start',
                        'status': 200,
                        'headers': [('Content-Type', 'text/plain')]})
            await send({'type': 'http.response.body',
                        'body': b'OK'})

        self.sio = sio
        self.app = socketio.ASGIApp(sio, http_app, on_shutdown=on_shutdown)
        self.httpd = None
        self.thread = None

    def start(self, port=8900):
        """Start the web server.

        :param port: the port to listen on. Defaults to 8900.

        The server is started in a background thread.
        """
        self.httpd = uvicorn.Server(config=uvicorn.Config(self.app, port=port))
        self.thread = threading.Thread(target=self.httpd.run)
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
        self.httpd.should_exit = True
        self.thread.join()
        self.thread = None
