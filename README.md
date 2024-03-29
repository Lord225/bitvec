# BitVec
Tools written for python for fast and simple bit manipulation
It is:
* Simpler to manipulate bits than with native python ints
* Able to correctly wrap numbers in arithmetic operations
* Emulate behavior of unsigned, signed integers
* Unit-tested 
* Written in Rust (Some operations are quite fast)
## Installation
```
pip install bitvec
```
# Unittests
```
python -m unittest python\tests\tests.py
```
# PyPi
```
https://pypi.org/project/bitvec/
```

Example use:
```py
from bitvec import Binary
from bitvec import arithm

# Creating new number. Size is inferred from leading zeros
x = Binary('0110')
y = Binary(1, lenght=9) # You can specify len too

print(f"{x}, lenght: {len(x)}") # prints '0110, lenght: 4'

print(int(~(x+y))) # prints 504 (0b111111000)

# Arithmetic correctly wraps and you can check the status
# overflowing_add return the wrapped sum and boolen to indicate if overflow occurs
print(arithm.overflowing_add(x, '1100')) # (0010, True)

# Set first bit to high
x[0] = True 

# slice bits
print(x[:3]) # ('111')

# sets first 3 bits to '001'
x[:3] = "001" 

# convert to hex
print(x.hex()) # '0x1'

# every second bit of '0001' 
print(x[::2]) # '01'    ^ ^

# you can quickly iterate over bits, bytes or any other chunk of bits with .iter(size) function
for i in x.iter(2):
    print("Chunk of two bits: ", i) # i is `01` then `00`

# count all zeros
print(x.count_zeros())  # prints 3

# find indexes of all zeros
print(x.find_all('0')) # prints [1, 2, 3] 
```

# Brief docs

## Binary
Class that represent numbers in binary. Wraps arithmetic to bouds of the binary number, 
allows for quick and easy bit manipulation.
### Parameters
* object - Any object that can be somehow converted to binary number. 
Including its representation as string, int, boolean, list of boolean-convertable values, byte-arrays, numpy arrays ect.
* lenght - Target lenght of the number in bits. This number can be inferred from object based on its value, extra zeros ect
* bytes_lenght - Target lenght of the number in bytes. Same as lenght but in bytes.
* sign_behavior - How number should implement sign.
## Examples

```py
>>> from bitvec import Binary
>>> Binary("0110") # From string representing binary number. Following zeros are used to inherit len of number.
'0110'
>>> Binary(4, lenght=8) # Crate number with 8 bits, 4 is converted to binary and padded with zeros.
'00000100'
>>> Binary(255)
'11111111'
>>> Binary([True, 0, 1, 1.0]) # From array of boolean-likes
'1011'
>>> Binary("0000 0001") # Ignores whitespace
'00000001'
>>> Binary("ff Aa C   C") # Works with hex too
'11111111 10101010 11001100'
```

## Alias
Module defines factories with predefined sizes and behaviors like u8, u16, i16, i64 ect. These ones can be used as followed:
```py
>>> from bitvec.alias import u8
>>> u8(3)
'00000011'
```
### Conversion
```py
>>> num = Binary("FA") # 11111010
```
To string (formatted binary)
```py
>>> str(num) # Returns just bits
'11111010'
>>> bin(num)
'0b11111010'
>>> num.bin()
'0b11111010'
>>> num.bin(prefix=False) # remove prefix 
'11111010'
>>> hex(num)
'0xfa'
>>> num.hex()
'0xfa'
>>> num.hex(prefx=False)
'fa'
```
```py
>>> int(num)
250
>>> num.int()
250
```

To boolean (`False` when `0`)
```py
>>> bool(num)
True
```

## Indexing and Access
### Index
Bits of the number can be accessed throught index:
```py
>>> num = Binary("FA") # 11111010
>>> num[0], num[1], num[2] # First 3 bits of the number
(False, True, False)
>>> num[-1] # Last bit
True
```

### Slice
```py
>>> num[:3] # from start to 3th bit (first 3 bits)
'010'
>>> num[-6:] # from 6th bit from the end to end (last 6 bits)
'111110'
>>> num[-6:-2] # From 6th bit from end to 2st bit from end
'1110'
>>> num[2:] # Skip first 2 bits
'111110'
>>> num[:16] # First 16 bits (padded with zeros)
'00000000 11111010'
>>> num[::2] # Every other bit
'1100'
>>> num[::-1] # Reversed
'01011111'
>>> num[[1,3]] # Get second and 4th bit
'11'
```
*NOTE* that behavior of slicing is slighty diffrent from slicing pythons `str` or list, first bit is from far right, not left. You can also exeed len of the value, in this case added bits will be padded with sign extending bit (`0` for unsigned, `sign_bit` for singed)

Note that slicing makes a copy of the vector

