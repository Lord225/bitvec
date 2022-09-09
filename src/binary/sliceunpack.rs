use pyo3::{AsPyPointer};
use pyo3::prelude::*;


pub trait PySliceUnpack {
    /// Extract the `start`, `stop` and `step` data members from a slice object as integers
    fn unpack(&self) -> PyResult<pyo3::types::PySliceIndices>;
}


impl PySliceUnpack for &pyo3::types::PySlice {
    fn unpack(&self) ->  PyResult<pyo3::types::PySliceIndices> {
        // safty: pyo3 has been doing it in this way so it has to be safe!
        unsafe {
            let mut start: isize = 0;
            let mut stop: isize = 0;
            let mut step: isize = 0;

            let r = pyo3::ffi::PySlice_Unpack(self.as_ptr(),  &mut start,  &mut stop,  &mut step);

            if r == 0 {
                Ok(pyo3::types::PySliceIndices::new(start, stop, step))
            } else {
                Err(PyErr::fetch(self.py()))
            }
        }
    }
}







