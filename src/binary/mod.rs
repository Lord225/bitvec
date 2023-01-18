pub mod reduce;
pub mod sliceunpack;

use std::mem::transmute;
use std::ops::Range;

use bv::{self, Bits, BitsPush, BitSliceable, BitsExt, BitSliceableMut, BitsMut };

use pyo3::{prelude::*, PyResult, types, exceptions};
use pyo3::types::{IntoPyDict, PySliceIndices};

use reduce::ReduceOps;

#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct BinaryBase {
    pub data: bv::BitVec::<u32>,
    pub sign_behavior: String,
}

/// ```txt
///  ************ *****
///      00000000 00000000
///  \   \             \___ range.start
///   \   \________________ range.end
///    \___________________ stop
/// ```
#[derive(Clone, PartialEq, Eq, Hash, Debug)]
pub struct BinaryRange {
    range: Range<u64>, // Range mapped onto the binary
    stop: u64,         // alternative to range.end, used for out-of-bounds indexing
    step: isize,         // step size
}

impl BinaryRange
{
    pub fn new(start: u64, stop: u64, step: isize, len: u64) -> PyResult<BinaryRange> {
        let wrapped_stop = stop.min(len);

        if stop < start {
            return Err(exceptions::PyValueError::new_err(format!("Stop index is smaller than start index: {} < {}", wrapped_stop, start)));
        }
        
        Ok(BinaryRange {
            range: start..wrapped_stop,
            stop,
            step,
        })
    }
    /// Returns the range for BitVec indexing. It will return `end..end` If slice is outside of the binary.
    pub fn range(&self) -> Range<u64> 
    {
        if self.get_start() >= self.get_wrapped_end() {
            self.get_wrapped_end()..self.get_wrapped_end()
        }
        else {
            self.range.clone()
        }
    }
    /// Real lenght of the slice
    pub fn len(&self) -> u64 {
        self.stop - self.range.start
    }
    /// Returns the step of the slice
    pub fn get_step(&self) -> isize {
        self.step
    }
    /// Returns the start of the slice
    pub fn get_wrapped_end(&self) -> u64 {
        self.range.end
    }
    /// Returns native end of the slice (not wrapped)
    pub fn get_real_end(&self) -> u64 {
        self.stop
    }
    /// Returns the start of the slice (not wrappend)
    pub fn get_start(&self) -> u64 {
        self.range.start
    }
}

impl BinaryBase {
    pub fn from_parts(data: bv::BitVec::<u32>, sign_behavior: String) -> Self {
        Self {
            data,
            sign_behavior,
        }
    }
    pub fn from_data(data: bv::BitVec::<u32>) -> Self {
        Self {
            data,
            sign_behavior: "unsigned".to_string(),
        }
    }
}

