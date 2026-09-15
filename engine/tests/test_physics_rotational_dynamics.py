"""Tests for rotational dynamics solver."""
import math
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_rotational_dynamics import PhysicsRotationalDynamicsSolver


@pytest.fixture
def torque_model():
    """Model for torque calculation: τ = F × r × sin(θ)."""
    return ScientificModel(
        id="rotdyn-torque",
        domain="physics.rotational_dynamics",
        description="Torque calculation",
        quantities=[
            Quantity(name="F", value=10.0, siUnit="N", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="theta", value=90.0, siUnit="deg", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="tau", rhs="torque(F, r, theta)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def moment_of_inertia_disk_model():
    """Model for disk moment of inertia: I = ½ × m × r²."""
    return ScientificModel(
        id="rotdyn-disk-moi",
        domain="physics.rotational_dynamics",
        description="Disk moment of inertia",
        quantities=[
            Quantity(name="m", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="I", rhs="moment_of_inertia_disk(m, r)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def rotational_kinetic_energy_model():
    """Model for rotational kinetic energy: KE = ½ × I × ω²."""
    return ScientificModel(
        id="rotdyn-rot-ke",
        domain="physics.rotational_dynamics",
        description="Rotational kinetic energy",
        quantities=[
            Quantity(name="I", value=0.25, siUnit="kg*m**2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="omega", value=10.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="KE", rhs="rotational_kinetic_energy(I, omega)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def angular_acceleration_model():
    """Model for angular acceleration: α = τ / I."""
    return ScientificModel(
        id="rotdyn-angular-accel",
        domain="physics.rotational_dynamics",
        description="Angular acceleration",
        quantities=[
            Quantity(name="tau", value=5.0, siUnit="N*m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="I", value=0.25, siUnit="kg*m**2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="alpha", rhs="angular_acceleration(tau, I)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def rolling_velocity_model():
    """Model for rolling without slipping: v = ω × r."""
    return ScientificModel(
        id="rotdyn-rolling-vel",
        domain="physics.rotational_dynamics",
        description="Rolling velocity",
        quantities=[
            Quantity(name="omega", value=20.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v", rhs="rolling_without_slipping_velocity(omega, r)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_torque_solvable(torque_model):
    """Test that torque solves successfully."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(torque_model)

    assert result.success
    assert "tau" in result.summary


def test_torque_correctness(torque_model):
    """Test torque: τ = F × r × sin(θ) with F=10, r=0.5, θ=90°."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(torque_model)

    assert result.success
    # Expected: τ = 10 × 0.5 × sin(90°) = 10 × 0.5 × 1 = 5 N⋅m
    expected_tau = 10.0 * 0.5 * math.sin(math.radians(90.0))
    assert abs(result.summary["tau"] - expected_tau) < 1e-6


def test_moment_of_inertia_disk_solvable(moment_of_inertia_disk_model):
    """Test that disk MOI solves successfully."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(moment_of_inertia_disk_model)

    assert result.success
    assert "I" in result.summary


def test_moment_of_inertia_disk_correctness(moment_of_inertia_disk_model):
    """Test disk MOI: I = ½ × m × r² with m=2, r=0.5."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(moment_of_inertia_disk_model)

    assert result.success
    # Expected: I = 0.5 × 2 × 0.5² = 0.5 × 2 × 0.25 = 0.25 kg⋅m²
    expected_I = 0.5 * 2.0 * (0.5**2)
    assert abs(result.summary["I"] - expected_I) < 1e-6


def test_rotational_kinetic_energy_solvable(rotational_kinetic_energy_model):
    """Test that rotational kinetic energy solves successfully."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(rotational_kinetic_energy_model)

    assert result.success
    assert "KE" in result.summary


def test_rotational_kinetic_energy_correctness(rotational_kinetic_energy_model):
    """Test rotational KE: KE = ½ × I × ω² with I=0.25, ω=10."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(rotational_kinetic_energy_model)

    assert result.success
    # Expected: KE = 0.5 × 0.25 × 10² = 0.5 × 0.25 × 100 = 12.5 J
    expected_KE = 0.5 * 0.25 * (10.0**2)
    assert abs(result.summary["KE"] - expected_KE) < 1e-6


def test_angular_acceleration_solvable(angular_acceleration_model):
    """Test that angular acceleration solves successfully."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(angular_acceleration_model)

    assert result.success
    assert "alpha" in result.summary


def test_angular_acceleration_correctness(angular_acceleration_model):
    """Test angular acceleration: α = τ / I with τ=5, I=0.25."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(angular_acceleration_model)

    assert result.success
    # Expected: α = 5 / 0.25 = 20 rad/s²
    expected_alpha = 5.0 / 0.25
    assert abs(result.summary["alpha"] - expected_alpha) < 1e-6


def test_rolling_velocity_solvable(rolling_velocity_model):
    """Test that rolling velocity solves successfully."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(rolling_velocity_model)

    assert result.success
    assert "v" in result.summary


def test_rolling_velocity_correctness(rolling_velocity_model):
    """Test rolling velocity: v = ω × r with ω=20, r=0.5."""
    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(rolling_velocity_model)

    assert result.success
    # Expected: v = 20 × 0.5 = 10 m/s
    expected_v = 20.0 * 0.5
    assert abs(result.summary["v"] - expected_v) < 1e-6


def test_moment_of_inertia_point_mass_correctness():
    """Test point mass MOI: I = m × r²."""
    model = ScientificModel(
        id="rotdyn-point-mass",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="m", value=3.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=2.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="I", rhs="moment_of_inertia_point_mass(m, r)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: I = 3 × 2² = 12 kg⋅m²
    expected_I = 3.0 * (2.0**2)
    assert abs(result.summary["I"] - expected_I) < 1e-6


def test_moment_of_inertia_sphere_correctness():
    """Test solid sphere MOI: I = ⅖ × m × r²."""
    model = ScientificModel(
        id="rotdyn-sphere",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="m", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="I", rhs="moment_of_inertia_sphere_solid(m, r)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: I = 0.4 × 2 × 0.5² = 0.2 kg⋅m²
    expected_I = 0.4 * 2.0 * (0.5**2)
    assert abs(result.summary["I"] - expected_I) < 1e-6


def test_moment_of_inertia_rod_correctness():
    """Test rod MOI (center): I = 1/12 × m × L²."""
    model = ScientificModel(
        id="rotdyn-rod",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="m", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="I", rhs="moment_of_inertia_rod_center(m, L)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: I = (1/12) × 2 × 1² = 1/6 ≈ 0.16667 kg⋅m²
    expected_I = 2.0 * (1.0**2) / 12.0
    assert abs(result.summary["I"] - expected_I) < 1e-6


def test_angular_momentum_correctness():
    """Test angular momentum: L = I × ω."""
    model = ScientificModel(
        id="rotdyn-ang-mom",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="I", value=0.5, siUnit="kg*m**2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="omega", value=4.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="L", rhs="angular_momentum(I, omega)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: L = 0.5 × 4 = 2 kg⋅m²/s
    expected_L = 0.5 * 4.0
    assert abs(result.summary["L"] - expected_L) < 1e-6


def test_angular_velocity_from_time_correctness():
    """Test angular velocity from time: ω = ω₀ + α × t."""
    model = ScientificModel(
        id="rotdyn-ang-vel-time",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="omega0", value=5.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="alpha", value=2.0, siUnit="rad/s**2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=3.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="omega", rhs="angular_velocity_from_time(omega0, alpha, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: ω = 5 + 2 × 3 = 11 rad/s
    expected_omega = 5.0 + 2.0 * 3.0
    assert abs(result.summary["omega"] - expected_omega) < 1e-6


def test_angular_displacement_correctness():
    """Test angular displacement: θ = ω₀ × t + ½ × α × t²."""
    model = ScientificModel(
        id="rotdyn-ang-disp",
        domain="physics.rotational_dynamics",
        quantities=[
            Quantity(name="omega0", value=0.0, siUnit="rad/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="alpha", value=4.0, siUnit="rad/s**2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=2.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta", rhs="angular_displacement(omega0, alpha, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsRotationalDynamicsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: θ = 0 + 0.5 × 4 × 2² = 0.5 × 4 × 4 = 8 rad
    expected_theta = 0.0 + 0.5 * 4.0 * (2.0**2)
    assert abs(result.summary["theta"] - expected_theta) < 1e-6


# ============ Determinism Tests ============

def test_determinism_torque(torque_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsRotationalDynamicsSolver()

    result1 = solver.solve(torque_model)
    result2 = solver.solve(torque_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_moment_of_inertia(moment_of_inertia_disk_model):
    """Test determinism for moment of inertia."""
    solver = PhysicsRotationalDynamicsSolver()

    result1 = solver.solve(moment_of_inertia_disk_model)
    result2 = solver.solve(moment_of_inertia_disk_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_rotational_kinetic_energy(rotational_kinetic_energy_model):
    """Test determinism for rotational kinetic energy."""
    solver = PhysicsRotationalDynamicsSolver()

    result1 = solver.solve(rotational_kinetic_energy_model)
    result2 = solver.solve(rotational_kinetic_energy_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("torque(F, r, theta)", {"F": 10, "r": -0.5, "theta": 90}, "Lever arm r must be non-negative"),
        ("moment_of_inertia_point_mass(m, r)", {"m": -2, "r": 0.5}, "Mass m must be non-negative"),
        ("moment_of_inertia_disk(m, r)", {"m": 2, "r": -0.5}, "Radius r must be non-negative"),
        ("angular_acceleration(tau, I)", {"tau": 5, "I": 0}, "Moment of inertia I must be greater than 0"),
        ("angular_velocity_from_time(omega0, alpha, t)", {"omega0": 5, "alpha": 2, "t": -1}, "Time t must be non-negative"),
        ("angular_displacement(omega0, alpha, t)", {"omega0": 0, "alpha": 4, "t": -2}, "Time t must be non-negative"),
        ("rolling_without_slipping_velocity(omega, r)", {"omega": 20, "r": -0.5}, "Radius r must be non-negative"),
    ],
)
def test_rotational_dynamics_validation(operation, quantities, expected_error):
    """Test error handling for invalid rotational dynamics parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    model = ScientificModel(
        id="rotdyn-error-test",
        domain="physics.rotational_dynamics",
        quantities=model_quantities,
        equations=[
            Equation(lhs="result", rhs=operation, type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = PhysicsRotationalDynamicsSolver().solve(model)

    assert not result.success
    assert expected_error in result.error


# ============ Routing Tests ============

def test_general_solver_routes_rotational_dynamics(torque_model):
    """Test that GeneralSolver routes to rotational dynamics solver."""
    result = GeneralSolver().solve(torque_model)

    assert result.success
    assert "tau" in result.summary
