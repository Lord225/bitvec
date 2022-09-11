use pyo3::{prelude::*};

pub mod add;
pub mod sub;
pub mod mul;
pub mod utility;
pub mod flags;
pub mod bitwise;
pub mod shifts;

pub fn register_arithm_module<'a>(_py: Python<'a>) -> PyResult<&'a PyModule> {
    let arithm = PyModule::new(_py, "arithm")?;
    
    arithm.add_class::<flags::Flags>()?;

    arithm.add_function(wrap_pyfunction!(add::overflowing_add, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(add::wrapping_add, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(add::flaged_add, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(add::arithmetic_neg, arithm)?)?;

    arithm.add_function(wrap_pyfunction!(sub::overflowing_sub, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(sub::wrapping_sub, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(sub::flaged_sub, arithm)?)?;

    arithm.add_function(wrap_pyfunction!(utility::cast, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(utility::convert, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(utility::extend_to_signed, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(utility::pad_zeros, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(utility::pad_ones, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(utility::pad_sign_extend, arithm)?)?;

    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_not, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_or, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_xor, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_and, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_nor, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_xnor, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(bitwise::bitwise_nand, arithm)?)?;
    
    arithm.add_function(wrap_pyfunction!(shifts::overflowing_lsh, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(shifts::wrapping_lsh, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(shifts::logical_underflowing_rsh, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(shifts::logical_wrapping_rsh, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(shifts::arithmetic_underflowing_rsh, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(shifts::arithmetic_wrapping_rsh, arithm)?)?;

    arithm.add_function(wrap_pyfunction!(mul::multiply, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(mul::overflowing_mul, arithm)?)?;
    arithm.add_function(wrap_pyfunction!(mul::wrapping_mul, arithm)?)?;

    return Ok(arithm);
}