# easychain: a simple python blockchain

This is the result of a bit of research and some tinkering to understand the fundamental concepts of a blockchain. Readers are directed to Ilya Gritorik's fantastic [Minimum Viable Blockchain](https://www.igvita.com/2014/05/05/minimum-viable-block-chain/) article for more general information about what blockchains are and how they work conceptually.

This implementation focuses *only* on the hashed ledger concept. It specifically does not include any concept of mining or any other form of 
distributed consensus. It also abstracts the concept of a transaction to that of a message in general. The concept of a header and payload in messages and blocks is adapted from Bitcoin.

I do not pretend to be a python expert, so some of this can certainly be written better.

# Example

This is a quick example. A more detailed example (including hostile tampering and detection) is in `example.py`. There are also a few basic unit tests.

    msg1 = Message("simple message")
    msg2 = Message("with a sender and receiver", "Alice", "Bob")
    
    # each of the above now has a hashed payload, link them by adding to a block

    block1 = Block()
    block1.add_message(msg1)
    block1.add_message(msg2)

    # or using the constructor

    block1 = Block(msg1, msg2)

    # messages are now fully hashed and linked, msg2 depends on msg1, tampering can be detected

    block2 = Block()
    block2.add_message(Message("just need a second block for an example"))

    # now link the blocks together

    chain = Blockchain()
    chain.add_block(block1)
    chain.add_block(block2)

    # now the blocks are linked, block2 depends on block1

# Classes

Conceptually it works somewhat like this image from [Satoshi Nakamoto's original Bitcoin paper](https://bitcoin.org/bitcoin.pdf). (incidentally if you haven't read it, its utterly brilliant, only nine pages, and much more approachable than you think)

![simplified bitcoin blockchain](https://i.imgur.com/hZObTJN.png)

A `Message` ("transaction/item" in Bitcoin/etc) is simply some data, an optional sender and receiver, and some metadata (timestamp and data size), which is then hashed together for integrity. A message has two sections -- a *header* and a *payload*. Each section is managed and hashed separately. First, the payload is populated and hashed when the message is created. Later, when the message is eventually added to a block, the header is finalized and the entire message is then hashed. The block will then link the messages (by populating the current message's `prev_hash` field with the last message's hash, unless it is the first message), seal the message, and validate it. Calling `seal` computes the message's hash from a combination of its payload hash and `prev_hash` value. (You can manually `link` and `seal` messages together, but the `Block` will handle this for you.) From this point any tampering of the message, or of any previous message, can be easily detected by recalculating hashes. `validate` will verify the message integrity. (It won't verify the `prev_hash` comes from the prior message, that is the responsibility of the block.)

A `Block` consists of 1..m `Message` objects linked together in a sequential chain. As each message is added to the block that message's `prev_hash` field is updated with the hash from the last message in the block. When no more messages are added and the block is eventually added to the blockchain it is linked to the previous block, sealed, and validated. (Again you can do this manually, but the `Blockchain` handles it automatically) When sealing, the most-recent message hash is pulled and combined with the block's `prev_hash` and the current timestamp. Only the most-recent message hash is required, since it transitively includes all prior messages in the block due to the message chaining described above. Once it is sealed and the block hash has been computed, tampering of any message in the block is detected by recomputing the block hash and comparing expected vs. actual. `validate` will verify block integrity by calling `validate` on each message in sequence, but as with messages it won't verify inter-block links are valid, the blockchain is responsible for that.

A `Blockchain` consists of 1..m `Block` objectss linked together just like `Message` objects are. Once the block is added it is linked to the previous block and sealed. This sequence of hashed blocks forms the "block chain." The integrity of the entire chain can be checked at any time by calling `validate` which calls `validate` on each block in sequence.