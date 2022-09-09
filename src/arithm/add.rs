use pyo3::{prelude::*};


pub mod add_base {
    use crate::binary::BinaryBase;
    use super::super::flags::*;
    use super::super::bitwise::bitwise_base;
    use pyo3::{prelude::*};
    use bv::{BitVec, Bits, BitsPush};
    use pyo3::exceptions::{PyTypeError, PyValueError};

    pub fn add_binary(a: &BinaryBase, b: Option<&BinaryBase>, mut carry: bool) -> PyResult<(BinaryBase, Flags)> 
    {
        let b_ref = BinaryBase::from_data(bv::BitVec::new());
        let b = b.unwrap_or(&b_ref);

        if a.sign_behavior != b.sign_behavior {
            return Err(PyValueError::new_err("Sign behavior mismatch, try casting one value"));
        }

        let len = Ord::max(a.len(), b.len());
        
        let a_data = &a.data;
        let b_data = &b.data;

        let block_len = Ord::max(a_data.block_len(), b_data.block_len());
        let mut result = BitVec::with_block_capacity(block_len);

        for bi in 0..a_data.block_len()
        {
            let a_block = if bi < a_data.block_len() { a_data.get_block(bi) } else { 0 }; 
            let b_block = if bi < b_data.block_len() { b_data.get_block(bi) } else { 0 };

            let (sum, cout) = u32::carrying_add(a_block, b_block, carry);
            carry = cout;
            
            result.push_block(sum);
        }
        
        let overflow = if carry { true } else if result.bit_len() > len { result.get_bit(len) } else { false };
        
        result.truncate(len);

        let result = BinaryBase::from_parts(result, a.sign_behavior.clone());
        let flags = Flags::from_binary(overflow, &result);

        return Ok((result, flags));
    }

    pub fn arithmetic_neg(a: &BinaryBase) -> PyResult<BinaryBase> 
    {
        let negated = bitwise_base::bitwise_neg(a);
        
        let (output, _) = add_binary(&negated, None, true)?;

        return Ok(output);
    }

    pub fn flaged_add(left: &crate::Binary, right: &crate::Binary, py: &Python) -> PyResult<(PyObject, Flags)>
    {
        let (sum, flags) = add_binary(&left.inner, Some(&right.inner), false)?;

        crate::Binary::wrap_object_gil(Ok(sum), py).and_then(|x| Ok((x, flags)))
    }


    pub fn add(binary: PyRef<crate::Binary>, other: &PyAny, py: &Python) -> PyResult<(PyObject, Flags)> {
        let _a = binary;
        
        if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
            flaged_add(&_a, &_b, &py)
        } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
            flaged_add(&_a, &_b, &py)
        } else {
            return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
        }
    }
}

#[pyfunction]
pub fn flaged_add(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<(PyObject, PyObject)> {
    Python::with_gil(|py| {
        let (sum, flags) = add_base::add(binary, other, &py)?;

        Ok((sum, flags.into_py(py)))
    })
}


#[pyfunction]
pub fn overflowing_add(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<(PyObject, PyObject)> {
    Python::with_gil(|py| {
        let (sum, flags) = add_base::add(binary, other, &py)?;

        Ok((sum, flags.overflow.into_py(py)))
    })
}

#[pyfunction]
pub fn wrapping_add(binary: PyRef<crate::Binary>, other: &PyAny) -> PyResult<PyObject> {
    let (sum, _) = overflowing_add(binary, other)?;

    Ok(sum)
}

#[pyfunction]
pub fn arithmetic_neg(binary: PyRef<crate::Binary>) -> PyResult<PyObject> {
    Python::with_gil(|py| {
        let negated = add_base::arithmetic_neg(&binary.inner)?;

        crate::Binary::wrap_object_gil(Ok(negated), &py)
    })
}