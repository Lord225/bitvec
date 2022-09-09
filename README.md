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
from pybytes import Binary
from pybytes import arithm

# Creating new number. Size is inferred from leading zeros
x = Binary('0110')
print(f"{x}, lenght: {len(x}") # prints '0110, lenght: 4'

y = Binary(1, lenght=9) # You can specify any len you want.

# prints 504 (~000000111)
print(int(~(x+y))) 

# Arithmetic correctly wraps and you can check the status
# overflowing_add return the wrapped sum and boolen to indicate if overflow occurs
print(arithm.overflowing_add(x, '1100')) 

# Set first bit to high
x[0] = True 

# prints first 3 bits
print(x[:3]) 

# sets first 3 bits to '010'
x[:3] = "010" 

# '0010'
print(x) 
```
