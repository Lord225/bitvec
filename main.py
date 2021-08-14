import pybytes.floats as fs
import numpy as np

from pybytes import *

import timeit
import math
from pybytes import *

f = floats.CustomFloat(preset='fp16') # Create 16 bit float point https://en.wikipedia.org/wiki/Half-precision_floating-point_format

x = np.linspace(0, 1, 115)
for i in x:
    print(f"{i:0.5f}", f(i))