## Public Methods
### Aliases for slicing number
* `high_byte()` - second 8bits (from 8th to 16th)
* `low_byte()` - first 8bits (from start to 8th)
* `extended_low()` - first 16bits
* `extended_high()` - second 16bits
* `get_byte(index: int)` - nth group of 8-bit chunks.
* `split_at(index: int)` - split number at nth bit.
### Information about number
* `sign_behavior()` - The way that number behaves on extending and converstions `signed` or `unsigned` 
* `maximal_value()` - Maximal possibe value than can be hold in this representation and lenght
* `minimal_value()` - Minimal possibe value than can be hold in this representation and lenght
* `is_negative()` - Returns if number is negative
* `sign_extending_bit()` - Returns the boolean that will be used to extend this value to left 
* `hex(prefix: bool=True)` - hex representation of this number
* `bin(prefix: bool=True)`- bin representation of this number
* `int()` - casted to python integer
### Searching & Finding Patterns
* `leading_zeros()` - Amount of leading zeros in the number
* `trailing_zeros()` - Amount of trailing zeros in the number
* `leading_ones()` - Amount of leading ones in the number
* `trailing_ones()` - Amount of trailing ones in the number
* `find(sub: bool|int|str|Binary)` - Find first occurence (index) of the pattern
* `find_all(sub: bool|int|str|Binary)` - Find all occurences (index) of the pattern
* `find_zeros()` - Find indexes of zeros
* `find_ones()` - Find indexes of ones
* `count_zeros()` - count how many zeros is in number
* `count_ones()` - count how many ones is in number
### Modifying
* `append(Binary|bool|str|int)` - Appends value to the end
* `prepend(Binary|bool|str|int)` - Appends vakue to the start
* `join(Binary|bool|str|int)` - Joins binary numbers like str.join does
### Iterating
* `bits()` - iterates over bits
* `bytes()` - iterates over bytes
* `iter()` - iterates over chunks or n bits 

### Modify by Index
You can modify bits with indexes:
```py
>>> num = Binary(0, lenght=8)
>>> num[0] = True # Set first bit to high
>>> num[1] = True # Set second bit to high
>>> num
'00000011'
>>> num[-1] = True # Set last bit to high
>>> num
'10000011'
>>> num[0] = 0 # Set first bit to low
>>> num
'10000010'
```

### Modify by Slice
You can select bits by slice and set them, or copy from other number
```py
>>> num = Binary(0, lenght=8)
>>> num[:3] = True
>>> num
'00000111'
>>> num[:3] = "101" # Insert 101 in place of first 3 bits of the number
>>> num
'00000101'
>>> num[5:8] = "111" # insert 111 in place of bits 5th 6th 7th
>>> num
'11100101'
>>> num[:] = 0 # Set all bits to 0
>>> num
'00000000'
```
### Modify by indeces
```py
>>> num = Binary(0, lenght=8)
>>> num[[1,2,3]] = True # Set first, second and third bit to True
>>> num
>>> '0000 1110'
```

There is few rules
* If right side of the slice is convertable to Binary, it will be converted to binary and inserted in place of the selected bits.
* If size of the converted value will be greater than size of the selected bits, it will throw an error.
* If right side is boolean the assigment will set all selectet bits to this value.
* step value is not supported.

## Iterating over bits or chunks
You can iterate over bits of the number:
```py
>>> num = Binary("FA") # 11111010
>>> for bit in num: # or num.bits()
...     print(bit, end=" ")  # bit is Binary class with lenght equal to 1 
0 1 0 1 1 1 1 1
```

Or over bytes:
```py
>>> num = Binary("FA") # 11111010
>>> list(num.extended_low().bytes())
[11111010, 00000000] 
```
Or over any other chunk of bits with `iter` function. For more sophisticated iteration you can use `itertools` or just play with indexing and slicing.

