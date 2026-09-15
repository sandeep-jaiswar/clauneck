"""Acid-base equilibrium solver (chemistry.acid_base_equilibrium domain)."""
import numpy as np
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _ph_from_h(h_conc: float) -> float:
    """pH = -log10([H+]) (dimensionless)."""
    if h_conc <= 0:
        raise ValueError("H+ concentration must be positive")
    return float(-np.log10(h_conc))


def _poh_from_oh(oh_conc: float) -> float:
    """pOH = -log10([OH-]) (dimensionless)."""
    if oh_conc <= 0:
        raise ValueError("OH- concentration must be positive")
    return float(-np.log10(oh_conc))


def _h_from_ph(pH: float) -> float:
    """[H+] = 10^(-pH) (mol/L)."""
    return float(10.0 ** (-pH))


def _oh_from_poh(pOH: float) -> float:
    """[OH-] = 10^(-pOH) (mol/L)."""
    return float(10.0 ** (-pOH))


def _poh_from_ph(pH: float) -> float:
    """pOH = 14 - pH (at 25°C, dimensionless)."""
    return float(14.0 - pH)


def _henderson_hasselbalch(pKa: float, base_conc: float, acid_conc: float) -> float:
    """Henderson-Hasselbalch: pH = pKa + log10([base]/[acid])."""
    if acid_conc <= 0 or base_conc <= 0:
        raise ValueError("Concentrations must be positive")
    return float(pKa + np.log10(base_conc / acid_conc))


def _ka_from_pka(pKa: float) -> float:
    """Ka = 10^(-pKa) (mol/L or L/mol)."""
    return float(10.0 ** (-pKa))


def _pka_from_ka(Ka: float) -> float:
    """pKa = -log10(Ka) (dimensionless)."""
    if Ka <= 0:
        raise ValueError("Ka must be positive")
    return float(-np.log10(Ka))


def _weak_acid_ph(Ka: float, C0: float) -> float:
    """Weak acid pH using quadratic formula (closed-form exact solution)."""
    if Ka <= 0 or C0 <= 0:
        raise ValueError("Ka and C0 must be positive")
    # [H+] = (-Ka + sqrt(Ka^2 + 4*Ka*C0)) / 2
    h_conc = (-Ka + np.sqrt(Ka**2 + 4.0 * Ka * C0)) / 2.0
    if h_conc <= 0:
        raise ValueError("H+ concentration must be positive")
    return float(-np.log10(h_conc))


def _titration_equivalence_volume(C_acid: float, V_acid: float, C_base: float) -> float:
    """Titration equivalence point: V_base = (C_acid * V_acid) / C_base (mL or L)."""
    if C_base <= 0:
        raise ValueError("Base concentration must be positive")
    return float((C_acid * V_acid) / C_base)


_OPERATIONS = {
    "ph_from_h": _ph_from_h,
    "poh_from_oh": _poh_from_oh,
    "h_from_ph": _h_from_ph,
    "oh_from_poh": _oh_from_poh,
    "poh_from_ph": _poh_from_ph,
    "henderson_hasselbalch": _henderson_hasselbalch,
    "ka_from_pka": _ka_from_pka,
    "pka_from_ka": _pka_from_ka,
    "weak_acid_ph": _weak_acid_ph,
    "titration_equivalence_volume": _titration_equivalence_volume,
}


@register("chemistry.acid_base_equilibrium")
class ChemistryAcidBaseSolver(SolverBase):
    """Solver for acid-base equilibrium: pH, pOH, buffer equations, titration."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Acid-base equilibrium solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
