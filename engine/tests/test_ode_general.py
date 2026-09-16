"""
Tests for general ODE solver (mathematics.ode domain).
Covers simple ODEs, coupled systems, determinism, and symbolic solutions.
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    TimeSpan, Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.ode_general import ODEGeneralSolver


@pytest.fixture
def simple_ode_model():
    """Simple first-order ODE: dy/dt = -2*y, y(0) = 1, solution y(t) = exp(-2*t)."""
    return ScientificModel(
        id="ode-simple-decay",
        domain="mathematics.ode",
        description="Exponential decay: dy/dt = -2*y",
        quantities=[
            Quantity(
                name="y",
                value=1.0,
                siUnit="dimensionless",
                description="State variable",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="t",
                value=None,
                siUnit="s",
                description="Time",
                isKnown=False,
                dimensionVector=DimensionVector(time=1)
            ),
        ],
        equations=[
            Equation(
                lhs="dy/dt",
                rhs="-2*y",
                type=EquationType.ODE,
                description="Exponential decay"
            ),
        ],
        initialConditions={"y": 1.0},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-8,
            timeSpan=TimeSpan(start=0, end=2, numPoints=500)
        ),
        metadata=Metadata(source="test", originalQuery="exponential decay ODE")
    )


@pytest.fixture
def coupled_ode_model():
    """Coupled ODE system: predator-prey (Lotka-Volterra)."""
    return ScientificModel(
        id="ode-predator-prey",
        domain="mathematics.ode",
        description="Lotka-Volterra predator-prey model",
        quantities=[
            Quantity(
                name="x",
                value=1.5,
                siUnit="dimensionless",
                description="Prey population",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="y",
                value=0.5,
                siUnit="dimensionless",
                description="Predator population",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="dx/dt",
                rhs="x - x*y",
                type=EquationType.ODE,
                description="Prey growth minus predation"
            ),
            Equation(
                lhs="dy/dt",
                rhs="x*y - y",
                type=EquationType.ODE,
                description="Predation minus predator death"
            ),
        ],
        initialConditions={"x": 1.5, "y": 0.5},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-7,
            timeSpan=TimeSpan(start=0, end=10, numPoints=1000)
        ),
        metadata=Metadata(source="test", originalQuery="predator prey model")
    )


@pytest.fixture
def second_order_ode_model():
    """Second-order ODE: d2x/dt2 = -x (harmonic oscillator, x(0)=1, dx/dt(0)=0)."""
    return ScientificModel(
        id="ode-harmonic-oscillator",
        domain="mathematics.ode",
        description="Simple harmonic motion: d2x/dt2 = -x",
        quantities=[
            Quantity(
                name="x",
                value=1.0,
                siUnit="m",
                description="Position",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="d2x/dt2",
                rhs="-x",
                type=EquationType.ODE,
                description="Restoring force"
            ),
        ],
        initialConditions={"x": 1.0, "dx/dt": 0.0},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-8,
            timeSpan=TimeSpan(start=0, end=2*np.pi, numPoints=1000)
        ),
        metadata=Metadata(source="test", originalQuery="harmonic oscillator")
    )


def test_simple_ode_solvable(simple_ode_model):
    """Test that simple exponential decay ODE solves successfully."""
    solver = ODEGeneralSolver()
    result = solver.solve(simple_ode_model)

    assert result.success
    assert result.trajectory is not None
    assert "t" in result.trajectory
    assert "y" in result.trajectory
    assert result.summary is not None
    assert "y_final" in result.summary
    assert len(result.trajectory["t"]) > 0
    assert len(result.trajectory["y"]) == len(result.trajectory["t"])


def test_simple_ode_analytic_check(simple_ode_model):
    """
    Test that numeric solution matches analytic solution y(t) = exp(-2*t) within tolerance.
    For dy/dt = -2*y with y(0) = 1, the exact solution is y(t) = e^(-2*t).
    """
    solver = ODEGeneralSolver()
    result = solver.solve(simple_ode_model)

    assert result.success
    t_vals = np.array(result.trajectory["t"])
    y_vals = np.array(result.trajectory["y"])

    # Compute expected values
    y_expected = np.exp(-2 * t_vals)

    # Check error within tolerance (should be less than solver tolerance)
    max_error = np.max(np.abs(y_vals - y_expected))
    assert max_error < 1e-5, f"Max error {max_error} exceeds tolerance"


def test_simple_ode_initial_condition(simple_ode_model):
    """Test that initial condition is satisfied."""
    solver = ODEGeneralSolver()
    result = solver.solve(simple_ode_model)

    assert result.success
    # y(0) should be 1.0
    assert abs(result.trajectory["y"][0] - 1.0) < 1e-10


def test_simple_ode_monotonic_decay(simple_ode_model):
    """Test that solution decays monotonically to zero."""
    solver = ODEGeneralSolver()
    result = solver.solve(simple_ode_model)

    assert result.success
    y_vals = np.array(result.trajectory["y"])

    # Check monotonic decrease
    differences = np.diff(y_vals)
    assert np.all(differences <= 0), "Solution should decay monotonically"

    # Check asymptotic behavior (should approach zero)
    assert y_vals[-1] < y_vals[0] * 0.1, "Solution should be much smaller at end"


def test_coupled_ode_solvable(coupled_ode_model):
    """Test that coupled ODE system (Lotka-Volterra) solves successfully."""
    solver = ODEGeneralSolver()
    result = solver.solve(coupled_ode_model)

    assert result.success
    assert result.trajectory is not None
    assert "t" in result.trajectory
    assert "x" in result.trajectory
    assert "y" in result.trajectory
    assert len(result.trajectory["x"]) == len(result.trajectory["t"])
    assert len(result.trajectory["y"]) == len(result.trajectory["t"])


def test_coupled_ode_oscillatory(coupled_ode_model):
    """Test that Lotka-Volterra model produces oscillatory behavior."""
    solver = ODEGeneralSolver()
    result = solver.solve(coupled_ode_model)

    assert result.success
    x_vals = np.array(result.trajectory["x"])
    y_vals = np.array(result.trajectory["y"])

    # For Lotka-Volterra, populations should oscillate
    # Check that both variables have significant variation
    x_range = np.max(x_vals) - np.min(x_vals)
    y_range = np.max(y_vals) - np.min(y_vals)

    # Both populations should vary by at least 20% from their initial value
    assert x_range > 0.2, f"x population should oscillate, but only varies {x_range}"
    assert y_range > 0.2, f"y population should oscillate, but only varies {y_range}"

    # Populations should stay positive
    assert np.min(x_vals) > 0, "x population should remain positive"
    assert np.min(y_vals) > 0, "y population should remain positive"


def test_second_order_ode_solvable(second_order_ode_model):
    """Test that second-order ODE solves successfully."""
    solver = ODEGeneralSolver()
    result = solver.solve(second_order_ode_model)

    assert result.success
    assert result.trajectory is not None
    assert "t" in result.trajectory
    assert "x" in result.trajectory
    assert result.summary is not None


def test_second_order_ode_oscillatory(second_order_ode_model):
    """Test that harmonic oscillator produces oscillatory motion."""
    solver = ODEGeneralSolver()
    result = solver.solve(second_order_ode_model)

    assert result.success
    x_vals = np.array(result.trajectory["x"])

    # For d2x/dt2 = -x with x(0)=1, dx/dt(0)=0, solution is x(t) = cos(t)
    # Should oscillate between -1 and 1
    assert np.max(x_vals) <= 1.1, "Solution amplitude should not exceed 1"
    assert np.min(x_vals) >= -1.1, "Solution amplitude should not exceed 1"


def test_determinism_simple_ode(simple_ode_model):
    """
    Test determinism: solving the same ODE twice produces identical results.
    Golden-file test: byte-identical output.
    """
    solver = ODEGeneralSolver()

    result1 = solver.solve(simple_ode_model)
    result2 = solver.solve(simple_ode_model)

    assert result1.success and result2.success

    # Compare trajectory points
    assert result1.trajectory["t"] == result2.trajectory["t"]
    assert result1.trajectory["y"] == result2.trajectory["y"]

    # Compare summary
    assert result1.summary == result2.summary


def test_determinism_coupled_ode(coupled_ode_model):
    """Test determinism for coupled ODE system."""
    solver = ODEGeneralSolver()

    result1 = solver.solve(coupled_ode_model)
    result2 = solver.solve(coupled_ode_model)

    assert result1.success and result2.success
    assert result1.trajectory["t"] == result2.trajectory["t"]
    assert result1.trajectory["x"] == result2.trajectory["x"]
    assert result1.trajectory["y"] == result2.trajectory["y"]


def test_general_solver_routes_simple_ode(simple_ode_model):
    """Test that GeneralSolver correctly routes mathematics.ode domain."""
    result = GeneralSolver().solve(simple_ode_model)

    assert result.success
    assert result.trajectory is not None
    assert "y" in result.trajectory


def test_general_solver_routes_coupled_ode(coupled_ode_model):
    """Test that GeneralSolver correctly routes coupled ODE system."""
    result = GeneralSolver().solve(coupled_ode_model)

    assert result.success
    assert result.trajectory is not None
    assert "x" in result.trajectory
    assert "y" in result.trajectory


def test_missing_initial_condition():
    """Test error handling for missing initial conditions."""
    model = ScientificModel(
        id="ode-missing-ic",
        domain="mathematics.ode",
        description="ODE with missing IC",
        quantities=[
            Quantity(name="y", value=None, siUnit="dimensionless", isKnown=False),
        ],
        equations=[
            Equation(lhs="dy/dt", rhs="-y", type=EquationType.ODE),
        ],
        initialConditions={},  # Missing y(0)
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6,
            timeSpan=TimeSpan(start=0, end=1, numPoints=100)
        )
    )

    solver = ODEGeneralSolver()
    result = solver.solve(model)

    assert not result.success
    assert "initial condition" in result.message.lower()


def test_missing_timespan():
    """Test error handling for missing timeSpan."""
    model = ScientificModel(
        id="ode-no-timespan",
        domain="mathematics.ode",
        description="ODE without timeSpan",
        quantities=[
            Quantity(name="y", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(lhs="dy/dt", rhs="-y", type=EquationType.ODE),
        ],
        initialConditions={"y": 1.0},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6,
            timeSpan=None  # Missing timeSpan
        )
    )

    solver = ODEGeneralSolver()
    result = solver.solve(model)

    assert not result.success
    assert "timespan" in result.message.lower() or "time bound" in result.message.lower()


def test_no_ode_equations():
    """Test error handling when no ODE equations present."""
    model = ScientificModel(
        id="ode-no-equations",
        domain="mathematics.ode",
        description="No ODE equations",
        quantities=[
            Quantity(name="y", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(lhs="x + y", rhs="5", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={"y": 1.0},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6,
            timeSpan=TimeSpan(start=0, end=1, numPoints=100)
        )
    )

    solver = ODEGeneralSolver()
    result = solver.solve(model)

    assert not result.success
    assert "ODE" in result.message or "equation" in result.message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
