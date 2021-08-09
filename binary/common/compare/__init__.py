import binary.common.compare.compare_base as cmp_base
import binary.binary_class as binary_class

def less(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    return cmp_base.less_compare_arrays(rsh._data, lsh._data)
def greater(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    return cmp_base.greater_compare_arrays(rsh._data, lsh._data)
def equal(rsh: binary_class.Binary, lsh: object) -> bool:
    if not isinstance(lsh, binary_class.Binary):
        lsh = binary_class.Binary(lsh, sign_behavior=rsh._sign_behavior)
    return cmp_base.equal_compare_arrays(rsh._data, lsh._data)