"""Waves solver (physics.waves domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _wave_speed(f: float, wavelength: float) -> float:
    """Wave speed: v = f * λ (m/s)."""
    return float(f * wavelength)


def _wavelength(v: float, f: float) -> float:
    """Wavelength: λ = v / f (m)."""
    if f <= 0:
        raise ValueError("Frequency f must be greater than 0")
    return float(v / f)


def _frequency(v: float, wavelength: float) -> float:
    """Frequency: f = v / λ (Hz)."""
    if wavelength <= 0:
        raise ValueError("Wavelength must be greater than 0")
    return float(v / wavelength)


def _period(f: float) -> float:
    """Period: T = 1/f (seconds)."""
    if f <= 0:
        raise ValueError("Frequency f must be greater than 0")
    return float(1.0 / f)


def _doppler_frequency(f_source: float, v_wave: float,
                       v_observer: float, v_source: float) -> float:
    """Doppler effect: f_observed = f_source * (v_wave + v_observer) / (v_wave - v_source)."""
    denominator = v_wave - v_source
    if abs(denominator) < 1e-10:
        raise ValueError("Source speed must be less than wave speed")
    return float(f_source * (v_wave + v_observer) / denominator)


def _standing_wave_frequency(n: float, v: float, L: float) -> float:
    """Standing wave frequency: f = n*v/(2L) (Hz)."""
    if L <= 0:
        raise ValueError("Length L must be greater than 0")
    if n < 1:
        raise ValueError("Harmonic number n must be >= 1")
    return float(n * v / (2.0 * L))


def _beat_frequency(f1: float, f2: float) -> float:
    """Beat frequency: f_beat = |f1 - f2| (Hz)."""
    return float(abs(f1 - f2))


_OPERATIONS = {
    "wave_speed": _wave_speed,
    "wavelength": _wavelength,
    "frequency": _frequency,
    "period": _period,
    "doppler_frequency": _doppler_frequency,
    "standing_wave_frequency": _standing_wave_frequency,
    "beat_frequency": _beat_frequency,
}


@register("physics.waves")
class PhysicsWavesSolver(SolverBase):
    """Solver for wave phenomena: speed, wavelength, Doppler effect, standing waves."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Waves solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
