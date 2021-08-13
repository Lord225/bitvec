# PyBytes

Tools written in python for quick bit manipulation on arbitrary sized number. 
It aims to:
* Simpler to manipulate bits than with native python ints
* Correctly wrap numbers in arithmetic operations
* Emulate behavior of unsigned, signed and sign-module 
* Not to be pathetically slow (builded with numpy and numba)

Example use:
```py
from pybytes import *

# creating new number, size is inferred from parameter
x = Binary('0110')
print(x, len(x)) # prints '0110 4'

y = Binary(1, bit_lenght=9) # You can specify any len you want.

# Support for operations
print(int(~(x+y))) # prints 504 (~000000111)

# Arithmetic correctly wraps and you can check the status 
print(ops.overflowing_add(x, '1100')) # overflowing_add return the wrapped sum and boolen to indicate if overflow occurs

x[0] = True  # Set first bit to high
print(x[:3]) # prints first 3 bits

x[:3] = "010" # sets first 3 bits to '010'
print(x) # '0010'
```

This module contains some tools to work with float point numbers

```py
from pybytes import *

f = floats.CustomFloat(preset='fp16') # Create 16 bit float point https://en.wikipedia.org/wiki/Half-precision_floating-point_format
print(f(0.25)) # Convert python float to custom value
print(f('0x3c00')) # prints 1.0 becouse hexadecimal 
print(f(2.0).as_hex()) # prints 2.0 in fp16 in hex

f2 = floats.CustomFloat(mantissa_size=3, exponent_size=3)

print(f2(f2(4.256))) # 4.256 is wraped to 4.0 becouse it is impossible to express with this float.
```
