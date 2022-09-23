use pyo3::{prelude::*};
use pyo3::exceptions::PyTypeError;

mod shifts_base 
{
    use std::convert::TryInto;

    use bv::Bits;
    use pyo3::{exceptions::PyValueError, PyResult, types::PySliceIndices};

    use crate::binary::BinaryBase;

    pub fn overflowing_lsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<(BinaryBase, BinaryBase)>
    {
        //               1
        // 1010 << 1  ->  0100
        //              10
        // 1010 << 2  ->  1000

        let shift: i64 = _b.into();
        
        if shift < 0 
        {
            Err(PyValueError::new_err("negative shift value"))
        } 
        else 
        {
            let mut result = bv::BitVec::<u32>::with_capacity(_a.len());
            let clamped_shift = shift.clamp(0, _a.len().try_into().unwrap());

            for _ in 0..clamped_shift {
                result.push(false);
            }
            let size = _a.len() as i64 - clamped_shift;

            for i in 0..size {
                result.push(_a.data.get_bit(i as u64));
            }
            let carry_start = _a.len() as i64 - shift;
            let carry_end = carry_start + shift;
            
            let carry = if carry_start >= 0 {
                _a.get_slice(&PySliceIndices::new(carry_start.try_into().unwrap(), carry_end.try_into().unwrap(), 1))?
            } else {
                let mut c = _a.clone();
                c.prepend_slice(&bv::BitVec::new_fill(false, carry_start.abs().try_into().unwrap()));
                c.data
            };
            Ok((BinaryBase::from_data(result), BinaryBase::from_data(carry)))
        }
    }

    pub fn wrapping_lsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<BinaryBase>
    {
        let (shift, _) = overflowing_lsh(_a, _b)?;

        Ok(shift)
    }

    pub fn logical_underflowing_rsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<(BinaryBase, BinaryBase)>
    {
        let shift: i64 = _b.into();

        if shift < 0 
        {
            Err(PyValueError::new_err("negative shift value"))
        } 
        else 
        {
            let mut result = bv::BitVec::<u32>::with_capacity(_a.len());
            let clamped_shift = shift.clamp(0, _a.len().try_into().unwrap());
            let len = _a.len() as i64;
            
            for i in clamped_shift..len {
                result.push(_a.data.get_bit(i as u64));
            }

            for _ in 0..clamped_shift {
                result.push(false);
            }

            let carry_start = 0;
            let carry_end = shift;

            let carry = _a.get_slice(&PySliceIndices::new(carry_start.try_into().unwrap(), carry_end.try_into().unwrap(), 1))?;
        
            Ok((BinaryBase::from_data(result), BinaryBase::from_data(carry)))
        }
    }

    pub fn logical_wrapping_rsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<BinaryBase>
    {
        let (shift, _) = logical_underflowing_rsh(_a, _b)?;

        Ok(shift)
    }

    pub fn arithmetic_underflowing_rsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<(BinaryBase, BinaryBase)>
    {
        let shift: i64 = _b.into();

        if shift < 0 
        {
            Err(PyValueError::new_err("negative shift value"))
        } 
        else 
        {
            let mut result = bv::BitVec::<u32>::with_capacity(_a.len());
            let clamped_shift = shift.clamp(0, _a.len().try_into().unwrap());
            let len = _a.len() as i64;
            
            for i in clamped_shift..len {
                result.push(_a.data.get_bit(i as u64));
            }

            let se = _a.sign_extending_bit();
            for _ in 0..clamped_shift {
                result.push(se);
            }

            let carry_start = 0;
            let carry_end = shift;

            let carry = _a.get_slice(&PySliceIndices::new(carry_start.try_into().unwrap(), carry_end.try_into().unwrap(), 1))?;
        
            Ok((BinaryBase::from_data(result), BinaryBase::from_data(carry)))
        }
    }

    pub fn arithmetic_wrapping_rsh(_a: &BinaryBase, _b: &BinaryBase) -> PyResult<BinaryBase>
    {
        let (shift, _) = arithmetic_underflowing_rsh(_a, _b)?;

        Ok(shift)
    }
}


// pyfunctions
#[pyfunction]
pub fn overflowing_lsh(_a: &crate::Binary, other: &PyAny) -> PyResult<(crate::Binary, crate::Binary)>
{
    let (result, carry) = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::overflowing_lsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::overflowing_lsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok((crate::Binary { inner: result }, crate::Binary { inner: carry } ))
}

#[pyfunction]
pub fn wrapping_lsh(_a: &crate::Binary, other: &PyAny) -> PyResult<crate::Binary>
{
    let result = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::wrapping_lsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::wrapping_lsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok(crate::Binary { inner: result })
}

#[pyfunction]
pub fn logical_underflowing_rsh(_a: &crate::Binary, other: &PyAny) -> PyResult<(crate::Binary, crate::Binary)>
{
    let (result, carry) = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::logical_underflowing_rsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::logical_underflowing_rsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok((crate::Binary { inner: result }, crate::Binary { inner: carry } ))
}

#[pyfunction]
pub fn logical_wrapping_rsh(_a: &crate::Binary, other: &PyAny) -> PyResult<crate::Binary>
{
    let result = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::logical_wrapping_rsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::logical_wrapping_rsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok(crate::Binary { inner: result })
}

#[pyfunction]
pub fn arithmetic_underflowing_rsh(_a: &crate::Binary, other: &PyAny) -> PyResult<(crate::Binary, crate::Binary)>
{
    let (result, carry) = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::arithmetic_underflowing_rsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::arithmetic_underflowing_rsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok((crate::Binary { inner: result }, crate::Binary { inner: carry } ))
}

#[pyfunction]
pub fn arithmetic_wrapping_rsh(_a: &crate::Binary, other: &PyAny) -> PyResult<crate::Binary>
{
    let result = if let Ok(_b) = other.extract::<PyRef<crate::Binary>>() {   
        shifts_base::arithmetic_wrapping_rsh(&_a.inner, &_b.inner)
    } else if let Ok(_b) = crate::Binary::from(other, Some(_a.len().try_into().unwrap()), Some(_a.sign_behavior())) {
        shifts_base::arithmetic_wrapping_rsh(&_a.inner, &_b.inner)
    } else {
        return Err(PyTypeError::new_err(format!("Invalid type {}", other)));
    }?;

    Ok(crate::Binary { inner: result })
}
