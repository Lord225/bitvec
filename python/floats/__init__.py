from pybytes import Binary
import pybytes
import math
from enum import Enum

# REWRITE THIS MESS

# class rounding_mode(Enum):
#     CLOSEST = 0,
#     LESS = 1,
#     MORE = 2,

# def isInteger(_input: str):
#     return "." not in _input
# def isFloatString(_input: str):
#     return "." in _input
# def fp(_input: str) -> float:
#     if isInteger(_input):
#         return float(int(_input, 2))
#     else:
#         Int, Real = _input.split(".")
#         IntNum = int(Int, 2) if len(Real) != 0 else 0
#         RealNum = int(Real, 2) if len(Real) != 0 else 0

#         return IntNum+RealNum/(2**len(Real))
# def float_to_binary(frac: float, output_size_limit = 20, rounding: rounding_mode = rounding_mode.CLOSEST):
#     if frac > 1 or frac < 0:
#         raise ValueError(f'Parameter frac should be in range [0, 1)')
#     out_frac = Binary(bit_lenght=output_size_limit)

#     for i in range(output_size_limit):
#         frac = frac*2
#         out_frac[-i-1] = frac >= 1.0
#         frac, _ = math.modf(frac)
#         if abs(frac) < 0.0000000000000001:
#             break
#     return out_frac.strip_right()
# def int_to_binary(input):
#     return pybytes.Binary(input)
# def get_sign(num: float):
#     return abs(num), num < 0
# def minimal_bin_places_for_decimal_precision(target_decimal_precision):
#     return math.floor(target_decimal_precision*(math.log(2)+ math.log(5))/math.log(2))
# def normalalize_float(f: float):
#     counter = 0
#     if f < 0:
#         f = -f 
#     if f == 0:
#         return None, None
    
#     while f <= 1.0:
#         counter -= 1
#         f *= 2
#     while f >= 2.0:
#         counter += 1
#         f /= 2
#     return f, counter
# def normalize_float_but_allow_for_denormalized(f: float, max: int):
#     f = f*2**-max
#     return f, 0
# def to_float(object: object):
#     if isinstance(object, str):
#         as_float = fp(object)
#     elif isinstance(object, float):
#         as_float = object
#     else:
#         raise
#     return as_float
# def split_to_fixed(object: object, binary_places = 20, target_decimal_precision=None):
#     as_float = to_float(object)

#     if target_decimal_precision is not None:
#         binary_places = minimal_bin_places_for_decimal_precision(target_decimal_precision)
#     as_float, sign = get_sign(as_float)
    
#     frac, whole = math.modf(as_float)

#     out_whole = int_to_binary(int(whole))

#     out_frac = float_to_binary(frac, binary_places)
    
#     return Splitted(out_frac, out_whole, Binary(sign))

# def mantissa_to_float(num: Binary, denormalized)-> float:
#     out = 0.0 if denormalized else 1.0
    
#     for i, bit in enumerate(reversed(num)):
#         out += float(bit)*2**(-i-1)
#     return out 
    
# class BinaryFloatPoint:
#     def __init__(self, mantissa: object, exponant: object, sign: object):
#         self.mantissa = mantissa
#         self.exponant = exponant
#         self.sign = sign

# class BinaryFixedPoint:
#     def __init__(self, value: object, midpoint: int):
#         pass
# class Splitted:
#     def __init__(self, frac, whole, sign) -> None:
#         self.frac = Binary(frac)
#         self.whole = Binary(whole)
#         self.sign = bool(sign)
#     def __str__(self) -> str:
#         return f'SplitedFloat(whole={self.whole}, frac={self.frac}, sign={self.sign})'

# class FloatInstance:
#     def __init__(self, MANTISSA, EXPONANT, SIGN):
#         self.MANTISSA = MANTISSA
#         self.EXPONANT = EXPONANT
#         self.SIGN = SIGN

# class CustomFloat:
#     PRESETS = {'fp8':(4, 3), 'fp16':(5, 10), 'fp32':(8, 23), 'bf16':(8, 7), 'tf':(8, 10), 'fp24':(7, 16), 'pxr24':(8, 15)}
#     def __init__(self, mantissa_size: int = None, exponent_size: int = None, exponent_bias = None, preset=None):
#         if preset is not None:
#             if preset in self.PRESETS:
#                 exponent_size = self.PRESETS[preset][0]
#                 mantissa_size = self.PRESETS[preset][1]

#         assert mantissa_size != None
#         assert exponent_size != None

#         self.MANTISA_SIZE: int = mantissa_size
#         self.EXPONENTIAL_SIZE:int = exponent_size
#         self.EXPONENT_BIAS: int = -abs(exponent_bias) if exponent_bias is not None else -(2**(exponent_size-1)-1)

