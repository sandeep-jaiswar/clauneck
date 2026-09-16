"""Tests for simple harmonic motion solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_shm import PhysicsSimpleHarmonicMotionSolver


@pytest.fixture
def spring_period_model():
    """Model for spring period calculation."""
    return ScientificModel(
        id="shm-spring-period",
        domain="physics.simple_harmonic_motion",
        description="Spring period",
        quantities=[
            Quantity(name="m", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=100.0, siUnit="N/m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="T", rhs="period_spring(m, k)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def pendulum_period_model():
    """Model for pendulum period calculation."""
    return ScientificModel(
        id="shm-pendulum-period",
        domain="physics.simple_harmonic_motion",
        description="Pendulum period",
        quantities=[
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="T", rhs="period_pendulum(L, g)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def max_velocity_model():
    """Model for maximum velocity in SHM."""
    return ScientificModel(
        id="shm-max-velocity",
        domain="physics.simple_harmonic_motion",
        description="Max velocity",
        quantities=[
            Quantity(name="A", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="omega", value=10.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v_max", rhs="max_velocity(A, omega)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def energy_model():
    """Model for total mechanical energy in SHM."""
    return ScientificModel(
        id="shm-energy",
        domain="physics.simple_harmonic_motion",
        description="Total energy",
        quantities=[
            Quantity(name="k", value=100.0, siUnit="N/m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="A", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E", rhs="total_energy(k, A)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def position_model():
    """Model for position in SHM."""
    return ScientificModel(
        id="shm-position",
        domain="physics.simple_harmonic_motion",
        description="Position",
        quantities=[
            Quantity(name="A", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="omega", value=2.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="phi", value=0.0, siUnit="rad", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=0.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="x", rhs="position_at_t(A, omega, phi, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_spring_period_solvable(spring_period_model):
    """Test that spring period solves successfully."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(spring_period_model)

    assert result.success
    assert "T" in result.summary


def test_spring_period_correctness(spring_period_model):
    """Test spring period: T = 2π√(m/k)."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(spring_period_model)

    assert result.success
    # T = 2π√(1/100) = 2π * 0.1 ≈ 0.628 s
    expected_T = 2.0 * np.pi * np.sqrt(1.0 / 100.0)
    assert abs(result.summary["T"] - expected_T) < 1e-6


def test_pendulum_period_solvable(pendulum_period_model):
    """Test that pendulum period solves successfully."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(pendulum_period_model)

    assert result.success
    assert "T" in result.summary


def test_pendulum_period_correctness(pendulum_period_model):
    """Test pendulum period: T = 2π√(L/g)."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(pendulum_period_model)

    assert result.success
    # T = 2π√(1/9.81) ≈ 2.006 s
    expected_T = 2.0 * np.pi * np.sqrt(1.0 / 9.81)
    assert abs(result.summary["T"] - expected_T) < 0.01


def test_max_velocity_solvable(max_velocity_model):
    """Test that maximum velocity solves successfully."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(max_velocity_model)

    assert result.success
    assert "v_max" in result.summary


def test_max_velocity_correctness(max_velocity_model):
    """Test max velocity: v_max = A*ω."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(max_velocity_model)

    assert result.success
    # v_max = 0.5 * 10 = 5 m/s
    expected_v = 5.0
    assert abs(result.summary["v_max"] - expected_v) < 1e-6


def test_energy_solvable(energy_model):
    """Test that total energy solves successfully."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(energy_model)

    assert result.success
    assert "E" in result.summary


def test_energy_correctness(energy_model):
    """Test total energy: E = 0.5*k*A^2."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(energy_model)

    assert result.success
    # E = 0.5 * 100 * 0.5^2 = 12.5 J
    expected_E = 0.5 * 100.0 * (0.5 ** 2)
    assert abs(result.summary["E"] - expected_E) < 1e-6


def test_position_solvable(position_model):
    """Test that position calculation solves successfully."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(position_model)

    assert result.success
    assert "x" in result.summary


def test_position_correctness(position_model):
    """Test position: x(t) = A*cos(ωt + φ)."""
    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(position_model)

    assert result.success
    # At t=0, x = 1 * cos(0 + 0) = 1 m
    expected_x = 1.0
    assert abs(result.summary["x"] - expected_x) < 1e-6


# ============ Determinism Tests ============

def test_determinism_spring_period(spring_period_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsSimpleHarmonicMotionSolver()

    result1 = solver.solve(spring_period_model)
    result2 = solver.solve(spring_period_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_energy(energy_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsSimpleHarmonicMotionSolver()

    result1 = solver.solve(energy_model)
    result2 = solver.solve(energy_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

def test_error_zero_spring_constant():
    """Test error with zero spring constant."""
    model = ScientificModel(
        id="shm-error-k",
        domain="physics.simple_harmonic_motion",
        description="Zero spring constant",
        quantities=[
            Quantity(name="m", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=0.0, siUnit="N/m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="T", rhs="period_spring(m, k)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


def test_error_zero_length():
    """Test error with zero pendulum length."""
    model = ScientificModel(
        id="shm-error-length",
        domain="physics.simple_harmonic_motion",
        description="Zero length",
        quantities=[
            Quantity(name="L", value=0.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="T", rhs="period_pendulum(L, g)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsSimpleHarmonicMotionSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


# ============ Routing Test ============

def test_general_solver_routes_shm(spring_period_model):
    """Test that GeneralSolver correctly routes to PhysicsSimpleHarmonicMotionSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(spring_period_model)

    assert result.success
    assert "T" in result.summary