// TO_STRING
#[allow(dead_code)]
impl BinaryBase
{
    /// Returns a string representation of the binary. And uses `high` and `low` as symbols for bit states
    /// ```
    /// use bv::BitVec;
    /// let binary = BinaryBase::from_data(BitVec::from_bits(5)));
    /// assert_eq!(binary.to_string_symbols('1', '0'), "101".to_string());
    /// ```
    pub fn to_string_symbols(&self, high: u8, low: u8) -> String
    {
        use reduce::*;

        if self.data.is_empty() {
            return String::new();
        }
        
        let mut s = Vec::<u8>::with_capacity(self.data.len().try_into().unwrap());

        for bit in IterableBitSlice::new(&self.data.as_slice()).into_iter().rev()
        {
            if bit {
                s.push(high);
            }
            else {
                s.push(low);
            }
        }
        // safty: TODO: check if this is safe, bsc high and low are u8.
        unsafe { String::from_utf8_unchecked(s) }
    }
    /// Returns a string representation of the binary but bits are in reversed order. And uses `high` and `low` as symbols for bit states
    pub fn to_string_symbols_rev(&self, high: u8, low: u8) -> String
    {
        use reduce::*;

        if self.data.is_empty() {
            return String::new();
        }
        
        let mut s = Vec::<u8>::with_capacity(self.data.len().try_into().unwrap());
        for bit in IterableBitSlice::new(&self.data).into_iter()
        {
            if bit {
                s.push(high);
            }
            else {
                s.push(low);
            }
        }
        // safty: TODO: check if this is safe, bsc high and low are u8.
        unsafe { String::from_utf8_unchecked(s) }
    }
    /// Returns a string representation of the binary in hex. Pads ramaining bits with zeros. if `prefix` is true adds `0x`
    pub fn to_string_hex(&self, prefix: bool) -> String
    {
        #[inline(always)]
        fn to_hex(n: u32) -> [u8; 8]
        {
            let mut chars = [0 as u8; 8];
            
            for i in 0..8
            {
                let chunk = n.get_bits(4*i as u64, 4);
                chars[i] = match chunk {
                    0 => '0',
                    1 => '1',
                    2 => '2',
                    3 => '3',
                    4 => '4',
                    5 => '5',
                    6 => '6',
                    7 => '7',
                    8 => '8',
                    9 => '9',
                    10 => 'a',
                    11 => 'b',
                    12 => 'c',
                    13 => 'd',
                    14 => 'e',
                    15 => 'f',
                    _ => unreachable!("Invalid Chunk Value"),
                } as u8;
            }
            chars
        }

        #[inline(always)]
        fn push_n(str: &mut Vec<u8>, chars: [u8; 8], n: usize)
        {
            for i in (0..n).rev()
            {
                str.push(chars[i]);
            }
        }

        #[inline(always)]
        fn push_all(str: &mut Vec<u8>, chars: [u8; 8])
        {
            for ch in chars
            {
                str.push(ch);
            }
        }

        fn div_ceil(a: usize, b: usize) -> usize
        {
            (a + b - 1) / b
        }

        let mut output = Vec::with_capacity(self.len_usize()/4);
        let data = &self.data;
        let last_block = data.block_len()-1;
        
        if data.block_len() != 0 
        {
            let bits_in_last_block = div_ceil(self.len_usize() % 32, 4);
            let block = data.get_block(last_block);
            
            if bits_in_last_block != 0 {
                push_n(&mut output, to_hex(block), bits_in_last_block);
            } else {
                push_all(&mut output, to_hex(block));
            }

            for i in (0..last_block).rev()
            {
                let block = data.get_raw_block(i);
                push_all(&mut output, to_hex(block));
            }
        }

        let output = unsafe{ String::from_utf8_unchecked(output) };
        
        if prefix {
            format!("0x{}", &output)
        } else {
            output
        }
        
    }

    /// Returns a string representation of the binary in hex. Pads ramaining bits with zeros. if `prefix` is true adds `0x`
    /// Uses `format` to pad bits in specified pattern. 
    /// Function while iterating over bits will add coresponding character from `format.1` to the output string after every `format.0` 
    /// bits and for next chunk it will use next item in collection
    /// Example
    /// ```rs
    /// &[(2, '\''), (2, ' ')]
    /// ```
    /// With input string `1111000011110000` will produce `1111'0000 1111'0000`
    pub fn to_string_formatted(&self, format: &[(usize, char)], high: u8, low: u8, prefix: bool) -> String
    {
        // format: "4'4 "
        // output:
        // 0000'0000 0000'0000 
        let mut output = String::with_capacity(self.len_usize());
        
        if format.len() == 0 {
            if prefix {
                return format!("0b{}", &self.to_string_symbols(high, low))
            } else {
                return self.to_string_symbols(high, low)
            }
        }

        let mut i = 0;
        let mut index = 0;
        for ch in self.to_string_symbols_rev(high, low).chars() {
            output.push(ch);
            i += 1;
            if i == format[index].0 {
                output.push(format[index].1);
                i = 0;
                index = (index+1)%format.len();
            }
        }

        let output_trimed = output.trim_end_matches(format[index].1);

        if prefix {
            format!("0b{}", &output_trimed.chars().rev().collect::<String>())
        } else {
            output_trimed.chars().rev().collect::<String>()
        }

    }

