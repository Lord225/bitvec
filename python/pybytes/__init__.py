from .pybytes import * # type: ignore
from . import alias

__doc__ = pybytes.__doc__ # type: ignore
if hasattr(pybytes, "__all__"): # type: ignore
	__all__ = pybytes.__all__ # type: ignore
	__all__ += [alias]          # type: ignore
