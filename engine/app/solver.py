"""
Deterministic solver dispatcher: routes to domain-specific solvers via registry.
All computation is deterministic given fixed Model input.
"""
from app.model import ScientificModel, SolverResult
from app.solvers import registry


class GeneralSolver:
    """
    Extensible solver dispatcher: routes to domain-specific solvers via registry.
    """

    def __init__(self):
        # Load all registered solvers on first instantiation
        registry.load_all()

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Route to the appropriate specialized solver based on domain.

        For physics.mechanics, also perform a structural check to ensure
        required quantities and equations are present (backward compatibility).
        """
        # Special handling for physics.mechanics: structural fingerprint check
        if model.domain == "physics.mechanics":
            quantity_names = {quantity.name for quantity in model.quantities}
            equation_lhss = {equation.lhs.replace(" ", "") for equation in model.equations}
            required_quantities = {"v0", "angle", "mass", "g"}
            required_equations = {"d2x/dt2", "d2y/dt2"}
            if not (required_quantities <= quantity_names
                    and required_equations <= equation_lhss):
                return SolverResult(
                    success=False,
                    message="physics.mechanics requires v0, angle, mass, g quantities and d2x/dt2, d2y/dt2 equations",
                    error="Missing required quantities or equations"
                )

        # Look up solver for this domain
        solver_cls = registry.get_solver(model.domain)
        if solver_cls is None:
            return SolverResult(
                success=False,
                message=f"Domain '{model.domain}' not yet implemented",
                error="No solver for this domain"
            )

        # Instantiate and solve
        try:
            solver = solver_cls()
            return solver.solve(model)
        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver instantiation error",
                error=str(e)
            )
