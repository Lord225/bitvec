use bv::BitSliceable;
use pyo3::{prelude::*, exceptions};

//trailing_zeros
//leading_zeros
//trailing_ones
//leading_ones
//count_ones
//count_zeros   
//find
//find_all


pub fn trailing_zeros(binary: &crate::Binary) -> usize
{
    find_one(binary).and_then(|count| Some(count)).unwrap_or(binary.len())
}

pub fn leading_zeros(binary: &crate::Binary) -> usize
{
    find_one_rev(binary).and_then(|count| Some(count)).unwrap_or(binary.len())
}

pub fn trailing_ones(binary: &crate::Binary) -> usize
{
    find_zero(binary).and_then(|count| Some(count)).unwrap_or(binary.len())
}

pub fn leading_ones(binary: &crate::Binary) -> usize
{
    find_zero_rev(binary).and_then(|count| Some(count)).unwrap_or(binary.len())
}   

pub fn count_ones(binary: &crate::Binary) -> usize
{
    use bv::Bits;

    let data = &binary.inner.data;
    let mut total = 0;
    for block_id in 0..data.block_len() {
        let block = data.get_block(block_id);
        total += block.count_ones() as usize;
    }


    return total;
}

pub fn count_zeros(binary: &crate::Binary) -> usize
{
    use bv::Bits;

    let data = &binary.inner.data;
    let mut total = 0;
    for block_id in 0..(data.block_len()-1) {
        let block = data.get_block(block_id);
        total += block.count_zeros() as usize;
    }

    let block = data.get_block(data.block_len()-1); 

    let last_block_bits = data.len() as u32 % u32::BITS as u32;
    let mask = !((1 << last_block_bits) - 1);
    total += (block | mask).count_zeros() as usize;

    return total;
}

struct Windows<'a> {
    slice: bv::BitSlice<'a, u32>,
    width: u64,
}
impl<'a> std::iter::Iterator for Windows<'a> {
    type Item = bv::BitSlice<'a, u32>;

    fn next(&mut self) -> Option<Self::Item> {
        if self.slice.len() < self.width {
            return None;
        }
        let slice = self.slice.bit_slice(..self.width);
        self.slice = self.slice.bit_slice(1..);
        Some(slice)
    }
}

pub fn find_one_rev(binary: &crate::Binary) -> Option<usize> {
    use super::binary::reduce::*;

    IterableBitSlice(&binary.inner.data).into_iter().rev().position(|bit| bit)
}
pub fn find_zero_rev(binary: &crate::Binary) -> Option<usize> {
    use super::binary::reduce::*;

    IterableBitSlice(&binary.inner.data).into_iter().rev().position(|bit| !bit)
}


pub fn find_one(binary: &crate::Binary) -> Option<usize> {
    use bv::Bits;

    let data = &binary.inner.data;

    for block_id in 0..data.block_len() {
        let block = data.get_block(block_id);
        if block != 0 {
            let offset = block.trailing_zeros() as usize;
            return Some(block_id * 32 + offset);
        }
    }
    None
}
pub fn find_zero(binary: &crate::Binary) -> Option<usize> {
    use bv::Bits;

    let data = &binary.inner.data;

    for block_id in 0..data.block_len() {
        let block = data.get_block(block_id);
        if block != u32::MAX {
            let offset = block.trailing_ones() as usize;
            return Some(block_id * 32 + offset);
        }
    }
    None
}

pub fn find(binary: &crate::Binary, sub: &crate::Binary) -> PyResult<Option<usize>>
{
    let slice = binary.inner.data.as_slice();
    let sub = &sub.inner.data;

    match sub.len() {
        0 => Err(exceptions::PyValueError::new_err("Pattern is empty")),
        1 =>   // Specialization for single bit
            if sub[0] {
                Ok(find_one(binary))
            } else {
                Ok(find_zero(binary))
            }
        _ => {
            Ok(
                Windows { slice: slice, width: sub.len() }
                .enumerate()
                .filter(|(_, window)| window == sub)
                .map(|(i, _)| i)
                .next()
            )
        }
    }
}

pub fn find_all_ones(binary: &crate::Binary) -> Vec<usize> {
    use super::binary::reduce::*;

    IterableBitSlice(&binary.inner.data).into_iter().enumerate().filter(|(_, x)| *x).map(|(i, _)| i).collect()
}
pub fn find_all_zeros(binary: &crate::Binary) -> Vec<usize> {
    use super::binary::reduce::*;

    IterableBitSlice(&binary.inner.data).into_iter().enumerate().filter(|(_, x)| !*x).map(|(i, _)| i).collect()
}

pub fn find_all(binary: &crate::Binary, sub: &crate::Binary) -> PyResult<Vec<usize>>
{
    let slice = binary.inner.data.as_slice();
    let sub = &sub.inner.data;

    match sub.len() {
        0 => Err(exceptions::PyValueError::new_err("Pattern is empty")),
        1 =>   // Specialization for single bit
            if sub[0] {
                Ok(find_all_ones(binary))
            } else {
                Ok(find_all_zeros(binary))
            }
        _ => {
            Ok(
                Windows { slice: slice, width: sub.len() }
                .enumerate()
                .filter(|(_, window)| window == sub)
                .map(|(i, _)| i)
                .collect()
            )
        }
    }
}