    /// Returns a string representation of the binary Using `1` to represend high state and `0` to represent low state, will not add any formatting
    pub fn to_string_bin(&self, prefix: bool) -> String
    {
        self.to_string_formatted(&[], '1' as u8, '0' as u8, prefix) 
    }

    /// Returns a string representation of the binary Using `1` to represend high state and `0` to represent low state, will add spaces every 8th bit.
    pub fn to_string_formatted_default(&self) -> String
    {
        self.to_string_formatted(&[(8, ' ')], '1' as u8, '0' as u8, false)
    }
}

// UTILITY
impl BinaryBase
{
    pub fn sign_bit(&self) -> bool
    {
        if self.data.len() == 0 {
            false
        } else {
            self.data.get_bit(self.data.len() - 1) 
        }
    }
    pub fn sign_extending_bit(&self) -> bool
    {
        if self.sign_behavior == "signed" { self.sign_bit() } else { false }
    }
}

// Object Construction
impl BinaryBase {
    fn check_for_size(&self, range: u64) -> PyResult<()>
    {
        fn check_unsigned(data: &bv::BitVec<u32>, range: u64) -> bool
        {
            data.bit_slice(range..).any()
        }

        fn check_signed(data: &bv::BitVec<u32>, range: u64) -> bool
        {
            if range == 0 {
                return data.bit_slice(..).any();
            }

            let sign_bit = data.get_bit(range-1);

            if sign_bit {
                !(data.bit_slice(range..).all() || data.bit_slice(range..).none())
            } else {
                data.bit_slice(range..).any()
            }
        }

        // 1
        if range <= self.data.len()
        {
            if (self.sign_behavior == "unsigned" && check_unsigned(&self.data, range)) || 
               (self.sign_behavior == "signed"   && check_signed(&self.data, range))
            {
                return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot fit in {} bits", self.to_string_formatted_default(), range)));
            }
        }

        Ok(())
    }

    fn resize_constrained(&mut self, new_size: usize) -> PyResult<()>
    {
        let new_size = new_size as u64;

        self.check_for_size(new_size)?;

        self.data.truncate(new_size);
        
        self.data.resize(new_size, self.sign_extending_bit());

        Ok(())
    }
    
    fn resize_trunc(&mut self, new_size: usize)
    {
        let new_size = new_size as u64;

        self.data.truncate(new_size);
        self.data.resize(new_size, self.sign_extending_bit());

    }

