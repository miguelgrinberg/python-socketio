import socketio


def main():
    sio = socketio.SimpleClient()
    sio.connect('http://localhost:5000', auth={'token': 'my-token'})
    print(sio.receive())
    sio.disconnect()


if __name__ == '__main__':
    main()
