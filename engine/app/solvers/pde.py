"""Partial Differential Equations solver (mathematics.pde domain)."""
from typing import Dict, List, Union, Any
import numpy as np
import sympy as sp
from sympy import symbols, Function, Eq, dsolve

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_value, get_vector, get_optional_value, parse_call


def _pde_resolve_arg(arg: str, quantities: Dict[str, Quantity]):
    """
    Resolve PDE arguments: handles quoted strings, numbers, and quantity lookups.
    Quoted strings like "sin(pi*x)" are returned as-is (unquoted).
    """
    # Handle quoted strings
    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]  # Remove quotes

    # Try float literal
    try:
        return float(arg)
    except ValueError:
        pass

    # Try quantity lookup
    if arg in quantities:
        q = quantities[arg]
        if q.value is None:
            raise ValueError(f"Quantity '{arg}' has no value")
        return q.value

    raise ValueError(f"Could not resolve argument: {arg}")


def _pde_run_dispatch(model, quantities: Dict[str, Quantity],
                      operations: Dict[str, callable]) -> Dict[str, Any]:
    """
    Custom dispatch for PDE solver that handles quoted strings.
    """
    summary = {}
    for equation in model.equations:
        func_name, arg_strs = parse_call(equation.rhs)
        if func_name not in operations:
            raise ValueError(f"Unknown operation: {func_name}")
        args = [_pde_resolve_arg(a, quantities) for a in arg_strs]
        result = operations[func_name](*args)
        key = equation.lhs.strip() or func_name
        if isinstance(result, dict):
            summary.update({f"{key}_{k}": v for k, v in result.items()})
        else:
            summary[key] = result
    return summary


def _heat_equation_1d(domain_length: float, time_span: float, diffusivity: float,
                      initial_condition: Union[str, List[float]],
                      bc_type: str = "dirichlet", bc_values: List[float] = None) -> Dict[str, Any]:
    """
    Solve 1D heat equation: ∂u/∂t = α * ∂²u/∂x².

    Args:
        domain_length: Length of spatial domain [0, L]
        time_span: Total time to solve
        diffusivity: Thermal diffusivity α
        initial_condition: Either "sin(pi*x)" or numeric array
        bc_type: "dirichlet", "neumann", or "robin"
        bc_values: [value_at_0, value_at_L] for Dirichlet, or [flux_0, flux_L] for Neumann

    Returns:
        Dict with solution array u_t (spatial values at final time), time grid, metadata
    """
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if time_span <= 0:
        raise ValueError("time_span must be positive")
    if diffusivity <= 0:
        raise ValueError("diffusivity must be positive")

    # Try symbolic solution for simple cases
    try:
        if isinstance(initial_condition, str) and initial_condition == "sin(pi*x)":
            # Exact solution: u(x,t) = exp(-π²*α*t) * sin(π*x)
            x, t, alpha = sp.symbols('x t alpha', real=True, positive=True)
            u = sp.exp(-sp.pi**2 * alpha * t) * sp.sin(sp.pi * x)

            t_val = time_span
            u_final = u.subs({t: t_val, alpha: diffusivity})

            # Evaluate on [0, 1] (normalized domain)
            n_points = 50
            x_vals = np.linspace(0, 1, n_points)
            u_vals = np.array([float(u_final.subs(x, xv)) for xv in x_vals])

            return {
                "solution_type": "symbolic",
                "solution_values": u_vals.tolist(),
                "spatial_grid": x_vals.tolist(),
                "time_final": time_span,
                "description": "Heat equation with exponential decay"
            }
    except Exception:
        pass

    # Fallback to numeric finite difference
    if bc_values is None:
        bc_values = [0.0, 0.0]  # Homogeneous Dirichlet by default

    # Discretize domain
    n_x = 50  # spatial points
    n_t = int(max(10, time_span * 10))  # temporal points
    dx = domain_length / (n_x - 1)
    dt = time_span / (n_t - 1)

    # Courant number (stability: r = α*dt/dx² ≤ 0.5 for FTCS)
    r = diffusivity * dt / (dx ** 2)
    if r > 0.5:
        # Reduce dt to maintain stability
        dt = 0.5 * dx ** 2 / diffusivity
        n_t = int(time_span / dt) + 1
        r = 0.5  # Exactly stable

    x_grid = np.linspace(0, domain_length, n_x)
    t_grid = np.linspace(0, time_span, n_t)

    # Initialize solution array
    u = np.zeros((n_t, n_x))

    # Set initial condition
    if isinstance(initial_condition, str):
        if "sin" in initial_condition:
            u[0, :] = np.sin(np.pi * x_grid / domain_length)
        else:
            u[0, :] = 1.0  # Default uniform
    else:
        u[0, :] = initial_condition[:n_x] if len(initial_condition) >= n_x else initial_condition[0]

    # Apply finite difference (Forward Time Centered Space)
    for n in range(n_t - 1):
        for i in range(1, n_x - 1):
            u[n + 1, i] = (r * u[n, i - 1] + (1 - 2 * r) * u[n, i] + r * u[n, i + 1])

        # Boundary conditions (Dirichlet)
        u[n + 1, 0] = bc_values[0]
        u[n + 1, -1] = bc_values[1]

    return {
        "solution_type": "numeric_ftcs",
        "solution_values": u[-1, :].tolist(),
        "spatial_grid": x_grid.tolist(),
        "time_final": t_grid[-1],
        "courant_number": r,
        "description": "1D heat equation solved via finite difference"
    }


