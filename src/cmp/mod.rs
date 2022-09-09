use std::cmp::Ordering;

use pyo3::prelude::*;

pub fn equal_cmp(a: &crate::Binary, b: &crate::Binary) -> bool {
    if a.len() == b.len() {
        a.inner.data == b.inner.data
    } else {
        false
    }
}

pub fn cmp(a: &crate::Binary, b: &crate::Binary) -> PyResult<Ordering> {
    if equal_cmp(a, b) {
        return Ok(Ordering::Equal);
    }

    let a_py_int = a.int()?;
    let b_py_int = b.int()?;

    Python::with_gil(|py| {
        let lt = a_py_int
            .call_method1(py, "__lt__", (b_py_int,))?
            .is_true(py)?; // lazy

        if lt {
            return Ok(Ordering::Less);
        }

        return Ok(Ordering::Greater);
    })
}
