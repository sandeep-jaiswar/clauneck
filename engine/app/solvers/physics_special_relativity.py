"""Special relativity solver (physics.special_relativity domain)."""
from typing import Dict
import math
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _validate_speed_of_light(c: float) -> None:
    """Require a finite, positive speed of light."""
    if not math.isfinite(c) or c <= 0:
        raise ValueError(f"Speed of light c must be finite and positive; got c={c} m/s")


def _validate_velocity(v: float, c: float, name: str = "v") -> None:
    """Require a finite velocity whose magnitude is below the speed of light."""
    _validate_speed_of_light(c)
    if not math.isfinite(v) or abs(v) >= c:
        raise ValueError(
            f"Velocity {name} must satisfy |{name}| < c; got {name}={v} m/s, c={c} m/s"
        )


def _lorentz_factor(v: float, c: float = 299792458) -> float:
    """Lorentz factor: γ = 1 / √(1 - v²/c²) (dimensionless)."""
    _validate_velocity(v, c)
    beta_squared = (v / c) ** 2
    return float(1.0 / math.sqrt(1.0 - beta_squared))


def _time_dilation(t0: float, v: float, c: float = 299792458) -> float:
    """Time dilation: t = t0 * γ = t0 / √(1 - v²/c²) (seconds)."""
    _validate_velocity(v, c)
    if t0 < 0:
        raise ValueError(f"Proper time t0 must be non-negative; got t0={t0} s")
    gamma = _lorentz_factor(v, c)
    return float(t0 * gamma)


def _length_contraction(L0: float, v: float, c: float = 299792458) -> float:
    """Length contraction: L = L0 * √(1 - v²/c²) (meters)."""
    _validate_velocity(v, c)
    if L0 < 0:
        raise ValueError(f"Rest length L0 must be non-negative; got L0={L0} m")
    beta_squared = (v / c) ** 2
    return float(L0 * math.sqrt(1.0 - beta_squared))


def _relativistic_momentum(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic momentum: p = m0 * v * γ (kg⋅m/s)."""
    _validate_velocity(v, c)
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    gamma = _lorentz_factor(v, c)
    return float(m0 * v * gamma)


def _relativistic_total_energy(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic total energy: E = m0 * c² * γ (Joules)."""
    _validate_velocity(v, c)
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    gamma = _lorentz_factor(v, c)
    return float(m0 * (c ** 2) * gamma)


def _rest_energy(m0: float, c: float = 299792458) -> float:
    """Rest energy: E0 = m0 * c² (Joules)."""
    _validate_speed_of_light(c)
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    return float(m0 * (c ** 2))


def _relativistic_kinetic_energy(m0: float, v: float, c: float = 299792458) -> float:
    """Relativistic kinetic energy: KE = (γ - 1) * m0 * c² (Joules)."""
    _validate_velocity(v, c)
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
    beta_squared = (v / c) ** 2
    sqrt_one_minus_beta_squared = math.sqrt(1.0 - beta_squared)
    return float(
        m0 * (v ** 2)
        / (sqrt_one_minus_beta_squared * (1.0 + sqrt_one_minus_beta_squared))
    )


def _relativistic_velocity_addition(u: float, v: float, c: float = 299792458) -> float:
    """Relativistic velocity addition: w = (u + v) / (1 + uv/c²) (m/s)."""
    _validate_velocity(u, c, "u")
    _validate_velocity(v, c)
    denominator = 1.0 + (u * v) / (c ** 2)
    if denominator <= 0:
        raise ValueError(f"Velocity addition denominator invalid; got 1 + uv/c² = {denominator}")
    return float((u + v) / denominator)


def _energy_momentum_relation(m0: float, p: float, c: float = 299792458) -> float:
    """Energy-momentum relation: E = √((pc)² + (m0c²)²) (Joules)."""
    _validate_speed_of_light(c)
    if m0 <= 0:
        raise ValueError(f"Rest mass m0 must be positive; got m0={m0} kg")
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
