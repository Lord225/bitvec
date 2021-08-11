import pybytes.floats as fs
import numpy as np

from pybytes import *

import timeit
import math
f = floats.CustomFloat(10, 5)

print('{:.10f}'.format(f.get_float('0001')))
print(f.get_hex(0.3333333333333333333))
