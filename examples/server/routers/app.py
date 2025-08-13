import fastsio
from .routers import router

sio = fastsio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=None,
)

# added all routers
sio.add_router(router=router)

