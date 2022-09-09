from typing import Any, Tuple
from .. import Binary

class Flags:
    overflow: bool
    zeroflag: bool
    signflag: bool
    def __init__(self, of, zf, sf): ...

def flaged_add(a: Binary, b: Any) -> Tuple[Binary, Flags]:
    """
    ## flaged_add
    Returns sum of two numbers with flags (in object `Flag`)
        * Zero Flag (number equal to zero)
        * OverFlow Flag (overflow occure)
        * Sign Flag (`out[-1] == True`)
    ```
    >>> flaged_add(u8(255), 1)
    ('00000000', Flags(of=false, zf=true, sf=false))
    ```
    """
    ...
def overflowing_add(a: Binary, b: Any) -> Tuple[Binary, bool]:
    """
    ## overflowing_add
    Returns sum of two numbers with wrapping arithmetic and information if overflow occure
    >>> overflowing_add(u8(1), u2(1))
    ('00000010', False)
    >>> overflowing_add(u8(255), 1) # 11111111 + 1 overflows
    ('00000000', True)
    """
    ...
def wrapping_add(a: Binary, b: Any) -> Binary:
    """
    ## wrapping_add
    Returns sum of two numbers with wrapping arithmetic.
    It is default behavior for `+` operator in `Binary` class
    ```
    >>> wrapping_add(u8(1), u2(1)) # output is 8 bit bsc 8 > 2
    '00000010'
    >>> wrapping_add(u8(255), 1) # 11111111 + 1 overflows
    '00000000'
    ```
    """
    ...

def flaged_sub(a: Binary, b: Any) -> Tuple[Binary, Flags]:
    """
    ## flaged_add
    Returns diffrance of two numbers with flags (in object `Flag`)
        * Zero Flag (number equal to zero)
        * OverFlow Flag (carry flag is true)
        * Sign Flag (`out[-1] == True`)
    ```
    >>> flaged_sub(u8(0), 1)
    ('11111111', Flags(of=true, zf=false, sf=true))
    ```
    It is equivalent of `flaged_add(a, arithmetic_neg(b))`
    """
    ...
def overflowing_sub(a: Binary, b: Any) -> Tuple[Binary, bool]:
    """
    ## overflowing_sub
    Returns diffrance of two numbers with wrapping arithmetic and information if carry was true
    >>> overflowing_sub(u8(1), u2(1))
    ('00000000', False)
    >>> overflowing_sub(u8(0), 1) #
    ('11111111', True)
    """
    ...
def wrapping_sub(a: Binary, b: Any) -> Binary:
    """
    ## overflowing_sub
    Returns diffrance of two numbers with wrapping arithmetic and information if carry was true
    >>> wrapping(u8(1), u2(1))
    '00000000'
    >>> overflowing_sub(u8(-128), 1).int()
    127
    """
    ...

def cast(binary: Binary, to_type: str) -> Binary:
    """
    ## cast
    Cast bit-wise an binary number to another type with same lenght
    ```
    >>> cast(u8(255), 'signed').int()
    -1
    >>> cast(i8(-1), 'unsigned').int()
    255
    ```
    ## similar functions
    * `convert` - convert binary to another sign behavior, rises if overflow
    * `extend_to_signed` - extend binary to signed behavior, adds bit if signed number cannot handle
    * `pad_zeros` - pad binary with zeros to given size
    * `pad_ones` - pad binary with ones to given size
    * `pad_sign_extended` - pad binary with `sign_extending_bit` to given size

    """
    ...
def convert(binary: Binary, to_type: str) -> Binary:
    """
    ## convert
    Convert binary to another sign behavior, rises if overflow
    ```
    >>> convert(u8(127), 'signed').int()
    127
    >>> convert(u8(128), 'signed').int()
    # ** rises ** signed 8bit value cannot handle 128
    >>> convert(u8(-1), 'unsigned').int()
    # ** rises ** unsigned numbers cannot handle negative values
    ```
    ## similar functions
    * `cast` - bit-wise cast to other sign behavior
    * `extend_to_signed` - extend binary to signed behavior, adds bit if signed number cannot handle
    * `pad_zeros` - pad binary with zeros to given size
    * `pad_ones` - pad binary with ones to given size
    * `pad_sign_extended` - pad binary with `sign_extending_bit` to given size
    """
    ...

