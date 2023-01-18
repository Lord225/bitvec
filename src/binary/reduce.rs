use std::ops::Deref;
use std::iter::IntoIterator;

use bv::{BitSlice, BlockType, Bits};

pub trait ReduceOps {
    fn none(&self) -> bool;
    fn all(&self) -> bool;
    fn any_false(&self) -> bool;
    fn any(&self) -> bool {
        !self.none()
    }
}

pub struct IterableBitSlice<'a, Other: Bits + 'a>(pub &'a Other, u64);

impl<'a, Other: Bits+'a> IterableBitSlice<'a, Other> {
    pub fn new(slice: &'a Other) -> Self {
        Self(slice, 0)
    }
}

impl<'a, Other: Bits+'a> Iterator for IterableBitSlice<'a, Other> 
{
    type Item = bool;

    fn next(&mut self) -> Option<Self::Item> {
        if self.1 >= self.0.bit_len() {
            None
        } else {
            let bit = self.0.get_bit(self.1);
            self.1 += 1;
            Some(bit)
        }
    }
}
impl<'a, Other: Bits+'a> DoubleEndedIterator for IterableBitSlice<'a, Other> 
{
    fn next_back(&mut self) -> Option<Self::Item> {
        if self.1 >= self.0.bit_len() {
            None
        } else {
            self.1 += 1;
            Some(self.0.get_bit(self.0.bit_len() - self.1))
        }
    }
}

impl<'a, Other: Bits+'a> Deref for IterableBitSlice<'a, Other> {
    type Target = Other;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'a, Block: BlockType> ReduceOps for BitSlice<'a, Block> 
{
    fn none(&self) -> bool
    {
        IterableBitSlice::new(self).into_iter().all(|b| b == false)
    }
    fn all(&self) -> bool
    {
        IterableBitSlice::new(self).into_iter().all(|b| b == true)
    }
    fn any_false(&self) -> bool {
        IterableBitSlice::new(self).into_iter().any(|b| b == false)
    }
}