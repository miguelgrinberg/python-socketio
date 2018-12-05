import sys

from .base_manager import BaseManager
from .pubsub_manager import PubSubManager
from .kombu_manager import KombuManager
from .redis_manager import RedisManager
from .zmq_manager import ZmqManager
from .server import Server
from .namespace import Namespace
from .middleware import WSGIApp, Middleware
from .tornado import get_tornado_handler
if sys.version_info >= (3, 5):  # pragma: no cover
    from .asyncio_server import AsyncServer
    from .asyncio_manager import AsyncManager
    from .asyncio_namespace import AsyncNamespace
    from .asyncio_redis_manager import AsyncRedisManager
    from .asgi import ASGIApp
else:  # pragma: no cover
    AsyncServer = None
    AsyncManager = None
    AsyncNamespace = None
    AsyncRedisManager = None

__version__ = '2.1.1'

__all__ = ['__version__', 'Server', 'BaseManager', 'PubSubManager',
           'KombuManager', 'RedisManager', 'ZmqManager', 'Namespace',
           'WSGIApp', 'Middleware']
if AsyncServer is not None:  # pragma: no cover
    __all__ += ['AsyncServer', 'AsyncNamespace', 'AsyncManager',
                'AsyncRedisManager', 'ASGIApp', 'get_tornado_handler']
