from bitvec.alias import unsigned_bin, u0, u8

def pack(data, size: int):
    # create empty vector
    output = u0()
    
    # covert input into bits and iterate over bytes
    for byte in unsigned_bin(data).bytes(): 
        # take size bits from each byte and append to output
        output.append(unsigned_bin(byte, size))
    
    # return packed valus as bytes
    return output.raw_bytes

def unpack(data, size: int):
    # create empty vector
    output = u0() 
    
    # iterate over chunks of size bits
    for chunk in unsigned_bin(data).iter(size): 
        # append each chunk to output and pad with 0 
        # (if out want signed values we can use i8 instead)
        output.append(u8(chunk)) 
    
    # return unpacked valus as bytes
    return output.raw_bytes 

def smallest_multiple_of(x: int, y: int):
    """
    Return the multiple of y that is smaller than x.
    ```py
    smallest_multiple_of(10, 3) == 9
    ```
    """
    return x-x%y

class Unpacker:
    def __init__(self, size: int):
        self.container = u0() # buffer for data
        self.size = size      # size of each chunk
    
    def append(self, data: bytes):
        # append all bits to buffer. Providing `bytes` to 
        # Binary will convert it to bits keeping the leading 0s 
        self.container.append(unsigned_bin(data)) 
    
    def unpack(self):
        # calculate end of last chunk of data
        
        end = smallest_multiple_of(len(self.container), self.size)   
        
        # split buffer into chunks of data and remaining bits
        data, self.container = self.container.split_at(end)

        # unpack data that we have enough bits for 
        return unpack(data, self.size) 

if __name__ == "__main__":
    print("Classic functions")
    
    packed = pack(b"\x01\x02\x03\x04", 6) # 4 bytes -> 4*6 bits -> 24 bits -> 3 bytes
    print(packed)
    
    unpacked = unpack(packed, 6)
    print(unpacked)

    
    print("Unpacker class")
    three_b_unpacker = Unpacker(3)
    
    # add 1, 2 and two bits of 3th packed byte
    three_b_unpacker.append(u8('11 010 001').raw_bytes)
    # b'\x01\x02' - unpacked 1 and 2
    print(three_b_unpacker.unpack())
    
    # add rest of 3th packed byte 4, 5 and 1st bit of 6th packed byte
    three_b_unpacker.append(u8('0 101 100 0').raw_bytes)
    # b'\x03\x04\x05' - unpacked 3, 4 and 5
    print(three_b_unpacker.unpack()) 