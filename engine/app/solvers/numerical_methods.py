"""Numerical methods solver (mathematics.numerical_methods domain)."""
from typing import Dict, List, Tuple, Callable, Any, Union
import numpy as np
import sympy as sp
from scipy.optimize import brentq
from scipy.interpolate import lagrange, CubicSpline
from scipy.integrate import quad, solve_ivp
from app.model import ScientificModel, SolverResult, Quantity, Equation, EquationType
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import get_value, get_vector, parse_call, resolve_arg


def _expr_to_lambda(expr: Union[str, sp.Expr], var_name: str = 'x') -> Callable:
    """Convert string expression or SymPy expr to callable lambda."""
    if isinstance(expr, str):
        try:
            sym = sp.Symbol(var_name)
            expr = sp.sympify(expr)
            return sp.lambdify(sym, expr, 'numpy')
        except Exception as e:
            raise ValueError(f"Could not parse expression '{expr}': {e}")
    elif isinstance(expr, sp.Expr):
        sym = sp.Symbol(var_name)
        return sp.lambdify(sym, expr, 'numpy')
    elif callable(expr):
        return expr
    else:
        raise ValueError(f"Expression must be string, SymPy expr, or callable")


def _newton_raphson(f_expr: Union[str, sp.Expr], df_expr: Union[str, sp.Expr],
                    x0: float, max_iter: int = 100, tolerance: float = 1e-6) -> float:
    """Newton-Raphson root-finding: solves f(x) = 0."""
    max_iter = int(max_iter)
    if max_iter <= 0:
        raise ValueError("max_iter must be greater than 0")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    f_lambda = _expr_to_lambda(f_expr, 'x')
    df_lambda = _expr_to_lambda(df_expr, 'x')

    x = float(x0)
    for i in range(int(max_iter)):
        f_val = float(f_lambda(x))
        df_val = float(df_lambda(x))

        if abs(df_val) < 1e-14:
            raise ValueError("Derivative too close to zero")

        x_new = x - f_val / df_val
        if abs(x_new - x) < tolerance:
            return float(x_new)
        x = x_new

    raise ValueError(f"Newton-Raphson did not converge after {max_iter} iterations")


def _bisection_method(f_expr: Union[str, sp.Expr], a: float, b: float,
                      max_iter: int = 100, tolerance: float = 1e-6) -> float:
    """Bisection method for root-finding in interval [a, b]."""
    max_iter = int(max_iter)
    if max_iter <= 0:
        raise ValueError("max_iter must be greater than 0")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if a >= b:
        raise ValueError("Interval [a, b] must have a < b")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    f_a = float(f_lambda(a))
    f_b = float(f_lambda(b))

    if f_a * f_b > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")

    for _ in range(int(max_iter)):
        c = (a + b) / 2.0
        f_c = float(f_lambda(c))

        if abs(f_c) < tolerance or (b - a) / 2.0 < tolerance:
            return float(c)

        if f_a * f_c < 0:
            b, f_b = c, f_c
        else:
            a, f_a = c, f_c

    return float((a + b) / 2.0)


def _secant_method(f_expr: Union[str, sp.Expr], x0: float, x1: float,
                   max_iter: int = 100, tolerance: float = 1e-6) -> float:
    """Secant method for root-finding."""
    max_iter = int(max_iter)
    if max_iter <= 0:
        raise ValueError("max_iter must be greater than 0")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    for _ in range(int(max_iter)):
        f_x0 = float(f_lambda(x0))
        f_x1 = float(f_lambda(x1))

        if abs(f_x1 - f_x0) < 1e-14:
            raise ValueError("Denominator too small")

        x2 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)

        if abs(x2 - x1) < tolerance:
            return float(x2)

        x0, x1 = x1, x2

    return float(x1)


