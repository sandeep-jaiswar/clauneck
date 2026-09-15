"""Projectile motion solver (physics.mechanics domain)."""
from typing import Dict
import numpy as np
from scipy.integrate import solve_ivp

from app.model import ScientificModel, SolverMethod, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("physics.mechanics")
class ProjectileMotionSolver(SolverBase):
    """
    Specialized solver for projectile motion with air resistance.
    This is the vertical slice proof-of-concept.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve projectile motion with drag.
        Equations expected:
          d2x/dt2 = -drag_coeff * vx * |v| / mass
          d2y/dt2 = -g - drag_coeff * vy * |v| / mass
        """
        try:
            # Extract quantities
            quantities = {q.name: q for q in model.quantities}
            ic = model.initialConditions or {}

            # Get parameters
            v0 = self._get_value(quantities, "v0", ic)
            angle = self._get_value(quantities, "angle", ic)
            mass = self._get_value(quantities, "mass", ic)
            g = self._get_value(quantities, "g", ic)
            drag_coeff = self._get_optional_value(
                quantities, "drag_coeff", ic, default=0.0
            )

            # Convert only when the model explicitly declares degrees.
            angle_unit = quantities["angle"].siUnit
            if angle_unit == "deg":
                angle_rad = np.radians(angle)
            elif angle_unit == "rad":
                angle_rad = angle
            else:
                raise ValueError(
                    f"Unsupported angle unit '{angle_unit}'; expected 'deg' or 'rad'"
                )

            # Initial conditions
            vx0 = v0 * np.cos(angle_rad)
            vy0 = v0 * np.sin(angle_rad)
            x0, y0 = 0.0, 0.0

            # Define the ODE system for solve_ivp
            def projectile_ode(t, state):
                x, y, vx, vy = state
                v_mag = np.sqrt(vx**2 + vy**2)

                # Avoid division by zero
                if v_mag < 1e-10:
                    ax = 0
                    ay = -g
                else:
                    drag = drag_coeff * v_mag / mass
                    ax = -drag * vx
                    ay = -g - drag * vy

                return [vx, vy, ax, ay]

            def ground_crossing(t, state):
                return state[1]

            ground_crossing.terminal = True
            ground_crossing.direction = -1

            # Determine time span
            time_span = model.solver.timeSpan
            if time_span:
                t_span = (time_span.start, time_span.end)
                t_eval = np.linspace(time_span.start, time_span.end,
                                      time_span.numPoints or 1000)
            else:
                # Default: integrate until projectile hits ground (y = 0)
                t_span = (0, 100)  # safety upper bound
                t_eval = np.linspace(0, 100, 10000)

            # Solve ODE
            sol = solve_ivp(
                projectile_ode,
                t_span,
                [x0, y0, vx0, vy0],
                t_eval=t_eval,
                method=self._map_solver_method(model.solver.method),
                rtol=model.solver.tolerance,
                atol=model.solver.tolerance * 1e-2,
                dense_output=True,
                events=ground_crossing,
            )

            if not sol.success:
                return SolverResult(
                    success=False,
                    message=f"Integration failed: {sol.message}",
                    error=sol.message
                )

            # Extract trajectory
            trajectory = {
                "t": sol.t.tolist(),
                "x": sol.y[0].tolist(),
                "y": sol.y[1].tolist(),
                "vx": sol.y[2].tolist(),
                "vy": sol.y[3].tolist(),
            }

            # Event values provide the actual impact rather than the last t_eval
            # sample. Keep the trajectory itself on the requested t_eval grid.
            if sol.t_events[0].size:
                flight_time = float(sol.t_events[0][0])
                max_range = float(sol.y_events[0][0][0])
            else:
                flight_time = float(sol.t[-1])
                max_range = float(sol.y[0, -1])

            max_height = float(np.max(sol.y[1]))

            summary = {
                "max_range": max_range,
                "max_height": max_height,
                "flight_time": flight_time,
            }

            return SolverResult(
                success=True,
                message="Projectile motion solved successfully",
                trajectory=trajectory,
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

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

    def _get_optional_value(self, quantities: Dict[str, Quantity],
                            name: str, ic: Dict[str, float],
                            default: float) -> float:
        """Get an optional quantity value, falling back to a domain default."""
        if name in ic:
            return ic[name]
        if name in quantities and quantities[name].value is not None:
            val = quantities[name].value
            if isinstance(val, (int, float)):
                return float(val)
            else:
                raise ValueError(f"Expected scalar value for {name}, got {type(val)}")
        return default

    def _map_solver_method(self, method: SolverMethod) -> str:
        """Map our SolverMethod enum to scipy method name."""
        mapping = {
            SolverMethod.RK45: "RK45",
            SolverMethod.RK23: "RK23",
            SolverMethod.DOP853: "DOP853",
            SolverMethod.SOLVE_IVP: "RK45",  # default
            SolverMethod.ODEINT: "RK45",      # odeint fallback
        }
        return mapping.get(method, "RK45")
