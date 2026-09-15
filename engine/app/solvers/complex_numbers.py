"""Complex number operations solver (mathematics.complex_numbers domain)."""
from typing import Dict, Union, List
import numpy as np
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.complex_numbers")
class ComplexNumbersSolver(SolverBase):
    """
    Solver for complex number operations including arithmetic, modulus,
    argument (phase), polar/rectangular conversion, and roots.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve complex number operations.

        Supported operations (via equation.rhs):
          - "add(z1, z2)", "subtract(z1, z2)", "multiply(z1, z2)", "divide(z1, z2)"
          - "modulus(z)" or "magnitude(z)"
          - "argument(z)" or "phase(z)"
          - "polar_to_rect(r, theta)"
          - "rect_to_polar(z)" or "to_polar(z)"
          - "nth_root(z, n)"
          - "power(z, n)"
        """
        try:
            # Parse quantities into a dict
            quantities = {q.name: q for q in model.quantities}
            ic = model.initialConditions or {}

            # Get the operation (first equation's RHS)
            if not model.equations:
                return SolverResult(
                    success=False,
                    message="No equations provided",
                    error="At least one equation is required"
                )

            operation = model.equations[0].rhs.strip()
            summary = {}

            # Route to appropriate operation handler
            if operation.startswith("add("):
                result = self._handle_add(operation, quantities, ic)
            elif operation.startswith("subtract(") or operation.startswith("sub("):
                result = self._handle_subtract(operation, quantities, ic)
            elif operation.startswith("multiply(") or operation.startswith("mul("):
                result = self._handle_multiply(operation, quantities, ic)
            elif operation.startswith("divide(") or operation.startswith("div("):
                result = self._handle_divide(operation, quantities, ic)
            elif operation.startswith("modulus(") or operation.startswith("magnitude("):
                result = self._handle_modulus(operation, quantities, ic)
            elif operation.startswith("argument(") or operation.startswith("phase("):
                result = self._handle_argument(operation, quantities, ic)
            elif operation.startswith("polar_to_rect("):
                result = self._handle_polar_to_rect(operation, quantities, ic)
            elif operation.startswith("rect_to_polar(") or operation.startswith("to_polar("):
                result = self._handle_rect_to_polar(operation, quantities, ic)
            elif operation.startswith("nth_root("):
                result = self._handle_nth_root(operation, quantities, ic)
            elif operation.startswith("power("):
                result = self._handle_power(operation, quantities, ic)
            else:
                return SolverResult(
                    success=False,
                    message=f"Unknown operation: {operation}",
                    error="Operation not supported"
                )

            summary["operation"] = operation
            if isinstance(result, tuple):
                summary.update(result[1])
                return SolverResult(success=True, message="Complex operation solved successfully", summary=summary)
            else:
                summary.update(result)
                return SolverResult(success=True, message="Complex operation solved successfully", summary=summary)

        except Exception as e:
            return SolverResult(
                success=False,
                message="Complex solver error",
                error=str(e)
            )

    def _get_complex_value(self, quantities: Dict[str, Quantity],
                           name: str, ic: Dict[str, Union[float, Dict]]) -> complex:
        """
        Extract a complex number from quantities or initial conditions.
        Complex can be represented as:
          - A dict {"real": a, "imag": b}
          - A scalar (treated as real part)
        """
        if name in ic:
            val = ic[name]
            if isinstance(val, dict) and "real" in val and "imag" in val:
                return complex(val["real"], val["imag"])
            elif isinstance(val, (int, float)):
                return complex(val, 0.0)
            else:
                raise ValueError(f"Cannot parse complex value for {name}: {val}")

        if name in quantities:
            q = quantities[name]
            if q.value is not None:
                if isinstance(q.value, dict) and "real" in q.value and "imag" in q.value:
                    return complex(q.value["real"], q.value["imag"])
                elif isinstance(q.value, (int, float)):
                    return complex(q.value, 0.0)
                else:
                    raise ValueError(f"Invalid value for {name}: {q.value}")

        raise ValueError(f"No value found for quantity: {name}")

    def _get_scalar_value(self, quantities: Dict[str, Quantity],
                         name: str, ic: Dict[str, Union[float, Dict]]) -> float:
        """Extract a scalar value (for n in nth_root, angle in polar, etc.)"""
        if name in ic:
            val = ic[name]
            if isinstance(val, (int, float)):
                return float(val)
            else:
                raise ValueError(f"Expected scalar for {name}, got {val}")

        if name in quantities:
            q = quantities[name]
            if q.value is not None and isinstance(q.value, (int, float)):
                return float(q.value)

        raise ValueError(f"No scalar value found for {name}")

    def _complex_to_dict(self, z: complex) -> Dict[str, float]:
        """Convert complex to JSON-serializable dict."""
        return {"real": float(z.real), "imag": float(z.imag)}

    def _handle_add(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: add(z1, z2)"""
        parts = self._extract_args(op, 2)
        z1 = self._get_complex_value(quantities, parts[0], ic)
        z2 = self._get_complex_value(quantities, parts[1], ic)
        result = z1 + z2
        return {"result": self._complex_to_dict(result)}

    def _handle_subtract(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: subtract(z1, z2) or sub(z1, z2)"""
        parts = self._extract_args(op, 2)
        z1 = self._get_complex_value(quantities, parts[0], ic)
        z2 = self._get_complex_value(quantities, parts[1], ic)
        result = z1 - z2
        return {"result": self._complex_to_dict(result)}

    def _handle_multiply(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: multiply(z1, z2) or mul(z1, z2)"""
        parts = self._extract_args(op, 2)
        z1 = self._get_complex_value(quantities, parts[0], ic)
        z2 = self._get_complex_value(quantities, parts[1], ic)
        result = z1 * z2
        return {"result": self._complex_to_dict(result)}

    def _handle_divide(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: divide(z1, z2) or div(z1, z2)"""
        parts = self._extract_args(op, 2)
        z1 = self._get_complex_value(quantities, parts[0], ic)
        z2 = self._get_complex_value(quantities, parts[1], ic)
        if abs(z2) < 1e-15:
            raise ValueError("Division by zero")
        result = z1 / z2
        return {"result": self._complex_to_dict(result)}

    def _handle_modulus(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: modulus(z) or magnitude(z)"""
        parts = self._extract_args(op, 1)
        z = self._get_complex_value(quantities, parts[0], ic)
        result = abs(z)
        return {"modulus": float(result)}

    def _handle_argument(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: argument(z) or phase(z) - returns angle in radians"""
        parts = self._extract_args(op, 1)
        z = self._get_complex_value(quantities, parts[0], ic)
        result = np.angle(z)  # Returns angle in [-π, π]
        return {"argument": float(result)}

    def _handle_polar_to_rect(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: polar_to_rect(r, theta) - theta in radians"""
        parts = self._extract_args(op, 2)
        r = self._get_scalar_value(quantities, parts[0], ic)
        theta = self._get_scalar_value(quantities, parts[1], ic)
        result = r * np.exp(1j * theta)
        return {"result": self._complex_to_dict(result)}

    def _handle_rect_to_polar(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: rect_to_polar(z) or to_polar(z)"""
        parts = self._extract_args(op, 1)
        z = self._get_complex_value(quantities, parts[0], ic)
        r = abs(z)
        theta = np.angle(z)
        return {"modulus": float(r), "argument": float(theta)}

    def _handle_nth_root(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: nth_root(z, n) - returns all n roots"""
        parts = self._extract_args(op, 2)
        z = self._get_complex_value(quantities, parts[0], ic)
        n = int(self._get_scalar_value(quantities, parts[1], ic))

        if n <= 0:
            raise ValueError("n must be a positive integer")

        # Compute all n-th roots using polar form
        r = abs(z)
        theta = np.angle(z)

        roots = []
        for k in range(n):
            root_r = r ** (1.0 / n)
            root_theta = (theta + 2 * np.pi * k) / n
            root = root_r * np.exp(1j * root_theta)
            roots.append(self._complex_to_dict(root))

        return {"roots": roots, "count": n}

    def _handle_power(self, op: str, quantities: Dict, ic: Dict) -> Dict:
        """Handle: power(z, n) - raises z to power n"""
        parts = self._extract_args(op, 2)
        z = self._get_complex_value(quantities, parts[0], ic)
        n = self._get_scalar_value(quantities, parts[1], ic)
        result = z ** n
        return {"result": self._complex_to_dict(result)}

    def _extract_args(self, op: str, expected_count: int) -> List[str]:
        """Extract argument names from operation string like 'add(z1, z2)'"""
        # Find content between parentheses
        start = op.find("(")
        end = op.rfind(")")
        if start == -1 or end == -1:
            raise ValueError(f"Malformed operation: {op}")

        args_str = op[start + 1:end].strip()
        args = [arg.strip() for arg in args_str.split(",")]

        if len(args) != expected_count:
            raise ValueError(f"Expected {expected_count} arguments, got {len(args)}")

        return args