def _brent_method(f_expr: Union[str, sp.Expr], a: float, b: float,
                  tolerance: float = 1e-6) -> float:
    """Brent's method for robust root-finding."""
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if a >= b:
        raise ValueError("Interval [a, b] must have a < b")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    return float(brentq(f_lambda, a, b, xtol=tolerance))


def _lagrange_interpolation(x_data: List[float], y_data: List[float], x: float) -> float:
    """Lagrange polynomial interpolation."""
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have same length")
    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points")

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    poly = lagrange(x_data, y_data)
    return float(poly(x))


def _newton_interpolation(x_data: List[float], y_data: List[float], x: float) -> float:
    """Newton divided difference polynomial interpolation."""
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have same length")
    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points")

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    coeffs = np.polyfit(x_data, y_data, len(x_data) - 1)
    poly = np.poly1d(coeffs)
    return float(poly(x))


def _cubic_spline(x_data: List[float], y_data: List[float], x: float) -> float:
    """Cubic spline interpolation."""
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have same length")
    if len(x_data) < 2:
        raise ValueError("Need at least 2 data points")

    x_data = np.asarray(x_data, dtype=float)
    y_data = np.asarray(y_data, dtype=float)

    spline = CubicSpline(x_data, y_data)
    return float(spline(x))


def _finite_difference_1st_order(f_expr: Union[str, sp.Expr], x: float,
                                 h: float = 1e-5) -> float:
    """First-order finite difference approximation of f'(x)."""
    if h <= 0:
        raise ValueError("Step size h must be positive")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    f_x = float(f_lambda(x))
    f_xh = float(f_lambda(x + h))
    return (f_xh - f_x) / h


def _finite_difference_2nd_order(f_expr: Union[str, sp.Expr], x: float,
                                 h: float = 1e-5) -> float:
    """Second-order finite difference approximation of f''(x)."""
    if h <= 0:
        raise ValueError("Step size h must be positive")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    f_xh_plus = float(f_lambda(x + h))
    f_x = float(f_lambda(x))
    f_xh_minus = float(f_lambda(x - h))
    return (f_xh_plus - 2.0 * f_x + f_xh_minus) / (h * h)


def _richardson_extrapolation(f_expr: Union[str, sp.Expr], x: float, order: int = 2,
                              h_init: float = 1e-3, n_steps: int = 5) -> float:
    """Richardson extrapolation for improved numerical derivative."""
    order = int(order)
    if order <= 0:
        raise ValueError("order must be positive")
    n_steps = int(n_steps)
    if n_steps <= 0:
        raise ValueError("n_steps must be positive")
    if h_init <= 0:
        raise ValueError("h_init must be positive")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    estimates = []
    for i in range(int(n_steps)):
        h = h_init / (2.0 ** i)
        f_xh = float(f_lambda(x + h))
        f_x = float(f_lambda(x))
        deriv = (f_xh - f_x) / h
        estimates.append(deriv)

    # Richardson extrapolation: combine last two estimates
    if len(estimates) >= 2:
        return float(2.0 * estimates[-1] - estimates[-2])
    return float(estimates[0])


def _trapezoidal_integration(f_expr: Union[str, sp.Expr], a: float, b: float,
                             n: int = 100) -> float:
    """Trapezoidal rule for numerical integration."""
    n = int(n)
    if n <= 0:
        raise ValueError("Number of intervals n must be positive")
    if a >= b:
        raise ValueError("Interval [a, b] must have a < b")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    h = (b - a) / float(n)
    result = 0.0

    for i in range(int(n) + 1):
        x = a + i * h
        f_val = float(f_lambda(x))

        if i == 0 or i == n:
            result += f_val / 2.0
        else:
            result += f_val

    result *= h
    return float(result)


