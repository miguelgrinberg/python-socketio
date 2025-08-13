from fastsio import RouterSIO

router = RouterSIO(namespace="/app")

@router.on("connect", namespace="/room") # override router namespace
async def on_connect(sid, environ):
    print("connect ", sid)

@router.on("disconnect")
async def on_disconnect(sid):
    print("disconnect ", sid)

@router.on("message")
async def on_message(sid, data):
    print("message ", data)

