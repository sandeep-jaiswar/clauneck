"""Base class for all domain-specific solvers."""
from abc import ABC, abstractmethod
from app.model import ScientificModel, SolverResult


class SolverBase(ABC):
    """Abstract base class for all scientific solvers."""

    @abstractmethod
    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve the given scientific model.

        Args:
            model: A validated ScientificModel instance.

        Returns:
            SolverResult with success flag, message, and domain-specific results.
        """
        pass
