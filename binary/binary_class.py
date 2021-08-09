from typing import Iterable, List, Literal, Union, Tuple, NewType
import numpy as np
import xxhash
from binary.common import utility
import binary.common as common

class Binary:
    def __init__(self, object: object = None, bit_lenght=None, bytes_lenght = None, sign_behavior: Literal["unsigned", "magnitude", "signed"] = None):
        """## Binary
        Class that represent numbers in binary. Wraps arithmetic to bouds of the binary number, 
        allows for quick and easy bit manipulation.
        ### Parameters
        * object - Any object that can be somehow converted to binary number. 
        Including its representation as string, int, boolean, list of boolean-convertable values, byte-arrays, numpy arrays ect.
        * bit_lenght - Target lenght of the number in bits. This number can be inferred from object based on its value, extra zeros ect
        * bytes_lenght - Target lenght of the number in bytes. Same as bit_lenght but in bytes.
        * sign_behavior - How number should implement sign.

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
        >>> Binary("ff Aa C   C") # Works with diffrent radix too
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
        
        To int
        >>> int(num)
        250

        To float (much faster than to `int`, but rounding errors show up)
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
        
        ### Usefull alias methods
        There is few methods that will simplyfy slicing like
        * high_byte
        * low_byte
        * extended_low
        * extended_high
        * get_byte
        *cc 
        
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

        self._sign_behavior = sign_behavior

        if bytes_lenght is not None and bit_lenght is not None and bytes_lenght!=bit_lenght*8:
            raise ValueError(f"Passed conflicting sizes")
        if bytes_lenght is None and bit_lenght is not None:
            self._len = bit_lenght
        if bytes_lenght is not None and bit_lenght is None:
            self._len = 8*bytes_lenght
        if bytes_lenght is None and bit_lenght is None:
            self._len = None

        if object is None:
            if self._len is None:
                self._len = 1
            self = np.zeros((len(self)),dtype=np.uint8)

        if isinstance(object, str):
            object, new_len = self.__generate_from_string(object)
            self._len = new_len if self._len is None and new_len is not None else self._len

        if isinstance(object, int):
            self.__from_integer(object)
        elif isinstance(object, np.ndarray):
            self.__from_ndarray(object)
        elif isinstance(object, Iterable):
           self.__from_iterable(object)
        elif isinstance(object, Binary):
            self.__copy(object)
        
        self._sign_behavior = self._sign_behavior if self._sign_behavior is not None else "unsigned"
        
        self.__fix_zero_lenght()
        self.__strip_array_to_lenght()
        self.__generate_bitmask()
        self.__apply_mask()
        self.__check_internal_integridy()

    #######################
    #     Constructors    #
    #######################
    def __copy(self, to_copy):
        self._len = to_copy._len if self._len is None else self._len
        self._data = to_copy._data.copy()
        self.__generate_bitmask()
        if self._sign_behavior != None and to_copy._sign_behavior != self._sign_behavior:
            self._data = common.alu.alu_base.sign_convert[to_copy._sign_behavior](self._data, self._len, self._mask, self._sign_behavior, False)

    def __from_iterable(self, iterable):
        bits = self.__generate_from_iterable(iterable)
        self._len = len(bits) if self._len is None else self._len 
        self._data = np.packbits(list(reversed(bits)), bitorder='little')
    def __from_ndarray(self, array):
        object = array.astype('uint8')
        self._data = object
        self._len = len(self._data)*8 if self._len is None else self._len
    def __from_integer(self, obj):
        if obj == 0:
            self._len = 1 if self._len is None else self._len
            self._data = np.zeros((1,), dtype=np.uint8)
        elif obj > 0:
            self.__from_number(obj)
        else:
            self.__from_negative_integer(obj)
    def __from_negative_integer(self, i: int):
        if self._sign_behavior == None:
            self._sign_behavior = 'signed'
        elif self._sign_behavior == "unsigned":
            raise ValueError()
        i = abs(i)

        self._len = i.bit_length()+1 if self._len is None else self._len
        buffer = i.to_bytes(utility.bytes_for_len(self._len), "little")
        self._data = np.frombuffer(buffer, dtype=np.uint8)
        
        self.__generate_bitmask() # early bitmask generation.
        negate = common.alu.arithmetic_neg(self)
        self.__copy(negate)
    def __from_number(self, i: int):
        assert i > 0
        self._len = i.bit_length() if self._len is None else self._len
        buffer = i.to_bytes(utility.bytes_for_len(self._len), "little")
        self._data = np.frombuffer(buffer, dtype=np.uint8)

    def __generate_from_iterable(self, Iter: Iterable):
        return [bool(i) for i in Iter]
    def __generate_from_string(self, my_str: str):
        if not my_str:
            return 0
        my_str = ''.join(my_str.strip().split())
        len_override = None
        
        try:
            number = int(my_str, 2)
            len_override = len(my_str.removeprefix("0b"))
        except:
            try:
                number = int(my_str.removeprefix("0x"), 16)
                len_override = 4*len(my_str)
            except:
                try:
                    number = int(my_str, 0)
                except:
                    raise ValueError(f"Value: '{my_str}' is invalid")
        return number, len_override
    def __generate_bitmask(self):
        self._mask = np.packbits([1]*self._len, bitorder='little')

    def __fix_zero_lenght(self):
        if self._len == 0:
            self._len = 1
    def __strip_array_to_lenght(self,):
        target_bytes = utility.bytes_for_len(self._len)
        lenght = len(self._data)
        if target_bytes < lenght:
            self._data = self._data[:target_bytes]
        elif target_bytes > lenght:
            self._data = np.append(self._data, [np.uint8(0)]*(target_bytes-lenght))
    def __check_internal_integridy(self):
        REQUIRED_ATTRIBUTES = [("_data", np.ndarray), ("_len", int), ("_mask", np.ndarray), ("_sign_behavior", str)]

        assert all((hasattr(self, ATTR) and isinstance(getattr(self, ATTR), TYPE) for ATTR, TYPE in REQUIRED_ATTRIBUTES)), "Missing internal components of Binary object."
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
    def sign_behavior(self):
        """Returns sign behavior of the number. Possible values are:
        * unsigned
        * signed
        * magnitute
        Default sign behavior is `unsigned`. If sign is needed `signed` is used insted.
        """
        return self._sign_behavior
    def maximum_value(self):
        """Maximal value of this number
        >>> Binary('0000').maximum_value()
        15

        >>> Binary('0000', sign_behavior='signed').maximum_value()
        7
        """
        if self._sign_behavior == "unsigned":
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
        if self._sign_behavior == "unsigned":
            return 0
        else:
            return int(-2**(len(self)-1))
    
    #####################
    #     Comparing     #
    #####################

    def __lt__(self, other):
        return common.cmp.less(self, other)
    
    def __le__(self, other):
        return not self.__gt__(other)

    def __gt__(self, other):
        return common.cmp.greater(self, other)
    
    def __ge__(self, other):
        return not self.__lt__(other)
    
    def __eq__(self, other):
        return common.cmp.equal(self, other)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    #####################
    #    Conversions    #
    #####################

    def __bool__(self):
        return True if (self._data==0).all() else False
    def __hash__(self):
        h = xxhash.xxh64()
        h.update(self._data)
        return h.intdigest()
    def __int__(self):
        return int(utility.to_integer(self._data))
    def __float__(self):
        return float(utility.to_float(self._data))    

    #####################
    #      Utility      #
    #####################

    def __len__(self):
        return self._len
    def is_negative(self):
        if self._sign_behavior == "unsigned":
            return False
        else:
            return self[-1] != 0
    def __in_bounds(self, value):
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
            as_str = format(self, 's')[::-1]
            as_str += "0"*(key.stop-len(as_str))
            return Binary(as_str[key][::-1])
        elif isinstance(key, int):
            key = len(self) + key if key < 0 else key
            if key >= len(self) or key < 0:
                raise IndexError("Value out of bounds")
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

    def __format__(self, spec):
        if not spec:
            if self._len%8 == 0:
                spec = "b"
            elif self._len > 16:
                spec = "w"
            else:
                spec = "s"
            
        if spec == "b":
            return utility.format_binary(self._data, ' ')[-self._len-len(self._data):]
        if spec == "s":
            return utility.format_binary(self._data, '')[-self._len:]

        jump = {"w":2, "d":4, "q":8}[spec]
        chunks = list(reversed(np.array_split(self._data, len(self._data)//jump)))
        
        return " ".join([(''.join((np.binary_repr(i, 8)) for i in reversed(chunk))) for chunk in chunks])
    def __repr__(self) -> str:
        return format(self)

class u8(Binary):
    def __init__(self, object: object = None):
        super(u8, self).__init__(object, bit_lenght=8, sign_behavior='unsigned')
class u16(Binary):
    def __init__(self, object: object = None):
        super(u8, self).__init__(object, bit_lenght=16, sign_behavior='unsigned')