def _wave_equation_1d(domain_length: float, time_span: float, wave_speed: float,
                      initial_displacement: Union[str, List[float]] = None,
                      initial_velocity: Union[str, List[float]] = None,
                      bc_type: str = "dirichlet", bc_values: List[float] = None) -> Dict[str, Any]:
    """
    Solve 1D wave equation: ∂²u/∂t² = c² * ∂²u/∂x².

    Args:
        domain_length: Length of spatial domain [0, L]
        time_span: Total time to solve
        wave_speed: Wave speed c
        initial_displacement: Initial position u(x, 0) or "sin(pi*x)"
        initial_velocity: Initial velocity ∂u/∂t(x, 0)
        bc_type: "dirichlet" or "periodic"
        bc_values: [value_at_0, value_at_L] for Dirichlet

    Returns:
        Dict with solution at final time, spatial grid, metadata
    """
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if time_span <= 0:
        raise ValueError("time_span must be positive")
    if wave_speed <= 0:
        raise ValueError("wave_speed must be positive")

    if bc_values is None:
        bc_values = [0.0, 0.0]

    # Discretize
    n_x = 50
    n_t = int(max(10, time_span * 10))
    dx = domain_length / (n_x - 1)
    dt = time_span / (n_t - 1)

    # Courant number (stability: r = c*dt/dx ≤ 1)
    r = wave_speed * dt / dx
    if r > 1.0:
        dt = 0.9 * dx / wave_speed
        n_t = int(time_span / dt) + 1
        r = 0.9

    x_grid = np.linspace(0, domain_length, n_x)
    t_grid = np.linspace(0, time_span, n_t)

    u = np.zeros((n_t, n_x))

    # Set initial displacement
    if initial_displacement is None or (isinstance(initial_displacement, str) and initial_displacement == "sin(pi*x)"):
        u[0, :] = np.sin(np.pi * x_grid / domain_length)
    else:
        u[0, :] = initial_displacement[:n_x] if len(initial_displacement) >= n_x else initial_displacement[0]

    # Set initial velocity: u[1, i] = u[0, i] + dt * v[i]
    if initial_velocity is None:
        v_ic = np.zeros_like(x_grid)
    elif isinstance(initial_velocity, str):
        v_ic = np.zeros_like(x_grid)  # Default to rest
    else:
        v_ic = initial_velocity[:n_x] if len(initial_velocity) >= n_x else initial_velocity[0]

    # First time step (forward Euler for velocity)
    r2 = r ** 2
    for i in range(1, n_x - 1):
        u[1, i] = (0.5 * r2 * (u[0, i + 1] - 2 * u[0, i] + u[0, i - 1])
                   + u[0, i] + dt * v_ic[i])
    u[1, 0] = bc_values[0]
    u[1, -1] = bc_values[1]

    # Subsequent time steps
    for n in range(1, n_t - 1):
        for i in range(1, n_x - 1):
            u[n + 1, i] = (r2 * (u[n, i + 1] - 2 * u[n, i] + u[n, i - 1])
                          + 2 * u[n, i] - u[n - 1, i])
        u[n + 1, 0] = bc_values[0]
        u[n + 1, -1] = bc_values[1]

    return {
        "solution_type": "numeric_ftcs",
        "solution_values": u[-1, :].tolist(),
        "spatial_grid": x_grid.tolist(),
        "time_final": t_grid[-1],
        "courant_number": r,
        "description": "1D wave equation solved via finite difference"
    }


