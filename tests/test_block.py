# -*- coding: utf-8 -*-
from __future__ import absolute_import
from easychain.blockchain import (Message,
                                  Block,
                                  InvalidBlock,
                                  InvalidMessage,
                                  bit_encode,
                                  _parse_args)
import unittest
import hashlib
from freezegun import freeze_time


@freeze_time("1955-11-12")
class TestBlock(unittest.TestCase):

    def get_messages(self, *args):
        content = []
        last_msg = None
        for arg in args:
            msg = Message(arg)
            content.append(msg)
            if last_msg:
                msg.link(last_msg)
            last_msg = msg
        return content

    def block_hash(self, block):
        payload = _parse_args(block.prev_hash, block.timestamp, block.messages[-1].hash)
        return bit_encode(payload)

    def payload_hash(self, msg):
        payload = _parse_args(msg.timestamp, msg.data, msg.sender, msg.receiver)
        return bit_encode(payload)

    def message_hash(self, msg, new_payload_hash=None):
        payload_hash = new_payload_hash or msg.payload_hash
        payload = _parse_args(msg.prev_hash, payload_hash)
        return bit_encode(payload)

    def test_block_unhashed_at_creation(self):
        block = Block()
        self.assertIsNone(block.hash)

    def test_constructor_appends_and_links_messages(self):
        block = Block(Message("first"), Message("second"), Message("third"))
        self.assertEqual(3, len(block.messages))
        self.assertEqual(block.messages[0].hash, block.messages[1].prev_hash)
        self.assertEqual(block.messages[1].hash, block.messages[2].prev_hash)
        self.assertEqual("first", block.messages[0].data)
        self.assertEqual("second", block.messages[1].data)
        self.assertEqual("third", block.messages[2].data)

    def test_add_message_appends_and_links_message(self):
        msg = Message("test")
        block = Block()
        block.add_message(msg)
        self.assertEqual(1, len(block.messages))
        self.assertEqual(msg, block.messages[0])

    def test_adding_messages_links_them_correctly(self):
        msg1 = Message("first")
        msg2 = Message("second")
        block = Block()
        block.add_message(msg1)
        block.add_message(msg2)
        self.assertEqual(msg2.prev_hash, msg1.hash)

    def test_sealing_unlinked_block_sets_hashes_correctly(self):
        block = Block()
        block.messages = self.get_messages("first", "second")
        self.assertEqual(self.block_hash(block), block.hash)

    def test_sealing_linked_block_sets_hashes_correctly(self):
        block1 = Block()
        block1.messages = self.get_messages("first", "second", "third")

        block2 = Block()
        block2.messages = self.get_messages("fourth", "fifth")
        block2.link(block1)

        self.assertEqual(self.block_hash(block2), block2.hash)
        self.assertEqual(block2.prev_hash, block1.hash)

    def test_message_tampering_invalidates_block(self):
        block = Block()
        block.messages = self.get_messages(
            "first", "second", "third", "fourth", "fifth")
        block.messages[1].data = "changed"
        self.assertTrue(block.validate())

    def test_auto_recreate_hashs(self):
        block = Block()
        block.messages = self.get_messages(
            "first", "second", "third", "fourth", "fifth")

        old_hashs = set([i.hash for i in block.messages])

        block.messages[1].data = "changed"
        new_hashs = set([i.hash for i in block.messages])
        self.assertNotEqual(old_hashs, new_hashs)


if __name__ == '__main__':
    unittest.main()
