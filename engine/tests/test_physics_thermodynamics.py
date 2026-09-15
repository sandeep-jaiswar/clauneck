"""Tests for thermodynamics solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_thermodynamics import PhysicsThermodynamicsSolver


@pytest.fixture
def thermodynamics_model():
    """Model for ideal gas pressure calculation: P = nRT/V."""
    return ScientificModel(
        id="thermo-ideal-gas",
        domain="physics.thermodynamics",
        description="Ideal gas pressure",
        quantities=[
            Quantity(name="n", value=1.0, siUnit="mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=8.314, siUnit="J/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=300.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="V", value=0.024, siUnit="m^3", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="P", rhs="ideal_gas_pressure(n, R, T, V)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def carnot_efficiency_model():
    """Model for Carnot cycle efficiency calculation."""
    return ScientificModel(
        id="thermo-carnot",
        domain="physics.thermodynamics",
        description="Carnot efficiency",
        quantities=[
            Quantity(name="T_hot", value=600.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T_cold", value=300.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="efficiency", rhs="carnot_efficiency(T_hot, T_cold)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def work_isothermal_model():
    """Model for isothermal work calculation."""
    return ScientificModel(
        id="thermo-work",
        domain="physics.thermodynamics",
        description="Isothermal work",
        quantities=[
            Quantity(name="n", value=1.0, siUnit="mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=8.314, siUnit="J/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=300.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="V1", value=0.022, siUnit="m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="V2", value=0.044, siUnit="m^3", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="W", rhs="work_isothermal(n, R, T, V1, V2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_ideal_gas_pressure_solvable(thermodynamics_model):
    """Test that ideal gas pressure solves successfully."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(thermodynamics_model)
    
    assert result.success
    assert "P" in result.summary


def test_ideal_gas_pressure_correctness(thermodynamics_model):
    """Test ideal gas law: P = nRT/V with n=1, R=8.314, T=300, V=0.024."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(thermodynamics_model)
    
    assert result.success
    # Expected: P = 1 * 8.314 * 300 / 0.024 = 103925 Pa
    expected_P = 1.0 * 8.314 * 300.0 / 0.024
    assert abs(result.summary["P"] - expected_P) < 1.0  # Pa precision


def test_carnot_efficiency_solvable(carnot_efficiency_model):
    """Test that Carnot efficiency solves successfully."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(carnot_efficiency_model)
    
    assert result.success
    assert "efficiency" in result.summary


def test_carnot_efficiency_correctness(carnot_efficiency_model):
    """Test Carnot efficiency: η = 1 - T_cold/T_hot with T_hot=600, T_cold=300."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(carnot_efficiency_model)
    
    assert result.success
    # Expected: η = 1 - 300/600 = 0.5
    expected_eta = 1.0 - 300.0 / 600.0
    assert abs(result.summary["efficiency"] - expected_eta) < 1e-6


def test_work_isothermal_solvable(work_isothermal_model):
    """Test that isothermal work solves successfully."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(work_isothermal_model)
    
    assert result.success
    assert "W" in result.summary


def test_work_isothermal_correctness(work_isothermal_model):
    """Test isothermal work: W = nRT*ln(V2/V1)."""
    solver = PhysicsThermodynamicsSolver()
    result = solver.solve(work_isothermal_model)
    
    assert result.success
    # Expected: W = 1 * 8.314 * 300 * ln(0.044/0.022) = 1 * 8.314 * 300 * ln(2)
    expected_W = 1.0 * 8.314 * 300.0 * np.log(0.044 / 0.022)
    assert abs(result.summary["W"] - expected_W) < 1.0  # J precision


# ============ Determinism Tests ============

def test_determinism_ideal_gas_pressure(thermodynamics_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsThermodynamicsSolver()
    
    result1 = solver.solve(thermodynamics_model)
    result2 = solver.solve(thermodynamics_model)
    
    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_carnot_efficiency(carnot_efficiency_model):
    """Test determinism for Carnot efficiency."""
    solver = PhysicsThermodynamicsSolver()
    
    result1 = solver.solve(carnot_efficiency_model)
    result2 = solver.solve(carnot_efficiency_model)
    
    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("ideal_gas_pressure(n, R, T, V)", {"n": 1.0, "R": 8.314, "T": 300, "V": 0}, "Volume V must be greater than 0"),
        ("ideal_gas_volume(n, R, T, P)", {"n": 1.0, "R": 8.314, "T": 300, "P": 0}, "Pressure P must be greater than 0"),
        ("carnot_efficiency(T_hot, T_cold)", {"T_hot": 300, "T_cold": 300}, "T_cold must be less than T_hot"),
        ("carnot_efficiency(T_hot, T_cold)", {"T_hot": -100, "T_cold": 50}, "Temperatures must be positive"),
    ],
)
def test_thermodynamics_validation(thermodynamics_model, operation, quantities, expected_error):
    """Test error handling for invalid thermodynamic parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    equation = thermodynamics_model.equations[0].model_copy(update={"rhs": operation})
    model = thermodynamics_model.model_copy(update={
        "quantities": model_quantities,
        "equations": [equation],
    })

    result = PhysicsThermodynamicsSolver().solve(model)

    assert not result.success
    assert expected_error in result.error


# ============ Routing Tests ============

def test_general_solver_routes_thermodynamics(thermodynamics_model):
    """Test that GeneralSolver routes to thermodynamics solver."""
    result = GeneralSolver().solve(thermodynamics_model)
    
    assert result.success
    assert "P" in result.summary
