"""Sequences and Series solver (mathematics.sequences_series domain)."""
from typing import Union, List, Dict, Any
import numpy as np
import sympy as sp
from sympy import symbols, oo, limit, summation, series, apart, diff, integrate, I, pi, exp, cos, sin
from scipy import special

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _arithmetic_sum(a1: float, d: float, n: int) -> float:
    """Sum of arithmetic sequence: S_n = n/2 * (2*a1 + (n-1)*d).

    Args:
        a1: First term
        d: Common difference
        n: Number of terms

    Returns:
        Sum of n terms
    """
    if n <= 0:
        raise ValueError("Number of terms n must be positive")
    n = int(n)
    return float(n / 2.0 * (2.0 * a1 + (n - 1) * d))


def _geometric_sum(a: float, r: float, n: int) -> float:
    """Sum of geometric sequence: S_n = a * (1 - r^n) / (1 - r) for r != 1.

    Args:
        a: First term
        r: Common ratio
        n: Number of terms

    Returns:
        Sum of n terms
    """
    if n <= 0:
        raise ValueError("Number of terms n must be positive")
    n = int(n)
    if abs(r - 1.0) < 1e-15:
        return float(a * n)
    return float(a * (1.0 - r**n) / (1.0 - r))


def _harmonic_sum(n: int) -> float:
    """Harmonic series partial sum: H_n = 1 + 1/2 + 1/3 + ... + 1/n.

    Args:
        n: Number of terms

    Returns:
        Partial sum H_n
    """
    if n <= 0:
        raise ValueError("Number of terms n must be positive")
    n = int(n)
    return float(sum(1.0 / i for i in range(1, n + 1)))


def _ratio_test(a_n: float, a_n_plus_1: float) -> Dict[str, Any]:
    """Ratio test for series convergence: L = lim |a_{n+1}/a_n|.

    Args:
        a_n: nth term of series
        a_n_plus_1: (n+1)th term of series

    Returns:
        Dictionary with 'limit_ratio' and 'convergence_status' (converges/diverges/inconclusive)
    """
    if abs(a_n) < 1e-15:
        raise ValueError("Denominator a_n is too close to zero")

    L = abs(a_n_plus_1 / a_n)

    if L < 1.0 - 1e-10:
        status = "converges"
    elif L > 1.0 + 1e-10:
        status = "diverges"
    else:
        status = "inconclusive"

    return {
        "limit_ratio": float(L),
        "convergence_status": status
    }


def _root_test(a_n: float, n: int) -> Dict[str, Any]:
    """Root test for series convergence: L = lim |a_n|^(1/n).

    Args:
        a_n: nth term of series
        n: Index n

    Returns:
        Dictionary with 'limit_nth_root' and 'convergence_status'
    """
    if n <= 0:
        raise ValueError("Index n must be positive")
    n = int(n)

    L = abs(a_n) ** (1.0 / n)

    if L < 1.0 - 1e-10:
        status = "converges"
    elif L > 1.0 + 1e-10:
        status = "diverges"
    else:
        status = "inconclusive"

    return {
        "limit_nth_root": float(L),
        "convergence_status": status
    }


def _integral_test(f_expr_str: str, a: int, b: int) -> Dict[str, Any]:
    """Integral test for series convergence.

    Args:
        f_expr_str: String expression for function f(n) (e.g., "1/n", "1/n**2")
        a: Lower bound of integration
        b: Upper bound of integration

    Returns:
        Dictionary with 'integral_value' and 'convergence_status'
    """
    try:
        n = symbols('n', positive=True, real=True)
        f = sp.sympify(f_expr_str)
        integral_val = integrate(f, (n, a, b))

        # Check if integral converges
        if integral_val == oo or integral_val == -oo:
            status = "diverges"
            integral_numeric = float('inf')
        elif integral_val.is_finite:
            status = "converges"
            integral_numeric = float(integral_val)
        else:
            status = "inconclusive"
            integral_numeric = float(integral_val) if integral_val.is_number else float('nan')

        return {
            "integral_value": integral_numeric,
            "convergence_status": status
        }
    except Exception as e:
        raise ValueError(f"Integral test failed: {e}")


