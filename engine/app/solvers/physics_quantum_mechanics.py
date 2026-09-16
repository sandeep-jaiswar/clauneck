"""Quantum mechanics solver (physics.quantum_mechanics domain)."""
from typing import Dict
import numpy as np
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch
from app.constants import (
    PLANCK_CONSTANT,
    REDUCED_PLANCK_CONSTANT,
    SPEED_OF_LIGHT,
    ELECTRON_MASS,
    ELEMENTARY_CHARGE,
    BOHR_RADIUS,
)


def _de_broglie_wavelength(h: float, p: float) -> float:
    """De Broglie wavelength: λ = h / p (meters)."""
    if p <= 0:
        raise ValueError("Momentum p must be positive")
    return float(h / p)


def _photon_energy(h: float, f: float) -> float:
    """Photon energy: E = h * f (Joules)."""
    if f < 0:
        raise ValueError("Frequency f must be non-negative")
    return float(h * f)


def _photoelectric_kinetic_energy(h: float, f: float, phi: float) -> float:
    """Photoelectric kinetic energy: KE = h*f - φ (Joules), where φ is work function."""
    if f < 0:
        raise ValueError("Frequency f must be non-negative")
    if phi < 0:
        raise ValueError("Work function φ must be non-negative")
    ke = h * f - phi
    if ke < 0:
        raise ValueError("Frequency too low; photon energy does not exceed work function")
    return float(ke)


def _photoelectric_stopping_voltage(KE_max: float, e: float) -> float:
    """Photoelectric stopping voltage: V_s = KE_max / e (Volts)."""
    if e <= 0:
        raise ValueError("Elementary charge e must be positive")
    if KE_max < 0:
        raise ValueError("Maximum kinetic energy must be non-negative")
    return float(KE_max / e)


def _particle_in_box_energy(n: float, h: float, m: float, L: float) -> float:
    """Particle in a box energy level: E_n = n² * h² / (8 * m * L²) (Joules)."""
    if n <= 0 or int(n) != n:
        raise ValueError("Quantum number n must be a positive integer")
    if m <= 0:
        raise ValueError("Mass m must be positive")
    if L <= 0:
        raise ValueError("Box length L must be positive")
    return float((n**2 * h**2) / (8.0 * m * L**2))


def _bohr_energy_level(n: float) -> float:
    """Bohr model energy level: E_n = -13.6 eV / n² (converted to Joules)."""
    if n <= 0 or int(n) != n:
        raise ValueError("Quantum number n must be a positive integer")
    # -13.6 eV in Joules (Rydberg energy)
    energy_eV = -13.6 / (n**2)
    return float(energy_eV * ELEMENTARY_CHARGE)


def _bohr_radius(n: float) -> float:
    """Bohr model orbital radius: a_n = n² * a_0 (meters), where a_0 is Bohr radius."""
    if n <= 0 or int(n) != n:
        raise ValueError("Quantum number n must be a positive integer")
    return float(n**2 * BOHR_RADIUS)


def _heisenberg_uncertainty_momentum(delta_x: float, hbar: float) -> float:
    """Heisenberg uncertainty principle (momentum): Δp ≥ hbar / (2 * Δx) (kg⋅m/s)."""
    if delta_x <= 0:
        raise ValueError("Position uncertainty Δx must be positive")
    if hbar <= 0:
        raise ValueError("Reduced Planck constant hbar must be positive")
    return float(hbar / (2.0 * delta_x))


def _compton_shift(h: float, m_e: float, c: float, theta: float) -> float:
    """Compton shift: Δλ = (h / (m_e * c)) * (1 - cos(θ)) (meters)."""
    if m_e <= 0:
        raise ValueError("Electron mass m_e must be positive")
    if c <= 0:
        raise ValueError("Speed of light c must be positive")
    if h <= 0:
        raise ValueError("Planck constant h must be positive")
    compton_wavelength = h / (m_e * c)
    return float(compton_wavelength * (1.0 - np.cos(theta)))


_OPERATIONS = {
    "de_broglie_wavelength": _de_broglie_wavelength,
    "photon_energy": _photon_energy,
    "photoelectric_kinetic_energy": _photoelectric_kinetic_energy,
    "photoelectric_stopping_voltage": _photoelectric_stopping_voltage,
    "particle_in_box_energy": _particle_in_box_energy,
    "bohr_energy_level": _bohr_energy_level,
    "bohr_radius": _bohr_radius,
    "heisenberg_uncertainty_momentum": _heisenberg_uncertainty_momentum,
    "compton_shift": _compton_shift,
}


@register("physics.quantum_mechanics")
class PhysicsQuantumMechanicsSolver(SolverBase):
    """
    Specialized solver for introductory quantum mechanics: de Broglie wavelength,
    photon energy, photoelectric effect, particle in a box, Bohr model,
    Heisenberg uncertainty principle, Compton scattering.
    All calculations are closed-form (no PDE/eigenvalue solving).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve quantum mechanics problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Quantum mechanics solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
