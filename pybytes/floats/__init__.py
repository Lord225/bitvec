from pybytes.binary_class import Binary
import pybytes
import math

def isInteger(_input: str):
    return "." not in _input

def fp(_input: str) -> float:
    if isInteger(_input):
        return float(int(_input, 2))
    else:
        Int, Real = _input.split(".")
        IntNum = int(Int, 2) if len(Real) != 0 else 0
        RealNum = int(Real, 2) if len(Real) != 0 else 0

        return IntNum+RealNum/(2**len(Real))
def float_to_binary(frac: float, output_size_limit = 200):
    if frac > 1 or frac < 0:
        raise ValueError(f'Parameter frac should be in range [0, 1)')
    out_frac = Binary(bit_lenght=output_size_limit)

    for i in range(output_size_limit):
        frac = frac*2
        out_frac[-i-1] = frac >= 1.0
        frac, _ = math.modf(frac)
        if frac == 0:
            break
    return out_frac.strip_right()
def int_to_binary(input):
    return pybytes.Binary(input)
def get_sign(num: float):
    return abs(num), num < 0
def minimal_bin_places_for_decimal_precision(target_decimal_precision):
    return math.floor(target_decimal_precision*(math.log(2)+ math.log(5))/math.log(2))
def normalalize_float(f: float):
    counter = 0
    if f < 0:
        f = -f 
    while f < 1.0:
        counter -= 1
        f *= 2
    while f > 2.0:
        counter += 1
        f /= 2
    return f, counter

def to_float(object: object):
    if isinstance(object, str):
        as_float = fp(object)
    elif isinstance(object, float):
        as_float = object
    else:
        as_float = float(object)
    return as_float
def split_to_fixed(object: object, binary_places = 200, target_decimal_precision=None):
    as_float = to_float(object)

    if target_decimal_precision is not None:
        binary_places = minimal_bin_places_for_decimal_precision(target_decimal_precision)
    as_float, sign = get_sign(as_float)
    
    frac, whole = math.modf(as_float)

    out_whole = int_to_binary(whole)

    out_frac = float_to_binary(frac, binary_places)
    
    return Splitted(out_frac, out_whole, Binary(sign))
def denormalize_mantissa():
    pass
def mantissa_to_float(num: Binary, denormalized)-> float:
    out = 0.0 if denormalized else 1.0
    
    for i, bit in enumerate(reversed(num)):
        out += float(bit)*2**(-i-1)
    return out 
    
class BinaryFloatPoint:
    def __init__(self, mantissa: object, exponant: object, sign: object):
        self.mantissa = mantissa
        self.exponant = exponant
        self.sign = sign

class BinaryFixedPoint:
    def __init__(self, value: object, midpoint: int):
        pass
class Splitted:
    def __init__(self, frac, whole, sign) -> None:
        self.frac = frac
        self.whole = whole
        self.sign = sign
    def __str__(self) -> str:
        return f'SplitedFloat(whole={self.whole}, frac={self.frac}, sign={self.sign})'


class CustomFloat:
    def __init__(self, MANTISA_SIZE: int, EXPONENTIAL_SIZE: int, EXPONENT_BIAS = None):
        self.MANTISA_SIZE = MANTISA_SIZE
        self.EXPONENTIAL_SIZE = EXPONENTIAL_SIZE
        self.EXPONENT_BIAS = -abs(EXPONENT_BIAS) if EXPONENT_BIAS is not None else -(2**(EXPONENTIAL_SIZE-1)-1)
    def __call__(self, *args, **kwds):
        pass
    def get(self, object: object):
        as_float = to_float(object)
        
        sign = as_float < 0
        as_float = abs(as_float)

        normalized, count = normalalize_float(as_float)

        biased_count = count-self.EXPONENT_BIAS

        manissa = Binary(bit_lenght=self.MANTISA_SIZE)
        splitted = split_to_fixed(normalized)
        manissa[-len(splitted.frac):] = splitted.frac

        return Binary(sign), manissa, Binary(biased_count, self.EXPONENTIAL_SIZE)
    def __len__(self):
        return self.EXPONENTIAL_SIZE+self.MANTISA_SIZE+1
    def get_concat(self, object: object):
        sign, manissa, exp = self.get(object)
        total_size = len(self)
        
        output = Binary(bit_lenght=total_size)
        output[-1] = sign
        output[-self.EXPONENTIAL_SIZE-1:-1] = exp
        output[:-self.EXPONENTIAL_SIZE-1] = manissa

        return output
    def get_hex(self, object: object):
        num = self.get_concat(object)
        return "{0:#0{1}x}".format(int(num), math.ceil(len(self)/4)+2)
    def get_mantissa(self, num: Binary):
        return num[:-self.EXPONENTIAL_SIZE-1]
    def get_exponent(self, num: Binary):
        return num[-self.EXPONENTIAL_SIZE-1:-1]
    def get_sign(self, num: Binary):
        return num[-1]
    def get_float(self, input:str):
        x = Binary(input, bit_lenght=len(self))
        mantissa = self.get_mantissa(x)
        exponent = self.get_exponent(x)
        sign = self.get_sign(x)

        mantissa_as_float = mantissa_to_float(mantissa, exponent==0)
        if exponent == 0:
            exponent = 1.0
        mantissa_as_float = mantissa_as_float*2**(float(exponent)+self.EXPONENT_BIAS)

        mantissa_as_float = -mantissa_as_float if sign else mantissa_as_float

        return mantissa_as_float


        
    

    
        

