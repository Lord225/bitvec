use std::ops::{Deref, Range};
use std::iter::{IntoIterator, Map};

use bv::{BitSlice, BlockType, Bits};

pub trait ReduceOps {
    fn none(&self) -> bool;
    fn all(&self) -> bool;
    fn any_false(&self) -> bool;
    fn any(&self) -> bool {
        !self.none()
    }
}

pub struct IterableBitSlice<'a, Other: Bits + 'a>(pub &'a Other);

impl<'a, Other: Bits+'a> IntoIterator for IterableBitSlice<'a, Other> {
    type Item = bool;

    type IntoIter = Map<Range<u64>, impl FnMut(u64) -> bool>;

    fn into_iter(self) -> Self::IntoIter {
        let len = self.bit_len();
        (0..len).map(move |i| self.get_bit(i))
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
        IterableBitSlice(self).into_iter().all(|b| b == false)
    }
    fn all(&self) -> bool
    {
        IterableBitSlice(self).into_iter().all(|b| b == true)
    }
    fn any_false(&self) -> bool {
        IterableBitSlice(self).into_iter().any(|b| b == false)
    }
}