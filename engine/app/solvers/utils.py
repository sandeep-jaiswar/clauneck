"""Shared utility functions for domain solvers.

New solvers (Phase 2+) should use these helpers to minimize boilerplate.
The original 11 solvers predate this module and reimplemented their own
local helpers — they are not retrofitted per the "don't refactor beyond
scope" principle, but they are candidates for a future cleanup ticket.
"""

import re
from typing import Dict, List, Tuple, Union, Callable, Any, Optional
import numpy as np
from app.model import Quantity


def get_value(quantities: Dict[str, Quantity], name: str,
              ic: Optional[Dict[str, float]] = None) -> float:
    """
    Lookup a required scalar quantity by name.
    Raises ValueError if quantity is not found or has no value.
    initialConditions takes precedence over Quantity.value if both present.
    """
    if ic and name in ic:
        return float(ic[name])
    if name not in quantities:
        raise ValueError(f"No value for quantity: {name}")
    q = quantities[name]
    if q.value is None:
        raise ValueError(f"Quantity '{name}' has no value")
    return float(q.value)


def get_optional_value(quantities: Dict[str, Quantity], name: str,
                       ic: Optional[Dict[str, float]] = None,
                       default: float = 0.0) -> float:
    """
    Lookup an optional scalar quantity by name.
    Returns `default` instead of raising if the quantity is missing or has no value.
    initialConditions takes precedence over Quantity.value if both present.
    """
    try:
        return get_value(quantities, name, ic)
    except ValueError:
        return default


def get_vector(quantities: Dict[str, Quantity], name: str) -> np.ndarray:
    """
    Lookup a vector (1D array) quantity by name.
    Accepts either a genuine 1D list or a 2D single-column list and normalizes to 1D.
    Raises ValueError if quantity is missing, not a list, or has non-numeric values.
    """
    if name not in quantities:
        raise ValueError(f"No quantity named: {name}")
    q = quantities[name]
    if q.value is None:
        raise ValueError(f"Quantity '{name}' has no value")
    try:
        arr = np.array(q.value, dtype=float)
        if arr.ndim == 1:
            return arr
        elif arr.ndim == 2 and arr.shape[1] == 1:
            return arr.flatten()
        else:
            raise ValueError(f"Quantity '{name}' must be a vector (1D array)")
    except (TypeError, ValueError) as e:
        raise ValueError(f"Quantity '{name}' is not a valid vector: {e}")


def get_matrix(quantities: Dict[str, Quantity], name: str) -> np.ndarray:
    """
    Lookup a matrix (2D array) quantity by name.
    Raises ValueError if quantity is missing, not a 2D array, or has non-numeric values.
    """
    if name not in quantities:
        raise ValueError(f"No quantity named: {name}")
    q = quantities[name]
    if q.value is None:
        raise ValueError(f"Quantity '{name}' has no value")
    try:
        arr = np.array(q.value, dtype=float)
        if arr.ndim != 2:
            raise ValueError(f"Quantity '{name}' must be a matrix (2D array)")
        return arr
    except (TypeError, ValueError) as e:
        raise ValueError(f"Quantity '{name}' is not a valid matrix: {e}")


def to_radians(value: float, si_unit: str) -> float:
    """
    Convert an angle to radians based on the siUnit field.
    Raises ValueError if unit is neither 'deg' nor 'rad'.
    """
    if si_unit == "rad":
        return value
    elif si_unit == "deg":
        return np.radians(value)
    else:
        raise ValueError(f"Unsupported angle unit '{si_unit}'; expected 'deg' or 'rad'")


def parse_call(expr: str) -> Tuple[str, List[str]]:
    """
    Parse a function call expression like 'func_name(arg1, arg2, ...)'.
    Returns (func_name, [list of argument strings]).
    Raises ValueError if the expression does not match the pattern.
    """
    match = re.fullmatch(r'([A-Za-z_]\w*)\((.*)\)', expr.strip())
    if not match:
        raise ValueError(f"Invalid operation format: {expr}")
    func_name = match.group(1)
    args_str = match.group(2).strip()
    if not args_str:
        return func_name, []
    arg_list = [arg.strip() for arg in args_str.split(',')]
    return func_name, arg_list


def resolve_arg(arg: str, quantities: Dict[str, Quantity]) -> Union[float, List[float]]:
    """
    Resolve an argument (name or literal) to a value.
    First tries to parse as a float literal; if that fails, looks up in quantities.
    Raises ValueError if neither works.
    """
    try:
        return float(arg)
    except ValueError:
        if arg in quantities:
            q = quantities[arg]
            if q.value is None:
                raise ValueError(f"Quantity '{arg}' has no value")
            return q.value
        raise ValueError(f"Could not resolve argument: {arg}")


def run_dispatch(model, quantities: Dict[str, Quantity],
                 operations: Dict[str, Callable]) -> Dict[str, Any]:
    """
    Shared multi-equation function-dispatch loop (the DRY win for Phase 2+ solvers).

    For each equation in model.equations (in order):
      1. Parse equation.rhs as 'func_name(arg1, arg2, ...)'
      2. Look up func_name in operations dict; raise ValueError if not found
      3. Resolve each argument (literal or quantity name)
      4. Call operations[func_name](*args), get result
      5. Accumulate into summary dict:
         - If result is a dict, add it with keys prefixed by equation.lhs + '_'
         - Otherwise, use equation.lhs as key (or func_name if lhs is empty)

    Returns the accumulated summary dict. Exceptions propagate as ValueError,
    caught by each solver's outer try/except per existing convention.
    """
    summary = {}
    for equation in model.equations:
        func_name, arg_strs = parse_call(equation.rhs)
        if func_name not in operations:
            raise ValueError(f"Unknown operation: {func_name}")
        args = [resolve_arg(a, quantities) for a in arg_strs]
        result = operations[func_name](*args)
        key = equation.lhs.strip() or func_name
        if isinstance(result, dict):
            summary.update({f"{key}_{k}": v for k, v in result.items()})
        else:
            summary[key] = result
    return summary
