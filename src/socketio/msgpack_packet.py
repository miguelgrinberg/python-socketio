import msgpack
from . import packet


class MsgPackPacket(packet.Packet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.packet_type == packet.BINARY_EVENT:
            self.packet_type = packet.EVENT
        elif self.packet_type == packet.BINARY_ACK:
            self.packet_type = packet.ACK

    def encode(self):
        """Encode the packet for transmission."""
        return msgpack.dumps(self._to_dict())

    def decode(self, encoded_packet):
        """Decode a transmitted package."""
        decoded = msgpack.loads(encoded_packet)
        self.packet_type = decoded['type']
        self.data = decoded['data']
        self.id = decoded.get('id')
        self.namespace = decoded['nsp']
