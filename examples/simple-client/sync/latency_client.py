import time
import socketio


def main():
    with socketio.SimpleClient() as sio:
        sio.connect('http://localhost:5000')
        while True:
            start_timer = time.time()
            sio.emit('ping_from_client')
            while sio.receive() != ['pong_from_server']:
                pass
            latency = time.time() - start_timer
            print('latency is {0:.2f} ms'.format(latency * 1000))

            time.sleep(1)


if __name__ == '__main__':
    main()
