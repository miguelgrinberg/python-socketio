import time
from socketio import packet


def test():
    p = packet.Packet(packet.EVENT, {'foo': b'bar'})
    start = time.time()
    count = 0
    while True:
        eps = p.encode()
        p = packet.Packet(encoded_packet=eps[0])
        for ep in eps[1:]:
            p.add_attachment(ep)
        count += 1
        if time.time() - start >= 5:
            break
    return count


if __name__ == '__main__':
    count = test()
    print('binary_packet:', count, 'packets processed.')