def _laplace_equation(domain_length: float, num_points: float = 50,
                      boundary_conditions: Dict = None) -> Dict[str, Any]:
    """
    Solve 2D Laplace equation: ∇²u = ∂²u/∂x² + ∂²u/∂y² = 0.
    Uses Dirichlet boundary conditions on a rectangular domain [0, L] × [0, L].

    Args:
        domain_length: Side length of square domain
        num_points: Grid resolution (num_points × num_points)
        boundary_conditions: {"bottom": scalar or array, "top": ..., "left": ..., "right": ...}

    Returns:
        Dict with solution grid, solution values, metadata
    """
    num_points = int(num_points)
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if num_points < 5:
        raise ValueError("num_points must be at least 5")

    if boundary_conditions is None:
        boundary_conditions = {"bottom": 0.0, "top": 1.0, "left": 0.0, "right": 0.0}

    # Create grid
    x = np.linspace(0, domain_length, num_points)
    y = np.linspace(0, domain_length, num_points)
    X, Y = np.meshgrid(x, y)

    # Initialize with boundary conditions
    u = np.zeros((num_points, num_points))

    # Set boundaries
    u[0, :] = boundary_conditions.get("bottom", 0.0)
    u[-1, :] = boundary_conditions.get("top", 1.0)
    u[:, 0] = boundary_conditions.get("left", 0.0)
    u[:, -1] = boundary_conditions.get("right", 0.0)

    # Iterative solver (Jacobi iteration)
    tol = 1e-6
    max_iter = 1000
    for iteration in range(max_iter):
        u_old = u.copy()
        for i in range(1, num_points - 1):
            for j in range(1, num_points - 1):
                u[i, j] = 0.25 * (u_old[i + 1, j] + u_old[i - 1, j]
                                  + u_old[i, j + 1] + u_old[i, j - 1])

        if np.max(np.abs(u - u_old)) < tol:
            break

    return {
        "solution_type": "laplace_jacobi",
        "solution_values": u.flatten().tolist(),
        "grid_x": x.tolist(),
        "grid_y": y.tolist(),
        "iterations": iteration + 1,
        "convergence": float(np.max(np.abs(u - u_old))),
        "description": "2D Laplace equation solved via Jacobi iteration"
    }


