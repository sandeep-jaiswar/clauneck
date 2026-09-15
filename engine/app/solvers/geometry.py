"""Geometry solver for mathematics.geometry domain."""
import re
import math
from typing import Dict, Tuple, Optional
from sympy import symbols, pi, sqrt, solve, simplify

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.geometry")
class GeometrySolver(SolverBase):
    """
    Solver for geometric calculations: areas, perimeters, volumes.
    Supports standard shapes: circle, triangle, rectangle, sphere, cylinder, cone.
    Can solve for unknown dimensions given constraints.
    """

    # Geometric formulas
    FORMULAS = {
        # Circle
        "area_circle": lambda r: pi * r**2,
        "perimeter_circle": lambda r: 2 * pi * r,
        "circumference": lambda r: 2 * pi * r,
        # Triangle
        "area_triangle": lambda base, height: base * height / 2,
        "perimeter_triangle_sides": lambda a, b, c: a + b + c,
        # Rectangle
        "area_rectangle": lambda length, width: length * width,
        "perimeter_rectangle": lambda length, width: 2 * (length + width),
        # Sphere
        "area_sphere": lambda r: 4 * pi * r**2,
        "volume_sphere": lambda r: 4 * pi * r**3 / 3,
        # Cylinder
        "area_cylinder_lateral": lambda r, h: 2 * pi * r * h,
        "area_cylinder_total": lambda r, h: 2 * pi * r * h + 2 * pi * r**2,
        "volume_cylinder": lambda r, h: pi * r**2 * h,
        # Cone
        "area_cone_lateral": lambda r, l: pi * r * l,
        "area_cone_total": lambda r, l: pi * r * l + pi * r**2,
        "volume_cone": lambda r, h: pi * r**2 * h / 3,
    }

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve geometric problem.
        Expected: equations with function-like RHS (e.g., "area = area_circle(r)")
        """
        try:
            # Extract quantities as a dict
            quantities_dict = {q.name: q for q in model.quantities}

            # Parse equations and compute results
            results = {}

            for equation in model.equations:
                result = self._solve_equation(equation, quantities_dict, model)
                if result is not None:
                    results.update(result)

            if not results:
                return SolverResult(
                    success=False,
                    message="No geometric equations could be evaluated",
                    error="No valid equations"
                )

            return SolverResult(
                success=True,
                message="Geometric problem solved successfully",
                summary=results
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Geometric solver error",
                error=str(e)
            )

    def _solve_equation(self, equation, quantities_dict: Dict[str, Quantity],
                        model: ScientificModel) -> Optional[Dict[str, float]]:
        """
        Solve a single geometric equation.
        Returns dict of computed values or None if not solvable.
        """
        lhs = equation.lhs.strip()
        rhs = equation.rhs.strip()

        # Case 1: Direct formula evaluation (e.g., "area = area_circle(r)")
        if "=" in lhs:
            # Handle "var = formula" format
            var_name = lhs.split("=")[0].strip()
            formula_rhs = rhs
        else:
            var_name = lhs
            formula_rhs = rhs

        # Try to evaluate the RHS formula
        result = self._evaluate_formula(formula_rhs, quantities_dict)
        if result is not None:
            return {var_name: float(result)}

        # Try to solve for unknowns (inverse problems)
        return self._solve_for_unknown(equation, quantities_dict)

    def _evaluate_formula(self, formula_str: str,
                          quantities_dict: Dict[str, Quantity]) -> Optional[float]:
        """
        Evaluate a formula string like 'area_circle(5)' or 'area_circle(r)'
        where r is a known quantity.
        Returns numeric value or None if unable to evaluate.
        """
        formula_str = formula_str.strip()

        # Extract function name and arguments
        match = re.match(r'(\w+)\((.*)\)', formula_str)
        if not match:
            return None

        func_name = match.group(1)
        args_str = match.group(2)

        if func_name not in self.FORMULAS:
            return None

        # Parse arguments (could be numbers or quantity names)
        args = [arg.strip() for arg in args_str.split(",")]
        numeric_args = []

        for arg in args:
            # Try to parse as float
            try:
                numeric_args.append(float(arg))
            except ValueError:
                # Try to get from quantities
                if arg in quantities_dict and quantities_dict[arg].value is not None:
                    val = quantities_dict[arg].value
                    if isinstance(val, (int, float)):
                        numeric_args.append(float(val))
                    else:
                        return None
                else:
                    return None

        # Evaluate the formula
        try:
            formula_func = self.FORMULAS[func_name]
            result = formula_func(*numeric_args)
            return float(result)
        except (TypeError, ValueError, ZeroDivisionError):
            return None

    def _solve_for_unknown(self, equation, quantities_dict: Dict[str, Quantity]
                           ) -> Optional[Dict[str, float]]:
        """
        Solve for an unknown when given a constraint.
        Example: solve_for_radius_given_area where area is known.
        """
        lhs = equation.lhs.strip()
        rhs = equation.rhs.strip()

        # Look for "solve_for_X_given_Y" pattern
        if not rhs.startswith("solve_for_"):
            return None

        # Split on "_given_" to separate unknown from constraint
        if "_given_" in rhs:
            parts = rhs.split("_given_")
            unknown_name = parts[0].replace("solve_for_", "")
            constraints_str = parts[1] if len(parts) > 1 else ""
        else:
            # Just "solve_for_X" without constraint
            unknown_name = rhs.replace("solve_for_", "")
            constraints_str = ""

        # Determine what we're solving for based on constraint
        if "area" in rhs.lower():
            return self._solve_inverse_area(unknown_name, rhs, quantities_dict)
        elif "volume" in rhs.lower():
            return self._solve_inverse_volume(unknown_name, rhs, quantities_dict)

        return None

    def _solve_inverse_area(self, unknown: str, formula: str,
                            quantities_dict: Dict[str, Quantity]) -> Optional[Dict[str, float]]:
        """Solve for dimension given area constraint."""
        # Find area constraint value
        constraint_value = None

        # Look for 'area' quantity specifically
        if "area" in quantities_dict:
            q = quantities_dict["area"]
            if q.isKnown and q.value is not None:
                constraint_value = float(q.value)

        if constraint_value is None:
            return None

        # Simple inverse formulas for common cases
        if unknown == "radius":
            # A = πr² → r = √(A/π)
            radius = math.sqrt(constraint_value / math.pi)
            return {"radius": radius}
        elif unknown == "r":
            # A = πr² → r = √(A/π)
            r = math.sqrt(constraint_value / math.pi)
            return {"r": r}

        return None

    def _solve_inverse_volume(self, unknown: str, formula: str,
                              quantities_dict: Dict[str, Quantity]) -> Optional[Dict[str, float]]:
        """Solve for dimension given volume constraint."""
        # Find volume constraint value
        volume_value = None

        # Look for 'volume' quantity specifically
        if "volume" in quantities_dict:
            q = quantities_dict["volume"]
            if q.isKnown and q.value is not None:
                volume_value = float(q.value)

        if volume_value is None:
            return None

        # Simple inverse formulas
        if unknown == "radius" or unknown == "r":
            # V = (4/3)πr³ → r = ∛(3V/4π)
            r = (volume_value * 3 / (4 * math.pi)) ** (1/3)
            return {"radius": r} if unknown == "radius" else {"r": r}
        elif unknown == "height" or unknown == "h":
            # V = πr²h → h = V/(πr²)
            # Need radius value
            r_val = None
            for q_name, q in quantities_dict.items():
                if q_name in ["r", "radius"] and q.isKnown and q.value is not None:
                    r_val = float(q.value)
                    break
            if r_val:
                h = volume_value / (math.pi * r_val**2)
                return {"height": h} if unknown == "height" else {"h": h}

        return None
