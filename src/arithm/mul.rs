use pyo3::prelude::*;

pub mod base_mul {
    use crate::binary::BinaryBase;
    use pyo3::{types, prelude::*};

    pub fn multiply(a: &crate::Binary, b: &crate::Binary) -> PyResult<crate::Binary> {
        // I'm lazy as fukx
        // just convert to python int and multiply them
        let a_py_int = a.int()?;
        let b_py_int = b.int()?;

        // best fitting size and sign beheavior for output
        let (sign_behavior, size) = match (a.sign_behavior().as_str(), b.sign_behavior().as_str()) {
            ("signed", _) | (_, "signed") => ("signed",   a.len() + b.len()),
            _                             => ("unsigned", a.len() + b.len()),
        };

        Python::with_gil(|py| {
            let result = a_py_int.call_method1(py, "__mul__", (b_py_int,))?;
            let result = BinaryBase::parse_bitvec_from_long_integer(result.extract::<&types::PyLong>(py)?, Some(size), Some(sign_behavior));

            crate::Binary::wrap(result)
        })
    }
    /// same as multiply but returns splitted output as tuple of (result, carry) (splited at a.len())
    pub fn overflowing_mul(a: &crate::Binary, b: &crate::Binary) -> PyResult<(crate::Binary, crate::Binary)>{
        let result = multiply(a, b)?;
        
        let low  = result.inner.get_slice(&types::PySliceIndices::new(0,                a.len()      as isize, 1))?;
        let high = result.inner.get_slice(&types::PySliceIndices::new(a.len() as isize, result.len() as isize, 1))?;
        
        Ok((crate::Binary::from_parts(low, "unsigned".into()), crate::Binary::from_parts(high, "unsigned".into())))
    }
    /// same as multiply but returns truncated to a.len()
    pub fn wrapping_mul(a: &crate::Binary, b: &crate::Binary) -> PyResult<crate::Binary> {
        let (result, _) = overflowing_mul(a, b)?;
        
        Ok(result)
    }
}


#[pyfunction]
pub fn multiply(a: &crate::Binary, b: &crate::Binary) -> PyResult<PyObject> {
    Ok(base_mul::multiply(a, b)?.into())
}

#[pyfunction]
pub fn overflowing_mul(a: &crate::Binary, b: &crate::Binary) -> PyResult<(PyObject, PyObject)> {
    let (low, high) = base_mul::overflowing_mul(a, b)?;
    
    Ok((low.into(), high.into()))
}

#[pyfunction]
pub fn wrapping_mul(a: &crate::Binary, b: &crate::Binary) -> PyResult<PyObject> {
    let result = base_mul::wrapping_mul(a, b)?;
    
    Ok(result.into())
}

