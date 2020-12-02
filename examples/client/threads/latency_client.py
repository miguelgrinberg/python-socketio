import time
import socketio

sio = socketio.Client(logger=True, engineio_logger=True)
start_timer = None


def send_ping():
    global start_timer
    start_timer = time.time()
    sio.emit('ping_from_client')


@sio.event
def connect():
    print('connected to server')
    send_ping()


@sio.event
def pong_from_server():
    global start_timer
    latency = time.time() - start_timer
    print('latency is {0:.2f} ms'.format(latency * 1000))
    sio.sleep(1)
    if sio.connected:
        send_ping()


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.wait()
