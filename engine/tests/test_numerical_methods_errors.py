"""
Error handling and edge case tests for numerical methods solver.
"""
import pytest
import math

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solvers.numerical_methods import NumericalMethodsSolver


def _make_model(domain_name, description, quantities, lhs, rhs):
    """Helper to create a model."""
    return ScientificModel(
        id=domain_name,
        domain="mathematics.numerical_methods",
        description=description,
        quantities=quantities,
        equations=[
            Equation(lhs=lhs, rhs=rhs, type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============= Root-Finding Error Tests =============

def test_bisection_no_sign_change():
    """Test bisection when f(a) and f(b) have same sign."""
    model = _make_model(
        "nm-error-bisect-sign",
        "Bisection without sign change",
        [
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="max_iter", value=100, siUnit="dimensionless", isKnown=True),
            Quantity(name="tolerance", value=1e-6, siUnit="dimensionless", isKnown=True),
        ],
        "root",
        "bisection_method(x**2 + 1, a, b, max_iter, tolerance)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_bisection_invalid_interval():
    """Test bisection with a >= b."""
    model = _make_model(
        "nm-error-bisect-interval",
        "Bisection with invalid interval",
        [
            Quantity(name="a", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="max_iter", value=100, siUnit="dimensionless", isKnown=True),
            Quantity(name="tolerance", value=1e-6, siUnit="dimensionless", isKnown=True),
        ],
        "root",
        "bisection_method(x**2 - 2, a, b, max_iter, tolerance)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_brent_no_sign_change():
    """Test Brent's method without sign change."""
    model = _make_model(
        "nm-error-brent-sign",
        "Brent without sign change",
        [
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="tolerance", value=1e-6, siUnit="dimensionless", isKnown=True),
        ],
        "root",
        "brent_method(x**2 + 1, a, b, tolerance)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


# ============= Interpolation Error Tests =============

def test_lagrange_mismatched_lengths():
    """Test Lagrange with mismatched x and y lengths."""
    model = _make_model(
        "nm-error-lagrange-length",
        "Lagrange with mismatched lengths",
        [
            Quantity(name="x_data", value=[0.0, 1.0, 2.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_data", value=[1.0, 2.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
        ],
        "y",
        "lagrange_interpolation(x_data, y_data, x)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_lagrange_insufficient_points():
    """Test Lagrange with only one data point."""
    model = _make_model(
        "nm-error-lagrange-points",
        "Lagrange with only one point",
        [
            Quantity(name="x_data", value=[0.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_data", value=[1.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
        ],
        "y",
        "lagrange_interpolation(x_data, y_data, x)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_cubic_spline_insufficient_points():
    """Test cubic spline with only one point."""
    model = _make_model(
        "nm-error-spline-points",
        "Cubic spline with one point",
        [
            Quantity(name="x_data", value=[0.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_data", value=[1.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
        ],
        "y",
        "cubic_spline(x_data, y_data, x)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


# ============= Finite Difference Error Tests =============

def test_finite_diff_1st_negative_step():
    """Test FD with negative step size."""
    model = _make_model(
        "nm-error-fd1-step",
        "FD1 with negative step",
        [
            Quantity(name="x", value=0.5, siUnit="dimensionless", isKnown=True),
            Quantity(name="h", value=-1e-5, siUnit="dimensionless", isKnown=True),
        ],
        "derivative",
        "finite_difference_1st_order(sin(x), x, h)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_finite_diff_2nd_zero_step():
    """Test FD2 with zero step size."""
    model = _make_model(
        "nm-error-fd2-step",
        "FD2 with zero step",
        [
            Quantity(name="x", value=0.5, siUnit="dimensionless", isKnown=True),
            Quantity(name="h", value=0.0, siUnit="dimensionless", isKnown=True),
        ],
        "second_deriv",
        "finite_difference_2nd_order(sin(x), x, h)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


# ============= Integration Error Tests =============

def test_trapezoidal_invalid_interval():
    """Test trapezoidal with a >= b."""
    model = _make_model(
        "nm-error-trap-interval",
        "Trapezoidal with invalid interval",
        [
            Quantity(name="a", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=100, siUnit="dimensionless", isKnown=True),
        ],
        "integral",
        "trapezoidal_integration(x**2, a, b, n)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_simpsons_zero_intervals():
    """Test Simpson's rule with zero intervals."""
    model = _make_model(
        "nm-error-simpson-intervals",
        "Simpson's with zero intervals",
        [
            Quantity(name="a", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=0, siUnit="dimensionless", isKnown=True),
        ],
        "integral",
        "simpsons_rule(x**2, a, b, n)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_gauss_legendre_invalid_interval():
    """Test Gauss-Legendre with a >= b."""
    model = _make_model(
        "nm-error-gauss-interval",
        "Gauss-Legendre with invalid interval",
        [
            Quantity(name="a", value=math.pi, siUnit="dimensionless", isKnown=True),
            Quantity(name="b", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=10, siUnit="dimensionless", isKnown=True),
        ],
        "integral",
        "gauss_legendre_integration(sin(x), a, b, n)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


# ============= ODE Error Tests =============

def test_rk45_negative_step():
    """Test RK45 with negative step size."""
    model = _make_model(
        "nm-error-rk45-step",
        "RK45 with negative step",
        [
            Quantity(name="y", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="t", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="dt", value=-0.1, siUnit="dimensionless", isKnown=True),
        ],
        "result",
        "rk45_step(y, y, t, dt)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success


def test_bdf_zero_step():
    """Test BDF with zero step size."""
    model = _make_model(
        "nm-error-bdf-step",
        "BDF with zero step",
        [
            Quantity(name="y", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="t", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="dt", value=0.0, siUnit="dimensionless", isKnown=True),
        ],
        "result",
        "bdf_step(-100*y, y, t, dt)"
    )

    solver = NumericalMethodsSolver()
    result = solver.solve(model)
    assert not result.success
