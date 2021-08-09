import floats as fs
import numpy as np

from binary import *

import timeit

x = Binary("0001", sign_behavior="signed")
y = Binary("0001", sign_behavior="signed")

print(x.maximum_value())
print(x.minimum_value())