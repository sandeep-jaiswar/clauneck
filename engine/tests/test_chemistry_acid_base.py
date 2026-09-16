"""Tests for acid-base equilibrium solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.chemistry_acid_base import ChemistryAcidBaseSolver


@pytest.fixture
def ph_model():
    """Model for pH calculation from H+ concentration."""
    return ScientificModel(
        id="acid-base-ph",
        domain="chemistry.acid_base_equilibrium",
        description="pH from H+ concentration",
        quantities=[
            Quantity(name="h_conc", value=1e-7, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pH", rhs="ph_from_h(h_conc)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def poh_model():
    """Model for pOH calculation from OH- concentration."""
    return ScientificModel(
        id="acid-base-poh",
        domain="chemistry.acid_base_equilibrium",
        description="pOH from OH- concentration",
        quantities=[
            Quantity(name="oh_conc", value=1e-7, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pOH", rhs="poh_from_oh(oh_conc)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def henderson_hasselbalch_model():
    """Model for Henderson-Hasselbalch pH calculation."""
    return ScientificModel(
        id="acid-base-hh",
        domain="chemistry.acid_base_equilibrium",
        description="Henderson-Hasselbalch equation",
        quantities=[
            Quantity(name="pKa", value=4.76, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="base_conc", value=0.1, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="acid_conc", value=0.1, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pH", rhs="henderson_hasselbalch(pKa, base_conc, acid_conc)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def weak_acid_model():
    """Model for weak acid pH calculation."""
    return ScientificModel(
        id="acid-base-weak",
        domain="chemistry.acid_base_equilibrium",
        description="Weak acid pH",
        quantities=[
            Quantity(name="Ka", value=1.8e-5, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="C0", value=0.1, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pH", rhs="weak_acid_ph(Ka, C0)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_ph_from_h_solvable(ph_model):
    """Test that pH calculation solves successfully."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(ph_model)

    assert result.success
    assert "pH" in result.summary


def test_ph_from_h_correctness(ph_model):
    """Test pH = -log10([H+]) with [H+] = 1e-7."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(ph_model)

    assert result.success
    # Expected: pH = -log10(1e-7) = 7
    expected_pH = 7.0
    assert abs(result.summary["pH"] - expected_pH) < 1e-6


def test_poh_from_oh_solvable(poh_model):
    """Test that pOH calculation solves successfully."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(poh_model)

    assert result.success
    assert "pOH" in result.summary


def test_poh_from_oh_correctness(poh_model):
    """Test pOH = -log10([OH-]) with [OH-] = 1e-7."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(poh_model)

    assert result.success
    # Expected: pOH = -log10(1e-7) = 7
    expected_pOH = 7.0
    assert abs(result.summary["pOH"] - expected_pOH) < 1e-6


def test_henderson_hasselbalch_solvable(henderson_hasselbalch_model):
    """Test that Henderson-Hasselbalch equation solves successfully."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(henderson_hasselbalch_model)

    assert result.success
    assert "pH" in result.summary


def test_henderson_hasselbalch_correctness(henderson_hasselbalch_model):
    """Test Henderson-Hasselbalch: pH = pKa + log10([base]/[acid]) with equal conc."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(henderson_hasselbalch_model)

    assert result.success
    # When [base] = [acid], pH = pKa
    expected_pH = 4.76
    assert abs(result.summary["pH"] - expected_pH) < 1e-6


def test_weak_acid_ph_solvable(weak_acid_model):
    """Test that weak acid pH calculation solves successfully."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(weak_acid_model)

    assert result.success
    assert "pH" in result.summary


def test_weak_acid_ph_correctness(weak_acid_model):
    """Test weak acid pH calculation."""
    solver = ChemistryAcidBaseSolver()
    result = solver.solve(weak_acid_model)

    assert result.success
    # pH should be between 2-3 for Ka=1.8e-5, C0=0.1
    pH_result = result.summary["pH"]
    assert 2.0 < pH_result < 3.0


# ============ Determinism Tests ============

def test_determinism_ph(ph_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryAcidBaseSolver()

    result1 = solver.solve(ph_model)
    result2 = solver.solve(ph_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_henderson_hasselbalch(henderson_hasselbalch_model):
    """Test determinism: solving twice produces identical results."""
    solver = ChemistryAcidBaseSolver()

    result1 = solver.solve(henderson_hasselbalch_model)
    result2 = solver.solve(henderson_hasselbalch_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

def test_error_negative_h_concentration():
    """Test error when H+ concentration is negative."""
    model = ScientificModel(
        id="acid-base-error-h",
        domain="chemistry.acid_base_equilibrium",
        description="Negative H+ concentration",
        quantities=[
            Quantity(name="h_conc", value=-1e-7, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pH", rhs="ph_from_h(h_conc)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ChemistryAcidBaseSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


def test_error_negative_oh_concentration():
    """Test error when OH- concentration is negative."""
    model = ScientificModel(
        id="acid-base-error-oh",
        domain="chemistry.acid_base_equilibrium",
        description="Negative OH- concentration",
        quantities=[
            Quantity(name="oh_conc", value=-1e-7, siUnit="mol/L", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="pOH", rhs="poh_from_oh(oh_conc)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ChemistryAcidBaseSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None


# ============ Routing Test ============

def test_general_solver_routes_acid_base(ph_model):
    """Test that GeneralSolver correctly routes to ChemistryAcidBaseSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(ph_model)

    assert result.success
    assert "pH" in result.summary
