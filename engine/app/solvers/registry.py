"""Solver registry with auto-loading via module discovery."""
import pkgutil
import importlib
from typing import Dict, Optional, Type
from app.solvers.base import SolverBase

# Global registry: domain string -> SolverBase subclass
_SOLVERS: Dict[str, Type[SolverBase]] = {}
_LOADED = False


def register(domain: str):
    """
    Class decorator to register a solver for a domain.

    Usage:
        @register("mathematics.algebra")
        class AlgebraSolver(SolverBase):
            ...
    """
    def decorator(cls: Type[SolverBase]) -> Type[SolverBase]:
        if not issubclass(cls, SolverBase):
            raise TypeError(f"{cls.__name__} must inherit from SolverBase")
        _SOLVERS[domain] = cls
        return cls
    return decorator


def get_solver(domain: str) -> Optional[Type[SolverBase]]:
    """Get the solver class for a domain, or None if not registered."""
    return _SOLVERS.get(domain)


def load_all() -> None:
    """
    Auto-discover and import all solver modules in this package.
    Each module's @register decorators populate the global registry.
    Call this once at startup (idempotent).
    """
    global _LOADED
    if _LOADED:
        return

    # Import all modules in this package except __init__ and registry
    import app.solvers as solvers_pkg
    for importer, modname, ispkg in pkgutil.iter_modules(solvers_pkg.__path__):
        if modname not in ("registry", "base"):
            importlib.import_module(f"app.solvers.{modname}")

    _LOADED = True
