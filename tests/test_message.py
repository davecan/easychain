# -*- coding: utf-8 -*-
from __future__ import absolute_import
from easychain.blockchain import (Message,
                                  Block,
                                  Blockchain,
                                  InvalidBlockchain,
                                  InvalidMessage,
                                  bit_encode,
                                  _parse_args)
import unittest
import hashlib
import time
from freezegun import freeze_time


@freeze_time("1955-11-12")
class TestMessage(unittest.TestCase):

    def payload_hash(self, msg):
        payload = _parse_args(msg.timestamp,
                              msg.data,
                              msg.sender,
                              msg.receiver)
        return bit_encode(payload)

    def message_hash(self, msg):
        payload = _parse_args(msg.prev_hash,
                              msg.payload_hash)
        return bit_encode(payload)

    def test_data_message_hashes_only_payload_on_create(self):
        data = "some data"
        msg = Message(data)

        self.assertEqual(msg.data, data)
        self.assertIsNone(msg.sender)
        self.assertIsNone(msg.receiver)
        self.assertIsNotNone(msg.timestamp)
        self.assertEqual(self.payload_hash(msg), msg.payload_hash)

    def test_full_message_hashes_only_payload_on_create(self):
        data = "some data"
        alice = "Alice"
        bob = "Bob"
        msg = Message(data, alice, bob)

        self.assertEqual(msg.data, data)
        self.assertEqual(msg.sender, alice)
        self.assertEqual(msg.receiver, bob)
        self.assertIsNotNone(msg.timestamp)
        self.assertEqual(self.payload_hash(msg), msg.payload_hash)

    def test_linking_populates_prev_hash_correctly(self):
        msg1 = Message("some data")
        msg2 = Message("some more data")
        msg2.link(msg1)

        self.assertEqual(msg2.prev_hash, msg1.hash)

    def test_sealing_unlinked_message_sets_message_hash_correctly(self):
        msg = Message("some data")

        self.assertEqual(self.message_hash(msg), msg.hash)

    def test_sealing_linked_message_sets_message_hash_correctly(self):
        msg1 = Message("some data")

        msg2 = Message("some more data")
        msg2.link(msg1)

        self.assertNotEqual(msg1.hash, msg2.hash)
        self.assertEqual(self.message_hash(msg2), msg2.hash)

    def test_fluent(self):
        msg1 = Message("first message")
        msg2 = Message("second message").link(msg1)

        self.assertEqual("first message", msg1.data)
        self.assertEqual("second message", msg2.data)
        self.assertEqual(msg2.prev_hash, msg1.hash)

    def test_good_unlinked_message_validates(self):
        msg = Message("some data", "Alice", "Bob")
        # sanity check the hashes
        self.assertEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertEqual(self.message_hash(msg), msg.hash)

    def test_good_linked_message_validates(self):
        msg1 = Message("first")
        msg2 = Message("second").link(msg1)
        # sanity check the hashes
        self.assertEqual(self.payload_hash(msg2), msg2.payload_hash)
        self.assertEqual(self.message_hash(msg2), msg2.hash)


if __name__ == '__main__':
    unittest.main()
