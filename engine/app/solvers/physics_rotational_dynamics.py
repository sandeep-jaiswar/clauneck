"""Rotational dynamics solver (physics.rotational_dynamics domain)."""
from typing import Dict
import math
import numpy as np
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, to_radians


def _torque(F: float, r: float, theta: float) -> float:
    """Torque: τ = F × r × sin(θ) (Newton-meters)."""
    if r < 0:
        raise ValueError("Lever arm r must be non-negative")
    return float(F * r * math.sin(math.radians(theta)))


def _moment_of_inertia_point_mass(m: float, r: float) -> float:
    """Moment of inertia for point mass: I = m × r² (kg⋅m²)."""
    if m < 0:
        raise ValueError("Mass m must be non-negative")
    if r < 0:
        raise ValueError("Distance r must be non-negative")
    return float(m * r**2)


def _moment_of_inertia_disk(m: float, r: float) -> float:
    """Moment of inertia for uniform disk (about central axis): I = ½ × m × r² (kg⋅m²)."""
    if m < 0:
        raise ValueError("Mass m must be non-negative")
    if r < 0:
        raise ValueError("Radius r must be non-negative")
    return float(0.5 * m * r**2)


def _moment_of_inertia_sphere_solid(m: float, r: float) -> float:
    """Moment of inertia for solid sphere (about central axis): I = ⅖ × m × r² (kg⋅m²)."""
    if m < 0:
        raise ValueError("Mass m must be non-negative")
    if r < 0:
        raise ValueError("Radius r must be non-negative")
    return float(0.4 * m * r**2)


def _moment_of_inertia_rod_center(m: float, L: float) -> float:
    """Moment of inertia for uniform rod (about center): I = 1/12 × m × L² (kg⋅m²)."""
    if m < 0:
        raise ValueError("Mass m must be non-negative")
    if L < 0:
        raise ValueError("Length L must be non-negative")
    return float(m * L**2 / 12.0)


def _angular_acceleration(tau: float, I: float) -> float:
    """Angular acceleration: α = τ / I (rad/s²)."""
    if I <= 0:
        raise ValueError("Moment of inertia I must be greater than 0")
    return float(tau / I)


def _angular_momentum(I: float, omega: float) -> float:
    """Angular momentum: L = I × ω (kg⋅m²/s)."""
    if I < 0:
        raise ValueError("Moment of inertia I must be non-negative")
    return float(I * omega)


def _rotational_kinetic_energy(I: float, omega: float) -> float:
    """Rotational kinetic energy: KE = ½ × I × ω² (Joules)."""
    if I < 0:
        raise ValueError("Moment of inertia I must be non-negative")
    return float(0.5 * I * omega**2)


def _angular_velocity_from_time(omega0: float, alpha: float, t: float) -> float:
    """Angular velocity from constant angular acceleration: ω = ω₀ + α × t (rad/s)."""
    if t < 0:
        raise ValueError("Time t must be non-negative")
    return float(omega0 + alpha * t)


def _angular_displacement(omega0: float, alpha: float, t: float) -> float:
    """Angular displacement from constant angular acceleration: θ = ω₀ × t + ½ × α × t² (radians)."""
    if t < 0:
        raise ValueError("Time t must be non-negative")
    return float(omega0 * t + 0.5 * alpha * t**2)


def _rolling_without_slipping_velocity(omega: float, r: float) -> float:
    """Velocity of rolling object (no slip condition): v = ω × r (m/s)."""
    if r < 0:
        raise ValueError("Radius r must be non-negative")
    return float(omega * r)


_OPERATIONS = {
    "torque": _torque,
    "moment_of_inertia_point_mass": _moment_of_inertia_point_mass,
    "moment_of_inertia_disk": _moment_of_inertia_disk,
    "moment_of_inertia_sphere_solid": _moment_of_inertia_sphere_solid,
    "moment_of_inertia_rod_center": _moment_of_inertia_rod_center,
    "angular_acceleration": _angular_acceleration,
    "angular_momentum": _angular_momentum,
    "rotational_kinetic_energy": _rotational_kinetic_energy,
    "angular_velocity_from_time": _angular_velocity_from_time,
    "angular_displacement": _angular_displacement,
    "rolling_without_slipping_velocity": _rolling_without_slipping_velocity,
}


@register("physics.rotational_dynamics")
class PhysicsRotationalDynamicsSolver(SolverBase):
    """
    Specialized solver for rotational dynamics: torque, angular acceleration,
    moment of inertia, angular momentum, rolling motion.
    Supports operations like torque, moment_of_inertia_*, angular_acceleration, etc.
    All calculations are closed-form (no ODE integration).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve rotational dynamics problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Rotational dynamics solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
