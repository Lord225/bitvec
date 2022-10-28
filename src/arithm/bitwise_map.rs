use pyo3::{prelude::*, types, exceptions};
use bv::{self, BitsExt, Bits, BitsMut, BitsMutExt};
use bv::BitSliceable;

use crate::binary::*;

use super::bitwise::bitwise_not;


#[pyfunction(args="*", kwargs="**")]
pub fn bitwise_map(args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> PyResult<PyObject> 
{
    let map = kwargs.and_then(|kwargs| kwargs.get_item("map")).expect("map is not provided");
    let args = args.as_slice();
    if args.len() >= 32 {
        return Err(exceptions::PyValueError::new_err("This function can handle up to 31 arguments"));
    }

    // get the mapping (32 bits)
    let map = 
    if let Ok(map_dict) = map.extract::<&types::PyDict>() {
        let mut bitvec = bv::BitVec::<u32>::new_fill(false, 32);
        for (key, value) in map_dict {
            let key = 
            if let Ok(x) = crate::Binary::from(key, None, None) {
                use crate::binary::*;
                i64::from(&x.inner)
            } else {
                return Err(exceptions::PyValueError::new_err("map keys must be integers or Binary convertable objects"));
            };

            if key < 0 || key > 31 {
                return Err(exceptions::PyValueError::new_err("map keys must be in range [0, 31]"));
            }

            let value = 
            if let Ok(x) = value.extract::<bool>() {
                x
            } else {
                return Err(exceptions::PyValueError::new_err("map values must be bool or Binary convertable objects"));
            };

            bitvec.set(key.try_into().unwrap(), value);
        }
        bitvec
    } else if let Ok(binary) = crate::Binary::from(map, Some(2_usize.pow(args.len().try_into().unwrap())), Some("unsigned".into())) {
        binary.inner.data
    } else {
        return Err(exceptions::PyTypeError::new_err("map is not a dict or a binary"));
    };
    
    if map.len() < args.len().try_into().unwrap() {
        return Err(exceptions::PyValueError::new_err("map does not contain enough terms"));
    }
    if map.len() > 32 {
        return Err(exceptions::PyValueError::new_err("map is too big"));
    }

    let positive_terms = 
    (0..(map.len() as u32))
    .filter(|i| map.get((*i).into()))
    .map(bv::BitVec::<u32>::from_bits)
    .collect::<Vec<_>>();

    // get longest argumnet (TODO, use better metric)
    let longest = args
    .iter()
    .map(|arg| arg.len().unwrap())
    .max()
    .unwrap_or(0);
    
    // get all arguments as BitVecs of the same length (longest)
    let pos_args = 
    args
    .iter()
    .map(|arg| crate::Binary::from(arg, Some(longest), Some("unsigned".into())).unwrap())
    .map(|vec| vec.inner.data)
    .collect::<Vec<_>>();
    
    // get negation of all arguments
    let neg_args = pos_args
    .iter()
    .map(|arg| 
        arg
        .bit_not()
        .to_bit_vec())
    .collect::<Vec<_>>();

    let mut result = bv::BitVec::<u32>::new_fill(false, longest.try_into().unwrap());
    let mut itermid = bv::BitVec::<u32>::new_fill(true, longest.try_into().unwrap());
    
    // for each `1` term
    for term in positive_terms
    {
        // set intermid to all ones
        for i in 0..itermid.block_len() {
            itermid.set_block(i, u32::MAX);
        }
        // for each argument
        for (i, (pos, neg)) in pos_args.iter().zip(neg_args.iter()).enumerate()
        {
            // check if the term inverts the argument or not
            if term.get(i.try_into().unwrap()) {
                itermid.bit_and_assign(pos);
            } else {
                itermid.bit_and_assign(neg);
            }
        }
        // or the result with the intermediate result
        result.bit_or_assign(&itermid);
    }

    crate::Binary::wrap_object(Ok(BinaryBase::from_data(result)))
}
