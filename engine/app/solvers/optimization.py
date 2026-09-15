"""Optimization solver (mathematics.optimization domain)."""
from typing import Dict, List, Optional
import numpy as np
from scipy.optimize import minimize, fsolve
import sympy as sp

from app.model import ScientificModel, SolverMethod, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.optimization")
class OptimizationSolver(SolverBase):
    """
    Optimization solver supporting:
    - Unconstrained minimization/maximization
    - Root-finding
    - Basic linear programming
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve optimization problems.

        Problem types are inferred from:
        - Equations: first equation is objective/root, rest are constraints
        - Unknown quantities: decision variables to optimize over
        - Solver method: determines algorithm (minimize, fsolve, etc.)
        """
        try:
            # Extract decision variables (unknowns)
            decision_vars = [
                q for q in model.quantities if not q.isKnown
            ]
            if not decision_vars:
                return SolverResult(
                    success=False,
                    message="No decision variables (unknown quantities)",
                    error="At least one unknown quantity required"
                )

            var_names = [q.name for q in decision_vars]

            # Extract objective/constraint equations
            if not model.equations:
                return SolverResult(
                    success=False,
                    message="No equations provided",
                    error="At least one equation required"
                )

            known_values = {q.name: q.value for q in model.quantities if q.isKnown}
            ic = model.initialConditions or {}
            known_values.update(ic)

            # Determine problem type and solve
            if model.solver.method == SolverMethod.FSOLVE:
                return self._solve_root_finding(model, var_names, known_values)
            elif model.solver.method == SolverMethod.SYMBOLIC_SOLVE:
                return self._solve_symbolic(model, var_names, known_values)
            else:
                # Default: minimize/maximize
                return self._solve_optimization(model, var_names, known_values)

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _solve_optimization(self, model: ScientificModel, var_names: List[str],
                           known_values: Dict[str, float]) -> SolverResult:
        """
        Unconstrained or constrained minimization/maximization.
        Uses scipy.optimize.minimize with chosen method.
        """
        objective_eq = model.equations[0]

        # Parse objective function
        try:
            obj_expr = sp.sympify(objective_eq.rhs)
            obj_func = self._compile_to_callable(obj_expr, var_names, known_values)
        except Exception as e:
            return SolverResult(
                success=False,
                message="Failed to parse objective function",
                error=str(e)
            )

        # Initial guess: zeros for all variables
        x0 = np.zeros(len(var_names))

        # Determine if maximization (check if objective is prefixed with "max_" or similar)
        is_maximize = objective_eq.lhs.lower().startswith("max")

        # Build constraints if present
        constraints = []
        for constraint_eq in model.equations[1:]:
            try:
                if constraint_eq.lhs.lower() in ("constraint", "c"):
                    # Constraint as rhs = 0
                    const_expr = sp.sympify(constraint_eq.rhs)
                    const_func = self._compile_to_callable(const_expr, var_names, known_values)
                    constraints.append({"type": "eq", "fun": const_func})
            except Exception:
                pass

        # Solve
        try:
            scipy_method = self._map_solver_method(model.solver.method)

            # For maximization, negate objective
            obj_func_actual = (lambda x: -obj_func(x)) if is_maximize else obj_func

            result = minimize(
                obj_func_actual,
                x0,
                method=scipy_method,
                constraints=constraints,
                options={"gtol": model.solver.tolerance}
            )

            if not result.success:
                return SolverResult(
                    success=False,
                    message=f"Minimization failed: {result.message}",
                    error=result.message
                )

            optimal_value = obj_func(result.x)

            # Flatten solution_point into summary: x_opt, y_opt, etc.
            summary = {}
            for i, var_name in enumerate(var_names):
                summary[f"{var_name}_opt"] = float(result.x[i])

            summary["optimal_value"] = float(optimal_value)
            summary["iterations"] = float(result.nit if hasattr(result, 'nit') else 0)
            summary["function_evaluations"] = float(result.nfev if hasattr(result, 'nfev') else 0)

            return SolverResult(
                success=True,
                message="Optimization solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Optimization error",
                error=str(e)
            )

    def _solve_root_finding(self, model: ScientificModel, var_names: List[str],
                           known_values: Dict[str, float]) -> SolverResult:
        """
        Root-finding for scalar equations using fsolve.
        """
        if len(var_names) != 1:
            return SolverResult(
                success=False,
                message="fsolve supports scalar root-finding only",
                error=f"Expected 1 variable, got {len(var_names)}"
            )

        equation = model.equations[0]

        try:
            # Parse as f(x) = rhs, find root of f(x) - rhs
            lhs_expr = sp.sympify(equation.lhs)
            rhs_expr = sp.sympify(equation.rhs)

            # Root-finding: lhs - rhs = 0
            root_expr = lhs_expr - rhs_expr
            root_func = self._compile_to_callable(root_expr, var_names, known_values)
        except Exception as e:
            return SolverResult(
                success=False,
                message="Failed to parse equation for root-finding",
                error=str(e)
            )

        # Initial guess: try 1.0 if the problem doesn't work with 0
        # This helps with cubic and higher-order polynomials
        x0 = np.array([1.0])

        try:
            roots = fsolve(root_func, x0, full_output=True)
            sol_x, info_dict, ier, msg = roots

            if ier != 1:
                return SolverResult(
                    success=False,
                    message=f"Root-finding failed: {msg.strip()}",
                    error=msg.strip()
                )

            root_value = float(sol_x[0])

            summary = {
                "root": root_value,
                "function_value": float(root_func(sol_x)),
                "iterations": float(info_dict['nfev']),
            }

            return SolverResult(
                success=True,
                message="Root found successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Root-finding error",
                error=str(e)
            )

    def _solve_symbolic(self, model: ScientificModel, var_names: List[str],
                       known_values: Dict[str, float]) -> SolverResult:
        """
        Symbolic solving using SymPy.
        """
        try:
            equations_to_solve = []
            symbols = {name: sp.Symbol(name) for name in var_names}

            for eq in model.equations:
                lhs_expr = sp.sympify(eq.lhs)
                rhs_expr = sp.sympify(eq.rhs)

                # Substitute known values
                for name, value in known_values.items():
                    if name not in var_names:
                        lhs_expr = lhs_expr.subs(name, value)
                        rhs_expr = rhs_expr.subs(name, value)

                equations_to_solve.append(sp.Eq(lhs_expr, rhs_expr))

            # Solve symbolically
            solutions = sp.solve(equations_to_solve, [symbols[name] for name in var_names])

            if not solutions:
                return SolverResult(
                    success=False,
                    message="No symbolic solutions found",
                    error="System may be inconsistent or have no solutions"
                )

            # Handle different solution formats from sp.solve
            summary = {}

            if not isinstance(solutions, list):
                solutions = [solutions]

            # If solutions is empty, return error
            if not solutions:
                return SolverResult(
                    success=False,
                    message="No symbolic solutions found",
                    error="sp.solve returned empty list"
                )

            first_solution = solutions[0]

            # sp.solve can return:
            # - Dict: {Symbol('x'): value, ...} with Symbol keys
            # - Number/Expr: single value (for single variable)
            # - Tuple/List: multiple values in order
            if isinstance(first_solution, dict):
                # Dict with Symbol keys - need to use the symbols dict
                for var_name in var_names:
                    sym = symbols[var_name]  # Get the Symbol object
                    if sym in first_solution:
                        summary[f"{var_name}_sol"] = float(first_solution[sym])
            elif isinstance(first_solution, (list, tuple)):
                # Multiple values in order
                for i, var_name in enumerate(var_names):
                    if i < len(first_solution):
                        summary[f"{var_name}_sol"] = float(first_solution[i])
            else:
                # Single value (for single variable)
                if len(var_names) == 1:
                    summary[f"{var_names[0]}_sol"] = float(first_solution)
                else:
                    return SolverResult(
                        success=False,
                        message="Could not parse symbolic solution",
                        error=f"Unexpected solution format: {type(first_solution)}"
                    )

            return SolverResult(
                success=True,
                message="Symbolic solution found",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Symbolic solving error",
                error=str(e)
            )

    def _compile_to_callable(self, expr: sp.Expr, var_names: List[str],
                            known_values: Dict[str, float]):
        """
        Compile SymPy expression to callable function.
        """
        # Substitute known values
        for name, value in known_values.items():
            if name not in var_names:
                expr = expr.subs(name, value)

        # Create callable lambda
        symbols = [sp.Symbol(name) for name in var_names]

        def func(x_array):
            # x_array is numpy array of decision variable values
            subs_dict = {symbols[i]: x_array[i] for i in range(len(var_names))}
            return float(expr.subs(subs_dict))

        return func

    def _map_solver_method(self, method: SolverMethod) -> str:
        """Map SolverMethod enum to scipy.optimize.minimize method."""
        mapping = {
            SolverMethod.RK45: "BFGS",
            SolverMethod.RK23: "BFGS",
            SolverMethod.SOLVE_IVP: "BFGS",
            SolverMethod.ODEINT: "BFGS",
        }
        return mapping.get(method, "BFGS")
