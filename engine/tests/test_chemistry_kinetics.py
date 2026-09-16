"""Tests for kinetics solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.chemistry_kinetics import ChemistryKineticsSolver

@pytest.fixture
def zero_order_model():
    """Model for zero-order reaction concentration."""
    return ScientificModel(
        id="kinetics-zero-order",
        domain="chemistry.kinetics",
        description="Zero-order rate law",
        quantities=[
            Quantity(name="A0", value=1.0, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=0.05, siUnit="mol/(L*s)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=10.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="A", rhs="zero_order_concentration(A0, k, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def first_order_model():
    """Model for first-order reaction concentration."""
    return ScientificModel(
        id="kinetics-first-order",
        domain="chemistry.kinetics",
        description="First-order rate law",
        quantities=[
            Quantity(name="A0", value=1.0, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=0.1, siUnit="1/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=10.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="A", rhs="first_order_concentration(A0, k, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def second_order_model():
    """Model for second-order reaction concentration."""
    return ScientificModel(
        id="kinetics-second-order",
        domain="chemistry.kinetics",
        description="Second-order rate law",
        quantities=[
            Quantity(name="A0", value=1.0, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=0.01, siUnit="L/(mol*s)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=50.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="A", rhs="second_order_concentration(A0, k, t)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def arrhenius_model():
    """Model for Arrhenius rate constant calculation."""
    return ScientificModel(
        id="kinetics-arrhenius",
        domain="chemistry.kinetics",
        description="Arrhenius equation",
        quantities=[
            Quantity(name="A", value=1.0e13, siUnit="1/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="Ea", value=50000.0, siUnit="J/mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=8.314, siUnit="J/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=300.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="k", rhs="arrhenius_rate_constant(A, Ea, R, T)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

# ============ Correctness Tests ============

def test_zero_order_concentration_solvable(zero_order_model):
    """Test that zero-order concentration solves successfully."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(zero_order_model)

    assert result.success
    assert "A" in result.summary

def test_zero_order_concentration_correctness(zero_order_model):
    """Test zero-order rate law: [A] = [A]0 - k*t with A0=1, k=0.05, t=10."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(zero_order_model)

    assert result.success
    # Expected: [A] = 1.0 - 0.05*10 = 0.5 mol/L
    expected_A = 1.0 - 0.05 * 10.0
    assert abs(result.summary["A"] - expected_A) < 1e-6

def test_first_order_concentration_solvable(first_order_model):
    """Test that first-order concentration solves successfully."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(first_order_model)

    assert result.success
    assert "A" in result.summary

def test_first_order_concentration_correctness(first_order_model):
    """Test first-order rate law: [A] = [A]0 * exp(-k*t) with A0=1, k=0.1, t=10."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(first_order_model)

    assert result.success
    # Expected: [A] = 1.0 * exp(-0.1*10) = exp(-1) ≈ 0.3679
    expected_A = 1.0 * np.exp(-0.1 * 10.0)
    assert abs(result.summary["A"] - expected_A) < 1e-6

def test_second_order_concentration_solvable(second_order_model):
    """Test that second-order concentration solves successfully."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(second_order_model)

    assert result.success
    assert "A" in result.summary

def test_second_order_concentration_correctness(second_order_model):
    """Test second-order rate law: [A] = [A]0 / (1 + [A]0*k*t)."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(second_order_model)

    assert result.success
    # Expected: [A] = 1.0 / (1 + 1.0*0.01*50) = 1.0 / 1.5 ≈ 0.6667
    expected_A = 1.0 / (1.0 + 1.0 * 0.01 * 50.0)
    assert abs(result.summary["A"] - expected_A) < 1e-6

def test_arrhenius_rate_constant_solvable(arrhenius_model):
    """Test that Arrhenius rate constant solves successfully."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(arrhenius_model)

    assert result.success
    assert "k" in result.summary

def test_arrhenius_rate_constant_correctness(arrhenius_model):
    """Test Arrhenius equation: k = A * exp(-Ea/(R*T))."""
    solver = ChemistryKineticsSolver()
    result = solver.solve(arrhenius_model)

    assert result.success
    # Expected: k = 1.0e13 * exp(-50000 / (8.314 * 300))
    expected_k = 1.0e13 * np.exp(-50000.0 / (8.314 * 300.0))
    assert abs(result.summary["k"] - expected_k) < expected_k * 1e-5

# ============ Determinism Tests ============

def test_determinism_zero_order(zero_order_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryKineticsSolver()

    result1 = solver.solve(zero_order_model)
    result2 = solver.solve(zero_order_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

def test_determinism_first_order(first_order_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryKineticsSolver()

    result1 = solver.solve(first_order_model)
    result2 = solver.solve(first_order_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

def test_determinism_arrhenius(arrhenius_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryKineticsSolver()

    result1 = solver.solve(arrhenius_model)
    result2 = solver.solve(arrhenius_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

# ============ Error Path Tests ============

def test_error_zero_order_negative_k():
    """Test error when rate constant k is negative."""
    model = ScientificModel(
        id="kinetics-error-neg-k",
        domain="chemistry.kinetics",
        description="Zero-order with negative k",
        quantities=[
            Quantity(name="A0", value=1.0, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="k", value=-0.05, siUnit="mol/(L*s)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="t", value=10.0, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="A", rhs="zero_order_half_life(A0, k)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ChemistryKineticsSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None

# ============ Routing Test ============

def test_general_solver_routes_kinetics(first_order_model):
    """Test that GeneralSolver correctly routes to ChemistryKineticsSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(first_order_model)

    assert result.success
    assert "A" in result.summary
