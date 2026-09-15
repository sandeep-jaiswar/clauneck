"""Thermochemistry solver (chemistry.thermochemistry domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_vector


def _hess_law_sum(delta_h_vec: list) -> float:
    """Hess's law: ΔH_rxn = Σ(ΔH_i) (kJ/mol)."""
    return float(np.sum(np.array(delta_h_vec, dtype=float)))


def _standard_enthalpy_reaction(hf_products: list, coeff_products: list,
                                hf_reactants: list, coeff_reactants: list) -> float:
    """Standard enthalpy of reaction: ΔH°_rxn = Σ(coeff*Hf)_products - Σ(coeff*Hf)_reactants."""
    hfp = np.array(hf_products, dtype=float)
    cp = np.array(coeff_products, dtype=float)
    hfr = np.array(hf_reactants, dtype=float)
    cr = np.array(coeff_reactants, dtype=float)
    
    if hfp.shape != cp.shape or hfr.shape != cr.shape:
        raise ValueError("Enthalpies and coefficients must have matching lengths")
    
    products_sum = np.sum(cp * hfp)
    reactants_sum = np.sum(cr * hfr)
    return float(products_sum - reactants_sum)


def _calorimetry_heat(m: float, c: float, delta_T: float) -> float:
    """Calorimetry: q = m*c*ΔT (Joules)."""
    return float(m * c * delta_T)


def _bond_energy_enthalpy(be_broken_vec: list, be_formed_vec: list) -> float:
    """Bond energy enthalpy: ΔH = Σ(BE_broken) - Σ(BE_formed) (kJ/mol)."""
    broken = np.sum(np.array(be_broken_vec, dtype=float))
    formed = np.sum(np.array(be_formed_vec, dtype=float))
    return float(broken - formed)


def _enthalpy_per_mole(delta_H: float, moles: float) -> float:
    """Enthalpy per mole: H_per_mol = ΔH / n (J/mol or kJ/mol)."""
    if moles <= 0:
        raise ValueError("Number of moles must be positive")
    return float(delta_H / moles)


_OPERATIONS = {
    "hess_law_sum": _hess_law_sum,
    "standard_enthalpy_reaction": _standard_enthalpy_reaction,
    "calorimetry_heat": _calorimetry_heat,
    "bond_energy_enthalpy": _bond_energy_enthalpy,
    "enthalpy_per_mole": _enthalpy_per_mole,
}


@register("chemistry.thermochemistry")
class ChemistryThermochemistrySolver(SolverBase):
    """Solver for thermochemistry: enthalpy, Hess's law, calorimetry."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Thermochemistry solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
