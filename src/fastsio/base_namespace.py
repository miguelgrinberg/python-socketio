from typing import Any, Optional


class BaseNamespace:
    def __init__(self, namespace: Optional[str] = None):
        self.namespace: str = namespace or "/"

    def is_asyncio_based(self) -> bool:
        return False


class BaseServerNamespace(BaseNamespace):
    def __init__(self, namespace: Optional[str] = None):
        super().__init__(namespace=namespace)
        self.server: Any = None

    def _set_server(self, server: Any) -> None:
        self.server = server

    def rooms(self, sid: str, namespace: Optional[str] = None):
        """Return the rooms a client is in.

        The only difference with the :func:`socketio.Server.rooms` method is
        that when the ``namespace`` argument is not given the namespace
        associated with the class is used.
        """
        return self.server.rooms(sid, namespace=namespace or self.namespace)


class BaseClientNamespace(BaseNamespace):
    def __init__(self, namespace: Optional[str] = None):
        super().__init__(namespace=namespace)
        self.client: Any = None

    def _set_client(self, client: Any) -> None:
        self.client = client
