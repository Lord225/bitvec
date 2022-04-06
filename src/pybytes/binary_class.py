from typing import Iterable, Literal, Union
import numpy as np
import xxhash
from pybytes.common import utility
import pybytes.common as common
import re
from textwrap import wrap
import types

class Binary:
    def __init__(self, object: object = None, bit_lenght: int=None, bytes_lenght:int = None, sign_behavior: Union[Literal["unsigned", "magnitude", "signed"], str] = None, signed: bool = None,  default_formatting:str = ""):
        """## Binary
        Class that represent numbers in binary. Wraps arithmetic to bouds of the binary number, 
        allows for quick and easy bit manipulation.
        ### Parameters
        * object - Any object that can be somehow converted to binary number. 
        Including its representation as string, int, boolean, list of boolean-convertable values, byte-arrays, numpy arrays ect.
        * bit_lenght - Target lenght of the number in bits. This number can be inferred from object based on its value, extra zeros ect
        * bytes_lenght - Target lenght of the number in bytes. Same as bit_lenght but in bytes.
        * sign_behavior - How number should implement sign.
        * signed - if passed, will set sign_behavior to 'signed'
        * default_formatting - formatting that will be applied if no other formating was passed

        ## Examples

        >>> Binary("0110") # From string representing binary number. Following zeros are used to inherit len of number.
        '0110'
        >>> Binary(4, bit_lenght=8) # From int and with overrided lenght
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
        Module defines classes with predefined sizes and behaviors like u8, u16, i16, i64 ect. These ones can be used as followed:
        >>> u8(3)
        '00000011'
    
        ### Conversion
        Some conversions are avalible:
        >>> num = Binary("FA") # 11111010

        To string
        >>> str(num)
        '11111010'
        
        To int conversions to floats have almost no cost (reinterpreting array of bytes)
        >>> int(num)
        250

        To float
        >>> float(num)
        250.0

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
        >>> num[:3] # First 3 bits
        '010'
        >>> num[-6:] # Last 6 bits
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
        ### Modifying
        * append_high
        * append_low
        * strip
        * strip_right

        
        ### Modify by Index
        You can modify bits with indexes:
        >>> num = Binary(0, bit_lenght=8)
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
        >>> num = Binary(0, bit_lenght=8)
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
        * If right side is bool-like (so, bool or integer equal to 0 or 1), 
        the assigment will set all selectet bits to this value.
        * If right side is object convertable to Binary, 
        assigment will set selected slice only if lenght of the slice and lenght of the value
        are equal. Assigment
        `num[:3] = "11"`
        will fail.
        * step value is not supported.

        ### Modyfy by List
        You can select which bits should be changed with array.
        >>> num = Binary(0, bit_lenght=8)
        >>> num[[1,2,5]] = True # Set second, 3th and 5th bit to True
        >>> num
        '00100110'

        ### Arithmetic  

        ## See also

        """
        
        if signed is not None:
            self.__init__(object, 
                          bit_lenght=bit_lenght, 
                          bytes_lenght=bytes_lenght, 
                          sign_behavior = 'signed' if signed else 'unsigned',
                          signed=None,
                          default_formatting=default_formatting)
            return

        self._default_formatting = str(default_formatting)

        to_build = types.SimpleNamespace()
        to_build._len = None
        to_build._data = None
        to_build._mask = None
        to_build._sign_behavior = sign_behavior

        if bytes_lenght is not None and bit_lenght is not None and bytes_lenght!=bit_lenght*8:
            raise ValueError(f"Passed conflicting sizes ({bytes_lenght} bytes and {bit_lenght} bits)")
        if bytes_lenght is None and bit_lenght is not None:
            to_build._len = bit_lenght
        if bytes_lenght is not None and bit_lenght is None:
            to_build._len = 8*bytes_lenght
        

        if object is None:
            object = 0

        from_str = False
        if isinstance(object, str):
            from_str = True
            object, new_len = self.__generate_from_string(object)
            to_build._len = new_len if to_build._len is None and new_len is not None else to_build._len
        
        self.__build_class(**to_build.__dict__)

        if isinstance(object, int):
            self.__from_integer(to_build, object, do_not_add_sign_bit=from_str)
        elif isinstance(object, np.ndarray):
            self.__from_ndarray(to_build, object)
        elif isinstance(object, Iterable):
            self.__from_iterable(to_build, object)
        elif isinstance(object, Binary):
            self.__copy(to_build, object)
        elif isinstance(object, bool):
            self.__from_integer(to_build, object!=0, do_not_add_sign_bit=False)
        elif isinstance(object, float):
            self.__from_float(to_build, object)

        self.__default_out(to_build)
        self.__build_class(**to_build.__dict__)
        self.__fix_zero_lenght()
        self.__strip_array_to_lenght()
        self.__generate_bitmask_for_self()
        self.__apply_mask()
        self.__selfcheck()
        
    def __generate_from_string(self, my_str: str):
        if my_str == "":
            return 0, 1
        my_str = ''.join(my_str.strip().split())
        len_override = None
        
        try:
            striped = my_str.removeprefix("0b")
            number = int(striped, 2)
            len_override = len(striped)
        except:
            try:
                striped = my_str.removeprefix("0x")
                number = int(striped, 16)
                len_override = 4*len(striped)
            except:
                try:
                    number = int(my_str, 0)
                    len_override = number.bit_length()
                except:
                    raise ValueError(f"Value: '{my_str}' is invalid")
        return number, len_override
    def __from_integer(self, to_build, obj: int, do_not_add_sign_bit):
        def get_bit_len_of_number(to_build, obj: int):
            if to_build._sign_behavior == "unsigned" or do_not_add_sign_bit:
                return obj.bit_length()
            else:
                return obj.bit_length()+1
        if to_build._sign_behavior is None:
            to_build._sign_behavior = 'unsigned' if obj >= 0 else 'signed'
        if to_build._len is None:
            to_build._len = get_bit_len_of_number(to_build, obj)
        
        self.__build_class(_len = to_build._len, _sign_behavior = to_build._sign_behavior)

        if to_build._len == 0:
            to_build._data = np.zeros((max(to_build._len, 1),), dtype=np.uint8)
        
        minimum = self.minimum_value()
        maximum = self.maximum_value()
        if obj > maximum or obj < minimum:
            if do_not_add_sign_bit == False or obj > 2**len(self):
                raise ValueError(f"Number {obj} cannot fit in lenght: {len(self)}")
        buffer = abs(obj).to_bytes(utility.bytes_for_len(self._len), "little")
        to_build._data = np.frombuffer(buffer, dtype=np.uint8)

        if obj < 0:
            to_build._mask = self.__generate_bitmask(to_build._len)
            to_build._data = common.alu.alu_base.arithmeitc_neg_number(to_build._data, to_build._len, to_build._mask, to_build._sign_behavior)
    def __from_ndarray(self, to_build, array: np.ndarray):
        object = array.astype('uint8')
        to_build._data = object
        to_build._len = len(to_build._data)*8 if to_build._len is None else to_build._len
    def __from_iterable(self, to_build, iterable):
        bits = self.__generate_from_iterable(iterable)
        to_build._len = len(bits) if to_build._len is None else to_build._len 
        to_build._data = np.array(np.packbits(list(reversed(bits)), bitorder='little'))
    def __generate_from_iterable(self, Iter: Iterable):
        return [bool(i) for i in Iter]
    def __copy(self, to_build, other):
        to_build._data = np.copy(other._data)
        to_build._len = other._len if to_build._len is None else to_build._len
        to_build._mask = self.__generate_bitmask(to_build._len)
        if to_build._sign_behavior != None and other._sign_behavior != to_build._sign_behavior:
            to_build._data = common.alu.alu_base.sign_convert[other._sign_behavior](
                to_build._data, 
                to_build._len, 
                to_build._mask, 
                to_build._sign_behavior,
                False)
        else:
            to_build._sign_behavior = other._sign_behavior
    def __from_float(self, to_build, i: float):
        if round(i) != i:
            raise ValueError("Cannot convert from none-integer value, try using float module.")
        else:
            self.__from_integer(to_build, int(i), False)
    def __default_out(self, to_build):
        if to_build._data is None:
            to_build._data = np.zeros((1,), dtype=np.uint8)
        if to_build._len is None or to_build._len == 0:
            to_build._len = 1
        if to_build._mask is None:
            to_build._mask = self.__generate_bitmask(to_build._len)
        if to_build._sign_behavior is None:
            to_build._sign_behavior = 'unsigned'
    def __generate_bitmask(self, _len):
        assert isinstance(_len, int)
        return np.array(np.packbits([1]*_len, bitorder='little'))
    def __generate_bitmask_for_self(self):
        self._mask = self.__generate_bitmask(len(self))
    def __fix_zero_lenght(self):
        if self._len == 0:
            self._len = 1
    def __strip_array_to_lenght(self):
        assert isinstance(self._len, int)
        target_bytes = utility.bytes_for_len(self._len)
        lenght = len(self._data)
        if target_bytes < lenght:
            self._data = self._data[:target_bytes]
        elif target_bytes > lenght:
            self._data = np.array(np.append(self._data, [np.uint8(0)]*(target_bytes-lenght)))
    def __build_class(self, **kwargs):
        if "_len" in kwargs and kwargs["_len"] is not None:
            self._len: int = kwargs["_len"]
        if "_data" in kwargs and kwargs["_len"] is not None:
            self._data: np.ndarray = kwargs["_data"]
        if "_mask" in kwargs and kwargs["_len"] is not None:
            self._mask: np.ndarray = kwargs["_mask"]
        if "_sign_behavior" in kwargs and kwargs["_len"] is not None:
            self._sign_behavior: Literal["unsigned", "magnitude", "signed"] = kwargs["_sign_behavior"]
        if "_default_formatting" in kwargs and kwargs["_len"] is not None:
            self._default_formatting: str = kwargs["_default_formatting"]
     
    def __selfcheck(self):
        assert hasattr(self, "_data") and isinstance(self._data, np.ndarray), "Missing component: _data"
        assert hasattr(self, "_len") and isinstance(self._len, int), "Missing component: _len"
        assert hasattr(self, "_mask") and isinstance(self._mask, np.ndarray), "Missing component: _mask"
        assert len(self._data) == common.utility.bytes_for_len(self._len), "Internal components of Binary object are invalid."
        assert self._len != 0, "Zero len Binary number is invalid"
        assert self._mask[-1] >= self._data[-1], "Data is invalid"
        assert self._data.dtype == np.uint8, "dtype of data is invalid"

    def __apply_mask(self,):
        self._data = utility.apply_mask(self._data, self._mask)
    
    ###########################
    #     Public Functions    #
    ###########################

    def low_byte(self):
        """First byte of the number. Fills with zeros if needed.
        
        >>> Binary("0000 1111 1000 1111").low_byte()
        '10001111'

        >>> Binary("11 0001").low_byte()
        '00110001'
        """
        return Binary(self[:8], bit_lenght=8)
    def high_byte(self):
        """Second byte of the number. Fills with zeros if needed.
        
        >>> Binary("0000 1111 1000 1111").high_byte()
        '00001111'

        >>> Binary("10 1111 0000 0000").high_byte()
        '00101111'
        """
        return Binary(self[8:16], bit_lenght=8)
    def extended_low(self):
        """First 16 bits of the number. Fills with zeros if needed."""
        return Binary(self[:16], bit_lenght=16)
    def extended_high(self):
        """Second 16 bits of the number. Fills with zeros if needed."""
        return Binary(self[16:32], bit_lenght=16)
    def get_byte(self, which):
        """Returns nth byte of the number. Works with negative indexes.

        >>> Binary("0000 1111 1000 1111").get_byte(0)
        '10001111'

        >>> Binary("0000 1111 1000 1111").get_byte(-1)
        '00001111'

        """
        if isinstance(which, int):
            return Binary(int(self._data[which]), bit_lenght=8)
        return None
    def sign_behavior(self) -> Literal["unsigned", "magnitude", "signed"]:
        """Returns sign behavior of the number. Possible values are:
        * unsigned
        * signed
        * magnitude
        Default sign behavior is `unsigned`. If sign is needed `signed` is used insted.
        """
        if self._sign_behavior is None:
            return "unsigned"
        else:
            if self._sign_behavior == "unsigned":
                return "unsigned"
            elif self._sign_behavior == "signed":
                return "signed"
            elif self._sign_behavior == "magnitude":
                return "magnitude"
            else:
                raise RuntimeError(f"This object is poisoned. {self._sign_behavior} is not valid state")
    def maximum_value(self):
        """Maximal value of this number
        >>> Binary('0000').maximum_value()
        15

        >>> Binary('0000', sign_behavior='signed').maximum_value()
        7
        """
        if self._sign_behavior == "unsigned" or self._sign_behavior is None:
            return int(2**len(self)-1)
        else:
            return int(2**(len(self)-1)-1)
    def minimum_value(self):
        """Minimal value of this number
        >>> Binary('0000').minimum_value()
        0

        >>> Binary('0000', sign_behavior='signed').minimum_value()
        -8
        """
        if self._sign_behavior == "unsigned" or self._sign_behavior is None:
            return 0
        else:
            return int(-2**(len(self)-1))
    
    def append_high(self, bit: bool):
        new_binary = Binary(self._data, bit_lenght=len(self)+1, sign_behavior=self.sign_behavior())
        new_binary[-1] = bit
        return new_binary
    def append_low(self, bit: bool):
        new_binary = Binary(self._data, bit_lenght=len(self)+1, sign_behavior=self.sign_behavior())
        new_binary = common.alu.wrapping_lsh(new_binary, 1)
        new_binary[0] = bit
        return new_binary

    def strip(self):
        """Removes leading zeros
        
        >>> Binary("0000 1000").strip()
        "1000"
        """
        return Binary(int(self), sign_behavior=self.sign_behavior())
    def strip_right(self):
        """Removes trailing zeros
        
        >>> Binary("1001 1000").strip_right()
        "1011"
        """
        zeros = self.trailing_zeros()
        return self[zeros:]

    def trailing_zeros(self) -> int:
        """Returns amount of trailing zeros
        
        >>> Binary("0001 0000").trailing_zeros()
        4
        >>> Binary("0000 0001").trailing_zeros()
        0
        >>> Binary("0000 0000").trailing_zeros()
        8
        """
        return utility.trailing_zeros(self._data, len(self))
    def leading_zeros(self) -> int:
        """Returns amount of leading zeros
        
        >>> Binary("0001 0000").leading_zeros()
        3
        >>> Binary("0000 0001").leading_zeros()
        7
        >>> Binary("0000 0000").leading_zeros()
        8
        """
        return utility.leading_zeros(self._data, len(self))
    def trailing_ones(self) -> int:
        """ NOT IMPLEMENTED
        Returns amount of trailing ones 
        
        >>> Binary("1110 1111").trailing_ones()
        4
        >>> Binary("1111 1110").trailing_ones()
        0
        >>> Binary("1111 1111").trailing_ones()
        8
        """
        return utility.trailing_ones(self._data, len(self))
    def leading_ones(self) -> int:
        """
        Returns amount of leading ones 
        
        >>> Binary("1110 1111").leading_ones()
        3
        >>> Binary("1111 1110").leading_ones()
        7
        >>> Binary("1111 1111").leading_ones()
        8
        """
        raise NotImplementedError()
        return utility.leading_ones(self._data, len(self))

    #####################
    #     Comparing     #
    #####################

    def __lt__(self, other):
        return common.cmp.less(self, other)
    def __eq__(self, other):
        return common.cmp.equal(self, other)
    def __gt__(self, other):
        return common.cmp.greater(self, other)   
    def __le__(self, other):
        return not self.__gt__(other)
    def __ge__(self, other):
        return not self.__lt__(other)
    def __ne__(self, other):
        return not self.__eq__(other)
    
    #####################
    #    Conversions    #
    #####################

    def __bool__(self):
        return False if np.all(self._data==0) else True
    def __hash__(self):
        h = xxhash.xxh64()
        h.update(bytearray(self._data))
        return h.intdigest()
    def __int__(self):
        data_cpy = self._data.copy()
        if self._sign_behavior == "unsigned":
            sign_bit = False
        else:
            sign_bit = self.is_negative()
            
            if sign_bit:
                data_cpy = common.alu.alu_base.arithmeitc_neg_number(data_cpy, len(self), self._mask, self.sign_behavior())
        value = int.from_bytes(data_cpy.data, 'little')
        if sign_bit:
            return -value
        else:
            return value
          
    def __float__(self):
        return float(utility.to_float(self._data))
    def __index__(self):
        return int(self)

    #####################
    #      Utility      #
    #####################

    def __len__(self) -> int:
        return self._len
    def is_negative(self) -> bool:
        """Returns True if number is less than zero. Unsigned numbers always returns True."""
        if self._sign_behavior == "unsigned":
            return False
        else:
            return self[-1] != 0
    def to_string(self) -> str:
        """Converts binary number to string of ones and zeros"""
        return utility.format_binary(self._data, '')[-len(self):]
    def as_hex(self) -> str:
        """Converts binary number to hexadecimal represenation"""
        return utility.format_hex(self._data, '')[-len(self)//4:]
    def __in_bounds(self, value) -> bool:
        if value<0:
            return False
        if value>=self._len:
            return False
        return True

    #####################
    #       Access      #
    #####################    

    def __getitem__(self, key):
        if isinstance(key, slice):
            stop = key.stop
            
            stop = stop if stop is not None else self._len
            stop =  len(self) + stop if stop < 0 else stop
            
            as_str = self.to_string()[::-1]
            as_str += "0"*(stop-len(as_str))
            return Binary(as_str[key][::-1])
        elif isinstance(key, int):
            key = len(self) + key if key < 0 else key
            if key >= len(self) or key < 0:
                raise IndexError("Key out of bounds")
            byte_index = key//8
            return utility.get_bit(self._data[byte_index], key%8)
        else:
            raise ValueError("Invalid value for indexing: {key}")
    def __setitem__(self, key, value):
        if isinstance(key, slice):
            if key.step is not None:
                raise NotImplementedError("Step is not supported in slice assigment")
            start = key.start
            stop = key.stop
            
            stop = stop if stop is not None else self._len
            start = start if start is not None else 0

            start = len(self) + start if start < 0 else start
            stop =  len(self) + stop if stop < 0 else stop

            if start > len(self):
                raise IndexError(f"Starting Index out of the bounds, got {start} expected less than {len(self)}")
            if stop > len(self):
                raise IndexError(f"Stoping Index out of the bounds got {stop} expected less than {len(self)}")
            if start>stop:
                raise IndexError(f"Value of Starting Index is larger than stopping")
            
            _len = stop-start

            if _len == 0:
                return 

            if isinstance(value, bool) or isinstance(value, int) and value in [1, 0]:
                value = "1" if bool(value) else "0"
                value = Binary(value*_len)
            else:
                try:
                    value = Binary(value)
                except:
                    raise ValueError(f"Value '{value}' is not convertable to Binary")
            if len(value) != _len:
                raise ValueError(f"Lenght of the left side of assigment have to match lenght of the slice, got: '{_len}' expected '{len(value)}'")
            try:
                utility.set_bits(self._data, value._data, start, _len, self._len)
            except:
                raise IndexError("Unkown Indexing error")   
        elif isinstance(key, int):
            try:
                value = bool(value)
            except:
                raise ValueError(f"Value {value} is not convertable to bool")

            key = len(self) + key if key < 0 else key
            if not self.__in_bounds(key):
                raise IndexError("Value out of bounds")
            utility.set_bit(self._data, key, self._len, value)
        elif isinstance(key, Iterable):
            keys = [int(k) for k in key]
            keys = [len(self) + key if key < 0 else key for key in keys]
            if any((not self.__in_bounds(key) for key in keys)):
                raise IndexError("Value out of bounds")
            for key in keys:
                utility.set_bit(self._data, key, self._len, value)
        else:
            raise ValueError("Invalid value for indexing: {key}")

    #####################
    #        Math       #
    #####################

    def __add__(self, other):
        return common.alu.wrapping_add(self, other)

    def __sub__(self, other):
        return common.alu.wrapping_sub(self, other)
    
    def __mul__(self, other):
        return common.alu.wrapping_mul(self, other)
    

    #####################
    #      bitwise      #
    #####################

    def __and__(self, other):
        return common.alu.bitwise_and(self, other)
    
    def __or__(self, other):
        return common.alu.bitwise_or(self, other)

    def __xor__(self, other):
        return common.alu.bitwise_xor(self, other)
    
    #####################
    #       Unary       #
    #####################

    def __pos__(self):
        return self
    def __neg__(self):
        return common.alu.arithmetic_neg(self)
    def __invert__(self):
        return common.alu.bitwise_not(self)
    def __abs__(self):
        if self.is_negative():
            return -self
        else:
            return self

    RE_SPLIT_PATTERN = re.compile('(\\d+|[\\D]+)') 
    def __find_pattern(self, pattern):
        if hasattr(self, '_computed_pattern'):
            return getattr(self, '_computed_pattern')
        PATTERN = []
        res = re.findall(self.RE_SPLIT_PATTERN, pattern)
        it = iter(res)
        try:
            while True:
                arg1 = int(next(it))
                arg2 = next(it)
                PATTERN.append((arg1, arg2))
        except StopIteration:
            pass
        setattr(self, '_computed_pattern', PATTERN)
        return PATTERN
    def __to_string_with_radix(self, radix) -> str:
        if radix == 'b':
            return utility.format_binary(self._data, '')[-len(self):]
        elif radix == 'x': 
            return utility.format_hex(self._data, '')[-len(self)//4:]
        return ''
    def __add_padding(self, as_str, padding, radix):
        #TODO REFACTOR
        if isinstance(padding, list):
            if len(padding) == 0:
                return as_str
            as_str = as_str[::-1]
            to_join = []
            index = 0
            pad_index = 0
            while True:
                to_join.append((as_str[index:index+padding[pad_index][0]], padding[pad_index][1]))
                index += padding[pad_index][0]
                pad_index = (pad_index+1)%(len(padding)+1)
                if index >= len(as_str):
                    break
            out = ''
            for val, join in reversed(to_join):
                out += f"{join}{val[::-1]}"
            return out.strip(''.join(i[1] for i in padding))
        else:
            if padding[0] == 0:
                return as_str
            width = padding[0]//{'b':1,'x':4}[radix]
            wraped = [chunk[::-1] for chunk in wrap(as_str[::-1], width)[::-1]]
            return padding[1].join(wraped)
    def __format(self, spec: str):
        #TODO REFACTOR
        # {:pad:pattern} {:pad:n}
        # {:%h} {:%b}
        # {:r.}    
        spec_list = spec.split(':')
        it = iter(spec_list)
        reverse = None
        padding_filter = None
        radix = None

        try:
            while True:
                mod = next(it)
                if len(mod) == 2 and mod.startswith('r'):
                    reverse = mod[1]
                elif mod == 'pad':
                    arg = next(it)
                    if (len(arg) == 1 or len(arg)==2) and arg[0] in ['s','n', 'b', 'w', 'd', 'q']:
                        pad_chars = arg[1:] if arg[1:] != '' else ' ' 
                        padding_filter = ({'s':0, 'n':4, 'b':8, 'w':16, 'd':32, 'q':64}[arg[0]], pad_chars)
                    else:
                        padding_filter = self.__find_pattern(arg)
                elif len(mod)==2 and mod.startswith('%') and mod[1] in ['x', 'b']:
                    radix = mod[1]
        except StopIteration:
            pass
        
        if padding_filter is None:
            if self._len%8 == 0:
                padding_filter = (8, ' ')
            elif self._len > 16:
                padding_filter = (8, ' ')
            else:
                padding_filter = (0, '')
        if radix is None:
            radix = 'b'
        
        as_str = self.__to_string_with_radix(radix)
        as_str = self.__add_padding(as_str, padding_filter, radix)
        if reverse is not None:
            as_str = f"{reverse}{as_str[::-1]}"
        return as_str

    def __format__(self, spec):
        if spec is None:
            return self.to_string()
        if spec == '' and self._default_formatting is not None:
            formatted = self.__format(self._default_formatting)
        else:
            formatted = self.__format(spec)
        return formatted
    def __repr__(self) -> str:
        return format(self)
    def __str__(self):
        return format(self)

