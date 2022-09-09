use pyo3::{prelude::*};
use crate::binary::BinaryBase;

#[pyclass]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Flags {
    pub overflow: bool,
    pub zeroflag: bool,
    pub signflag: bool,
}

impl Flags {
    pub fn new(overflow: bool, zeroflag: bool, signflag: bool) -> Self {
        Self {
            overflow,
            zeroflag,
            signflag,
        }
    }

    pub fn from_binary(overflow: bool, binary: &BinaryBase) -> Self
    {
        use crate::binary::reduce::ReduceOps;
        let zeroflag = binary.data.as_slice().none();
        let signflag = binary.sign_bit();
        Self::new(overflow, zeroflag, signflag)
    }
}

#[pymethods]
impl Flags {
    pub fn __repr__(&self) -> String {
        format!("Flags(of={}, zf={}, sf={})", self.overflow, self.zeroflag, self.signflag)
    }
    #[getter]
    pub fn overflow(&self) -> bool {
        self.overflow
    }
    #[getter]
    pub fn zeroflag(&self) -> bool {
        self.zeroflag
    }
    #[getter]
    pub fn signflag(&self) -> bool {
        self.signflag
    }
}
