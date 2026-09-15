"""Equilibrium solver (chemistry.equilibrium domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_vector


def _reaction_quotient(conc_products: list, coeff_products: list,
                       conc_reactants: list, coeff_reactants: list) -> float:
    """Reaction quotient Q = Π([products]^coeff_p) / Π([reactants]^coeff_r)."""
    cp = np.array(conc_products, dtype=float)
    coeff_p = np.array(coeff_products, dtype=float)
    cr = np.array(conc_reactants, dtype=float)
    coeff_r = np.array(coeff_reactants, dtype=float)
    
    if cp.shape != coeff_p.shape or cr.shape != coeff_r.shape:
        raise ValueError("Concentrations and coefficients must have matching lengths")
    
    numerator = np.prod(cp ** coeff_p)
    denominator = np.prod(cr ** coeff_r)
    if denominator <= 0:
        raise ValueError("Reactant concentrations must be positive")
    return float(numerator / denominator)


def _kp_from_kc(Kc: float, delta_n: float, R: float, T: float) -> float:
    """Kp from Kc: Kp = Kc * (R*T)^(Δn) (atm/Pa depending on units)."""
    if T <= 0:
        raise ValueError("Temperature T must be positive")
    if R <= 0:
        raise ValueError("Gas constant R must be positive")
    return float(Kc * ((R * T) ** delta_n))


def _le_chatelier_direction(Q: float, K: float, tol: float = 1e-9) -> str:
    """Determine reaction direction: Q<K (forward), Q>K (reverse), Q≈K (at equilibrium)."""
    if abs(Q - K) / (max(abs(K), 1.0)) < tol:
        return "at_equilibrium"
    elif Q < K:
        return "forward"
    else:
        return "reverse"


def _percent_dissociation(c0: float, c_eq: float) -> float:
    """Percent dissociation: % = (c0 - c_eq) / c0 * 100."""
    if c0 <= 0:
        raise ValueError("Initial concentration c0 must be positive")
    return float((c0 - c_eq) / c0 * 100.0)


_OPERATIONS = {
    "reaction_quotient": _reaction_quotient,
    "kp_from_kc": _kp_from_kc,
    "le_chatelier_direction": _le_chatelier_direction,
    "percent_dissociation": _percent_dissociation,
}


@register("chemistry.equilibrium")
class ChemistryEquilibriumSolver(SolverBase):
    """Solver for chemical equilibrium: Q, K, Le Chatelier predictions."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Equilibrium solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
