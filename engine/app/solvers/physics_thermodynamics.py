"""Thermodynamics solver (physics.thermodynamics domain)."""
from typing import Dict
import numpy as np
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _ideal_gas_pressure(n: float, R: float, T: float, V: float) -> float:
    """Ideal gas law: P = nRT/V (Pascal)."""
    if V <= 0:
        raise ValueError("Volume V must be greater than 0")
    return float(n * R * T / V)


def _ideal_gas_volume(n: float, R: float, T: float, P: float) -> float:
    """Ideal gas law rearranged: V = nRT/P (cubic meters)."""
    if P <= 0:
        raise ValueError("Pressure P must be greater than 0")
    return float(n * R * T / P)


def _ideal_gas_temperature(P: float, V: float, n: float, R: float) -> float:
    """Ideal gas law rearranged: T = PV/(nR) (Kelvin)."""
    if n <= 0:
        raise ValueError("Number of moles n must be greater than 0")
    return float(P * V / (n * R))


def _ideal_gas_moles(P: float, V: float, R: float, T: float) -> float:
    """Ideal gas law rearranged: n = PV/(RT) (moles)."""
    if T <= 0:
        raise ValueError("Temperature T must be greater than 0")
    return float(P * V / (R * T))


def _work_isobaric(P: float, delta_V: float) -> float:
    """Work done at constant pressure: W = P * ΔV (Joules)."""
    return float(P * delta_V)


def _work_isothermal(n: float, R: float, T: float,
                     V1: float, V2: float) -> float:
    """Work done at constant temperature: W = nRT * ln(V2/V1) (Joules)."""
    if V1 <= 0 or V2 <= 0:
        raise ValueError("Volumes V1 and V2 must be greater than 0")
    if V2 / V1 <= 0:
        raise ValueError("Volume ratio V2/V1 must be positive")
    return float(n * R * T * np.log(V2 / V1))


def _heat_transfer(m: float, c: float, delta_T: float) -> float:
    """Heat transfer: Q = m * c * ΔT (Joules)."""
    return float(m * c * delta_T)


def _first_law_delta_u(Q: float, W: float) -> float:
    """First law of thermodynamics: ΔU = Q - W (Joules)."""
    return float(Q - W)


def _carnot_efficiency(T_hot: float, T_cold: float) -> float:
    """Carnot cycle efficiency: η = 1 - T_cold/T_hot (dimensionless, 0-1)."""
    if T_hot <= 0 or T_cold <= 0:
        raise ValueError("Temperatures must be positive (Kelvin)")
    if T_cold >= T_hot:
        raise ValueError("T_cold must be less than T_hot")
    return float(1.0 - T_cold / T_hot)


def _entropy_change_isothermal(Q: float, T: float) -> float:
    """Entropy change at constant temperature: ΔS = Q/T (J/K)."""
    if T <= 0:
        raise ValueError("Temperature T must be greater than 0")
    return float(Q / T)


_OPERATIONS = {
    "ideal_gas_pressure": _ideal_gas_pressure,
    "ideal_gas_volume": _ideal_gas_volume,
    "ideal_gas_temperature": _ideal_gas_temperature,
    "ideal_gas_moles": _ideal_gas_moles,
    "work_isobaric": _work_isobaric,
    "work_isothermal": _work_isothermal,
    "heat_transfer": _heat_transfer,
    "first_law_delta_u": _first_law_delta_u,
    "carnot_efficiency": _carnot_efficiency,
    "entropy_change_isothermal": _entropy_change_isothermal,
}


@register("physics.thermodynamics")
class PhysicsThermodynamicsSolver(SolverBase):
    """
    Specialized solver for thermodynamics: ideal gas law, work, heat, entropy, efficiency.
    Supports operations like ideal_gas_pressure, work_isobaric, carnot_efficiency, etc.
    All calculations are closed-form (no ODE integration).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve thermodynamics problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Thermodynamics solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
