import pybytes.floats as fs
import numpy as np

from pybytes import *

import timeit
import math

f = floats.CustomFloat(preset='fp16')

print(f.get(0.1))
print(f.get('2e66'))
