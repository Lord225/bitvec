use std::cmp::Ordering;

use pyo3::basic::CompareOp;
use pyo3::{prelude::*, types, IntoPy};
use pyo3::exceptions;
use pyo3::types::IntoPyDict;

use bv::{self, Bits};

mod binary;
mod arithm;
mod cmp;
mod utility;

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
    extend: bool,
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
    fn parse_prefix_kwargs_args(args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> bool
    {
        match args.as_slice() {
            [value] if value.is_true().is_ok() => value.is_true().unwrap(),
            _                => kwargs.and_then(|kwargs| kwargs.get_item("prefix"))
                                      .and_then(|x| x.is_true().ok())
                                      .unwrap_or(true)
        }
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
    pub fn wrap_self(self) -> PyResult<PyObject> {
        Python::with_gil(|py| Ok(self.into_py(py)))
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
        // from bytes
        if let Ok(object) = object.extract::<&types::PyBytes>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_bytes(&object, bit_size, sign_behavior));
        }
        // from iterable
        if let Ok(object) = object.iter() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_iterable(object, bit_size, sign_behavior));
        }
        // from float
        if let Ok(object) = object.extract::<f64>() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_float(object, bit_size, sign_behavior));
        }
        if object.is_none() {
            return Self::wrap(binary::BinaryBase::parse_bitvec_from_isize(0, bit_size, sign_behavior));
        }
        
        return Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", object)));
    }

    fn slice(&self, slice: &types::PySliceIndices) -> PyResult<PyObject>
    {
        let slice = self.inner.get_slice(slice)?;

        return Self::wrap_object(binary::BinaryBase::parse_bitvec_from_slice(slice, None, None));
    }
    #[allow(unused)]
    fn from_parts(data: bv::BitVec::<u32>, sign: String) -> Self
    {
        Self::wrap(Ok(binary::BinaryBase {data, sign_behavior: sign})).unwrap()
    }
}

