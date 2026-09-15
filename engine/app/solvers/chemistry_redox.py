"""Redox reactions solver (chemistry.redox_reactions domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _cell_potential(E_cathode: float, E_anode: float) -> float:
    """Cell potential: E_cell = E_cathode - E_anode (Volts)."""
    return float(E_cathode - E_anode)


def _nernst_equation(E_standard: float, n: float, Q: float, R: float, T: float, F: float) -> float:
    """Nernst equation: E = E° - (R*T)/(n*F) * ln(Q) (Volts)."""
    if F <= 0:
        raise ValueError("Faraday constant F must be positive")
    if n <= 0:
        raise ValueError("Number of electrons n must be positive")
    if Q <= 0:
        raise ValueError("Reaction quotient Q must be positive")
    if T <= 0:
        raise ValueError("Temperature T must be positive")
    return float(E_standard - (R * T) / (n * F) * np.log(Q))


def _gibbs_free_energy_from_cell(n: float, F: float, E_cell: float) -> float:
    """Gibbs free energy: ΔG = -n*F*E_cell (Joules)."""
    return float(-n * F * E_cell)


def _equilibrium_constant_from_cell(n: float, F: float, E_standard: float, R: float, T: float) -> float:
    """Equilibrium constant from cell potential: K = exp(n*F*E°/(R*T))."""
    if T <= 0:
        raise ValueError("Temperature T must be positive")
    if R <= 0:
        raise ValueError("Gas constant R must be positive")
    if F <= 0:
        raise ValueError("Faraday constant F must be positive")
    return float(np.exp(n * F * E_standard / (R * T)))


_OPERATIONS = {
    "cell_potential": _cell_potential,
    "nernst_equation": _nernst_equation,
    "gibbs_free_energy_from_cell": _gibbs_free_energy_from_cell,
    "equilibrium_constant_from_cell": _equilibrium_constant_from_cell,
}


@register("chemistry.redox_reactions")
class ChemistryRedoxSolver(SolverBase):
    """Solver for redox reactions: cell potential, Nernst equation, electrochemistry."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Redox reactions solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
