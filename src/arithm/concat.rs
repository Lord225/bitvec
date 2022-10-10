use pyo3::{prelude::*, types, exceptions};
use bv;

use crate::binary::BinaryBase;


pub fn append_any(bitvec: &mut BinaryBase, obj: &PyAny) -> PyResult<()>{
    if let Ok(bin) = obj.extract::<PyRef<crate::Binary>>() { 
        bitvec.append_slice(&bin.inner.data);
    } else if let Ok(bin) = obj.extract::<bool>() { 
        bitvec.append_bit(bin);
    } else if let Ok(bin) = crate::Binary::from(obj, None, None) {
        bitvec.append_slice(&bin.inner.data);
    } else {
        return Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", obj)))
    }
    Ok(())
}

#[pyfunction(args="*")]
pub fn concat(args: &types::PyTuple) -> PyResult<PyObject> {
    let slice = args.as_slice();
    let mut bitvec = BinaryBase::from_data(bv::BitVec::new());

    for arg in slice.iter().rev() {
        append_any(&mut bitvec, arg)?;
    }
    
    crate::Binary::wrap_object(Ok(bitvec))
}