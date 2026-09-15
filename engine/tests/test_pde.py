"""
Tests for Partial Differential Equations solver.
Comprehensive coverage: correctness, determinism, error paths, edge cases.
"""
import numpy as np
import pytest

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.pde import PDESolver


@pytest.fixture
def heat_equation_model():
    """Model for solving 1D heat equation with default parameters."""
    return ScientificModel(
        id="pde-heat-1d",
        domain="mathematics.pde",
        description="Solve 1D heat equation",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="diffusivity", value=1.0, siUnit="m^2/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="heat_solution",
                rhs='heat_equation_1d(domain_length, time_span, diffusivity, "sin(pi*x)")',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def wave_equation_model():
    """Model for solving 1D wave equation."""
    return ScientificModel(
        id="pde-wave-1d",
        domain="mathematics.pde",
        description="Solve 1D wave equation",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="wave_speed", value=1.0, siUnit="m/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="wave_solution",
                rhs='wave_equation_1d(domain_length, time_span, wave_speed)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def laplace_equation_model():
    """Model for solving 2D Laplace equation."""
    return ScientificModel(
        id="pde-laplace-2d",
        domain="mathematics.pde",
        description="Solve 2D Laplace equation",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="num_points", value=30.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="laplace_solution",
                rhs='laplace_equation(domain_length, num_points)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def poisson_equation_model():
    """Model for solving 2D Poisson equation."""
    return ScientificModel(
        id="pde-poisson-2d",
        domain="mathematics.pde",
        description="Solve 2D Poisson equation",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="num_points", value=30.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="source_term", value="1.0", siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="poisson_solution",
                rhs='poisson_equation(domain_length, num_points, source_term)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def separation_of_variables_model():
    """Model for separation of variables method."""
    return ScientificModel(
        id="pde-sov",
        domain="mathematics.pde",
        description="Solve via separation of variables",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="diffusivity", value=1.0, siUnit="m^2/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="sov_solution",
                rhs='separation_of_variables(domain_length, time_span, "heat", diffusivity)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def method_of_characteristics_model():
    """Model for method of characteristics."""
    return ScientificModel(
        id="pde-moc",
        domain="mathematics.pde",
        description="Solve via method of characteristics",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="wave_speed", value=1.0, siUnit="m/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="moc_solution",
                rhs='method_of_characteristics(domain_length, time_span, wave_speed)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def d_alembert_model():
    """Model for D'Alembert solution."""
    return ScientificModel(
        id="pde-dalembert",
        domain="mathematics.pde",
        description="Wave equation via D'Alembert",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="wave_speed", value=1.0, siUnit="m/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="dalembert_solution",
                rhs='d_alembert_solution(domain_length, time_span, wave_speed)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# Correctness Tests

def test_heat_equation_solvable(heat_equation_model):
    """Test that heat equation solves successfully."""
    solver = PDESolver()
    result = solver.solve(heat_equation_model)

    assert result.success
    assert result.summary is not None
    assert "heat_solution_solution_values" in result.summary


def test_heat_equation_returns_array(heat_equation_model):
    """Test that heat equation returns solution array."""
    solver = PDESolver()
    result = solver.solve(heat_equation_model)

    assert result.success
    solution_values = result.summary["heat_solution_solution_values"]
    assert isinstance(solution_values, list)
    assert len(solution_values) > 0


def test_heat_equation_solution_bounded(heat_equation_model):
    """Test that heat solution is bounded by initial condition (diffusivity property)."""
    solver = PDESolver()
    result = solver.solve(heat_equation_model)

    assert result.success
    solution_values = result.summary["heat_solution_solution_values"]
    # Solution should be bounded by initial condition max
    assert max(solution_values) <= 1.1  # With small tolerance for numerical error


def test_wave_equation_solvable(wave_equation_model):
    """Test that wave equation solves successfully."""
    solver = PDESolver()
    result = solver.solve(wave_equation_model)

    assert result.success
    assert result.summary is not None


def test_wave_equation_energy_conservation(wave_equation_model):
    """Test that wave equation solution doesn't blow up (energy property)."""
    solver = PDESolver()
    result = solver.solve(wave_equation_model)

    assert result.success
    solution_values = result.summary.get("wave_solution_solution_values", [])
    # Solution should not explode
    assert all(abs(v) <= 1.5 for v in solution_values)


def test_laplace_equation_solvable(laplace_equation_model):
    """Test that Laplace equation solves successfully."""
    solver = PDESolver()
    result = solver.solve(laplace_equation_model)

    assert result.success
    assert result.summary is not None


def test_laplace_max_principle(laplace_equation_model):
    """Test maximum principle: solution max occurs at boundary."""
    solver = PDESolver()
    result = solver.solve(laplace_equation_model)

    assert result.success
    solution_values = result.summary["laplace_solution_solution_values"]
    # Solution bounded by BCs (max should be 1.0 for this model)
    assert max(solution_values) <= 1.0 + 1e-4


def test_poisson_equation_solvable(poisson_equation_model):
    """Test that Poisson equation solves successfully."""
    solver = PDESolver()
    result = solver.solve(poisson_equation_model)

    assert result.success
    assert result.summary is not None


def test_poisson_equation_has_source_effect(poisson_equation_model):
    """Test that Poisson solution depends on source term."""
    solver = PDESolver()
    result = solver.solve(poisson_equation_model)

    assert result.success
    solution_values = result.summary["poisson_solution_solution_values"]
    # With positive source, interior values should be nonzero
    assert any(abs(v) > 0.01 for v in solution_values)


def test_separation_of_variables_heat(separation_of_variables_model):
    """Test separation of variables for heat equation."""
    solver = PDESolver()
    result = solver.solve(separation_of_variables_model)

    assert result.success
    assert "sov_solution_solution_values" in result.summary


def test_separation_of_variables_decay(separation_of_variables_model):
    """Test that heat equation solution decays over time."""
    solver = PDESolver()
    result = solver.solve(separation_of_variables_model)

    assert result.success
    solution_values = result.summary["sov_solution_solution_values"]
    # Solution should decay (max value decreases over time)
    assert max(solution_values) < 1.0


def test_method_of_characteristics_solvable(method_of_characteristics_model):
    """Test method of characteristics solves successfully."""
    solver = PDESolver()
    result = solver.solve(method_of_characteristics_model)

    assert result.success
    assert "moc_solution_solution_values" in result.summary


def test_method_of_characteristics_shape_preservation(method_of_characteristics_model):
    """Test that advection preserves profile shape."""
    solver = PDESolver()
    result = solver.solve(method_of_characteristics_model)

    assert result.success
    solution_values = result.summary["moc_solution_solution_values"]
    # Advection should preserve profile (max should remain similar)
    assert max(solution_values) <= 1.0 + 1e-4


def test_d_alembert_solvable(d_alembert_model):
    """Test D'Alembert solution solves successfully."""
    solver = PDESolver()
    result = solver.solve(d_alembert_model)

    assert result.success
    assert "dalembert_solution_solution_values" in result.summary


def test_d_alembert_energy_bounded(d_alembert_model):
    """Test D'Alembert solution has bounded energy."""
    solver = PDESolver()
    result = solver.solve(d_alembert_model)

    assert result.success
    solution_values = result.summary["dalembert_solution_solution_values"]
    # Energy should be bounded
    assert all(abs(v) <= 2.0 for v in solution_values)


# Boundary Condition Tests

def test_dirichlet_bc():
    """Test Dirichlet boundary condition function."""
    from app.solvers.pde import _dirichlet_bc

    result = _dirichlet_bc(1.5)
    assert result == 1.5


def test_neumann_bc():
    """Test Neumann boundary condition function."""
    from app.solvers.pde import _neumann_bc

    result = _neumann_bc(0.5)
    assert result == 0.5


def test_robin_bc():
    """Test Robin boundary condition function."""
    from app.solvers.pde import _robin_bc

    result = _robin_bc(1.0, 2.0, 3.0)
    assert isinstance(result, dict)
    assert result["alpha"] == 1.0
    assert result["beta"] == 2.0
    assert result["gamma"] == 3.0


def test_periodic_bc():
    """Test periodic boundary condition function."""
    from app.solvers.pde import _periodic_bc

    result = _periodic_bc(2.0)
    assert result == 2.0


# Error Path Tests

def test_heat_equation_negative_domain_length(heat_equation_model):
    """Test error handling for negative domain length."""
    model = heat_equation_model.model_copy(update={
        "quantities": [
            Quantity(name="domain_length", value=-1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="diffusivity", value=1.0, siUnit="m^2/s", isKnown=True),
        ]
    })

    solver = PDESolver()
    result = solver.solve(model)

    assert not result.success
    assert "domain_length" in result.error.lower() or "positive" in result.error.lower()


def test_heat_equation_zero_time_span(heat_equation_model):
    """Test error handling for zero time span."""
    model = heat_equation_model.model_copy(update={
        "quantities": [
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.0, siUnit="s", isKnown=True),
            Quantity(name="diffusivity", value=1.0, siUnit="m^2/s", isKnown=True),
        ]
    })

    solver = PDESolver()
    result = solver.solve(model)

    assert not result.success


def test_wave_equation_negative_wave_speed(wave_equation_model):
    """Test error handling for negative wave speed."""
    model = wave_equation_model.model_copy(update={
        "quantities": [
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="wave_speed", value=-1.0, siUnit="m/s", isKnown=True),
        ]
    })

    solver = PDESolver()
    result = solver.solve(model)

    assert not result.success


def test_laplace_equation_small_num_points(laplace_equation_model):
    """Test error handling for too few grid points."""
    model = laplace_equation_model.model_copy(update={
        "quantities": [
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="num_points", value=2.0, siUnit="dimensionless", isKnown=True),
        ]
    })

    solver = PDESolver()
    result = solver.solve(model)

    assert not result.success


def test_robin_bc_both_coefficients_zero():
    """Test error handling for degenerate Robin BC."""
    from app.solvers.pde import _robin_bc

    with pytest.raises(ValueError, match="nonzero"):
        _robin_bc(0.0, 0.0, 1.0)


def test_periodic_bc_negative_period():
    """Test error handling for negative period."""
    from app.solvers.pde import _periodic_bc

    with pytest.raises(ValueError, match="positive"):
        _periodic_bc(-1.0)


def test_method_of_characteristics_zero_wave_speed():
    """Test error handling for zero wave speed in advection."""
    from app.solvers.pde import _method_of_characteristics

    with pytest.raises(ValueError, match="zero"):
        _method_of_characteristics(1.0, 0.1, 0.0)


def test_d_alembert_negative_wave_speed():
    """Test error handling for negative wave speed in D'Alembert."""
    from app.solvers.pde import _d_alembert_solution

    with pytest.raises(ValueError, match="positive"):
        _d_alembert_solution(1.0, 0.1, -1.0)


# Determinism Tests

def test_determinism_heat_equation(heat_equation_model):
    """Test determinism: solving twice gives same results."""
    solver = PDESolver()

    result1 = solver.solve(heat_equation_model)
    result2 = solver.solve(heat_equation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_wave_equation(wave_equation_model):
    """Test determinism for wave equation."""
    solver = PDESolver()

    result1 = solver.solve(wave_equation_model)
    result2 = solver.solve(wave_equation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_laplace_equation(laplace_equation_model):
    """Test determinism for Laplace equation."""
    solver = PDESolver()

    result1 = solver.solve(laplace_equation_model)
    result2 = solver.solve(laplace_equation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_poisson_equation(poisson_equation_model):
    """Test determinism for Poisson equation."""
    solver = PDESolver()

    result1 = solver.solve(poisson_equation_model)
    result2 = solver.solve(poisson_equation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_separation_of_variables(separation_of_variables_model):
    """Test determinism for separation of variables."""
    solver = PDESolver()

    result1 = solver.solve(separation_of_variables_model)
    result2 = solver.solve(separation_of_variables_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_method_of_characteristics(method_of_characteristics_model):
    """Test determinism for method of characteristics."""
    solver = PDESolver()

    result1 = solver.solve(method_of_characteristics_model)
    result2 = solver.solve(method_of_characteristics_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_d_alembert(d_alembert_model):
    """Test determinism for D'Alembert solution."""
    solver = PDESolver()

    result1 = solver.solve(d_alembert_model)
    result2 = solver.solve(d_alembert_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# General Solver Routing Tests

def test_general_solver_routes_pde_heat(heat_equation_model):
    """Test that GeneralSolver routes to PDE solver."""
    result = GeneralSolver().solve(heat_equation_model)

    assert result.success
    assert result.summary is not None
    assert "heat_solution" in result.summary or "heat_solution_solution_values" in result.summary


def test_general_solver_routes_pde_wave(wave_equation_model):
    """Test GeneralSolver routes wave equation."""
    result = GeneralSolver().solve(wave_equation_model)

    assert result.success
    assert result.summary is not None


def test_general_solver_routes_pde_laplace(laplace_equation_model):
    """Test GeneralSolver routes Laplace equation."""
    result = GeneralSolver().solve(laplace_equation_model)

    assert result.success
    assert result.summary is not None


def test_general_solver_routes_pde_poisson(poisson_equation_model):
    """Test GeneralSolver routes Poisson equation."""
    result = GeneralSolver().solve(poisson_equation_model)

    assert result.success
    assert result.summary is not None


# Edge Case Tests

def test_heat_equation_large_time_span():
    """Test heat equation with large time value."""
    model = ScientificModel(
        id="pde-heat-large-time",
        domain="mathematics.pde",
        description="Heat equation with large time",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=1.0, siUnit="s", isKnown=True),
            Quantity(name="diffusivity", value=1.0, siUnit="m^2/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="heat_solution",
                rhs='heat_equation_1d(domain_length, time_span, diffusivity, "sin(pi*x)")',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PDESolver()
    result = solver.solve(model)

    assert result.success
    solution_values = result.summary["heat_solution_solution_values"]
    # After long time, solution should decay to near zero
    assert max(solution_values) < 0.1


def test_wave_equation_high_wave_speed():
    """Test wave equation with high wave speed (stability test)."""
    model = ScientificModel(
        id="pde-wave-highspeed",
        domain="mathematics.pde",
        description="Wave equation high speed",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.05, siUnit="s", isKnown=True),
            Quantity(name="wave_speed", value=10.0, siUnit="m/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="wave_solution",
                rhs='wave_equation_1d(domain_length, time_span, wave_speed)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PDESolver()
    result = solver.solve(model)

    assert result.success
    solution_values = result.summary.get("wave_solution_solution_values", [])
    # Solution should remain bounded despite high wave speed
    assert all(abs(v) <= 2.0 for v in solution_values)


def test_laplace_equation_high_resolution():
    """Test Laplace equation with high grid resolution."""
    model = ScientificModel(
        id="pde-laplace-highres",
        domain="mathematics.pde",
        description="Laplace high resolution",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="num_points", value=100.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="laplace_solution",
                rhs='laplace_equation(domain_length, num_points)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PDESolver()
    result = solver.solve(model)

    assert result.success
    solution_values = result.summary["laplace_solution_solution_values"]
    assert len(solution_values) == 100 * 100  # Full grid


def test_finite_difference_solve_heat():
    """Test generic finite difference solver for heat equation."""
    model = ScientificModel(
        id="pde-fd-heat",
        domain="mathematics.pde",
        description="Finite difference heat solver",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="parameter", value=1.0, siUnit="m^2/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="fd_solution",
                rhs='finite_difference_solve(domain_length, time_span, "heat", parameter)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PDESolver()
    result = solver.solve(model)

    assert result.success


def test_finite_difference_solve_wave():
    """Test generic finite difference solver for wave equation."""
    model = ScientificModel(
        id="pde-fd-wave",
        domain="mathematics.pde",
        description="Finite difference wave solver",
        quantities=[
            Quantity(name="domain_length", value=1.0, siUnit="m", isKnown=True),
            Quantity(name="time_span", value=0.1, siUnit="s", isKnown=True),
            Quantity(name="parameter", value=1.0, siUnit="m/s", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="fd_solution",
                rhs='finite_difference_solve(domain_length, time_span, "wave", parameter)',
                type=EquationType.PDE,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PDESolver()
    result = solver.solve(model)

    assert result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
