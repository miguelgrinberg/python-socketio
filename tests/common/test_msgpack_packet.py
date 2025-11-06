from datetime import datetime, timedelta, timezone

import pytest
import msgpack

from socketio import msgpack_packet
from socketio import packet


class TestMsgPackPacket:
    def test_encode_decode(self):
        p = msgpack_packet.MsgPackPacket(
            packet.CONNECT, data={'auth': {'token': '123'}}, namespace='/foo')
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p.packet_type == p2.packet_type
        assert p.data == p2.data
        assert p.id == p2.id
        assert p.namespace == p2.namespace

    def test_encode_decode_with_id(self):
        p = msgpack_packet.MsgPackPacket(
            packet.EVENT, data=['ev', 42], id=123, namespace='/foo')
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p.packet_type == p2.packet_type
        assert p.data == p2.data
        assert p.id == p2.id
        assert p.namespace == p2.namespace

    def test_encode_binary_event_packet(self):
        p = msgpack_packet.MsgPackPacket(packet.EVENT, data={'foo': b'bar'})
        assert p.packet_type == packet.EVENT
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p2.data == {'foo': b'bar'}

    def test_encode_binary_ack_packet(self):
        p = msgpack_packet.MsgPackPacket(packet.ACK, data={'foo': b'bar'})
        assert p.packet_type == packet.ACK
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p2.data == {'foo': b'bar'}

    def test_encode_with_dumps_default(self):
        def default(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError('Unknown type')

        data = {
            'current': datetime.now(tz=timezone(timedelta(0))),
            'key': 'value',
        }
        p = msgpack_packet.MsgPackPacket.configure(dumps_default=default)(
            data=data)
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p.packet_type == p2.packet_type
        assert p.id == p2.id
        assert p.namespace == p2.namespace
        assert p.data != p2.data

        assert isinstance(p2.data, dict)
        assert 'current' in p2.data
        assert isinstance(p2.data['current'], str)
        assert default(data['current']) == p2.data['current']

        data.pop('current')
        p2_data_without_current = p2.data.copy()
        p2_data_without_current.pop('current')
        assert data == p2_data_without_current

    def test_encode_without_dumps_default(self):
        data = {
            'current': datetime.now(tz=timezone(timedelta(0))),
            'key': 'value',
        }
        p_without_default = msgpack_packet.MsgPackPacket(data=data)
        with pytest.raises(TypeError):
            p_without_default.encode()

    def test_encode_decode_with_ext_hook(self):
        class Custom:
            def __init__(self, value):
                self.value = value

            def __eq__(self, value: object) -> bool:
                return isinstance(value, Custom) and self.value == value.value

        def default(obj):
            if isinstance(obj, Custom):
                return msgpack.ExtType(1, obj.value)
            raise TypeError('Unknown type')

        def ext_hook(code, data):
            if code == 1:
                return Custom(data)
            raise TypeError('Unknown ext type')

        data = {'custom': Custom(b'custom_data'), 'key': 'value'}
        p = msgpack_packet.MsgPackPacket.configure(dumps_default=default)(
            data=data)
        p2 = msgpack_packet.MsgPackPacket.configure(ext_hook=ext_hook)(
            encoded_packet=p.encode()
        )
        assert p.packet_type == p2.packet_type
        assert p.id == p2.id
        assert p.data == p2.data
        assert p.namespace == p2.namespace

    def test_encode_decode_without_ext_hook(self):
        class Custom:
            def __init__(self, value):
                self.value = value

            def __eq__(self, value: object) -> bool:
                return isinstance(value, Custom) and self.value == value.value

        def default(obj):
            if isinstance(obj, Custom):
                return msgpack.ExtType(1, obj.value)
            raise TypeError('Unknown type')

        data = {'custom': Custom(b'custom_data'), 'key': 'value'}
        p = msgpack_packet.MsgPackPacket.configure(dumps_default=default)(
            data=data)
        p2 = msgpack_packet.MsgPackPacket(encoded_packet=p.encode())
        assert p.packet_type == p2.packet_type
        assert p.id == p2.id
        assert p.namespace == p2.namespace
        assert p.data != p2.data

        assert isinstance(p2.data, dict)
        assert 'custom' in p2.data
        assert isinstance(p2.data['custom'], msgpack.ExtType)
        assert p2.data['custom'].code == 1
        assert p2.data['custom'].data == b'custom_data'

        data.pop('custom')
        p2_data_without_custom = p2.data.copy()
        p2_data_without_custom.pop('custom')
        assert data == p2_data_without_custom