    /// Crate a new BinaryBase object with specified size and sign behavior based on &str input (hex or bin representaion of the number)
    /// trailing `0x` or `0b` will be ignored, trailing `0` will be used to determine `bit_size` if not provided. Characters `\t`, `\n`, ` ` will be ignored in input string and not counted towards `bit_size`
    /// 
    /// It can fail if:
    /// * `bit_size` is provided and input value cannot fit in specified size
    /// * String has invalid characters or radix
    pub fn parse_bitvec_from_str(object: &str, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        enum Prefix {
            Bin,
            Hex,
        }

        impl Prefix {
            fn max_size_for_u32(&self) -> usize
            {
                match self {
                    Prefix::Bin => 32/1,
                    Prefix::Hex => 32/4,
                }
            }
            fn radix(&self) -> u32 
            {
                match self {
                    Prefix::Bin => 2,
                    Prefix::Hex => 16,
                }
            }
            fn calculate_size_from_str(&self, src: &String) -> usize
            {
                match self {
                    Prefix::Bin => src.len()*1,
                    Prefix::Hex => src.len()*4,
                }
            }
        }

        fn get_radix_from_str(src: &str) -> PyResult<Prefix>
        {
            const HEX_CHARS: &str = "23456789abcdef";
            
            if src.to_ascii_lowercase().chars().map(|ch| ch).any(|ch| HEX_CHARS.find(ch).is_some()) {
                Ok(Prefix::Hex)
            } else  {
                Ok(Prefix::Bin)
            }
        }

        // get & strip prefix
        let (radix, object) = match object {
            _ if object.starts_with("0b") => (Prefix::Bin, object.trim_start_matches("0b")),
            _ if object.starts_with("0x") => (Prefix::Hex, object.trim_start_matches("0x")),
            _ => (get_radix_from_str(&object)?, object),
        };

        // remove all whitespaces & calculate actual size
        let object = object.replace(" ", "").replace("\t", "").replace("\n", "");
        let size = bit_size.unwrap_or(radix.calculate_size_from_str(&object));
        

        // collect characters into blocks
        let chunks = object
        .chars()
        .rev()
        .collect::<Vec<char>>()
        .chunks(radix.max_size_for_u32())
        .map(|chunk| u32::from_str_radix(&chunk.iter().rev().collect::<String>(), radix.radix()))
        .collect::<Result<Vec<_>, _>>()?;
        
        // create & fill vector
        let mut bitvec = bv::BitVec::<u32>::with_block_capacity(chunks.len());
        
        for chunk in chunks {
            bitvec.push_block(chunk);
        }

        let mut binary = Self { data: bitvec, sign_behavior: sign_behavior.unwrap_or("unsigned").to_string() };
        
        binary.resize_constrained(size)?;
        

        return Ok(binary);

    }

    /// Crate a new BinaryBase object with specified size and sign behavior based on integer input.
    /// If `bit_size` is not provided, the smallest possible size will be used for giver signedness. (e.g. 0 will be 0 bit, 1 will be 1 bit, -1 will be 1 bits)
    /// If `sign_behavior` is not provided it will be based on the sign of the input.
    /// 
    /// It can fail if:
    /// * `bit_size` is provided and input value cannot fit in specified size
    pub fn parse_bitvec_from_isize(object: isize, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let sign_behevior = sign_behavior.unwrap_or(if object.is_negative() { "signed" } else { "unsigned"});

        // beautiful match                                  __ chad edge case handling
        let bit_size_from_obj = match object { //   /                                     ____________________ counting leading_zeros in unsigned values
                                        0 /*______________/           */ => 0,           //     /
                                        isize::MIN  /* __/            */ => isize::BITS, //    / 
                                        (1..) if sign_behevior!="signed" => isize::BITS - object.leading_zeros(),
                                        (1..) if sign_behevior=="signed" => isize::BITS - object.leading_zeros() + 1, // <---- extra space for sign bit
                                        _                                => isize::BITS - object.abs().leading_zeros() + if object.unsigned_abs().is_power_of_two() { 0 } else { 1 },
                                       }.try_into().unwrap();  //                                                        \
                                                               //                                                         \_______ correcion for negative values that can fit in less bits
                                                               //                                                                  negative powers of two requires less bits than others
        let bit_lenght = bit_size.unwrap_or(bit_size_from_obj);
 
                
        // safty: isize -> usize have same size and all values of usize are valid in isize
        let transmutated = unsafe { transmute::<_, usize>(object) };
        
        let mut bitvec = bv::BitVec::<u32>::with_block_capacity((isize::BITS/u32::BITS).try_into().unwrap());
        bitvec.push_block(transmutated as u32);         // lower half
        bitvec.push_block((transmutated >> 32) as u32); // higer half (if usize is 64 bits, otherwise 0 is pushed so it has no effect on the result)

        let mut binary = Self { data: bitvec, sign_behavior: sign_behevior.to_string() };
        
        if bit_lenght < bit_size_from_obj{
            return Err(exceptions::PyTypeError::new_err(format!("Value {} cannot fit in {} bits", binary.to_string_formatted_default(), bit_lenght))); 
        }

        binary.resize_constrained(bit_lenght)?;

        return Ok(binary);
    }
    
