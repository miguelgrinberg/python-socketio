import asyncio
import socketio


async def main():
    sio = socketio.AsyncSimpleClient()
    await sio.connect('http://localhost:5000', auth={'token': 'my-token'})
    print(await sio.receive())
    await sio.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
