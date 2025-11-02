import msgpack
from . import packet


class MsgPackPacket(packet.Packet):
    uses_binary_events = False

    def __init__(
        self,
        packet_type=packet.EVENT,
        data=None,
        namespace=None,
        id=None,
        binary=None,
        encoded_packet=None,
        dumps_default=None,
        ext_hook=None,
    ):
        super().__init__(
            packet_type, data, namespace, id, binary, encoded_packet
        )
        self.dumps_default = dumps_default
        self.ext_hook = ext_hook

    def encode(self):
        """Encode the packet for transmission."""
        return msgpack.dumps(self._to_dict(), default=self.dumps_default)

    def decode(self, encoded_packet):
        """Decode a transmitted package."""
        if self.ext_hook is None:
            decoded = msgpack.loads(encoded_packet)
        else:
            decoded = msgpack.loads(encoded_packet, ext_hook=self.ext_hook)
        self.packet_type = decoded['type']
        self.data = decoded.get('data')
        self.id = decoded.get('id')
        self.namespace = decoded['nsp']
