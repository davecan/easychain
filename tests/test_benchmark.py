# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from easychain.blockchain import (Message,
                                  Block,
                                  Blockchain)

def create_message():
    msg = Message("first data")
    return msg.hash

def create_block():
    block = Block()
    for i in range(5):
        msg = Message("test{}".format(i))
        block.add_message(msg)
    block.validate()
    return block

def create_blockchain():
    chain = Blockchain()
    block = create_block()
    chain.add_block(block)

def test_message_hash(benchmark):
    result = benchmark(create_message)

def test_block(benchmark):
    result = benchmark(create_block)

def test_blockchain(benchmark):
    result = benchmark(create_blockchain)
