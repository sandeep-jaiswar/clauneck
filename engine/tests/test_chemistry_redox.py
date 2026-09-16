"""Tests for redox reactions solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.chemistry_redox import ChemistryRedoxSolver

@pytest.fixture
def cell_potential_model():
    """Model for cell potential calculation."""
    return ScientificModel(
        id="redox-cell-potential",
        domain="chemistry.redox_reactions",
        description="Cell potential",
        quantities=[
            Quantity(name="E_cathode", value=0.8, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="E_anode", value=-0.4, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E_cell", rhs="cell_potential(E_cathode, E_anode)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def nernst_model():
    """Model for Nernst equation calculation."""
    return ScientificModel(
        id="redox-nernst",
        domain="chemistry.redox_reactions",
        description="Nernst equation",
        quantities=[
            Quantity(name="E_standard", value=1.0, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="Q", value=0.1, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=8.314, siUnit="J/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=298.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="F", value=0.0, siUnit="C/mol", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E_cell", rhs="nernst_equation(E_standard, n, Q, R, T, F)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def gibbs_model():
    """Model for Gibbs free energy from cell potential."""
    return ScientificModel(
        id="redox-gibbs",
        domain="chemistry.redox_reactions",
        description="Gibbs free energy",
        quantities=[
            Quantity(name="n", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="F", value=0.0, siUnit="C/mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="E_cell", value=0.5, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_G", rhs="gibbs_free_energy_from_cell(n, F, E_cell)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def equilibrium_constant_model():
    """Model for equilibrium constant from cell potential."""
    return ScientificModel(
        id="redox-K",
        domain="chemistry.redox_reactions",
        description="Equilibrium constant from E",
        quantities=[
            Quantity(name="n", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="F", value=0.0, siUnit="C/mol", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="E_standard", value=0.5, siUnit="V", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R", value=8.314, siUnit="J/(mol*K)", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="T", value=298.0, siUnit="K", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="K", rhs="equilibrium_constant_from_cell(n, F, E_standard, R, T)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

# ============ Correctness Tests ============

def test_cell_potential_solvable(cell_potential_model):
    """Test that cell potential solves successfully."""
    solver = ChemistryRedoxSolver()
    result = solver.solve(cell_potential_model)

    assert result.success
    assert "E_cell" in result.summary

def test_cell_potential_correctness(cell_potential_model):
    """Test cell potential: E_cell = E_cathode - E_anode."""
    solver = ChemistryRedoxSolver()
    result = solver.solve(cell_potential_model)

    assert result.success
    # E_cell = 0.8 - (-0.4) = 1.2 V
    expected_E_cell = 0.8 - (-0.4)
    assert abs(result.summary["E_cell"] - expected_E_cell) < 1e-6

# ============ Routing Test ============

def test_general_solver_routes_redox(cell_potential_model):
    """Test that GeneralSolver correctly routes to ChemistryRedoxSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(cell_potential_model)

    assert result.success
    assert "E_cell" in result.summary
