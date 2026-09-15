"""Number theory solver (mathematics.number_theory domain)."""
import re
from typing import Dict, Any, List, Union
from sympy import gcd as sp_gcd
from sympy import lcm as sp_lcm
from sympy.ntheory import factorint, isprime
from sympy import factorial, Rational
from math import comb, perm

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.number_theory")
class NumberTheorySolver(SolverBase):
    """
    Solver for number theory operations: GCD, LCM, prime factorization,
    primality testing, modular exponentiation, permutations, combinations.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve number theory operations.
        Equations expected to contain operation names like:
          "gcd(a, b)", "lcm(a, b)", "prime_factors(n)", "is_prime(n)",
          "mod_exp(base, exp, mod)", "nPr(n, r)", "nCr(n, r)"
        """
        try:
            # Extract quantities and initial conditions
            quantities = {q.name: q for q in model.quantities}
            ic = model.initialConditions or {}

            # Process equations and compute results
            results = {}
            for equation in model.equations:
                # The equation name is typically in the lhs, operation formula in rhs
                operation_name = equation.lhs.strip()
                operation_result = self._evaluate_operation(
                    operation_name, quantities, ic
                )
                results[operation_name] = operation_result

            # Create summary with results
            summary = self._build_summary(results)

            return SolverResult(
                success=True,
                message="Number theory operations computed successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _evaluate_operation(
        self,
        operation_name: str,
        quantities: Dict[str, Quantity],
        ic: Dict[str, float]
    ) -> Union[int, List[int], bool, float]:
        """
        Evaluate a number theory operation given its name and operands.
        Operands come from quantities or initial conditions.
        """
        operation_name = operation_name.strip()

        # Parse operation name and extract operands
        match = re.match(r"(\w+)\((.*)\)", operation_name)
        if not match:
            raise ValueError(f"Invalid operation format: {operation_name}")

        op_type = match.group(1).lower()
        args_str = match.group(2)
        args = [arg.strip() for arg in args_str.split(",")]

        # Convert argument names to values
        args_values = []
        for arg in args:
            val = self._get_numeric_value(arg, quantities, ic)
            args_values.append(int(val) if arg not in ic and "." not in str(val) else val)

        # Dispatch to appropriate operation
        if op_type == "gcd":
            if len(args_values) != 2:
                raise ValueError(f"gcd requires 2 arguments, got {len(args_values)}")
            return int(sp_gcd(int(args_values[0]), int(args_values[1])))

        elif op_type == "lcm":
            if len(args_values) != 2:
                raise ValueError(f"lcm requires 2 arguments, got {len(args_values)}")
            return int(sp_lcm(int(args_values[0]), int(args_values[1])))

        elif op_type == "prime_factors" or op_type == "prime_factorization":
            if len(args_values) != 1:
                raise ValueError(f"prime_factors requires 1 argument, got {len(args_values)}")
            n = int(args_values[0])
            if n < 2:
                raise ValueError("prime_factors requires n >= 2")
            factor_dict = factorint(n)
            # Return factors as a sorted list (expanded, e.g., [2, 3, 5] for 30)
            factors = []
            for prime, exp in sorted(factor_dict.items()):
                factors.extend([prime] * exp)
            return factors

        elif op_type == "is_prime":
            if len(args_values) != 1:
                raise ValueError(f"is_prime requires 1 argument, got {len(args_values)}")
            n = int(args_values[0])
            return bool(isprime(n))

        elif op_type == "mod_exp" or op_type == "modular_exponentiation":
            if len(args_values) != 3:
                raise ValueError(f"mod_exp requires 3 arguments, got {len(args_values)}")
            base, exp, mod = int(args_values[0]), int(args_values[1]), int(args_values[2])
            return int(pow(base, exp, mod))

        elif op_type == "nper" or op_type == "npr":
            if len(args_values) != 2:
                raise ValueError(f"nPr requires 2 arguments, got {len(args_values)}")
            n, r = int(args_values[0]), int(args_values[1])
            return int(perm(n, r))

        elif op_type == "ncr" or op_type == "comb":
            if len(args_values) != 2:
                raise ValueError(f"nCr requires 2 arguments, got {len(args_values)}")
            n, r = int(args_values[0]), int(args_values[1])
            return int(comb(n, r))

        else:
            raise ValueError(f"Unknown operation: {op_type}")

    def _get_numeric_value(
        self,
        name: str,
        quantities: Dict[str, Quantity],
        ic: Dict[str, float]
    ) -> float:
        """Get a numeric value from initial conditions or quantity definition."""
        # Try initial conditions first
        if name in ic:
            val = ic[name]
            if isinstance(val, (int, float)):
                return float(val)
            else:
                raise ValueError(f"Expected numeric value for {name}, got {type(val)}")

        # Try quantities
        if name in quantities and quantities[name].value is not None:
            val = quantities[name].value
            if isinstance(val, (int, float)):
                return float(val)
            else:
                raise ValueError(f"Expected numeric value for {name}, got {type(val)}")

        # Try parsing as literal integer
        try:
            return float(int(name))
        except ValueError:
            pass

        raise ValueError(f"No value found for operand: {name}")

    def _build_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Build summary dictionary from operation results."""
        summary = {}
        for op_name, result in results.items():
            # Use operation name as key in summary
            summary[op_name] = result
        return summary
