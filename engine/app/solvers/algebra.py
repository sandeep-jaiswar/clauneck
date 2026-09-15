"""Algebraic equation solver (mathematics.algebra domain)."""
from typing import Dict, List, Any, Set
import sympy as sp
from sympy import symbols, sympify, Eq, linsolve, solve

from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.algebra")
class AlgebraSolver(SolverBase):
    """
    Symbolic algebraic solver using SymPy.
    Solves systems of polynomial and general algebraic equations.
    Deterministic: produces sorted, JSON-serializable results.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve algebraic equations for unknowns.

        Quantities: each variable (known with value, or unknown with isKnown=false).
        Equations: algebraic equations (lhs and rhs are SymPy-parseable expressions).
        Solver config: method in ["symbolic_solve", "fsolve"].

        Returns:
            SolverResult with success flag and summary dict containing solution sets.
            Each solution is a dict mapping variable names to values.
        """
        try:
            # Extract unknowns (isKnown=false) and known variables (isKnown=true)
            unknowns: Set[str] = set()
            known_vars: Dict[str, float] = {}

            for quantity in model.quantities:
                if quantity.isKnown:
                    # Known quantities: extract value for substitution
                    val = quantity.value
                    if isinstance(val, (int, float)):
                        known_vars[quantity.name] = float(val)
                    elif isinstance(val, list):
                        # For vectors/matrices, convert to list
                        known_vars[quantity.name] = val
                    else:
                        known_vars[quantity.name] = val
                else:
                    # Unknown: to be solved for
                    unknowns.add(quantity.name)

            if not unknowns:
                return SolverResult(
                    success=False,
                    message="No unknowns specified",
                    error="All quantities marked as known"
                )

            if not model.equations:
                return SolverResult(
                    success=False,
                    message="No equations provided",
                    error="Cannot solve without equations"
                )

            # Parse equations into SymPy Eq objects
            equations_list: List[Eq] = []
            for eq in model.equations:
                try:
                    lhs_expr = sympify(eq.lhs)
                    rhs_expr = sympify(eq.rhs)
                    equations_list.append(Eq(lhs_expr, rhs_expr))
                except Exception as e:
                    return SolverResult(
                        success=False,
                        message="Failed to parse equation",
                        error=f"Equation '{eq.lhs}={eq.rhs}': {str(e)}"
                    )

            # Substitute known values into equations
            substitutions = {sp.Symbol(name): val
                           for name, val in known_vars.items()}
            equations_substituted = [eq.subs(substitutions) for eq in equations_list]

            # Create SymPy symbols for unknowns
            unknown_symbols = [sp.Symbol(name) for name in sorted(unknowns)]

            # Solve the system
            # Try linsolve first (faster for linear systems)
            solutions = []
            try:
                # linsolve returns a FiniteSet of solutions (tuples for each)
                result = linsolve(equations_substituted, unknown_symbols)
                if result and len(result) > 0:
                    # linsolve succeeded
                    for sol_tuple in result:
                        sol_dict = {unknown_symbols[i]: sol_tuple[i]
                                   for i in range(len(unknown_symbols))}
                        solutions.append(sol_dict)
                else:
                    # Empty solution set from linsolve; try general solve
                    result = solve(equations_substituted, unknown_symbols, dict=True)
                    if result:
                        solutions = result
                    else:
                        return SolverResult(
                            success=False,
                            message="No solutions found",
                            error="The equation system has no solutions"
                        )
            except Exception as linsolve_err:
                # linsolve failed; try general solve
                try:
                    result = solve(equations_substituted, unknown_symbols, dict=True)
                    if result:
                        solutions = result
                    else:
                        return SolverResult(
                            success=False,
                            message="No solutions found",
                            error="The equation system has no solutions"
                        )
                except Exception as solve_err:
                    return SolverResult(
                        success=False,
                        message="Failed to solve system",
                        error=f"solve() failed: {str(solve_err)}"
                    )

            # Convert solutions to JSON-serializable dicts with sorted keys
            summary = self._convert_solutions(solutions, unknown_symbols)

            return SolverResult(
                success=True,
                message=f"Solved {len(equations_list)} equation(s) for {len(unknowns)} unknown(s)",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _convert_solutions(self, solutions: List[Dict],
                          unknown_symbols: List) -> Dict[str, float]:
        """
        Convert SymPy solutions to flat JSON-serializable dict of floats.

        For multiple solutions, uses keys like:
          solution_0_x, solution_0_y, solution_1_x, solution_1_y, ...
        For single solution, uses keys like:
          x, y, ...

        Args:
            solutions: List of dicts mapping SymPy symbols to values.
            unknown_symbols: List of SymPy symbols (for ordering).

        Returns:
            Flat dict with string keys mapping to float values.
        """
        summary = {}

        if len(solutions) == 1:
            # Single solution: use flat variable names
            sol_dict = solutions[0]
            for sym in sorted(unknown_symbols, key=lambda s: s.name):
                if sym in sol_dict:
                    value = sol_dict[sym]
                    summary[sym.name] = self._sympy_to_python(value)
        else:
            # Multiple solutions: use solution_{idx}_{var_name} format
            for idx, sol_dict in enumerate(solutions):
                for sym in sorted(unknown_symbols, key=lambda s: s.name):
                    if sym in sol_dict:
                        value = sol_dict[sym]
                        key = f"solution_{idx}_{sym.name}"
                        summary[key] = self._sympy_to_python(value)

        return summary

    def _sympy_to_python(self, value: Any) -> Any:
        """
        Convert SymPy numeric types to Python types for JSON serialization.

        Handles:
        - Rational -> float
        - Integer -> float
        - Float -> float
        - Complex -> {"real": float, "imag": float}
        - Infinity / -Infinity -> string "inf" / "-inf"
        """
        # Handle SymPy types
        if isinstance(value, sp.Rational):
            return float(value)
        elif isinstance(value, sp.Integer):
            return float(value)
        elif isinstance(value, sp.Float):
            return float(value)
        elif isinstance(value, sp.complexes.ComplexNumber):
            # SymPy complex number
            return {
                "real": float(sp.re(value)),
                "imag": float(sp.im(value))
            }
        elif isinstance(value, sp.Infinity):
            return "inf"
        elif isinstance(value, sp.NegativeInfinity):
            return "-inf"
        elif isinstance(value, complex):
            # Python native complex
            return {
                "real": float(value.real),
                "imag": float(value.imag)
            }
        elif isinstance(value, (int, float)):
            # Native Python types
            return float(value)
        elif isinstance(value, str):
            # Symbolic result that couldn't be simplified
            return value
        else:
            # Fallback: convert to string
            return str(value)
