"""Simple Harmonic Motion solver (physics.simple_harmonic_motion domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _angular_frequency_spring(k: float, m: float) -> float:
    """Spring angular frequency: ω = √(k/m) (rad/s)."""
    if k <= 0 or m <= 0:
        raise ValueError("Spring constant k and mass m must be greater than 0")
    return float(np.sqrt(k / m))


def _angular_frequency_pendulum(g: float, L: float) -> float:
    """Pendulum angular frequency: ω = √(g/L) (rad/s)."""
    if g <= 0 or L <= 0:
        raise ValueError("g and L must be greater than 0")
    return float(np.sqrt(g / L))


def _period_spring(m: float, k: float) -> float:
    """Spring period: T = 2π√(m/k) (seconds)."""
    if k <= 0 or m <= 0:
        raise ValueError("Mass m and spring constant k must be greater than 0")
    return float(2.0 * np.pi * np.sqrt(m / k))


def _period_pendulum(L: float, g: float) -> float:
    """Pendulum period: T = 2π√(L/g) (seconds)."""
    if L <= 0 or g <= 0:
        raise ValueError("Length L and g must be greater than 0")
    return float(2.0 * np.pi * np.sqrt(L / g))


def _max_velocity(A: float, omega: float) -> float:
    """Max velocity in SHM: v_max = A*ω (m/s)."""
    return float(A * omega)


def _max_acceleration(A: float, omega: float) -> float:
    """Max acceleration in SHM: a_max = A*ω^2 (m/s^2)."""
    return float(A * omega ** 2)


def _total_energy(k: float, A: float) -> float:
    """Total mechanical energy in SHM: E = 0.5*k*A^2 (Joules)."""
    if k <= 0:
        raise ValueError("Spring constant k must be greater than 0")
    return float(0.5 * k * A ** 2)


def _damped_amplitude(A0: float, gamma: float, t: float) -> float:
    """Damped amplitude: A(t) = A0 * exp(-γ*t) (m)."""
    return float(A0 * np.exp(-gamma * t))


def _position_at_t(A: float, omega: float, phi: float, t: float) -> float:
    """Position in SHM: x(t) = A*cos(ωt + φ) (m)."""
    return float(A * np.cos(omega * t + phi))


_OPERATIONS = {
    "angular_frequency_spring": _angular_frequency_spring,
    "angular_frequency_pendulum": _angular_frequency_pendulum,
    "period_spring": _period_spring,
    "period_pendulum": _period_pendulum,
    "max_velocity": _max_velocity,
    "max_acceleration": _max_acceleration,
    "total_energy": _total_energy,
    "damped_amplitude": _damped_amplitude,
    "position_at_t": _position_at_t,
}


@register("physics.simple_harmonic_motion")
class PhysicsSimpleHarmonicMotionSolver(SolverBase):
    """Solver for SHM: oscillators, pendulums, springs, damping."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="SHM solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
