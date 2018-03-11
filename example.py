from blockchain import Message, Block, Blockchain
import pickle

B1 = Block()
B1.add_message(Message("This is the first message"))
B1.add_message(Message("Second message", "Alice", "Bob"))
B1.add_message(Message("Third message", "Bob", "Alice"))

B2 = Block()
B2.add_message(Message("Fourth message"))
B2.add_message(Message("Fifth message", "Eve", "Steve"))

B3 = Block()
B3.add_message(Message("Sixth message"))
B3.add_message(Message("Seventh Son of a Seventh Son is Iron Maiden's best album", "Me", "Everyone"))

B4 = Block()
B4.add_message(Message("Eighth message", "Bob", "Charlie"))
B4.add_message(Message("Ninth message", "Charlie", "Daniels"))
B4.add_message(Message("Tenth message", "Charlie", "Brown"))

chain = Blockchain()
chain.add_block(B1)
chain.add_block(B2)
chain.add_block(B3)
chain.add_block(B4)

print("Validating blockchain...")
chain.validate()   # all messages and inter-message links are valid, and all blocks and inter-block links are valid

print("Serializing...")
pickle.dump(chain, open('chain.p', 'wb'))

print("Deserializing and validating...")
chain2 = pickle.load(open('chain.p', 'rb'))
chain2.validate()

print("Serializing for tampering...")
pickle.dump(chain2, open('chain.p', 'wb'))

print("Hostile tampering...")
tampered = pickle.load(open('chain.p', 'rb'))
tampered.blocks[2].messages[1].data = "Seventh Son of a Seventh Son is THE WORST ALBUM EVER MADE"  # blasphemy!
pickle.dump(tampered, open('chain.p', 'wb'))

print("Deserializing tampered chain and validating...")
chain3 = pickle.load(open('chain.p', 'rb'))
chain3.validate()       # EARTH-SHATTERING KABOOM
