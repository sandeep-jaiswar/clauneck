"""
Tests for geometry solver.
Covers area/perimeter/volume calculations and inverse solving for unknowns.
"""
import math
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.geometry import GeometrySolver


@pytest.fixture
def circle_area_model():
    """Circle area calculation: radius 5 -> area ≈ 78.54"""
    return ScientificModel(
        id="circle-area",
        domain="mathematics.geometry",
        description="Circle area given radius",
        quantities=[
            Quantity(
                name="r",
                value=5.0,
                siUnit="m",
                description="Radius",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="area",
                rhs="area_circle(r)",
                type=EquationType.ALGEBRAIC,
                description="Area of circle"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="circle area radius 5")
    )


@pytest.fixture
def circle_solve_radius_model():
    """Solve for radius given area: area 100 -> radius ≈ 5.64"""
    return ScientificModel(
        id="circle-solve-radius",
        domain="mathematics.geometry",
        description="Solve for radius given area",
        quantities=[
            Quantity(
                name="area",
                value=100.0,
                siUnit="m^2",
                description="Area",
                isKnown=True,
                dimensionVector=DimensionVector(length=2)
            ),
        ],
        equations=[
            Equation(
                lhs="radius",
                rhs="solve_for_radius_given_area",
                type=EquationType.ALGEBRAIC,
                description="Solve for radius from area"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="find radius given area 100")
    )


@pytest.fixture
def sphere_volume_model():
    """Sphere volume calculation: radius 3 -> volume ≈ 113.1"""
    return ScientificModel(
        id="sphere-volume",
        domain="mathematics.geometry",
        description="Sphere volume given radius",
        quantities=[
            Quantity(
                name="r",
                value=3.0,
                siUnit="m",
                description="Radius",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="volume",
                rhs="volume_sphere(r)",
                type=EquationType.ALGEBRAIC,
                description="Volume of sphere"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="sphere volume radius 3")
    )


@pytest.fixture
def rectangle_area_model():
    """Rectangle area calculation: length 6, width 4 -> area 24"""
    return ScientificModel(
        id="rectangle-area",
        domain="mathematics.geometry",
        description="Rectangle area given dimensions",
        quantities=[
            Quantity(
                name="length",
                value=6.0,
                siUnit="m",
                description="Length",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
            Quantity(
                name="width",
                value=4.0,
                siUnit="m",
                description="Width",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="area",
                rhs="area_rectangle(length, width)",
                type=EquationType.ALGEBRAIC,
                description="Area of rectangle"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="rectangle area 6 4")
    )


@pytest.fixture
def cylinder_volume_model():
    """Cylinder volume calculation: radius 2, height 5 -> volume ≈ 62.83"""
    return ScientificModel(
        id="cylinder-volume",
        domain="mathematics.geometry",
        description="Cylinder volume given radius and height",
        quantities=[
            Quantity(
                name="r",
                value=2.0,
                siUnit="m",
                description="Radius",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
            Quantity(
                name="h",
                value=5.0,
                siUnit="m",
                description="Height",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="volume",
                rhs="volume_cylinder(r, h)",
                type=EquationType.ALGEBRAIC,
                description="Volume of cylinder"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6,
        ),
        metadata=Metadata(source="test", originalQuery="cylinder volume r=2 h=5")
    )


def test_circle_area_solvable(circle_area_model):
    """Test that circle area calculation solves successfully."""
    solver = GeometrySolver()
    result = solver.solve(circle_area_model)

    assert result.success
    assert result.summary is not None
    assert "area" in result.summary


def test_circle_area_correct(circle_area_model):
    """Test that circle area is π*r² ≈ 78.54 for r=5."""
    solver = GeometrySolver()
    result = solver.solve(circle_area_model)

    assert result.success
    expected_area = math.pi * 5**2
    actual_area = result.summary["area"]
    assert abs(actual_area - expected_area) < 0.01, \
        f"Area {actual_area} far from expected {expected_area}"


def test_circle_solve_radius_solvable(circle_solve_radius_model):
    """Test that solving for radius given area succeeds."""
    solver = GeometrySolver()
    result = solver.solve(circle_solve_radius_model)

    assert result.success
    assert result.summary is not None
    assert "radius" in result.summary


def test_circle_solve_radius_correct(circle_solve_radius_model):
    """Test that radius is correctly solved from area 100."""
    # A = πr² = 100 → r = √(100/π) ≈ 5.64
    solver = GeometrySolver()
    result = solver.solve(circle_solve_radius_model)

    assert result.success
    expected_radius = math.sqrt(100 / math.pi)
    actual_radius = result.summary["radius"]
    assert abs(actual_radius - expected_radius) < 0.01, \
        f"Radius {actual_radius} far from expected {expected_radius}"


def test_sphere_volume_solvable(sphere_volume_model):
    """Test that sphere volume calculation solves successfully."""
    solver = GeometrySolver()
    result = solver.solve(sphere_volume_model)

    assert result.success
    assert result.summary is not None
    assert "volume" in result.summary


def test_sphere_volume_correct(sphere_volume_model):
    """Test that sphere volume is (4/3)*π*r³ ≈ 113.1 for r=3."""
    solver = GeometrySolver()
    result = solver.solve(sphere_volume_model)

    assert result.success
    expected_volume = (4/3) * math.pi * 3**3
    actual_volume = result.summary["volume"]
    assert abs(actual_volume - expected_volume) < 0.1, \
        f"Volume {actual_volume} far from expected {expected_volume}"


def test_rectangle_area_correct(rectangle_area_model):
    """Test that rectangle area = length * width = 6 * 4 = 24."""
    solver = GeometrySolver()
    result = solver.solve(rectangle_area_model)

    assert result.success
    assert result.summary is not None
    assert "area" in result.summary
    expected_area = 6.0 * 4.0
    assert abs(result.summary["area"] - expected_area) < 0.01


def test_cylinder_volume_correct(cylinder_volume_model):
    """Test that cylinder volume = π*r²*h ≈ 62.83 for r=2, h=5."""
    solver = GeometrySolver()
    result = solver.solve(cylinder_volume_model)

    assert result.success
    assert result.summary is not None
    assert "volume" in result.summary
    expected_volume = math.pi * 2**2 * 5
    assert abs(result.summary["volume"] - expected_volume) < 0.1


def test_determinism_circle_area(circle_area_model):
    """
    Test determinism: solving the same model twice produces identical results.
    Golden-file test: numeric values should be identical.
    """
    solver = GeometrySolver()

    result1 = solver.solve(circle_area_model)
    result2 = solver.solve(circle_area_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_sphere_volume(sphere_volume_model):
    """Test determinism for sphere volume calculation."""
    solver = GeometrySolver()

    result1 = solver.solve(sphere_volume_model)
    result2 = solver.solve(sphere_volume_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_general_solver_routes_circle_area(circle_area_model):
    """Test that GeneralSolver correctly routes geometry.mathematics models."""
    result = GeneralSolver().solve(circle_area_model)

    assert result.success
    assert result.summary is not None
    assert "area" in result.summary


def test_general_solver_routes_sphere_volume(sphere_volume_model):
    """Test that GeneralSolver routes sphere volume correctly."""
    result = GeneralSolver().solve(sphere_volume_model)

    assert result.success
    assert result.summary is not None
    assert "volume" in result.summary


def test_circle_perimeter_solvable():
    """Test circle perimeter calculation."""
    model = ScientificModel(
        id="circle-perimeter",
        domain="mathematics.geometry",
        description="Circle perimeter (circumference) given radius",
        quantities=[
            Quantity(
                name="r",
                value=7.0,
                siUnit="m",
                description="Radius",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="perimeter",
                rhs="perimeter_circle(r)",
                type=EquationType.ALGEBRAIC,
                description="Circumference"
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = GeometrySolver().solve(model)
    assert result.success
    expected_perimeter = 2 * math.pi * 7.0
    assert abs(result.summary["perimeter"] - expected_perimeter) < 0.01


def test_rectangle_perimeter_solvable():
    """Test rectangle perimeter calculation."""
    model = ScientificModel(
        id="rectangle-perimeter",
        domain="mathematics.geometry",
        description="Rectangle perimeter given dimensions",
        quantities=[
            Quantity(
                name="length",
                value=8.0,
                siUnit="m",
                description="Length",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
            Quantity(
                name="width",
                value=5.0,
                siUnit="m",
                description="Width",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="perimeter",
                rhs="perimeter_rectangle(length, width)",
                type=EquationType.ALGEBRAIC,
                description="Perimeter"
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = GeometrySolver().solve(model)
    assert result.success
    expected_perimeter = 2 * (8.0 + 5.0)
    assert abs(result.summary["perimeter"] - expected_perimeter) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