    /// Crate a new BinaryBase object with specified size and sign behavior based on Python integer input. It behaves the same as `parse_bitvec_from_isize` but it accepts Arbitrary Sized Integers.
    /// ```py
    /// raw_bytes = object.to_bytes(size, "big", signed=True) # where size is the number of bytes in blocks that will be used (next multiple of 32) // 8) 
    /// ```
    /// It can fail if:
    /// * `bit_size` is provided and input value cannot fit in specified size
    /// * If python fails to call `bit_lenght` or `to_bytes` functions on integer
    /// * If pyo3 fails to convert python `bytes` to `&[u8]
    /// * If python has diffrent alighment for bytes than rust (unlikely)
    pub fn parse_bitvec_from_long_integer(object: &types::PyLong, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        fn checked_next_multiple_of(n: usize, multiple: usize) -> Option<usize> {
            let rem = n % multiple;
            if rem == 0 {
                Some(n)
            } else {
                n.checked_add(multiple - rem)
            }
        }

        let sign_behevior = sign_behavior.unwrap_or(if object.compare(0i64).and_then(|x| Ok(x.is_lt())).unwrap_or(false) { "signed" } else { "unsigned" });

        let bit_lenght = bit_size.unwrap_or(object.call_method0("bit_length")?.extract::<usize>()?);

        let mut bitvec = bv::BitVec::<u32>::with_capacity(bit_lenght.try_into().unwrap());

        let (bytes, bit_lenght) = Python::with_gil(|py| {
            //try calling object.to_bytes(size, "big", signed=True) if it failes (for negative powers of two) call same function but add one bit.
            if let Ok(bytes) = object.call_method(
                                          "to_bytes", 
                                          (checked_next_multiple_of(bit_lenght, 32).ok_or(exceptions::PyOverflowError::new_err("lenght overflowed"))?/8, "big"),
                                        Some(vec![("signed", sign_behevior=="signed")].into_py_dict(py))) {
                PyResult::Ok((bytes, bit_lenght))
            } else {
                let bytes = object.call_method(
                                   "to_bytes", 
                                   (checked_next_multiple_of(bit_lenght+1, 32).ok_or(exceptions::PyOverflowError::new_err("lenght overflowed"))?/8, "big"),     
                                 Some(vec![("signed", sign_behevior=="signed")].into_py_dict(py)))?;
                PyResult::Ok((bytes,  bit_lenght+1))
            }
        })?;

        
        let bytes = bytes.extract::<&[u8]>()?;

        // align and reverse bits in way that bv can handle safty: bytes.len() is multiple of 32/8=4 and transutating [u8; 4] to u32 is safe bsc all values of [u8; 4] are in range of u32 
        let bytes = bytes.iter().map(|x| x.reverse_bits()).collect::<Vec<u8>>();
        let (prefix, number, suffix) = unsafe { bytes.align_to::<u32>() };
        if prefix.len() != 0 || suffix.len() != 0 {
            return Err(exceptions::PyTypeError::new_err(format!("Unexpected aligment error for integer: {}", object)));
        }

        // push blocks in reverse order to get correct order in bitvec
        for block in number.iter().rev() {
            bitvec.push_block(block.reverse_bits());
        }
        let mut binary = Self { data: bitvec, sign_behavior: sign_behevior.to_string() };
        
        binary.resize_constrained(bit_lenght)?;

        return Ok(binary);
    }

    pub fn parse_bitvec_from_float(object: f64, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        Self::parse_bitvec_from_isize(object as isize, bit_size, sign_behavior)
    }

