use std::convert::TryInto;

use crate::binary::BinaryBase;
use pyo3::{prelude::*, types::PySliceIndices};


macro_rules! gen_bitwise_all { 
    ($([$function:ident, $bv_function:ident]),*) => {
        pub mod bitwise_base {
            use crate::binary::BinaryBase;
            use bv::{Bits, BitsExt};

            pub fn bitwise_not(binary: &BinaryBase) -> BinaryBase {
                BinaryBase::from_parts(binary.data.bit_not().to_bit_vec(), binary.sign_behavior.clone())
            }

            $(
                pub fn $function(a: &BinaryBase, b: &BinaryBase) -> BinaryBase {
                    BinaryBase::from_parts(a.data.$bv_function(&b.data).to_bit_vec(), a.sign_behavior.clone())
                }
            )*
    
        }

        #[pyfunction]
        pub fn bitwise_not(a: PyRef<crate::Binary>) -> PyResult<PyObject> {
            crate::Binary::wrap_object(Ok(bitwise_base::bitwise_neg(&a.inner)))
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
        )*
    }
}

gen_bitwise_all!([bitwise_or, bit_or], [bitwise_xor, bit_xor], [bitwise_and, bit_and]);
