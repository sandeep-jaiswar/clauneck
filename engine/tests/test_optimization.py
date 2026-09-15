"""
Tests for optimization solver.
Covers minimization, root-finding, and determinism.
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.optimization import OptimizationSolver


@pytest.fixture
def minimize_quadratic_model():
    """
    Minimize f(x) = (x-2)^2
    Expected minimum: x=2, f(x)=0
    """
    return ScientificModel(
        id="minimize-quadratic",
        domain="mathematics.optimization",
        description="Minimize quadratic function",
        quantities=[
            Quantity(
                name="x",
                value=None,  # Unknown, to be solved
                siUnit="dimensionless",
                description="Decision variable",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="f",
                rhs="(x-2)**2",
                type=EquationType.ALGEBRAIC,
                description="Objective: minimize quadratic"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def minimize_quadratic_multivar_model():
    """
    Minimize f(x, y) = x^2 + (y-1)^2
    Expected minimum: x=0, y=1, f=0
    """
    return ScientificModel(
        id="minimize-multivar-quadratic",
        domain="mathematics.optimization",
        description="Minimize multivariable quadratic",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="y",
                value=None,
                siUnit="dimensionless",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="f",
                rhs="x**2 + (y-1)**2",
                type=EquationType.ALGEBRAIC,
                description="Objective: minimize multivar quadratic"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def root_finding_model():
    """
    Find root of f(x) = x^2 - 4 = 0
    Expected roots: x = ±2
    """
    return ScientificModel(
        id="root-finding-quadratic",
        domain="mathematics.optimization",
        description="Root-finding: x^2 - 4 = 0",
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
            Equation(
                lhs="x**2",
                rhs="4",
                type=EquationType.ALGEBRAIC,
                description="Find root of x^2 = 4"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.FSOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def root_finding_cubic_model():
    """
    Find root of f(x) = x^3 - x - 1 = 0
    One real root near x ≈ 1.3247
    """
    return ScientificModel(
        id="root-finding-cubic",
        domain="mathematics.optimization",
        description="Root-finding: x^3 - x - 1 = 0",
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
            Equation(
                lhs="x**3 - x - 1",
                rhs="0",
                type=EquationType.ALGEBRAIC,
                description="Find root of cubic"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.FSOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def symbolic_solve_linear_model():
    """
    Solve symbolically: 2*x + 3 = 7
    Expected: x = 2
    """
    return ScientificModel(
        id="symbolic-linear",
        domain="mathematics.optimization",
        description="Symbolic solve: 2*x + 3 = 7",
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
            Equation(
                lhs="2*x + 3",
                rhs="7",
                type=EquationType.ALGEBRAIC,
                description="Linear equation"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


def test_minimize_quadratic_solvable(minimize_quadratic_model):
    """Test that quadratic minimization solves successfully."""
    solver = OptimizationSolver()
    result = solver.solve(minimize_quadratic_model)

    assert result.success
    assert result.summary is not None
    assert "x_opt" in result.summary
    assert "optimal_value" in result.summary
    assert "iterations" in result.summary


def test_minimize_quadratic_accuracy(minimize_quadratic_model):
    """Test that quadratic minimum is found accurately."""
    solver = OptimizationSolver()
    result = solver.solve(minimize_quadratic_model)

    assert result.success
    x_optimal = result.summary["x_opt"]
    f_optimal = result.summary["optimal_value"]

    # Minimum should be near x=2, f=0
    assert abs(x_optimal - 2.0) < 1e-2, f"Expected x≈2, got {x_optimal}"
    assert abs(f_optimal - 0.0) < 1e-4, f"Expected f≈0, got {f_optimal}"


def test_minimize_multivar_solvable(minimize_quadratic_multivar_model):
    """Test that multivariable quadratic minimization solves successfully."""
    solver = OptimizationSolver()
    result = solver.solve(minimize_quadratic_multivar_model)

    assert result.success
    assert result.summary is not None
    assert "x_opt" in result.summary
    assert "y_opt" in result.summary


def test_minimize_multivar_accuracy(minimize_quadratic_multivar_model):
    """Test that multivariable minimum is found accurately."""
    solver = OptimizationSolver()
    result = solver.solve(minimize_quadratic_multivar_model)

    assert result.success
    x_opt = result.summary["x_opt"]
    y_opt = result.summary["y_opt"]
    f_opt = result.summary["optimal_value"]

    # Minimum should be at x=0, y=1, f=0
    assert abs(x_opt - 0.0) < 1e-2, f"Expected x≈0, got {x_opt}"
    assert abs(y_opt - 1.0) < 1e-2, f"Expected y≈1, got {y_opt}"
    assert abs(f_opt - 0.0) < 1e-4, f"Expected f≈0, got {f_opt}"


def test_root_finding_quadratic_solvable(root_finding_model):
    """Test that root-finding for x^2=4 solves successfully."""
    solver = OptimizationSolver()
    result = solver.solve(root_finding_model)

    assert result.success
    assert result.summary is not None
    assert "root" in result.summary
    assert "function_value" in result.summary


def test_root_finding_quadratic_accuracy(root_finding_model):
    """Test that root is found accurately (x^2=4 → x=±2)."""
    solver = OptimizationSolver()
    result = solver.solve(root_finding_model)

    assert result.success
    root = result.summary["root"]
    f_val = result.summary["function_value"]

    # Root should be ±2 (likely +2 from initial guess 0)
    assert abs(abs(root) - 2.0) < 1e-2, f"Expected |root|≈2, got {root}"
    assert abs(f_val) < 1e-4, f"Expected f(root)≈0, got {f_val}"


def test_root_finding_cubic_solvable(root_finding_cubic_model):
    """Test that root-finding for x^3-x-1=0 solves successfully."""
    solver = OptimizationSolver()
    result = solver.solve(root_finding_cubic_model)

    assert result.success
    assert result.summary is not None
    assert "root" in result.summary


def test_root_finding_cubic_accuracy(root_finding_cubic_model):
    """Test that cubic root is found accurately."""
    solver = OptimizationSolver()
    result = solver.solve(root_finding_cubic_model)

    assert result.success
    root = result.summary["root"]
    f_val = result.summary["function_value"]

    # Root should be near 1.3247
    assert abs(root - 1.3247) < 0.05, f"Expected root≈1.3247, got {root}"
    assert abs(f_val) < 1e-3, f"Expected f(root)≈0, got {f_val}"


def test_symbolic_solve_linear_solvable(symbolic_solve_linear_model):
    """Test that symbolic solve works for linear equation."""
    solver = OptimizationSolver()
    result = solver.solve(symbolic_solve_linear_model)

    assert result.success
    assert result.summary is not None
    assert "x_sol" in result.summary


def test_symbolic_solve_linear_accuracy(symbolic_solve_linear_model):
    """Test that symbolic solve finds correct solution (2*x+3=7 → x=2)."""
    solver = OptimizationSolver()
    result = solver.solve(symbolic_solve_linear_model)

    assert result.success
    x_sol = result.summary["x_sol"]

    # Solution should be x=2
    assert abs(x_sol - 2.0) < 1e-6, f"Expected x=2, got {x_sol}"


def test_determinism_minimize(minimize_quadratic_model):
    """
    Test determinism: solving the same minimization twice produces identical results.
    Golden-file test: same output.
    """
    solver = OptimizationSolver()

    result1 = solver.solve(minimize_quadratic_model)
    result2 = solver.solve(minimize_quadratic_model)

    assert result1.success and result2.success

    # Compare summary
    assert result1.summary["optimal_value"] == result2.summary["optimal_value"]
    assert result1.summary["x_opt"] == result2.summary["x_opt"]


def test_determinism_root_finding(root_finding_model):
    """
    Test determinism: root-finding twice produces identical results.
    """
    solver = OptimizationSolver()

    result1 = solver.solve(root_finding_model)
    result2 = solver.solve(root_finding_model)

    assert result1.success and result2.success

    # Compare results
    assert result1.summary["root"] == result2.summary["root"]
    assert result1.summary["function_value"] == result2.summary["function_value"]


def test_error_no_unknowns():
    """Test that solver rejects models with no unknown quantities."""
    model = ScientificModel(
        id="no-unknowns",
        domain="mathematics.optimization",
        description="No unknown quantities",
        quantities=[
            Quantity(
                name="x",
                value=1.0,
                siUnit="dimensionless",
                isKnown=True
            ),
        ],
        equations=[
            Equation(
                lhs="f",
                rhs="x**2",
                type=EquationType.ALGEBRAIC
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6
        )
    )

    solver = OptimizationSolver()
    result = solver.solve(model)

    assert not result.success
    assert "No decision variables" in result.message


def test_error_no_equations():
    """Test that solver rejects models with no equations."""
    model = ScientificModel(
        id="no-equations",
        domain="mathematics.optimization",
        description="No equations",
        quantities=[
            Quantity(
                name="x",
                value=None,
                siUnit="dimensionless",
                isKnown=False
            ),
        ],
        equations=[],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6
        )
    )

    solver = OptimizationSolver()
    result = solver.solve(model)

    assert not result.success
    assert "No equations" in result.message


def test_error_fsolve_multivar():
    """Test that fsolve rejects multivar problems."""
    model = ScientificModel(
        id="fsolve-multivar",
        domain="mathematics.optimization",
        description="fsolve with multiple variables",
        quantities=[
            Quantity(name="x", value=None, siUnit="dimensionless", isKnown=False),
            Quantity(name="y", value=None, siUnit="dimensionless", isKnown=False),
        ],
        equations=[
            Equation(lhs="x**2", rhs="4", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.FSOLVE,
            tolerance=1e-6
        )
    )

    solver = OptimizationSolver()
    result = solver.solve(model)

    assert not result.success
    assert "scalar root-finding only" in result.message


def test_general_solver_routes_optimization_minimize(minimize_quadratic_model):
    """Test that GeneralSolver correctly routes to optimization solver."""
    result = GeneralSolver().solve(minimize_quadratic_model)

    assert result.success
    assert result.summary is not None
    assert "x_opt" in result.summary


def test_general_solver_routes_optimization_root_finding(root_finding_model):
    """Test that GeneralSolver correctly routes root-finding."""
    result = GeneralSolver().solve(root_finding_model)

    assert result.success
    assert result.summary is not None
    assert "root" in result.summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
