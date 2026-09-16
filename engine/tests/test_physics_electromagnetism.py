"""Tests for electromagnetism solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_electromagnetism import PhysicsElectromagnetismSolver


@pytest.fixture
def coulomb_model():
    """Model for Coulomb's law force calculation."""
    return ScientificModel(
        id="em-coulomb",
        domain="physics.electromagnetism",
        description="Coulomb force",
        quantities=[
            Quantity(name="q1", value=1e-6, siUnit="C", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="q2", value=2e-6, siUnit="C", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.1, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k_e", value=8.99e9, siUnit="N*m^2/C^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="F", rhs="coulomb_force(q1, q2, r, k_e)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def electric_field_model():
    """Model for electric field calculation."""
    return ScientificModel(
        id="em-field",
        domain="physics.electromagnetism",
        description="Electric field",
        quantities=[
            Quantity(name="q", value=1e-6, siUnit="C", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.1, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k_e", value=8.99e9, siUnit="N*m^2/C^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E", rhs="electric_field_point_charge(q, r, k_e)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def ohms_law_model():
    """Model for Ohm's law voltage calculation."""
    return ScientificModel(
        id="em-ohms",
        domain="physics.electromagnetism",
        description="Ohm's law",
        quantities=[
            Quantity(name="I", value=2.0, siUnit="A", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=5.0, siUnit="Ohm", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="V", rhs="ohms_law_voltage(I, R)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def power_model():
    """Model for electrical power calculation."""
    return ScientificModel(
        id="em-power",
        domain="physics.electromagnetism",
        description="Electrical power",
        quantities=[
            Quantity(name="V", value=10.0, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="I", value=2.0, siUnit="A", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="P", rhs="power_electrical(V, I)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def capacitor_energy_model():
    """Model for capacitor energy calculation."""
    return ScientificModel(
        id="em-capacitor",
        domain="physics.electromagnetism",
        description="Capacitor energy",
        quantities=[
            Quantity(name="C", value=1e-6, siUnit="F", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="V", value=100.0, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="U", rhs="capacitor_energy(C, V)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_coulomb_force_solvable(coulomb_model):
    """Test that Coulomb force solves successfully."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(coulomb_model)

    assert result.success
    assert "F" in result.summary


def test_coulomb_force_correctness(coulomb_model):
    """Test Coulomb's law: F = k_e * |q1*q2| / r^2."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(coulomb_model)

    assert result.success
    # F = 8.99e9 * |1e-6 * 2e-6| / (0.1)^2 = 8.99e9 * 2e-12 / 0.01 = 1.798 N
    expected_F = 8.99e9 * abs(1e-6 * 2e-6) / (0.1 ** 2)
    assert abs(result.summary["F"] - expected_F) < 0.01


def test_electric_field_solvable(electric_field_model):
    """Test that electric field solves successfully."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(electric_field_model)

    assert result.success
    assert "E" in result.summary


def test_electric_field_correctness(electric_field_model):
    """Test electric field: E = k_e * |q| / r^2."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(electric_field_model)

    assert result.success
    # E = 8.99e9 * 1e-6 / (0.1)^2 = 8.99e5 N/C
    expected_E = 8.99e9 * abs(1e-6) / (0.1 ** 2)
    assert abs(result.summary["E"] - expected_E) < 1000.0


def test_ohms_law_solvable(ohms_law_model):
    """Test that Ohm's law solves successfully."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(ohms_law_model)

    assert result.success
    assert "V" in result.summary


def test_ohms_law_correctness(ohms_law_model):
    """Test Ohm's law: V = I * R."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(ohms_law_model)

    assert result.success
    # V = 2 * 5 = 10 V
    expected_V = 10.0
    assert abs(result.summary["V"] - expected_V) < 1e-6


def test_power_solvable(power_model):
    """Test that electrical power solves successfully."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(power_model)

    assert result.success
    assert "P" in result.summary


def test_power_correctness(power_model):
    """Test electrical power: P = V * I."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(power_model)

    assert result.success
    # P = 10 * 2 = 20 W
    expected_P = 20.0
    assert abs(result.summary["P"] - expected_P) < 1e-6


def test_capacitor_energy_solvable(capacitor_energy_model):
    """Test that capacitor energy solves successfully."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(capacitor_energy_model)

    assert result.success
    assert "U" in result.summary


def test_capacitor_energy_correctness(capacitor_energy_model):
    """Test capacitor energy: U = 0.5 * C * V^2."""
    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(capacitor_energy_model)

    assert result.success
    # U = 0.5 * 1e-6 * 100^2 = 0.005 J
    expected_U = 0.5 * 1e-6 * (100.0 ** 2)
    assert abs(result.summary["U"] - expected_U) < 1e-8


# ============ Determinism Tests ============

def test_determinism_coulomb(coulomb_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsElectromagnetismSolver()

    result1 = solver.solve(coulomb_model)
    result2 = solver.solve(coulomb_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_power(power_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsElectromagnetismSolver()

    result1 = solver.solve(power_model)
    result2 = solver.solve(power_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

def test_error_zero_distance():
    """Test error with zero distance."""
    model = ScientificModel(
        id="em-error-distance",
        domain="physics.electromagnetism",
        description="Zero distance",
        quantities=[
            Quantity(name="q", value=1e-6, siUnit="C", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k_e", value=8.99e9, siUnit="N*m^2/C^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E", rhs="electric_field_point_charge(q, r, k_e)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


def test_error_zero_resistance():
    """Test error with zero resistance."""
    model = ScientificModel(
        id="em-error-resistance",
        domain="physics.electromagnetism",
        description="Zero resistance",
        quantities=[
            Quantity(name="V", value=10.0, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=0.0, siUnit="Ohm", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="I", rhs="ohms_law_current(V, R)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsElectromagnetismSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


# ============ Routing Test ============

def test_general_solver_routes_electromagnetism(ohms_law_model):
    """Test that GeneralSolver correctly routes to PhysicsElectromagnetismSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(ohms_law_model)

    assert result.success
    assert "V" in result.summary
