"""Tests for thermochemistry solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.chemistry_thermochemistry import ChemistryThermochemistrySolver


@pytest.fixture
def hess_law_model():
    """Model for Hess's law calculation."""
    return ScientificModel(
        id="thermo-hess",
        domain="chemistry.thermochemistry",
        description="Hess's law",
        quantities=[
            Quantity(name="delta_h_vec", value=[-100.0, -200.0], siUnit="kJ/mol", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_H_rxn", rhs="hess_law_sum(delta_h_vec)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def calorimetry_model():
    """Model for calorimetry heat calculation."""
    return ScientificModel(
        id="thermo-calorimetry",
        domain="chemistry.thermochemistry",
        description="Calorimetry",
        quantities=[
            Quantity(name="m", value=100.0, siUnit="g", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=4.18, siUnit="J/(g*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="delta_T", value=10.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="q", rhs="calorimetry_heat(m, c, delta_T)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def bond_energy_model():
    """Model for bond energy enthalpy calculation."""
    return ScientificModel(
        id="thermo-bond-energy",
        domain="chemistry.thermochemistry",
        description="Bond energy enthalpy",
        quantities=[
            Quantity(name="be_broken_vec", value=[400.0, 300.0], siUnit="kJ/mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="be_formed_vec", value=[500.0, 250.0], siUnit="kJ/mol", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_H", rhs="bond_energy_enthalpy(be_broken_vec, be_formed_vec)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_hess_law_solvable(hess_law_model):
    """Test that Hess's law solves successfully."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(hess_law_model)

    assert result.success
    assert "delta_H_rxn" in result.summary


def test_hess_law_correctness(hess_law_model):
    """Test Hess's law: sum all ΔH values."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(hess_law_model)

    assert result.success
    # ΔH_rxn = -100 + -200 = -300 kJ/mol
    expected_delta_H = -300.0
    assert abs(result.summary["delta_H_rxn"] - expected_delta_H) < 1.0


def test_calorimetry_solvable(calorimetry_model):
    """Test that calorimetry heat calculation solves successfully."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(calorimetry_model)

    assert result.success
    assert "q" in result.summary


def test_calorimetry_correctness(calorimetry_model):
    """Test calorimetry: q = m*c*ΔT."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(calorimetry_model)

    assert result.success
    # q = 100 * 4.18 * 10 = 4180 J
    expected_q = 100.0 * 4.18 * 10.0
    assert abs(result.summary["q"] - expected_q) < 10.0


def test_bond_energy_solvable(bond_energy_model):
    """Test that bond energy calculation solves successfully."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(bond_energy_model)

    assert result.success
    assert "delta_H" in result.summary


def test_bond_energy_correctness(bond_energy_model):
    """Test bond energy: ΔH = Σ(BE_broken) - Σ(BE_formed)."""
    solver = ChemistryThermochemistrySolver()
    result = solver.solve(bond_energy_model)

    assert result.success
    # ΔH = (400 + 300) - (500 + 250) = 700 - 750 = -50 kJ/mol
    expected_delta_H = (400.0 + 300.0) - (500.0 + 250.0)
    assert abs(result.summary["delta_H"] - expected_delta_H) < 1.0


# ============ Determinism Tests ============

def test_determinism_hess_law(hess_law_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryThermochemistrySolver()

    result1 = solver.solve(hess_law_model)
    result2 = solver.solve(hess_law_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_calorimetry(calorimetry_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryThermochemistrySolver()

    result1 = solver.solve(calorimetry_model)
    result2 = solver.solve(calorimetry_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

def test_error_negative_moles():
    """Test error with negative moles."""
    model = ScientificModel(
        id="thermo-error-moles",
        domain="chemistry.thermochemistry",
        description="Negative moles",
        quantities=[
            Quantity(name="delta_H", value=-100.0, siUnit="kJ/mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="moles", value=-1.0, siUnit="mol", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="H_per_mol", rhs="enthalpy_per_mole(delta_H, moles)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ChemistryThermochemistrySolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


# ============ Routing Test ============

def test_general_solver_routes_thermochemistry(calorimetry_model):
    """Test that GeneralSolver correctly routes to ChemistryThermochemistrySolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(calorimetry_model)

    assert result.success
    assert "q" in result.summary
