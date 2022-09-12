import unittest
import numpy as np
from pybytes import Binary
from pybytes import arithm
from pybytes import alias

# python -m unittest python\tests\tests.py

class TestConstruct(unittest.TestCase):
    def test_from_int(self):
        value = Binary(0)
        self.assertEqual(str(value), "")
        self.assertEqual(value.len, 0)

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
        self.assertEqual(str(value), '1')

        value = Binary(-2)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '10')
        
        value = Binary(-256)
        self.assertEqual(value.sign_behavior(), 'signed')
        self.assertEqual(str(value), '1 00000000')

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
    def test_edge_cases(self):
        self.assertEqual(Binary(0, lenght=0, sign_behavior='unsigned').int(), 0)
        with self.assertRaises(Exception):
            Binary(1, lenght=0, sign_behavior='unsigned')
        with self.assertRaises(Exception):
            Binary(-1, lenght=0, sign_behavior='unsigned')

        self.assertEqual(Binary(0, lenght=1, sign_behavior='unsigned').int(), 0)
        self.assertEqual(Binary(1, lenght=1, sign_behavior='unsigned').int(), 1)
        with self.assertRaises(Exception):
            Binary(-1, lenght=1, sign_behavior='unsigned')
        with self.assertRaises(Exception):
            Binary(2, lenght=1, sign_behavior='unsigned')

        self.assertEqual(Binary(0, lenght=0, sign_behavior='signed').int(), 0)
        with self.assertRaises(Exception):
            Binary(1, lenght=0, sign_behavior='signed')
        with self.assertRaises(Exception):
            Binary(-1, lenght=0, sign_behavior='signed')
            
        self.assertEqual(Binary(0, lenght=1, sign_behavior='signed').int(), 0)
        self.assertEqual(Binary(-1, lenght=1, sign_behavior='signed').int(), -1)
        with self.assertRaises(Exception):
            Binary(1, lenght=1, sign_behavior='signed')
        with self.assertRaises(Exception):
            Binary(-2, lenght=1, sign_behavior='signed')
        

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
        self.assertEqual(value.hex(), "0x")

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
        self.assertEqual(value.bin(), "0b")

        value = Binary(0, lenght=0)
        self.assertEqual(value.bin(), "0b")

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

        value = Binary(0)
        self.assertEqual(value.bin(prefix=False), "")
        value = Binary(0)
        self.assertEqual(value.bin(False), "")

