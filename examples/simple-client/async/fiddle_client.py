import asyncio
import socketio


async def main():
    async with socketio.AsyncSimpleClient() as sio:
        await sio.connect('http://localhost:5000', auth={'token': 'my-token'})
        print(await sio.receive())


if __name__ == '__main__':
    asyncio.run(main())
