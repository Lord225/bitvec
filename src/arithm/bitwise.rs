use std::convert::TryInto;

use crate::binary::BinaryBase;
use pyo3::{prelude::*, types::PySliceIndices};

macro_rules! gen_bitwise_all { 
    ($([$function:ident, $neg_function:ident, $bv_function:ident]),*) => {
        pub mod bitwise_base {
            use crate::binary::BinaryBase;
            use bv::{Bits, BitsExt};

            pub fn bitwise_not(binary: &BinaryBase) -> BinaryBase {
                BinaryBase::from_parts(binary.data.bit_not().to_bit_vec(), binary.sign_behavior.clone())
            }

            $(
                pub fn $function(a: &BinaryBase, b: &BinaryBase) -> BinaryBase {
                    let value = a.data.$bv_function(&b.data).to_bit_vec();
                    BinaryBase::from_parts(value, a.sign_behavior.clone())
                }
                pub fn $neg_function(a: &BinaryBase, b: &BinaryBase) -> BinaryBase {
                    let value = a.data.$bv_function(&b.data).bit_not().to_bit_vec();
                    BinaryBase::from_parts(value, a.sign_behavior.clone())
                }
            )*
    
        }

        #[pyfunction]
        pub fn bitwise_not(a: PyRef<crate::Binary>) -> PyResult<PyObject> {
            crate::Binary::wrap_object(Ok(bitwise_base::bitwise_not(&a.inner)))
        }

        $(
            #[pyfunction]
            pub fn $function(a: PyRef<crate::Binary>, b: PyRef<crate::Binary>) -> PyResult<PyObject> {
                crate::Binary::wrap_object(
                    if a.len() == b.len() {
                        Ok(bitwise_base::$function(&a.inner, &b.inner))
                    } else if a.len() > b.len() {
                        let slice = BinaryBase::from_data(b.inner.get_slice(&PySliceIndices::new(0, a.len().try_into().unwrap(), 1))?);
                        Ok(bitwise_base::$function(&a.inner, &slice))
                    } else {
                        let slice = BinaryBase::from_data(a.inner.get_slice(&PySliceIndices::new(0, b.len().try_into().unwrap(), 1))?);
                        Ok(bitwise_base::$function(&slice, &b.inner))
                    }
                )
            }
            #[pyfunction]
            pub fn $neg_function(a: PyRef<crate::Binary>, b: PyRef<crate::Binary>) -> PyResult<PyObject> {
                crate::Binary::wrap_object(
                    if a.len() == b.len() {
                        Ok(bitwise_base::$neg_function(&a.inner, &b.inner))
                    } else if a.len() > b.len() {
                        let slice = BinaryBase::from_data(b.inner.get_slice(&PySliceIndices::new(0, a.len().try_into().unwrap(), 1))?);
                        Ok(bitwise_base::$neg_function(&a.inner, &slice))
                    } else {
                        let slice = BinaryBase::from_data(a.inner.get_slice(&PySliceIndices::new(0, b.len().try_into().unwrap(), 1))?);
                        Ok(bitwise_base::$neg_function(&slice, &b.inner))
                    }
                )
            }
        )*
    }
}

gen_bitwise_all!([bitwise_or, bitwise_nor, bit_or], [bitwise_xor, bitwise_xnor, bit_xor], [bitwise_and, bitwise_nand, bit_and]);