impl Binary
{
    fn cmp(&self, obj: &PyAny) -> PyResult<Ordering>
    {
        // prioritize:
        // 1 Casting to Binary
        // 2 Creating other with same Lenght as self
        // 3 Creating a new Binary without constrains
        if let Ok(bin) = obj.extract::<PyRef<Binary>>() { 
            cmp::cmp(&self, &bin)
        } else if let Ok( bin) = Self::from(obj, Some(self.len()), Some(self.sign_behavior())) {
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
    fn py_new(object: &PyAny, args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> PyResult<Self> 
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
            (None, None, Some(true)) => Some("signed"),
            (None, None, Some(false)) => Some("unsigned"),
            _ => {
                return Err(exceptions::PyTypeError::new_err(format!("Provided more than one sign_behavior")));
            }
        };

        // create the object
        Self::from(object, bit_size, sign_behavior)
    }

    #[getter]
    pub fn raw_bytes(&self) -> PyObject {
        data::<{u8::BITS}>(self)
    }

    #[getter]
    pub fn len(&self) -> usize {
        self.inner.len().try_into().unwrap()
    }
    #[getter]
    pub fn sb(&self) -> &String {
        &self.inner.sign_behavior
    }

    pub fn sign_behavior(&self) -> &String {
        self.sb()
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
    ///
    /// Calculated with python using equivalent code:
    /// ```python
    /// if self.sign_behavior() == "unsigned":
    ///     retrun 2**self.len() - 1
    /// else:
    ///     return 2**(self.len() - 1) - 1
    /// ```
    /// 
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
    /// 
    /// Calculated with python using equivalent code:
    /// ```python
    /// if self.sign_behavior() == "unsigned":
    ///    retrun 0
    /// else:
    ///   return -2**(self.len() - 1)
    /// 
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
    pub fn get_slice(&self, offset: isize, size: isize) -> PyResult<PyObject> {
        if offset >= 0  {
            self.slice(&types::PySliceIndices::new(offset, offset + size, 1))
        } else {
            let end = if offset + size >= 0 { self.len() as isize + offset + size } else { offset + size };
            self.slice(&types::PySliceIndices::new(offset, end, 1))
        }
    }

    pub fn append(&mut self, obj: &PyAny) -> PyResult<()> {
        // prioritize:
        // 1 Casting to Binary
        // 2 Casting to bool
        // 3 Creating a new Binary

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

    pub fn join(&self, obj: &PyAny) -> PyResult<PyObject> {
        Self::wrap_object(self.inner.join(obj))
    }

    /// Returns represenation in hex (with or without prefix depeding on args)
    /// `kwargs` -> prefix
    /// `args` -> 1st argument - boolean
    /// 
    #[args(args = "*", kwargs = "**")]
    pub fn hex(&self, args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> String {
        self.inner.to_string_hex(Self::parse_prefix_kwargs_args(args, kwargs))
    }
    /// Returns represenation in binary (with or without prefix depeding on args)
    /// `kwargs` -> prefix
    /// `args` -> 1st argument - boolean
    /// 
    #[args(args = "*", kwargs = "**")]
    pub fn bin(&self, args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> String {
        self.inner.to_string_bin(Self::parse_prefix_kwargs_args(args, kwargs))
    }
    /// Returns Python int
    /// Translates raw bytes into Python int
    pub fn int(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let python_int: PyObject = 0.into_py(py);
            
            python_int.call_method(py, "from_bytes", (data::<{u32::BITS}>(self), "little"), Some(vec![("signed", self.sign_behavior() == "signed")].into_py_dict(py)))
        }) // from_bytes(self._data, "big", {"signed": self.sign_behavior() == "signed"})
    }
    
    // Aliases

    pub fn __int__(&self) -> PyResult<PyObject> {
        self.int()
    }
    pub fn __hex__(&self) -> String {
        self.inner.to_string_hex(true)
    }
    pub fn __bin__(&self) -> String {
        self.inner.to_string_bin(true)
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
    pub fn __and__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        // prioritize:
        // 1 Casting to Binary
        // 2 Creating new Binary
        if let Ok(other) = other.extract::<PyRef<Binary>>() {
            arithm::bitwise::bitwise_and(_self, other)
        } else {
            Python::with_gil(|py| {
                let binary = Binary::from(other, None, Some(_self.sign_behavior()))?.into_py(py);
                let pyref = PyRef::extract(binary.as_ref(py))?;
            
                arithm::bitwise::bitwise_and(_self, pyref)
            })
        }
    }
    pub fn __or__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        if let Ok(other) = other.extract::<PyRef<Binary>>() {
            arithm::bitwise::bitwise_or(_self, other)
        } else {
            Python::with_gil(|py| {
                let binary = Binary::from(other, None, Some(_self.sign_behavior()))?.into_py(py);
                let pyref = PyRef::extract(binary.as_ref(py))?;
            
                arithm::bitwise::bitwise_or(_self, pyref)
            })
        }
    }
    pub fn __xor__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        if let Ok(other) = other.extract::<PyRef<Binary>>() {
            arithm::bitwise::bitwise_xor(_self, other)
        } else {
            Python::with_gil(|py| {
                let binary = Binary::from(other, None, Some(_self.sign_behavior()))?.into_py(py);
                let pyref = PyRef::extract(binary.as_ref(py))?;
            
                arithm::bitwise::bitwise_xor(_self, pyref)
            })
        }
    }
    pub fn __rshift__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        arithm::shifts::arithmetic_wrapping_rsh(&_self, other)?.wrap_self()
    }
    pub fn __lshift__(_self: PyRef<'_, Self>, other: &PyAny) -> PyResult<PyObject>{
        arithm::shifts::wrapping_lsh(&_self, other)?.wrap_self()
    }
    pub fn __neg__(_self: PyRef<'_, Self>) -> PyResult<PyObject>{
        arithm::add::arithmetic_neg(_self)
    }
    pub fn __invert__(_self: PyRef<'_, Self>) -> PyResult<PyObject>{
        arithm::bitwise::bitwise_not(_self)
    }

