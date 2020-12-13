import time
import socketio


class Server(socketio.Server):
    def _send_packet(self, eio_sid, pkt):
        pass


def test():
    s = Server()
    start = time.time()
    count = 0
    s._handle_eio_connect('123', 'environ')
    s._handle_eio_message('123', '0')
    while True:
        s.emit('test', 'hello')
        count += 1
        if time.time() - start >= 5:
            break
    return count


if __name__ == '__main__':
    count = test()
    print('server_send:', count, 'packets received.')
