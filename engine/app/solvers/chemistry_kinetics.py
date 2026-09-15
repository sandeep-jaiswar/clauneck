"""Kinetics solver (chemistry.kinetics domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _zero_order_concentration(A0: float, k: float, t: float) -> float:
    """Zero-order rate law: [A] = [A]0 - k*t (mol/L)."""
    return float(A0 - k * t)


def _zero_order_half_life(A0: float, k: float) -> float:
    """Zero-order half-life: t_1/2 = [A]0 / (2*k) (seconds)."""
    if k <= 0:
        raise ValueError("Rate constant k must be greater than 0")
    return float(A0 / (2.0 * k))


def _first_order_concentration(A0: float, k: float, t: float) -> float:
    """First-order rate law: [A] = [A]0 * exp(-k*t) (mol/L)."""
    if k < 0:
        raise ValueError("Rate constant k must be >= 0")
    return float(A0 * np.exp(-k * t))


def _first_order_half_life(k: float) -> float:
    """First-order half-life: t_1/2 = ln(2)/k (seconds)."""
    if k <= 0:
        raise ValueError("Rate constant k must be greater than 0")
    return float(np.log(2.0) / k)


def _second_order_concentration(A0: float, k: float, t: float) -> float:
    """Second-order rate law: [A] = [A]0 / (1 + [A]0*k*t) (mol/L)."""
    denom = 1.0 + A0 * k * t
    if denom <= 0:
        raise ValueError("Denominator 1 + [A]0*k*t must be positive")
    return float(A0 / denom)


def _second_order_half_life(A0: float, k: float) -> float:
    """Second-order half-life: t_1/2 = 1 / ([A]0*k) (seconds)."""
    if A0 <= 0 or k <= 0:
        raise ValueError("A0 and k must be greater than 0")
    return float(1.0 / (A0 * k))


def _arrhenius_rate_constant(A: float, Ea: float, R: float, T: float) -> float:
    """Arrhenius equation: k = A * exp(-Ea/(R*T)) (1/s or L/(mol*s))."""
    if T <= 0:
        raise ValueError("Temperature T must be greater than 0")
    if R <= 0:
        raise ValueError("Gas constant R must be greater than 0")
    return float(A * np.exp(-Ea / (R * T)))


def _arrhenius_activation_energy(k1: float, k2: float, T1: float, T2: float, R: float) -> float:
    """Arrhenius activation energy: Ea = -R*ln(k1/k2) / (1/T1 - 1/T2) (J/mol)."""
    if k1 <= 0 or k2 <= 0:
        raise ValueError("Rate constants must be positive")
    if T1 <= 0 or T2 <= 0:
        raise ValueError("Temperatures must be positive")
    if R <= 0:
        raise ValueError("Gas constant R must be positive")
    denom = 1.0 / T1 - 1.0 / T2
    if abs(denom) < 1e-10:
        raise ValueError("Temperatures must be different")
    return float(-R * np.log(k1 / k2) / denom)


_OPERATIONS = {
    "zero_order_concentration": _zero_order_concentration,
    "zero_order_half_life": _zero_order_half_life,
    "first_order_concentration": _first_order_concentration,
    "first_order_half_life": _first_order_half_life,
    "second_order_concentration": _second_order_concentration,
    "second_order_half_life": _second_order_half_life,
    "arrhenius_rate_constant": _arrhenius_rate_constant,
    "arrhenius_activation_energy": _arrhenius_activation_energy,
}


@register("chemistry.kinetics")
class ChemistryKineticsSolver(SolverBase):
    """Solver for reaction kinetics: rate laws, half-life, Arrhenius equation."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Kinetics solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
