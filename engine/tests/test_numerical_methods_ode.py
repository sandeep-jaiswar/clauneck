"""
Tests for ODE solvers in numerical methods.
Covers RK45, BDF, adaptive step control, and stiff systems.
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
def rk45_step_model():
    """Model for RK45 step: dy/dt = y, y(0)=1."""
    return ScientificModel(
        id="nm-rk45-exp",
        domain="mathematics.numerical_methods",
        description="RK45 step for exponential growth",
        quantities=[
            Quantity(name="y_val", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="t_val", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="dt_val", value=0.1, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="result",
                rhs="rk45_step(y, y_val, t_val, dt_val)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def bdf_step_model():
    """Model for BDF step: dy/dt = -100*y (stiff), y(0)=1."""
    return ScientificModel(
        id="nm-bdf-stiff",
        domain="mathematics.numerical_methods",
        description="BDF step for stiff ODE",
        quantities=[
            Quantity(name="y_val", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="t_val", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="dt_val", value=0.01, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="result",
                rhs="bdf_step(-100*y, y_val, t_val, dt_val)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def adaptive_step_model():
    """Model for adaptive step control."""
    return ScientificModel(
        id="nm-adaptive-step",
        domain="mathematics.numerical_methods",
        description="Adaptive step control for ODE",
        quantities=[
            Quantity(name="y_val", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="t_val", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="dt_val", value=0.1, siUnit="dimensionless", isKnown=True),
            Quantity(name="tol_val", value=1e-6, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="result",
                rhs="ode_adaptive_step(y, y_val, t_val, dt_val, tol_val)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def solve_stiff_system_model():
    """Model for solving stiff ODE system."""
    return ScientificModel(
        id="nm-stiff-system",
        domain="mathematics.numerical_methods",
        description="Solve stiff ODE system",
        quantities=[
            Quantity(name="f_code_list", value=["y0 - y1", "-100*y1"], siUnit="dimensionless", isKnown=True),
            Quantity(name="y_init", value=[1.0, 1.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="t_span", value=[0.0, 1.0], siUnit="dimensionless", isKnown=True),
            Quantity(name="n_points", value=100, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="solution",
                rhs="solve_stiff_system(f_code_list, y_init, t_span, n_points)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============= RK45 Tests =============

def test_rk45_step_solvable(rk45_step_model):
    """Test RK45 step solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(rk45_step_model)
    assert result.success
    assert result.summary is not None
    assert "result" in result.summary


def test_rk45_step_correctness(rk45_step_model):
    """Test RK45 step for exponential growth."""
    solver = NumericalMethodsSolver()
    result = solver.solve(rk45_step_model)
    assert result.success

    t_new, y_new = result.summary["result"]
    expected_y = math.exp(0.1)
    assert abs(y_new - expected_y) < 0.01
    assert abs(t_new - 0.1) < 1e-10


def test_rk45_step_time_advance(rk45_step_model):
    """Test that RK45 properly advances time."""
    solver = NumericalMethodsSolver()
    result = solver.solve(rk45_step_model)
    assert result.success

    t_new, y_new = result.summary["result"]
    assert t_new > 0.0


# ============= BDF Tests =============

def test_bdf_step_solvable(bdf_step_model):
    """Test BDF step solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(bdf_step_model)
    assert result.success
    assert result.summary is not None
    assert "result" in result.summary


def test_bdf_step_handles_stiff_system(bdf_step_model):
    """Test BDF is stable for stiff systems."""
    solver = NumericalMethodsSolver()
    result = solver.solve(bdf_step_model)
    assert result.success

    t_new, y_new = result.summary["result"]
    assert y_new > 0


# ============= Adaptive Step Tests =============

def test_adaptive_step_solvable(adaptive_step_model):
    """Test adaptive step control solves successfully."""
    solver = NumericalMethodsSolver()
    result = solver.solve(adaptive_step_model)
    assert result.success
    assert result.summary is not None
    assert "result" in result.summary


def test_adaptive_step_returns_new_step(adaptive_step_model):
    """Test adaptive step returns next step size."""
    solver = NumericalMethodsSolver()
    result = solver.solve(adaptive_step_model)
    assert result.success

    t_new, y_new, dt_new = result.summary["result"]
    assert t_new >= 0
    assert y_new > 0
    assert dt_new > 0
