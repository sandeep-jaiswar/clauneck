"""Tests for special relativity solver."""
import math
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_special_relativity import PhysicsSpecialRelativitySolver


# Speed of light constant for reference calculations
C = 299792458  # m/s


@pytest.fixture
def lorentz_factor_model():
    """Model for Lorentz factor calculation: γ = 1 / √(1 - v²/c²)."""
    return ScientificModel(
        id="sr-lorentz",
        domain="physics.special_relativity",
        description="Lorentz factor",
        quantities=[
            Quantity(name="v", value=0.9 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="gamma", rhs="lorentz_factor(v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def time_dilation_model():
    """Model for time dilation calculation: t = t0 * γ."""
    return ScientificModel(
        id="sr-time-dilation",
        domain="physics.special_relativity",
        description="Time dilation",
        quantities=[
            Quantity(name="t0", value=2.2e-6, siUnit="s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.9 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="t", rhs="time_dilation(t0, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def length_contraction_model():
    """Model for length contraction calculation: L = L0 * √(1 - v²/c²)."""
    return ScientificModel(
        id="sr-length-contraction",
        domain="physics.special_relativity",
        description="Length contraction",
        quantities=[
            Quantity(name="L0", value=10.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.9 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="L", rhs="length_contraction(L0, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def relativistic_momentum_model():
    """Model for relativistic momentum calculation: p = m0 * v * γ."""
    return ScientificModel(
        id="sr-momentum",
        domain="physics.special_relativity",
        description="Relativistic momentum",
        quantities=[
            Quantity(name="m0", value=1.67e-27, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.9 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="p", rhs="relativistic_momentum(m0, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def relativistic_total_energy_model():
    """Model for relativistic total energy calculation: E = m0 * c² * γ."""
    return ScientificModel(
        id="sr-total-energy",
        domain="physics.special_relativity",
        description="Relativistic total energy",
        quantities=[
            Quantity(name="m0", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.5 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E", rhs="relativistic_total_energy(m0, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def rest_energy_model():
    """Model for rest energy calculation: E0 = m0 * c²."""
    return ScientificModel(
        id="sr-rest-energy",
        domain="physics.special_relativity",
        description="Rest energy",
        quantities=[
            Quantity(name="m0", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E0", rhs="rest_energy(m0, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def relativistic_kinetic_energy_model():
    """Model for relativistic kinetic energy calculation: KE = (γ - 1) * m0 * c²."""
    return ScientificModel(
        id="sr-kinetic-energy",
        domain="physics.special_relativity",
        description="Relativistic kinetic energy",
        quantities=[
            Quantity(name="m0", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.5 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="KE", rhs="relativistic_kinetic_energy(m0, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def relativistic_velocity_addition_model():
    """Model for relativistic velocity addition: w = (u + v) / (1 + uv/c²)."""
    return ScientificModel(
        id="sr-velocity-addition",
        domain="physics.special_relativity",
        description="Relativistic velocity addition",
        quantities=[
            Quantity(name="u", value=0.6 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=0.5 * C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="w", rhs="relativistic_velocity_addition(u, v, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def energy_momentum_relation_model():
    """Model for energy-momentum relation: E = √((pc)² + (m0c²)²)."""
    return ScientificModel(
        id="sr-energy-momentum",
        domain="physics.special_relativity",
        description="Energy-momentum relation",
        quantities=[
            Quantity(name="m0", value=1.0, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="p", value=1e8, siUnit="kg*m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=C, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E", rhs="energy_momentum_relation(m0, p, c)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_lorentz_factor_solvable(lorentz_factor_model):
    """Test that Lorentz factor solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(lorentz_factor_model)

    assert result.success
    assert "gamma" in result.summary


def test_lorentz_factor_correctness(lorentz_factor_model):
    """Test Lorentz factor: γ = 1 / √(1 - v²/c²) with v=0.9c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(lorentz_factor_model)

    assert result.success
    # Expected: γ = 1 / √(1 - 0.9²) = 1 / √(1 - 0.81) = 1 / √0.19 ≈ 2.2942
    beta = 0.9
    expected_gamma = 1.0 / math.sqrt(1.0 - beta**2)
    assert abs(result.summary["gamma"] - expected_gamma) < 1e-4


def test_time_dilation_solvable(time_dilation_model):
    """Test that time dilation solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(time_dilation_model)

    assert result.success
    assert "t" in result.summary


def test_time_dilation_correctness(time_dilation_model):
    """Test time dilation: t = t0 * γ with t0=2.2e-6 s, v=0.9c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(time_dilation_model)

    assert result.success
    # Expected: t = 2.2e-6 * γ where γ ≈ 2.2942
    beta = 0.9
    gamma = 1.0 / math.sqrt(1.0 - beta**2)
    expected_t = 2.2e-6 * gamma
    assert abs(result.summary["t"] - expected_t) < 1e-12


def test_length_contraction_solvable(length_contraction_model):
    """Test that length contraction solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(length_contraction_model)

    assert result.success
    assert "L" in result.summary


def test_length_contraction_correctness(length_contraction_model):
    """Test length contraction: L = L0 * √(1 - v²/c²) with L0=10, v=0.9c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(length_contraction_model)

    assert result.success
    # Expected: L = 10 * √(1 - 0.81) = 10 * √0.19 ≈ 4.3589
    beta = 0.9
    expected_L = 10.0 * math.sqrt(1.0 - beta**2)
    assert abs(result.summary["L"] - expected_L) < 1e-3


def test_relativistic_momentum_solvable(relativistic_momentum_model):
    """Test that relativistic momentum solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_momentum_model)

    assert result.success
    assert "p" in result.summary


def test_relativistic_momentum_correctness(relativistic_momentum_model):
    """Test relativistic momentum: p = m0 * v * γ."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_momentum_model)

    assert result.success
    # Expected: p = m0 * v * γ
    m0 = 1.67e-27
    v = 0.9 * C
    beta = 0.9
    gamma = 1.0 / math.sqrt(1.0 - beta**2)
    expected_p = m0 * v * gamma
    assert abs(result.summary["p"] - expected_p) < 1e-19


def test_relativistic_total_energy_solvable(relativistic_total_energy_model):
    """Test that relativistic total energy solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_total_energy_model)

    assert result.success
    assert "E" in result.summary


def test_relativistic_total_energy_correctness(relativistic_total_energy_model):
    """Test relativistic total energy: E = m0 * c² * γ with m0=1, v=0.5c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_total_energy_model)

    assert result.success
    # Expected: E = 1 * c² * γ where γ = 1/√(1 - 0.25) = 1/√0.75 ≈ 1.1547
    m0 = 1.0
    beta = 0.5
    gamma = 1.0 / math.sqrt(1.0 - beta**2)
    expected_E = m0 * (C ** 2) * gamma
    assert abs(result.summary["E"] - expected_E) < 1e9


def test_rest_energy_solvable(rest_energy_model):
    """Test that rest energy solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(rest_energy_model)

    assert result.success
    assert "E0" in result.summary


def test_rest_energy_correctness(rest_energy_model):
    """Test rest energy: E0 = m0 * c² with m0=1 kg."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(rest_energy_model)

    assert result.success
    # Expected: E0 = 1 * (299792458)² ≈ 8.987552e16 J
    m0 = 1.0
    expected_E0 = m0 * (C ** 2)
    assert abs(result.summary["E0"] - expected_E0) < 1e9


def test_relativistic_kinetic_energy_solvable(relativistic_kinetic_energy_model):
    """Test that relativistic kinetic energy solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_kinetic_energy_model)

    assert result.success
    assert "KE" in result.summary


def test_relativistic_kinetic_energy_correctness(relativistic_kinetic_energy_model):
    """Test relativistic kinetic energy: KE = (γ - 1) * m0 * c² with m0=1, v=0.5c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_kinetic_energy_model)

    assert result.success
    # Expected: KE = (γ - 1) * m0 * c²
    m0 = 1.0
    beta = 0.5
    gamma = 1.0 / math.sqrt(1.0 - beta**2)
    expected_KE = (gamma - 1.0) * m0 * (C ** 2)
    assert abs(result.summary["KE"] - expected_KE) < 1e9


def test_relativistic_velocity_addition_solvable(relativistic_velocity_addition_model):
    """Test that relativistic velocity addition solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_velocity_addition_model)

    assert result.success
    assert "w" in result.summary


def test_relativistic_velocity_addition_correctness(relativistic_velocity_addition_model):
    """Test relativistic velocity addition: w = (u + v) / (1 + uv/c²) with u=0.6c, v=0.5c."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(relativistic_velocity_addition_model)

    assert result.success
    # Expected: w = (0.6c + 0.5c) / (1 + 0.6*0.5) = 1.1c / 1.3
    u = 0.6 * C
    v = 0.5 * C
    expected_w = (u + v) / (1.0 + (u * v) / (C ** 2))
    assert abs(result.summary["w"] - expected_w) < 1e6


def test_energy_momentum_relation_solvable(energy_momentum_relation_model):
    """Test that energy-momentum relation solves successfully."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(energy_momentum_relation_model)

    assert result.success
    assert "E" in result.summary


def test_energy_momentum_relation_correctness(energy_momentum_relation_model):
    """Test energy-momentum relation: E = √((pc)² + (m0c²)²)."""
    solver = PhysicsSpecialRelativitySolver()
    result = solver.solve(energy_momentum_relation_model)

    assert result.success
    # Expected: E = √((pc)² + (m0c²)²)
    m0 = 1.0
    p = 1e8
    pc_squared = (p * C) ** 2
    m0c2_squared = (m0 * (C ** 2)) ** 2
    expected_E = math.sqrt(pc_squared + m0c2_squared)
    assert abs(result.summary["E"] - expected_E) < 1e9


# ============ Determinism Tests ============

def test_determinism_lorentz_factor(lorentz_factor_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsSpecialRelativitySolver()

    result1 = solver.solve(lorentz_factor_model)
    result2 = solver.solve(lorentz_factor_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_time_dilation(time_dilation_model):
    """Test determinism for time dilation."""
    solver = PhysicsSpecialRelativitySolver()

    result1 = solver.solve(time_dilation_model)
    result2 = solver.solve(time_dilation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_rest_energy(rest_energy_model):
    """Test determinism for rest energy."""
    solver = PhysicsSpecialRelativitySolver()

    result1 = solver.solve(rest_energy_model)
    result2 = solver.solve(rest_energy_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("lorentz_factor(v, c)", {"v": 299792458, "c": 299792458}, "Velocity must be 0 ≤ v < c"),
        ("lorentz_factor(v, c)", {"v": 3e8, "c": 299792458}, "Velocity must be 0 ≤ v < c"),
        ("lorentz_factor(v, c)", {"v": -1e7, "c": 299792458}, "Velocity must be 0 ≤ v < c"),
        ("time_dilation(t0, v, c)", {"t0": -1e-6, "v": 1e8, "c": 299792458}, "Proper time t0 must be non-negative"),
        ("length_contraction(L0, v, c)", {"L0": -10.0, "v": 1e8, "c": 299792458}, "Rest length L0 must be non-negative"),
        ("relativistic_momentum(m0, v, c)", {"m0": -1e-27, "v": 1e8, "c": 299792458}, "Rest mass m0 must be positive"),
        ("relativistic_momentum(m0, v, c)", {"m0": 1e-27, "v": 3e8, "c": 299792458}, "Velocity must be 0 ≤ v < c"),
        ("rest_energy(m0, c)", {"m0": 0, "c": 299792458}, "Rest mass m0 must be positive"),
        ("energy_momentum_relation(m0, p, c)", {"m0": -1.0, "p": 1e8, "c": 299792458}, "Rest mass m0 must be positive"),
        ("energy_momentum_relation(m0, p, c)", {"m0": 1.0, "p": -1e8, "c": 299792458}, "Momentum p must be non-negative"),
    ],
)
def test_special_relativity_validation(lorentz_factor_model, operation, quantities, expected_error):
    """Test error handling for invalid special relativity parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    equation = lorentz_factor_model.equations[0].model_copy(update={"rhs": operation})
    model = lorentz_factor_model.model_copy(update={
        "quantities": model_quantities,
        "equations": [equation],
    })

    result = PhysicsSpecialRelativitySolver().solve(model)

    assert not result.success
    assert expected_error in result.error


# ============ Routing Tests ============

def test_general_solver_routes_special_relativity(lorentz_factor_model):
    """Test that GeneralSolver routes to special relativity solver."""
    result = GeneralSolver().solve(lorentz_factor_model)

    assert result.success
    assert "gamma" in result.summary
