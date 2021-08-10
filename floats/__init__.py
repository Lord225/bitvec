import binary 


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

class FloatPoint:
    def __init__(self, MANTISA_SIZE: int, EXPONENTIAL_SIZE: int, SIGN_FLAG: bool):
        self.MANTISA_SIZE = MANTISA_SIZE
        self.EXPONENTIAL_SIZE = EXPONENTIAL_SIZE
        self.SIGN_FLAG = SIGN_FLAG

    def to_hex(self, _input) -> str:
        if _input is str:
            _input = fp(_input)
        else:
            _input = float(_input)

