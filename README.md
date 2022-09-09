# PyBytes
Quick Start
```
pip install git+https://github.com/Lord225/PyBytes.git
```
Tools written in python for quick bit manipulation on arbitrary sized number. 
It is:
* Simpler to manipulate bits than with native python ints
* Able to correctly wrap numbers in arithmetic operations
* Emulate behavior of unsigned, signed integers
* Written in Rust

# Unittests
```
python -m unittest src\pybytes\tests\binary_test.py
```

Example use:
```py
from pybytes import *

# Creating new number. Size is inferred from leading zeros
x = Binary('0110')
print(f"{x}, lenght: {len(x}") # prints '0110, lenght: 4'

y = Binary(1, bit_lenght=9) # You can specify any len you want.

# prints 504 (~000000111)
print(int(~(x+y))) 

# Arithmetic correctly wraps and you can check the status
# overflowing_add return the wrapped sum and boolen to indicate if overflow occurs
print(ops.overflowing_add(x, '1100')) 

# Set first bit to high
x[0] = True 

# prints first 3 bits
print(x[:3]) 

# sets first 3 bits to '010'
x[:3] = "010" 

# '0010'
print(x) 
```

This module contains some tools to work with float point numbers

```py
from pybytes import *

f = floats.CustomFloat(preset='fp16') # Create 16 bit float point https://en.wikipedia.org/wiki/Half-precision_floating-point_format

# Convert python float to binary value
print(f(0.25)) 

# prints 1.0
print(f('0x3c00'))

# prints 2.0 representation in hex
print(f(2.0).as_hex())

# 1.11_2 * 2**(15-15) = 1.75
print(f(mantissa='11 0000 0000', exponent=15)) 

f2 = floats.CustomFloat(mantissa_size=3, exponent_size=3)

# 4.256 is wraped to 4.0 becouse it is impossible to express with this float.
print(f2(f2(4.256)))

# len in bits of this float (3+3+1 = 7 bits)
print(len(f2)) 
```