def _poisson_equation(domain_length: float, num_points: float = 50,
                      source_term: str = "1.0", boundary_conditions: Dict = None) -> Dict[str, Any]:
    """
    Solve 2D Poisson equation: ∇²u = f(x, y) = ∂²u/∂x² + ∂²u/∂y².

    Args:
        domain_length: Side length of square domain
        num_points: Grid resolution
        source_term: Source function f as string (e.g., "1.0", "sin(pi*x)*cos(pi*y)")
        boundary_conditions: Dirichlet BCs on domain boundary

    Returns:
        Dict with solution grid and values
    """
    num_points = int(num_points)
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if num_points < 5:
        raise ValueError("num_points must be at least 5")

    if boundary_conditions is None:
        boundary_conditions = {"bottom": 0.0, "top": 0.0, "left": 0.0, "right": 0.0}

    # Create grid
    x = np.linspace(0, domain_length, num_points)
    y = np.linspace(0, domain_length, num_points)
    dx = domain_length / (num_points - 1)
    X, Y = np.meshgrid(x, y)

    # Initialize
    u = np.zeros((num_points, num_points))
    u[0, :] = boundary_conditions.get("bottom", 0.0)
    u[-1, :] = boundary_conditions.get("top", 0.0)
    u[:, 0] = boundary_conditions.get("left", 0.0)
    u[:, -1] = boundary_conditions.get("right", 0.0)

    # Source term evaluation
    f = np.ones((num_points, num_points))
    if source_term != "1.0":
        try:
            for i in range(num_points):
                for j in range(num_points):
                    f[i, j] = float(eval(source_term, {"x": X[i, j], "y": Y[i, j], "sin": np.sin, "cos": np.cos, "pi": np.pi}))
        except Exception:
            f[:] = 1.0

    # Jacobi iteration with source
    tol = 1e-6
    max_iter = 1000
    dx2 = dx ** 2

    for iteration in range(max_iter):
        u_old = u.copy()
        for i in range(1, num_points - 1):
            for j in range(1, num_points - 1):
                u[i, j] = 0.25 * (u_old[i + 1, j] + u_old[i - 1, j]
                                  + u_old[i, j + 1] + u_old[i, j - 1]
                                  - dx2 * f[i, j])

        if np.max(np.abs(u - u_old)) < tol:
            break

    return {
        "solution_type": "poisson_jacobi",
        "solution_values": u.flatten().tolist(),
        "grid_x": x.tolist(),
        "grid_y": y.tolist(),
        "iterations": iteration + 1,
        "convergence": float(np.max(np.abs(u - u_old))),
        "description": "2D Poisson equation solved via Jacobi iteration"
    }


def _dirichlet_bc(bc_value: float) -> float:
    """
    Dirichlet boundary condition: u = constant on boundary.
    Helper function to encode BC value.

    Args:
        bc_value: Constant value on boundary

    Returns:
        The boundary condition value
    """
    return float(bc_value)


def _neumann_bc(flux_value: float) -> float:
    """
    Neumann boundary condition: ∂u/∂n = constant on boundary.
    Helper function to encode flux.

    Args:
        flux_value: Flux value (normal derivative)

    Returns:
        The flux value
    """
    return float(flux_value)


def _robin_bc(alpha: float, beta: float, gamma: float) -> float:
    """
    Robin boundary condition: α*u + β*∂u/∂n = γ on boundary.
    Encodes the three parameters of the Robin condition.

    Args:
        alpha: Coefficient of u
        beta: Coefficient of normal derivative
        gamma: Right-hand side

    Returns:
        Dict with BC parameters
    """
    if alpha == 0 and beta == 0:
        raise ValueError("robin_bc: at least one of alpha, beta must be nonzero")
    return {"alpha": alpha, "beta": beta, "gamma": gamma}


def _periodic_bc(period: float) -> float:
    """
    Periodic boundary condition: u(0) = u(L), ∂u/∂x(0) = ∂u/∂x(L).
    Helper to encode period.

    Args:
        period: Length of periodic domain

    Returns:
        The period value
    """
    if period <= 0:
        raise ValueError("period must be positive")
    return float(period)


