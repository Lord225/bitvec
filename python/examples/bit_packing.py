from bitvec.alias import unsigned_bin, u0, u8

def pack(data, size: int):
    output = u0() # create empty vector
    
    for byte in unsigned_bin(data).bytes(): # covert input into bits and iterate over bytes
        output.append(unsigned_bin(byte, size)) # take size bits from each byte and append to output
    
    return output.raw_bytes # return packed valus as bytes

def unpack(data, size: int):
    output = u0() # create empty vector
    
    for chunk in unsigned_bin(data).iter(size): # iterate over chunks of size bits
        output.append(u8(chunk)) # append each chunk to output and pad with 0 (if out want signed values we can use i8 instead)
    
    return output.raw_bytes # return unpacked valus as bytes

class Unpacker:
    def __init__(self, size: int):
        self.container = u0() # buffer for data
        self.size = size      # size of each chunk
    
    def append(self, data: bytes):
        self.container.append(unsigned_bin(data)) # append all bits to buffer
    
    def unpack(self):
        end = len(self.container)-len(self.container)%self.size # calculate end of last chunk of data
        
        bytes = unpack(self.container[:end], self.size) # unpack data that we have enough bits for
        self.container = self.container[end:] # remove unpacked data from buffer
        
        return bytes 

if __name__ == "__main__":
    print("Classic functions")
    packed = pack(b"\x01\x02\x03\x04", 6) # 4 bytes -> 4*6 bits -> 24 bits -> 3 bytes
    print(packed)
    unpacked = unpack(packed, 6)
    print(unpacked)

    print("Unpacker class")
    three_b_unpacker = Unpacker(3)
    three_b_unpacker.append(u8('11 010 001').raw_bytes) # add 1, 2 and two bits of 3th packed byte
    print(three_b_unpacker.unpack()) # b'\x01\x02' - unpacked 1 and 2
    three_b_unpacker.append(u8('0 101 100 0').raw_bytes) # add rest of 3th packed byte 4, 5 and 1st bit of 6th packed byte
    print(three_b_unpacker.unpack()) # b'\x03\x04\x05' - unpacked 3, 4 and 5