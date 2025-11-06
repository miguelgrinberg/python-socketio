import msgpack
from . import packet


class MsgPackPacket(packet.Packet):
    uses_binary_events = False
    dumps_default = None
    ext_hook = msgpack.ExtType

    @classmethod
    def configure(cls, dumps_default=None, ext_hook=msgpack.ExtType):
        class CustomMsgPackPacket(MsgPackPacket):
            dumps_default = None
            ext_hook = None

        CustomMsgPackPacket.dumps_default = dumps_default
        CustomMsgPackPacket.ext_hook = ext_hook
        return CustomMsgPackPacket

    def encode(self):
        """Encode the packet for transmission."""
        return msgpack.dumps(self._to_dict(),
                             default=self.__class__.dumps_default)

    def decode(self, encoded_packet):
        """Decode a transmitted package."""
        decoded = msgpack.loads(encoded_packet,
                                ext_hook=self.__class__.ext_hook)
        self.packet_type = decoded['type']
        self.data = decoded.get('data')
        self.id = decoded.get('id')
        self.namespace = decoded['nsp']
