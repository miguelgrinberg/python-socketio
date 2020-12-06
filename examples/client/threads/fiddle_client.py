import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connected to server')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.event
def hello(a, b, c):
    print(a, b, c)


if __name__ == '__main__':
    sio.connect('http://localhost:5000')
    sio.wait()
