#![feature(is_some_with)]
#![feature(int_roundings)]
#![feature(bigint_helper_methods)]
#![feature(decl_macro)]

use std::cmp::Ordering;

use pyo3::pyclass::CompareOp;
use pyo3::{prelude::*, types};
use pyo3::exceptions;
use pyo3::types::IntoPyDict;

use bv::{self, Bits};

mod binary;
mod arithm;
mod cmp;


#[pyclass]
#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct Binary
{
    inner: binary::BinaryBase,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct BinaryIterator
{
    inner: Py<Binary>,
    chunk_size: usize,
    index: usize,
}

// Arg Parsing
impl Binary
{
    fn parse_args(args: &types::PyTuple) -> PyResult<(Option<usize>, Option<&str>, Option<usize>)>
    {
        fn parse_usize(might_be_usize: &PyAny) -> PyResult<Option<usize>> { Ok(if !might_be_usize.is_none() { Some(might_be_usize.extract::<usize>()?) } else {None}) }
        fn parse_str(might_be_str: &PyAny) -> PyResult<Option<&str>> { Ok(if !might_be_str.is_none() { Some(might_be_str.extract::<&str>()?) } else {None}) }
        
        Ok(match args.as_slice() {
            [] => 
            {
                (None, None, None)
            },
            [bit_size] => 
            {
                let bit_size = parse_usize(bit_size)?;

                (bit_size, None, None)
            },
            [bit_size, sign_behavior] => 
            {
                let bit_size = parse_usize(bit_size)?;
                let sign_behavior = parse_str(sign_behavior)?;

                (bit_size, sign_behavior, None)
            },
            [bit_size, sign_behavior, byte_size] => 
            {
                let bit_size = parse_usize(bit_size)?;
                let sign_behavior = parse_str(sign_behavior)?;
                let byte_size = parse_usize(byte_size)?;

                (bit_size, sign_behavior, byte_size)
            },
            _ => 
            {
                return Err(exceptions::PyTypeError::new_err(format!("Invalid arguments: {:?}", args)));
            }
        })
    }

    fn parse_kwargs(kwargs: Option<&types::PyDict>) -> PyResult<(Option<usize>, Option<&str>, Option<usize>, Option<bool>)>
    {
        Ok(if let Some(kwargs) = kwargs {
            (
                kwargs.get_item("lenght").and_then(|x| Some(x.extract::<usize>().ok()?)),
                kwargs.get_item("sign_behavior").and_then(|x| Some(x.extract::<&str>().ok()?)),
                kwargs.get_item("byte_lenght").and_then(|x| Some(x.extract::<usize>().ok()?)),
                kwargs.get_item("signed").and_then(|x| Some(x.extract::<bool>().ok()?)),
            )
        }
        else
        {
            (None, None, None, None)
        })
    }
}

impl Binary
{
    pub fn wrap(inner: PyResult<binary::BinaryBase>) -> PyResult<Self>
    {
        inner.and_then(|inner| Ok( Binary { inner }))
    }

    pub fn wrap_object(inner: PyResult<binary::BinaryBase>) -> PyResult<PyObject>
    {
        Python::with_gil(|py| Self::wrap_object_gil(inner, &py))
    }
    pub fn wrap_object_gil(inner: PyResult<binary::BinaryBase>, py: &Python) -> PyResult<PyObject>
    {
        Self::wrap(inner).and_then(|binary| Ok(binary.into_py(*py)))
    }

    pub fn unwrap(&self) -> &binary::BinaryBase
    {
        &self.inner
    }

    pub fn from(object: &PyAny, bit_size: Option<usize>, sign_behavior: Option<&str>) ->  PyResult<Self>
    {
        // from str
        if let Ok(object) = object.extract::<&str>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_str(object, bit_size, sign_behavior));
        }
        // from isize
        if let Ok(object) = object.extract::<isize>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_isize(object, bit_size, sign_behavior));
        }
        // from int
        if let Ok(true) = object.is_instance_of::<types::PyLong>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_long_integer(&object.downcast().unwrap(), bit_size, sign_behavior));
        }
        // copy constructor
        if let Ok(object) = object.extract::<PyRef<Binary>>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_copy(object.unwrap(), bit_size, sign_behavior));
        }
        // from iterable
        if let Ok(object) = object.iter() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_iterable(object, bit_size, sign_behavior));
        }
        // from bytes
        if let Ok(object) = object.extract::<&types::PyBytes>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_bytes(&object, bit_size, sign_behavior));
        }
        // from float
        if let Ok(object) = object.extract::<f64>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_float(object, bit_size, sign_behavior));
        }
        
        return Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", object)));
    }

    fn slice(&self, slice: &types::PySliceIndices) -> PyResult<PyObject>
    {
        let slice = self.inner.get_slice(slice)?;

        return Self::wrap_object(binary::BinaryBase::parse_bitvec_from_slice(slice, None, None));
    }
    #[allow(unused)]
    fn from_parts(data: bv::BitVec::<u32>, sign: String) -> PyResult<Self>
    {
        Self::wrap(Ok(binary::BinaryBase {data, sign_behavior: sign}))
    }
}

