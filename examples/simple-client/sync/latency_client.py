import time
import socketio


def main():
    sio = socketio.SimpleClient()
    sio.connect('http://localhost:5000')

    try:
        while True:
            start_timer = time.time()
            sio.emit('ping_from_client')
            while sio.receive() != ['pong_from_server']:
                pass
            latency = time.time() - start_timer
            print('latency is {0:.2f} ms'.format(latency * 1000))

            time.sleep(1)
    except KeyboardInterrupt:
        sio.disconnect()


if __name__ == '__main__':
    main()
