import asyncio
import time
import socketio


async def main():
    async with socketio.AsyncSimpleClient() as sio:
        await sio.connect('http://localhost:5000')
        while True:
            start_timer = time.time()
            await sio.emit('ping_from_client')
            while (await sio.receive()) != ['pong_from_server']:
                pass
            latency = time.time() - start_timer
            print('latency is {0:.2f} ms'.format(latency * 1000))

            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
