"""Tests for chemical equilibrium solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.chemistry_equilibrium import ChemistryEquilibriumSolver


@pytest.fixture
def reaction_quotient_model():
    """Model for reaction quotient calculation."""
    return ScientificModel(
        id="eq-quotient",
        domain="chemistry.equilibrium",
        description="Reaction quotient Q",
        quantities=[
            Quantity(name="conc_products", value=[2.0], siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="coeff_products", value=[1.0], siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="conc_reactants", value=[0.5], siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="coeff_reactants", value=[1.0], siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="Q", rhs="reaction_quotient(conc_products, coeff_products, conc_reactants, coeff_reactants)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def kp_kc_model():
    """Model for Kp from Kc conversion."""
    return ScientificModel(
        id="eq-kp-kc",
        domain="chemistry.equilibrium",
        description="Kp from Kc",
        quantities=[
            Quantity(name="Kc", value=1.0, siUnit="mol^2/L^2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="delta_n", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=0.08206, siUnit="L*atm/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=298.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="Kp", rhs="kp_from_kc(Kc, delta_n, R, T)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def le_chatelier_model():
    """Model for Le Chatelier direction prediction."""
    return ScientificModel(
        id="eq-le-chatelier",
        domain="chemistry.equilibrium",
        description="Le Chatelier direction",
        quantities=[
            Quantity(name="Q", value=0.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="K", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="direction", rhs="le_chatelier_direction(Q, K)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_reaction_quotient_solvable(reaction_quotient_model):
    """Test that reaction quotient solves successfully."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(reaction_quotient_model)

    assert result.success
    assert "Q" in result.summary


def test_reaction_quotient_correctness(reaction_quotient_model):
    """Test Q calculation: [products]^coeff / [reactants]^coeff."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(reaction_quotient_model)

    assert result.success
    # Q = [2.0]^1 / [0.5]^1 = 4.0
    expected_Q = 4.0
    assert abs(result.summary["Q"] - expected_Q) < 1e-6


def test_kp_kc_solvable(kp_kc_model):
    """Test that Kp from Kc conversion solves successfully."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(kp_kc_model)

    assert result.success
    assert "Kp" in result.summary


def test_kp_kc_correctness(kp_kc_model):
    """Test Kp = Kc * (R*T)^(delta_n)."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(kp_kc_model)

    assert result.success
    # Kp = 1.0 * (0.08206 * 298)^1 = 24.46
    expected_Kp = 1.0 * ((0.08206 * 298.0) ** 1.0)
    assert abs(result.summary["Kp"] - expected_Kp) < 0.1


def test_le_chatelier_solvable(le_chatelier_model):
    """Test that Le Chatelier direction solves successfully."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(le_chatelier_model)

    assert result.success
    assert "direction" in result.summary


def test_le_chatelier_correctness(le_chatelier_model):
    """Test Le Chatelier direction: Q < K -> forward."""
    solver = ChemistryEquilibriumSolver()
    result = solver.solve(le_chatelier_model)

    assert result.success
    # Q=0.5, K=2.0 -> Q < K -> forward
    assert result.summary["direction"] == "forward"


# ============ Determinism Tests ============

def test_determinism_reaction_quotient(reaction_quotient_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryEquilibriumSolver()

    result1 = solver.solve(reaction_quotient_model)
    result2 = solver.solve(reaction_quotient_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_le_chatelier(le_chatelier_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryEquilibriumSolver()

    result1 = solver.solve(le_chatelier_model)
    result2 = solver.solve(le_chatelier_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

def test_error_negative_concentration():
    """Test error with negative concentration."""
    model = ScientificModel(
        id="eq-error-neg",
        domain="chemistry.equilibrium",
        description="Negative concentration",
        quantities=[
            Quantity(name="conc_products", value=[2.0], siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="coeff_products", value=[1.0], siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="conc_reactants", value=[-0.5], siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="coeff_reactants", value=[1.0], siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="Q", rhs="reaction_quotient(conc_products, coeff_products, conc_reactants, coeff_reactants)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ChemistryEquilibriumSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


# ============ Routing Test ============

def test_general_solver_routes_equilibrium(reaction_quotient_model):
    """Test that GeneralSolver correctly routes to ChemistryEquilibriumSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(reaction_quotient_model)

    assert result.success
    assert "Q" in result.summary
