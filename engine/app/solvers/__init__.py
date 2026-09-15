"""Solver package: registry-based domain dispatch for scientific solving."""
from .registry import register, get_solver, load_all
from .base import SolverBase

__all__ = ["register", "get_solver", "load_all", "SolverBase"]
