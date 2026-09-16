"""Physical and chemical constants for solvers.

Loads constants from constants.json and provides convenient access via module-level
attributes, reducing hardcoded magic numbers across solvers.

Usage:
    from app.constants import PLANCK_CONSTANT, SPEED_OF_LIGHT, GAS_CONSTANT
    wavelength = PLANCK_CONSTANT / momentum
"""

import json
import os
from typing import Dict, Any

# Path to constants.json (located at engine/data/constants.json)
_CONSTANTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "constants.json"
)


def _load_constants() -> Dict[str, Any]:
    """Load constants from JSON file."""
    with open(_CONSTANTS_PATH, "r") as f:
        return json.load(f)


_CONSTANTS_DB = _load_constants()


def get_constant(name: str, category: str = None) -> float:
    """
    Retrieve a constant by name.

    Args:
        name: Constant name (e.g., "speed_of_light", "planck_constant")
        category: Optional category to narrow search (e.g., "fundamental")

    Returns:
        float: The constant value in SI units

    Raises:
        KeyError: If constant not found
    """
    if category:
        if category not in _CONSTANTS_DB:
            raise KeyError(f"Category '{category}' not found in constants database")
        if name not in _CONSTANTS_DB[category]:
            raise KeyError(
                f"Constant '{name}' not found in category '{category}'"
            )
        return float(_CONSTANTS_DB[category][name]["value"])

    # Search across all categories
    for cat, consts in _CONSTANTS_DB.items():
        if cat in ["metadata"]:
            continue
        if name in consts:
            return float(consts[name]["value"])

    raise KeyError(f"Constant '{name}' not found in any category")


def get_constant_info(name: str, category: str = None) -> Dict[str, Any]:
    """
    Retrieve full constant information (value, unit, description, symbol).

    Args:
        name: Constant name
        category: Optional category to narrow search

    Returns:
        dict: Full constant entry with symbol, value, unit, description
    """
    if category:
        if category not in _CONSTANTS_DB:
            raise KeyError(f"Category '{category}' not found in constants database")
        if name not in _CONSTANTS_DB[category]:
            raise KeyError(
                f"Constant '{name}' not found in category '{category}'"
            )
        return _CONSTANTS_DB[category][name]

    # Search across all categories
    for cat, consts in _CONSTANTS_DB.items():
        if cat in ["metadata"]:
            continue
        if name in consts:
            return consts[name]

    raise KeyError(f"Constant '{name}' not found in any category")


# Module-level constants for direct import (most common use case)
# These are eagerly loaded from the JSON at module import time

# Fundamental constants
SPEED_OF_LIGHT = get_constant("speed_of_light")
PLANCK_CONSTANT = get_constant("planck_constant")
REDUCED_PLANCK_CONSTANT = get_constant("reduced_planck_constant")
ELEMENTARY_CHARGE = get_constant("elementary_charge")
AVOGADRO_CONSTANT = get_constant("avogadro_constant")
BOLTZMANN_CONSTANT = get_constant("boltzmann_constant")
GRAVITATIONAL_CONSTANT = get_constant("gravitational_constant")

# Particle physics
ELECTRON_MASS = get_constant("electron_mass")
PROTON_MASS = get_constant("proton_mass")
NEUTRON_MASS = get_constant("neutron_mass")

# Atomic and quantum
BOHR_RADIUS = get_constant("bohr_radius")
FINE_STRUCTURE_CONSTANT = get_constant("fine_structure_constant")
RYDBERG_ENERGY = get_constant("rydberg_energy")  # in eV
RYDBERG_ENERGY_JOULES = get_constant("rydberg_energy_joules")

# Chemistry
GAS_CONSTANT = get_constant("gas_constant")
FARADAY_CONSTANT = get_constant("faraday_constant")

# Thermodynamics
STEFAN_BOLTZMANN_CONSTANT = get_constant("stefan_boltzmann_constant")

# Classical physics
STANDARD_GRAVITY = get_constant("standard_gravity")

# Aliases for common naming conventions
h = PLANCK_CONSTANT
hbar = REDUCED_PLANCK_CONSTANT
c = SPEED_OF_LIGHT
e = ELEMENTARY_CHARGE
m_e = ELECTRON_MASS
m_p = PROTON_MASS
m_n = NEUTRON_MASS
a_0 = BOHR_RADIUS
k_B = BOLTZMANN_CONSTANT
N_A = AVOGADRO_CONSTANT
G = GRAVITATIONAL_CONSTANT
R = GAS_CONSTANT
F = FARADAY_CONSTANT
g = STANDARD_GRAVITY
sigma = STEFAN_BOLTZMANN_CONSTANT
alpha = FINE_STRUCTURE_CONSTANT
