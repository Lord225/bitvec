import floats as fs
import numpy as np

from binary import *

import timeit

x = Binary("1101 0111", sign_behavior="signed")

print(ops.arithmetic_flaged_lsh(x, 2))