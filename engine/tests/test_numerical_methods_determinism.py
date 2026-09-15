"""
Determinism tests for numerical methods solver.
Verifies that solve(model) twice produces identical results.
"""
import pytest
import math

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solvers.numerical_methods import NumericalMethodsSolver


@pytest.fixture
def bisection_model():
    """Bisection model for determinism testing."""
    return ScientificModel(
        id="nm-det-bisection",
        domain="mathematics.numerical_methods",
        description="Determinism test: Bisection",
        quantities=[
            Quantity(name="a", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="max_iter", value=100, siUnit="dimensionless", isKnown=True),
            Quantity(name="tolerance", value=1e-6, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="root",
                rhs="bisection_method(x**2 - 2, a, b, max_iter, tolerance)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def lagrange_model():
    """Lagrange interpolation model for determinism testing."""
    return ScientificModel(
        id="nm-det-lagrange",
        domain="mathematics.numerical_methods",
        description="Determinism test: Lagrange",
        quantities=[
            Quantity(name="x_data", value=[0.0, 1.0, 2.0, 3.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_data", value=[1.0, 2.0, 4.0, 8.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="y",
                rhs="lagrange_interpolation(x_data, y_data, x)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def trapezoidal_model():
    """Trapezoidal integration model for determinism testing."""
    return ScientificModel(
        id="nm-det-trapezoidal",
        domain="mathematics.numerical_methods",
        description="Determinism test: Trapezoidal",
        quantities=[
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=1000, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="integral",
                rhs="trapezoidal_integration(x**2, a, b, n)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def finite_diff_model():
    """Finite difference model for determinism testing."""
    return ScientificModel(
        id="nm-det-fd",
        domain="mathematics.numerical_methods",
        description="Determinism test: Finite Difference",
        quantities=[
            Quantity(name="x", value=0.5, siUnit="dimensionless", isKnown=True),
            Quantity(name="h", value=1e-5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="derivative",
                rhs="finite_difference_1st_order(sin(x), x, h)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============= Determinism Tests =============

def test_determinism_bisection(bisection_model):
    """Test bisection returns same result on repeated calls."""
    solver = NumericalMethodsSolver()

    result1 = solver.solve(bisection_model)
    result2 = solver.solve(bisection_model)

    assert result1.success and result2.success
    assert result1.summary["root"] == result2.summary["root"]


def test_determinism_lagrange(lagrange_model):
    """Test Lagrange interpolation returns same result on repeated calls."""
    solver = NumericalMethodsSolver()

    result1 = solver.solve(lagrange_model)
    result2 = solver.solve(lagrange_model)

    assert result1.success and result2.success
    assert result1.summary["y"] == result2.summary["y"]


def test_determinism_trapezoidal(trapezoidal_model):
    """Test trapezoidal integration returns same result on repeated calls."""
    solver = NumericalMethodsSolver()

    result1 = solver.solve(trapezoidal_model)
    result2 = solver.solve(trapezoidal_model)

    assert result1.success and result2.success
    # Use approximate equality for floating point
    assert abs(result1.summary["integral"] - result2.summary["integral"]) < 1e-10


def test_determinism_finite_diff(finite_diff_model):
    """Test finite difference returns same result on repeated calls."""
    solver = NumericalMethodsSolver()

    result1 = solver.solve(finite_diff_model)
    result2 = solver.solve(finite_diff_model)

    assert result1.success and result2.success
    # Use approximate equality for floating point
    assert abs(result1.summary["derivative"] - result2.summary["derivative"]) < 1e-10


def test_determinism_multiple_calls():
    """Test that multiple sequential calls produce consistent results."""
    model = ScientificModel(
        id="nm-det-multi",
        domain="mathematics.numerical_methods",
        description="Multi-call determinism",
        quantities=[
            Quantity(name="a", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="max_iter", value=50, siUnit="dimensionless", isKnown=True),
            Quantity(name="tolerance", value=1e-7, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="root",
                rhs="bisection_method(x**2 - 3, a, b, max_iter, tolerance)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-7),
        metadata=Metadata(source="test")
    )

    solver = NumericalMethodsSolver()

    # Solve 5 times
    results = [solver.solve(model) for _ in range(5)]

    # All should succeed
    assert all(r.success for r in results)

    # All should have same root
    root_values = [r.summary["root"] for r in results]
    for root in root_values[1:]:
        assert root == root_values[0]


def test_determinism_simpson_rule():
    """Test Simpson's rule determinism."""
    model = ScientificModel(
        id="nm-det-simpson",
        domain="mathematics.numerical_methods",
        description="Determinism test: Simpson's rule",
        quantities=[
            Quantity(name="a", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=3.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=100, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="integral",
                rhs="simpsons_rule(x**3, a, b, n)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = NumericalMethodsSolver()

    result1 = solver.solve(model)
    result2 = solver.solve(model)

    assert result1.success and result2.success
    assert abs(result1.summary["integral"] - result2.summary["integral"]) < 1e-12
