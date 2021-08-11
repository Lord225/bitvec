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
    def isZero(self) -> bool:
        return bool(self.zf)
    def isOverflow(self) -> bool:
        return bool(self.of)
    def isSign(self) -> bool:
        return bool(self.sf)
    def isPartity(self) -> bool:
        return bool(self.pf)
    def __repr__(self) -> str:
        return f"Flags(of={self.isOverflow()},zf={self.isZero()},sf={self.isSign()},pf={self.isPartity()})"


def wrapping_add(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = overflowing_add(rsh, lsh)
    return out
def overflowing_add(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_add(rsh, lsh)
    return out, of
def flaged_add(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    out_data, of, zf, sf, pf = alu_base.add_arrays(rsh._data, lsh._data,new_mask, carry=0)
    return binary_class.Binary(out_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior), Flags(of, zf, sf, pf)

def wrapping_sub(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = overflowing_sub(rsh, lsh)
    return out
def overflowing_sub(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  flaged_sub(rsh, lsh)
    return out, of
def flaged_sub(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, Flags]:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)

    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()

    out_data, of, zf, sf, pf = alu_base.sub_arrays(rsh._data, lsh._data, rsh._len, lsh._len, new_mask, rsh._sign_behavior)
    
    return binary_class.Binary(out_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior), Flags(of, zf, sf, pf)

def flaged_mul(rsh: binary_class.Binary, lsh: object)-> Tuple[binary_class.Binary, Flags]:
    pass

def bitwise_not(tar: binary_class.Binary):
    _not_data = alu_base.bitwise_neg_array(tar._data, tar._mask)
    return binary_class.Binary(_not_data, bit_lenght=tar._len, sign_behavior=tar._sign_behavior)
def arithmetic_neg(tar: binary_class.Binary):
    _neg_data = alu_base.arithmeitc_neg_number(tar._data, tar._len, tar._mask, tar._sign_behavior)
    return binary_class.Binary(_neg_data, bit_lenght=tar._len, sign_behavior=tar._sign_behavior)

def bitwise_and(rsh: binary_class.Binary, lsh: object):
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_and(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_or(rsh: binary_class.Binary, lsh: object):
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    if lsh._sign_behavior != rsh._sign_behavior:
        raise ValueError()
    new_mask = utils.get_mask_union(rsh._mask, lsh._mask)
    new_len = max(rsh._len, lsh._len)
    new_data = alu_base.bitwise_or(rsh._data, lsh._data, new_mask)
    return binary_class.Binary(new_data, bit_lenght=new_len, sign_behavior=lsh._sign_behavior)
def bitwise_xor(rsh: binary_class.Binary, lsh: object):
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
    new_data = alu_base.sign_convert[sign_behavior](tar._data, tar._len, tar._mask, tar._sign_behavior, False)
    return binary_class.Binary(new_data, bit_lenght=tar._len, sign_behavior=sign_behavior)
def cast(tar: binary_class.Binary, sign_behavior: Literal["unsigned", "magnitude", "signed"]):
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

def arithmetic_wrapping_lsh(rsh: binary_class.Binary, lsh: object) -> binary_class.Binary:
    out, _ = arithmetic_overflowing_lsh(rsh, lsh)
    return out
def arithmetic_overflowing_lsh(rsh: binary_class.Binary, lsh: object) -> Tuple[binary_class.Binary, bool]:
    out, (of, _, _, _) =  arithmetic_flaged_lsh(rsh, lsh)
    return out, of
def arithmetic_flaged_lsh(rsh: binary_class.Binary, lhs: object) -> Tuple[binary_class.Binary, Flags]:
    lsh_casted = int(cast(lhs, "unsigned")) if isinstance(lhs, binary_class.Binary) else int(lhs)

    sign_bit = rsh.is_negative()
    rhs = cast(rsh, 'unsigned')
    rhs[-1] = False

    output, flags = flaged_lsh(rhs, lsh_casted)
    
    if output[-1]:
        flags.of = True

    output[-1] = sign_bit
    
    return output, flags

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
