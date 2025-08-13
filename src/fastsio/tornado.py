from typing import Any

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false

try:
    from engineio.async_drivers.tornado import (
        get_tornado_handler as get_engineio_handler,
    )
except ImportError:  # pragma: no cover
    get_engineio_handler = None  # type: ignore[assignment]


def get_tornado_handler(socketio_server: Any) -> Any:  # pragma: no cover
    # engineio handler factory expects an Engine.IO server instance
    if get_engineio_handler is None:
        raise RuntimeError("Tornado async driver is not available")
    return get_engineio_handler(socketio_server.eio)  # type: ignore[operator]
