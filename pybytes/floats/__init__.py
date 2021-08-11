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
    def __init__(self, MANTISA_SIZE: int, EXPONENTIAL_SIZE: int, SIGN_FLAG: bool):
        self.MANTISA_SIZE = MANTISA_SIZE
        self.EXPONENTIAL_SIZE = EXPONENTIAL_SIZE
        self.SIGN_FLAG = SIGN_FLAG

    def float_to_binary(self, frac: float, output_size_limit = 200):
        if frac > 1 or frac < 0:
            raise ValueError(f'Parameter frac should be in range [0, 1)')
        out_frac = Binary(bit_lenght=output_size_limit, reversed_display='.')

        for i in range(output_size_limit):
            frac = frac*2
            out_frac[i] = frac >= 1.0
            frac, _ = math.modf(frac)
            if frac == 0:
                break
        return out_frac.strip()
    def int_to_binary(self, input):
        return pybytes.Binary(input)
    def get_sign(self, num: float):
        return abs(num), num < 0
    
    def split(self, object: object) -> str:
        if isinstance(object, str):
            as_float = fp(object)
        elif isinstance(object, float):
            as_float = object
        else:
            as_float = float(object)
        
        as_float, sign = self.get_sign(as_float)
        
        frac, whole = math.modf(as_float)

        out_whole = self.int_to_binary(whole)
        out_frac = self.float_to_binary(frac)
        
        return Splitted(out_frac, out_whole, Binary(sign))

    
        

