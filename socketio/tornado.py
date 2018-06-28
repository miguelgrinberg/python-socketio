import sys
if sys.version_info >= (3, 5):
    from engineio.async_tornado import get_tornado_handler as \
        get_engineio_handler


def get_tornado_handler(socketio_server):
    return get_engineio_handler(socketio_server.eio)
