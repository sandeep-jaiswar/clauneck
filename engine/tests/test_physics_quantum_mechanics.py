"""Tests for quantum mechanics solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_quantum_mechanics import PhysicsQuantumMechanicsSolver


@pytest.fixture
def de_broglie_model():
    """Model for de Broglie wavelength: λ = h / p."""
    return ScientificModel(
        id="quantum-de-broglie",
        domain="physics.quantum_mechanics",
        description="De Broglie wavelength",
        quantities=[
            Quantity(name="h", value=6.62607015e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="p", value=1e-24, siUnit="kg*m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="wavelength", rhs="de_broglie_wavelength(h, p)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def photon_energy_model():
    """Model for photon energy: E = h * f."""
    return ScientificModel(
        id="quantum-photon",
        domain="physics.quantum_mechanics",
        description="Photon energy",
        quantities=[
            Quantity(name="h", value=6.62607015e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="f", value=5e14, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E_photon", rhs="photon_energy(h, f)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def particle_in_box_model():
    """Model for particle in a box energy: E_n = n² * h² / (8 * m * L²)."""
    return ScientificModel(
        id="quantum-box",
        domain="physics.quantum_mechanics",
        description="Particle in a box",
        quantities=[
            Quantity(name="n", value=1.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="h", value=6.62607015e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m", value=9.1093837015e-31, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1e-10, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E_n", rhs="particle_in_box_energy(n, h, m, L)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def bohr_energy_model():
    """Model for Bohr energy level: E_n = -13.6 eV / n²."""
    return ScientificModel(
        id="quantum-bohr-energy",
        domain="physics.quantum_mechanics",
        description="Bohr energy level",
        quantities=[
            Quantity(name="n", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="E_n", rhs="bohr_energy_level(n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def bohr_radius_model():
    """Model for Bohr radius: a_n = n² * a_0."""
    return ScientificModel(
        id="quantum-bohr-radius",
        domain="physics.quantum_mechanics",
        description="Bohr orbital radius",
        quantities=[
            Quantity(name="n", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="a_n", rhs="bohr_radius(n)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def heisenberg_model():
    """Model for Heisenberg uncertainty: Δp ≥ hbar / (2 * Δx)."""
    return ScientificModel(
        id="quantum-heisenberg",
        domain="physics.quantum_mechanics",
        description="Heisenberg uncertainty momentum",
        quantities=[
            Quantity(name="delta_x", value=1e-10, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="hbar", value=1.054571817e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_p", rhs="heisenberg_uncertainty_momentum(delta_x, hbar)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def photoelectric_ke_model():
    """Model for photoelectric kinetic energy: KE = h*f - φ."""
    return ScientificModel(
        id="quantum-photoelectric-ke",
        domain="physics.quantum_mechanics",
        description="Photoelectric kinetic energy",
        quantities=[
            Quantity(name="h", value=6.62607015e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="f", value=8e14, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="phi", value=2e-19, siUnit="J", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="KE_max", rhs="photoelectric_kinetic_energy(h, f, phi)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def compton_shift_model():
    """Model for Compton shift: Δλ = (h / (m_e * c)) * (1 - cos(θ))."""
    return ScientificModel(
        id="quantum-compton",
        domain="physics.quantum_mechanics",
        description="Compton wavelength shift",
        quantities=[
            Quantity(name="h", value=6.62607015e-34, siUnit="J*s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="m_e", value=9.1093837015e-31, siUnit="kg", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="c", value=299792458.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="theta", value=np.pi / 2, siUnit="rad", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="delta_lambda", rhs="compton_shift(h, m_e, c, theta)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Correctness Tests ============

def test_de_broglie_wavelength_solvable(de_broglie_model):
    """Test that de Broglie wavelength solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(de_broglie_model)

    assert result.success
    assert "wavelength" in result.summary


def test_de_broglie_wavelength_correctness(de_broglie_model):
    """Test de Broglie wavelength: λ = h / p with h=6.626e-34, p=1e-24."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(de_broglie_model)

    assert result.success
    # Expected: λ = 6.62607015e-34 / 1e-24 = 6.62607015e-10 m
    expected = 6.62607015e-34 / 1e-24
    assert abs(result.summary["wavelength"] - expected) < 1e-20


def test_photon_energy_solvable(photon_energy_model):
    """Test that photon energy solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(photon_energy_model)

    assert result.success
    assert "E_photon" in result.summary


