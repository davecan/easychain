import hashlib
import time


# TODO: Sender digitally signs payload. (and recipient too?)
class Message:

    def __init__(self, data, sender=None, receiver=None):
        self.hash = None
        self.prev_hash = None
        self.timestamp = time.time()
        self.size = len(data.encode('utf-8'))   # length in bytes
        self.sender = sender
        self.receiver = receiver
        self.data = data
        self.payload_hash = self.__get_payload_hash()

    def __get_payload_hash(self):
        return hashlib.sha256(bytearray(str(self.timestamp) + str(self.data) + str(self.sender) + str(self.receiver), "utf-8")).hexdigest()

    def __get_message_hash(self):
        return hashlib.sha256(bytearray(str(self.prev_hash) + self.payload_hash, "utf-8")).hexdigest()

    def link(self, msg):
        self.prev_hash = msg.hash
        return self

    def seal(self):
        self.hash = self.__get_message_hash()
        return self

    def validate(self):
        if self.payload_hash != self.__get_payload_hash():
            raise InvalidMessage("Invalid payload hash in message: " + str(self))
        if self.hash != self.__get_message_hash():
            raise InvalidMessage("Invalid message hash in message: " + str(self))

    def __repr__(self):
        return 'Message<hash: {}, prev_hash: {}, sender: {}, receiver: {}, data: {}>'.format(
            self.hash, self.prev_hash, self.sender, self.receiver, self.data[:25]
        )



# TODO: Block creator digitally signs the block to seal it.
class Block:

    def __init__(self, *args):
        self.messages = []
        self.timestamp = None
        self.prev_hash = None
        self.hash = None
        if args:
            for arg in args:
                self.add_message(arg)

    def __get_block_hash(self):
        return hashlib.sha256(bytearray(str(self.prev_hash) + str(self.timestamp) + self.messages[-1].hash, "utf-8")).hexdigest()

    def add_message(self, msg):
        if len(self.messages) > 0:
            msg.link(self.messages[-1])
        msg.seal()
        msg.validate()
        self.messages.append(msg)

    # The block hash only needs to incorporate the head message hash, which then transitively includes all prior hashes.
    def link(self, block):
        self.prev_hash = block.hash
        
    def seal(self):
        self.timestamp = time.time()
        self.hash = self.__get_block_hash()

    # Validates each message hash, then chain integrity, then the block hash.
    # Calls each message's validate() method.
    # If a message fails validation, this method captures the exception and 
    # throws InvalidBlock since an invalid message invalidates the whole block.
    def validate(self):
        for i, msg in enumerate(self.messages):
            try:
                msg.validate()
                if i > 0 and msg.prev_hash != self.messages[i-1].hash:
                    raise InvalidBlock("Invalid block: Message #{} has invalid message link in block: {}".format(i, str(self)))
            except InvalidMessage as ex:
                raise InvalidBlock("Invalid block: Message #{} failed validation: {}. In block: {}".format(
                    i, str(ex), str(self))
                )

    def __repr__(self):
        return 'Block<hash: {}, prev_hash: {}, messages: {}, time: {}>'.format(
            self.hash, self.prev_hash, len(self.messages), self.timestamp
        )



class Blockchain:
    
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        if len(self.blocks) > 0:
            block.prev_hash = self.blocks[-1].hash
        block.seal()
        block.validate()
        self.blocks.append(block)

    # Validates each block, in order.
    # An invalid block invalidates the whole chain. (well, from that point forward anyway)
    def validate(self):
        for i, block in enumerate(self.blocks):
            try:
                block.validate()
            except InvalidBlock as ex:
                raise InvalidBlockchain("Invalid blockchain at block {} caused by: {}".format(i, str(ex)))

    def __repr__(self):
        return 'Blockchain<blocks: {}>'.format(len(self.blocks))


class InvalidMessage(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidBlock(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

class InvalidBlockchain(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)