def _alternating_series_test(a_n: float, a_n_plus_1: float) -> Dict[str, Any]:
    """Alternating series test: series converges if terms decrease in absolute value.

    Args:
        a_n: nth term (positive)
        a_n_plus_1: (n+1)th term (positive)

    Returns:
        Dictionary with 'term_ratio' and 'convergence_status'
    """
    if a_n < 0 or a_n_plus_1 < 0:
        raise ValueError("Terms should be positive for alternating series test")

    decreasing = a_n_plus_1 < a_n
    # Check if ratio is significantly less than 1 (approaching 0)
    if a_n > 0:
        ratio = a_n_plus_1 / a_n
    else:
        ratio = 0.0

    if decreasing and ratio < 1.0:
        status = "converges"
    elif not decreasing:
        status = "diverges"
    else:
        status = "inconclusive"

    return {
        "term_ratio": float(ratio),
        "convergence_status": status
    }


def _power_series_convergence(x: float, radius: float) -> Dict[str, Any]:
    """Check convergence of power series sum(c_n * x^n) at point x.

    Args:
        x: Point to check convergence
        radius: Radius of convergence

    Returns:
        Dictionary with 'convergence_check' and 'status'
    """
    if radius <= 0:
        raise ValueError("Radius must be positive")

    distance_from_center = abs(x)

    if distance_from_center < radius:
        status = "converges_interior"
    elif distance_from_center > radius:
        status = "diverges_exterior"
    elif distance_from_center == radius:
        status = "boundary_inconclusive"
    else:
        status = "error"

    return {
        "distance_from_center": float(distance_from_center),
        "radius_of_convergence": float(radius),
        "convergence_status": status
    }


def _taylor_series(f_expr_str: str, x_var: str, x0: float, n_terms: int) -> Dict[str, Any]:
    """Taylor series expansion of f(x) around x = x0.

    Args:
        f_expr_str: String expression for f(x) (e.g., "exp(x)", "sin(x)")
        x_var: Variable name (typically 'x')
        x0: Center point
        n_terms: Number of terms to compute

    Returns:
        Dictionary with 'series_expansion' and 'coefficients'
    """
    try:
        if n_terms <= 0:
            raise ValueError("Number of terms must be positive")

        x = symbols(x_var, real=True)
        f = sp.sympify(f_expr_str)

        # Compute Taylor series around x0
        taylor_expansion = series(f, x, x0, n=n_terms)

        # Extract coefficients
        coeffs = taylor_expansion.removeO().as_coefficients_dict()

        coeff_list = []
        for k in range(n_terms):
            power = (x - x0)**k
            coeff = coeffs.get(power, 0)
            coeff_list.append(float(coeff) if coeff.is_number else 0.0)

        return {
            "series_expansion": str(taylor_expansion),
            "coefficients": coeff_list,
            "center": float(x0)
        }
    except Exception as e:
        raise ValueError(f"Taylor series computation failed: {e}")


def _maclaurin_series(f_expr_str: str, x_var: str, n_terms: int) -> Dict[str, Any]:
    """Maclaurin series expansion of f(x) (Taylor series at x = 0).

    Args:
        f_expr_str: String expression for f(x)
        x_var: Variable name
        n_terms: Number of terms

    Returns:
        Dictionary with series expansion and coefficients
    """
    return _taylor_series(f_expr_str, x_var, 0.0, n_terms)


def _fourier_sine_series(f_expr_str: str, L: float, n_terms: int) -> Dict[str, Any]:
    """Fourier sine series coefficients for f(x) on [0, L].

    Args:
        f_expr_str: String expression for f(x) (e.g., "x", "1")
        L: Period/interval length
        n_terms: Number of Fourier coefficients to compute

    Returns:
        Dictionary with 'coefficients' (list of b_n values)
    """
    try:
        if L <= 0:
            raise ValueError("Interval length L must be positive")
        if n_terms <= 0:
            raise ValueError("Number of terms must be positive")

        x = symbols('x', real=True)
        f = sp.sympify(f_expr_str)

        b_coeffs = []
        for n in range(1, n_terms + 1):
            # b_n = (2/L) * integral(f(x) * sin(n*pi*x/L), x, 0, L)
            integrand = f * sp.sin(n * pi * x / L)
            try:
                b_n = integrate(integrand, (x, 0, L))
                b_n = (2.0 / L) * b_n
                b_n_float = float(b_n.evalf()) if b_n.is_number else 0.0
            except Exception:
                b_n_float = 0.0
            b_coeffs.append(b_n_float)

        return {
            "coefficients": b_coeffs,
            "coefficient_type": "sine",
            "period": float(L)
        }
    except Exception as e:
        raise ValueError(f"Fourier sine series failed: {e}")