def test_photon_energy_correctness(photon_energy_model):
    """Test photon energy: E = h * f with h=6.626e-34, f=5e14."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(photon_energy_model)

    assert result.success
    # Expected: E = 6.62607015e-34 * 5e14 = 3.313e-19 J
    expected = 6.62607015e-34 * 5e14
    assert abs(result.summary["E_photon"] - expected) < 1e-30


def test_particle_in_box_solvable(particle_in_box_model):
    """Test that particle in a box energy solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(particle_in_box_model)

    assert result.success
    assert "E_n" in result.summary


def test_particle_in_box_correctness(particle_in_box_model):
    """Test particle in a box: E_n = n² * h² / (8 * m * L²)."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(particle_in_box_model)

    assert result.success
    # n=1, h=6.626e-34, m=9.109e-31, L=1e-10
    # E_1 = 1 * (6.626e-34)^2 / (8 * 9.109e-31 * (1e-10)^2)
    h = 6.62607015e-34
    m = 9.1093837015e-31
    L = 1e-10
    expected = (h**2) / (8.0 * m * L**2)
    assert abs(result.summary["E_n"] - expected) < 1e-50


def test_bohr_energy_solvable(bohr_energy_model):
    """Test that Bohr energy level solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(bohr_energy_model)

    assert result.success
    assert "E_n" in result.summary


def test_bohr_energy_correctness(bohr_energy_model):
    """Test Bohr energy level: E_n = -13.6 eV / n² for n=2."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(bohr_energy_model)

    assert result.success
    # E_2 = -13.6 / 4 = -3.4 eV = -3.4 * 1.602e-19 J
    e = 1.602176634e-19
    expected = (-13.6 / 4.0) * e
    assert abs(result.summary["E_n"] - expected) < 1e-38


def test_bohr_radius_solvable(bohr_radius_model):
    """Test that Bohr radius solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(bohr_radius_model)

    assert result.success
    assert "a_n" in result.summary


def test_bohr_radius_correctness(bohr_radius_model):
    """Test Bohr radius: a_n = n² * a_0 for n=2."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(bohr_radius_model)

    assert result.success
    # a_2 = 4 * a_0 = 4 * 5.291e-11 m
    a_0 = 5.29177210903e-11
    expected = 4.0 * a_0
    assert abs(result.summary["a_n"] - expected) < 1e-20


def test_heisenberg_solvable(heisenberg_model):
    """Test that Heisenberg uncertainty resolves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(heisenberg_model)

    assert result.success
    assert "delta_p" in result.summary


def test_heisenberg_correctness(heisenberg_model):
    """Test Heisenberg uncertainty: Δp ≥ hbar / (2 * Δx)."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(heisenberg_model)

    assert result.success
    # Δx = 1e-10 m, hbar = 1.055e-34
    # Δp = 1.055e-34 / (2 * 1e-10) = 5.275e-25
    hbar = 1.054571817e-34
    delta_x = 1e-10
    expected = hbar / (2.0 * delta_x)
    assert abs(result.summary["delta_p"] - expected) < 1e-40


def test_photoelectric_ke_solvable(photoelectric_ke_model):
    """Test that photoelectric kinetic energy solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(photoelectric_ke_model)

    assert result.success
    assert "KE_max" in result.summary


def test_photoelectric_ke_correctness(photoelectric_ke_model):
    """Test photoelectric KE: KE = h*f - φ."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(photoelectric_ke_model)

    assert result.success
    # h = 6.626e-34, f = 8e14, φ = 2e-19
    # KE = 6.626e-34 * 8e14 - 2e-19 = 5.301e-19 - 2e-19 = 3.301e-19
    h = 6.62607015e-34
    f = 8e14
    phi = 2e-19
    expected = h * f - phi
    assert abs(result.summary["KE_max"] - expected) < 1e-30


def test_compton_shift_solvable(compton_shift_model):
    """Test that Compton shift solves successfully."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(compton_shift_model)

    assert result.success
    assert "delta_lambda" in result.summary


