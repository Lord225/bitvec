import unittest
import numpy as np
from pybytes import Binary
from pybytes import arithm

# python -m unittest python\tests\tests.py

class TestConstruct(unittest.TestCase):
    def test_from_int(self):
        value = Binary(0)
        self.assertEqual(str(value), "0")
        self.assertEqual(value.len, 1)

        value = Binary(1)
        self.assertEqual(str(value), "1")
        self.assertEqual(value.len, 1)

        value = Binary(255)
        self.assertEqual(str(value), "11111111")
        self.assertEqual(value.len, 8)

        value = Binary(256)
        self.assertEqual(str(value), "1 00000000")
        self.assertEqual(value.len, 9)
        
        value = Binary(2**64)
        self.assertEqual(str(value), "1 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 65)

        value = Binary(2**64 - 1)
        self.assertEqual(str(value), "11111111 11111111 11111111 11111111 11111111 11111111 11111111 11111111")
        self.assertEqual(value.len, 64)

        value = Binary(2**65)
        self.assertEqual(str(value), "10 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 66)

    def test_from_int_signed(self):
        value = Binary(-1)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '11')

        value = Binary(-2)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '110')
        
        value = Binary(-256)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '11 00000000')

        value = Binary(-1, lenght=9)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '1 11111111')

        value = Binary(-1, lenght=2)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '11')

        value = Binary(-(2**64))
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '1 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000')
        

    def test_from_string(self):
        value = Binary("")
        self.assertEqual(str(value), "")
        self.assertEqual(value.len, 0)

        value = Binary("0")
        self.assertEqual(str(value), "0")
        self.assertEqual(value.len, 1)

        value = Binary("0000")
        self.assertEqual(str(value), "0000")
        self.assertEqual(value.len, 4)

        value = Binary("0   1 1 0")
        self.assertEqual(str(value), "0110")
        self.assertEqual(value.len, 4)

        value = Binary("0b1111")
        self.assertEqual(str(value), "1111")
        self.assertEqual(value.len, 4)

        value = Binary("0xFF")
        self.assertEqual(str(value), "11111111")
        self.assertEqual(value.len, 8)

        value = Binary("FF")
        self.assertEqual(str(value), "11111111")
        self.assertEqual(value.len, 8)

        value = Binary("f")
        self.assertEqual(str(value), "1111")
        self.assertEqual(value.len, 4)

        value = Binary("10000000 00000000 00000000 00000000")
        self.assertEqual(str(value), "10000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 32)

        value = Binary("10000000 00000000 00000000 00000000", lenght=32)
        self.assertEqual(str(value), "10000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 32)

        value = Binary("1 00000000 00000000 00000000 00000000", lenght=33)
        self.assertEqual(str(value), "1 00000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 33)

        value = Binary("0000", lenght=33)
        self.assertEqual(str(value), "0 00000000 00000000 00000000 00000000")
        self.assertEqual(value.len, 33)

    def test_from_arrays(self):
        value = Binary([True, True, 0, 0.0])
        self.assertEqual(str(value), "1100")
        self.assertEqual(value.len, 4)

        value = Binary([])
        self.assertEqual(str(value), "")
        self.assertEqual(value.len, 0)

    def test_rises(self):
        with self.assertRaises(Exception):
            Binary(0, byte_lenght=2, lenght=1)

class TestConversions(unittest.TestCase):
    def test_as_int(self):
        value = Binary(0)
        self.assertEqual(value.int(), 0)

        value = Binary(1)
        self.assertEqual(value.int(), 1)

        value = Binary(255)
        self.assertEqual(value.int(), 255)

        value = Binary(256)
        self.assertEqual(value.int(), 256)
        
        value = Binary(2**64)
        self.assertEqual(value.int(), 2**64)

        value = Binary(2**64 - 1)
        self.assertEqual(value.int(), 2**64 - 1)

        value = Binary(2**65)
        self.assertEqual(value.int(), 2**65)

        # with size
        value = Binary(0, byte_lenght=2)
        self.assertEqual(value.int(), 0)

        value = Binary(1, byte_lenght=2)
        self.assertEqual(value.int(), 1)

    
    def test_int_signed(self):
        value = Binary(-1)
        self.assertEqual(value.int(), -1)

        value = Binary(-2)
        self.assertEqual(value.int(), -2)
        
        value = Binary(-256)
        self.assertEqual(value.int(), -256)

        value = Binary(-1, lenght=9)
        self.assertEqual(value.int(), -1)

        value = Binary(-1, lenght=2)
        self.assertEqual(value.int(), -1)

        value = Binary(-(2**64))
        self.assertEqual(value.int(), -(2**64))

        # with size
        value = Binary(0, byte_lenght=2)
        self.assertEqual(value.int(), 0)

        value = Binary(-1, byte_lenght=2)
        self.assertEqual(value.int(), -1)

    def test_as_hex(self):
        value = Binary(0)
        self.assertEqual(value.hex(), "0x0")

        value = Binary(1)
        self.assertEqual(value.hex(), "0x1")

        value = Binary(255)
        self.assertEqual(value.hex(), "0xff")

        value = Binary(256)
        self.assertEqual(value.hex(), "0x100")
        
        value = Binary(2**64)
        self.assertEqual(value.hex(), "0x10000000000000000")

        value = Binary(2**64 - 1)
        self.assertEqual(value.hex(), "0xffffffffffffffff")

        value = Binary(2**65)
        self.assertEqual(value.hex(), "0x20000000000000000")

        # with size
        value = Binary(0, byte_lenght=2)
        self.assertEqual(value.hex(), "0x0000")

        value = Binary(1, byte_lenght=2)
        self.assertEqual(value.hex(), "0x0001")
    def test_as_bin(self):
        value = Binary(0)
        self.assertEqual(value.bin(), "0b0")

        value = Binary(1)
        self.assertEqual(value.bin(), "0b1")

        value = Binary(255)
        self.assertEqual(value.bin(), "0b11111111")

        value = Binary(256)
        self.assertEqual(value.bin(), "0b100000000")
        
        value = Binary(2**64)
        self.assertEqual(value.bin(), "0b10000000000000000000000000000000000000000000000000000000000000000")

        value = Binary(2**64 - 1)
        self.assertEqual(value.bin(), "0b1111111111111111111111111111111111111111111111111111111111111111")

        value = Binary(2**65)
        self.assertEqual(value.bin(), "0b100000000000000000000000000000000000000000000000000000000000000000")

        # with size
        value = Binary(0, byte_lenght=2)
        self.assertEqual(value.bin(), "0b0000000000000000")

        value = Binary(1, byte_lenght=2)
        self.assertEqual(value.bin(), "0b0000000000000001")

class TestAssigns(unittest.TestCase):    
    def test_assign_int_key(self):
        x = Binary("0000 0000")
        x[0] = True
        self.assertEqual(str(x), "00000001")
        x[1] = True
        self.assertEqual(str(x), "00000011")
        x[-1] = True
        self.assertEqual(str(x), "10000011")
        x[0] = False
        self.assertEqual(str(x), "10000010")
    def test_read_int_key(self):
        x = Binary("10000010")
        self.assertEqual(x[0], False)
        self.assertEqual(x[1], True)
        self.assertEqual(x[2], False)

        x = Binary("1 10000010")
        self.assertEqual(x[7], True)
        self.assertEqual(x[8], True)
        self.assertEqual(x[-1], True)
    def test_read_slice_key(self):
        x = Binary("10000010")
        self.assertEqual(x[0:3], "010")
        self.assertEqual(x[:3], "010")
        self.assertEqual(x[-3:], "100")
        
        x = Binary("1 10000010")
        self.assertEqual(x[:-3], "000010")
        self.assertEqual(x[-5:-1], '1000')
        self.assertEqual(x[5:7], '00')
        self.assertEqual(x[:], "1 10000010")
    def test_assign_slice_key(self): 
        def gen():
            return Binary("10000010"), Binary("101")
        
        x, y = gen()
        x[:3] = y
        self.assertEqual(str(x), "10000101")
        
        x, y = gen()
        x[4:] = 1
        self.assertEqual(str(x), "00010010")

        x, y = gen()
        x[:4] = 0
        self.assertEqual(str(x), "10000000")

        x, y = gen()
        x[1:4] = "101"
        self.assertEqual(str(x), "10001010")

        x, y = gen()
        x[:] = False
        self.assertEqual(str(x), "00000000")

        x, y = gen()
        x[:] = False
        self.assertEqual(str(x), "00000000")    
    def test_illegal_assigns(self):
        x = Binary("10000010")
        with self.assertRaises(Exception):
            x[0:1] = "1111 1111"
        with self.assertRaises(Exception):
            x[-100:1] = "1111 1111"

class TestCompare(unittest.TestCase):
    def test_unsigned_cmps(self):
        TESTDATA = [1, 2, 256, 255, 1024, 0]
        for x in TESTDATA:
            for y in TESTDATA:
                xx = Binary(x)
                yy = Binary(y)

                self.assertEqual(xx==yy, x==y)
                self.assertEqual(xx!=yy, x!=y)
                self.assertEqual(xx>yy, x>y)
                self.assertEqual(xx>=yy, x>=y)
                self.assertEqual(xx<yy, x<y)
                self.assertEqual(xx<=yy, x<=y)

                self.assertEqual(x==yy, x==y)
                self.assertEqual(x!=yy, x!=y)
                self.assertEqual(x>yy, x>y)
                self.assertEqual(x>=yy, x>=y)
                self.assertEqual(x<yy, x<y)
                self.assertEqual(x<=yy, x<=y)

                self.assertEqual(xx==y, x==y)
                self.assertEqual(xx!=y, x!=y)
                self.assertEqual(xx>y, x>y)
                self.assertEqual(xx>=y, x>=y)
                self.assertEqual(xx<y, x<y)
                self.assertEqual(xx<=y, x<=y)
    def test_signed_cmps(self):
        TESTDATA = [1, 2, 256, 255, 1024, 0, -1, -2, -256, -255, -1024]
        for x in TESTDATA:
            for y in TESTDATA:
                xx = Binary(x, sign_behavior='signed')
                yy = Binary(y, sign_behavior='signed')

                self.assertEqual(xx==yy, x==y)
                self.assertEqual(xx!=yy, x!=y)
                self.assertEqual(xx>yy, x>y)
                self.assertEqual(xx>=yy, x>=y)
                self.assertEqual(xx<yy, x<y)
                self.assertEqual(xx<=yy, x<=y)

                self.assertEqual(x==yy, x==y)
                self.assertEqual(x!=yy, x!=y)
                self.assertEqual(x>yy, x>y)
                self.assertEqual(x>=yy, x>=y)
                self.assertEqual(x<yy, x<y)
                self.assertEqual(x<=yy, x<=y)

                self.assertEqual(xx==y, x==y)
                self.assertEqual(xx!=y, x!=y)
                self.assertEqual(xx>y, x>y)
                self.assertEqual(xx>=y, x>=y)
                self.assertEqual(xx<y, x<y)
                self.assertEqual(xx<=y, x<=y)

class Operations(unittest.TestCase):
    def test_add(self):
        self.assertEqual(Binary("0000 0001")+Binary("0000 0001"), Binary("0000 0010"))
        self.assertEqual(Binary("0001")+Binary("0001"), Binary("0010"))
        self.assertEqual(Binary("1")+Binary("1"), Binary("0"))
        self.assertEqual(arithm.overflowing_add(Binary("1"), Binary("1")), (Binary("0"), True))
        self.assertEqual(Binary("1 0000 0000")+Binary("0000 0001"), Binary("1 0000 0001"))
        self.assertEqual(Binary("00 1000 0000")+Binary("1000 0000"), Binary("01 0000 0000"))
        self.assertEqual(Binary("01 1000 0000")+Binary("1000 0000"), Binary("10 0000 0000"))
        self.assertEqual(Binary("11 0000 0000")+1, Binary("11 0000 0001"))
    def test_add_long(self):
        NUMS_TO_TEST = [1,2,4,15, 2**63,2**64-1, 2**64]

        for x in NUMS_TO_TEST:
            for y in NUMS_TO_TEST:
                xx = Binary(x, lenght=65)
                yy = Binary(y, lenght=65)

                self.assertEqual(xx+yy, arithm.wrapping_add(xx, yy))
    def test_add_lenghts(self):
        NUMS_TO_TEST = [i for i in range(0, 15)]
        SIZES = [i for i in range(4, 66, 2)]
        
        for x in NUMS_TO_TEST:
            for y in NUMS_TO_TEST:
                for size in SIZES:
                    xx = Binary(x, lenght=size)
                    yy = Binary(y, lenght=size)

                    self.assertEqual(xx+yy, arithm.wrapping_add(xx, yy))
    def test_sub(self):
        self.assertEqual(Binary("0000 0001")-Binary("0000 0001"), Binary("0000 0000"))
        self.assertEqual(Binary("0000 0000")-Binary("0000 0001"), Binary("1111 1111"))
        self.assertEqual(Binary("0000 0001")-Binary("0000 0000"), Binary("0000 0001"))
        self.assertEqual(Binary("0 0000 0000")-Binary("0000 0001"), Binary("1 1111 1111"))
        self.assertEqual(Binary("1 0000 0000")-Binary("0000 0001"), Binary("0 1111 1111"))

        