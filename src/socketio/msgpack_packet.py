__all__ = ["MsgPackPacket"]

import datetime
import msgpack
from . import packet

def _default(o):
    if isinstance(o, datetime.datetime):
        return msgpack.Timestamp.from_datetime(o)
    elif isinstance(o, datetime.date):
        dt = datetime.datetime.combine(o, datetime.time(), datetime.timezone.utc)
        return msgpack.Timestamp.from_datetime(dt)
    elif isinstance(o, datetime.time):
        return o.isoformat()
    return o

class MsgPackPacket(packet.Packet):
    uses_binary_events = False

    def encode(self):
        """Encode the packet for transmission."""
        return msgpack.dumps(self._to_dict(), default=_default, datetime=True)  # True - convert datetime with timezone to timestamp

    def decode(self, encoded_packet):
        """Decode a transmitted package."""
        decoded = msgpack.loads(encoded_packet, timestamp=3)  # 3 - convert timestamp to datetime
        self.packet_type = decoded['type']
        self.data = decoded.get('data')
        self.id = decoded.get('id')
        self.namespace = decoded['nsp']
