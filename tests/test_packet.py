import unittest

import six

from socketio import packet


class TestPacket(unittest.TestCase):
    def test_encode_default_packet(self):
        pkt = packet.Packet()
        self.assertEqual(pkt.packet_type, packet.EVENT)
        self.assertIsNone(pkt.data)
        self.assertIsNone(pkt.namespace)
        self.assertIsNone(pkt.id)
        self.assertEqual(pkt.attachment_count, 0)
        self.assertEqual(pkt.encode(), '2')

    def test_decode_default_packet(self):
        pkt = packet.Packet(encoded_packet='2')
        self.assertTrue(pkt.encode(), '2')

    def test_encode_text_event_packet(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data=[six.text_type('foo')])
        self.assertEqual(pkt.packet_type, packet.EVENT)
        self.assertEqual(pkt.data, ['foo'])
        self.assertEqual(pkt.encode(), '2["foo"]')

    def test_decode_text_event_packet(self):
        pkt = packet.Packet(encoded_packet='2["foo"]')
        self.assertEqual(pkt.packet_type, packet.EVENT)
        self.assertEqual(pkt.data, ['foo'])
        self.assertEqual(pkt.encode(), '2["foo"]')

    def test_decode_empty_event_packet(self):
        pkt = packet.Packet(encoded_packet='1')
        self.assertEqual(pkt.packet_type, packet.DISCONNECT)
        # same thing, but with a numeric payload
        pkt = packet.Packet(encoded_packet=1)
        self.assertEqual(pkt.packet_type, packet.DISCONNECT)

    def test_encode_binary_event_packet(self):
        pkt = packet.Packet(packet_type=packet.EVENT, data=b'1234')
        self.assertEqual(pkt.packet_type, packet.BINARY_EVENT)
        self.assertEqual(pkt.data, b'1234')
        a = ['51-{"_placeholder":true,"num":0}', b'1234']
        b = ['51-{"num":0,"_placeholder":true}', b'1234']
        encoded_packet = pkt.encode()
        self.assertTrue(encoded_packet == a or encoded_packet == b)

    def test_decode_binary_event_packet(self):
        pkt = packet.Packet(encoded_packet='51-{"_placeholder":true,"num":0}')
        self.assertTrue(pkt.add_attachment(b'1234'))
        self.assertEqual(pkt.packet_type, packet.BINARY_EVENT)
        self.assertEqual(pkt.data, b'1234')

    def test_encode_text_ack_packet(self):
        pkt = packet.Packet(packet_type=packet.ACK,
                            data=[six.text_type('foo')])
        self.assertEqual(pkt.packet_type, packet.ACK)
        self.assertEqual(pkt.data, ['foo'])
        self.assertEqual(pkt.encode(), '3["foo"]')

    def test_decode_text_ack_packet(self):
        pkt = packet.Packet(encoded_packet='3["foo"]')
        self.assertEqual(pkt.packet_type, packet.ACK)
        self.assertEqual(pkt.data, ['foo'])
        self.assertEqual(pkt.encode(), '3["foo"]')

    def test_encode_binary_ack_packet(self):
        pkt = packet.Packet(packet_type=packet.ACK, data=b'1234')
        self.assertEqual(pkt.packet_type, packet.BINARY_ACK)
        self.assertEqual(pkt.data, b'1234')
        a = ['61-{"_placeholder":true,"num":0}', b'1234']
        b = ['61-{"num":0,"_placeholder":true}', b'1234']
        encoded_packet = pkt.encode()
        self.assertTrue(encoded_packet == a or encoded_packet == b)

    def test_decode_binary_ack_packet(self):
        pkt = packet.Packet(encoded_packet='61-{"_placeholder":true,"num":0}')
        self.assertTrue(pkt.add_attachment(b'1234'))
        self.assertEqual(pkt.packet_type, packet.BINARY_ACK)
        self.assertEqual(pkt.data, b'1234')

    def test_invalid_binary_packet(self):
        self.assertRaises(ValueError, packet.Packet, packet_type=packet.ERROR,
                          data=b'123')

    def test_encode_namespace(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data=[six.text_type('foo')], namespace='/bar')
        self.assertEqual(pkt.namespace, '/bar')
        self.assertEqual(pkt.encode(), '2/bar,["foo"]')

    def test_decode_namespace(self):
        pkt = packet.Packet(encoded_packet='2/bar,["foo"]')
        self.assertEqual(pkt.namespace, '/bar')
        self.assertEqual(pkt.encode(), '2/bar,["foo"]')

    def test_encode_namespace_no_data(self):
        pkt = packet.Packet(packet_type=packet.EVENT, namespace='/bar')
        self.assertEqual(pkt.encode(), '2/bar')

    def test_decode_namespace_no_data(self):
        pkt = packet.Packet(encoded_packet='2/bar')
        self.assertEqual(pkt.namespace, '/bar')
        self.assertEqual(pkt.encode(), '2/bar')

    def test_encode_namespace_with_hyphens(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data=[six.text_type('foo')], namespace='/b-a-r')
        self.assertEqual(pkt.namespace, '/b-a-r')
        self.assertEqual(pkt.encode(), '2/b-a-r,["foo"]')

    def test_decode_namespace_with_hyphens(self):
        pkt = packet.Packet(encoded_packet='2/b-a-r,["foo"]')
        self.assertEqual(pkt.namespace, '/b-a-r')
        self.assertEqual(pkt.encode(), '2/b-a-r,["foo"]')

    def test_encode_id(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data=[six.text_type('foo')], id=123)
        self.assertEqual(pkt.id, 123)
        self.assertEqual(pkt.encode(), '2123["foo"]')

    def test_decode_id(self):
        pkt = packet.Packet(encoded_packet='2123["foo"]')
        self.assertEqual(pkt.id, 123)
        self.assertEqual(pkt.encode(), '2123["foo"]')

    def test_encode_namespace_and_id(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data=[six.text_type('foo')], namespace='/bar',
                            id=123)
        self.assertEqual(pkt.namespace, '/bar')
        self.assertEqual(pkt.id, 123)
        self.assertEqual(pkt.encode(), '2/bar,123["foo"]')

    def test_decode_namespace_and_id(self):
        pkt = packet.Packet(encoded_packet='2/bar,123["foo"]')
        self.assertEqual(pkt.namespace, '/bar')
        self.assertEqual(pkt.id, 123)
        self.assertEqual(pkt.encode(), '2/bar,123["foo"]')

    def test_encode_many_binary(self):
        pkt = packet.Packet(packet_type=packet.EVENT,
                            data={'a': six.text_type('123'),
                                  'b': b'456',
                                  'c': [b'789', 123]})
        self.assertEqual(pkt.packet_type, packet.BINARY_EVENT)
        ep = pkt.encode()
        self.assertEqual(len(ep), 3)
        self.assertIn(b'456', ep)
        self.assertIn(b'789', ep)

    def test_encode_many_binary_ack(self):
        pkt = packet.Packet(packet_type=packet.ACK,
                            data={'a': six.text_type('123'),
                                  'b': b'456',
                                  'c': [b'789', 123]})
        self.assertEqual(pkt.packet_type, packet.BINARY_ACK)
        ep = pkt.encode()
        self.assertEqual(len(ep), 3)
        self.assertIn(b'456', ep)
        self.assertIn(b'789', ep)

    def test_decode_many_binary(self):
        pkt = packet.Packet(encoded_packet=(
            '52-{"a":"123","b":{"_placeholder":true,"num":0},'
            '"c":[{"_placeholder":true,"num":1},123]}'))
        self.assertFalse(pkt.add_attachment(b'456'))
        self.assertTrue(pkt.add_attachment(b'789'))
        self.assertEqual(pkt.packet_type, packet.BINARY_EVENT)
        self.assertEqual(pkt.data['a'], '123')
        self.assertEqual(pkt.data['b'], b'456')
        self.assertEqual(pkt.data['c'], [b'789', 123])

    def test_decode_many_binary_ack(self):
        pkt = packet.Packet(encoded_packet=(
            '62-{"a":"123","b":{"_placeholder":true,"num":0},'
            '"c":[{"_placeholder":true,"num":1},123]}'))
        self.assertFalse(pkt.add_attachment(b'456'))
        self.assertTrue(pkt.add_attachment(b'789'))
        self.assertEqual(pkt.packet_type, packet.BINARY_ACK)
        self.assertEqual(pkt.data['a'], '123')
        self.assertEqual(pkt.data['b'], b'456')
        self.assertEqual(pkt.data['c'], [b'789', 123])

    def test_decode_too_many_binary_packets(self):
        pkt = packet.Packet(encoded_packet=(
            '62-{"a":"123","b":{"_placeholder":true,"num":0},'
            '"c":[{"_placeholder":true,"num":1},123]}'))
        self.assertFalse(pkt.add_attachment(b'456'))
        self.assertTrue(pkt.add_attachment(b'789'))
        self.assertRaises(ValueError, pkt.add_attachment, b'123')

    def test_data_is_binary_list(self):
        pkt = packet.Packet()
        self.assertFalse(pkt._data_is_binary([six.text_type('foo')]))
        self.assertFalse(pkt._data_is_binary([]))
        self.assertTrue(pkt._data_is_binary([b'foo']))
        self.assertTrue(pkt._data_is_binary([six.text_type('foo'), b'bar']))

    def test_data_is_binary_dict(self):
        pkt = packet.Packet()
        self.assertFalse(pkt._data_is_binary({'a': six.text_type('foo')}))
        self.assertFalse(pkt._data_is_binary({}))
        self.assertTrue(pkt._data_is_binary({'a': b'foo'}))
        self.assertTrue(pkt._data_is_binary({'a': six.text_type('foo'),
                                             'b': b'bar'}))