    /// Copy constructor
    pub fn parse_bitvec_from_copy(object: &BinaryBase, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let bit_size = bit_size.unwrap_or(object.len_usize());
        let sign_behavior = sign_behavior.unwrap_or(&object.sign_behavior);

        let mut binary = Self { data: object.data.clone(), sign_behavior: sign_behavior.to_string() };
        
        binary.resize_trunc(bit_size);
        
        return Ok(binary);
    }

    /// Takes raw bytes and uses them as bitvec data
    /// 
    pub fn parse_bitvec_from_bytes(object: &types::PyBytes, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let bit_size = bit_size.unwrap_or(object.len()?*8);
        let sign_behavior = sign_behavior.unwrap_or("unsigned");
        let mut data = bv::BitVec::<u32>::with_capacity(bit_size.try_into().unwrap());

        for byte in object.as_bytes().iter() {
            for bit in 0..8 {
                data.push((byte >> bit) & 1 == 1); // Mask bit & push to bitvec
            }
        }

        
        let mut binary = Self { data: data, sign_behavior: sign_behavior.to_string() };
        
        binary.resize_constrained(bit_size)?;
        
        return Ok(binary);
    }

    /// Takes Python Iterator and uses it as bitvec data
    /// 
    pub fn parse_bitvec_from_iterable(mut object: &types::PyIterator, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let sign_behavior = sign_behavior.unwrap_or("unsigned");
        
        let mut bitvec = bv::BitVec::<u32>::with_block_capacity(1);
        while let Some(next_item) = object.next() {
            let item = next_item?.is_true().unwrap_or(false); // if it fails here it means that exeption was raised in iterator.next() other than StopIteration
            bitvec.push_bit(item);
        }
        
        let mut bitvec_reverse = bv::BitVec::<u32>::with_block_capacity(bitvec.block_capacity());
        while let Some(bit) = bitvec.pop_bit()
        {
            bitvec_reverse.push_bit(bit);
        }
        
        let mut binary = Self { data: bitvec_reverse, sign_behavior: sign_behavior.to_string() };
        
        binary.resize_constrained(bit_size.unwrap_or(binary.len_usize()))?;

        return Ok(binary);
    }

    /// Constructior that wraps raw `BitVec` inside `BinaryBase`
    pub fn parse_bitvec_from_slice(object: bv::BitVec<u32>, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self> 
    {
        let sign_behavior = sign_behavior.unwrap_or("unsigned");
        let mut binary = Self { data: object, sign_behavior: sign_behavior.to_string() };
        
        binary.resize_constrained(bit_size.unwrap_or(binary.len_usize()))?;
        
        return Ok(binary);
    }

}


// indexing
impl BinaryBase
{ 
    fn in_bounds(&self, index: usize) -> PyResult<usize>
    {
        if index >= self.len_usize() {
            return Err(exceptions::PyIndexError::new_err(format!("Index out of range: {}", index)));
        }
        return Ok(index);
    }

    /// Flattening uses special value `i64::MAX` to represent `None` provied value in python (so it is assumed to be last index)
    fn flatten_index(&self, index: isize) -> usize
    {
        const INF_SYMBOL_HIG_BOUND: isize = i64::MAX as _;
        const INF_SYMBOL_LOW_BOUND: isize = i64::MIN as _;

        match index
        {
            INF_SYMBOL_HIG_BOUND => self.len_usize(), // default value, if index was provided as None in python
            INF_SYMBOL_LOW_BOUND => 0,                // If Python decided to use i64::MIN as None in lower bound of slice
            0..               => index as usize,
            _                 => (self.len() as isize + index) as usize,
        }
    }

    pub fn slice_to_range(&self, slice: &types::PySliceIndices) -> PyResult<BinaryRange> {
        let start: u64 = self.flatten_index(slice.start).try_into().unwrap();
        let stop: u64  = self.flatten_index(slice.stop).try_into().unwrap();
        let step       = slice.step;

        if step == 0 {
            return Err(exceptions::PyIndexError::new_err("Slice step cannot be zero"));
        }

        // Handle this stupid python's edge case where for negative step
        if step < 0 {
            BinaryRange::new(stop, start, step, self.len())
        } else{
            BinaryRange::new(start, stop, step, self.len())
        }
    }