    #[args(kwargs = "**")] 
    pub fn iter<'a>(self_: PyRef<'_, Self>, block_size: isize,  kwargs: Option<&types::PyDict>) -> PyResult<PyObject> 
    {
        fn parse_kwargs(kwargs: Option<&types::PyDict>) -> bool {
            if let Some(kwargs) = kwargs {
                return kwargs.get_item("extend").and_then(|x| x.extract::<bool>().ok()).unwrap_or(true);
            }

            return true; // Default
        }
        Python::with_gil(|py| {
            let slf = unsafe { Py::from_borrowed_ptr(py, self_.into_ptr()) } ;
            let iter = BinaryIterator::new(slf, block_size, parse_kwargs(kwargs))?;

            Ok(iter.into_py(py))
        })
    }
    #[args(kwargs = "**")]    
    pub fn bytes<'a>(self_: PyRef<'_, Self>,  kwargs: Option<&types::PyDict>) -> PyResult<PyObject> 
    {
        Self::iter(self_, 8, kwargs)
    }
    pub fn bits<'a>(self_: PyRef<'_, Self>) -> PyResult<PyObject> 
    {
        Self::iter(self_, 1, None)
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

        // index
        if let Ok(index) = index.extract::<isize>() {
            let bit = self.inner.get_bit(index)?;
            return Ok(Python::with_gil(|py| bit.into_py(py)));
        }
        // slice
        if let Ok(slice) = index.extract::<&types::PySlice>() {
            return Ok(self.slice(&slice.unpack()?)?);
        }
        // indeces
        if let Ok(iterator) = index.iter() {
            return Self::wrap_object(Ok(binary::BinaryBase::from_data(self.inner.get_indices(iterator)?)));
        }
        
        Err(exceptions::PyTypeError::new_err(format!("Invalid index type {}", index)))
    }
    pub fn __setitem__(&mut self, index: &PyAny, value: &PyAny) -> PyResult<()> {
        use binary::sliceunpack::PySliceUnpack;

        // index
        if let Ok(index) = index.extract::<isize>() {
            if let Ok(value) = value.extract::<bool>() {
                self.inner.set_bit(index, value)?;
                return Ok(());
            } else {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot be converted to bool", value)));
            }
        }
        
        // slice
        if let Ok(slice) = index.extract::<&types::PySlice>() {
            let slice = &slice.unpack()?;
            let range = self.inner.slice_to_range(&slice)?;

            if let Ok(value) = value.extract::<bool>() {
                self.inner.set_slice_bool(slice, value)?;
            } else if let Ok(value) = Self::from(value, Some(range.len().try_into().unwrap()), Some("unsigned")) {
                self.inner.set_slice(slice, &value.inner)?;
            } else  {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot be used in range {:?}", value, range.range())));
            }
            
            return Ok(());
        }

        // indeces
        if let Ok(iterator) = index.iter() {
            if let Ok(value) = value.extract::<bool>() {
                self.inner.set_indices_bool(iterator, value)?;
            } else if let Ok(value) = Self::from(value, iterator.len().ok(), Some("unsigned")) {
                self.inner.set_indices_slice(iterator, &value.inner)?;
            } else  {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot be used with {}", value, index)));
            }
            return Ok(())
        }

        return Err(exceptions::PyTypeError::new_err(format!("Invalid index type {}", index)));
    }
    pub fn split_at(&self, idx: isize) -> PyResult<(PyObject, PyObject)>{
        let low = self.inner.get_slice(&types::PySliceIndices::new(0, idx, 1))?;
        let hig = self.inner.get_slice(&types::PySliceIndices::new(idx, self.len().try_into().unwrap(), 1))?;

        Ok((Self::wrap_object(Ok(binary::BinaryBase::from_data(low)))?, Self::wrap_object(Ok(binary::BinaryBase::from_data(hig)))?))
    } 

    // Utility
    pub fn find(&self, sub: &PyAny) -> PyResult<Option<usize>> {
        if let Ok(sub) = sub.extract::<PyRef<Binary>>() { 
            utility::find(&self, &sub)
        } else if let Ok(bin) = sub.extract::<bool>() { 
            if bin { 
                Ok(utility::find_one(&self)) 
            } else { 
                Ok(utility::find_zero(&self)) 
            }
        } else if let Ok( sub) = Self::from(sub, None, Some(self.sign_behavior())) {
            utility::find(&self, &sub)
        } else {
            Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", sub)))
        }
    } 
    pub fn find_all(&self, sub: &PyAny) -> PyResult<Vec<usize>> {
        if let Ok(sub) = sub.extract::<PyRef<Binary>>() { 
            utility::find_all(&self, &sub)
        } else if let Ok(bin) = sub.extract::<bool>() { 
            if bin { 
                Ok(utility::find_all_ones(&self))
            } else { 
                Ok(utility::find_all_zeros(&self))
            }
        } else if let Ok( sub) = Self::from(sub, None, Some(self.sign_behavior())) {
            utility::find_all(&self, &sub)
        } else {
            Err(exceptions::PyTypeError::new_err(format!("Unsupported type: {}", sub)))
        }
    }
    pub fn find_zeros(&self) -> PyResult<Vec<usize>>
    {
        Ok(utility::find_all_zeros(&self))
    }
    pub fn find_ones(&self) -> PyResult<Vec<usize>>
    {
        Ok(utility::find_all_ones(&self))
    }
    pub fn count_zeros(&self) -> PyResult<usize>
    {
        Ok(utility::count_zeros(&self))
    }
    pub fn count_ones(&self) -> PyResult<usize>
    {
        Ok(utility::count_ones(&self))
    }
    pub fn leading_zeros(&self) -> PyResult<usize>
    {
        Ok(utility::leading_zeros(&self))
    }
    pub fn trailing_zeros(&self) -> PyResult<usize>
    {
        Ok(utility::trailing_zeros(&self))
    }
    pub fn leading_ones(&self) -> PyResult<usize>
    {
        Ok(utility::leading_ones(&self))
    }
    pub fn trailing_ones(&self) -> PyResult<usize>
    {
        Ok(utility::trailing_ones(&self))
    }
}