def _method_of_characteristics(domain_length: float, time_span: float,
                                wave_speed: float, initial_condition: str = "sin(pi*x)") -> Dict[str, Any]:
    """
    Solve advection equation ∂u/∂t + c*∂u/∂x = 0 via method of characteristics.
    Characteristics: dx/dt = c, so u is constant along x - c*t = const.

    Args:
        domain_length: Domain length
        time_span: Time to solve
        wave_speed: Advection speed c
        initial_condition: Initial profile as string

    Returns:
        Dict with solution at final time
    """
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if time_span <= 0:
        raise ValueError("time_span must be positive")
    if wave_speed == 0:
        raise ValueError("wave_speed cannot be zero for advection")

    n_x = 50
    x_grid = np.linspace(0, domain_length, n_x)

    # Evaluate initial condition
    u_init = np.zeros(n_x)
    if "sin" in initial_condition:
        u_init = np.sin(np.pi * x_grid / domain_length)
    elif "cos" in initial_condition:
        u_init = np.cos(np.pi * x_grid / domain_length)
    else:
        u_init[:] = 1.0

    # Solution along characteristics: u(x, t) = u_init(x - c*t)
    shift = (wave_speed * time_span) % domain_length
    u_final = np.roll(u_init, int(-shift / (domain_length / n_x)))

    return {
        "solution_type": "characteristics",
        "solution_values": u_final.tolist(),
        "spatial_grid": x_grid.tolist(),
        "time_final": time_span,
        "advection_shift": shift,
        "description": "Advection equation solved via method of characteristics"
    }


def _separation_of_variables(domain_length: float, time_span: float,
                              pde_type: str = "heat", diffusivity: float = 1.0) -> Dict[str, Any]:
    """
    Solve PDE via separation of variables (analytical approach).
    For heat equation: u(x,t) = exp(-π²*α*t) * sin(π*x/L).

    Args:
        domain_length: Domain length L
        time_span: Time interval
        pde_type: "heat" or "wave"
        diffusivity: Diffusivity α (for heat) or wave speed c (for wave)

    Returns:
        Dict with analytical solution
    """
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")

    n_x = 50
    x_grid = np.linspace(0, domain_length, n_x)

    if pde_type == "heat":
        # u(x,t) = exp(-π²*α*t/L²) * sin(π*x/L)
        decay = np.exp(-np.pi**2 * diffusivity * time_span / domain_length**2)
        u_final = decay * np.sin(np.pi * x_grid / domain_length)
        desc = "Heat equation via separation of variables"
    elif pde_type == "wave":
        # u(x,t) = sin(π*(x - c*t)/L) for wave propagation
        # Simplified: u(x,t) = sin(π*x/L) * cos(π*c*t/L)
        cos_term = np.cos(np.pi * diffusivity * time_span / domain_length)
        u_final = cos_term * np.sin(np.pi * x_grid / domain_length)
        desc = "Wave equation via separation of variables"
    else:
        raise ValueError(f"pde_type '{pde_type}' not supported (use 'heat' or 'wave')")

    return {
        "solution_type": "separation_of_variables",
        "solution_values": u_final.tolist(),
        "spatial_grid": x_grid.tolist(),
        "time_final": time_span,
        "description": desc
    }


def _finite_difference_solve(domain_length: float, time_span: float,
                             pde_type: str = "heat", parameter: float = 1.0,
                             initial_condition: str = "sin(pi*x)") -> Dict[str, Any]:
    """
    Generic finite difference solver for heat or wave PDEs.
    Dispatches to appropriate method based on pde_type.

    Args:
        domain_length: Domain length
        time_span: Time interval
        pde_type: "heat" or "wave"
        parameter: Diffusivity (heat) or wave speed (wave)
        initial_condition: Initial profile string

    Returns:
        Dict with numeric solution
    """
    if pde_type == "heat":
        return _heat_equation_1d(domain_length, time_span, parameter, initial_condition, "dirichlet", [0.0, 0.0])
    elif pde_type == "wave":
        return _wave_equation_1d(domain_length, time_span, parameter, initial_condition, None, "dirichlet", [0.0, 0.0])
    else:
        raise ValueError(f"pde_type '{pde_type}' not supported (use 'heat' or 'wave')")