def extend_to_signed(binary: Binary) -> Binary:
    """
    ## extend_to_signed
    Extend binary to signed behavior, adds bit if signed number cannot handle
    ```
    >>> extend_to_signed(u8(127)).int()
    127
    >>> extend_to_signed(u8(128)).int()
    -128
    >>> extend_to_signed(u8(-1)).int()
    -1
    ```
    ## similar functions
    * `cast` - bit-wise cast to other sign behavior
    * `convert` - convert binary to another sign behavior, rises if overflow
    * `pad_zeros` - pad binary with zeros to given size
    * `pad_ones` - pad binary with ones to given size
    * `pad_sign_extended` - pad binary with `sign_extending_bit` to given size
    """
    ...
def pad_zeros(binary: Binary, size: int) -> Binary:
    """
    ## pad_zeros
    Pad binary with zeros to given size. Ignores sign_behavior
    ```
    >>> pad_zeros(u8(1), 16).int()
    1
    >>> pad_zeros(u8(1), 16).bin()
    '0000000000000001'
    ```
    ## similar functions
    * `cast` - bit-wise cast to other sign behavior
    * `convert` - convert binary to another sign behavior, rises if overflow
    * `extend_to_signed` - extend binary to signed behavior, adds bit if signed number cannot handle
    * `pad_ones` - pad binary with ones to given size
    * `pad_sign_extended` - pad binary with `sign_extending_bit` to given size
    """
    ...
def pad_ones(binary: Binary, size: int) -> Binary:
    """
    ## pad_ones
    Pad binary with ones to given size. Ignores sign_behavior
    ```
    >>> pad_ones(u8(1), 16).int()
    1
    >>> pad_ones(u8(1), 16).bin()
    '1111111111111111'
    ```
    ## similar functions
    * `cast` - bit-wise cast to other sign behavior
    * `convert` - convert binary to another sign behavior, rises if overflow
    * `extend_to_signed` - extend binary to signed behavior, adds bit if signed number cannot handle
    * `pad_zeros` - pad binary with zeros to given size
    * `pad_sign_extended` - pad binary with `sign_extending_bit` to given size
    """
    ...
def pad_sign_extend(binary: Binary, size: int) -> Binary:
    """
    ## pad_sign_extend
    Pad binary with `sign_extending_bit` to given size. Ignores sign_behavior
    ```
    >>> pad_sign_extend(u8(1), 16)
    '0000000000000001'
    >>> pad_sign_extend(u8(1), 16)
    '0000000000000001'
    >>> pad_sign_extend(u8(-1), 16)
    '1111111111111111'
    ```
    ## similar functions
    * `cast` - bit-wise cast to other sign behavior
    * `convert` - convert binary to another sign behavior, rises if overflow
    * `extend_to_signed` - extend binary to signed behavior, adds bit if signed number cannot handle
    * `pad_zeros` - pad binary with zeros to given size
    * `pad_ones` - pad binary with ones to given size
    """
    ...

def arithmetic_neg(binary: Binary) -> Binary:
    """
    ## arithmetic_negate
    Negate binary number using two's complement arithmetic (~X + 1)
    It has same effect as `wrapping_add(bitwise_neg(X), 1)`.
    ```
    >>> arithmetic_negate(u8(1))
    '11111111'
    >>> arithmetic_negate(u8(-1))
    '00000001'
    ```
    """
    ...
def bitwise_not(binary: Binary) -> Binary:
    """
    ## bitwise_negate
    Negate binary number using bitwise negation (~X)
    ```
    >>> bitwise_negate(u8(1))
    '11111110'
    >>> bitwise_negate(u8(-1))
    '00000000'
    ```
    """
    ...

def bitwise_or(binary: Binary) -> Binary:
    """
    ## bitwise_or
    Bitwise OR of binary numbers
    ```
    >>> bitwise_or(u8(1), u8(2))
    '00000011'
    ```
    """
    ...
def bitwise_and(binary: Binary) -> Binary:
    """
    ## bitwise_and
    Bitwise AND of binary numbers
    ```
    >>> bitwise_and(u8(1), u8(2))
    '00000000'
    >>> bitwise_and(u8(1), u8(1))
    '00000001'
    ```
    """
    ...