fn next_multiple_of(num: usize, multiple: usize) -> usize {
    if num % multiple == 0 {
        num
    } else {
        num + multiple - num % multiple
    }
}
fn data<const SIZE: u32>(_self: &Binary) -> PyObject 
{
    // let size = _self.len().next_multiple_of(SIZE as usize);
    let size = next_multiple_of(_self.len(), SIZE as usize);
    
    let mut bytes  = _self.inner
        .get_slice(
            &types::PySliceIndices::new(0, 
                                        size as isize,
                                        1))
        .unwrap()
        .into_boxed_slice(); // for signed mask bitvec
    
        let (_, bytes, _) = unsafe { bytes.align_to_mut::<u8>() }; 

        Python::with_gil(|py| types::PyBytes::new(py, &bytes[..size/8]).to_object(py))
}


impl From<Binary> for PyObject {
    fn from(binary: Binary) -> PyObject {
        Binary::wrap_object(Ok(binary.inner)).unwrap()
    }
}

impl BinaryIterator {
    pub fn new(binary: Py<Binary>, chunk_size: isize, extend: bool) -> PyResult<Self> 
    {
        return Ok(Self {
            inner: binary,
            index: 0,
            chunk_size: chunk_size.try_into().unwrap(),
            extend: extend,
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
                extend: self.extend,
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

            let stop = if self.extend || self.index + self.chunk_size <= inner.len() {
                (self.index + self.chunk_size).try_into().unwrap()
            } else {
                inner.inner.len().try_into().unwrap()
            };

            let slice = inner.slice(&types::PySliceIndices::new(start, stop, 1))?;
            self.index += self.chunk_size;

            Ok(Some(slice))
        })   
    }
}

/// A Python module implemented in Rust.
#[pymodule()]
#[pyo3(name = "bitvec")]
fn pybytes(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Binary>()?;
    m.add_class::<BinaryIterator>()?;

    m.add_submodule(arithm::register_arithm_module(_py)?)?;

    Ok(())
}
