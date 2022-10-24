from .bitvec import * # type: ignore
from . import alias

__doc__ = bitvec.__doc__ # type: ignore
if hasattr(bitvec, "__all__"): # type: ignore
	__all__ = bitvec.__all__ # type: ignore
	__all__ += ['alias']          # type: ignore
