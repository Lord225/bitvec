from typing import Any, Iterable, Literal, Optional, overload
from . import arithm

class Binary:
    _data: bytes
    len: int
    _sign_behavior: Literal['unsigned', 'signed']

    def __init__(self, object: object = None, lenght: Optional[int]=None, sign_behavior: Optional[Literal["unsigned", "signed"]] = None, byte_lenght: Optional[int] = None, signed: Optional[bool]=None):
        """## Binary
            Class that represent numbers in binary. Wraps arithmetic to bouds of the binary number, 
            allows for quick and easy bit manipulation.
            ### Parameters
            * object - Any object that can be somehow converted to binary number. 
            Including its representation as string, int, boolean, list of boolean-convertable values, byte-arrays, numpy arrays ect.
            * lenght - Target lenght of the number in bits. This number can be inferred from object based on its value, extra zeros ect
            * bytes_lenght - Target lenght of the number in bytes. Same as lenght but in bytes.
            * sign_behavior - How number should implement sign.
            ## Examples
            
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
            ### Alias
            Module defines factories with predefined sizes and behaviors like u8, u16, i16, i64 ect. These ones can be used as followed:
            
            >>> u8(3)
            '00000011'
        
            ### Conversion

            >>> num = Binary("FA") # 11111010
            To string (formatted binary)
            >>> str(num)
            >>> bin(num)
            '0b11111010'
            >>> num.bin()
            '0b11111010'
            >>> hex(num)
            '0xfa'
            >>> num.hex()
            '0xfa'

            >>> int(num)
            250
            >>> num.int()
            To boolean (`False` when `0`)
            >>> bool(num)
            True

            ## Indexing and Access
            ### Index
            Bits of the number can be accessed throught index:
            
            >>> num = Binary("FA") # 11111010
            >>> num[0], num[1], num[2] # First 3 bits of the number
            (False, True, False)
            >>> num[-1] # Last bit
            True
            ### Slice
            
            >>> num[:3] # from start to 3th bit (first 3 bits)
            '010'
            >>> num[-6:] # from 6th bit from the end to start (last 6 bits)
            '111110'
            >>> num[-6:-2] # From 6th bit from end to 2th bit from end
            '1110'
            >>> num[2:] # Skip first 2 bits
            '111110'
            *NOTE* that behavior of slicing is slighty diffrent from slicing pythons `str` or list, first bit is from far right, not left.
            
            ## Public Methods
            ### Aliases for slicing number:
            * high_byte
            * low_byte
            * extended_low
            * extended_high
            * get_byte
            ### Information about number
            * sign_behavior
            * maximal_value
            * minimal_value
            * leading_zeros
            * trailing_zeros
            * is_negative
            * sign_extending_bit
            * hex
            * bin
            * int
            ### Modifying
            * append
            * prepend
            * strip
            * strip_right
            ### Iterating
            * bits()
            * bytes()
            
            ### Modify by Index
            You can modify bits with indexes:
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
            
            ### Modyfy by Slice
            You can select bits by slice and set them, or copy from other number
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
            There is few rules
            * If right side of the slice is convertable to Binary, it will be converted to binary and inserted in place of the selected bits.
            * If size of the converted value will be greater than size of the selected bits, it will throw an error.
            * If right side is boolean the assigment will set all selectet bits to this value.
            * step value is not supported.

            ## Iterating

            '00100110'
            ### Arithmetic  
            ## See also
        """
        ...

    def sign_behavior(self) -> Literal['unsigned', 'signed']:
        """
        ## sign_behavior
        Returns sign behavior of the number.
        >>> Binary("11111111").sign_behavior()
        'unsigned'
        >>> Binary("11111111", signed=True).sign_behavior()
        'signed'
        """
        ...
    def is_negative(self) -> bool: 
        """
        ## is_negative
        Returns true if number is negative.
        >>> Binary("11111111").is_negative()
        False
        >>> Binary("11111111", signed=True).is_negative()
        True
        """
        ...
    def sign_extending_bit(self) -> bool:
        """
        ## sign_extending_bit
        Returns bit that is used for sign extending.
        >>> Binary("1111").sign_extending_bit()
        False
        >>> Binary("0000", signed=True).sign_extending_bit()
        False
        >>> Binary("1000", signed=True).sign_extending_bit()
        True
        """
        ...
    def minimum_value(self) -> int: 
        """
        ## minimum_value
        Returns minimal value for current size of the number
        >>> Binary("11111111").minimum_value()
        0
        >>> Binary("00000000", signed=True).minimum_value()
        -127
        """
        ...
    def maximum_value(self) -> int:
        """Returns maximal value for current size of the number
        >>> Binary(0, lenght=8).maximum_value()
        255
        >>> Binary(0, lenght=8, signed=True).maximum_value()
        127
        """
        ...

    def append(self, value: bool|int|str|Binary):
        """
        ## append
        appends value to the end of the number
        >>> Binary('0101').append('111')
        '1110101' 
        """
        ...
    def prepend(self, value: bool|int|str|Binary):
        """
        ## prepend
        appends value to the start of the number
        >>> Binary('0101').prepend('111')
        '0101111' 
        """
        ...

    def hex(self) -> str:
        """
        ## hex
        Returns hex representation of the number with prefix. It does not add negative sign.
        It is an alias for `__hex__` method
        >>> Binary("11111111").hex()
        '0xff'
        ## Similar methods
        * __hex__
        * bin
        * int
        """
        ...
    def bin(self) -> str: 
        """
        ## bin
        Returns binary representation of the number with prefix. It does not add negative sign.
        It is an alias for `__bin__` method
        >>> Binary("11111111").bin()
        '0b11111111'
        """
        ...
    def int(self) -> int:
        """
        ## int
        Returns binary value as integer.
        It is an alias for `__int__` method
        >>> Binary("11111111").int()
        255
        """
        ...
    
    def __hex__(self) -> str: ...
    def __bin__(self) -> str: ...
    def __int__(self) -> int: ...
    
    def low_byte(self) -> Binary:
        """
        ## low_byte
        Returns first 8bit of the number. Padded with sign extending bit.
        >>> Binary("101").low_byte()
        '00000101'

        ## Similar methods
        * `low_byte` - first 8bit
        * `high_byte` - second 8bit
        * `extended_low` - first 16bit
        * `extended_high` - second 16bit
        """
        ...
    def high_byte(self) -> Binary:
        """
        ## high_byte
        Returns second 8bit of the number. Padded with sign extending bit.
        >>> Binary("101").high_byte()
        '00000000'
        """
        ...
    def extended_low(self) -> Binary:
        """
        ## extended_low
        Returns first 16bit of the number. Padded with sign extending bit.
        >>> Binary("1111 1111 1111").extended_low()
        '0000 0000 1111 1111 1111'
        """
        ...
    def extended_high(self) -> Binary:
        """
        ## extended_high
        Returns second 16bit of the number. Padded with sign extending bit.
        >>> Binary("1 1111 1111 1111 1111").extended_high() # 17 bits
        '0000 0000 0000 0000 0001'
        """
        ...

    def bits(self) -> BinaryIterator: 
        """
        ## bits
        Returns iterator that iterates over bits. It is alias for `__iter__` method
        >>> [i for i in Binary("101").bits()]
        [1, 0, 1]
        >>> b0, b1, b2 = Binary("101")
        """
        ...
    def bytes(self) -> BinaryIterator:
        """
        ## bytes
        Returns iterator that iterates over bytes. additional bits will be padded with sign exteding bit. It is alias for `__iter__` method
        >>> [i for i in Binary("101").bytes()]
        ['00000101']
        >>> for b7,b6,b5,b4,b3,b2,b1,b0 in Binary("101").bytes(): print(b1,b2,b3,b4,b5,b6,b7,b8)
        """
        ...
    def iter(self, block_size: int) -> BinaryIterator:
        """
        ## iter
        Returns iterator that iterates over blocks of size block_size. 
        
        Additional bits will be padded with sign exteding bit.
        
        Functions `bit` and `bytes` are aliases for this method with `block_size` set to 1 or 8
        >>> [i for i in Binary("101").iter(2)]
        ['01', '10']
        
        ## Similar methods
        * `bit` - iterates over bits `iter(1)`
        * `bytes` - iterates over bytes `iter(8)`
        * `__iter__` - iterates over bits `iter(1)`

        If you need more control use `itertools` module
        """
        ...

    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __bool__(self) -> bool: ...

    def __add__(self, other: Any) -> Binary:
        """
        Adds two binary numbers with wrapping arithmetic. 
        Equivalent to `arithm.wrapping_add()` function
        >>> Binary("0001") + Binary("0001")
        >>> '0010'
        """
        ...
    def __sub__(self, other: Any) -> Binary:
        """
        Subtracts two binary numbers with wrapping arithmetic
        Equvalent to `arithm.wrapping_sub()` function
        >>> Binary("0001") - Binary("0001")
        '0000'
        """
        ...
    def __or__(self, other: Any) -> Binary:
        """
        Performs bitwise or operation
        >>> Binary("0001") | Binary("0001")
        '0001'
        """
        ...
    def __and__(self, other: Any) -> Binary:
        """
        Performs bitwise and operation
        >>> Binary("0001") & Binary("0001")
        '0001'
        """
        ...
    def __xor__(self, other: Any) -> Binary:
        """
        Performs bitwise xor operation
        >>> Binary("0001") ^ Binary("0001")
        '0000'
        """
        ...
    def __invert__(self) -> Binary:
        """
        Performs bitwise not operation
        >>> ~Binary("0001")
        '1110'
        """
        ...
    def __neg__(self) -> Binary:
        """
        Performs negation operation
        >>> -Binary("0001")
        '1111'
        """
        ...

    def __eq__(self, __o: object) -> bool: ...
    def __ne__(self, __o: object) -> bool: ...
    def __lt__(self, __o: object) -> bool: ...
    def __le__(self, __o: object) -> bool: ...
    def __gt__(self, __o: object) -> bool: ...
    def __ge__(self, __o: object) -> bool: ...


    @overload
    def __getitem__(self, key: int) -> bool: 
        """
        ## __getitem__ for int
        returns bit at given index. Index starts from 0 and goes from right to left. If index is negative, it will be counted from the end (-1 is the last bit)
        bits outside of the number will be returned as sign_extend value
        >>> num = Binary("0xFA") # 11111010
        >>> num[0], num[1], num[2]
        >>> (False, True, False)
        >>> num[-1]
        >>> True
        """
        ...
    @overload
    def __getitem__(self, key: slice|Iterable) -> Binary:
        """
        ## __getitem__ for slice
        returns `Binary` object with selected bits. If slice index is negative, it will be counted from the end (-1 is the last bit)
        bits outside of the number will be returned as sign_extend value
        
        >>> num = Binary("0xFA") # 11111010
        >>> num[:3] # First 3 bits
        >>> "010"
        >>> num[-6:] # Last 6 bits
        >>> "111110"
        >>> num[:16] # First two bytes (paded with zero)
        >>> "00000000 11111010"
        >>> num[:]  # All bits (it is automaticly casted to unsigned)
        """
        ...
    
    def __setitem__(self, key: int|slice|Iterable, value: bool|Binary|str|int) -> None:
        """
        ## __setitem__
        sets given bits at given `index`, `slice` or `iterable`.
        >>> num = Binary("0xFA") # 11111010
        >>> num[0] = True # Set first bit to high
        >>> num[-1] = False # Set last bit to low
        >>> num
        >>> "01111011"
        >>> num[0:2] = "01" # Set first 2 bits to 01
        >>> num
        >>> "01111010"
        >>> num[0:8] = "11" # Set first 8 bit to 11 (rest are padded to zero) 
        >>> num
        >>> "00000010"
        """
        ...

class BinaryIterator:
    def __iter__(self) -> BinaryIterator: ...
    def __next__(self) -> Binary: ...