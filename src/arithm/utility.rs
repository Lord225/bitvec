use std::convert::TryInto;

use bv::BitsPush;
use pyo3::{prelude::*, exceptions::PyOverflowError, exceptions::PyValueError};
use crate::Binary;
use crate::binary::BinaryBase;


pub fn cast_base(binary: &BinaryBase, sign_behavior: &str) -> BinaryBase
{
    BinaryBase::from_parts(binary.data.clone(), sign_behavior.to_string())
}


pub fn convert_base(binary: &BinaryBase, sign_behavior: &str) -> PyResult<BinaryBase>
{
    fn to_signed(binary: &BinaryBase) -> PyResult<BinaryBase> 
    {
        match binary.sign_behavior.as_str() {
            "unsigned" => {
                if binary.sign_bit() {
                    Err(PyOverflowError::new_err(format!("Converstion overflow: value {} is to big to represent as signed", binary.to_string_formatted_default())))
                } else {
                    Ok(cast_base(binary, "signed"))
                }
            },
            "signed" => Ok(binary.clone()),
            _ => Err(PyValueError::new_err("Invalid sign behavior"))
        }
    }
    fn to_unsigned(binary: &BinaryBase) -> PyResult<BinaryBase> 
    {
        match binary.sign_behavior.as_str() {
            "unsigned" => Ok(binary.clone()),
            "signed" => {
                if binary.sign_bit() {
                    Err(PyOverflowError::new_err(format!("Converstion overflow: value {} is negative so it cant be represented as unsigned integer", binary.to_string_formatted_default())))
                } else {
                    Ok(cast_base(binary, "signed"))
                }
            }
            _ => Err(PyValueError::new_err("Invalid sign behavior"))
        }
    }

    match sign_behavior {
        "signed" => to_signed(binary),
        "unsigned" => to_unsigned(binary),
        _ => Err(PyValueError::new_err(format!("Invalid sign behavior: {}", sign_behavior)))
    }
}
pub fn extend_to_signed_base(binary: &BinaryBase) -> PyResult<BinaryBase>
{
    match binary.sign_behavior.as_str() {
        "unsigned" => {
            if binary.sign_bit() {
                let mut cloned = binary.data.clone();
                cloned.push_bit(false);
                //BinaryBase::from_parts(cloned, "signed".into())
                Ok(BinaryBase::from_parts(cloned, "signed".into()))
            } else {
                Ok(cast_base(binary, "signed"))
            }
        },
        "signed" => Ok(binary.clone()),
        _ => Err(PyValueError::new_err("Invalid sign behavior"))
    }
}

pub fn pad(binary: &BinaryBase, length: usize, bit: bool) -> BinaryBase
{
    let mut data = binary.data.clone();
    data.resize(length.try_into().unwrap(), bit);
    
    //BinaryBase::from_parts(data, binary.inner.sign_behavior.clone())
    BinaryBase::from_parts(data, binary.sign_behavior.clone())
}


#[pyfunction]
pub fn cast(binary: &Binary, sign_behavior: &str) -> PyResult<PyObject>
{
    Binary::wrap_object(Ok(cast_base(&binary.inner, sign_behavior)))
}

#[pyfunction]
pub fn convert(binary: &Binary, sign_behavior: &str) -> PyResult<PyObject>
{
    Binary::wrap_object(convert_base(&binary.inner, sign_behavior))
}

#[pyfunction]
pub fn extend_to_signed(binary: &Binary) -> PyResult<PyObject>
{
    Binary::wrap_object(extend_to_signed_base(&binary.inner))
}

#[pyfunction]
pub fn pad_zeros(binary: &Binary, length: usize) -> PyResult<PyObject>
{
    Binary::wrap_object(Ok(pad(&binary.inner, length, false)))
}

#[pyfunction]
pub fn pad_ones(binary: &Binary, length: usize) -> PyResult<PyObject>
{
    Binary::wrap_object(Ok(pad(&binary.inner, length, true)))
}

#[pyfunction]
pub fn pad_sign_extend(binary: &Binary, length: usize) -> PyResult<PyObject>
{
    Binary::wrap_object(Ok(pad(&binary.inner, length, binary.inner.sign_bit())))
}

