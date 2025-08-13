#!/usr/bin/env python
import uvicorn
from litestar import Litestar, MediaType, get
from litestar.response import File
from litestar.static_files.config import StaticFilesConfig

import socketio

sio = socketio.AsyncServer(async_mode="asgi")


@get("/", media_type=MediaType.HTML)
async def index() -> File:
    return File("fiddle.html", content_disposition_type="inline")


@get("/hello")
async def hello() -> dict:
    return {"message": "Hello, World!"}


@sio.event
async def connect(sid, environ, auth):
    print(f"connected auth={auth} sid={sid}")
    await sio.emit("hello", (1, 2, {"hello": "you"}), to=sid)


@sio.event
def disconnect(sid):
    print("disconnected", sid)


app = Litestar(
    [index, hello],
    static_files_config=[StaticFilesConfig("static", directories=["static"])],
)
combined_asgi_app = socketio.ASGIApp(sio, app)


if __name__ == "__main__":
    uvicorn.run(combined_asgi_app, host="127.0.0.1", port=5000)
