from typing import Optional
from ..pybytes import Binary
from .. import pybytes 

def unsigned_bin(object: object = None, size: Optional[int] = None) -> Binary:
    """
    Returns `Binary` object with sign_behavior set to 'unsigned'
    """
    return Binary(object, lenght=size, sign_behavior='unsigned')

def u0(object: object = None) -> Binary:
    """
    Returns unsigned 0 bit Binary value. Pads remaing bits with 0
    It it 'holds' always 0. 
    """
    return unsigned_bin(object, 0)

def u1(object: object = None) -> Binary:
    """
    Returns unsigned 1 bit Binary value. Pads remaing bits with 0
    It includes integers 0 or 1
    """
    return unsigned_bin(object, 1)

def u2(object: object = None) -> Binary:
    """
    Returns unsigned 2 bit Binary value. Pads remaing bits with 0
    It includes integers from 0 to 3
    """
    return unsigned_bin(object, 2)
def u3(object: object = None):
    """
    Returns unsigned 2 bit Binary value. Pads remaing bits with 0
    It includes integers from 0 to 7
    """
    return unsigned_bin(object, 3)
def u4(object: object = None):
    """
    Returns unsigned 4 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 4)
def u5(object: object = None):
    """
    Returns unsigned 5 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 5)
def u6(object: object = None):
    """
    Returns unsigned 6 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 6)
def u7(object: object = None):
    """
    Returns unsigned 7 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 7)
def u8(object: object = None):
    """
    Returns unsigned 8 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 8)
def u16(object: object = None):
    """
    Returns unsigned 16 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 16)
def u32(object: object = None):
    """
    Returns unsigned 32 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 32)
def u64(object: object = None):
    """
    Returns unsigned 64 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 64)
def u128(object: object = None):
    """
    Returns unsigned 128 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 128)
def u1024(object: object = None):
    """
    Returns unsigned 1024 bit Binary value. Pads remaing bits with 0
    """
    return unsigned_bin(object, 1024)


#####################
#  Signed Integers  #
#####################

def signed_bin(object: object = None, size: Optional[int] = None, raise_on_big_value=False) -> Binary:
    """
    Returns `Binary` object with sign_behavior set to 'signed'
    """
    return Binary(object, lenght=size, sign_behavior='signed')

def i0(object: object = None) -> Binary:
    """
    Returns signed 2 bit Binary value. Pads remaing bits with last bit (sign extended).
    It 'holds' always 0.
    """
    return signed_bin(object, 1, True)

def i1(object: object = None) -> Binary:
    """
    Returns signed 2 bit Binary value. Pads remaing bits with last bit (sign extended).
    It includes integers -1 and 0
    """
    return signed_bin(object, 1, True)

def i2(object: object = None) -> Binary:
    """
    Returns signed 2 bit Binary value. Pads remaing bits with last bit (sign extended).
    It includes integers from -2 to 1
    """
    return signed_bin(object, 2, True)
def i3(object: object = None):
    """
    Returns signed 2 bit Binary value. Pads remaing bits with last bit (sign extended)
    It includes integers from -4 to 3
    """
    return signed_bin(object, 3, True)
def i4(object: object = None):
    """
    Returns signed 4 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 4, True)
def i5(object: object = None):
    """
    Returns signed 5 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 5, True)
def i6(object: object = None):
    """
    Returns signed 6 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 6, True)
def i7(object: object = None):
    """
    Returns signed 7 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 7, True)
def i8(object: object = None):
    """
    Returns signed 8 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 8, True)
def i16(object: object = None):
    """
    Returns signed 16 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 16, True)
def i32(object: object = None):
    """
    Returns signed 16 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 32, True)
def i64(object: object = None):
    """
    Returns signed 16 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 64, True)
def i128(object: object = None):
    """
    Returns signed 16 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 128, True)
def i1024(object: object = None):
    """
    Returns signed 16 bit Binary value. Pads remaing bits with last bit (sign extended)
    """
    return signed_bin(object, 1024, True)