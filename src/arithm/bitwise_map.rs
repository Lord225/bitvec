use pyo3::{prelude::*, types, exceptions};
use bv::{self, BitsExt, Bits, BitsMut, BitsMutExt};

use crate::binary::*;


#[pyfunction(args="*", kwargs="**")]
pub fn bitwise_map(args: &types::PyTuple, kwargs: Option<&types::PyDict>) -> PyResult<PyObject> 
{
    let map = kwargs.and_then(|kwargs| kwargs.get_item("map")).expect("Map is not provided, provide map by adding `map=\"..\"` to the function call");
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
            match crate::Binary::from(key, None, None) {
                Ok(key) => i64::from(&key.inner),
                Err(_) => return Err(exceptions::PyValueError::new_err(format!("Key cannot be interpreted as Binary '{:?}'", key))),
            };

            if key < 0 || key > 31 {
                return Err(exceptions::PyValueError::new_err("Map keys must be in range [0, 31]"));
            }

            let value = 
            match value.extract::<bool>() {
                Ok(x) => x,
                Err(_) => return Err(exceptions::PyValueError::new_err(format!("Dict Values should be booleans, but got '{:?}'", key))),
            };

            bitvec.set(key.try_into().unwrap(), value);
        }
        bitvec
    } else {
        match crate::Binary::from(map, Some(2_usize.pow(args.len().try_into().unwrap())), Some("unsigned".into())) {
            Ok(x) => x.inner.data,
            Err(err) => return Err(exceptions::PyValueError::new_err(format!("Map should be dict or Binary, but instead got: '{:?}' and it faild to convert: {:?}", map, err))),
        }
    };
    
    if map.len() < args.len().try_into().unwrap() {
        return Err(exceptions::PyValueError::new_err(format!("Map should have at least {} terms but it has {}", args.len(), map.len())));
    }
    if map.len() > 32 {
        return Err(exceptions::PyValueError::new_err(format!("Map cannot exeed 32 terms, but it contains {} terms", map.len())));
    }

    // get all terms that should be tested
    let positive_terms = 
    (0..(map.len() as u32))
    .filter(|i| map.get((*i).into()))
    .map(bv::BitVec::<u32>::from_bits)
    .map(|x| (0..32u64).map(|i| x.get(i)).collect::<Vec<_>>())
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
            if term[i] {
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
