"""Tests for collisions solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_collisions import PhysicsCollisionsSolver

@pytest.fixture
def elastic_collision_model():
    """Model for elastic collision."""
    return ScientificModel(
        id="collision-elastic",
        domain="physics.collisions",
        description="Elastic collision",
        quantities=[
            Quantity(name="m1", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v1", value=4.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m2", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v2", value=0.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="velocities", rhs="elastic_1d_final_velocities(m1, v1, m2, v2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def inelastic_collision_model():
    """Model for perfectly inelastic collision."""
    return ScientificModel(
        id="collision-inelastic",
        domain="physics.collisions",
        description="Inelastic collision",
        quantities=[
            Quantity(name="m1", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v1", value=4.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m2", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v2", value=0.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v_final", rhs="inelastic_1d_final_velocity(m1, v1, m2, v2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def momentum_model():
    """Model for momentum calculation."""
    return ScientificModel(
        id="collision-momentum",
        domain="physics.collisions",
        description="Momentum",
        quantities=[
            Quantity(name="m", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=5.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="p", rhs="momentum(m, v)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def kinetic_energy_model():
    """Model for kinetic energy calculation."""
    return ScientificModel(
        id="collision-ke",
        domain="physics.collisions",
        description="Kinetic energy",
        quantities=[
            Quantity(name="m", value=2.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=5.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="KE", rhs="kinetic_energy(m, v)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

# ============ Correctness Tests ============

def test_elastic_collision_solvable(elastic_collision_model):
    """Test that elastic collision solves successfully."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(elastic_collision_model)

    assert result.success
    assert "velocities_v1_final" in result.summary

def test_elastic_collision_correctness(elastic_collision_model):
    """Test elastic collision formula."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(elastic_collision_model)

    assert result.success
    v1_final = result.summary.get("velocities_v1_final")
    # For m1=2, v1=4, m2=1, v2=0:
    # v1_f = (2-1)*4 + 0 / 3 = 4/3 m/s
    # v2_f = (1-2)*0 + 2*2*4 / 3 = 16/3 m/s
    assert v1_final is not None
    assert "velocities_v2_final" in result.summary
    assert 1.0 < v1_final < 2.0

def test_inelastic_collision_solvable(inelastic_collision_model):
    """Test that inelastic collision solves successfully."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(inelastic_collision_model)

    assert result.success
    assert "v_final" in result.summary

def test_inelastic_collision_correctness(inelastic_collision_model):
    """Test inelastic collision: v_final = (m1*v1 + m2*v2)/(m1+m2)."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(inelastic_collision_model)

    assert result.success
    # v_final = (2*4 + 1*0) / 3 = 8/3 ≈ 2.667 m/s
    expected_v = (2.0 * 4.0 + 1.0 * 0.0) / 3.0
    assert abs(result.summary["v_final"] - expected_v) < 1e-6

def test_momentum_solvable(momentum_model):
    """Test that momentum solves successfully."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(momentum_model)

    assert result.success
    assert "p" in result.summary

def test_momentum_correctness(momentum_model):
    """Test momentum: p = m*v."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(momentum_model)

    assert result.success
    # p = 2.0 * 5.0 = 10.0 kg*m/s
    expected_p = 10.0
    assert abs(result.summary["p"] - expected_p) < 1e-6

def test_kinetic_energy_solvable(kinetic_energy_model):
    """Test that kinetic energy solves successfully."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(kinetic_energy_model)

    assert result.success
    assert "KE" in result.summary

def test_kinetic_energy_correctness(kinetic_energy_model):
    """Test kinetic energy: KE = 0.5*m*v^2."""
    solver = PhysicsCollisionsSolver()
    result = solver.solve(kinetic_energy_model)

    assert result.success
    # KE = 0.5 * 2.0 * 5.0^2 = 25 J
    expected_KE = 25.0
    assert abs(result.summary["KE"] - expected_KE) < 1e-6

# ============ Determinism Tests ============

def test_determinism_elastic(elastic_collision_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsCollisionsSolver()

    result1 = solver.solve(elastic_collision_model)
    result2 = solver.solve(elastic_collision_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

def test_determinism_momentum(momentum_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsCollisionsSolver()

    result1 = solver.solve(momentum_model)
    result2 = solver.solve(momentum_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

# ============ Error Path Tests ============

def test_error_zero_total_mass():
    """Test error when total mass is zero."""
    model = ScientificModel(
        id="collision-error-mass",
        domain="physics.collisions",
        description="Zero total mass",
        quantities=[
            Quantity(name="m1", value=0.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v1", value=4.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m2", value=0.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v2", value=0.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v_final", rhs="inelastic_1d_final_velocity(m1, v1, m2, v2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsCollisionsSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None

# ============ Routing Test ============

def test_general_solver_routes_collisions(momentum_model):
    """Test that GeneralSolver correctly routes to PhysicsCollisionsSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(momentum_model)

    assert result.success
    assert "p" in result.summary
