"""Special relativity solver (physics.special_relativity domain)."""
from typing import Dict
import math
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _lorentz_factor(v: float, c: float = 299792458) -> float:
    """Lorentz factor: γ = 1 / √(1 - v²/c²) (dimensionless)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    beta_squared = (v / c) ** 2
    return float(1.0 / math.sqrt(1.0 - beta_squared))


def _time_dilation(t0: float, v: float, c: float = 299792458) -> float:
    """Time dilation: t = t0 * γ = t0 / √(1 - v²/c²) (seconds)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    if t0 < 0:
        raise ValueError(f"Proper time t0 must be non-negative; got t0={t0} s")
    gamma = _lorentz_factor(v, c)
    return float(t0 * gamma)


def _length_contraction(L0: float, v: float, c: float = 299792458) -> float:
    """Length contraction: L = L0 * √(1 - v²/c²) (meters)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    if L0 < 0:
        raise ValueError(f"Rest length L0 must be non-negative; got L0={L0} m")
    beta_squared = (v / c) ** 2
    return float(L0 * math.sqrt(1.0 - beta_squared))


def _relativistic_momentum(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic momentum: p = m0 * v * γ (kg⋅m/s)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    gamma = _lorentz_factor(v, c)
    return float(m0 * v * gamma)


def _relativistic_total_energy(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic total energy: E = m0 * c² * γ (Joules)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    gamma = _lorentz_factor(v, c)
    return float(m0 * (c ** 2) * gamma)


def _rest_energy(m0: float, c: float = 299792458) -> float:
    """Rest energy: E0 = m0 * c² (Joules)."""
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    return float(m0 * (c ** 2))


def _relativistic_kinetic_energy(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic kinetic energy: KE = (γ - 1) * m0 * c² (Joules)."""
    if v < 0 or v >= c:
        raise ValueError(f"Velocity must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    gamma = _lorentz_factor(v, c)
    return float((gamma - 1.0) * m0 * (c ** 2))


def _relativistic_velocity_addition(u: float, v: float, c: float = 299792458) -> float:
    """Relativistic velocity addition: w = (u + v) / (1 + uv/c²) (m/s)."""
    if u < 0 or u >= c:
        raise ValueError(f"Velocity u must be 0 ≤ u < c; got u={u} m/s, c={c} m/s")
    if v < 0 or v >= c:
        raise ValueError(f"Velocity v must be 0 ≤ v < c; got v={v} m/s, c={c} m/s")
    denominator = 1.0 + (u * v) / (c ** 2)
    if denominator <= 0:
        raise ValueError(f"Velocity addition denominator invalid; got 1 + uv/c² = {denominator}")
    return float((u + v) / denominator)


def _energy_momentum_relation(m0: float, p: float, c: float = 299792458) -> float:
    """Energy-momentum relation: E = √((pc)² + (m0c²)²) (Joules)."""
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    if p < 0:
        raise ValueError(f"Momentum p must be non-negative; got p={p} kg⋅m/s")
    pc_squared = (p * c) ** 2
    m0c2_squared = (m0 * (c ** 2)) ** 2
    return float(math.sqrt(pc_squared + m0c2_squared))


_OPERATIONS = {
    "lorentz_factor": _lorentz_factor,
    "time_dilation": _time_dilation,
    "length_contraction": _length_contraction,
    "relativistic_momentum": _relativistic_momentum,
    "relativistic_total_energy": _relativistic_total_energy,
    "rest_energy": _rest_energy,
    "relativistic_kinetic_energy": _relativistic_kinetic_energy,
    "relativistic_velocity_addition": _relativistic_velocity_addition,
    "energy_momentum_relation": _energy_momentum_relation,
}


@register("physics.special_relativity")
class PhysicsSpecialRelativitySolver(SolverBase):
    """
    Specialized solver for special relativity: Lorentz transformations, time dilation,
    length contraction, relativistic momentum and energy.
    Supports operations like lorentz_factor, time_dilation, length_contraction, etc.
    All calculations are closed-form (no ODE integration).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve special relativity problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        Speed of light defaults to 299792458 m/s if not provided.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Special relativity solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
