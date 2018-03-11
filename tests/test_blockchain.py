# -*- coding: utf-8 -*-
from __future__ import absolute_import
from easychain.blockchain import Message, Block, Blockchain, InvalidBlockchain
import unittest
import hashlib
from freezegun import freeze_time


@freeze_time("1955-11-12")
class TestBlockchain(unittest.TestCase):

    def get_block(self, msg):
        block = Block()
        block.add_message(Message(msg))
        return block

    def get_blocks(self, *args):
        content = []
        last_block = None
        for arg in args:
            block = Block()
            block.add_message(Message(arg))

            if last_block:
                block.link(last_block)

            last_block = block
            content.append(block)
        return content

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
        chain.blocks = self.get_blocks(
            "first", "second", "third", "fourth", "fifth")
        chain.blocks[1].messages[0].data = "changed"
        self.assertTrue(chain.validate())

    def test_auto_recreate_blocks(self):
        chain = Blockchain()
        chain.blocks = self.get_blocks(
            "first", "second", "third", "fourth", "fifth")

        old_hashs = set([i.hash for i in chain.blocks])
        chain.blocks[1].messages[0].data = "changed"
        new_hashs = set([i.hash for i in chain.blocks])
        self.assertNotEqual(old_hashs, new_hashs)


if __name__ == '__main__':
    unittest.main()
