use pyo3::{prelude::*};


mod hamming_distance_base {
    use bv::Bits;
    use pyo3::{exceptions::PyValueError, PyResult};

    use crate::binary::BinaryBase;


    pub fn hamming_distance(a: &BinaryBase, b: Option<&BinaryBase>) -> PyResult<usize> {
        let b_ref = BinaryBase::from_data(bv::BitVec::new());
        let b = b.unwrap_or(&b_ref);

        if a.sign_behavior != b.sign_behavior {
            return Err(PyValueError::new_err("Sign behavior mismatch, try casting one value"));
        }


        let a_data = &a.data;
        let b_data = &b.data;

        let mut distance = 0;
        
        for bi in 0..a_data.block_len()
        {
            let a_block = if bi < a_data.block_len() { a_data.get_block(bi) } else { 0 }; 
            let b_block = if bi < b_data.block_len() { b_data.get_block(bi) } else { 0 };

            let mut xor = a_block ^ b_block;
            while xor != 0 {
                distance += 1;
                xor &= xor - 1;
            }
        }

        Ok(distance)
    }
}


#[pyfunction]
pub fn hamming_distance(a: &crate::Binary, b: &crate::Binary) -> PyResult<usize> {
    let distance = hamming_distance_base::hamming_distance(&a.inner, Some(&b.inner))?;

    Ok(distance) 
}