def _fourier_cosine_series(f_expr_str: str, L: float, n_terms: int) -> Dict[str, Any]:
    """Fourier cosine series coefficients for f(x) on [0, L].

    Args:
        f_expr_str: String expression for f(x)
        L: Period/interval length
        n_terms: Number of Fourier coefficients

    Returns:
        Dictionary with 'a0', 'coefficients' (list of a_n values)
    """
    try:
        if L <= 0:
            raise ValueError("Interval length L must be positive")
        if n_terms <= 0:
            raise ValueError("Number of terms must be positive")

        x = symbols('x', real=True)
        f = sp.sympify(f_expr_str)

        # a_0 = (1/L) * integral(f(x), x, 0, L)
        try:
            a_0 = integrate(f, (x, 0, L))
            a_0 = (1.0 / L) * a_0
            a_0_float = float(a_0.evalf()) if a_0.is_number else 0.0
        except Exception:
            a_0_float = 0.0

        a_coeffs = []
        for n in range(1, n_terms + 1):
            # a_n = (2/L) * integral(f(x) * cos(n*pi*x/L), x, 0, L)
            integrand = f * sp.cos(n * pi * x / L)
            try:
                a_n = integrate(integrand, (x, 0, L))
                a_n = (2.0 / L) * a_n
                a_n_float = float(a_n.evalf()) if a_n.is_number else 0.0
            except Exception:
                a_n_float = 0.0
            a_coeffs.append(a_n_float)

        return {
            "a0": a_0_float,
            "coefficients": a_coeffs,
            "coefficient_type": "cosine",
            "period": float(L)
        }
    except Exception as e:
        raise ValueError(f"Fourier cosine series failed: {e}")


def _fourier_complex_series(f_expr_str: str, L: float, n_terms: int) -> Dict[str, Any]:
    """Complex exponential Fourier series coefficients.

    Args:
        f_expr_str: String expression for f(x)
        L: Half-period
        n_terms: Number of Fourier coefficients

    Returns:
        Dictionary with complex coefficients
    """
    try:
        if L <= 0:
            raise ValueError("Half-period L must be positive")
        if n_terms <= 0:
            raise ValueError("Number of terms must be positive")

        x = symbols('x', real=True)
        f = sp.sympify(f_expr_str)

        coefficients = []
        for n in range(-n_terms, n_terms + 1):
            # c_n = (1/(2*L)) * integral(f(x) * exp(-i*n*pi*x/L), x, -L, L)
            integrand = f * exp(-I * n * pi * x / L)
            try:
                c_n = integrate(integrand, (x, -L, L))
                c_n = c_n / (2.0 * L)
                c_n_val = complex(c_n.evalf())
            except Exception:
                c_n_val = 0.0 + 0.0j

            coefficients.append({
                "n": int(n),
                "coefficient_real": float(c_n_val.real),
                "coefficient_imag": float(c_n_val.imag),
                "magnitude": float(abs(c_n_val))
            })

        return {
            "coefficients": coefficients,
            "coefficient_type": "complex_exponential",
            "half_period": float(L)
        }
    except Exception as e:
        raise ValueError(f"Fourier complex series failed: {e}")


def _generating_function(coefficients: List[float], x: float) -> float:
    """Evaluate generating function G(x) = sum(c_n * x^n).

    Args:
        coefficients: List of coefficients [c_0, c_1, c_2, ...]
        x: Point to evaluate at

    Returns:
        Value of generating function
    """
    try:
        result = sum(c * (x ** n) for n, c in enumerate(coefficients))
        return float(result)
    except Exception as e:
        raise ValueError(f"Generating function evaluation failed: {e}")


def _series_convergence_radius(a_n: float, a_n_plus_1: float) -> Dict[str, Any]:
    """Estimate radius of convergence using ratio test.

    Args:
        a_n: Coefficient a_n
        a_n_plus_1: Coefficient a_{n+1}

    Returns:
        Dictionary with 'radius_of_convergence' and 'interval_endpoints'
    """
    if abs(a_n) < 1e-15:
        raise ValueError("Coefficient a_n is too close to zero")

    ratio = abs(a_n_plus_1 / a_n)

    if ratio < 1e-15:
        R = float('inf')
    else:
        R = 1.0 / ratio

    return {
        "radius_of_convergence": R,
        "interval_endpoints": [-R, R] if R != float('inf') else None
    }