impl Into<PyObject> for Binary
{
    fn into(self) -> PyObject
    {
        Python::with_gil(|py| self.into_py(py))
    }
}

impl Binary
{
    fn cmp(&self, obj: &PyAny) -> PyResult<Ordering>
    {
        // extract binary or crate new from object
        if let Ok(bin) = obj.extract::<PyRef<Binary>>() { 
            cmp::cmp(&self, &bin)
        } else if let Ok( bin) = Self::from(obj, None, Some(self.sign_behavior())) {
            cmp::cmp(&self, &bin)
        } else {
            Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", obj)))
        }
    }
}

#[pymethods]
impl Binary
{
    #[new]
    #[args(args = "*", kwargs = "**")]
    fn py_new(object: &PyAny, args: &types::PyTuple, kwargs: Option<&types::PyDict>,) -> PyResult<Self> 
    {
        // arguments:
        // * lenght
        // * sign_behavior
        // * byte_lenght

        // get args (all optional, if these are None or not provied None is used)
        let (bit_size_args, sign_behavior_args, byte_size_args) = Self::parse_args(args)?;
        
        // get kwargs (all optional, if provied None is used)
        let (bit_size_kwargs, sign_behavior_kwargs, byte_size_kwargs, signed_kwargs) = Self::parse_kwargs(kwargs)?;
        
        
        // choose the final value for bit size, if not provied at all None is used (to inherit from object)
        let bit_size = match (bit_size_args, bit_size_kwargs, byte_size_kwargs, byte_size_args) {
            (None, None, None, None) => None,
            (Some(bit_size), None, None, None) => Some(bit_size),
            (None, Some(bit_size), None, None) => Some(bit_size),
            (None, None, Some(byte_size), None) => Some(byte_size * 8),
            (None, None, None, Some(byte_size)) => Some(byte_size * 8),
            _ => {
                return Err(exceptions::PyTypeError::new_err(format!("Provided more than one size")));
            }
        };

        // choose the final value for sign behavior, if not provied at all None is used (to inherit from object)
        let sign_behavior = match (sign_behavior_args, sign_behavior_kwargs, signed_kwargs) {
            (None, None, None) => None,
            (Some(sign_behavior), None, None) => Some(sign_behavior),
            (None, Some(sign_behavior), None) => Some(sign_behavior),
            (None, Some(_), Some(true)) => Some("signed"),
            (None, Some(_), Some(false)) => Some("unsigned"),
            _ => {
                return Err(exceptions::PyTypeError::new_err(format!("Provided more than one sign_behavior")));
            }
        };

        // create the object
        Self::from(object, bit_size, sign_behavior)
    }

    #[getter]
    pub fn _data(&self) -> PyObject {
        let mut bytes  = self.inner.data.clone().into_boxed_slice();
        let (_, bytes, _) = unsafe { bytes.align_to_mut::<u8>() };

        Python::with_gil(|py| types::PyBytes::new(py, bytes).to_object(py))
    }
    #[getter]
    pub fn len(&self) -> usize {
        self.inner.len().try_into().unwrap()
    }
    #[getter]
    pub fn _sign_behavior(&self) -> &String {
        &self.inner.sign_behavior
    }