class AliasTest(unittest.TestCase):
    def test_base(self):
        OBJ_TO_TEST = ['1111', 15, b'\x0F', '0xf']

        for size in range(4, 32):
            for obj in OBJ_TO_TEST:
                val = alias.unsigned_bin(obj, size)

                self.assertEqual(val.len, size)
                self.assertEqual(val.sign_behavior(), 'unsigned')
                self.assertEqual(val.int(), 15)
    def test_uN(self):
        uN = [(alias.u2, 2), (alias.u3, 3), (alias.u4, 4), (alias.u5, 5), (alias.u6, 6), (alias.u7, 7), (alias.u8, 8), (alias.u16, 16), (alias.u32, 32)]

        for (func, size) in uN:
            self.assertEqual(func(1), Binary(1, lenght=size, sign_behavior='unsigned'))

    def test_iN(self):
        iN = [(alias.i2, 2), (alias.i3, 3), (alias.i4, 4), (alias.i5, 5), (alias.i6, 6), (alias.i7, 7), (alias.i8, 8), (alias.i16, 16), (alias.i32, 32)]

        for val in [0, 1, -1]:
            for (func, size) in iN:
                as_bin: Binary = func(val)
                self.assertEqual(as_bin, Binary(val, lenght=size, sign_behavior='signed'))
                self.assertEqual(as_bin.int(), val)

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
    def test_slice(self):
        from pybytes.alias import u4, i4
        a, b = u4('1101'), i4('1101')

        self.assertEqual(str(a[0:0]), '')
        self.assertEqual(str(a[0:1]), '1')
        self.assertEqual(str(a[0:2]), '01')
        self.assertEqual(str(a[0:3]), '101')
        self.assertEqual(str(a[0:4]), '1101')
        self.assertEqual(str(a[0:5]), '01101')
        self.assertEqual(str(a[0:6]), '001101')
        self.assertEqual(str(a[0:7]), '0001101')

        self.assertEqual(str(a[1:1]), '')
        self.assertEqual(str(a[1:2]), '0')
        self.assertEqual(str(a[1:3]), '10')
        self.assertEqual(str(a[1:4]), '110')
        self.assertEqual(str(a[1:5]), '0110')
        self.assertEqual(str(a[1:6]), '00110')
        self.assertEqual(str(a[1:7]), '000110')

        self.assertEqual(str(a[2:2]), '')
        self.assertEqual(str(a[2:3]), '1')
        self.assertEqual(str(a[2:4]), '11')
        self.assertEqual(str(a[2:5]), '011')
        self.assertEqual(str(a[2:6]), '0011')
        self.assertEqual(str(a[2:7]), '00011')

        self.assertEqual(str(a[3:3]), '')
        self.assertEqual(str(a[3:4]), '1')
        self.assertEqual(str(a[3:5]), '01')
        self.assertEqual(str(a[3:6]), '001')
        self.assertEqual(str(a[3:7]), '0001')

        self.assertEqual(str(a[4:4]), '')
        self.assertEqual(str(a[4:5]), '0')
        self.assertEqual(str(a[4:6]), '00')
        self.assertEqual(str(a[4:7]), '000')

        self.assertEqual(str(a[5:5]), '')
        self.assertEqual(str(a[5:6]), '0')
        self.assertEqual(str(a[5:7]), '00')

        self.assertEqual(str(a[6:6]), '')
        self.assertEqual(str(a[6:7]), '0')

        self.assertEqual(str(a[7:7]), '')

        self.assertEqual(str(b[0:0]), '')
        self.assertEqual(str(b[0:1]), '1')
        self.assertEqual(str(b[0:2]), '01')
        self.assertEqual(str(b[0:3]), '101')
        self.assertEqual(str(b[0:4]), '1101')
        self.assertEqual(str(b[0:5]), '11101')
        self.assertEqual(str(b[0:6]), '111101')
        self.assertEqual(str(b[0:7]), '1111101')

        self.assertEqual(str(b[1:1]), '')
        self.assertEqual(str(b[1:2]), '0')
        self.assertEqual(str(b[1:3]), '10')
        self.assertEqual(str(b[1:4]), '110')
        self.assertEqual(str(b[1:5]), '1110')
        self.assertEqual(str(b[1:6]), '11110')
        self.assertEqual(str(b[1:7]), '111110')

        self.assertEqual(str(b[2:2]), '')
        self.assertEqual(str(b[2:3]), '1')
        self.assertEqual(str(b[2:4]), '11')
        self.assertEqual(str(b[2:5]), '111')
        self.assertEqual(str(b[2:6]), '1111')
        self.assertEqual(str(b[2:7]), '11111')

        self.assertEqual(str(b[3:3]), '')
        self.assertEqual(str(b[3:4]), '1')
        self.assertEqual(str(b[3:5]), '11')
        self.assertEqual(str(b[3:6]), '111')
        self.assertEqual(str(b[3:7]), '1111')

        self.assertEqual(str(b[4:4]), '')
        self.assertEqual(str(b[4:5]), '1')
        self.assertEqual(str(b[4:6]), '11')
        self.assertEqual(str(b[4:7]), '111')

        self.assertEqual(str(b[5:5]), '')
        self.assertEqual(str(b[5:6]), '1')
        self.assertEqual(str(b[5:7]), '11')

        self.assertEqual(str(b[6:6]), '')
        self.assertEqual(str(b[6:7]), '1')

        self.assertEqual(str(b[7:7]), '')


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

                self.assertEqual(x==yy, x==y, f'{x}=={yy}, {x}=={y}')
                self.assertEqual(x!=yy, x!=y)
                self.assertEqual(x>yy, x>y)
                self.assertEqual(x>=yy, x>=y)
                self.assertEqual(x<yy, x<y)
                self.assertEqual(x<=yy, x<=y)

                self.assertEqual(xx==y, x==y, f'{xx}=={y}, {x}=={y}')
                self.assertEqual(xx!=y, x!=y)
                self.assertEqual(xx>y, x>y)
                self.assertEqual(xx>=y, x>=y)
                self.assertEqual(xx<y, x<y)
                self.assertEqual(xx<=y, x<=y)

