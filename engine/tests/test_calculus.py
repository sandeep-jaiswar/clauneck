"""
Tests for calculus solver.
Golden-file tests for determinism: same model → same output.
"""
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.calculus import CalculusSolver


@pytest.fixture
def derivative_sin_model():
    """Model for derivative of sin(x)."""
    return ScientificModel(
        id="deriv-sin",
        domain="mathematics.calculus",
        description="Derivative of sin(x) with respect to x",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="diff(sin(x), x)",
                rhs="",
                type=EquationType.ALGEBRAIC,
                description="Derivative of sine"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="derivative sin x")
    )


@pytest.fixture
def indefinite_integral_x2_model():
    """Model for indefinite integral of x^2."""
    return ScientificModel(
        id="integral-x2",
        domain="mathematics.calculus",
        description="Indefinite integral of x^2 with respect to x",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="integrate(x**2, x)",
                rhs="",
                type=EquationType.ALGEBRAIC,
                description="Indefinite integral"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="integral x^2")
    )


@pytest.fixture
def definite_integral_x_model():
    """Model for definite integral of x from 0 to 1."""
    return ScientificModel(
        id="definite-integral-x",
        domain="mathematics.calculus",
        description="Definite integral of x from 0 to 1",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="integrate(x, x, 0, 1)",
                rhs="",
                type=EquationType.ALGEBRAIC,
                description="Definite integral"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="definite integral")
    )


@pytest.fixture
def limit_sinc_model():
    """Model for limit of sin(x)/x as x approaches 0."""
    return ScientificModel(
        id="limit-sinc",
        domain="mathematics.calculus",
        description="Limit of sin(x)/x as x approaches 0",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="limit(sin(x)/x, x, 0)",
                rhs="",
                type=EquationType.ALGEBRAIC,
                description="Limit at zero"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="limit sinc")
    )


@pytest.fixture
def derivative_polynomial_model():
    """Model for derivative of 3*x^2 + 2*x + 1."""
    return ScientificModel(
        id="deriv-poly",
        domain="mathematics.calculus",
        description="Derivative of polynomial 3*x^2 + 2*x + 1",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                description="Variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="diff(3*x**2 + 2*x + 1, x)",
                rhs="",
                type=EquationType.ALGEBRAIC,
                description="Derivative of polynomial"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="derivative polynomial")
    )


def test_derivative_sin_solvable(derivative_sin_model):
    """Test that derivative of sin(x) solves successfully."""
    solver = CalculusSolver()
    result = solver.solve(derivative_sin_model)

    assert result.success
    assert result.summary is not None
    assert "result" in result.summary
    assert result.summary["operation"] == "derivative"
    # cos(x) is the derivative of sin(x)
    assert "cos(x)" in result.summary["result"] or "cos" in result.summary["result"]


def test_derivative_sin_correctness(derivative_sin_model):
    """Test that derivative of sin(x) equals cos(x)."""
    solver = CalculusSolver()
    result = solver.solve(derivative_sin_model)

    assert result.success
    result_str = result.summary["result"]
    # The derivative should be cos(x)
    assert "cos" in result_str, f"Expected 'cos' in result, got: {result_str}"


def test_indefinite_integral_x2_solvable(indefinite_integral_x2_model):
    """Test that indefinite integral of x^2 solves successfully."""
    solver = CalculusSolver()
    result = solver.solve(indefinite_integral_x2_model)

    assert result.success
    assert result.summary is not None
    assert "result" in result.summary
    assert result.summary["operation"] == "indefinite_integral"


def test_indefinite_integral_x2_correctness(indefinite_integral_x2_model):
    """Test that indefinite integral of x^2 equals x^3/3 (plus C)."""
    solver = CalculusSolver()
    result = solver.solve(indefinite_integral_x2_model)

    assert result.success
    result_str = result.summary["result"]
    # Should contain x**3/3 or x^3/3 or similar form
    assert "x**3/3" in result_str or "x^3/3" in result_str or "/3" in result_str, \
        f"Expected x^3/3 form in result, got: {result_str}"


def test_definite_integral_x_solvable(definite_integral_x_model):
    """Test that definite integral of x from 0 to 1 solves successfully."""
    solver = CalculusSolver()
    result = solver.solve(definite_integral_x_model)

    assert result.success
    assert result.summary is not None
    assert "result" in result.summary
    assert result.summary["operation"] == "definite_integral"
    assert "bounds" in result.summary