def _nth_term(a1: float, d_or_r: float, n: int, series_type: str = "arithmetic") -> float:
    """Nth term of arithmetic or geometric sequence.

    Args:
        a1: First term
        d_or_r: Common difference (arithmetic) or ratio (geometric)
        n: Index n
        series_type: "arithmetic" or "geometric"

    Returns:
        The nth term
    """
    if n <= 0:
        raise ValueError("Index n must be positive")
    n = int(n)

    if series_type.lower() == "arithmetic":
        # a_n = a_1 + (n-1)*d
        return float(a1 + (n - 1) * d_or_r)
    elif series_type.lower() == "geometric":
        # a_n = a_1 * r^(n-1)
        return float(a1 * (d_or_r ** (n - 1)))
    else:
        raise ValueError(f"Unknown series type: {series_type}")


_OPERATIONS = {
    "arithmetic_sum": _arithmetic_sum,
    "geometric_sum": _geometric_sum,
    "harmonic_sum": _harmonic_sum,
    "ratio_test": _ratio_test,
    "root_test": _root_test,
    "integral_test": _integral_test,
    "alternating_series_test": _alternating_series_test,
    "power_series_convergence": _power_series_convergence,
    "taylor_series": _taylor_series,
    "maclaurin_series": _maclaurin_series,
    "fourier_sine_series": _fourier_sine_series,
    "fourier_cosine_series": _fourier_cosine_series,
    "fourier_complex_series": _fourier_complex_series,
    "generating_function": _generating_function,
    "series_convergence_radius": _series_convergence_radius,
    "nth_term": _nth_term,
}


@register("mathematics.sequences_series")
class SequencesSeriesSolver(SolverBase):
    """
    Specialized solver for sequences and series: convergence tests, power series,
    Taylor/Fourier expansions, generating functions.

    Supports operations for arithmetic/geometric/harmonic sums, convergence tests
    (ratio, root, integral, alternating), and Fourier analysis.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve sequences and series problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            import re
            quantities = {q.name: q for q in model.quantities}
            summary = {}

            for equation in model.equations:
                func_name, arg_strs = self._parse_call(equation.rhs)

                if func_name not in _OPERATIONS:
                    raise ValueError(f"Unknown operation: {func_name}")

                # Special handling for operations that need string expressions
                if func_name in ["taylor_series", "maclaurin_series", "fourier_sine_series",
                                 "fourier_cosine_series", "fourier_complex_series", "integral_test",
                                 "nth_term"]:
                    args = self._resolve_args_special(arg_strs, quantities)
                else:
                    # Standard numeric resolution
                    from app.solvers.utils import resolve_arg
                    args = [resolve_arg(a, quantities) for a in arg_strs]

                result = _OPERATIONS[func_name](*args)
                key = equation.lhs.strip() or func_name

                if isinstance(result, dict):
                    summary.update({f"{key}_{k}": v for k, v in result.items()})
                else:
                    summary[key] = result

            return SolverResult(
                success=True,
                message="Sequences and series solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _parse_call(self, expr: str):
        """Parse function call and return (func_name, [args])."""
        import re
        match = re.fullmatch(r'([A-Za-z_]\w*)\((.*)\)', expr.strip())
        if not match:
            raise ValueError(f"Invalid operation format: {expr}")
        func_name = match.group(1)
        args_str = match.group(2).strip()
        if not args_str:
            return func_name, []
        arg_list = [arg.strip() for arg in self._split_args(args_str)]
        return func_name, arg_list

    def _split_args(self, s: str):
        """Split arguments by comma, respecting parentheses."""
        parts = []
        current = []
        depth = 0
        for char in s:
            if char in '([':
                depth += 1
                current.append(char)
            elif char in ')]':
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

    def _resolve_args_special(self, arg_strs, quantities):
        """Resolve arguments allowing strings for expressions and keywords."""
        result = []
        for arg in arg_strs:
            # Check if it's a known keyword
            if arg.lower() in ["arithmetic", "geometric", "sine", "cosine"]:
                result.append(arg.lower())
            else:
                # Try to resolve as number or quantity first
                try:
                    result.append(float(arg))
                except ValueError:
                    # Try quantity
                    if arg in quantities:
                        result.append(quantities[arg].value)
                    else:
                        # Treat as expression string
                        result.append(arg)
        return result