def bitwise_xor(binary: Binary) -> Binary:
    """
    ## bitwise_xor
    Bitwise XOR of binary numbers
    ```
    >>> bitwise_xor(u8(1), u8(2))
    '00000011'
    >>> bitwise_xor(u8(1), u8(1))
    '00000000'
    ```
    """
    ...

def overflowing_lsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:
    """
    ## overflowing_lsh
    Left shift binary number by given amount of bits. Returns tuple of (result, overflow)
    ```
    >>> overflowing_lsh(u8('0100 1010'), 0)
    ('01001010', '')
    >>> overflowing_lsh(u8('0100 1010'), 1)
    ('10010100', '0')
    >>> overflowing_lsh(u8('0100 1010'), 2)
    ('00101000', '01')
    ```
    """
    ...
def wrapping_lsh(a: Binary, b: Any) -> Binary:
    """
    ## wrapping_lsh
    Left shift binary number by given amount of bits. Returns only shifted bits discarding overflow
    ```
    >>> wrapping_lsh(u8('0100 1010'), 0)
    '01001010'
    >>> wrapping_lsh(u8('0100 1010'), 1)
    '10010100'
    >>> wrapping_lsh(u8('0100 1010'), 2)
    '00101000'
    ```
    """
    ...
def logical_underflowing_rsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:
    """
    ## logical_underflowing_rsh
    Logical right shift binary number by given amount of bits. Returns tuple of (result, underflow).
    Bits from left are filled with zeros.
    ```
    >>> logical_underflowing_rsh(u8('0100 1010'), 0)
    ('01001010', '')
    >>> logical_underflowing_rsh(u8('0100 1010'), 1)
    ('00100101', '0')
    >>> logical_underflowing_rsh(u8('0100 1010'), 2)
    ('00010010', '10')
    ```
    """
    ...
def logical_wrapping_rsh(a: Binary, b: Any) -> Binary:
    """
    ## logical_wrapping_rsh
    Logical right shift binary number by given amount of bits. Returns only shifted bits discarding underflow.
    Bits from left are filled with zeros.
    ```
    >>> logical_wrapping_rsh(u8('0100 1010'), 0)
    '01001010'
    >>> logical_wrapping_rsh(u8('0100 1010'), 1)
    '00100101'
    >>> logical_wrapping_rsh(u8('0100 1010'), 2)
    '00010010'
    ```
    """
    ...
def arithmetic_underflowing_rsh(a: Binary, b: Any) -> Tuple[Binary, Binary]:
    """
    ## arithmetic_underflowing_rsh
    Arithmetic right shift binary number by given amount of bits. Returns tuple of (result, underflow).
    Bits from left are filled with sign bit if number is signed, otherwise with zeros.
    ```
    >>> arithmetic_underflowing_rsh(i8('0100 1010'), 0)
    ('01001010', '')
    >>> arithmetic_underflowing_rsh(i8('0100 1010'), 1)
    ('00100101', '0')
    >>> arithmetic_underflowing_rsh(i8('0100 1010'), 2)
    ('00010010', '10')
    >>> arithmetic_underflowing_rsh(i8('1100 1010'), 0)
    ('11001010', '')
    >>> arithmetic_underflowing_rsh(i8('1100 1010'), 1)
    ('11100101', '0')
    >>> arithmetic_underflowing_rsh(i8('1100 1010'), 2)
    ('11110010', '10')
    ```
    """
    ...
def arithmetic_wrapping_rsh(a: Binary, b: Any) -> Binary:
    """
    ## arithmetic_wrapping_rsh
    Arithmetic right shift binary number by given amount of bits. Returns only shifted value (discards overflow)
    Bits from left are filled with sign bit if number is signed, otherwise with zeros.
    ```
    >>> arithmetic_wrapping_rsh(i8('0100 1010'), 0)
    '01001010'
    >>> arithmetic_wrapping_rsh(i8('0100 1010'), 1)
    '00100101'
    >>> arithmetic_wrapping_rsh(i8('0100 1010'), 2)
    '00010010'
    >>> arithmetic_wrapping_rsh(i8('1100 1010'), 0)
    '11001010'
    >>> arithmetic_wrapping_rsh(i8('1100 1010'), 1)
    '11100101'
    >>> arithmetic_wrapping_rsh(i8('1100 1010'), 2)
    '11110010'
    ```
    """