class BinaryFunctions(unittest.TestCase):
    def test_sign_behavior(self):
        from pybytes.alias import u4, i4, u8, i8, i16
        
        self.assertEqual(u4('0000').sign_behavior(), 'unsigned')
        self.assertEqual(i4('0000').sign_behavior(), 'signed')

        self.assertEqual(u4('0000').sign_extending_bit(), False)
        self.assertEqual(u4('1000').sign_extending_bit(), False)
        self.assertEqual(i4('0000').sign_extending_bit(), False)
        self.assertEqual(i4('1000').sign_extending_bit(), True)

        self.assertEqual(u4('0000').is_negative(), False)
        self.assertEqual(u4('1000').is_negative(), False)
        self.assertEqual(i4('1111').is_negative(), True)

        self.assertEqual(u4('1111').low_byte(), u8('0000 1111'))
        self.assertEqual(i4('1111').low_byte(), i8('1111 1111'))
        
        self.assertEqual(u4('1111').high_byte(), u8('0000 0000'))
        self.assertEqual(i4('1111').high_byte(), i8('1111 1111'))

        self.assertEqual(i16('0100 0011 0010 0001').get_byte(0), i8('0010 0001'))
        self.assertEqual(i16('0100 0011 0010 0001').get_byte(1), i8('0100 0011'))
        self.assertEqual(i16('0100 0011 0010 0001').get_byte(2), i8('0000 0000'))


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
        SIZES = [i for i in range(4, 66, 4)]
        
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

    def test_sub_long(self):
        NUMS_TO_TEST = [1,2,4,15, 2**63,2**64-1, 2**64]

        for x in NUMS_TO_TEST:
            for y in NUMS_TO_TEST:
                xx = Binary(x, lenght=65)
                yy = Binary(y, lenght=65)

                self.assertEqual(xx-yy, arithm.wrapping_sub(xx, yy))
    def test_bitwise(self):
        from pybytes.alias import u4
        TEST_CASES = [i for i in range(0, 16)]
        
        for a in TEST_CASES:
            for b in TEST_CASES:
                self.assertEqual(arithm.bitwise_and(u4(a), u4(b)).int(), a&b)
                self.assertEqual(arithm.bitwise_or(u4(a), u4(b)).int(), a|b)
                self.assertEqual(arithm.bitwise_xor(u4(a), u4(b)).int(), a^b)
                
                self.assertEqual(arithm.bitwise_nand(u4(a), u4(b)).int(), (a&b)^0xf)
                self.assertEqual(arithm.bitwise_nor(u4(a), u4(b)).int(), (a|b)^0xf)
                self.assertEqual(arithm.bitwise_xnor(u4(a), u4(b)).int(), (a^b)^0xf)
    def test_bitwise_with_diffrent_sizes(self):
        from pybytes.alias import u4, u7, i4

        self.assertEqual(arithm.bitwise_and(u7('111 1111'), u4('0001')), u7('000 0001'))
        self.assertEqual(arithm.bitwise_or (u7('111 1111'), u4('0001')), u7('111 1111'))
        self.assertEqual(arithm.bitwise_and(u7('111 1111'), i4('0001')), u7('000 0001'))
        self.assertEqual(arithm.bitwise_and(u7('111 1111'), i4('1001')), u7('111 1001'))
    def test_bitwise_operators(self):
        from pybytes.alias import u8, i4
        a,b = u8(6), u8(14)

        self.assertEqual(a|b, u8('0000 1110'))
        self.assertEqual(a^b, u8('0000 1000'))
        self.assertEqual(a&b, u8('0000 0110'))
        self.assertEqual(~b,  u8('1111 0001')) 
        self.assertEqual(-b,  u8('1111 0010')) # -14

        self.assertEqual(a|1, u8('0000 0111'))
        self.assertEqual(a&1, u8('0000 0000'))
        self.assertEqual(a&2, u8('0000 0010'))
        
        c, d = i4('0001'), i4('1111')
        
        self.assertEqual(a|c, u8('0000 0111'))
        self.assertEqual(a|d, u8('1111 1111'))  # i4 extended to i8, sign is taken from first arg
        self.assertEqual(a^d, u8('1111 1001'))


    def test_mul(self):
        TEST_CASES = [1,2,3,5,16,32,1024,2**31,2**32, -2**32, -1,-2,-3]

        for i in TEST_CASES:
            for j in TEST_CASES:
                ii, jj = Binary(i), Binary(j)

                self.assertEqual(arithm.multiply(ii, jj).int(), i*j)
    def test_mul_u4(self):
        from pybytes.alias import i4, u4, i8, u8

        self.assertEqual(arithm.multiply(u4('0001'), u4('0001')), u8('0000 0001'))
        self.assertEqual(arithm.multiply(u4('0010'), u4('0010')), u8('0000 0100'))
        self.assertEqual(arithm.multiply(u4('1111'), u4('0010')), u8('0001 1110'))
