from typing import Iterable, List, Literal, Tuple, Union
import numpy as np
import numba as nb

@nb.njit(cache=True)
def pad_number_to_size(a: np.ndarray, target_len: int) -> np.ndarray:
    target_size = np.zeros((target_len), dtype=np.uint8)
    target_size[:len(a)] = a
    return target_size
@nb.njit(cache=True)
def pad_to_same_size(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    len_a = len(a)
    len_b = len(b)

    if len_a > len_b:
        arg1 = a
        arg2 = pad_number_to_size(b, len_a)
    elif len_b > len_a:
        arg1 = pad_number_to_size(a, len_b)
        arg2 = b
    else:
        arg1 = a
        arg2 = b
    return (arg1, arg2)
@nb.njit(cache=True)
def bytes_for_number(i: int):
    return bytes_for_len(i.bit_length())
@nb.njit(cache=True)
def bytes_for_len(i: int):
    return int(np.ceil(i/8))
@nb.njit(cache=True)
def get_bit_array(to_mask: np.ndarray, idx: int, lenght: int):
    byte_index = idx//8
    bit_index =  idx%8
    return get_bit(to_mask[byte_index], bit_index)
@nb.njit(cache=True)
def get_bit(to_mask: np.uint8, idx: int) -> bool:
    mask = (1<<idx)
    return mask & to_mask > 0
@nb.njit(cache=True)
def set_bit(to_mask: np.ndarray, idx: int, lenght: int, value: bool):
    byte_index = idx//8
    bit_index = idx%8
    mask = 255 if value else 0
    to_mask[byte_index] ^= (mask ^ to_mask[byte_index]) & (1 << bit_index);
@nb.njit(cache=True)
def set_bits(to_mask: np.ndarray, to_set: np.ndarray, offset: int, lenght: int, size_of_array: int):
    for i in range(lenght):
        set_bit(to_mask, i+offset, size_of_array, get_bit_array(to_set, i, lenght))
@nb.njit(cache=True)
def apply_mask(to_mask: np.ndarray, values: np.ndarray):
    return to_mask&values
@nb.njit(cache=True)
def apply_mask_checked(to_mask: np.ndarray, values: np.ndarray):
    x = to_mask&(~values)
    to_mask = apply_mask(to_mask, values)
    return to_mask, (x!=0).any()
@nb.njit(cache=True)
def get_mask_union(mask_a: np.ndarray, mask_b: np.ndarray):
    return mask_a|mask_b

def format_binary(_data: np.ndarray, to_join: str):
    return to_join.join(((np.binary_repr(i, 8)) for i in reversed(_data)))
def format_hex(_data: np.ndarray, to_join:str):
    return to_join.join("{0:0{1}x}".format(i,2) for i in reversed(_data))
@nb.njit(cache=True, locals={'sum_of_values': nb.float64, 'increment':nb.float64})
def to_float(_data: np.ndarray):
    sum_of_values = 0
    for i, byte in enumerate(_data):
        increment = (2**(8*float(i)))
        sum_of_values += float(byte)*increment
    return sum_of_values

@nb.njit(cache=True)
def leading_zeros(_data: np.ndarray, lenght: int):
    bits_count = lenght%8 if lenght%8 != 0 else lenght
    if _data[len(_data)-1] != 0:
        return bits_count-int(np.floor(np.log2(_data[len(_data)-1])))-1

    for i in range(0, len(_data)):
        index = len(_data)-i-1
        byte = _data[index]
        if byte==0:
            bits_count += 8
        else:
            return bits_count -int(np.floor(np.log2(byte)))-1
    return lenght
@nb.njit(cache=True)
def trailing_zeros(_data: np.ndarray, lenght: int):
    first_non_zero_index = 0
    for i, byte in enumerate(_data):
        if byte != 0:
            first_non_zero_index = i
            break
    else:
        return lenght
    
    no_zero_byte = _data[first_non_zero_index]
    for bx in range(8):
        if get_bit(no_zero_byte, bx) == True:
            return first_non_zero_index*8 + bx
    return 0

@nb.njit(cache=True)
def leading_ones(_data: np.ndarray, lenght: int):
    raise NotImplementedError()
    return 0
@nb.njit(cache=True)    
def trailing_ones(_data: np.ndarray, lenght: int):
    first_non_255_index = 0
    for i, byte in enumerate(_data):
        if byte != 255:
            first_non_255_index = i
            break
    else:
        return lenght
    
    no_zero_byte = _data[first_non_255_index]
    for bx in range(8):
        if get_bit(no_zero_byte, bx) == False:
            return first_non_255_index*8 + bx
    return 0

