"""
Tests for linear algebra solver.
Golden-file tests for determinism: same model -> same output.
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.linear_algebra import LinearAlgebraSolver


@pytest.fixture
def matrix_determinant_model():
    """Basic 2x2 matrix determinant computation."""
    # Matrix A = [[1, 2], [3, 4]]
    # det(A) = 1*4 - 2*3 = 4 - 6 = -2
    return ScientificModel(
        id="linalg-det-2x2",
        domain="mathematics.linear_algebra",
        description="Compute determinant of 2x2 matrix",
        quantities=[
            Quantity(
                name="A",
                value=[[1.0, 2.0], [3.0, 4.0]],
                siUnit="dimensionless",
                description="2x2 matrix",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="det(A)",
                rhs="determinant",
                type=EquationType.ALGEBRAIC,
                description="Determinant of matrix A"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="determinant of 2x2 matrix")
    )


@pytest.fixture
def matrix_inverse_model():
    """2x2 matrix inverse computation."""
    # Matrix B = [[4, 7], [2, 6]]
    # det(B) = 4*6 - 7*2 = 24 - 14 = 10
    # B^-1 = (1/10) * [[6, -7], [-2, 4]] = [[0.6, -0.7], [-0.2, 0.4]]
    return ScientificModel(
        id="linalg-inv-2x2",
        domain="mathematics.linear_algebra",
        description="Compute inverse of 2x2 matrix",
        quantities=[
            Quantity(
                name="B",
                value=[[4.0, 7.0], [2.0, 6.0]],
                siUnit="dimensionless",
                description="2x2 matrix",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="inv(B)",
                rhs="inverse",
                type=EquationType.ALGEBRAIC,
                description="Inverse of matrix B"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="inverse of 2x2 matrix")
    )


@pytest.fixture
def solve_linear_system_model():
    """Solve Ax=b for 2x2 system."""
    # A = [[3, 1], [2, -1]], b = [9, 8]
    # Solution: x = [5, -6] (check: 3*5 + 1*(-6) = 9, 2*5 - (-6) = 16... wait let me recalculate)
    # 3*5 + 1*(-6) = 15 - 6 = 9 ✓
    # 2*5 - 1*(-6) = 10 + 6 = 16... that's not 8
    # Let me use: A = [[2, 1], [1, 3]], b = [5, 6]
    # 2*x1 + x2 = 5, x1 + 3*x2 = 6
    # From first: x2 = 5 - 2*x1
    # Substitute: x1 + 3*(5 - 2*x1) = 6
    # x1 + 15 - 6*x1 = 6
    # -5*x1 = -9
    # x1 = 1.8, x2 = 5 - 2*1.8 = 5 - 3.6 = 1.4
    # Check: 2*1.8 + 1.4 = 5 ✓, 1.8 + 3*1.4 = 1.8 + 4.2 = 6 ✓
    return ScientificModel(
        id="linalg-solve-2x2",
        domain="mathematics.linear_algebra",
        description="Solve linear system Ax=b",
        quantities=[
            Quantity(
                name="A",
                value=[[2.0, 1.0], [1.0, 3.0]],
                siUnit="dimensionless",
                description="Coefficient matrix",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="b",
                value=[5.0, 6.0],
                siUnit="dimensionless",
                description="Right-hand side vector",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="solve(A @ x, b)",
                rhs="solution",
                type=EquationType.ALGEBRAIC,
                description="Solve for x in Ax=b"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="solve Ax=b")
    )


@pytest.fixture
def matrix_eigenvalues_model():
    """Eigenvalue computation."""
    # Matrix C = [[5, -2], [1, 2]]
    # char poly: det([[5-λ, -2], [1, 2-λ]]) = (5-λ)(2-λ) + 2 = 10 - 5λ - 2λ + λ^2 + 2 = λ^2 - 7λ + 12
    # = (λ - 3)(λ - 4)
    # eigenvalues: λ = 4, 3
    return ScientificModel(
        id="linalg-eig-2x2",
        domain="mathematics.linear_algebra",
        description="Compute eigenvalues",
        quantities=[
            Quantity(
                name="C",
                value=[[5.0, -2.0], [1.0, 2.0]],
                siUnit="dimensionless",
                description="2x2 matrix",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="eigenvalues(C)",
                rhs="eigenvalues",
                type=EquationType.ALGEBRAIC,
                description="Eigenvalues of matrix C"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="eigenvalues of 2x2 matrix")
    )


@pytest.fixture
def matrix_rank_model():
    """Matrix rank computation."""
    # Matrix D = [[1, 2], [2, 4]] (second row is 2x first row)
    # rank = 1 (linearly dependent rows)
    return ScientificModel(
        id="linalg-rank-2x2",
        domain="mathematics.linear_algebra",
        description="Compute matrix rank",
        quantities=[
            Quantity(
                name="D",
                value=[[1.0, 2.0], [2.0, 4.0]],
                siUnit="dimensionless",
                description="2x2 matrix with rank 1",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="rank(D)",
                rhs="rank",
                type=EquationType.ALGEBRAIC,
                description="Rank of matrix D"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="rank of matrix")
    )


def test_determinant_solvable(matrix_determinant_model):
    """Test that determinant computation succeeds."""
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_determinant_model)

    assert result.success
    assert result.summary is not None
    assert "det(A)" in result.summary


def test_determinant_value(matrix_determinant_model):
    """Test that determinant value is correct."""
    # A = [[1, 2], [3, 4]], det(A) = -2
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_determinant_model)

    assert result.success
    expected_det = -2.0
    actual_det = result.summary["det(A)"]
    assert abs(actual_det - expected_det) < 1e-10


def test_inverse_solvable(matrix_inverse_model):
    """Test that matrix inverse computation succeeds."""
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_inverse_model)

    assert result.success
    assert result.summary is not None
    assert "inv(B)" in result.summary


def test_inverse_value(matrix_inverse_model):
    """Test that matrix inverse is correct."""
    # B = [[4, 7], [2, 6]], B^-1 = [[0.6, -0.7], [-0.2, 0.4]]
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_inverse_model)

    assert result.success
    actual_inv = np.array(result.summary["inv(B)"])
    expected_inv = np.array([[0.6, -0.7], [-0.2, 0.4]])
    assert np.allclose(actual_inv, expected_inv, atol=1e-10)


def test_solve_linear_system_solvable(solve_linear_system_model):
    """Test that linear system solving succeeds."""
    solver = LinearAlgebraSolver()
    result = solver.solve(solve_linear_system_model)

    assert result.success
    assert result.summary is not None
    assert "solve(A @ x, b)" in result.summary


def test_solve_linear_system_value(solve_linear_system_model):
    """Test that linear system solution is correct."""
    # A = [[2, 1], [1, 3]], b = [5, 6]
    # Solution: x = [1.8, 1.4]
    solver = LinearAlgebraSolver()
    result = solver.solve(solve_linear_system_model)

    assert result.success
    actual_solution = np.array(result.summary["solve(A @ x, b)"])
    expected_solution = np.array([1.8, 1.4])
    assert np.allclose(actual_solution, expected_solution, atol=1e-10)


def test_eigenvalues_solvable(matrix_eigenvalues_model):
    """Test that eigenvalue computation succeeds."""
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_eigenvalues_model)

    assert result.success
    assert result.summary is not None
    assert "eigenvalues(C)" in result.summary


def test_eigenvalues_value(matrix_eigenvalues_model):
    """Test that eigenvalues are correct."""
    # C = [[5, -2], [1, 2]], eigenvalues = 4, 3
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_eigenvalues_model)

    assert result.success
    eigenvals = sorted(result.summary["eigenvalues(C)"])
    expected = sorted([3.0, 4.0])
    assert np.allclose(eigenvals, expected, atol=1e-8)


def test_rank_solvable(matrix_rank_model):
    """Test that rank computation succeeds."""
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_rank_model)

    assert result.success
    assert result.summary is not None
    assert "rank(D)" in result.summary


def test_rank_value(matrix_rank_model):
    """Test that rank is correct."""
    # D = [[1, 2], [2, 4]], rank = 1
    solver = LinearAlgebraSolver()
    result = solver.solve(matrix_rank_model)

    assert result.success
    actual_rank = result.summary["rank(D)"]
    assert actual_rank == 1


def test_determinism_determinant(matrix_determinant_model):
    """Test determinism: solving twice produces identical results."""
    solver = LinearAlgebraSolver()

    result1 = solver.solve(matrix_determinant_model)
    result2 = solver.solve(matrix_determinant_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_inverse(matrix_inverse_model):
    """Test determinism for matrix inverse."""
    solver = LinearAlgebraSolver()

    result1 = solver.solve(matrix_inverse_model)
    result2 = solver.solve(matrix_inverse_model)

    assert result1.success and result2.success
    # Compare as numpy arrays for floating point equality
    inv1 = np.array(result1.summary["inv(B)"])
    inv2 = np.array(result2.summary["inv(B)"])
    assert np.allclose(inv1, inv2, atol=1e-15)


def test_determinism_solve_system(solve_linear_system_model):
    """Test determinism for linear system solving."""
    solver = LinearAlgebraSolver()

    result1 = solver.solve(solve_linear_system_model)
    result2 = solver.solve(solve_linear_system_model)

    assert result1.success and result2.success
    sol1 = np.array(result1.summary["solve(A @ x, b)"])
    sol2 = np.array(result2.summary["solve(A @ x, b)"])
    assert np.allclose(sol1, sol2, atol=1e-15)


def test_general_solver_routes_linear_algebra(matrix_determinant_model):
    """Test that GeneralSolver correctly routes to LinearAlgebraSolver."""
    solver = GeneralSolver()
    result = solver.solve(matrix_determinant_model)

    assert result.success
    assert result.summary is not None


def test_multiple_operations(matrix_determinant_model, matrix_inverse_model,
                            matrix_rank_model):
    """Test solver with multiple operations in one model."""
    # Create a model with multiple operations
    model = ScientificModel(
        id="linalg-multi-ops",
        domain="mathematics.linear_algebra",
        description="Multiple linear algebra operations",
        quantities=[
            Quantity(
                name="A",
                value=[[2.0, 1.0], [1.0, 3.0]],
                siUnit="dimensionless",
                description="2x2 matrix",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(lhs="det(A)", rhs="det", type=EquationType.ALGEBRAIC),
            Equation(lhs="rank(A)", rhs="rank", type=EquationType.ALGEBRAIC),
            Equation(lhs="transpose(A)", rhs="transpose", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        )
    )

    solver = LinearAlgebraSolver()
    result = solver.solve(model)

    assert result.success
    assert "det(A)" in result.summary
    assert "rank(A)" in result.summary
    assert "transpose(A)" in result.summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
