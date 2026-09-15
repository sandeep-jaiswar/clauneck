"""Trigonometric operations solver (mathematics.trigonometry domain)."""
from typing import Dict, Optional, Tuple
import numpy as np
import sympy as sp
from sympy import symbols, sin, cos, tan, asin, acos, atan, rad, deg, solve, sqrt

from app.model import ScientificModel, SolverMethod, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.trigonometry")
class TrigonometrySolver(SolverBase):
    """
    Specialized solver for trigonometric operations:
    - Evaluate trig functions (sin, cos, tan, etc.)
    - Solve trig equations
    - Solve triangles using law of sines/cosines
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve trigonometric problem based on equations and known quantities.
        Supports:
          - Simple trig evaluation: e.g., sin(angle) = result
          - Law of cosines: c^2 = a^2 + b^2 - 2*a*b*cos(C)
          - Law of sines: a/sin(A) = b/sin(B) = c/sin(C)
          - General trig equation solving
        """
        try:
            quantities = {q.name: q for q in model.quantities}
            ic = model.initialConditions or {}

            # Check if this is a triangle problem (law of sines/cosines)
            if self._is_triangle_problem(quantities, model.equations):
                return self._solve_triangle(model, quantities, ic)

            # Otherwise, solve as general trig equations
            return self._solve_trig_equations(model, quantities, ic)

        except Exception as e:
            return SolverResult(
                success=False,
                message="Trigonometry solver error",
                error=str(e)
            )

    def _is_triangle_problem(self, quantities: Dict[str, Quantity],
                            equations) -> bool:
        """Detect if this is a triangle-solving problem."""
        # Look for quantity patterns: sides (a, b, c) and angles (A, B, C)
        # or common names like side1, side2, angle, etc.
        quantity_names = {q.name for q in quantities.values()}
        has_sides = any(name in quantity_names
                       for name in ["a", "b", "c", "side1", "side2", "side3"])
        has_angles = any(name in quantity_names
                        for name in ["A", "B", "C", "angle_A", "angle_B", "angle_C",
                                   "angle1", "angle2", "angle3"])

        # Check for law of cosines or law of sines patterns
        for eq in equations:
            if "**2" in eq.lhs or "**2" in eq.rhs:  # law of cosines
                if "cos" in eq.rhs:
                    return True
            if "sin" in eq.lhs or "sin" in eq.rhs:  # law of sines
                if "/" in eq.lhs and "/" in eq.rhs:
                    return True

        return has_sides and has_angles

    def _solve_triangle(self, model: ScientificModel,
                       quantities: Dict[str, Quantity],
                       ic: Dict[str, float]) -> SolverResult:
        """
        Solve triangle given known sides/angles using law of cosines/sines.
        Example: Given a, b, C (angle between them), find c.
        """
        try:
            # Extract sides and angles
            known_values = {}
            for q in model.quantities:
                if q.isKnown:
                    val = q.value if q.value is not None else ic.get(q.name)
                    if val is not None:
                        # Convert angles from degrees to radians if needed
                        if q.siUnit == "deg" and q.name.upper() in ["A", "B", "C"]:
                            val = np.radians(val)
                        known_values[q.name] = val

            # Find unknowns (quantities marked as isKnown=False)
            unknowns = []
            for q in model.quantities:
                if not q.isKnown:
                    unknowns.append(q.name)

            # Attempt to solve using the given equations
            results = self._apply_triangle_laws(known_values, unknowns, model.equations)

            if not results:
                return SolverResult(
                    success=False,
                    message="Could not solve triangle with given information",
                    error="Insufficient constraints"
                )

            # Flatten results for summary (Dict[str, float])
            summary = {}
            for name, value in results.items():
                summary[name] = float(value)

            return SolverResult(
                success=True,
                message="Triangle solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Triangle solving error",
                error=str(e)
            )

    def _apply_triangle_laws(self, known: Dict[str, float],
                            unknowns: list, equations) -> Dict[str, float]:
        """Apply law of cosines/sines to solve for unknowns."""
        results = {}

        for eq in equations:
            # Parse the equation and try to solve
            try:
                # Create symbols for all variables
                all_vars = set(known.keys()) | set(unknowns)
                sym_dict = {var: symbols(var, real=True, positive=True)
                           for var in all_vars}

                # Try to parse and solve the equation
                lhs_expr = self._parse_expression(eq.lhs, sym_dict)
                rhs_expr = self._parse_expression(eq.rhs, sym_dict)

                # Solve for unknowns
                for unknown in unknowns:
                    if unknown in results:
                        continue

                    try:
                        # Substitute known values
                        eq_with_known = lhs_expr - rhs_expr
                        for var, val in known.items():
                            if var in sym_dict:
                                eq_with_known = eq_with_known.subs(sym_dict[var], val)

                        # Solve for the unknown
                        sol = solve(eq_with_known, sym_dict[unknown])
                        if sol:
                            # Take the positive real solution
                            for s in sol:
                                if isinstance(s, (int, float)) and s > 0:
                                    results[unknown] = float(s)
                                    known[unknown] = float(s)
                                    break
                                elif isinstance(s, sp.Expr):
                                    val = float(s.evalf())
                                    if val > 0:
                                        results[unknown] = val
                                        known[unknown] = val
                                        break
                    except Exception:
                        continue

            except Exception:
                continue

        return results

    def _solve_trig_equations(self, model: ScientificModel,
                             quantities: Dict[str, Quantity],
                             ic: Dict[str, float]) -> SolverResult:
        """
        Solve general trigonometric equations.
        Example: sin(x) = 0.5 where x is the angle to solve for.
        """
        try:
            # Identify the unknown variable
            unknowns = [q.name for q in model.quantities if not q.isKnown]
            known_values = {}

            for q in model.quantities:
                if q.isKnown:
                    val = q.value if q.value is not None else ic.get(q.name)
                    if val is not None:
                        # Convert angles from degrees to radians if needed
                        if q.siUnit == "deg":
                            val = np.radians(val)
                        known_values[q.name] = val

            if not unknowns:
                # No unknowns; just evaluate the expressions
                return self._evaluate_trig_expressions(model, known_values, quantities)

            # Solve equations for unknowns
            results = {}
            for unknown in unknowns:
                for eq in model.equations:
                    sol = self._solve_single_equation(eq, unknown, known_values)
                    if sol is not None:
                        results[unknown] = float(sol)
                        known_values[unknown] = float(sol)

            # Flatten results for summary (Dict[str, float])
            summary = {}
            for name, value in results.items():
                summary[name] = float(value)

            return SolverResult(
                success=True,
                message="Trigonometric equations solved",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Trig equation solving error",
                error=str(e)
            )

    def _evaluate_trig_expressions(self, model: ScientificModel,
                                  known_values: Dict[str, float],
                                  quantities: Dict[str, Quantity]) -> SolverResult:
        """Evaluate trig expressions with known values."""
        try:
            # Flatten results for summary (Dict[str, float])
            summary = {}

            for eq in model.equations:
                # Evaluate both sides with known values
                try:
                    rhs_val = self._evaluate_expression(eq.rhs, known_values)
                    # Store the evaluated result
                    key = eq.description or f"eval_{eq.lhs}"
                    summary[key] = float(rhs_val)
                except Exception:
                    # If evaluation fails, skip this equation
                    continue

            return SolverResult(
                success=True,
                message="Trig expressions evaluated successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Expression evaluation error",
                error=str(e)
            )

    def _solve_single_equation(self, equation, unknown: str,
                              known_values: Dict[str, float]) -> Optional[float]:
        """Solve a single equation for an unknown."""
        try:
            # Create symbolic variable
            x = symbols(unknown, real=True)

            # Parse the equation
            lhs_expr = self._parse_expression(equation.lhs, {unknown: x})
            rhs_expr = self._parse_expression(equation.rhs, {unknown: x})

            # Substitute known values into both sides
            for var, val in known_values.items():
                lhs_expr = lhs_expr.subs(symbols(var, real=True), val)
                rhs_expr = rhs_expr.subs(symbols(var, real=True), val)

            # Solve for the unknown
            equation_expr = lhs_expr - rhs_expr
            solutions = solve(equation_expr, x)

            if solutions:
                # Return the first real positive solution
                for sol in solutions:
                    if isinstance(sol, (int, float)):
                        return float(sol)
                    elif isinstance(sol, sp.Expr):
                        val = float(sol.evalf())
                        return val

        except Exception:
            pass

        return None

    def _parse_expression(self, expr_str: str, symbol_dict: Dict = None) -> sp.Expr:
        """Parse a string expression into a SymPy expression."""
        if symbol_dict is None:
            symbol_dict = {}

        # Create local namespace for evaluation
        local_ns = {
            'sin': sin, 'cos': cos, 'tan': tan,
            'asin': asin, 'acos': acos, 'atan': atan,
            'sqrt': sqrt, 'pi': sp.pi, 'e': sp.E,
            'rad': rad, 'deg': deg
        }
        local_ns.update(symbol_dict)

        # Parse the expression
        try:
            return sp.sympify(expr_str, locals=local_ns)
        except Exception:
            # If sympify fails, try with more lenient parsing
            return sp.sympify(expr_str)

    def _evaluate_expression(self, expr_str: str,
                            known_values: Dict[str, float]) -> float:
        """Numerically evaluate an expression with known values."""
        try:
            # Create local namespace for evaluation
            local_ns = {
                'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
                'asin': np.arcsin, 'acos': np.arccos, 'atan': np.arctan,
                'sqrt': np.sqrt, 'pi': np.pi, 'e': np.e,
                'rad': np.radians, 'deg': np.degrees
            }
            local_ns.update(known_values)

            # Evaluate the expression
            result = eval(expr_str, {"__builtins__": {}}, local_ns)
            return float(result)
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression '{expr_str}': {e}")

    def _get_value(self, quantities: Dict[str, Quantity],
                   name: str, ic: Dict[str, float]) -> float:
        """Get a quantity value from initial conditions or quantity definition."""
        if name in ic:
            return ic[name]
        if name in quantities and quantities[name].value is not None:
            val = quantities[name].value
            if isinstance(val, (int, float)):
                return float(val)
            else:
                raise ValueError(f"Expected scalar value for {name}, got {type(val)}")
        raise ValueError(f"No value for quantity: {name}")
