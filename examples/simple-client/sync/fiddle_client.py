import socketio


def main():
    with socketio.SimpleClient() as sio:
        sio.connect('http://localhost:5000', auth={'token': 'my-token'})
        print(sio.receive())


if __name__ == '__main__':
    main()