    pub fn get_bit(&self, index: isize) -> PyResult<bool> {
        let index = self.flatten_index(index);

        if let Ok(_) = self.in_bounds(index) {
            return Ok(self.data.get_bit(index.try_into().unwrap()));
        } else {
            return Ok(self.sign_extending_bit())
        }
    }
    
    pub fn get_slice(&self, slice: &types::PySliceIndices) -> PyResult<bv::BitVec<u32>> {
        use reduce::*;

        let range = self.slice_to_range(slice)?;

        // get data from range
        let slice = self.data.bit_slice(range.range());

        // get padding bits for slice outside t
        let lenght = (range.len() as i64 - slice.len() as i64).max(0) as u64;
        let padd = bv::BitVec::new_fill(self.sign_extending_bit(), lenght);
        let concated = slice.bit_concat(padd);

        let quick_reverse = |vec: bv::BitVec<u32>| {
            let vector_lenght = vec.bit_len();
            let blocks = vec.into_boxed_slice();
            
            let mut reversed = bv::BitVec::with_block_capacity(blocks.len());
            for block in blocks.iter().rev() {
                reversed.push_block(block.reverse_bits());
            }
            if vector_lenght % u32::BITS as u64 == 0 {
                reversed
            } else {
                let rem_bits = u32::BITS as u64 - vector_lenght % u32::BITS as u64;
                BinaryBase::from_data(reversed).get_slice(&PySliceIndices::new(rem_bits.try_into().unwrap(), isize::MAX, 1)).unwrap()
            }
        };
    
        let out = match range.step {
            0   => Err(exceptions::PyIndexError::new_err(format!("Step cannot be zero"))),
            1   => Ok(concated.to_bit_vec()), // specialization for most common case
            -1  => Ok(quick_reverse(concated.to_bit_vec())), // specialization for common case (reversing with ::-1)
            0.. => {
                let mut out = bv::BitVec::<u32>::with_capacity(concated.bit_len()/range.step as u64);
                for bit in IterableBitSlice::new(&concated).into_iter().step_by(range.step.try_into().unwrap()) {
                    out.push(bit);
                }
                Ok(out)
            },
            _ => {
                let mut out = bv::BitVec::<u32>::with_capacity(concated.bit_len()/range.step as u64);
                for bit in IterableBitSlice::new(&concated).into_iter().rev().step_by(range.step.abs().try_into().unwrap()) {
                    out.push(bit);
                }
                Ok(out)
            }  
        }?;

        Ok(out)
    }

    pub fn get_indices(&self, _slice: &types::PyIterator) -> PyResult<bv::BitVec<u32>> {
        let mut out = bv::BitVec::<u32>::with_capacity(1);

        for index in _slice {
            let index = index?.extract::<isize>()?;
            let index = self.flatten_index(index);
            if let Ok(index) = self.in_bounds(index) {
                out.push_bit(self.data.get_bit(index.try_into().unwrap()));
            } else {
                out.push_bit(self.sign_extending_bit());
            }
        }
        return Ok(out);
    }

