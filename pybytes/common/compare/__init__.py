import pybytes.common.compare.compare_base as cmp_base
import pybytes.binary_class as binary_class

def less(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh)
    return int(rsh) < int(lsh) # Much safer than cmp_base module
def greater(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh)
    return int(rsh) > int(lsh)
def equal(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh)
    return int(rsh) == int(lsh)