def test_definite_integral_x_correctness(definite_integral_x_model):
    """Test that definite integral of x from 0 to 1 equals 0.5."""
    solver = CalculusSolver()
    result = solver.solve(definite_integral_x_model)

    assert result.success
    result_str = result.summary["result"]
    result_numeric = float(result_str)
    assert abs(result_numeric - 0.5) < 1e-6, \
        f"Expected 0.5, got: {result_numeric}"


def test_limit_sinc_solvable(limit_sinc_model):
    """Test that limit of sin(x)/x as x→0 solves successfully."""
    solver = CalculusSolver()
    result = solver.solve(limit_sinc_model)

    assert result.success
    assert result.summary is not None
    assert "result" in result.summary
    assert result.summary["operation"] == "limit"
    assert "point" in result.summary


def test_limit_sinc_correctness(limit_sinc_model):
    """Test that limit of sin(x)/x as x→0 equals 1."""
    solver = CalculusSolver()
    result = solver.solve(limit_sinc_model)

    assert result.success
    result_str = result.summary["result"]
    result_numeric = float(result_str)
    assert abs(result_numeric - 1.0) < 1e-6, \
        f"Expected 1.0, got: {result_numeric}"


def test_derivative_polynomial_solvable(derivative_polynomial_model):
    """Test that derivative of polynomial solves successfully."""
    solver = CalculusSolver()
    result = solver.solve(derivative_polynomial_model)

    assert result.success
    assert result.summary is not None
    assert "result" in result.summary
    assert result.summary["operation"] == "derivative"


def test_derivative_polynomial_correctness(derivative_polynomial_model):
    """Test that derivative of 3x^2 + 2x + 1 equals 6x + 2."""
    solver = CalculusSolver()
    result = solver.solve(derivative_polynomial_model)

    assert result.success
    result_str = result.summary["result"]
    # The derivative should be 6*x + 2 or 6*x + 2 or similar
    assert "6" in result_str and "x" in result_str and "2" in result_str, \
        f"Expected '6x + 2' form in result, got: {result_str}"


def test_determinism_derivative(derivative_sin_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = CalculusSolver()

    result1 = solver.solve(derivative_sin_model)
    result2 = solver.solve(derivative_sin_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_integral(definite_integral_x_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = CalculusSolver()

    result1 = solver.solve(definite_integral_x_model)
    result2 = solver.solve(definite_integral_x_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_limit(limit_sinc_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = CalculusSolver()

    result1 = solver.solve(limit_sinc_model)
    result2 = solver.solve(limit_sinc_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_general_solver_routes_derivative(derivative_sin_model):
    """Test that GeneralSolver routes calculus models correctly."""
    result = GeneralSolver().solve(derivative_sin_model)

    assert result.success


def test_general_solver_routes_integral(definite_integral_x_model):
    """Test that GeneralSolver routes calculus models correctly."""
    result = GeneralSolver().solve(definite_integral_x_model)

    assert result.success


def test_general_solver_routes_limit(limit_sinc_model):
    """Test that GeneralSolver routes calculus models correctly."""
    result = GeneralSolver().solve(limit_sinc_model)

    assert result.success


def test_missing_equation():
    """Test error handling when no equation is provided."""
    model = ScientificModel(
        id="test",
        domain="mathematics.calculus",
        quantities=[],
        equations=[],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
    )

    solver = CalculusSolver()
    result = solver.solve(model)

    assert not result.success
    assert "No equations" in result.message


def test_invalid_equation_format():
    """Test error handling for invalid equation format."""
    model = ScientificModel(
        id="test",
        domain="mathematics.calculus",
        quantities=[],
        equations=[
            Equation(
                lhs="not a valid equation",
                rhs="",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
    )

    solver = CalculusSolver()
    result = solver.solve(model)

    assert not result.success
    assert "Could not parse" in result.message


def test_invalid_expression():
    """Test error handling for invalid expression."""
    model = ScientificModel(
        id="test",
        domain="mathematics.calculus",
        quantities=[],
        equations=[
            Equation(
                lhs="diff(not_a_function(), x)",
                rhs="",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
    )

    solver = CalculusSolver()
    result = solver.solve(model)

    # Should fail to parse the expression
    assert not result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
