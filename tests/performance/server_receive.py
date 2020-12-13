import time
import socketio


def test():
    s = socketio.Server(async_handlers=False)
    start = time.time()
    count = 0
    s._handle_eio_connect('123', 'environ')
    s._handle_eio_message('123', '0')
    while True:
        s._handle_eio_message('123', '2["test","hello"]')
        count += 1
        if time.time() - start >= 5:
            break
    return count


if __name__ == '__main__':
    count = test()
    print('server_receive:', count, 'packets received.')
