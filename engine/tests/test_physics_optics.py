"""Tests for optics solver."""
import math
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_optics import PhysicsOpticsSolver


@pytest.fixture
def thin_lens_model():
    """Model for thin lens image distance calculation: 1/f = 1/d_o + 1/d_i."""
    return ScientificModel(
        id="optics-thin-lens",
        domain="physics.optics",
        description="Thin lens image distance",
        quantities=[
            Quantity(name="f", value=0.1, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d_o", value=0.2, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="d_i", rhs="thin_lens_image_distance(f, d_o)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def magnification_model():
    """Model for optical magnification calculation."""
    return ScientificModel(
        id="optics-magnification",
        domain="physics.optics",
        description="Optical magnification",
        quantities=[
            Quantity(name="d_i", value=-0.2, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d_o", value=0.2, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="m", rhs="magnification_optical(d_i, d_o)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def snells_law_model():
    """Model for Snell's law refraction angle calculation."""
    return ScientificModel(
        id="optics-snells",
        domain="physics.optics",
        description="Snell's law refraction",
        quantities=[
            Quantity(name="n1", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="theta1", value=45.0, siUnit="deg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n2", value=1.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta2", rhs="snells_law_angle2(n1, theta1, n2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def critical_angle_model():
    """Model for critical angle calculation."""
    return ScientificModel(
        id="optics-critical-angle",
        domain="physics.optics",
        description="Critical angle for total internal reflection",
        quantities=[
            Quantity(name="n1", value=1.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n2", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta_c", rhs="critical_angle(n1, n2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def double_slit_model():
    """Model for double slit fringe spacing calculation."""
    return ScientificModel(
        id="optics-double-slit",
        domain="physics.optics",
        description="Double slit fringe spacing",
        quantities=[
            Quantity(name="wavelength", value=500e-9, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=1e-3, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_y", rhs="double_slit_fringe_spacing(wavelength, L, d)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def lensmaker_model():
    """Model for lensmaker's equation."""
    return ScientificModel(
        id="optics-lensmaker",
        domain="physics.optics",
        description="Lensmaker's equation",
        quantities=[
            Quantity(name="n", value=1.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R1", value=0.1, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="R2", value=-0.1, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="f", rhs="lensmaker_focal_length(n, R1, R2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def lens_power_model():
    """Model for lens power calculation."""
    return ScientificModel(
        id="optics-lens-power",
        domain="physics.optics",
        description="Lens power",
        quantities=[
            Quantity(name="f", value=0.05, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="P", rhs="lens_power(f)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_thin_lens_image_distance_solvable(thin_lens_model):
    """Test that thin lens image distance solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(thin_lens_model)

    assert result.success
    assert "d_i" in result.summary


def test_thin_lens_image_distance_correctness(thin_lens_model):
    """Test thin lens equation: 1/f = 1/d_o + 1/d_i with f=0.1, d_o=0.2."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(thin_lens_model)

    assert result.success
    # Expected: 1/0.1 = 1/0.2 + 1/d_i -> 10 = 5 + 1/d_i -> d_i = 0.2
    expected_d_i = 1.0 / (1.0 / 0.1 - 1.0 / 0.2)
    assert abs(result.summary["d_i"] - expected_d_i) < 1e-9


def test_magnification_solvable(magnification_model):
    """Test that magnification solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(magnification_model)

    assert result.success
    assert "m" in result.summary


def test_magnification_correctness(magnification_model):
    """Test magnification: m = -d_i/d_o with d_i=-0.2, d_o=0.2."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(magnification_model)

    assert result.success
    # Expected: m = -(-0.2)/0.2 = 1.0
    expected_m = -(-0.2) / 0.2
    assert abs(result.summary["m"] - expected_m) < 1e-9


def test_snells_law_solvable(snells_law_model):
    """Test that Snell's law solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(snells_law_model)

    assert result.success
    assert "theta2" in result.summary


def test_snells_law_correctness(snells_law_model):
    """Test Snell's law: n1*sin(θ1) = n2*sin(θ2) with n1=1.0, θ1=45°, n2=1.5."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(snells_law_model)

    assert result.success
    # Expected: sin(θ2) = (1.0/1.5)*sin(45°)
    expected_sin_theta2 = (1.0 / 1.5) * math.sin(math.radians(45.0))
    expected_theta2 = math.degrees(math.asin(expected_sin_theta2))
    assert abs(result.summary["theta2"] - expected_theta2) < 1e-6


def test_critical_angle_solvable(critical_angle_model):
    """Test that critical angle solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(critical_angle_model)

    assert result.success
    assert "theta_c" in result.summary


def test_critical_angle_correctness(critical_angle_model):
    """Test critical angle: sin(θ_c) = n2/n1 with n1=1.5, n2=1.0."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(critical_angle_model)

    assert result.success
    # Expected: sin(θ_c) = 1.0/1.5 = 2/3
    expected_sin_theta_c = 1.0 / 1.5
    expected_theta_c = math.degrees(math.asin(expected_sin_theta_c))
    assert abs(result.summary["theta_c"] - expected_theta_c) < 1e-6


def test_double_slit_solvable(double_slit_model):
    """Test that double slit fringe spacing solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(double_slit_model)

    assert result.success
    assert "delta_y" in result.summary


def test_double_slit_correctness(double_slit_model):
    """Test double slit: Δy = λL/d with λ=500nm, L=1m, d=1mm."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(double_slit_model)

    assert result.success
    # Expected: Δy = 500e-9 * 1.0 / 1e-3 = 5e-4 m = 0.5 mm
    expected_delta_y = 500e-9 * 1.0 / 1e-3
    assert abs(result.summary["delta_y"] - expected_delta_y) < 1e-12


def test_lensmaker_equation_solvable(lensmaker_model):
    """Test that lensmaker's equation solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(lensmaker_model)

    assert result.success
    assert "f" in result.summary


def test_lensmaker_equation_correctness(lensmaker_model):
    """Test lensmaker's equation: 1/f = (n-1)(1/R1 - 1/R2) with n=1.5, R1=0.1, R2=-0.1."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(lensmaker_model)

    assert result.success
    # Expected: 1/f = (1.5-1)(1/0.1 - 1/(-0.1)) = 0.5 * (10 + 10) = 10 -> f = 0.1
    expected_f = 1.0 / ((1.5 - 1.0) * (1.0 / 0.1 - 1.0 / (-0.1)))
    assert abs(result.summary["f"] - expected_f) < 1e-9


def test_lens_power_solvable(lens_power_model):
    """Test that lens power solves successfully."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(lens_power_model)

    assert result.success
    assert "P" in result.summary


def test_lens_power_correctness(lens_power_model):
    """Test lens power: P = 1/f with f=0.05m."""
    solver = PhysicsOpticsSolver()
    result = solver.solve(lens_power_model)

    assert result.success
    # Expected: P = 1/0.05 = 20 diopters
    expected_P = 1.0 / 0.05
    assert abs(result.summary["P"] - expected_P) < 1e-9


# ============ Determinism Tests ============

def test_determinism_thin_lens(thin_lens_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(thin_lens_model)
    result2 = solver.solve(thin_lens_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_magnification(magnification_model):
    """Test determinism for magnification."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(magnification_model)
    result2 = solver.solve(magnification_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_snells_law(snells_law_model):
    """Test determinism for Snell's law."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(snells_law_model)
    result2 = solver.solve(snells_law_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_critical_angle(critical_angle_model):
    """Test determinism for critical angle."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(critical_angle_model)
    result2 = solver.solve(critical_angle_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_double_slit(double_slit_model):
    """Test determinism for double slit."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(double_slit_model)
    result2 = solver.solve(double_slit_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_lensmaker(lensmaker_model):
    """Test determinism for lensmaker's equation."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(lensmaker_model)
    result2 = solver.solve(lensmaker_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_lens_power(lens_power_model):
    """Test determinism for lens power."""
    solver = PhysicsOpticsSolver()

    result1 = solver.solve(lens_power_model)
    result2 = solver.solve(lens_power_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("thin_lens_image_distance(f, d_o)", {"f": 0, "d_o": 0.2}, "Focal length f must be non-zero"),
        ("thin_lens_image_distance(f, d_o)", {"f": 0.1, "d_o": 0}, "Object distance d_o must be non-zero"),
        ("magnification_optical(d_i, d_o)", {"d_i": 0.2, "d_o": 0}, "Object distance d_o must be non-zero"),
        ("snells_law_angle2(n1, theta1, n2)", {"n1": -1.0, "theta1": 45, "n2": 1.5}, "Refractive indices must be positive"),
        ("critical_angle(n1, n2)", {"n1": 1.5, "n2": 1.5}, "First medium must be denser than second"),
        ("critical_angle(n1, n2)", {"n1": 1.0, "n2": 1.5}, "First medium must be denser than second"),
        ("double_slit_fringe_spacing(wavelength, L, d)", {"wavelength": -500e-9, "L": 1.0, "d": 1e-3}, "Wavelength must be positive"),
        ("double_slit_fringe_spacing(wavelength, L, d)", {"wavelength": 500e-9, "L": 0, "d": 1e-3}, "Distance to screen L must be positive"),
        ("double_slit_fringe_spacing(wavelength, L, d)", {"wavelength": 500e-9, "L": 1.0, "d": 0}, "Slit separation d must be positive"),
        ("lensmaker_focal_length(n, R1, R2)", {"n": 0.8, "R1": 0.1, "R2": -0.1}, "Refractive index n must be > 1"),
        ("lensmaker_focal_length(n, R1, R2)", {"n": 1.5, "R1": 0, "R2": -0.1}, "Radii R1 and R2 must be non-zero"),
        ("lens_power(f)", {"f": 0}, "Focal length f must be non-zero"),
    ],
)
def test_optics_validation(thin_lens_model, operation, quantities, expected_error):
    """Test error handling for invalid optical parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    equation = thin_lens_model.equations[0].model_copy(update={"rhs": operation})
    model = thin_lens_model.model_copy(update={
        "quantities": model_quantities,
        "equations": [equation],
    })

    result = PhysicsOpticsSolver().solve(model)

    assert not result.success
    assert expected_error in result.error


def test_snells_law_total_internal_reflection():
    """Test Snell's law error when total internal reflection occurs."""
    model = ScientificModel(
        id="optics-snells-tir",
        domain="physics.optics",
        description="Snell's law - total internal reflection",
        quantities=[
            Quantity(name="n1", value=1.5, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="theta1", value=50.0, siUnit="deg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="n2", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta2", rhs="snells_law_angle2(n1, theta1, n2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = PhysicsOpticsSolver().solve(model)
    # May succeed (no error) or fail depending on whether angle is below critical
    # For n1=1.5, n2=1.0, critical angle = arcsin(1/1.5) ≈ 41.8°
    # So 50° should trigger TIR error
    assert not result.success
    assert "exceeds 1" in result.error


def test_diffraction_grating_high_order():
    """Test diffraction grating error when order m is unobservable."""
    model = ScientificModel(
        id="optics-diffraction-high-order",
        domain="physics.optics",
        description="Diffraction grating - high order",
        quantities=[
            Quantity(name="wavelength", value=500e-9, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=1e-6, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m", value=10, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta", rhs="diffraction_grating_angle(wavelength, d, m)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = PhysicsOpticsSolver().solve(model)
    # m=10 wavelengths in d=1 micron grating spacing would require sin(θ) > 1
    assert not result.success
    assert "exceeds 1" in result.error


# ============ Routing Tests ============

def test_general_solver_routes_optics(thin_lens_model):
    """Test that GeneralSolver routes to optics solver."""
    result = GeneralSolver().solve(thin_lens_model)

    assert result.success
    assert "d_i" in result.summary


def test_mirror_equation_correctness():
    """Test mirror equation (same as lens formula)."""
    model = ScientificModel(
        id="optics-mirror",
        domain="physics.optics",
        description="Mirror image distance",
        quantities=[
            Quantity(name="f", value=0.15, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d_o", value=0.3, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="d_i", rhs="mirror_image_distance(f, d_o)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsOpticsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: 1/0.15 = 1/0.3 + 1/d_i -> d_i = 0.3
    expected_d_i = 1.0 / (1.0 / 0.15 - 1.0 / 0.3)
    assert abs(result.summary["d_i"] - expected_d_i) < 1e-9


def test_diffraction_grating_correctness():
    """Test diffraction grating angle: d*sin(θ) = m*λ."""
    model = ScientificModel(
        id="optics-diffraction-grating",
        domain="physics.optics",
        description="Diffraction grating angle",
        quantities=[
            Quantity(name="wavelength", value=600e-9, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="d", value=2e-6, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="theta", rhs="diffraction_grating_angle(wavelength, d, m)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsOpticsSolver()
    result = solver.solve(model)

    assert result.success
    # Expected: sin(θ) = (1.0 * 600e-9) / 2e-6 = 0.3
    expected_sin_theta = (1.0 * 600e-9) / 2e-6
    expected_theta = math.degrees(math.asin(expected_sin_theta))
    assert abs(result.summary["theta"] - expected_theta) < 1e-6
