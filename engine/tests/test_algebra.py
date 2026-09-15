"""
Tests for algebraic equation solver.
Golden-file tests for determinism: same model → same output.
"""
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.algebra import AlgebraSolver


@pytest.fixture
def quadratic_model():
    """Quadratic equation: x**2 - 5*x + 6 = 0 (solutions: x=2, x=3)."""
    return ScientificModel(
        id="quadratic-simple",
        domain="mathematics.algebra",
        description="Simple quadratic equation",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Unknown variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="x**2 - 5*x + 6",
                rhs="0",
                type=EquationType.ALGEBRAIC,
                description="Quadratic with roots x=2, x=3"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="solve x**2 - 5*x + 6 = 0")
    )


@pytest.fixture
def linear_system_model():
    """Linear system: 2*x + 3*y = 8, x + y = 3 (solutions: x=1, y=2)."""
    return ScientificModel(
        id="linear-system-2x2",
        domain="mathematics.algebra",
        description="Linear system 2x2",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Unknown x",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="y",
                value=None,
                siUnit="dimensionless",
                description="Unknown y",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="2*x + 3*y",
                rhs="8",
                type=EquationType.ALGEBRAIC,
                description="First linear equation"
            ),
            Equation(
                lhs="x + y",
                rhs="3",
                type=EquationType.ALGEBRAIC,
                description="Second linear equation"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="solve linear system")
    )


@pytest.fixture
def cubic_model():
    """Cubic equation: x**3 - 6*x**2 + 11*x - 6 = 0 (solutions: x=1, x=2, x=3)."""
    return ScientificModel(
        id="cubic-simple",
        domain="mathematics.algebra",
        description="Cubic equation",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Unknown variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="x**3 - 6*x**2 + 11*x - 6",
                rhs="0",
                type=EquationType.ALGEBRAIC,
                description="Cubic with roots x=1, x=2, x=3"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="solve cubic")
    )


@pytest.fixture
def quadratic_with_parameters_model():
    """Quadratic with known parameter: a*x**2 + b*x + c = 0, where a=1, b=-5, c=6."""
    return ScientificModel(
        id="quadratic-with-params",
        domain="mathematics.algebra",
        description="Quadratic with parameters",
        quantities=[
            Quantity(
                name="a",
                value=1.0,
                siUnit="dimensionless",
                description="Coefficient a",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="b",
                value=-5.0,
                siUnit="dimensionless",
                description="Coefficient b",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="c",
                value=6.0,
                siUnit="dimensionless",
                description="Coefficient c",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Unknown variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="a*x**2 + b*x + c",
                rhs="0",
                type=EquationType.ALGEBRAIC,
                description="Quadratic with parameters"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="solve parametric quadratic")
    )


def test_quadratic_solvable(quadratic_model):
    """Test that quadratic equation solves successfully."""
    solver = AlgebraSolver()
    result = solver.solve(quadratic_model)

    assert result.success
    assert result.summary is not None
    # Two solutions with flat keys: solution_0_x, solution_1_x
    assert len(result.summary) == 2

    # Extract solutions (multiple solutions use solution_{idx}_{var} format)
    values = sorted([result.summary.get(f"solution_{i}_x")
                     for i in range(len(result.summary))])
    assert len(values) == 2
    assert abs(values[0] - 2.0) < 1e-10
    assert abs(values[1] - 3.0) < 1e-10


def test_linear_system_solvable(linear_system_model):
    """Test that linear system solves successfully."""
    solver = AlgebraSolver()
    result = solver.solve(linear_system_model)

    assert result.success
    assert result.summary is not None
    # One solution with flat keys: x, y
    assert len(result.summary) == 2

    assert "x" in result.summary
    assert "y" in result.summary
    assert abs(result.summary["x"] - 1.0) < 1e-10
    assert abs(result.summary["y"] - 2.0) < 1e-10


def test_cubic_solvable(cubic_model):
    """Test that cubic equation solves successfully."""
    solver = AlgebraSolver()
    result = solver.solve(cubic_model)

    assert result.success
    assert result.summary is not None
    assert len(result.summary) == 3  # Three solutions

    # Extract solutions (multiple solutions use solution_{idx}_{var} format)
    values = sorted([result.summary.get(f"solution_{i}_x")
                     for i in range(len(result.summary))])

    # Check all three roots
    assert abs(values[0] - 1.0) < 1e-10
    assert abs(values[1] - 2.0) < 1e-10
    assert abs(values[2] - 3.0) < 1e-10


def test_quadratic_with_parameters_solvable(quadratic_with_parameters_model):
    """Test that quadratic with known parameters solves successfully."""
    solver = AlgebraSolver()
    result = solver.solve(quadratic_with_parameters_model)

    assert result.success
    assert result.summary is not None

    # Extract solutions (multiple solutions use solution_{idx}_{var} format)
    values = sorted([result.summary.get(f"solution_{i}_x")
                     for i in range(len(result.summary))])

    # Should have same roots as direct quadratic
    assert abs(values[0] - 2.0) < 1e-10
    assert abs(values[1] - 3.0) < 1e-10


def test_determinism_quadratic(quadratic_model):
    """
    Test determinism: solving the same quadratic twice produces identical results.
    Golden-file test: byte-identical output.
    """
    solver = AlgebraSolver()

    result1 = solver.solve(quadratic_model)
    result2 = solver.solve(quadratic_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_linear_system(linear_system_model):
    """
    Test determinism for linear system: identical results across two calls.
    """
    solver = AlgebraSolver()

    result1 = solver.solve(linear_system_model)
    result2 = solver.solve(linear_system_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_cubic(cubic_model):
    """
    Test determinism for cubic: identical results across two calls.
    """
    solver = AlgebraSolver()

    result1 = solver.solve(cubic_model)
    result2 = solver.solve(cubic_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_general_solver_routes_algebra_quadratic(quadratic_model):
    """Test that GeneralSolver routes algebra domain to AlgebraSolver."""
    result = GeneralSolver().solve(quadratic_model)

    assert result.success
    assert result.summary is not None
    assert len(result.summary) == 2


def test_general_solver_routes_algebra_linear_system(linear_system_model):
    """Test that GeneralSolver routes linear system correctly."""
    result = GeneralSolver().solve(linear_system_model)

    assert result.success
    assert result.summary is not None
    assert len(result.summary) == 2  # Two variables: x, y


def test_error_no_unknowns():
    """Test error handling when all quantities are known."""
    model = ScientificModel(
        id="test-no-unknowns",
        domain="mathematics.algebra",
        description="All known",
        quantities=[
            Quantity(
                name="x",
                value=5.0,
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(lhs="x", rhs="5", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )

    result = AlgebraSolver().solve(model)
    assert not result.success
    assert "No unknowns" in result.message


def test_error_no_equations():
    """Test error handling when no equations provided."""
    model = ScientificModel(
        id="test-no-equations",
        domain="mathematics.algebra",
        description="No equations",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[],  # Empty equations list
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )

    result = AlgebraSolver().solve(model)
    assert not result.success
    assert "No equations" in result.message


def test_error_malformed_equation():
    """Test error handling for malformed equation syntax."""
    model = ScientificModel(
        id="test-malformed",
        domain="mathematics.algebra",
        description="Malformed equation",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(lhs="x ** ** 2", rhs="0", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6)
    )

    result = AlgebraSolver().solve(model)
    assert not result.success
    assert "Failed to parse equation" in result.message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