    pub fn sign_behavior(&self) -> &String {
        self._sign_behavior()
    }
    pub fn is_negative(&self) -> bool {
        if self.sign_behavior() == "unsigned" {
            return false;
        }
        return self.inner.data.get_bit(self.inner.data.bit_len() - 1);
    }
    pub fn sign_extending_bit(&self) -> bool {
        return self.inner.sign_extending_bit()
    }
    pub fn maximum_value(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            if self.len() == 0 {
                return Ok(0.into_py(py));
            }

            let one: PyObject = 1.into_py(py);
            let len: PyObject = self.len().into_py(py);
            
            if self.sign_behavior() == "unsigned" {
                // 1.__lshift__(len).__sub__(1)
                Ok(one.call_method1(py, "__lshift__", (&len,))?.call_method1(py, "__sub__", (&one,))?)
            } else {
                // 1.__lshift__(len.__sub__(1)).__sub__(1)
                Ok(one.call_method1(py, "__lshift__", (&len.call_method1(py, "__sub__", (&one,))?,))?.call_method1(py, "__sub__", (&one,))?)
            }
        })
    }
    pub fn minimum_value(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            if self.len() == 0 {
                return Ok(0.into_py(py));
            }
            
            if self.sign_behavior() == "unsigned" {
                Ok(0.into_py(py))
            } else {
                let one: PyObject = 1.into_py(py);
                let len: PyObject = self.len().into_py(py);
                
                // 1.__lshift__(len.__sub__(1)).__neg__()
                Ok(one.call_method1(py, "__lshift__", (&len.call_method1(py, "__sub__", (&one,))?,))?.call_method1(py, "__neg__", ())?)
            }
        })
    }

    pub fn low_byte(&self) -> PyResult<PyObject> {
        self.slice(&types::PySliceIndices::new(0, 8, 1))
    }
    pub fn high_byte(&self) -> PyResult<PyObject> {
        self.slice(&types::PySliceIndices::new(8, 16, 1))
    }
    pub fn extended_low(&self) -> PyResult<PyObject> {
        self.slice(&types::PySliceIndices::new(0, 16, 1))
    }
    pub fn extended_high(&self) -> PyResult<PyObject> {
        self.slice(&types::PySliceIndices::new(16, 32, 1))
    }
    pub fn get_byte(&self, byte_index: isize) -> PyResult<PyObject> {
        self.slice(&types::PySliceIndices::new(byte_index * 8, (byte_index + 1) * 8, 1))
    }

    pub fn append(&mut self, obj: &PyAny) -> PyResult<()> {

        if let Ok(bin) = obj.extract::<PyRef<Binary>>() { 
            self.inner.append_slice(&bin.inner.data);
        } else if let Ok(bin) = obj.extract::<bool>() { 
            self.inner.append_bit(bin);
        } else if let Ok( bin) = Self::from(obj, None, Some(self.sign_behavior())) {
            self.inner.append_slice(&bin.inner.data);
        } else {
            return Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", obj)));
        }
        Ok(())
    }
    pub fn prepend(&mut self, obj: &PyAny) -> PyResult<()> {

        if let Ok(bin) = obj.extract::<PyRef<Binary>>() { 
            self.inner.prepend_slice(&bin.inner.data);
        } else if let Ok(bin) = obj.extract::<bool>() { 
            self.inner.prepend_slice(&bv::BitVec::<u32>::new_fill(bin, 1));
        } else if let Ok( bin) = Self::from(obj, None, Some(self.sign_behavior())) {
            self.inner.prepend_slice(&bin.inner.data);
        } else {
            return Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", obj)));
        }
        Ok(())
    }

    pub fn hex(&self) -> String {
        self.inner.to_string_hex(true)
    }
    pub fn bin(&self) -> String {
        self.inner.to_string_bin(true)
    }
    pub fn int(&self) -> PyResult<PyObject> {
        let python_int: PyObject = Python::with_gil(|py| 0.into_py(py));

        Python::with_gil(|py| {
            python_int.call_method(py, "from_bytes", (self._data(), "little"), Some(vec![("signed", self.sign_behavior() == "signed")].into_py_dict(py)))
        }) // from_bytes(self._data, "big", {"signed": self.sign_behavior() == "signed"})
    }

    pub fn __int__(&self) -> PyResult<PyObject> {
        self.int()
    }
    pub fn __hex__(&self) -> String {
        self.hex()
    }
    pub fn __bin__(&self) -> String {
        self.bin()
    }

    pub fn __len__(&self) -> usize {
        self.len()
    }
    pub fn __repr__(&self) -> String {
        self.inner.to_string_formatted_default()
    }
    pub fn __str__(&self) -> String {
        self.inner.to_string_formatted_default()
    }
    pub fn __bool__(&self) -> bool {
        use binary::reduce::ReduceOps;
        self.inner.data.as_slice().any()
    }

    pub fn __add__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        arithm::add::wrapping_add(_self, other)
    }

    pub fn __sub__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        arithm::sub::wrapping_sub(_self, other)
    }

    pub fn __neg__(_self: PyRef<'_, Self>) -> PyResult<PyObject>{
        arithm::add::arithmetic_neg(_self)
    }
    pub fn __invert__(_self: PyRef<'_, Self>) -> PyResult<PyObject>{
        arithm::bitwise::bitwise_not(_self)
    }

    pub fn iter<'a>(self_: PyRef<'_, Self>, block_size: isize) -> PyResult<PyObject> 
    {
        Python::with_gil(|py| {
            let slf = unsafe { Py::from_borrowed_ptr(py, self_.into_ptr()) } ;
            let iter = BinaryIterator::new(slf, block_size)?;

            Ok(iter.into_py(py))
        })
    }
    
    pub fn bits<'a>(self_: PyRef<'_, Self>) -> PyResult<PyObject> 
    {
        Self::iter(self_, 1)
    }
    pub fn bytes<'a>(self_: PyRef<'_, Self>) -> PyResult<PyObject> 
    {
        Self::iter(self_, 8)
    }
    pub fn __iter__(self_: PyRef<'_, Self>) -> PyResult<PyObject> 
    {
        Self::bits(self_)
    }

    // Function ideas
    // - __add__
    // - __sub__
    // - bits()        - iterates over bits
    // - bytes()       - iterates over bytes
    // - high_byte     - returns the high byte of the binary
    // - low_byte      - returns the low byte of the binary
    // - extended_low  - returns the low 16bits of the binary
    // - extended_high - returns the high 16bits of the binary
    // - get_byte      - returns the byte at the given index
    // - get_bit       - returns the bit at the given index
    // - int()         - new name for as_int()
    // - hex()
    // - bin()
    // - __int__       - alias for int()
    // - __hex__       - alias for hex()
    // - __bin__       - alias for bin()
    // - __len__       - alias for len()
    // - 
    // - sign_behavior - returns the sign behavior of the binary
    // - maximal_value - returns the maximal value of the binary
    // - minimal_value - returns the minimal value of the binary
    // - leading_zeros - returns the number of leading zeros of the binary
    // - trailing_zeros - returns the number of trailing zeros of the binary
    // - is_negative - returns true if the binary is negative
    // - sign_extending_bit - returns bit that would be used for sign extending

    
    pub fn __richcmp__(&self, other: &PyAny, op: CompareOp) -> PyResult<bool> {
        let cmp = self.cmp(other)?;

        match op {
            CompareOp::Eq => Ok(cmp.is_eq()),
            CompareOp::Ne => Ok(cmp.is_ne()),
            CompareOp::Lt => Ok(cmp.is_lt()),
            CompareOp::Le => Ok(cmp.is_le()),
            CompareOp::Gt => Ok(cmp.is_gt()),
            CompareOp::Ge => Ok(cmp.is_ge()),
        }
    }
    pub fn __hash__(&self) -> PyResult<u64> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        let mut hasher = DefaultHasher::new();
        self.inner.data.as_slice().hash(&mut hasher);

        Ok(hasher.finish())
    }


    pub fn __getitem__(&self, index: &PyAny) -> PyResult<PyObject> {
        use binary::sliceunpack::PySliceUnpack;

        if let Ok(index) = index.extract::<isize>() {
            let bit = self.inner.get_bit(index)?;

            return Ok(Python::with_gil(|py| bit.into_py(py)));
        }

        if let Ok(slice) = index.extract::<&types::PySlice>() {
            return Ok(self.slice(&slice.unpack()?)?);
        }
        
        Err(exceptions::PyTypeError::new_err(format!("Invalid index type {}", index)))
    }
    pub fn __setitem__(&mut self, index: &PyAny, value: &PyAny) -> PyResult<()> {
        use binary::sliceunpack::PySliceUnpack;

        if let Ok(index) = index.extract::<isize>() {
            if let Ok(value) = value.extract::<bool>() {
                self.inner.set_bit(index, value)?;
                return Ok(());
            } else {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot be converted to bool", value)));
            }
        }

        if let Ok(slice) = index.extract::<&types::PySlice>() {
            let slice = &slice.unpack()?;
            let range = self.inner.slice_to_range(&slice)?;

            if let Ok(value) = value.extract::<bool>() {
                self.inner.set_slice_bool(slice, value)?;
            } else if let Ok(value) = Self::from(value, Some(range.len().try_into().unwrap()), Some("unsigned")) {
                self.inner.set_slice(slice, &value.inner.data)?;
            } else  {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot be used in range {:?}", value, range.range())));
            }
            
            return Ok(());
        }   

        return Err(exceptions::PyTypeError::new_err(format!("Invalid index type {}", index)));
    }
    
}


impl BinaryIterator {
    pub fn new(binary: Py<Binary>, chunk_size: isize) -> PyResult<Self> 
    {
        return Ok(Self {
            inner: binary,
            index: 0,
            chunk_size: chunk_size.try_into().unwrap()
        });
    }
}

#[pymethods]
impl BinaryIterator {
    fn __iter__(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            Ok(Self{
                index: 0,
                inner: self.inner.clone(),
                chunk_size: self.chunk_size,
            }.into_py(py))
        })
    }
    fn __next__(&mut self) -> PyResult<Option<PyObject>> {
        Python::with_gil(|py|{
            let inner = self.inner.borrow(py); 

            if self.index >= inner.len() {
                return Ok(None);
            }  
            let start = self.index.try_into().unwrap();
            let stop = (self.index + self.chunk_size).try_into().unwrap();

            let slice = inner.slice(&types::PySliceIndices::new(start, stop, 1))?;
            self.index += self.chunk_size;

            Ok(Some(slice))
        })   
    }
}

/// A Python module implemented in Rust.
#[pymodule]
fn pybytes(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Binary>()?;
    m.add_class::<BinaryIterator>()?;

    m.add_submodule(arithm::register_arithm_module(_py)?)?;

    Ok(())
}
