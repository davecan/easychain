from blockchain import Message, Block, Blockchain, InvalidBlockchain
import unittest
import hashlib

class TestBlockchain(unittest.TestCase):
    def get_block(self, msg):
        B = Block()
        B.add_message(Message(msg))
        return B

    def get_blocks(self, *args):
        L = []
        for arg in args:
            b = Block()
            b.add_message(Message(arg))
            L.append(b)
        for i, block in enumerate(L):
            block.link(L[i-1]) if i > 0 else None
            block.seal()
        return L

    def test_creation(self):
        chain = Blockchain()
        self.assertEqual([], chain.blocks)

    def test_add_block(self):
        chain = Blockchain()
        chain.add_block(self.get_block("some message"))
        self.assertEqual(1, len(chain.blocks))
        self.assertEqual("some message", chain.blocks[-1].messages[0].data)

    def test_add_multiple_blocks_sets_hashes_correctly(self):
        chain = Blockchain()
        chain.blocks = self.get_blocks("first", "second", "third")

        self.assertEqual(3, len(chain.blocks))
        self.assertEqual("first", chain.blocks[0].messages[0].data)
        self.assertEqual("second", chain.blocks[1].messages[0].data)
        self.assertEqual("third", chain.blocks[2].messages[0].data)
        self.assertIsNotNone(chain.blocks[-1].hash)
        self.assertEqual(chain.blocks[1].prev_hash, chain.blocks[0].hash)
        self.assertEqual(chain.blocks[2].prev_hash, chain.blocks[1].hash)

    def test_invalid_block_breaks_chain(self):
        chain = Blockchain()
        chain.blocks = self.get_blocks("first", "second", "third", "fourth", "fifth")
        chain.blocks[1].messages[0].data = "changed"
        self.assertRaises(InvalidBlockchain, chain.validate)

    

        
if __name__ == '__main__':
    unittest.main()