    pub fn set_bit(&mut self, index: isize, value: bool) -> PyResult<()> {
        let index = self.in_bounds(self.flatten_index(index))?;
        self.data.set(index.try_into().unwrap(), value); 

        Ok(())
    }
    pub fn set_slice(&mut self, slice: &types::PySliceIndices, value: &BinaryBase) -> PyResult<()> {
        let range = self.slice_to_range(slice)?;

        let mut slice = self.data.as_mut_slice().bit_slice_mut(range.range());

        if slice.len() > value.len() {
            return Err(exceptions::PyValueError::new_err(format!("Value and slice are in diffrent lenghts: {} > {}", slice.len(), value.len())));
        }

        if range.step > 0 
        {
            for (index, i) in (0..slice.bit_len()).step_by(range.step as _).enumerate()
            {
                slice.set_bit(i, value.get_bit(index.try_into().unwrap())?);
            }
        } 
        else 
        {
            for (index, i) in (0..slice.bit_len()).rev().step_by(range.step.abs() as _).enumerate()
            {
                slice.set_bit(i, value.get_bit(index.try_into().unwrap())?);   
            }
        }
        Ok(())
        
    }
    pub fn set_slice_bool(&mut self, slice: &types::PySliceIndices, value: bool) -> PyResult<()> {
        let range = self.slice_to_range(slice)?;

        let mut slice = self.data.as_mut_slice().bit_slice_mut(range.range());

        if range.step > 0 
        {
            for i in (0..slice.bit_len()).step_by(range.step as _)
            {
                slice.set_bit(i, value);
            }
        } 
        else 
        {
            for i in (0..slice.bit_len()).rev().step_by(range.step.abs() as _)
            {
                slice.set_bit(i, value);
            }
        }

        Ok(())
    }
    pub fn set_indices_slice(&mut self, _slice: &types::PyIterator, value: &BinaryBase) -> PyResult<()> {
        for (index, i) in _slice.enumerate() {
            let i = i?.extract::<isize>()?;
            let i = self.flatten_index(i);
            
            self.in_bounds(i)?;
            
            self.data.set(i.try_into().unwrap(), value.get_bit(index.try_into().unwrap())?);
        }
        Ok(())
    }
    pub fn set_indices_bool(&mut self, _slice: &types::PyIterator, value: bool) -> PyResult<()> {
        for i in _slice {
            let i = i?.extract::<isize>()?;
            let i = self.flatten_index(i);
            
            self.in_bounds(i)?;

            self.data.set(i.try_into().unwrap(), value);

        }
        Ok(())
    }

    pub fn len(&self) -> u64 {
        return self.data.bit_len();
    }
    pub fn len_usize(&self) -> usize {
        return self.data.bit_len().try_into().unwrap();
    }
    pub fn append_bit(&mut self, val: bool) 
    {
        self.data.push_bit(val);
    }
    pub fn append_slice(&mut self, val: &bv::BitVec<u32>) 
    {
        // brefly benchmarked: 
        // 0.3181476593017578s
        //self.data = self.data.bit_concat(val).to_bit_vec();
        
        // 0.005983591079711914s
        for i in 0..val.bit_len()
        {
            self.data.push_bit(val.get_bit(i));
        }
    }
    pub fn prepend_slice(&mut self, val: &bv::BitVec<u32>) 
    {
        self.data = val.bit_concat(&self.data).to_bit_vec();
    }

    pub fn join(&self, val: &PyAny) -> PyResult<BinaryBase> {
        use super::arithm::concat::append_any;
        let joiner = &self.data;
        
        let mut output = BinaryBase::from_data(bv::BitVec::new());
        if let Some((last, collection)) = val.iter()?.into_iter().collect::<PyResult<Vec<_>>>()?.split_last() 
        {
            for values in collection 
            {
                append_any(&mut output, values)?;
                output.append_slice(joiner);
            }
            append_any(&mut output, last)?;
        }
        Ok(output)
    }
}

impl From<&BinaryBase> for i64 {
    fn from(_self: &BinaryBase) -> Self {
        let slice = _self.get_slice(&types::PySliceIndices::new(0, 64, 1)).unwrap().into_boxed_slice();
        
        assert_eq!(slice.len(), 2);

        let (lo, slice, hi) = unsafe { slice.align_to::<i64>() };

        assert!(lo.is_empty() && hi.is_empty() && slice.len() == 1);

        return slice[0];
    }
}

