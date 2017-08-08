from blockchain import Message, Block, InvalidBlock, InvalidMessage
import unittest
import hashlib

class TestBlock(unittest.TestCase):
    def get_messages(self, *args):
        L = []
        for arg in args:
            L.append(Message(arg).seal())
        for i, msg in enumerate(L):
            msg.link(L[i-1]) if i > 0 else None
            msg.seal()
            msg.validate()
        return L

    def block_hash(self, block):
        return hashlib.sha256(bytearray(str(block.prev_hash) + str(block.timestamp) + block.messages[-1].hash, "utf-8")).hexdigest()

    def payload_hash(self, msg):
        return hashlib.sha256(bytearray(str(msg.timestamp) + str(msg.data) + str(msg.sender) + str(msg.receiver), "utf-8")).hexdigest()

    def message_hash(self, msg, new_payload_hash=None):
        payload_hash = new_payload_hash or msg.payload_hash
        return hashlib.sha256(bytearray(str(msg.prev_hash) + payload_hash, "utf-8")).hexdigest()

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
        block.seal()
        self.assertEqual(self.block_hash(block), block.hash)

    def test_sealing_linked_block_sets_hashes_correctly(self):
        block1 = Block()
        block1.messages = self.get_messages("first", "second", "third")
        block1.seal()

        block2 = Block()
        block2.messages = self.get_messages("fourth", "fifth")
        block2.link(block1)
        block2.seal()

        self.assertEqual(self.block_hash(block2), block2.hash)
        self.assertEqual(block2.prev_hash, block1.hash)

    # def test_message_tampering_invalidates_block_hash(self):
    #     block = Block()
    #     block.messages = self.get_messages("first")
    #     block.messages[0].data = "changed"
    #     self.assertNotEqual(self.block_hash(block), block.hash)

    # def test_message_tampering_invalidates_next_message_hash(self):
    #     block = Block()
    #     block.messages = self.get_messages("first", "second")
    #     block.messages[0].data = "changed"
    #     self.assertNotEqual(self.)

    def test_message_tampering_invalidates_block(self):
        block = Block()
        block.messages = self.get_messages("first", "second", "third", "fourth", "fifth")
        block.messages[1].data = "changed"
        self.assertRaises(InvalidBlock, block.validate)


if __name__ == '__main__':
    unittest.main()