def _simpsons_rule(f_expr: Union[str, sp.Expr], a: float, b: float, n: int = 100) -> float:
    """Simpson's rule for numerical integration."""
    n = int(n)
    if n <= 0:
        raise ValueError("Number of intervals n must be positive")
    if n % 2 != 0:
        n += 1  # Make even
    if a >= b:
        raise ValueError("Interval [a, b] must have a < b")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    h = (b - a) / float(n)
    result = 0.0

    for i in range(int(n) + 1):
        x = a + i * h
        f_val = float(f_lambda(x))

        if i == 0 or i == n:
            result += f_val
        elif i % 2 == 1:
            result += 4.0 * f_val
        else:
            result += 2.0 * f_val

    result *= h / 3.0
    return float(result)


def _gauss_legendre_integration(f_expr: Union[str, sp.Expr], a: float, b: float,
                                n: int = 10) -> float:
    """Gaussian quadrature (Gauss-Legendre) for numerical integration."""
    n = int(n)
    if n <= 0:
        raise ValueError("Number of points n must be positive")
    if a >= b:
        raise ValueError("Interval [a, b] must have a < b")

    f_lambda = _expr_to_lambda(f_expr, 'x')

    result, _ = quad(f_lambda, a, b, limit=n)
    return float(result)


def _rk45_step(f_expr: Union[str, sp.Expr], y: float, t: float, dt: float) -> Tuple[float, float]:
    """One step of RK45 ODE solver for dy/dt = f(t, y)."""
    if dt <= 0:
        raise ValueError("Step size dt must be positive")

    if isinstance(f_expr, str):
        f_expr = sp.sympify(f_expr)

    if isinstance(f_expr, sp.Expr):
        t_sym, y_sym = sp.symbols('t y')
        f_lambda = sp.lambdify((t_sym, y_sym), f_expr, 'numpy')
    else:
        f_lambda = f_expr

    sol = solve_ivp(lambda t, y: f_lambda(t, y), [t, t + dt], [y], method='RK45', max_step=dt)

    if sol.status != 0:
        raise ValueError("RK45 solver failed")

    t_new = float(sol.t[-1])
    y_new = float(sol.y[0, -1])
    return (t_new, y_new)


def _bdf_step(f_expr: Union[str, sp.Expr], y: float, t: float, dt: float) -> Tuple[float, float]:
    """One step of BDF ODE solver for stiff systems."""
    if dt <= 0:
        raise ValueError("Step size dt must be positive")

    if isinstance(f_expr, str):
        f_expr = sp.sympify(f_expr)

    if isinstance(f_expr, sp.Expr):
        t_sym, y_sym = sp.symbols('t y')
        f_lambda = sp.lambdify((t_sym, y_sym), f_expr, 'numpy')
    else:
        f_lambda = f_expr

    sol = solve_ivp(lambda t, y: f_lambda(t, y), [t, t + dt], [y], method='BDF', max_step=dt)

    if sol.status != 0:
        raise ValueError("BDF solver failed")

    t_new = float(sol.t[-1])
    y_new = float(sol.y[0, -1])
    return (t_new, y_new)


def _ode_adaptive_step(f_expr: Union[str, sp.Expr], y: float, t: float, dt: float,
                       tolerance: float = 1e-6) -> Tuple[float, float, float]:
    """Adaptive step control for ODE solver."""
    if dt <= 0:
        raise ValueError("Step size dt must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")

    if isinstance(f_expr, str):
        f_expr = sp.sympify(f_expr)

    if isinstance(f_expr, sp.Expr):
        t_sym, y_sym = sp.symbols('t y')
        f_lambda = sp.lambdify((t_sym, y_sym), f_expr, 'numpy')
    else:
        f_lambda = f_expr

    try:
        sol = solve_ivp(lambda t, y: f_lambda(t, y), [t, t + dt], [y], method='RK45',
                       dense_output=True, max_step=dt)

        if sol.status != 0:
            dt_new = dt / 2.0
            return (t, y, dt_new)

        t_new = float(sol.t[-1])
        y_new = float(sol.y[0, -1])
        dt_new = min(dt * 1.2, dt * 2.0)

        return (t_new, y_new, dt_new)
    except Exception:
        return (t, y, dt / 2.0)


