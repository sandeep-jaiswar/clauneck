"""Test suite for shared solver utilities."""

import pytest
import numpy as np
from app.model import Quantity, Equation, ScientificModel, Solver, SolverMethod, EquationType, DimensionVector
from app.solvers.utils import (
    get_value, get_optional_value, get_vector, get_matrix,
    to_radians, parse_call, resolve_arg, run_dispatch
)


# ============ Fixtures ============

@pytest.fixture
def sample_quantities():
    """Build a sample quantities dict for testing."""
    return {
        "x": Quantity(name="x", value=3.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        "y": Quantity(name="y", value=2.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        "vector_v": Quantity(name="vector_v", value=[1.0, 2.0, 3.0], siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        "matrix_A": Quantity(name="matrix_A", value=[[1.0, 2.0], [3.0, 4.0]], siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        "angle_deg": Quantity(name="angle_deg", value=45.0, siUnit="deg", isKnown=True, dimensionVector=DimensionVector()),
        "angle_rad": Quantity(name="angle_rad", value=np.pi/4, siUnit="rad", isKnown=True, dimensionVector=DimensionVector()),
        "missing_value": Quantity(name="missing_value", value=None, siUnit="m", isKnown=False, dimensionVector=DimensionVector()),
    }


@pytest.fixture
def sample_ic():
    """Sample initialConditions dict."""
    return {"x": 10.0, "y": 20.0}


# ============ get_value tests ============

def test_get_value_from_quantity(sample_quantities):
    """get_value retrieves a scalar from Quantity.value."""
    assert get_value(sample_quantities, "x") == 3.5
    assert get_value(sample_quantities, "y") == 2.0


def test_get_value_from_ic_takes_precedence(sample_quantities, sample_ic):
    """initialConditions overrides Quantity.value."""
    assert get_value(sample_quantities, "x", sample_ic) == 10.0  # ic wins
    assert get_value(sample_quantities, "y", sample_ic) == 20.0  # ic wins


def test_get_value_missing_quantity(sample_quantities):
    """get_value raises ValueError for missing quantity."""
    with pytest.raises(ValueError, match="No value for quantity: nonexistent"):
        get_value(sample_quantities, "nonexistent")


def test_get_value_missing_value(sample_quantities):
    """get_value raises ValueError when value is None."""
    with pytest.raises(ValueError, match="has no value"):
        get_value(sample_quantities, "missing_value")


# ============ get_optional_value tests ============

def test_get_optional_value_returns_default(sample_quantities):
    """get_optional_value returns default when quantity missing."""
    assert get_optional_value(sample_quantities, "nonexistent", default=99.0) == 99.0


def test_get_optional_value_returns_zero_by_default(sample_quantities):
    """get_optional_value returns 0.0 by default."""
    assert get_optional_value(sample_quantities, "nonexistent") == 0.0


def test_get_optional_value_returns_value_if_found(sample_quantities):
    """get_optional_value returns the value if quantity exists."""
    assert get_optional_value(sample_quantities, "x") == 3.5


def test_get_optional_value_ic_takes_precedence(sample_quantities, sample_ic):
    """initialConditions overrides Quantity.value for optional values."""
    assert get_optional_value(sample_quantities, "x", sample_ic) == 10.0


# ============ get_vector tests ============

def test_get_vector_1d_list(sample_quantities):
    """get_vector returns a 1D NumPy array from a 1D list."""
    result = get_vector(sample_quantities, "vector_v")
    assert isinstance(result, np.ndarray)
    assert result.ndim == 1
    assert np.allclose(result, [1.0, 2.0, 3.0])


def test_get_vector_2d_single_column(sample_quantities):
    """get_vector flattens a 2D single-column array to 1D."""
    sample_quantities["col_vector"] = Quantity(
        name="col_vector", value=[[1.0], [2.0], [3.0]], siUnit="m", isKnown=True, dimensionVector=DimensionVector()
    )
    result = get_vector(sample_quantities, "col_vector")
    assert result.ndim == 1
    assert np.allclose(result, [1.0, 2.0, 3.0])


def test_get_vector_missing_quantity(sample_quantities):
    """get_vector raises ValueError for missing quantity."""
    with pytest.raises(ValueError, match="No quantity named"):
        get_vector(sample_quantities, "nonexistent")


def test_get_vector_wrong_shape(sample_quantities):
    """get_vector raises ValueError for non-vector shapes."""
    with pytest.raises(ValueError, match="must be a vector"):
        get_vector(sample_quantities, "matrix_A")


def test_get_vector_none_value(sample_quantities):
    """get_vector raises ValueError when value is None."""
    sample_quantities["none_vector"] = Quantity(
        name="none_vector", value=None, siUnit="m", isKnown=False, dimensionVector=DimensionVector()
    )
    with pytest.raises(ValueError, match="has no value"):
        get_vector(sample_quantities, "none_vector")


# ============ get_matrix tests ============

def test_get_matrix_2d_array(sample_quantities):
    """get_matrix returns a 2D NumPy array."""
    result = get_matrix(sample_quantities, "matrix_A")
    assert isinstance(result, np.ndarray)
    assert result.ndim == 2
    assert np.allclose(result, [[1.0, 2.0], [3.0, 4.0]])


def test_get_matrix_wrong_shape_1d(sample_quantities):
    """get_matrix raises ValueError for 1D arrays."""
    with pytest.raises(ValueError, match="must be a matrix"):
        get_matrix(sample_quantities, "vector_v")


def test_get_matrix_missing_quantity(sample_quantities):
    """get_matrix raises ValueError for missing quantity."""
    with pytest.raises(ValueError, match="No quantity named"):
        get_matrix(sample_quantities, "nonexistent")


# ============ to_radians tests ============

def test_to_radians_from_degrees(sample_quantities):
    """to_radians converts degrees to radians."""
    result = to_radians(45.0, "deg")
    assert np.isclose(result, np.pi / 4)


def test_to_radians_from_radians(sample_quantities):
    """to_radians returns radians unchanged."""
    result = to_radians(np.pi / 4, "rad")
    assert np.isclose(result, np.pi / 4)


def test_to_radians_invalid_unit():
    """to_radians raises ValueError for unsupported units."""
    with pytest.raises(ValueError, match="Unsupported angle unit"):
        to_radians(45.0, "grads")


# ============ parse_call tests ============

def test_parse_call_no_args():
    """parse_call handles zero-argument functions."""
    func_name, args = parse_call("sin()")
    assert func_name == "sin"
    assert args == []


def test_parse_call_single_arg():
    """parse_call parses single-argument functions."""
    func_name, args = parse_call("sqrt(x)")
    assert func_name == "sqrt"
    assert args == ["x"]


def test_parse_call_multiple_args():
    """parse_call parses multi-argument functions."""
    func_name, args = parse_call("add(a, b, c)")
    assert func_name == "add"
    assert args == ["a", "b", "c"]


def test_parse_call_whitespace_handling():
    """parse_call handles whitespace around arguments."""
    func_name, args = parse_call("  func_name(  arg1 , arg2  )  ")
    assert func_name == "func_name"
    assert args == ["arg1", "arg2"]


def test_parse_call_invalid_format():
    """parse_call raises ValueError for invalid format."""
    with pytest.raises(ValueError, match="Invalid operation format"):
        parse_call("not_a_call")


def test_parse_call_nested_parens():
    """parse_call does not parse nested function calls (simplicity)."""
    # This would require recursive parsing, which is out of scope for Phase 2.
    # Document as a limitation.
    func_name, args = parse_call("outer(inner(x))")
    assert func_name == "outer"
    assert args == ["inner(x)"]  # Single arg that contains a nested call


# ============ resolve_arg tests ============

def test_resolve_arg_numeric_literal(sample_quantities):
    """resolve_arg parses numeric literals."""
    assert resolve_arg("3.14", sample_quantities) == 3.14
    assert resolve_arg("42", sample_quantities) == 42


def test_resolve_arg_quantity_lookup(sample_quantities):
    """resolve_arg looks up quantity names."""
    assert resolve_arg("x", sample_quantities) == 3.5


def test_resolve_arg_list_quantity(sample_quantities):
    """resolve_arg can return a list from a vector quantity."""
    result = resolve_arg("vector_v", sample_quantities)
    assert isinstance(result, list)
    assert result == [1.0, 2.0, 3.0]


def test_resolve_arg_unresolvable(sample_quantities):
    """resolve_arg raises ValueError when argument can't be resolved."""
    with pytest.raises(ValueError, match="Could not resolve argument"):
        resolve_arg("unknown_symbol", sample_quantities)


# ============ run_dispatch tests ============

def test_run_dispatch_single_operation(sample_quantities):
    """run_dispatch calls a single operation and stores result."""
    operations = {"double": lambda x: x * 2}
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="result", rhs="double(5.0)", type=EquationType.ALGEBRAIC)
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    summary = run_dispatch(model, sample_quantities, operations)
    assert summary["result"] == 10.0


def test_run_dispatch_multiple_operations(sample_quantities):
    """run_dispatch processes multiple equations in order."""
    operations = {
        "double": lambda x: x * 2,
        "square": lambda x: x ** 2,
    }
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="a", rhs="double(3)", type=EquationType.ALGEBRAIC),
            Equation(lhs="b", rhs="square(4)", type=EquationType.ALGEBRAIC),
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    summary = run_dispatch(model, sample_quantities, operations)
    assert summary["a"] == 6.0
    assert summary["b"] == 16.0


def test_run_dispatch_dict_result_prefix(sample_quantities):
    """run_dispatch prefixes dict results by equation.lhs."""
    operations = {
        "pair": lambda x: {"left": x * 2, "right": x * 3},
    }
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="out", rhs="pair(5)", type=EquationType.ALGEBRAIC),
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    summary = run_dispatch(model, sample_quantities, operations)
    assert summary["out_left"] == 10.0
    assert summary["out_right"] == 15.0


def test_run_dispatch_unknown_operation(sample_quantities):
    """run_dispatch raises ValueError for unknown operations."""
    operations = {"known_op": lambda x: x}
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="result", rhs="unknown_op(5)", type=EquationType.ALGEBRAIC),
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    with pytest.raises(ValueError, match="Unknown operation"):
        run_dispatch(model, sample_quantities, operations)


def test_run_dispatch_unresolvable_arg(sample_quantities):
    """run_dispatch raises ValueError when arguments can't be resolved."""
    operations = {"op": lambda x: x}
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="result", rhs="op(unknown_var)", type=EquationType.ALGEBRAIC),
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    with pytest.raises(ValueError, match="Could not resolve argument"):
        run_dispatch(model, sample_quantities, operations)


def test_run_dispatch_empty_lhs_uses_func_name(sample_quantities):
    """run_dispatch uses function name as key if lhs is empty."""
    operations = {"func": lambda x: x * 10}
    model = ScientificModel(
        id="test", domain="test.domain", quantities=[], equations=[
            Equation(lhs="", rhs="func(2)", type=EquationType.ALGEBRAIC),
        ], solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )
    summary = run_dispatch(model, sample_quantities, operations)
    assert summary["func"] == 20.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
