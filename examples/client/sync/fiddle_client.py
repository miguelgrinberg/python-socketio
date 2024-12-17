import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connected to server')


@sio.event
def disconnect(reason):
    print('disconnected from server, reason:', reason)


@sio.event
def hello(a, b, c):
    print(a, b, c)


if __name__ == '__main__':
    sio.connect('http://localhost:5000', auth={'token': 'my-token'})
    sio.wait()
