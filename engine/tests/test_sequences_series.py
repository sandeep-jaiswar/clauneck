"""Tests for sequences and series solver."""
import pytest
import numpy as np
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.sequences_series import SequencesSeriesSolver


@pytest.fixture
def arithmetic_sum_model():
    """Model for arithmetic sequence sum: a1=1, d=2, n=10."""
    return ScientificModel(
        id="seq-arithmetic",
        domain="mathematics.sequences_series",
        description="Arithmetic sequence sum",
        quantities=[
            Quantity(name="a1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="arithmetic_sum(a1, d, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def geometric_sum_model():
    """Model for geometric sequence sum: a=2, r=0.5, n=10."""
    return ScientificModel(
        id="seq-geometric",
        domain="mathematics.sequences_series",
        description="Geometric sequence sum",
        quantities=[
            Quantity(name="a", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="geometric_sum(a, r, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def harmonic_sum_model():
    """Model for harmonic series sum: H_n with n=10."""
    return ScientificModel(
        id="seq-harmonic",
        domain="mathematics.sequences_series",
        description="Harmonic series sum",
        quantities=[
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="H", rhs="harmonic_sum(n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def ratio_test_model():
    """Model for ratio test: a_n=1/2^n, a_n+1=1/2^(n+1)."""
    return ScientificModel(
        id="seq-ratio-test",
        domain="mathematics.sequences_series",
        description="Ratio test convergence",
        quantities=[
            Quantity(name="a_n", value=0.0625, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),  # 1/16
            Quantity(name="a_n_plus_1", value=0.03125, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),  # 1/32
        ],
        equations=[
            Equation(lhs="test", rhs="ratio_test(a_n, a_n_plus_1)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def nth_term_arithmetic_model():
    """Model for nth term of arithmetic sequence: a1=1, d=2, n=5."""
    return ScientificModel(
        id="seq-nth-arithmetic",
        domain="mathematics.sequences_series",
        description="Nth term of arithmetic sequence",
        quantities=[
            Quantity(name="a1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="term", rhs="nth_term(a1, d, n, arithmetic)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def nth_term_geometric_model():
    """Model for nth term of geometric sequence: a1=2, r=0.5, n=5."""
    return ScientificModel(
        id="seq-nth-geometric",
        domain="mathematics.sequences_series",
        description="Nth term of geometric sequence",
        quantities=[
            Quantity(name="a1", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="term", rhs="nth_term(a1, r, n, geometric)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_arithmetic_sum_solvable(arithmetic_sum_model):
    """Test that arithmetic sum solves successfully."""
    solver = SequencesSeriesSolver()
    result = solver.solve(arithmetic_sum_model)

    assert result.success
    assert "S" in result.summary


def test_arithmetic_sum_correctness(arithmetic_sum_model):
    """Test arithmetic sum: a1=1, d=2, n=10.

    Expected: S = 10/2 * (2*1 + 9*2) = 5 * 20 = 100
    """
    solver = SequencesSeriesSolver()
    result = solver.solve(arithmetic_sum_model)

    assert result.success
    expected = 100.0
    assert abs(result.summary["S"] - expected) < 1e-6


def test_geometric_sum_solvable(geometric_sum_model):
    """Test that geometric sum solves successfully."""
    solver = SequencesSeriesSolver()
    result = solver.solve(geometric_sum_model)

    assert result.success
    assert "S" in result.summary


def test_geometric_sum_correctness(geometric_sum_model):
    """Test geometric sum: a=2, r=0.5, n=10.

    Expected: S = 2 * (1 - 0.5^10) / (1 - 0.5)
    """
    solver = SequencesSeriesSolver()
    result = solver.solve(geometric_sum_model)

    assert result.success
    expected = 2.0 * (1.0 - 0.5**10) / (1.0 - 0.5)
    assert abs(result.summary["S"] - expected) < 1e-6


def test_harmonic_sum_solvable(harmonic_sum_model):
    """Test that harmonic sum solves successfully."""
    solver = SequencesSeriesSolver()
    result = solver.solve(harmonic_sum_model)

    assert result.success
    assert "H" in result.summary


def test_harmonic_sum_correctness(harmonic_sum_model):
    """Test harmonic sum: H_10 = 1 + 1/2 + 1/3 + ... + 1/10."""
    solver = SequencesSeriesSolver()
    result = solver.solve(harmonic_sum_model)

    assert result.success
    # H_10 ≈ 2.9289...
    expected = sum(1.0 / i for i in range(1, 11))
    assert abs(result.summary["H"] - expected) < 1e-6


def test_ratio_test_solvable(ratio_test_model):
    """Test that ratio test solves successfully."""
    solver = SequencesSeriesSolver()
    result = solver.solve(ratio_test_model)

    assert result.success
    # run_dispatch prefixes dict keys with lhs, so "test" becomes "test_limit_ratio" and "test_convergence_status"
    assert "test_limit_ratio" in result.summary
    assert "test_convergence_status" in result.summary


def test_ratio_test_convergence(ratio_test_model):
    """Test ratio test convergence detection."""
    solver = SequencesSeriesSolver()
    result = solver.solve(ratio_test_model)

    assert result.success
    # For geometric series with r=0.5, ratio should be 0.5 < 1 (converges)
    # a_n = 1/16, a_n+1 = 1/32, ratio = 0.5
    assert result.summary.get("test_convergence_status") == "converges"


def test_nth_term_arithmetic_solvable(nth_term_arithmetic_model):
    """Test that nth term of arithmetic sequence solves successfully."""
    solver = SequencesSeriesSolver()
    result = solver.solve(nth_term_arithmetic_model)

    assert result.success
    assert "term" in result.summary


def test_nth_term_arithmetic_correctness(nth_term_arithmetic_model):
    """Test nth term: a1=1, d=2, n=5.

    Expected: a_5 = 1 + (5-1)*2 = 1 + 8 = 9
    """
    solver = SequencesSeriesSolver()
    result = solver.solve(nth_term_arithmetic_model)

    assert result.success
    expected = 9.0
    assert abs(result.summary["term"] - expected) < 1e-6


def test_nth_term_geometric_correctness(nth_term_geometric_model):
    """Test nth term: a1=2, r=0.5, n=5.

    Expected: a_5 = 2 * 0.5^(5-1) = 2 * 0.5^4 = 2 * 1/16 = 0.125
    """
    solver = SequencesSeriesSolver()
    result = solver.solve(nth_term_geometric_model)

    assert result.success
    expected = 0.125
    assert abs(result.summary["term"] - expected) < 1e-6


# ============ Determinism Tests ============

def test_arithmetic_sum_determinism(arithmetic_sum_model):
    """Test that arithmetic sum is deterministic: solve twice -> same result."""
    solver = SequencesSeriesSolver()
    result1 = solver.solve(arithmetic_sum_model)
    result2 = solver.solve(arithmetic_sum_model)

    assert result1.success and result2.success
    assert abs(result1.summary["S"] - result2.summary["S"]) < 1e-15


def test_geometric_sum_determinism(geometric_sum_model):
    """Test that geometric sum is deterministic."""
    solver = SequencesSeriesSolver()
    result1 = solver.solve(geometric_sum_model)
    result2 = solver.solve(geometric_sum_model)

    assert result1.success and result2.success
    assert abs(result1.summary["S"] - result2.summary["S"]) < 1e-15


def test_harmonic_sum_determinism(harmonic_sum_model):
    """Test that harmonic sum is deterministic."""
    solver = SequencesSeriesSolver()
    result1 = solver.solve(harmonic_sum_model)
    result2 = solver.solve(harmonic_sum_model)

    assert result1.success and result2.success
    assert abs(result1.summary["H"] - result2.summary["H"]) < 1e-15


def test_nth_term_determinism(nth_term_arithmetic_model):
    """Test that nth term is deterministic."""
    solver = SequencesSeriesSolver()
    result1 = solver.solve(nth_term_arithmetic_model)
    result2 = solver.solve(nth_term_arithmetic_model)

    assert result1.success and result2.success
    assert abs(result1.summary["term"] - result2.summary["term"]) < 1e-15


# ============ Error Path Tests ============

def test_arithmetic_sum_negative_n():
    """Test that arithmetic sum fails with negative n."""
    model = ScientificModel(
        id="seq-bad-n",
        domain="mathematics.sequences_series",
        description="Arithmetic sum with negative n",
        quantities=[
            Quantity(name="a1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=-5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="arithmetic_sum(a1, d, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert not result.success
    assert "positive" in result.error.lower() or "must be" in result.error.lower()


def test_harmonic_sum_zero_n():
    """Test that harmonic sum fails with n=0."""
    model = ScientificModel(
        id="seq-bad-harmonic",
        domain="mathematics.sequences_series",
        description="Harmonic sum with n=0",
        quantities=[
            Quantity(name="n", value=0.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="H", rhs="harmonic_sum(n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert not result.success


def test_ratio_test_zero_denominator():
    """Test that ratio test fails with zero denominator."""
    model = ScientificModel(
        id="seq-bad-ratio",
        domain="mathematics.sequences_series",
        description="Ratio test with a_n near zero",
        quantities=[
            Quantity(name="a_n", value=1e-20, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="a_n_plus_1", value=0.5e-20, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="test", rhs="ratio_test(a_n, a_n_plus_1)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert not result.success


def test_geometric_sum_large_ratio():
    """Test geometric sum with large ratio (should still work but sum diverges conceptually)."""
    model = ScientificModel(
        id="seq-large-r",
        domain="mathematics.sequences_series",
        description="Geometric sum with large ratio",
        quantities=[
            Quantity(name="a", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="geometric_sum(a, r, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    # Should still compute the partial sum correctly
    assert result.success
    expected = 1.0 * (1.0 - 2.0**10) / (1.0 - 2.0)
    assert abs(result.summary["S"] - expected) < 1.0


def test_nth_term_invalid_series_type():
    """Test that nth_term fails with invalid series_type."""
    model = ScientificModel(
        id="seq-bad-type",
        domain="mathematics.sequences_series",
        description="Nth term with invalid series type",
        quantities=[
            Quantity(name="a1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="term", rhs="nth_term(a1, d, n, fibonacci)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert not result.success


# ============ Edge Case Tests ============

def test_geometric_sum_ratio_one():
    """Test geometric sum with r=1 (special case: S_n = a*n)."""
    model = ScientificModel(
        id="seq-r-one",
        domain="mathematics.sequences_series",
        description="Geometric sum with r=1",
        quantities=[
            Quantity(name="a", value=5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="geometric_sum(a, r, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert result.success
    # S = 5 * 10 = 50
    assert abs(result.summary["S"] - 50.0) < 1e-6


def test_alternating_series_test_converges():
    """Test alternating series test with converging series."""
    model = ScientificModel(
        id="seq-alt-converge",
        domain="mathematics.sequences_series",
        description="Alternating series convergence",
        quantities=[
            Quantity(name="a_n", value=0.1, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="a_n_plus_1", value=0.01, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="test", rhs="alternating_series_test(a_n, a_n_plus_1)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert result.success
    assert result.summary.get("test_convergence_status") == "converges"


def test_root_test_convergence():
    """Test root test convergence detection."""
    model = ScientificModel(
        id="seq-root-test",
        domain="mathematics.sequences_series",
        description="Root test convergence",
        quantities=[
            Quantity(name="a_n", value=0.064, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),  # (0.4)^3
            Quantity(name="n", value=3.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="test", rhs="root_test(a_n, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = SequencesSeriesSolver()
    result = solver.solve(model)

    assert result.success
    # nth_root of 0.064 = 0.4
    assert result.summary.get("test_convergence_status") == "converges"


# ============ Integration Tests ============

def test_general_solver_routing():
    """Test that GeneralSolver routes to SequencesSeriesSolver correctly."""
    model = ScientificModel(
        id="seq-routing",
        domain="mathematics.sequences_series",
        description="Routing test",
        quantities=[
            Quantity(name="a1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n", value=5.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="S", rhs="arithmetic_sum(a1, d, n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    general_solver = GeneralSolver()
    result = general_solver.solve(model)

    assert result.success
    assert "S" in result.summary
