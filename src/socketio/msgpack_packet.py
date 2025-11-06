import logging
import msgpack
from . import packet

logger = logging.getLogger('socketio')


class MsgPackPacket(packet.Packet):
    uses_binary_events = False

    def encode(self):
        """Encode the packet for transmission."""
        return self._encode()

    def _encode(self, **kwargs):
        return _msgpack.dumps(self._to_dict(), **kwargs)

    def decode(self, encoded_packet):
        """Decode a transmitted package."""
        return self._decode(encoded_packet)

    def _decode(self, encoded_packet, **kwargs):
        decoded = msgpack.loads(encoded_packet, **kwargs)
        self.packet_type = decoded['type']
        self.data = decoded.get('data')
        self.id = decoded.get('id')
        self.namespace = decoded['nsp']

    @classmethod
    def _configure(cls, *args, **kwargs):
        dumps_default = kwargs.pop('dumps_default', None)
        ext_hook = kwargs.pop('ext_hook', msgpack.ExtType)

        if args:
            logger.warning(
                'Some positional arguments to MsgPackPacket.configure() are '
                'not used: %s',
                args,
            )
        if kwargs:
            logger.warning(
                'Some keyword arguments to MsgPackPacket.configure() are '
                'not used: %s',
                kwargs,
            )

        class ConfiguredMsgPackPacket(cls):
            def _encode(self, **kwargs):
                kwargs.setdefault('default', dumps_default)
                return super()._encode(**kwargs)

            def _decode(self, encoded_packet, **kwargs):
                kwargs.setdefault('ext_hook', ext_hook)
                return super()._decode(encoded_packet, **kwargs)

        return ConfiguredMsgPackPacket
