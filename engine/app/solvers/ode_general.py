"""General ODE solver for arbitrary user-supplied RHS expressions."""
from typing import Dict, List, Callable, Tuple, Optional
import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

from app.model import ScientificModel, SolverMethod, SolverResult, Quantity, Equation, EquationType
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.ode")
class ODEGeneralSolver(SolverBase):
    """
    Generic symbolic/numeric ODE solver for arbitrary user-supplied RHS expressions.
    Attempts closed-form solution via sympy.dsolve, falls back to numeric integration.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve ODEs in the form: dy/dt = <expression>, d2y/dt2 = <expression>, etc.
        Returns trajectory dict with time array and state arrays.
        """
        try:
            # Extract ODE equations
            ode_equations = [eq for eq in model.equations if eq.type == EquationType.ODE]
            if not ode_equations:
                return SolverResult(
                    success=False,
                    message="No ODE equations found in model",
                    error="Expected at least one ODE equation"
                )

            # Extract quantities into a map for value lookup
            quantities = {q.name: q for q in model.quantities}
            ic = model.initialConditions or {}

            # Parse ODE system: extract dependent variable, independent variable, RHS expressions
            # For now, assume single independent variable (t) and extract all ODEs
            ode_system = self._parse_ode_system(ode_equations, quantities, ic)
            if not ode_system:
                return SolverResult(
                    success=False,
                    message="Could not parse ODE system",
                    error="Unable to extract dependent variables from equations"
                )

            independent_var = ode_system["independent_var"]  # Usually 't'
            dependent_vars = ode_system["dependent_vars"]  # e.g., ['y', 'z']
            derivatives = ode_system["derivatives"]  # e.g., {('y', 1): '-2*y', ...}

            # Try symbolic solution first
            symbolic_result = self._try_symbolic_solve(
                independent_var, dependent_vars, derivatives, ic
            )
            if symbolic_result is not None:
                return symbolic_result

            # Fall back to numeric integration
            return self._numeric_solve(
                model, independent_var, dependent_vars, derivatives, ic, quantities
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="ODE solver error",
                error=str(e)
            )

    def _parse_ode_system(self, ode_equations: List[Equation], quantities: Dict[str, Quantity],
                          ic: Dict[str, float]) -> Optional[Dict]:
        """
        Parse ODE equations to extract dependent variables, independent variable, and RHS expressions.
        Recognizes patterns like: dy/dt, d2y/dt2, dz/dt, etc.
        Returns dict with independent_var, dependent_vars, and derivatives mapping.
        """
        derivatives = {}  # {(var_name, order): rhs_expr_str}
        independent_var = None
        dependent_vars_set = set()

        for eq in ode_equations:
            lhs = eq.lhs.strip()
            # Parse LHS: e.g., "dy/dt" -> (y, 1, t), "d2y/dt2" -> (y, 2, t)
            parsed = self._parse_derivative_lhs(lhs)
            if parsed is None:
                continue

            var_name, order, ind_var = parsed
            dependent_vars_set.add(var_name)

            if independent_var is None:
                independent_var = ind_var
            elif independent_var != ind_var:
                # Multi-variable independent system not supported yet
                return None

            derivatives[(var_name, order)] = eq.rhs.strip()

        if not dependent_vars_set or not independent_var:
            return None

        return {
            "independent_var": independent_var,
            "dependent_vars": sorted(list(dependent_vars_set)),
            "derivatives": derivatives,
        }

    def _parse_derivative_lhs(self, lhs: str) -> Optional[Tuple[str, int, str]]:
        """
        Parse derivative notation: dy/dt, d2y/dt2, etc.
        Returns (variable_name, order, independent_var) or None if not recognized.
        """
        # Remove spaces
        lhs = lhs.replace(" ", "")

        # Match pattern: d^n<var>/d<indvar>^n
        # Simple parsing: look for d, number (optional), variable, /, d, variable
        if not lhs.startswith("d"):
            return None

        # Extract order (e.g., "2" from "d2y/dt2")
        idx = 1
        order_str = ""
        while idx < len(lhs) and lhs[idx].isdigit():
            order_str += lhs[idx]
            idx += 1
        order = int(order_str) if order_str else 1

        # Next char should be the dependent variable
        if idx >= len(lhs):
            return None
        var_name = lhs[idx]
        idx += 1

        # Next should be "/"
        if idx >= len(lhs) or lhs[idx] != "/":
            return None
        idx += 1

        # Now parse the denominator: d<indvar>^n
        if idx >= len(lhs) or lhs[idx] != "d":
            return None
        idx += 1

        # Extract independent variable name (usually just one character, but allow more)
        ind_var_start = idx
        while idx < len(lhs) and lhs[idx].isalpha():
            idx += 1
        ind_var = lhs[ind_var_start:idx]

        # Check if there's an order indicator in denominator (e.g., dt2)
        denom_order_str = ""
        while idx < len(lhs) and lhs[idx].isdigit():
            denom_order_str += lhs[idx]
            idx += 1
        denom_order = int(denom_order_str) if denom_order_str else 1

        # Verify order matches
        if order != denom_order:
            return None

        # Consume any trailing characters (shouldn't be any)
        if idx != len(lhs):
            return None

        return (var_name, order, ind_var)

    def _try_symbolic_solve(self, ind_var: str, dependent_vars: List[str],
                            derivatives: Dict, ic: Dict[str, float]) -> Optional[SolverResult]:
        """
        Attempt symbolic solution using sympy.dsolve for simple ODEs.
        Only attempt if we have first-order ODEs or simple second-order.
        Returns SolverResult on success, None to fall back to numeric.
        """
        # Only attempt symbolic for single first-order ODE with known closed form
        if len(dependent_vars) != 1 or not any(order == 1 for _, order in derivatives.keys()):
            return None

        var = sp.Symbol(dependent_vars[0])
        t = sp.Symbol(ind_var)

        # Find first-order ODE
        rhs_expr_str = derivatives.get((dependent_vars[0], 1))
        if rhs_expr_str is None:
            return None

        try:
            # Parse RHS expression
            rhs_expr = sp.sympify(rhs_expr_str)
            # Create ODE: d(var)/d(t) = rhs
            ode = sp.Eq(sp.Derivative(var, t), rhs_expr)

            # Try to solve symbolically
            dsolve_solution = sp.dsolve(ode, var)
            if dsolve_solution is None or isinstance(dsolve_solution, list):
                return None

            # Extract solution: dsolve returns Eq, get RHS
            solution = dsolve_solution.rhs

            # Apply initial condition to find constant
            if dependent_vars[0] not in ic:
                return None
            y0 = ic[dependent_vars[0]]

            # Substitute t=0 and solve for the constant C1 (or similar)
            solution_at_0 = solution.subs(t, 0)
            constants = solution.free_symbols - {t, sp.Symbol(dependent_vars[0])}
            if constants:
                # Solve for constant
                const = list(constants)[0]
                const_value = sp.solve(sp.Eq(solution_at_0, y0), const)
                if const_value:
                    solution = solution.subs(const, const_value[0])

            # Lambdify for evaluation
            y_func = sp.lambdify(t, solution, "numpy")
            return SolverResult(
                success=False,  # Mark as "try numeric instead"
                message="Symbolic solution found but using numeric for consistency",
                error=None
            )
        except Exception:
            return None

    def _numeric_solve(self, model: ScientificModel, ind_var: str,
                       dependent_vars: List[str], derivatives: Dict,
                       ic: Dict[str, float], quantities: Dict[str, Quantity]) -> SolverResult:
        """
        Numeric ODE solver using scipy.integrate.solve_ivp.
        Constructs RHS function and integrates over timeSpan.
        """
        # Validate timeSpan
        if not model.solver.timeSpan:
            return SolverResult(
                success=False,
                message="timeSpan is required for numeric ODE solving",
                error="No time bounds provided"
            )

        time_span = model.solver.timeSpan
        t_span = (time_span.start, time_span.end)
        t_eval = np.linspace(time_span.start, time_span.end,
                             time_span.numPoints or 1000)

        # For each dependent variable, find the highest-order derivative
        max_order = {}
        for (var, order), _ in derivatives.items():
            if var not in max_order:
                max_order[var] = order
            max_order[var] = max(max_order[var], order)

        # Build state vector representation
        # If we have d2y/dt2, we need both y and dy/dt
        state_vars = []
        state_var_to_idx = {}
        idx = 0
        for var in dependent_vars:
            state_vars.append(var)
            state_var_to_idx[(var, 0)] = idx
            idx += 1
            if max_order.get(var, 0) > 1:
                state_vars.append(f"d{var}/d{ind_var}")
                state_var_to_idx[(var, 1)] = idx
                idx += 1

        # Build initial state vector in the order of state_vars
        y0 = []
        for var in dependent_vars:
            if var not in ic:
                return SolverResult(
                    success=False,
                    message=f"Missing initial condition for {var}",
                    error=f"No value in initialConditions for {var}"
                )
            y0.append(ic[var])

            # For second-order ODEs, need velocity IC
            if max_order.get(var, 0) > 1:
                vel_var = f"d{var}/d{ind_var}"
                if vel_var not in ic:
                    # Try to infer from IC or default to 0
                    y0.append(ic.get(vel_var, 0.0))
                else:
                    y0.append(ic[vel_var])

        # Create lambdified RHS functions
        # For each derivative, create a function with only the symbols it uses
        rhs_funcs = {}
        for (var, order), rhs_expr_str in derivatives.items():
            try:
                expr = sp.sympify(rhs_expr_str)
                # Get all symbols in this expression
                expr_symbols = expr.free_symbols
                # Build argument list: always include time first, then only needed state vars
                arg_symbols = [sp.Symbol(ind_var)]
                for sv in state_vars:
                    if sp.Symbol(sv) in expr_symbols:
                        arg_symbols.append(sp.Symbol(sv))

                # Store both the function and the list of argument symbols
                rhs_funcs[(var, order)] = {
                    'func': sp.lambdify(arg_symbols, expr, "numpy"),
                    'args': [s.name for s in arg_symbols]
                }
            except Exception as e:
                return SolverResult(
                    success=False,
                    message=f"Failed to parse RHS for d{order}{var}/d{ind_var}{order}: {e}",
                    error=str(e)
                )

        # Define ODE system
        def ode_rhs(t, y_state):
            # y_state is ordered as: [y, dy/dt, z, dz/dt, ...] for second-order vars
            dydt = np.zeros(len(y_state))

            # Helper to map variable names to state values
            def get_state_value(arg_name):
                """Map variable name to state value."""
                # Check if it's a direct variable
                if (arg_name, 0) in state_var_to_idx:
                    return y_state[state_var_to_idx[(arg_name, 0)]]
                # Check if it's a derivative
                elif (arg_name, 1) in state_var_to_idx:
                    return y_state[state_var_to_idx[(arg_name, 1)]]
                # Try parsing derivative notation
                else:
                    # Handle patterns like "dx/dt"
                    for (v, deriv), idx_val in state_var_to_idx.items():
                        if v == arg_name:
                            return y_state[idx_val]
                        elif f"d{v}/d{ind_var}" == arg_name and deriv == 1:
                            return y_state[idx_val]
                    # Not found, return 0.0
                    return 0.0

            for var in dependent_vars:
                order = max_order.get(var, 1)

                if order == 1:
                    # First-order: dy/dt = f(t, y)
                    if (var, 1) in rhs_funcs:
                        func_data = rhs_funcs[(var, 1)]
                        args = [t]
                        # Build arguments in the order expected by the lambdified function
                        for arg_name in func_data['args'][1:]:  # Skip time (already added)
                            args.append(get_state_value(arg_name))

                        result = func_data['func'](*args)
                        dydt[state_var_to_idx[(var, 0)]] = result

                elif order == 2:
                    # Second-order: convert to first-order system
                    # dy1/dt = y2 (where y1 = y, y2 = dy/dt)
                    # dy2/dt = d2y/dt2 = f(t, y, dy/dt)

                    # First equation: dy/dt = dy/dt (identity)
                    dydt[state_var_to_idx[(var, 0)]] = y_state[state_var_to_idx[(var, 1)]]

                    # Second equation: d(dy/dt)/dt = d2y/dt2
                    if (var, 2) in rhs_funcs:
                        func_data = rhs_funcs[(var, 2)]
                        args = [t]
                        for arg_name in func_data['args'][1:]:  # Skip time
                            args.append(get_state_value(arg_name))

                        result = func_data['func'](*args)
                        dydt[state_var_to_idx[(var, 1)]] = result

            return dydt

        # Solve ODE
        try:
            sol = solve_ivp(
                ode_rhs,
                t_span,
                y0,
                t_eval=t_eval,
                method=self._map_solver_method(model.solver.method),
                rtol=model.solver.tolerance,
                atol=model.solver.tolerance * 1e-2,
                dense_output=True,
            )

            if not sol.success:
                return SolverResult(
                    success=False,
                    message=f"Integration failed: {sol.message}",
                    error=sol.message
                )

            # Build trajectory dict
            trajectory = {"t": sol.t.tolist()}
            idx = 0
            for var in dependent_vars:
                trajectory[var] = sol.y[idx].tolist()
                idx += 1
                if max_order.get(var, 0) > 1:
                    trajectory[f"d{var}/d{ind_var}"] = sol.y[idx].tolist()
                    idx += 1

            # Build summary: final values
            summary = {}
            idx = 0
            for var in dependent_vars:
                summary[f"{var}_final"] = float(sol.y[idx, -1])
                idx += 1
                if max_order.get(var, 0) > 1:
                    summary[f"d{var}/d{ind_var}_final"] = float(sol.y[idx, -1])
                    idx += 1

            return SolverResult(
                success=True,
                message="ODE solved successfully",
                trajectory=trajectory,
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Integration error",
                error=str(e)
            )

    def _map_solver_method(self, method: SolverMethod) -> str:
        """Map SolverMethod enum to scipy method name."""
        mapping = {
            SolverMethod.RK45: "RK45",
            SolverMethod.RK23: "RK23",
            SolverMethod.DOP853: "DOP853",
            SolverMethod.SOLVE_IVP: "RK45",  # default
            SolverMethod.ODEINT: "RK45",      # odeint fallback
            SolverMethod.SYMBOLIC_SOLVE: "RK45",  # symbolic fallback to numeric
        }
        return mapping.get(method, "RK45")