#         self.__selfcheck()
    
#     def __selfcheck(self):
#         assert self.MANTISA_SIZE is not None and self.MANTISA_SIZE > 0
#         assert self.EXPONENTIAL_SIZE is not None and self.EXPONENTIAL_SIZE > 0
#         assert self.EXPONENT_BIAS is not None and self.EXPONENT_BIAS < 0

#         if self.MANTISA_SIZE > 54:
#             print("WARNING: Mantissa with size over 54 could will not be properly emulated")
#     def __call__(self, *args, **kwds):
#         return self.get(*args, **kwds)
#     def get_parts(self, object: object):
#         self.__selfcheck()

#         as_float = to_float(object)
        
#         sign = as_float < 0
#         as_float = abs(as_float)

#         normalized, count = normalalize_float(as_float)
#         if normalized is None or count is None:
#             biased_count = 0
#             normalized = 0
#         elif count < -2**(self.EXPONENTIAL_SIZE-1):
#             normalized, biased_count = normalize_float_but_allow_for_denormalized(as_float, -(self.EXPONENT_BIAS+1))
#         else:
#             biased_count = count-self.EXPONENT_BIAS

#         manissa = Binary(bit_lenght=self.MANTISA_SIZE)
#         splitted = split_to_fixed(normalized, self.MANTISA_SIZE+2)
#         manissa[-len(splitted.frac):] = splitted.frac

#         return Binary(sign), manissa, Binary(biased_count, self.EXPONENTIAL_SIZE)
#     def __len__(self):
#         return self.EXPONENTIAL_SIZE+self.MANTISA_SIZE+1
#     def get_concat(self, object: object):
#         sign, manissa, exp = self.get_parts(object)
#         total_size = len(self)
        
#         output = Binary(bit_lenght=total_size, default_formatting=f'pad:{self.MANTISA_SIZE} {self.EXPONENTIAL_SIZE} 1 ')
#         output[-1] = sign
#         output[-self.EXPONENTIAL_SIZE-1:-1] = exp
#         output[:-self.EXPONENTIAL_SIZE-1] = manissa

#         return output
#     def get(self, *args, **kwds):
#         if 'rounding' in kwds:
#             rounding = kwds['rounding']
#         else:
#             rounding = 'Closest'
#         if len(args) == 1:
#             if isinstance(args[0], str):
#                 try:
#                     as_bin = Binary(args[0], bit_lenght=len(self))
#                     return self.get_float(as_bin)
#                 except:
#                     pass
#             if isinstance(args[0], (float, int)):
#                 return self.get_concat(float(args[0]))
#             if isinstance(args[0], Binary):
#                 if len(args[0]) == len(self):
#                     return self.get_float(args[0])
#                 else:
#                     raise ValueError(f"Expectet {len(self)} bit value")
#         if len(args) == 2 or len(args) == 3:
#             mantissa = Binary(args[0], bit_lenght=self.MANTISA_SIZE)
#             exponant = Binary(args[1], bit_lenght=self.EXPONENTIAL_SIZE)
#             sign = False if len(args) != 3 else bool(args[2])

#         if 'mantissa' in kwds and 'exponent' in kwds:
#             mantissa = Binary(kwds['mantissa'], bit_lenght=self.MANTISA_SIZE)
#             exponant = Binary(kwds['exponent'], bit_lenght=self.EXPONENTIAL_SIZE)
#             sign = False if 'sign' not in kwds else bool(kwds['sign'])

#             value =  self.get_float_from_parts(mantissa, exponant, sign)
#             return value
#         return None
#     def get_hex(self, object: object):
#         num = self.get_concat(object)
#         return "{0:#0{1}x}".format(int(num), math.ceil(len(self)/4)+2)
#     def get_mantissa(self, num: Binary):
#         return num[:-self.EXPONENTIAL_SIZE-1]
#     def get_exponent(self, num: Binary):
#         return num[-self.EXPONENTIAL_SIZE-1:-1]
#     def get_sign(self, num: Binary):
#         return num[-1]

#     def get_float_from_parts(self, mantissa, exponent, sign):
#         mantissa_as_float = mantissa_to_float(mantissa, exponent==0)
#         if exponent == 0:
#             exponent = 1.0
#         mantissa_as_float = mantissa_as_float*2**(float(exponent)+self.EXPONENT_BIAS)

#         mantissa_as_float = -mantissa_as_float if sign else mantissa_as_float
#         return mantissa_as_float
#     def get_float(self, input):
#         x = Binary(input, bit_lenght=len(self))

#         mantissa = self.get_mantissa(x)
#         exponent = self.get_exponent(x)
#         sign = self.get_sign(x)

#         mantissa_as_float = self.get_float_from_parts(mantissa, exponent, sign)

#         return mantissa_as_float