import numpy as np
import numba as nb
import binary.common.utils as utils

@nb.njit(cache=True)
def greater_compare_arrays(a: np.array, b: np.array) -> bool:
    arg1, arg2 = utils.pad_to_same_size(a, b)    

    for i in range(len(arg1)-1, -1, -1):
        a = arg1[i]
        b = arg2[i]

        if a==b:
            continue
        if a>b:
            return True
        else:
            return False
    return False

@nb.njit(cache=True)
def less_compare_arrays(a: np.array, b: np.array) -> bool:
    arg1, arg2 = utils.pad_to_same_size(a, b)   

    for i in range(len(arg1)-1, -1, -1):
        a = arg1[i]
        b = arg2[i]

        if a==b:
            continue
        if a<b:
            return True
        else:
            return False
    return False

@nb.njit(cache=True)
def equal_compare_arrays(a: np.array, b: np.array) -> bool:
    arg1, arg2 = utils.pad_to_same_size(a, b)   

    # from low bytes to hi bytes
    for i in range(len(arg1)):
        a = arg1[i]
        b = arg2[i]

        if a!=b:
            return False
    return True
