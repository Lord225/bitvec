use bv::{BitSlice, BlockType, Bits};


pub trait ReduceOps {
    fn none(&self) -> bool;
    fn all(&self) -> bool;
    fn any_false(&self) -> bool;
    fn any(&self) -> bool {
        !self.none()
    }
}

impl<'a, Block: BlockType> ReduceOps for BitSlice<'a, Block> 
{
    fn none(&self) -> bool
    {
        (0..self.bit_len()).map(|i| self.get_bit(i)).all(|b| b == false)
    }
    fn all(&self) -> bool
    {
        (0..self.bit_len()).map(|i| self.get_bit(i)).all(|b| b == true)
    }
    fn any_false(&self) -> bool {
        (0..self.bit_len()).map(|i| self.get_bit(i)).any(|b| b == false)
    }
}