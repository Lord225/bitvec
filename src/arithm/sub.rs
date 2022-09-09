use pyo3::exceptions::PyTypeError;
use pyo3::{prelude::*};

use crate::binary::BinaryBase;
use super::add::add_base::add_binary;
use super::bitwise::bitwise_base;
use super::flags::*;
use super::utility::cast_base;

fn base_sub_binary(a: &BinaryBase, b: &BinaryBase) -> PyResult<(BinaryBase, Flags)> 
{
    let a_signed = cast_base(a, "signed");
    let b_signed = bitwise_base::bitwise_neg(&cast_base(b, "signed"));
    
    add_binary(&a_signed, Some(&b_signed), true)
}

fn base_flaged_sub_binary(left: &crate::Binary, right: &crate::Binary, py: &Python) -> PyResult<(PyObject, Flags)>
{
    let (out, flags) = base_sub_binary(&left.inner, &right.inner)?;
    
    crate::Binary::wrap_object_gil(Ok(out), py).and_then(|x| Ok((x, flags)))
}

fn base_sub(binary: PyRef<crate::Binary>, other: &PyAny, py: &Python) -> PyResult<(PyObject, Flags)> {
    let _a = binary;
    
    if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        base_flaged_sub_binary(&_a, &_b, &py)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        base_flaged_sub_binary(&_a, &_b, &py)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }
}

#[pyfunction]
pub fn flaged_sub(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<(PyObject, PyObject)> {
    Python::with_gil(|py| {
        let (sum, flags) = base_sub(binary, other, &py)?;

        Ok((sum, flags.into_py(py)))
    })
}



#[pyfunction]
pub fn overflowing_sub(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<(PyObject, PyObject)> {
    Python::with_gil(|py| {
        let (sum, flags) = base_sub(binary, other, &py)?;

        Ok((sum, flags.overflow.into_py(py)))
    })
}

#[pyfunction]
pub fn wrapping_sub(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<PyObject> {
    let (sum, _) = overflowing_sub(binary, other)?;

    Ok(sum)
}