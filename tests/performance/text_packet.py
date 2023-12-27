import time
from socketio import packet


def test():
    p = packet.Packet(packet.EVENT, "hello")
    start = time.time()
    count = 0
    while True:
        p = packet.Packet(encoded_packet=p.encode())
        count += 1
        if time.time() - start >= 5:
            break
    return count


if __name__ == "__main__":
    count = test()
    print("text_packet:", count, "packets processed.")
