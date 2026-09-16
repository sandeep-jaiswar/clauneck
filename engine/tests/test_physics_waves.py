"""Tests for waves solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.physics_waves import PhysicsWavesSolver

@pytest.fixture
def wave_speed_model():
    """Model for wave speed calculation."""
    return ScientificModel(
        id="waves-speed",
        domain="physics.waves",
        description="Wave speed",
        quantities=[
            Quantity(name="f", value=10.0, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="wavelength", value=2.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="v", rhs="wave_speed(f, wavelength)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def doppler_model():
    """Model for Doppler effect calculation."""
    return ScientificModel(
        id="waves-doppler",
        domain="physics.waves",
        description="Doppler effect",
        quantities=[
            Quantity(name="f_source", value=440.0, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v_wave", value=343.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v_observer", value=0.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v_source", value=10.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="f_obs", rhs="doppler_frequency(f_source, v_wave, v_observer, v_source)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def standing_wave_model():
    """Model for standing wave frequency calculation."""
    return ScientificModel(
        id="waves-standing",
        domain="physics.waves",
        description="Standing wave",
        quantities=[
            Quantity(name="n", value=2.0, siUnit="dimensionless", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="v", value=100.0, siUnit="m/s", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="L", value=1.0, siUnit="m", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="f", rhs="standing_wave_frequency(n, v, L)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

@pytest.fixture
def beat_frequency_model():
    """Model for beat frequency calculation."""
    return ScientificModel(
        id="waves-beats",
        domain="physics.waves",
        description="Beat frequency",
        quantities=[
            Quantity(name="f1", value=440.0, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
            Quantity(name="f2", value=443.0, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="f_beat", rhs="beat_frequency(f1, f2)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

# ============ Correctness Tests ============

def test_wave_speed_solvable(wave_speed_model):
    """Test that wave speed solves successfully."""
    solver = PhysicsWavesSolver()
    result = solver.solve(wave_speed_model)

    assert result.success
    assert "v" in result.summary

def test_wave_speed_correctness(wave_speed_model):
    """Test wave speed: v = f * λ."""
    solver = PhysicsWavesSolver()
    result = solver.solve(wave_speed_model)

    assert result.success
    # v = 10 * 2 = 20 m/s
    expected_v = 20.0
    assert abs(result.summary["v"] - expected_v) < 1e-6

def test_doppler_solvable(doppler_model):
    """Test that Doppler effect solves successfully."""
    solver = PhysicsWavesSolver()
    result = solver.solve(doppler_model)

    assert result.success
    assert "f_obs" in result.summary

def test_doppler_correctness(doppler_model):
    """Test Doppler effect: f_obs = f_source * (v_wave + v_obs) / (v_wave - v_source)."""
    solver = PhysicsWavesSolver()
    result = solver.solve(doppler_model)

    assert result.success
    # f_obs = 440 * 343 / (343 - 10) ≈ 453 Hz
    expected_f = 440.0 * 343.0 / (343.0 - 10.0)
    assert abs(result.summary["f_obs"] - expected_f) < 1.0

def test_standing_wave_solvable(standing_wave_model):
    """Test that standing wave frequency solves successfully."""
    solver = PhysicsWavesSolver()
    result = solver.solve(standing_wave_model)

    assert result.success
    assert "f" in result.summary

def test_standing_wave_correctness(standing_wave_model):
    """Test standing wave: f = n*v/(2*L)."""
    solver = PhysicsWavesSolver()
    result = solver.solve(standing_wave_model)

    assert result.success
    # f = 2 * 100 / (2 * 1) = 100 Hz
    expected_f = 2.0 * 100.0 / (2.0 * 1.0)
    assert abs(result.summary["f"] - expected_f) < 1e-6

def test_beat_frequency_solvable(beat_frequency_model):
    """Test that beat frequency solves successfully."""
    solver = PhysicsWavesSolver()
    result = solver.solve(beat_frequency_model)

    assert result.success
    assert "f_beat" in result.summary

def test_beat_frequency_correctness(beat_frequency_model):
    """Test beat frequency: f_beat = |f1 - f2|."""
    solver = PhysicsWavesSolver()
    result = solver.solve(beat_frequency_model)

    assert result.success
    # f_beat = |440 - 443| = 3 Hz
    expected_f = 3.0
    assert abs(result.summary["f_beat"] - expected_f) < 1e-6

# ============ Determinism Tests ============

def test_determinism_wave_speed(wave_speed_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsWavesSolver()

    result1 = solver.solve(wave_speed_model)
    result2 = solver.solve(wave_speed_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

def test_determinism_doppler(doppler_model):
    """Test determinism: solving twice produces identical results."""
    solver = PhysicsWavesSolver()

    result1 = solver.solve(doppler_model)
    result2 = solver.solve(doppler_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary

# ============ Error Path Tests ============

def test_error_zero_frequency():
    """Test error with zero frequency."""
    model = ScientificModel(
        id="waves-error-freq",
        domain="physics.waves",
        description="Zero frequency",
        quantities=[
            Quantity(name="f", value=0.0, siUnit="Hz", isKnown=True, dimensionVector=DimensionVector()),
        ],
        equations=[
            Equation(lhs="T", rhs="period(f)", type=EquationType.ALGEBRAIC),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = PhysicsWavesSolver()
    result = solver.solve(model)

    assert not result.success
    assert result.error is not None

# ============ Routing Test ============

def test_general_solver_routes_waves(wave_speed_model):
    """Test that GeneralSolver correctly routes to PhysicsWavesSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(wave_speed_model)

    assert result.success
    assert "v" in result.summary
