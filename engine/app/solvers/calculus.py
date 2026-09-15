"""Symbolic calculus solver (mathematics.calculus domain)."""
import re
from typing import Optional, Tuple, List, Any, Dict
import sympy as sp
from sympy import symbols, diff, integrate, limit, sympify, oo

from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.calculus")
class CalculusSolver(SolverBase):
    """
    Specialized solver for symbolic calculus: derivatives, integrals, limits.
    Parses equations with format: <operation>(<expr>, <variable>[, <bounds>])
    Operations: diff, integrate, limit
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve calculus problems using SymPy.

        Expects one equation with format:
          lhs = "<operation>(<expr>, <variable>[, <bounds>])"
          e.g., "diff(sin(x), x)", "integrate(x**2, x, 0, 1)", "limit(sin(x)/x, x, 0)"
        """
        try:
            if not model.equations:
                return SolverResult(
                    success=False,
                    message="No equations provided",
                    error="At least one equation is required"
                )

            equation = model.equations[0]
            lhs = equation.lhs.strip()

            # Parse the calculus operation from LHS
            operation, expr_str, variable_str, bounds = self._parse_equation(lhs)

            if operation is None:
                return SolverResult(
                    success=False,
                    message="Could not parse equation",
                    error=f"Expected format: <operation>(<expr>, <variable>[, <bounds>])"
                )

            # Parse expression and create symbols
            variables_list = self._extract_symbols(expr_str)
            symbol_dict = {var: symbols(var, real=True) for var in variables_list}

            # Create variable symbol
            if variable_str not in symbol_dict:
                symbol_dict[variable_str] = symbols(variable_str, real=True)
            var = symbol_dict[variable_str]

            # Parse and evaluate expression with substituted symbols
            try:
                expr = sympify(expr_str, locals=symbol_dict)
            except Exception as e:
                return SolverResult(
                    success=False,
                    message=f"Failed to parse expression: {expr_str}",
                    error=str(e)
                )

            # Perform operation
            if operation == "diff":
                try:
                    result = diff(expr, var)
                    result_str = str(result)
                    summary = {"result": result_str, "operation": "derivative"}
                except Exception as e:
                    return SolverResult(
                        success=False,
                        message="Differentiation failed",
                        error=str(e)
                    )

            elif operation == "integrate":
                try:
                    if bounds:
                        # Definite integral
                        lower, upper = bounds
                        result = integrate(expr, (var, lower, upper))
                        result_numeric = float(result) if result.is_number else result
                        summary = {
                            "result": str(result_numeric),
                            "operation": "definite_integral",
                            "bounds": {"lower": float(lower), "upper": float(upper)}
                        }
                    else:
                        # Indefinite integral (without constant of integration)
                        result = integrate(expr, var)
                        result_str = str(result)
                        summary = {"result": result_str, "operation": "indefinite_integral"}
                except Exception as e:
                    return SolverResult(
                        success=False,
                        message="Integration failed",
                        error=str(e)
                    )

            elif operation == "limit":
                try:
                    if not bounds or len(bounds) < 1:
                        return SolverResult(
                            success=False,
                            message="Limit requires bounds: limit(<expr>, <var>, <point>)",
                            error="Missing limit point"
                        )
                    limit_point = bounds[0]
                    result = limit(expr, var, limit_point)

                    # Convert result to numeric or string
                    if result is sp.oo:
                        result_str = "oo"
                    elif result is -sp.oo:
                        result_str = "-oo"
                    elif result.is_number:
                        result_str = str(float(result))
                    else:
                        result_str = str(result)

                    summary = {
                        "result": result_str,
                        "operation": "limit",
                        "point": str(limit_point)
                    }
                except Exception as e:
                    return SolverResult(
                        success=False,
                        message="Limit computation failed",
                        error=str(e)
                    )

            else:
                return SolverResult(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    error=f"Expected one of: diff, integrate, limit"
                )

            return SolverResult(
                success=True,
                message=f"{operation.capitalize()} computed successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _parse_equation(self, equation: str) -> Tuple[Optional[str], str, str, Optional[Tuple]]:
        """
        Parse equation in format: <operation>(<expr>, <variable>[, <bounds>])

        Returns: (operation, expr_str, variable_str, bounds)
        where bounds is None or a tuple of boundary values for definite integrals/limits
        """
        # Match pattern: operation(contents)
        match = re.match(r'(\w+)\((.*)\)', equation.strip())
        if not match:
            return None, "", "", None

        operation = match.group(1).lower()
        contents = match.group(2)

        # Split on top-level commas only (not within parentheses)
        parts = self._split_arguments(contents)

        if len(parts) < 2:
            return None, "", "", None

        expr_str = parts[0].strip()
        variable_str = parts[1].strip()
        bounds = None

        if operation == "integrate" and len(parts) >= 4:
            # Definite integral: integrate(expr, var, lower, upper)
            try:
                lower = sympify(parts[2].strip())
                upper = sympify(parts[3].strip())
                bounds = (lower, upper)
            except Exception:
                pass

        elif operation == "limit" and len(parts) >= 3:
            # Limit: limit(expr, var, point)
            try:
                limit_point = sympify(parts[2].strip())
                bounds = (limit_point,)
            except Exception:
                pass

        return operation, expr_str, variable_str, bounds

    def _split_arguments(self, s: str) -> List[str]:
        """
        Split a string by commas, respecting nested parentheses.

        Example: "sin(x), x, 0, pi" -> ["sin(x)", "x", "0", "pi"]
        """
        parts = []
        current = []
        depth = 0

        for char in s:
            if char == '(' or char == '[':
                depth += 1
                current.append(char)
            elif char == ')' or char == ']':
                depth -= 1
                current.append(char)
            elif char == ',' and depth == 0:
                parts.append(''.join(current))
                current = []
            else:
                current.append(char)

        if current:
            parts.append(''.join(current))

        return parts

    def _extract_symbols(self, expr_str: str) -> List[str]:
        """
        Extract all symbol names from an expression string.

        Looks for valid Python identifiers (variable names).
        """
        # Match valid Python identifiers that are not SymPy functions
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        candidates = re.findall(pattern, expr_str)

        # Filter out SymPy functions and constants
        sympy_funcs = {
            'sin', 'cos', 'tan', 'sqrt', 'exp', 'log', 'ln', 'abs',
            'sinh', 'cosh', 'tanh', 'asin', 'acos', 'atan',
            'factorial', 'factorial2', 'binomial', 'fib',
            'Abs', 'Max', 'Min', 'Piecewise', 'atan2',
            'e', 'pi', 'I', 'oo', 'nan'
        }

        symbols_list = []
        for candidate in candidates:
            if candidate not in sympy_funcs and not hasattr(sp, candidate):
                if candidate not in symbols_list:
                    symbols_list.append(candidate)

        return symbols_list
