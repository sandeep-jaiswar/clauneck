"""Optics solver (physics.optics domain)."""
import math
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _optical_image_distance(f: float, d_o: float) -> float:
    """Optical image distance (thin lens/mirror): 1/f = 1/d_o + 1/d_i -> d_i (meters)."""
    if f == 0:
        raise ValueError("Focal length f must be non-zero")
    if d_o == 0:
        raise ValueError("Object distance d_o must be non-zero")
    denominator = 1.0 / f - 1.0 / d_o
    if abs(denominator) < 1e-10:
        raise ValueError("Image distance would be infinite (denominator near zero)")
    return float(1.0 / denominator)


def _thin_lens_image_distance(f: float, d_o: float) -> float:
    """Thin lens equation: 1/f = 1/d_o + 1/d_i -> d_i (meters)."""
    return _optical_image_distance(f, d_o)


def _mirror_image_distance(f: float, d_o: float) -> float:
    """Mirror equation (same as lens): 1/f = 1/d_o + 1/d_i -> d_i (meters)."""
    return _optical_image_distance(f, d_o)


def _magnification_optical(d_i: float, d_o: float) -> float:
    """Magnification: m = -d_i/d_o (dimensionless)."""
    if d_o == 0:
        raise ValueError("Object distance d_o must be non-zero")
    return float(-d_i / d_o)


def _lensmaker_focal_length(n: float, R1: float, R2: float) -> float:
    """Lensmaker's equation: 1/f = (n-1)(1/R1 - 1/R2) -> f (meters)."""
    if n <= 1:
        raise ValueError("Refractive index n must be > 1")
    if R1 == 0 or R2 == 0:
        raise ValueError("Radii R1 and R2 must be non-zero")
    denominator = (n - 1.0) * (1.0 / R1 - 1.0 / R2)
    if abs(denominator) < 1e-10:
        raise ValueError("Focal length would be infinite")
    return float(1.0 / denominator)


def _snells_law_angle2(n1: float, theta1: float, n2: float) -> float:
    """Snell's law: n1*sin(θ1) = n2*sin(θ2) -> θ2 (degrees)."""
    if n1 <= 0 or n2 <= 0:
        raise ValueError("Refractive indices must be positive")
    # Convert theta1 from degrees to radians
    theta1_rad = math.radians(theta1)
    sin_theta2 = (n1 / n2) * math.sin(theta1_rad)
    if abs(sin_theta2) > 1.0:
        raise ValueError(f"sin(θ2) = {sin_theta2} exceeds 1 (total internal reflection)")
    theta2_rad = math.asin(sin_theta2)
    return float(math.degrees(theta2_rad))


def _critical_angle(n1: float, n2: float) -> float:
    """Critical angle for total internal reflection: sin(θ_c) = n2/n1 -> θ_c (degrees)."""
    if n1 <= n2:
        raise ValueError("First medium must be denser than second (n1 > n2)")
    if n1 <= 0 or n2 < 0:
        raise ValueError("Refractive indices must be non-negative")
    sin_theta_c = n2 / n1
    if sin_theta_c > 1.0:
        raise ValueError(f"sin(θ_c) = {sin_theta_c} exceeds 1 (invalid optical media)")
    theta_c_rad = math.asin(sin_theta_c)
    return float(math.degrees(theta_c_rad))


def _double_slit_fringe_spacing(wavelength: float, L: float, d: float) -> float:
    """Double slit fringe spacing: Δy = λL/d (meters)."""
    if wavelength <= 0:
        raise ValueError("Wavelength must be positive")
    if L <= 0:
        raise ValueError("Distance to screen L must be positive")
    if d <= 0:
        raise ValueError("Slit separation d must be positive")
    return float(wavelength * L / d)


def _diffraction_grating_angle(wavelength: float, d: float, m: float) -> float:
    """Diffraction grating: d*sin(θ) = m*λ -> θ (degrees)."""
    if d <= 0:
        raise ValueError("Grating spacing d must be positive")
    if wavelength <= 0:
        raise ValueError("Wavelength must be positive")
    sin_theta = (m * wavelength) / d
    if abs(sin_theta) > 1.0:
        raise ValueError(f"sin(θ) = {sin_theta} exceeds 1 (order m not observable)")
    theta_rad = math.asin(sin_theta)
    return float(math.degrees(theta_rad))


def _lens_power(f: float) -> float:
    """Lens power: P = 1/f (diopters, D = m^-1)."""
    if f == 0:
        raise ValueError("Focal length f must be non-zero")
    return float(1.0 / f)


_OPERATIONS = {
    "thin_lens_image_distance": _thin_lens_image_distance,
    "mirror_image_distance": _mirror_image_distance,
    "magnification_optical": _magnification_optical,
    "lensmaker_focal_length": _lensmaker_focal_length,
    "snells_law_angle2": _snells_law_angle2,
    "critical_angle": _critical_angle,
    "double_slit_fringe_spacing": _double_slit_fringe_spacing,
    "diffraction_grating_angle": _diffraction_grating_angle,
    "lens_power": _lens_power,
}


@register("physics.optics")
class PhysicsOpticsSolver(SolverBase):
    """
    Solver for geometric optics: thin lenses, mirrors, refraction, diffraction.
    Supports operations like thin_lens_image_distance, snells_law_angle2, etc.
    All calculations are closed-form (no ODE integration).
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve optics problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Optics solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