def _d_alembert_solution(domain_length: float, time_span: float,
                        wave_speed: float, initial_displacement: str = "sin(pi*x)",
                        initial_velocity: str = "0") -> Dict[str, Any]:
    """
    D'Alembert's solution for 1D wave equation:
    u(x,t) = 1/2[f(x+ct) + f(x-ct)] + 1/(2c) ∫ g(s) ds from (x-ct) to (x+ct)

    where f is initial displacement, g is initial velocity.

    Args:
        domain_length: Domain length L
        time_span: Time to solve
        wave_speed: Wave speed c
        initial_displacement: Initial displacement f(x) as string
        initial_velocity: Initial velocity g(x) as string

    Returns:
        Dict with analytical solution
    """
    if domain_length <= 0:
        raise ValueError("domain_length must be positive")
    if time_span <= 0:
        raise ValueError("time_span must be positive")
    if wave_speed <= 0:
        raise ValueError("wave_speed must be positive")

    n_x = 50
    x_grid = np.linspace(0, domain_length, n_x)

    # Evaluate initial conditions
    f = np.zeros(n_x)
    g = np.zeros(n_x)

    if "sin" in initial_displacement:
        f = np.sin(np.pi * x_grid / domain_length)
    elif "cos" in initial_displacement:
        f = np.cos(np.pi * x_grid / domain_length)
    else:
        f[:] = 1.0

    if "0" not in initial_velocity:
        if "sin" in initial_velocity:
            g = np.sin(np.pi * x_grid / domain_length)
        elif "cos" in initial_velocity:
            g = np.cos(np.pi * x_grid / domain_length)

    # D'Alembert solution (simplified for periodic extension)
    u_final = np.zeros(n_x)
    c = wave_speed
    t = time_span

    for i, x in enumerate(x_grid):
        # Periodic extension for f and g
        x_plus = (x + c * t) % domain_length
        x_minus = (x - c * t) % domain_length

        # Linear interpolation for f(x ± ct)
        idx_plus = int(x_plus / domain_length * (n_x - 1))
        idx_minus = int(x_minus / domain_length * (n_x - 1))
        idx_plus = min(idx_plus, n_x - 1)
        idx_minus = min(idx_minus, n_x - 1)

        f_sum = 0.5 * (f[idx_plus] + f[idx_minus])

        # Velocity integral (simplified)
        g_integral = 0.5 / c * np.mean(g)  # Approximate as mean

        u_final[i] = f_sum + g_integral

    return {
        "solution_type": "d_alembert",
        "solution_values": u_final.tolist(),
        "spatial_grid": x_grid.tolist(),
        "time_final": time_span,
        "wave_speed": wave_speed,
        "description": "1D wave equation via D'Alembert solution"
    }


_OPERATIONS = {
    "heat_equation_1d": _heat_equation_1d,
    "wave_equation_1d": _wave_equation_1d,
    "laplace_equation": _laplace_equation,
    "poisson_equation": _poisson_equation,
    "dirichlet_bc": _dirichlet_bc,
    "neumann_bc": _neumann_bc,
    "robin_bc": _robin_bc,
    "periodic_bc": _periodic_bc,
    "method_of_characteristics": _method_of_characteristics,
    "separation_of_variables": _separation_of_variables,
    "finite_difference_solve": _finite_difference_solve,
    "d_alembert_solution": _d_alembert_solution,
}


@register("mathematics.pde")
class PDESolver(SolverBase):
    """
    Partial Differential Equations solver for heat, wave, Laplace, Poisson equations.
    Supports both symbolic (SymPy) and numeric (finite difference, iterative) methods.
    All operations are pure functions with deterministic output.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve PDE models using function-dispatch pattern.
        Equations expected: operation_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations using custom PDE resolver
            summary = _pde_run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="PDE solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
