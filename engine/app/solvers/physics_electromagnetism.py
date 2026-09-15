"""Electromagnetism solver (physics.electromagnetism domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_vector


def _coulomb_force(q1: float, q2: float, r: float, k_e: float) -> float:
    """Coulomb's law: F = k_e * |q1 * q2| / r^2 (Newtons)."""
    if r <= 0:
        raise ValueError("Distance r must be greater than 0")
    return float(k_e * abs(q1 * q2) / (r ** 2))


def _electric_field_point_charge(q: float, r: float, k_e: float) -> float:
    """Electric field: E = k_e * |q| / r^2 (N/C)."""
    if r <= 0:
        raise ValueError("Distance r must be greater than 0")
    return float(k_e * abs(q) / (r ** 2))


def _electric_potential_point_charge(q: float, r: float, k_e: float) -> float:
    """Electric potential: V = k_e * q / r (Volts)."""
    if r <= 0:
        raise ValueError("Distance r must be greater than 0")
    return float(k_e * q / r)


def _ohms_law_voltage(I: float, R: float) -> float:
    """Ohm's law: V = I * R (Volts)."""
    return float(I * R)


def _ohms_law_current(V: float, R: float) -> float:
    """Ohm's law: I = V / R (Amperes)."""
    if R <= 0:
        raise ValueError("Resistance R must be greater than 0")
    return float(V / R)


def _ohms_law_resistance(V: float, I: float) -> float:
    """Ohm's law: R = V / I (Ohms)."""
    if I <= 0:
        raise ValueError("Current I must be greater than 0")
    return float(V / I)


def _power_electrical(V: float, I: float) -> float:
    """Electrical power: P = V * I (Watts)."""
    return float(V * I)


def _series_resistance(r_vec: list) -> float:
    """Series resistance: R_total = Σ R_i (Ohms)."""
    return float(np.sum(np.array(r_vec, dtype=float)))


def _parallel_resistance(r_vec: list) -> float:
    """Parallel resistance: 1/R_total = Σ(1/R_i) (Ohms)."""
    r = np.array(r_vec, dtype=float)
    if np.any(r <= 0):
        raise ValueError("All resistances must be greater than 0")
    return float(1.0 / np.sum(1.0 / r))


def _capacitor_energy(C: float, V: float) -> float:
    """Capacitor energy: U = 0.5 * C * V^2 (Joules)."""
    return float(0.5 * C * V ** 2)


def _magnetic_force_on_charge(q: float, v: float, B: float, theta: float) -> float:
    """Magnetic force: F = q*v*B*sin(θ) (Newtons). Angle in radians."""
    return float(q * v * B * np.sin(theta))


def _faraday_emf(N: float, delta_phi: float, delta_t: float) -> float:
    """Faraday's law: ε = -N * dΦ/dt (Volts, magnitude)."""
    if delta_t <= 0:
        raise ValueError("Time interval delta_t must be greater than 0")
    return float(abs(N * delta_phi / delta_t))


_OPERATIONS = {
    "coulomb_force": _coulomb_force,
    "electric_field_point_charge": _electric_field_point_charge,
    "electric_potential_point_charge": _electric_potential_point_charge,
    "ohms_law_voltage": _ohms_law_voltage,
    "ohms_law_current": _ohms_law_current,
    "ohms_law_resistance": _ohms_law_resistance,
    "power_electrical": _power_electrical,
    "series_resistance": _series_resistance,
    "parallel_resistance": _parallel_resistance,
    "capacitor_energy": _capacitor_energy,
    "magnetic_force_on_charge": _magnetic_force_on_charge,
    "faraday_emf": _faraday_emf,
}


@register("physics.electromagnetism")
class PhysicsElectromagnetismSolver(SolverBase):
    """Solver for electromagnetism: circuits, fields, forces, energy."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Electromagnetism solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
