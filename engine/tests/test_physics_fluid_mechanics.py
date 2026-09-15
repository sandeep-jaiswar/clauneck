"""Tests for fluid mechanics solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_fluid_mechanics import PhysicsFluidMechanicsSolver


@pytest.fixture
def hydrostatic_pressure_model():
    """Model for hydrostatic pressure calculation: P = P0 + ρ⋅g⋅h."""
    return ScientificModel(
        id="fluid-hydrostatic",
        domain="physics.fluid_mechanics",
        description="Hydrostatic pressure",
        quantities=[
            Quantity(name="P0", value=101325.0, siUnit="Pa", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="rho", value=1000.0, siUnit="kg/m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="h", value=10.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="P", rhs="hydrostatic_pressure(P0, rho, g, h)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def buoyant_force_model():
    """Model for buoyant force calculation: F_b = ρ⋅V⋅g."""
    return ScientificModel(
        id="fluid-buoyancy",
        domain="physics.fluid_mechanics",
        description="Buoyant force",
        quantities=[
            Quantity(name="rho_fluid", value=1000.0, siUnit="kg/m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="V_displaced", value=0.002, siUnit="m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="F_b", rhs="buoyant_force(rho_fluid, V_displaced, g)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def continuity_model():
    """Model for continuity equation: v2 = A1⋅v1 / A2."""
    return ScientificModel(
        id="fluid-continuity",
        domain="physics.fluid_mechanics",
        description="Continuity equation",
        quantities=[
            Quantity(name="A1", value=0.01, siUnit="m^2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v1", value=2.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="A2", value=0.005, siUnit="m^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v2", rhs="continuity_velocity2(A1, v1, A2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def bernoulli_model():
    """Model for Bernoulli's equation: P2 = P1 + 0.5⋅ρ⋅(v1² - v2²) + ρ⋅g⋅(h1 - h2)."""
    return ScientificModel(
        id="fluid-bernoulli",
        domain="physics.fluid_mechanics",
        description="Bernoulli's equation",
        quantities=[
            Quantity(name="P1", value=101325.0, siUnit="Pa", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="rho", value=1000.0, siUnit="kg/m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v1", value=1.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="h1", value=0.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v2", value=2.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="h2", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="P2", rhs="bernoulli_pressure2(P1, rho, v1, h1, v2, h2, g)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def reynolds_model():
    """Model for Reynolds number: Re = ρ⋅v⋅L / η."""
    return ScientificModel(
        id="fluid-reynolds",
        domain="physics.fluid_mechanics",
        description="Reynolds number",
        quantities=[
            Quantity(name="rho", value=1.225, siUnit="kg/m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=10.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="eta", value=1.81e-5, siUnit="Pa*s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="Re", rhs="reynolds_number(rho, v, L, eta)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def poiseuille_model():
    """Model for Poiseuille flow rate: Q = π⋅ΔP⋅r⁴ / (8⋅η⋅L)."""
    return ScientificModel(
        id="fluid-poiseuille",
        domain="physics.fluid_mechanics",
        description="Poiseuille flow rate",
        quantities=[
            Quantity(name="delta_P", value=1000.0, siUnit="Pa", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="r", value=0.001, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="eta", value=0.001, siUnit="Pa*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="Q", rhs="poiseuille_flow_rate(delta_P, r, eta, L)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def torricelli_model():
    """Model for Torricelli efflux velocity: v = √(2⋅g⋅h)."""
    return ScientificModel(
        id="fluid-torricelli",
        domain="physics.fluid_mechanics",
        description="Torricelli efflux velocity",
        quantities=[
            Quantity(name="g", value=9.81, siUnit="m/s^2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="h", value=5.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v", rhs="torricelli_efflux_velocity(g, h)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def drag_force_model():
    """Model for drag force: F_d = 0.5⋅Cd⋅ρ⋅A⋅v²."""
    return ScientificModel(
        id="fluid-drag",
        domain="physics.fluid_mechanics",
        description="Drag force",
        quantities=[
            Quantity(name="Cd", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="rho", value=1.225, siUnit="kg/m^3", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="A", value=2.0, siUnit="m^2", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=20.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="F_d", rhs="drag_force(Cd, rho, A, v)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_hydrostatic_pressure_solvable(hydrostatic_pressure_model):
    """Test that hydrostatic pressure solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(hydrostatic_pressure_model)

    assert result.success
    assert "P" in result.summary


def test_hydrostatic_pressure_correctness(hydrostatic_pressure_model):
    """Test hydrostatic pressure: P = P0 + ρ⋅g⋅h with typical ocean depth."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(hydrostatic_pressure_model)

    assert result.success
    # Expected: P = 101325 + 1000 * 9.81 * 10 = 199125 Pa
    expected_P = 101325.0 + 1000.0 * 9.81 * 10.0
    assert abs(result.summary["P"] - expected_P) < 1.0  # Pa precision


def test_buoyant_force_solvable(buoyant_force_model):
    """Test that buoyant force solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(buoyant_force_model)

    assert result.success
    assert "F_b" in result.summary


def test_buoyant_force_correctness(buoyant_force_model):
    """Test buoyant force: F_b = ρ⋅V⋅g for displaced water volume."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(buoyant_force_model)

    assert result.success
    # Expected: F_b = 1000 * 0.002 * 9.81 = 19.62 N
    expected_F_b = 1000.0 * 0.002 * 9.81
    assert abs(result.summary["F_b"] - expected_F_b) < 0.01  # N precision


def test_continuity_solvable(continuity_model):
    """Test that continuity equation solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(continuity_model)

    assert result.success
    assert "v2" in result.summary


def test_continuity_correctness(continuity_model):
    """Test continuity equation: v2 = A1⋅v1 / A2 (conservation of mass)."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(continuity_model)

    assert result.success
    # Expected: v2 = 0.01 * 2.0 / 0.005 = 4.0 m/s
    expected_v2 = 0.01 * 2.0 / 0.005
    assert abs(result.summary["v2"] - expected_v2) < 1e-6


def test_bernoulli_solvable(bernoulli_model):
    """Test that Bernoulli's equation solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(bernoulli_model)

    assert result.success
    assert "P2" in result.summary


def test_bernoulli_correctness(bernoulli_model):
    """Test Bernoulli's equation: P2 = P1 + 0.5⋅ρ⋅(v1² - v2²) + ρ⋅g⋅(h1 - h2)."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(bernoulli_model)

    assert result.success
    # Expected: P2 = 101325 + 0.5*1000*(1² - 2²) + 1000*9.81*(0 - 1)
    #              = 101325 - 1500 - 9810 = 90015 Pa
    g = 9.81
    expected_P2 = 101325.0 + 0.5 * 1000.0 * (1.0**2 - 2.0**2) + 1000.0 * g * (0.0 - 1.0)
    assert abs(result.summary["P2"] - expected_P2) < 1.0  # Pa precision


def test_reynolds_solvable(reynolds_model):
    """Test that Reynolds number solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(reynolds_model)

    assert result.success
    assert "Re" in result.summary


def test_reynolds_correctness(reynolds_model):
    """Test Reynolds number: Re = ρ⋅v⋅L / η for air flow."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(reynolds_model)

    assert result.success
    # Expected: Re = 1.225 * 10 * 1.0 / 1.81e-5 ≈ 676,243
    expected_Re = 1.225 * 10.0 * 1.0 / 1.81e-5
    assert abs(result.summary["Re"] - expected_Re) < 100  # unitless, turbulent regime


def test_drag_force_solvable(drag_force_model):
    """Test that drag force solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(drag_force_model)

    assert result.success
    assert "F_d" in result.summary


def test_drag_force_correctness(drag_force_model):
    """Test drag force: F_d = 0.5⋅Cd⋅ρ⋅A⋅v²."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(drag_force_model)

    assert result.success
    # Expected: F_d = 0.5 * 1.0 * 1.225 * 2.0 * 20² = 0.5 * 1.225 * 2 * 400 = 490 N
    expected_F_d = 0.5 * 1.0 * 1.225 * 2.0 * 20.0**2
    assert abs(result.summary["F_d"] - expected_F_d) < 1.0  # N precision


def test_poiseuille_solvable(poiseuille_model):
    """Test that Poiseuille flow rate solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(poiseuille_model)

    assert result.success
    assert "Q" in result.summary


def test_poiseuille_correctness(poiseuille_model):
    """Test Poiseuille flow rate: Q = π⋅ΔP⋅r⁴ / (8⋅η⋅L)."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(poiseuille_model)

    assert result.success
    # Expected: Q = π * 1000 * (0.001)^4 / (8 * 0.001 * 1.0)
    expected_Q = np.pi * 1000.0 * (0.001)**4 / (8 * 0.001 * 1.0)
    assert abs(result.summary["Q"] - expected_Q) < 1e-10  # m^3/s precision


def test_torricelli_solvable(torricelli_model):
    """Test that Torricelli efflux velocity solves successfully."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(torricelli_model)

    assert result.success
    assert "v" in result.summary


def test_torricelli_correctness(torricelli_model):
    """Test Torricelli efflux velocity: v = sqrt(2*g*h)."""
    solver = PhysicsFluidMechanicsSolver()
    result = solver.solve(torricelli_model)

    assert result.success
    # Expected: v = sqrt(2 * 9.81 * 5) = sqrt(98.1) ~= 9.904 m/s
    expected_v = np.sqrt(2 * 9.81 * 5.0)
    assert abs(result.summary["v"] - expected_v) < 1e-6  # m/s precision


# ============ Determinism Tests ============

def test_determinism_hydrostatic_pressure(hydrostatic_pressure_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsFluidMechanicsSolver()

    result1 = solver.solve(hydrostatic_pressure_model)
    result2 = solver.solve(hydrostatic_pressure_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_continuity(continuity_model):
    """Test determinism for continuity equation."""
    solver = PhysicsFluidMechanicsSolver()

    result1 = solver.solve(continuity_model)
    result2 = solver.solve(continuity_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_bernoulli(bernoulli_model):
    """Test determinism for Bernoulli's equation."""
    solver = PhysicsFluidMechanicsSolver()

    result1 = solver.solve(bernoulli_model)
    result2 = solver.solve(bernoulli_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_poiseuille(poiseuille_model):
    """Test determinism for Poiseuille flow rate."""
    solver = PhysicsFluidMechanicsSolver()

    result1 = solver.solve(poiseuille_model)
    result2 = solver.solve(poiseuille_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_torricelli(torricelli_model):
    """Test determinism for Torricelli efflux velocity."""
    solver = PhysicsFluidMechanicsSolver()

    result1 = solver.solve(torricelli_model)
    result2 = solver.solve(torricelli_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("hydrostatic_pressure(P0, rho, g, h)", {"P0": 101325, "rho": -1, "g": 9.81, "h": 10}, "Density and height must be non-negative"),
        ("hydrostatic_pressure(P0, rho, g, h)", {"P0": 101325, "rho": 1000, "g": 9.81, "h": -1}, "Density and height must be non-negative"),
        ("buoyant_force(rho_fluid, V_displaced, g)", {"rho_fluid": -1, "V_displaced": 0.002, "g": 9.81}, "Density and volume must be non-negative"),
        ("continuity_velocity2(A1, v1, A2)", {"A1": 0.01, "v1": 2.0, "A2": 0}, "Cross-sectional area A2 must be greater than 0"),
        ("bernoulli_pressure2(P1, rho, v1, h1, v2, h2, g)", {"P1": 101325, "rho": -1, "v1": 1.0, "h1": 0, "v2": 2.0, "h2": 1.0, "g": 9.81}, "Density must be non-negative"),
        ("bernoulli_pressure2(P1, rho, v1, h1, v2, h2, g)", {"P1": 101325, "rho": 1000, "v1": 1.0, "h1": 0, "v2": 2.0, "h2": 1.0, "g": 0}, "Gravitational acceleration must be greater than 0"),
        ("poiseuille_flow_rate(delta_P, r, eta, L)", {"delta_P": 1000, "r": 0, "eta": 1e-3, "L": 1}, "Radius, viscosity, and length must be greater than 0"),
        ("reynolds_number(rho, v, L, eta)", {"rho": 1.225, "v": 10, "L": 1, "eta": 0}, "viscosity must be positive"),
        ("torricelli_efflux_velocity(g, h)", {"g": -9.81, "h": 10}, "Gravitational acceleration must be positive"),
        ("drag_force(Cd, rho, A, v)", {"Cd": -1, "rho": 1.225, "A": 2, "v": 20}, "Drag coefficient, density, and area must be non-negative"),
    ],
)
def test_fluid_mechanics_validation(hydrostatic_pressure_model, operation, quantities, expected_error):
    """Test error handling for invalid fluid mechanics parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    equation = hydrostatic_pressure_model.equations[0].model_copy(update={"rhs": operation})
    model = hydrostatic_pressure_model.model_copy(update={
        "quantities": model_quantities,
        "equations": [equation],
    })

    result = PhysicsFluidMechanicsSolver().solve(model)

    assert not result.success
    assert expected_error in result.error


# ============ Routing Tests ============

def test_general_solver_routes_fluid_mechanics(hydrostatic_pressure_model):
    """Test that GeneralSolver routes to fluid mechanics solver."""
    result = GeneralSolver().solve(hydrostatic_pressure_model)

    assert result.success
    assert "P" in result.summary
