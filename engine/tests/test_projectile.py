"""
Tests for projectile motion solver.
Golden-file tests for determinism: same model → same output.
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    TimeSpan, Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_mechanics import ProjectileMotionSolver


@pytest.fixture
def projectile_model():
    """Basic projectile motion model (no drag)."""
    return ScientificModel(
        id="projectile-no-drag",
        domain="physics.mechanics",
        description="Projectile motion without air resistance",
        quantities=[
            Quantity(
                name="v0",
                value=20.0,
                siUnit="m/s",
                description="Initial velocity",
                isKnown=True,
                dimensionVector=DimensionVector(length=1, time=-1)
            ),
            Quantity(
                name="angle",
                value=45.0,
                siUnit="deg",
                description="Launch angle",
                isKnown=True,
                dimensionVector=DimensionVector()  # dimensionless
            ),
            Quantity(
                name="mass",
                value=1.0,
                siUnit="kg",
                description="Object mass",
                isKnown=True,
                dimensionVector=DimensionVector(mass=1)
            ),
            Quantity(
                name="g",
                value=9.81,
                siUnit="m/s^2",
                description="Gravitational acceleration",
                isKnown=True,
                dimensionVector=DimensionVector(length=1, time=-2)
            ),
            Quantity(
                name="drag_coeff",
                value=0.0,
                siUnit="dimensionless",
                description="Drag coefficient (0 = no drag)",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="d2x/dt2",
                rhs="-drag_coeff * vx * |v| / mass",
                type=EquationType.ODE,
                description="Horizontal acceleration"
            ),
            Equation(
                lhs="d2y/dt2",
                rhs="-g - drag_coeff * vy * |v| / mass",
                type=EquationType.ODE,
                description="Vertical acceleration"
            ),
        ],
        initialConditions={"v0": 20.0, "angle": 45.0, "mass": 1.0, "g": 9.81, "drag_coeff": 0.0},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6,
            timeSpan=TimeSpan(start=0, end=5, numPoints=500)
        ),
        metadata=Metadata(source="test", originalQuery="projectile 20m/s 45deg")
    )


@pytest.fixture
def projectile_with_drag():
    """Projectile motion with air resistance."""
    return ScientificModel(
        id="projectile-with-drag",
        domain="physics.mechanics",
        description="Projectile motion with quadratic drag",
        quantities=[
            Quantity(name="v0", value=20.0, siUnit="m/s", isKnown=True,
                     dimensionVector=DimensionVector(length=1, time=-1)),
            Quantity(name="angle", value=45.0, siUnit="deg", isKnown=True),
            Quantity(name="mass", value=0.5, siUnit="kg", isKnown=True,
                     dimensionVector=DimensionVector(mass=1)),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True,
                     dimensionVector=DimensionVector(length=1, time=-2)),
            Quantity(name="drag_coeff", value=0.1, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(lhs="d2x/dt2", rhs="-drag_coeff * vx * |v| / mass", type=EquationType.ODE),
            Equation(lhs="d2y/dt2", rhs="-g - drag_coeff * vy * |v| / mass", type=EquationType.ODE),
        ],
        initialConditions={"v0": 20.0, "angle": 45.0, "mass": 0.5, "g": 9.81, "drag_coeff": 0.1},
        solver=Solver(
            method=SolverMethod.RK45,
            tolerance=1e-6,
            timeSpan=TimeSpan(start=0, end=5, numPoints=500)
        )
    )


def test_projectile_no_drag_solvable(projectile_model):
    """Test that projectile motion without drag solves successfully."""
    solver = ProjectileMotionSolver()
    result = solver.solve(projectile_model)

    assert result.success
    assert result.trajectory is not None
    assert "x" in result.trajectory
    assert "y" in result.trajectory
    assert result.summary is not None
    assert "max_range" in result.summary
    assert "max_height" in result.summary
    assert "flight_time" in result.summary
    assert all(y >= 0 for y in result.trajectory["y"])


def test_projectile_no_drag_range(projectile_model):
    """Test that range is approximately correct for 45° launch angle."""
    # v0 = 20 m/s, angle = 45°, g = 9.81 m/s²
    # Range ≈ v0² * sin(2*45°) / g = 400 * sin(90°) / 9.81 ≈ 40.8 m
    solver = ProjectileMotionSolver()
    result = solver.solve(projectile_model)

    assert result.success
    expected_range = 20**2 * 1 / 9.81  # sin(90°) = 1
    actual_range = result.summary["max_range"]
    assert abs(actual_range - expected_range) < 2.0, \
        f"Range {actual_range} far from expected {expected_range}"


def test_impact_summary_uses_event_at_coarse_output_resolution(projectile_model):
    """Impact time/range come from event interpolation, not the last grid sample."""
    coarse_solver = projectile_model.solver.model_copy(update={
        "timeSpan": TimeSpan(start=0, end=5, numPoints=6),
    })
    model = projectile_model.model_copy(update={"solver": coarse_solver})

    result = ProjectileMotionSolver().solve(model)

    expected_time = 2 * 20 * np.sin(np.pi / 4) / 9.81
    expected_range = 20 * np.cos(np.pi / 4) * expected_time
    assert result.success
    assert len(result.trajectory["t"]) == 3
    assert result.trajectory["t"] == [0.0, 1.0, 2.0]
    assert result.summary["flight_time"] == pytest.approx(expected_time, abs=1e-5)
    assert result.summary["max_range"] == pytest.approx(expected_range, abs=1e-4)


def test_projectile_with_drag_solvable(projectile_with_drag):
    """Test that projectile motion with drag solves successfully."""
    solver = ProjectileMotionSolver()
    result = solver.solve(projectile_with_drag)

    assert result.success
    assert result.trajectory is not None
    assert result.summary is not None


def test_projectile_with_drag_reduces_range(projectile_model, projectile_with_drag):
    """Test that drag reduces range compared to no-drag case."""
    solver = ProjectileMotionSolver()

    no_drag_result = solver.solve(projectile_model)
    with_drag_result = solver.solve(projectile_with_drag)

    assert no_drag_result.success
    assert with_drag_result.success

    no_drag_range = no_drag_result.summary["max_range"]
    with_drag_range = with_drag_result.summary["max_range"]

    assert with_drag_range < no_drag_range, \
        f"Drag should reduce range: {with_drag_range} >= {no_drag_range}"


def test_determinism(projectile_model):
    """
    Test determinism: solving the same model twice produces identical results.
    Golden-file test: byte-identical output.
    """
    solver = ProjectileMotionSolver()

    result1 = solver.solve(projectile_model)
    result2 = solver.solve(projectile_model)

    assert result1.success and result2.success

    # Compare trajectory points
    assert result1.trajectory["t"] == result2.trajectory["t"]
    assert result1.trajectory["x"] == result2.trajectory["x"]
    assert result1.trajectory["y"] == result2.trajectory["y"]

    # Compare summary
    assert result1.summary == result2.summary


def test_declared_radians_are_not_reinterpreted(projectile_model):
    """A small radian value remains radians rather than being treated as degrees."""
    quantities = [
        quantity.model_copy(update={"value": 0.5, "siUnit": "rad"})
        if quantity.name == "angle" else quantity
        for quantity in projectile_model.quantities
    ]
    initial_conditions = dict(projectile_model.initialConditions)
    initial_conditions["angle"] = 0.5
    model = projectile_model.model_copy(update={
        "quantities": quantities,
        "initialConditions": initial_conditions,
    })

    result = ProjectileMotionSolver().solve(model)

    assert result.success
    expected_range = 20**2 * np.sin(1.0) / 9.81
    assert abs(result.summary["max_range"] - expected_range) < 2.0


def test_general_solver_routes_no_drag_projectile(projectile_model):
    quantities = [
        quantity for quantity in projectile_model.quantities
        if quantity.name != "drag_coeff"
    ]
    initial_conditions = dict(projectile_model.initialConditions)
    initial_conditions.pop("drag_coeff")
    equations = [
        Equation(lhs="d2x/dt2", rhs="0", type=EquationType.ODE),
        Equation(lhs="d2y/dt2", rhs="-g", type=EquationType.ODE),
    ]
    model = projectile_model.model_copy(update={
        "quantities": quantities,
        "initialConditions": initial_conditions,
        "equations": equations,
    })

    result = GeneralSolver().solve(model)

    assert result.success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
