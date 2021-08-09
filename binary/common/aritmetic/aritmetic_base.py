from typing import Dict, Tuple
import numpy as np
import numba as nb
import binary.common.utils as utils

@nb.njit(cache=True)
def add_arrays(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray, carry: int = 0) -> Tuple[np.ndarray, bool, bool, bool, bool]:
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)   
    out = np.zeros((len(arg1)), dtype=np.uint8)
    
    overflow = carry
    zero = True
    
    # from low bytes to hi bytes
    for i in range(len(arg1)):
        a = arg1[i]
        b = arg2[i]
        
        byte_sum = nb.types.int32(a) + nb.types.int32(b)+overflow
        out[i] = byte_sum & 255
        
        overflow = 1 if byte_sum > 255 else 0
        zero = False if out[i] != 0 else zero
    
    out, overflow = utils.apply_mask_checked(out, mask)

    return out, bool(overflow), zero, not (out[-1]&128 != 0),out[0]&1==1
@nb.njit(cache=True)
def sub_arrays(rsh: np.ndarray, lsh: np.ndarray, rsh_len: int, lsh_len: int, mask: np.ndarray, sign_behavior: str) -> Tuple[np.ndarray, bool, bool, bool, bool]:
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    len_max = max(rsh_len, lsh_len)

    arg1 = to_signed(arg1, len_max, mask, sign_behavior, False, True)
    arg2 = to_signed(arg2, len_max, mask, sign_behavior, False, True)

    arg2 = bitwise_neg_array(arg2, mask)

    output, of, zf, sf, pf = add_arrays(arg1, arg2, mask, 1)
    
    if sign_behavior == "magnitute":
        output = to_magnitute(output, len_max, mask, "signed", False, True)
    if sign_behavior == "unsigned":
        output = to_unsigned(output, len_max, mask, "signed", False, True)
    return output, of, zf, sf, pf

@nb.njit(cache=True)
def arithmeitc_neg_number(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str) -> np.ndarray:
    value = value.copy()
    if sign_behavior == "unsigned":
        return value
    elif sign_behavior == "magnitute":
        utils.set_bit(value, num_lenght-1, num_lenght, not utils.get_bit_array(value, num_lenght-1, num_lenght))
        return value
    elif sign_behavior == "signed":
        if utils.get_bit_array(value, num_lenght-1, num_lenght):
            value = decrement_array(value, num_lenght, mask, sign_behavior)
            value = bitwise_neg_array(value, mask)
            return value
        else:
            value = bitwise_neg_array(value, mask)
            value = increment_array(value, num_lenght, mask, sign_behavior)
            return value
    return value
@nb.njit(cache=True)
def bitwise_neg_array(rsh: np.ndarray, mask: np.ndarray):
    return utils.apply_mask(np.bitwise_not(rsh), mask)

@nb.njit(cache=True)
def decrement_array(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str):
    output, _, _, _, _ = add_arrays(value, np.full(len(value), 255, dtype=np.uint8), mask, 0)
    return output
@nb.njit(cache=True)
def increment_array(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str):
    output, _, _, _, _ = add_arrays(value, np.zeros(len(value), dtype=np.uint8), mask, 1)
    return output

@nb.njit(cache=True)
def to_signed(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str, abs: bool, allow_overflow: bool) -> np.ndarray:
    value = value.copy()
    if sign_behavior == "unsigned":
        if utils.get_bit_array(value, num_lenght-1, num_lenght) and not allow_overflow:
            raise ValueError("Value overflow.")
        return value
    elif sign_behavior == "signed":
        return value
    elif sign_behavior == "magnitute":
        if utils.get_bit_array(value, num_lenght-1, num_lenght):
            # Negative value
            utils.set_bit(value, num_lenght-1, num_lenght, 0)
            return arithmeitc_neg_number(value, num_lenght, mask, "signed")
        else:
            # Positive value
            utils.set_bit(value, num_lenght-1, num_lenght, 0)
            return value
    return value
@nb.njit(cache=True)
def to_magnitute(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str, abs: bool, allow_overflow: bool) -> np.ndarray:
    value = value.copy()
    if sign_behavior == "unsigned":
        if utils.get_bit_array(value, num_lenght-1, num_lenght) and not allow_overflow:
            raise ValueError("Value overflow.")
        return value 
    elif sign_behavior == "signed":
        if utils.get_bit_array(value, num_lenght-1, num_lenght):
            value = arithmeitc_neg_number(value, num_lenght, mask, "signed")
            utils.set_bit(value, num_lenght-1, num_lenght, 1)
        return value
    elif sign_behavior == "magnitute":
        return value
    return value
@nb.njit(cache=True)
def to_unsigned(value: np.ndarray, num_lenght: int, mask: np.ndarray, sign_behavior: str, abs: bool, allow_overflow: bool):
    value = value.copy()
    if sign_behavior == "unsigned":
        return value
    elif sign_behavior == "signed":
        if utils.get_bit_array(value, num_lenght-1, num_lenght):
            if abs:
                value = arithmeitc_neg_number(value, num_lenght, mask, "signed")
            elif not allow_overflow:  
                raise ValueError("Value overflow.") 
        return value
    elif sign_behavior == "magnitute":
        if utils.get_bit_array(value, num_lenght-1, num_lenght):
            if abs:
                value = arithmeitc_neg_number(value, num_lenght, mask, "magnitute")
            elif not allow_overflow:
                raise ValueError("Value overflow.") 
        return value
    return value

sign_convert = {"unsigned": to_unsigned, "magnitute": to_magnitute, "signed": to_signed}

@nb.njit(cache=True) 
def bitwise_and(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_and(arg1, arg2)
    return utils.apply_mask(out, mask)
@nb.njit(cache=True) 
def bitwise_or(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_or(arg1, arg2)
    return utils.apply_mask(out, mask)
@nb.njit(cache=True) 
def bitwise_xor(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_xor(arg1, arg2)
    return utils.apply_mask(out, mask)
@nb.njit(cache=True) 
def bitwise_nand(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_and(arg1, arg2)
    return bitwise_neg_array(out, mask)
@nb.njit(cache=True) 
def bitwise_nor(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_or(arg1, arg2)
    return bitwise_neg_array(out, mask)
@nb.njit(cache=True) 
def bitwise_xnor(rsh: np.ndarray, lsh: np.ndarray, mask: np.ndarray):
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.bitwise_xor(arg1, arg2)
    return bitwise_neg_array(out, mask)
@nb.njit(cache=True) 
def bitwise_map(rsh: np.ndarray, lsh: np.ndarray, rsh_len: int, lsh_len:int, mask: np.ndarray, map00, map01, map10, map11):
    _map = {
        (False, False): map00, 
        (False, True): map01,
        (True, False): map10,
        (True, True): map11
        }

    _len = max(rsh_len, lsh_len)
    arg1, arg2 = utils.pad_to_same_size(rsh, lsh)
    out = np.zeros((len(arg1)), dtype=np.uint8)
    for i in range(_len):
        bit1 = utils.get_bit_array(arg1, i, _len)
        bit2 = utils.get_bit_array(arg2, i, _len)

        utils.set_bit(out, i, _len, _map[(bit1, bit2)])
    return out