def _solve_stiff_system(f_expr_list: List[Union[str, sp.Expr]], y_init: List[float],
                        t_span: List[float], n_points: int = 100) -> List[List[float]]:
    """Solve a system of stiff ODEs using BDF method."""
    if len(f_expr_list) == 0:
        raise ValueError("At least one equation required")
    if len(y_init) != len(f_expr_list):
        raise ValueError("Number of initial conditions must match number of equations")
    if len(t_span) != 2:
        raise ValueError("t_span must have [t_start, t_end]")
    if t_span[0] >= t_span[1]:
        raise ValueError("t_end must be greater than t_start")
    n_points = int(n_points)
    if n_points <= 1:
        raise ValueError("n_points must be > 1")

    y_init = np.asarray(y_init, dtype=float)
    t_eval = np.linspace(t_span[0], t_span[1], n_points)

    # Convert expressions to lambdas
    lambdas = []
    for f_expr in f_expr_list:
        if isinstance(f_expr, str):
            f_expr = sp.sympify(f_expr)

        if isinstance(f_expr, sp.Expr):
            t_sym = sp.Symbol('t')
            y_syms = [sp.Symbol(f'y{j}') for j in range(len(f_expr_list))]
            f_lambda = sp.lambdify((t_sym,) + tuple(y_syms), f_expr, 'numpy')
            lambdas.append(f_lambda)
        else:
            lambdas.append(f_expr)

    def system(t, y):
        result = []
        for f_lambda in lambdas:
            val = float(f_lambda(t, *y))
            result.append(val)
        return np.array(result)

    sol = solve_ivp(system, t_span, y_init, method='BDF', t_eval=t_eval)

    if sol.status != 0:
        raise ValueError("BDF solver failed to solve system")

    return sol.y.T.tolist()


_OPERATIONS = {
    "newton_raphson": _newton_raphson,
    "bisection_method": _bisection_method,
    "secant_method": _secant_method,
    "brent_method": _brent_method,
    "lagrange_interpolation": _lagrange_interpolation,
    "newton_interpolation": _newton_interpolation,
    "cubic_spline": _cubic_spline,
    "finite_difference_1st_order": _finite_difference_1st_order,
    "finite_difference_2nd_order": _finite_difference_2nd_order,
    "richardson_extrapolation": _richardson_extrapolation,
    "trapezoidal_integration": _trapezoidal_integration,
    "simpsons_rule": _simpsons_rule,
    "gauss_legendre_integration": _gauss_legendre_integration,
    "rk45_step": _rk45_step,
    "bdf_step": _bdf_step,
    "ode_adaptive_step": _ode_adaptive_step,
    "solve_stiff_system": _solve_stiff_system,
}


@register("mathematics.numerical_methods")
class NumericalMethodsSolver(SolverBase):
    """
    Specialized solver for numerical methods: root-finding, interpolation,
    numerical differentiation/integration, ODE solving.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve numerical methods problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = {}

            for eq in model.equations:
                # Parse equation: lhs = operation(args...)
                func_name, arg_strs = parse_call(eq.rhs)

                if func_name not in _OPERATIONS:
                    raise ValueError(f"Unknown operation: {func_name}")

                # Resolve arguments
                args = []
                for arg_str in arg_strs:
                    # Try to resolve as a quantity or literal
                    try:
                        val = resolve_arg(arg_str, quantities)
                        args.append(val)
                    except ValueError:
                        # If not a quantity, treat as an expression string
                        # (for symbolic operations like root-finding)
                        args.append(arg_str)

                # Call the operation
                result = _OPERATIONS[func_name](*args)

                # Store result
                if eq.lhs:
                    summary[eq.lhs] = result
                else:
                    summary[func_name] = result

            return SolverResult(
                success=True,
                message="Numerical methods solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