## Arithm  
In module `arithm` there are functions that can be used to perform arithmetic/logical operations on binary numbers. That's includes
### add
* `flaged_add(a: Binary, b: Any) -> Tuple[Binary, Flags]:` - add, and return with flags (of, zf, sf)
* `overflowing_add(a: Binary, b: Any) -> Tuple[Binary, bool]:` - add and return overflow flag too
* `wrapping_add(a: Binary, b: Any) -> Binary:` - add and return only result
### sub
* `flaged_sub(a: Binary, b: Any) -> Tuple[Binary, Flags]:` - sub, and return with flags (of, zf, sf)
* `overflowing_sub(a: Binary, b: Any) -> Tuple[Binary, bool]:` - sub and return overflow flag too
* `wrapping_sub(a: Binary, b: Any) -> Binary:` - sub and return only result
### converting
* `cast(binary: Binary, to_type: str) -> Binary:` - change sb without any checks ('transmutate' value)
* `convert(binary: Binary, to_type: str) -> Binary:` - change sb and rise if conversion is impossible
* `extend_to_signed(binary: Binary) -> Binary:` - change to sb and add sign bit if nessesery
* `pad_zeros(binary: Binary, size: int) -> Binary:` - add zeros to match the lenght
* `pad_ones(binary: Binary, size: int) -> Binary:` - add ones to match the lenght
* `pad_sign_extend(binary: Binary, size: int) -> Binary:` - add sign extending bits to match the lenght
* `concat(*args: Any) -> Binary:` - concats args into one long binary
### Neg
* `arithmetic_neg(binary: Binary) -> Binary:` - negates number with 2's logic
* `bitwise_neg(binary: Binary) -> Binary:` - flips bits
### bitwise
* `bitwise_or(binary: Binary, b: Any) -> Binary:`
* `bitwise_and(binary: Binary, b: Any) -> Binary:`
* `bitwise_xor(binary: Binary, b: Any) -> Binary:`
* `bitwise_xnor(binary: Binary, b: Any) -> Binary:`
* `bitwise_nand(binary: Binary, b: Any) -> Binary:`
* `bitwise_nor(binary: Binary, b: Any) -> Binary:`
* `bitwise_map(*args: Any, map: Binary|str|int|dict[Binary|str|int, bool]) -> Binary:` - maps bits by sum-of-products table 
### multiply
* `multiply(binary: Binary, b: Any) -> Binary:` - mul and returns whole result
* `overflowing_mul(binary: Binary, b: Any) -> Tuple[Binary, Binary]:` - mul and returns splited result
* `wrapping_mul(binary: Binary, b: Any) -> Binary:` - mul and returns only `len(binary)` first bits
### shifts
* `overflowing_lsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:` - left shifts, returns result and shifted out bits
* `wrapping_lsh(a: Binary, b: Any) -> Binary:` - left shifts, returns result and discards shifted out bits
* `logical_underflowing_rsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:` - right shift padded with zeros, returns result and shifted out bits
* `logical_wrapping_rsh(a: Binary, b: Any) -> Binary:` - right shift padded with zeros, returns result and discards shifted out bits
* `arithmetic_underflowing_rsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:` - right shift paded sign extending bits, returns result and shifted out bits
* `arithmetic_wrapping_rsh(a: Binary, b: Any) -> Binary:` - right shift paded sign extending bits, returns result and discards shifted out bits

```py
>>> from bitvec import arithm
>>> arithm.wrapping_add(u4("1111"), "0001") 
'0000' # 15 + 1 = 16, but we have only 4 bits, so we wrap around and get 0
>>> arithm.overflowing_add(u4("1111"), "0001")
('0000', True) # If you want to know if there was overflow, use overflowing_add
>>> arithm.overflowing_lsh(u8('0100 1010'), 2)
('00101000', '01') # 0100 1010 << 2 = 0010 1000, but we have only 8 bits, so we wrap around to get 0010 1000, and we have 2 'wrapped' bits from left, so we return them as second value
```
Some functions are implemented for Binary class (usually wrapping ones), so you can use them directly with operators number:

```py
>>> u8("0100 1010") + u8("0000 0010")
'0100 1100'
```
That includes:
* `__add__`, `__sub__`, `__mul__`, `__lshift__`, `__rshift__`, `__and__`, `__or__`, `__xor__`, `__invert__`, `__neg__`

## Creating numbers - details 
* If you didn't specify lenght, it will be calculated from value
    * For string it will be lenght of string including leading zeros/ones
    * For int it will be minimal lenght of binary representation of the number
* If you specify lenght, it will be used but if value is longer, it will raise an error

This module assumes that for `signed` numbers the most significant bit is sign bit. So for signed number with lenght of `1` (so we have `only` sign_bit that has weight equal to `-1`) possible values will be `0` and `-1`
Numbers with lenght of `0` will be always treated as `0`
### Examples
```py
>>> Binary(0                        )  # lenght will be 0, displayed as ''
>>> Binary(0,               lenght=1)  # lenght will be 1, displayed as '0'
>>> Binary(0,               lenght=2)  # lenght will be 2, displayed as '00'
>>> Binary(0,  signed=True          )  # lenght will be 0, displayed as '0'
>>> Binary(0,  signed=True, lenght=1)  # lenght will be 1, displayed as '0'
>>> Binary(-1, signed=True, lenght=1)  # lenght will be 1, displayed as '1'
>>> Binary(-1, signed=True, lenght=2)  # lenght will be 2, displayed as '11'
>>> Binary(1,  signed=True          )  # lenght will be 2, displayed as '01'
```

This behavior is based on the interpretation of the number as a signed integer where sign bit is treated as it has negative weight
```txt
for unsigned:

0 0 0 0
 \ \ \ \_ weight 1
  \ \ \__ weight 2
   \ \___ weight 4
    \____ weight 8
Value = sum of weights of bits set to 1
```

```txt
for signed:
    
0 0 0 0
 \ \ \ \_ weight  1
  \ \ \__ weight  2
   \ \___ weight  4
    \____ weight -8
Value = sum of weights of bits set to 1
```

```txt
for size 1
unsigned:
0
 \_ weight 1
signed:
0
 \_ weight -1 (last bit)
```
And zero-lenght number just fills up the pattern well.