def test_compton_shift_correctness(compton_shift_model):
    """Test Compton shift: Δλ = (h / (m_e * c)) * (1 - cos(θ)) at θ=π/2."""
    solver = PhysicsQuantumMechanicsSolver()
    result = solver.solve(compton_shift_model)

    assert result.success
    # θ = π/2, cos(π/2) = 0
    # Δλ = (h / (m_e * c)) * 1 = h / (m_e * c)
    h = 6.62607015e-34
    m_e = 9.1093837015e-31
    c = 299792458.0
    expected = (h / (m_e * c)) * (1.0 - np.cos(np.pi / 2))
    assert abs(result.summary["delta_lambda"] - expected) < 1e-47


# ============ Determinism Tests ============

def test_determinism_de_broglie(de_broglie_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = PhysicsQuantumMechanicsSolver()

    result1 = solver.solve(de_broglie_model)
    result2 = solver.solve(de_broglie_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_photon_energy(photon_energy_model):
    """Test determinism for photon energy."""
    solver = PhysicsQuantumMechanicsSolver()

    result1 = solver.solve(photon_energy_model)
    result2 = solver.solve(photon_energy_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_bohr_energy(bohr_energy_model):
    """Test determinism for Bohr energy level."""
    solver = PhysicsQuantumMechanicsSolver()

    result1 = solver.solve(bohr_energy_model)
    result2 = solver.solve(bohr_energy_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============ Error Path Tests ============

@pytest.mark.parametrize(
    ("operation", "quantities", "expected_error"),
    [
        ("de_broglie_wavelength(h, p)", {"h": 6.626e-34, "p": 0}, "Momentum p must be positive"),
        ("de_broglie_wavelength(h, p)", {"h": 6.626e-34, "p": -1e-24}, "Momentum p must be positive"),
        ("photon_energy(h, f)", {"h": 6.626e-34, "f": -5e14}, "Frequency f must be non-negative"),
        ("photoelectric_kinetic_energy(h, f, phi)", {"h": 6.626e-34, "f": 3e14, "phi": 1e-18}, "Frequency too low"),
        ("photoelectric_stopping_voltage(KE_max, e)", {"KE_max": 1e-19, "e": 0}, "Elementary charge e must be positive"),
        ("particle_in_box_energy(n, h, m, L)", {"n": 0, "h": 6.626e-34, "m": 9.109e-31, "L": 1e-10}, "Quantum number n must be a positive integer"),
        ("particle_in_box_energy(n, h, m, L)", {"n": 1.5, "h": 6.626e-34, "m": 9.109e-31, "L": 1e-10}, "Quantum number n must be a positive integer"),
        ("bohr_energy_level(n)", {"n": 0}, "Quantum number n must be a positive integer"),
        ("bohr_radius(n)", {"n": 2.5}, "Quantum number n must be a positive integer"),
        ("heisenberg_uncertainty_momentum(delta_x, hbar)", {"delta_x": 0, "hbar": 1.055e-34}, "Position uncertainty Δx must be positive"),
        ("compton_shift(h, m_e, c, theta)", {"h": 6.626e-34, "m_e": 0, "c": 3e8, "theta": 0}, "Electron mass m_e must be positive"),
    ],
)
def test_quantum_mechanics_validation(de_broglie_model, operation, quantities, expected_error):
    """Test error handling for invalid quantum mechanics parameters."""
    model_quantities = [
        Quantity(name=name, value=value, siUnit="dimensionless", isKnown=True)
        for name, value in quantities.items()
    ]
    equation = de_broglie_model.equations[0].model_copy(update={"rhs": operation})
    model = de_broglie_model.model_copy(update={
        "quantities": model_quantities,
        "equations": [equation],
    })

    result = PhysicsQuantumMechanicsSolver().solve(model)

    assert not result.success
    assert expected_error in result.error


# ============ Routing Tests ============

def test_general_solver_routes_quantum_mechanics(de_broglie_model):
    """Test that GeneralSolver routes to quantum mechanics solver."""
    result = GeneralSolver().solve(de_broglie_model)

    assert result.success
    assert "wavelength" in result.summary
