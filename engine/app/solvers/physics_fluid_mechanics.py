"""Fluid mechanics solver (physics.fluid_mechanics domain)."""
from typing import Dict
import numpy as np
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _hydrostatic_pressure(P0: float, rho: float, g: float, h: float) -> float:
    """Hydrostatic pressure: P = P0 + ρ⋅g⋅h (Pascals)."""
    if rho < 0 or h < 0:
        raise ValueError("Density and height must be non-negative")
    return float(P0 + rho * g * h)


def _buoyant_force(rho_fluid: float, V_displaced: float, g: float) -> float:
    """Buoyant force: F_b = ρ_fluid⋅V_displaced⋅g (Newtons)."""
    if rho_fluid < 0 or V_displaced < 0:
        raise ValueError("Density and volume must be non-negative")
    return float(rho_fluid * V_displaced * g)


def _continuity_velocity2(A1: float, v1: float, A2: float) -> float:
    """Continuity equation for velocity: v2 = A1⋅v1 / A2 (m/s)."""
    if A2 <= 0:
        raise ValueError("Cross-sectional area A2 must be greater than 0")
    return float(A1 * v1 / A2)


def _bernoulli_pressure2(P1: float, rho: float, v1: float, h1: float,
                         v2: float, h2: float, g: float) -> float:
    """Bernoulli's equation: P2 = P1 + 0.5⋅ρ⋅(v1² - v2²) + ρ⋅g⋅(h1 - h2) (Pascals)."""
    if rho < 0:
        raise ValueError("Density must be non-negative")
    if g <= 0:
        raise ValueError("Gravitational acceleration must be greater than 0")
    return float(P1 + 0.5 * rho * (v1**2 - v2**2) + rho * g * (h1 - h2))


def _poiseuille_flow_rate(delta_P: float, r: float, eta: float, L: float) -> float:
    """Poiseuille flow rate: Q = π⋅ΔP⋅r⁴ / (8⋅η⋅L) (m³/s)."""
    if r <= 0 or eta <= 0 or L <= 0:
        raise ValueError("Radius, viscosity, and length must be greater than 0")
    if delta_P < 0:
        raise ValueError("Pressure difference must be non-negative")
    return float(np.pi * delta_P * r**4 / (8 * eta * L))


def _reynolds_number(rho: float, v: float, L: float, eta: float) -> float:
    """Reynolds number: Re = ρ⋅v⋅L / η (dimensionless)."""
    if rho < 0 or L < 0 or eta <= 0:
        raise ValueError("Density and length must be non-negative; viscosity must be positive")
    return float(rho * v * L / eta)


def _torricelli_efflux_velocity(g: float, h: float) -> float:
    """Torricelli efflux velocity: v = √(2⋅g⋅h) (m/s)."""
    if g <= 0 or h < 0:
        raise ValueError("Gravitational acceleration must be positive; height must be non-negative")
    return float(np.sqrt(2 * g * h))


def _drag_force(Cd: float, rho: float, A: float, v: float) -> float:
    """Drag force: F_d = 0.5⋅Cd⋅ρ⋅A⋅v² (Newtons)."""
    if Cd < 0 or rho < 0 or A < 0:
        raise ValueError("Drag coefficient, density, and area must be non-negative")
    return float(0.5 * Cd * rho * A * v**2)


_OPERATIONS = {
    "hydrostatic_pressure": _hydrostatic_pressure,
    "buoyant_force": _buoyant_force,
    "continuity_velocity2": _continuity_velocity2,
    "bernoulli_pressure2": _bernoulli_pressure2,
    "poiseuille_flow_rate": _poiseuille_flow_rate,
    "reynolds_number": _reynolds_number,
    "torricelli_efflux_velocity": _torricelli_efflux_velocity,
    "drag_force": _drag_force,
}


@register("physics.fluid_mechanics")
class PhysicsFluidMechanicsSolver(SolverBase):
    """
    Specialized solver for fluid mechanics: hydrostatic pressure, buoyancy, continuity,
    Bernoulli's principle, Poiseuille flow, Reynolds number, drag.
    Supports operations like hydrostatic_pressure, buoyant_force, continuity_velocity2, etc.
    All calculations are closed-form (no CFD/Navier-Stokes integration).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve fluid mechanics problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Fluid mechanics solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
