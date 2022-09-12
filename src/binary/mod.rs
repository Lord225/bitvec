pub mod reduce;
pub mod sliceunpack;

use std::mem::transmute;
use std::ops::Range;

use bv::{self, Bits, BitsPush, BitSlice, BitSliceable, BitsExt, BitSliceableMut, BitsMut };

use pyo3::{prelude::*, PyResult, types, exceptions};
use pyo3::types::IntoPyDict;

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
    step: u64,
}

impl BinaryRange
{
    pub fn new(start: u64, stop: u64, step: u64, len: u64) -> PyResult<BinaryRange> {
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
    pub fn range(&self) -> Range<u64> 
    {
        if self.get_start() >= self.get_wrapped_end() {
            self.get_wrapped_end()..self.get_wrapped_end()
        }
        else {
            self.range.clone()
        }
    }
    pub fn len(&self) -> u64 {
        (self.stop - self.range.start) / self.step
    }
    pub fn get_step(&self) -> u64 {
        self.step
    }
    pub fn get_wrapped_end(&self) -> u64 {
        self.range.end
    }
    pub fn get_real_end(&self) -> u64 {
        self.stop
    }
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
    pub fn to_string_symbols(&self, high: char, low: char) -> String
    {
        if self.data.is_empty() {
            return String::new();
        }
        
        let mut s = String::new();
        for i in 0..self.len()
        {
            s.push(if self.data.get_bit(self.len() - i - 1) { high } else { low });
        }
        s
    }

    pub fn to_string_symbols_rev(&self, high: char, low: char) -> String
    {
        let mut s = String::new();
        for i in 0..self.len()
        {
            s.push(if self.data.get_bit(i) { high } else { low });
        }
        s
    }

    pub fn to_string_hex(&self, prefix: bool) -> String
    {
        fn slice_to_u32(slice: &BitSlice<u32>) -> u32
        {
            let mut result = 0;
            for i in 0..slice.bit_len()
            {
                result |= (slice.get_bit(i) as u32) << i;
            }
            result
        }

        let mut output = String::with_capacity(self.len_usize()/4);
    

        for i in (0..self.len()).step_by(4)
        {
            let i = i.try_into().unwrap();

            let slice: BitSlice<u32> = if i+4 < self.len() { 
                self.data.bit_slice(i..(i+4)) 
            } else {
                self.data.bit_slice(i..self.len())    
            };

            output.push_str(&format!("{:x}", slice_to_u32(&slice)));
        }
        
        if prefix {
            format!("0x{}", &output.chars().rev().collect::<String>())
        } else {
            output.chars().rev().collect::<String>()
        }
        
    }

    pub fn to_string_formatted(&self, format: &[(usize, char)], high: char, low: char, prefix: bool) -> String
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

    pub fn to_string_bin(&self, prefix: bool) -> String
    {
        self.to_string_formatted(&[], '1', '0', prefix) 
    }

    pub fn to_string_formatted_default(&self) -> String
    {
        self.to_string_formatted(&[(8, ' ')], '1', '0', false)
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
        .map(|chunk| u32::from_str_radix(&chunk.iter().rev().collect::<String>(), radix.radix()).unwrap())
        .collect::<Vec<_>>();
        
        // create & fill vector
        let mut bitvec = bv::BitVec::<u32>::with_block_capacity(chunks.len());
        
        for chunk in chunks {
            bitvec.push_block(chunk);
        }

        let mut binary = Self { data: bitvec, sign_behavior: sign_behavior.unwrap_or("unsigned").to_string() };
        
        binary.resize_constrained(size)?;
        

        return Ok(binary);

    }

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

    pub fn parse_bitvec_from_long_integer(object: &types::PyLong, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let sign_behevior = sign_behavior.unwrap_or(if object.compare(0).is_ok_and(|x|x.is_lt()) { "signed" } else { "unsigned" });
        let bit_lenght = bit_size.unwrap_or(object.call_method0("bit_length")?.extract::<usize>()?);


        let mut bitvec = bv::BitVec::<u32>::with_capacity(bit_lenght.try_into().unwrap());

        let bytes = Python::with_gil(|py| {
            object.call_method("to_bytes", 
                ((bit_lenght.checked_next_multiple_of(32).unwrap())/8, "big"),     
              Some(vec![("signed", sign_behevior=="signed")].into_py_dict(py))
            )
        })?.extract::<&[u8]>()?;  // object.to_bytes(size, "big", signed=True)


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

    pub fn parse_bitvec_from_copy(object: &BinaryBase, bit_size: Option<usize>, sign_behavior: Option<&str>) -> PyResult<Self>
    {
        let bit_size = bit_size.unwrap_or(object.len_usize());
        let sign_behavior = sign_behavior.unwrap_or(&object.sign_behavior);
        

        let mut binary = Self { data: object.data.clone(), sign_behavior: sign_behavior.to_string() };
        
        binary.resize_trunc(bit_size);
        
        return Ok(binary);
    }

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

    fn flatten_index(&self, index: isize) -> usize
    {
        const INF_SYMBOL: isize = i64::MAX as _;

        match index
        {
            INF_SYMBOL => self.len_usize(), // default value, if index was provided as None in python
            0..               => index as usize,
            _                 => (self.len() as isize + index) as usize,
        }
    }

    pub fn slice_to_range(&self, slice: &types::PySliceIndices) -> PyResult<BinaryRange> {
        let start: u64 = self.flatten_index(slice.start).try_into().unwrap();
        let stop: u64  = self.flatten_index(slice.stop).try_into().unwrap();
        let step: u64  = slice.step.try_into().unwrap();

        BinaryRange::new(start, stop, step, self.len())
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
        let range = self.slice_to_range(slice)?;

        // get data from range
        let slice = self.data.bit_slice(range.range()).to_bit_vec();

        // get padding bits for slice outside t
        let padd = bv::BitVec::new_fill(self.sign_extending_bit(), (range.len() as i64 - slice.len() as i64).max(0) as u64);

        let concated = slice.bit_concat(padd).to_bit_vec();

        Ok(concated)
    }

    pub fn get_indices(&self, _slice: &types::PyIterator) -> PyResult<bv::BitVec<u32>> {
        todo!()
    }

    pub fn set_bit(&mut self, index: isize, value: bool) -> PyResult<()> {
        let index = self.in_bounds(self.flatten_index(index))?;
        self.data.set(index.try_into().unwrap(), value); 

        Ok(())
    }
    pub fn set_slice(&mut self, slice: &types::PySliceIndices, value: &bv::BitVec<u32>) -> PyResult<()> {
        let range = self.slice_to_range(slice)?;

        let mut slice = self.data.as_mut_slice().bit_slice_mut(range.range());

        if slice.len() > value.len() {
            return Err(exceptions::PyValueError::new_err(format!("Value and slice are in diffrent lenghts: {} > {}", slice.len(), value.len())));
        }

        for i in 0..slice.bit_len()
        {
            if i >= value.bit_len() {
                slice.set_bit(i, false);
            } else {
                slice.set_bit(i, value.get_bit(i));
            }
        }
        Ok(())
        
    }
    pub fn set_slice_bool(&mut self, slice: &types::PySliceIndices, value: bool) -> PyResult<()> {
        let range = self.slice_to_range(slice)?;

        let mut slice = self.data.as_mut_slice().bit_slice_mut(range.range());

        for i in 0..slice.bit_len()
        {
            slice.set_bit(i, value);
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

