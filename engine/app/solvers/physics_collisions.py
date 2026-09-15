"""Collisions solver (physics.collisions domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_vector


def _elastic_1d_final_velocities(m1: float, v1: float, m2: float, v2: float) -> dict:
    """Elastic collision in 1D: returns v1_final and v2_final."""
    denom = m1 + m2
    if denom == 0:
        raise ValueError("Total mass must be nonzero")
    v1_f = ((m1 - m2) * v1 + 2 * m2 * v2) / denom
    v2_f = ((m2 - m1) * v2 + 2 * m1 * v1) / denom
    return {"v1_final": float(v1_f), "v2_final": float(v2_f)}


def _inelastic_1d_final_velocity(m1: float, v1: float, m2: float, v2: float) -> float:
    """Perfectly inelastic collision: v_final = (m1*v1 + m2*v2)/(m1+m2)."""
    denom = m1 + m2
    if denom == 0:
        raise ValueError("Total mass must be nonzero")
    return float((m1 * v1 + m2 * v2) / denom)


def _momentum(m: float, v: float) -> float:
    """Momentum: p = m*v (kg*m/s)."""
    return float(m * v)


def _kinetic_energy(m: float, v: float) -> float:
    """Kinetic energy: KE = 0.5*m*v^2 (Joules)."""
    return float(0.5 * m * v ** 2)


def _coefficient_of_restitution(v1i: float, v2i: float,
                                 v1f: float, v2f: float) -> float:
    """Coefficient of restitution: e = -(v1f - v2f)/(v1i - v2i)."""
    denom = v1i - v2i
    if abs(denom) < 1e-10:
        raise ValueError("Initial velocities must differ")
    return float(-(v1f - v2f) / denom)


def _impulse(F: float, delta_t: float) -> float:
    """Impulse: J = F*Δt (kg*m/s)."""
    return float(F * delta_t)


def _center_of_mass(masses_vec: list, positions_vec: list) -> float:
    """Center of mass: x_cm = Σ(m_i * x_i) / Σ(m_i)."""
    m = np.array(masses_vec, dtype=float)
    x = np.array(positions_vec, dtype=float)
    if m.shape != x.shape:
        raise ValueError("masses_vec and positions_vec must have same length")
    total_m = np.sum(m)
    if total_m <= 0:
        raise ValueError("Total mass must be positive")
    return float(np.sum(m * x) / total_m)


_OPERATIONS = {
    "elastic_1d_final_velocities": _elastic_1d_final_velocities,
    "inelastic_1d_final_velocity": _inelastic_1d_final_velocity,
    "momentum": _momentum,
    "kinetic_energy": _kinetic_energy,
    "coefficient_of_restitution": _coefficient_of_restitution,
    "impulse": _impulse,
    "center_of_mass": _center_of_mass,
}


@register("physics.collisions")
class PhysicsCollisionsSolver(SolverBase):
    """Solver for collisions: elastic/inelastic, momentum, energy."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Collisions solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
