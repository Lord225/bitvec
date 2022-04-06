from pybytes.common import utils
from typing import Dict, Literal, Tuple, Union
import pybytes.common.aritmetic.aritmetic_base as alu_base
import pybytes.binary_class as binary_class
import numpy as np

class Flags:
    def __init__(self, of = False, zf = False, sf = False, pf = False):
        self.of = bool(of)
        self.zf = bool(zf)
        self.sf = bool(sf)
        self.pf = bool(pf)
    def __iter__(self):
        return iter((self.of, self.zf, self.sf, self.pf))
    def is_zero(self) -> bool:
        return bool(self.zf)
    def is_overflow(self) -> bool:
        return bool(self.of)
    def is_sign(self) -> bool:
        return bool(self.sf)
    def is_partity(self) -> bool:
        return bool(self.pf)
    def __repr__(self) -> str:
        return f"Flags(of={self.is_overflow()},zf={self.is_zero()},sf={self.is_sign()},pf={self.is_partity()})"
    def __eq__(self, o: object) -> bool:
        if isinstance(o, Flags):
            return self.of == o.of and self.pf == o.pf and self.zf == o.zf and self.sf == o.sf
        else:
            return False


def wrapping_add(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    """
    Returns sum of two numbers with wrapping arithmetic.
    It is default behavior for `+` operator in `Binary` class
    ```
    >>> wrapping_add(u8(1), u2(1)) # output is 8 bit bsc 8 > 2
    '00000010'
    >>> wrapping_add(u8(255), 1) # 11111111 + 1 overflows
    '00000000'
    ```

    """
    out, _ = overflowing_add(rsh, lsh)
    return out
def overflowing_add(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    """
    Returns sum of two numbers with wrapping arithmetic and information if overflow occure
    >>> overflowing_add(u8(1), u2(1))
    ('00000010', False)
    >>> overflowing_add(u8(255), 1) # 11111111 + 1 overflows
    ('00000000', True)
    """
    out, (of, _, _, _) =  flaged_add(rsh, lsh)
    return out, of
def flaged_add(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    """
    Returns sum of two numbers with all arithmetic flags (wrappend in object `Flags`):
    
        * Zero Flag (number equal to zero)
        * OverFlow Flag (overflow occure)
        * Sign Flag (`out[-1] == True`)
        * Partity Flag [`out[0] == True`]
    
    ```
    >>> flaged_add(u8(255), 1)
    ('00000000', Flags(of=True,zf=True,sf=False,pf=False))
    ```
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, bit_lenght=len(rsh), sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    out_data, of, zf, pf = alu_base.add_arrays(rsh._data, lsh._data,new_mask, carry=0)
    output = binary_class.Binary(out_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
    return output, Flags(of, zf, output[-1], pf)

def wrapping_sub(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    """
    Subtracts rsh from lsh using binary arithmetic
    """
    out, _ = overflowing_sub(rsh, lsh)
    return out
def overflowing_sub(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_sub(rsh, lsh)
    return out, of
def flaged_sub(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, bit_lenght=len(rsh), sign_behavior=rsh._sign_behavior)
    
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)

    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()

    out_data, of, zf, pf = alu_base.sub_arrays(rsh._data, lsh._data, rsh._len, lsh._len, new_mask, rsh._sign_behavior)
    output = binary_class.Binary(out_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior) 
    
    return output, Flags(of, zf, output[-1], pf)

def flaged_mul(rsh: binary_class.Binary, lsh: object)-> Tuple[binary_class.Binary, binary_class.Binary]:
    """
    Multiplays two binary numbers, and returns two values: lower half of the product and higher half
    ```
    >>> i4(2)*i4(2) 
    ('0000', '0100')
    >>> i4(4)*i4(4) 
    ('0001', '0000') # result wrapps to carry (hi half)
    ```
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, bit_lenght=len(rsh), sign_behavior=rsh._sign_behavior)
    
    rsh_as_int = int(rsh)
    lsh_as_int = int(lsh)

    new_lenght = max(len(rsh), len(lsh))

    if lsh.sign_behavior() != rsh.sign_behavior():
        raise ValueError("Cannot multiply numbers with diffrent sign behavior")

    mul = binary_class.Binary(rsh_as_int*lsh_as_int, bit_lenght=2*new_lenght, sign_behavior=rsh._sign_behavior)

    return binary_class.Binary(mul[len(rsh):]), binary_class.Binary(mul[:len(rsh)])

def wrapping_mul(rsh: binary_class.Binary, lsh: object)-> Tuple[binary_class.Binary, binary_class.Binary]:
    """
    Multiplays two binary numbers, but discards second half of product (output will always be of lenght `max(len(rsh), len(lsh))`)

    It is default behavior for `*` operator in Binary number
    ```
    >>> i4(2)*i4(2) 
    '0100'
    >>> i4(4)*i4(4) 
    '0000' # wraps around to 0
    ```
    """
    _, lo = flaged_mul(rsh, lsh)
    return lo
    

def bitwise_not(tar: binary_class.Binary):
    """
    Flips all bits in number
    ```
    >>> bitwise_not(u4('0101'))
    '1010'
    ```
    """
    _not_data = alu_base.bitwise_neg_array(tar._data, tar._mask)
    return binary_class.Binary(_not_data, bit_lenght=tar._len, sign_behavior=tar._sign_behavior)
def arithmetic_neg(tar: binary_class.Binary):
    """
    Performs arithmetic negatin of the number: `~tar + 1` For 1 returns -1, -2 2 ect.
    ```
    >>> arithmetic_neg(u4('0101'))
    '1011' # 5 becomes "-5" in signed domain
    ```
    """
    _neg_data = alu_base.arithmeitc_neg_number(tar._data, tar._len, tar._mask, tar._sign_behavior)
    return binary_class.Binary(_neg_data, bit_lenght=tar._len, sign_behavior=tar._sign_behavior)

def bitwise_and(rsh: binary_class.Binary, lsh: object):
    """
    Performs and operation on bits, pads shorter value with zeros
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_and(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_or(rsh: binary_class.Binary, lsh: object):
    """
    Performs or operation on bits, pads shorter value with zeros
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_or(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_xor(rsh: binary_class.Binary, lsh: object):
    """
    Performs xor operation on bits, pads shorter value with zeros
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_xor(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)

def bitwise_nand(rsh: binary_class.Binary, lsh: object):
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_nand(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_nor(rsh: binary_class.Binary, lsh: object):
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_nor(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_xnor(rsh: binary_class.Binary, lsh: object):
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_xnor(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)

def bitwise_map(rsh: binary_class.Binary, lsh: object, map: Union[Dict[Tuple[bool, bool], bool], Dict[int, bool]]):
    """Any custom 2 argument boolean function. should contain all combinations of 
    two argument boolean function. 
    ```
    map = {(arg1, arg2): output, ...}
    ```

    For example:
    ```
    xor_map = {(False, False): False, (True, False): True, (False, True): True, (True, True): False}
    xnor_map = {0:True, 1:False, 2:False 3: True}
    ```
    """
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    if isinstance(list(map.keys())[0], type(int)):
        new_map = dict()
        new_map[(False, False)] = map[0]
        new_map[(False, True)] = map[1]
        new_map[(True, False)] = map[2]
        new_map[(True, True)] = map[3]
    else:
        new_map = map
    new_data = alu_base.bitwise_map(rsh._data, lsh._data, rsh._len, lsh._len, new_mask, new_map[(False, False)], new_map[(False, True)], new_map[(True, False)], new_map[(True, True)])
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)

def convert(tar: binary_class.Binary, sign_behavior: Literal["unsigned", "magnitude", "signed"]):
    """
    Converts any Binary value to given sign_behavior.
    ```
    >>>convert(u8(1), 'signed')
    '00000001' # sign_behavior is now 'signed'
    >>>convert(i8(-1), 'magnitude')
    '10000001' 
    ```
    """
    new_data = alu_base.sign_convert[sign_behavior](tar._data, tar._len, tar._mask, tar._sign_behavior, False)
    return binary_class.Binary(new_data, bit_lenght=tar._len, sign_behavior=sign_behavior)
def cast(tar: binary_class.Binary, sign_behavior: Literal["unsigned", "magnitude", "signed"]):
    """
    Cast value to diffrent `sign_behavior` without any modifications in bits
    ```
    >>>int(cast(u4('1111'), 'signed'))
    -1
    >>>int(cast(i4('1111'), 'unsigned'))
    15
    ```
    """
    return binary_class.Binary(tar._data, bit_lenght=tar._len, sign_behavior=sign_behavior)

def wrapping_lsh(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = overflowing_lsh(rsh, lsh)
    return out
def overflowing_lsh(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_lsh(rsh, lsh)
    return out, of
def flaged_lsh(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    rsh_casted = int(cast(rsh, "unsigned"))
    lsh_casted = int(cast(lsh, "unsigned")) if isinstance(lsh, binary_class.Binary) else int(lsh)

    if lsh_casted >= 0:
        output = rsh_casted<<lsh_casted
    else:
        output = rsh_casted

    of = output > rsh.maximum_value()
    zf = output==0
    sf = rsh[-1]
    pf = rsh[0]
    
    output = binary_class.Binary(output, bit_lenght=rsh._len, sign_behavior=rsh._sign_behavior)
    
    return output, Flags(of, zf, sf, pf)

def wrapping_shld(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = overflowing_shld(rsh, lsh)
    return out
def overflowing_shld(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_shld(rsh, lsh)
    return out, of
def flaged_shld(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    rsh_casted = int(cast(rsh, "unsigned"))
    lsh_casted = int(cast(lsh, "unsigned")) if isinstance(lsh, binary_class.Binary) else int(lsh)

    output = rsh_casted<<lsh_casted

    of = output > rsh.maximum_value()
    zf = output==0
    sf = utils.get_bit_array(rsh._data, rsh._len-1, rsh._len)
    pf = utils.get_bit_array(rsh._data, 0, rsh._len)

    output = binary_class.Binary(output)[len(rsh):2*len(rsh)]

    return output, Flags(of, zf, sf, pf)

def wrapping_rsh(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = underflowing_rsh(rsh, lsh)
    return out
def underflowing_rsh(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_rsh(rsh, lsh)
    return out, of
def flaged_rsh(rsh: binary_class.Binary, lhs: object) -> Tuple[binary_class.Binary, Flags]:
    rsh_casted = int(cast(rsh, "unsigned"))
    lsh_casted = int(cast(lhs, "unsigned")) if isinstance(lhs, binary_class.Binary) else int(lhs)
 
    if lsh_casted >= 0:
        output = rsh_casted>>lsh_casted
    else:
        output = rsh_casted
    
    uf = output<<lsh_casted != rsh_casted
    zf = output==0
    sf = rsh[-1]
    pf = rsh[0]
    
    output = binary_class.Binary(output, bit_lenght=rsh._len, sign_behavior=rsh._sign_behavior)
    
    return output, Flags(uf, zf, sf, pf)

def arithmetic_flaged_rsh(rhs: binary_class.Binary, lhs: object):
    lsh_casted = int(cast(lhs, "unsigned")) if isinstance(lhs, binary_class.Binary) else int(lhs)

    sign_bit = rhs.is_negative()
    rhs = cast(rhs, 'unsigned')
    rhs[-1] = False

    output, flags = flaged_rsh(rhs, lsh_casted)
    
    output[-lsh_casted-1:] = sign_bit
    
    return output, flags

def pad_zeros(obj: binary_class.Binary, size: int) -> binary_class.Binary:
    """
    Returns same number but paded with zeros to given size
    ```
    >>> x = u8(255)
    >>> x
    '11111111'
    >>> pad_zeros(x, 16)
    '00000000 11111111'
    ```
    """
    
    if len(obj) >= size:
        return obj
    
    zeros = binary_class.Binary(0, bit_lenght=size, sign_behavior=obj.sign_behavior(), default_formatting=obj._default_formatting)
    zeros[:len(obj)] = obj
    return zeros

def pad_ones(obj: binary_class.Binary, size: int) -> binary_class.Binary:
    """
    Returns same number but paded with ones to given size
    ```
    >>> x = u8(0)
    >>> x
    '00000000'
    >>> pad_ones(x, 16)
    '11111111 00000000'
    ```
    """
    
    if len(obj) >= size:
        return obj
    
    ones = cast(binary_class.Binary(2**size-1, bit_lenght=size, default_formatting=obj._default_formatting), obj.sign_behavior())
    ones[:len(obj)] = obj
    return ones

def sign_extend(obj: binary_class.Binary, size: int) -> binary_class.Binary:
    """
    Returns same number but paded with last bit value to given size.
    sign_behavtor does not make any diffrence here
    ```
    >>> sign_extend(u8(128), 16)
    '11111111 10000000'
    >>> sign_extend(u8(127), 16)
    '00000000 01111111'
    ```
    """
    
    if len(obj) >= size:
        return obj
    
    if obj[-1]:
        return pad_ones(obj, size)
    else:
        return pad_zeros(obj, size)
 
