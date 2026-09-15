"""
Tests for numerical methods solver.
Covers root-finding, interpolation, differentiation, integration, ODE solving.
"""
import numpy as np
import pytest
import math

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.numerical_methods import NumericalMethodsSolver


@pytest.fixture
def bisection_model():
    """Model for bisection method: find root of x^2 - 2 in [1, 2]."""
    return ScientificModel(
        id="nm-bisection-sqrt2",
        domain="mathematics.numerical_methods",
        description="Find sqrt(2) using bisection",
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
                description="Root of x^2 - 2"
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def lagrange_model():
    """Model for Lagrange interpolation."""
    return ScientificModel(
        id="nm-lagrange-interp",
        domain="mathematics.numerical_methods",
        description="Lagrange interpolation",
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
def cubic_spline_model():
    """Model for cubic spline interpolation."""
    return ScientificModel(
        id="nm-spline-interp",
        domain="mathematics.numerical_methods",
        description="Cubic spline interpolation",
        quantities=[
            Quantity(name="x_data", value=[0.0, 1.0, 2.0, 3.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_data", value=[0.0, 1.0, 4.0, 9.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="y",
                rhs="cubic_spline(x_data, y_data, x)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def finite_diff_1st_model():
    """Model for first-order finite difference."""
    return ScientificModel(
        id="nm-fd1-sin",
        domain="mathematics.numerical_methods",
        description="First-order finite difference of sin(x)",
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


@pytest.fixture
def trapezoidal_model():
    """Model for trapezoidal integration."""
    return ScientificModel(
        id="nm-trap-int",
        domain="mathematics.numerical_methods",
        description="Trapezoidal integration of x^2 from 0 to 2",
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
def simpsons_model():
    """Model for Simpson's rule integration."""
    return ScientificModel(
        id="nm-simpson-int",
        domain="mathematics.numerical_methods",
        description="Simpson's rule integration of x^2 from 0 to 2",
        quantities=[
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=1000, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="integral",
                rhs="simpsons_rule(x**2, a, b, n)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def gauss_legendre_model():
    """Model for Gauss-Legendre integration."""
    return ScientificModel(
        id="nm-gauss-int",
        domain="mathematics.numerical_methods",
        description="Gauss-Legendre integration of sin(x) from 0 to pi",
        quantities=[
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=math.pi, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=10, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="integral",
                rhs="gauss_legendre_integration(sin(x), a, b, n)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============= Correctness Tests =============

def test_bisection_solvable(bisection_model):
    """Test bisection method solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(bisection_model)
    assert result.success
    assert result.summary is not None
    assert "root" in result.summary


def test_bisection_correctness(bisection_model):
    """Test bisection method finds correct root."""
    solver = NumericalMethodsSolver()
    result = solver.solve(bisection_model)
    assert result.success

    root = result.summary["root"]
    expected_root = math.sqrt(2)
    assert abs(root - expected_root) < 1e-5


def test_lagrange_solvable(lagrange_model):
    """Test Lagrange interpolation solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(lagrange_model)
    assert result.success
    assert result.summary is not None
    assert "y" in result.summary


def test_lagrange_correctness(lagrange_model):
    """Test Lagrange interpolation accuracy."""
    solver = NumericalMethodsSolver()
    result = solver.solve(lagrange_model)
    assert result.success

    y = result.summary["y"]
    assert y > 2.0
    assert y < 4.0


def test_cubic_spline_solvable(cubic_spline_model):
    """Test cubic spline interpolation solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(cubic_spline_model)
    assert result.success
    assert result.summary is not None
    assert "y" in result.summary


def test_cubic_spline_correctness(cubic_spline_model):
    """Test cubic spline interpolation accuracy."""
    solver = NumericalMethodsSolver()
    result = solver.solve(cubic_spline_model)
    assert result.success

    y = result.summary["y"]
    assert y > 1.0
    assert y < 4.0


def test_finite_diff_1st_solvable(finite_diff_1st_model):
    """Test first-order finite difference solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(finite_diff_1st_model)
    assert result.success
    assert result.summary is not None
    assert "derivative" in result.summary


def test_finite_diff_1st_correctness(finite_diff_1st_model):
    """Test first-order finite difference is close to actual derivative."""
    solver = NumericalMethodsSolver()
    result = solver.solve(finite_diff_1st_model)
    assert result.success

    deriv = result.summary["derivative"]
    expected = math.cos(0.5)
    assert abs(deriv - expected) < 0.01


def test_trapezoidal_solvable(trapezoidal_model):
    """Test trapezoidal integration solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(trapezoidal_model)
    assert result.success
    assert result.summary is not None
    assert "integral" in result.summary


def test_trapezoidal_correctness(trapezoidal_model):
    """Test trapezoidal integration accuracy."""
    solver = NumericalMethodsSolver()
    result = solver.solve(trapezoidal_model)
    assert result.success

    integral = result.summary["integral"]
    expected = 8.0 / 3.0  # ∫₀² x² dx = 8/3
    assert abs(integral - expected) < 0.01


def test_simpsons_solvable(simpsons_model):
    """Test Simpson's rule integration solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(simpsons_model)
    assert result.success
    assert result.summary is not None
    assert "integral" in result.summary


def test_simpsons_correctness(simpsons_model):
    """Test Simpson's rule integration accuracy."""
    solver = NumericalMethodsSolver()
    result = solver.solve(simpsons_model)
    assert result.success

    integral = result.summary["integral"]
    expected = 8.0 / 3.0
    assert abs(integral - expected) < 0.001


def test_gauss_legendre_solvable(gauss_legendre_model):
    """Test Gauss-Legendre integration solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(gauss_legendre_model)
    assert result.success
    assert result.summary is not None
    assert "integral" in result.summary


def test_gauss_legendre_correctness(gauss_legendre_model):
    """Test Gauss-Legendre integration accuracy."""
    solver = NumericalMethodsSolver()
    result = solver.solve(gauss_legendre_model)
    assert result.success

    integral = result.summary["integral"]
    expected = 2.0  # ∫₀^π sin(x) dx = 2
    assert abs(integral - expected) < 0.01
