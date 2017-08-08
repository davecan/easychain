from blockchain import Message, InvalidMessage
import unittest
import hashlib
import time

class TestMessage(unittest.TestCase):
    
    def payload_hash(self, msg):
        return hashlib.sha256(bytearray(str(msg.timestamp) + str(msg.data) + str(msg.sender) + str(msg.receiver), "utf-8")).hexdigest()

    def message_hash(self, msg):
        return hashlib.sha256(bytearray(str(msg.prev_hash) + msg.payload_hash, "utf-8")).hexdigest()

    def test_data_message_hashes_only_payload_on_create(self):
        data = "some data"
        msg = Message(data)

        self.assertEqual(msg.data, data)
        self.assertIsNone(msg.sender)
        self.assertIsNone(msg.receiver)
        self.assertIsNotNone(msg.timestamp)
        self.assertEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertIsNone(msg.hash)

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
        self.assertIsNone(msg.hash)

    def test_tampering_invalidates_payload_hash(self):
        msg = Message("some data", "Alice", "Bob")
        msg.receiver = "Eve"

        self.assertNotEqual(self.payload_hash(msg), msg.payload_hash)

    def test_linking_populates_prev_hash_correctly(self):
        msg1 = Message("some data")
        msg2 = Message("some more data")
        msg2.link(msg1)

        self.assertEqual(msg2.prev_hash, msg1.hash)
        self.assertIsNone(msg2.hash)

    def test_sealing_unlinked_message_sets_message_hash_correctly(self):
        msg = Message("some data")
        self.assertIsNone(msg.hash)

        msg.seal()
        self.assertEqual(self.message_hash(msg), msg.hash)

    def test_sealing_linked_message_sets_message_hash_correctly(self):
        msg1 = Message("some data")
        msg1.seal()
        
        msg2 = Message("some more data")
        msg2.link(msg1)
        msg2.seal()

        self.assertNotEqual(msg1.hash, msg2.hash)
        self.assertEqual(self.message_hash(msg2), msg2.hash)

    def test_fluent(self):
        msg1 = Message("first message").seal()
        msg2 = Message("second message").link(msg1).seal()
        
        self.assertEqual("first message", msg1.data)
        self.assertEqual("second message", msg2.data)
        self.assertEqual(msg2.prev_hash, msg1.hash)

    def test_good_unlinked_message_validates(self):
        msg = Message("some data", "Alice", "Bob").seal()
        msg.validate()  # no exceptions raised
        # sanity check the hashes
        self.assertEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertEqual(self.message_hash(msg), msg.hash)

    def test_good_linked_message_validates(self):
        msg1 = Message("first").seal()
        msg2 = Message("second").link(msg1).seal()
        msg2.validate()  # no exceptions raised
        # sanity check the hashes
        self.assertEqual(self.payload_hash(msg2), msg2.payload_hash)
        self.assertEqual(self.message_hash(msg2), msg2.hash)

    def test_tampering_invalidates_hashes(self):
        msg = Message("some data")
        msg.data = "more data"
        self.assertNotEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertNotEqual(self.message_hash(msg), msg.hash)

        msg = Message("some data", "Alice", "Bob")
        msg.receiver = "Eve"
        self.assertNotEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertNotEqual(self.message_hash(msg), msg.hash)

        msg = Message("some data", "Alice", "Bob")
        msg.sender = "Charlie"
        self.assertNotEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertNotEqual(self.message_hash(msg), msg.hash)

        msg = Message("some data")
        msg.timestamp = time.time() + 100   # force different time
        self.assertNotEqual(self.payload_hash(msg), msg.payload_hash)
        self.assertNotEqual(self.message_hash(msg), msg.hash)

    def test_message_tampering_implies_validation_exception(self):
        msg = Message("first").seal()
        msg.data = "changed"
        self.assertRaises(InvalidMessage, msg.validate)



if __name__ == '__main__':
    unittest.main()