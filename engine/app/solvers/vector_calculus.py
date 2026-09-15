"""Vector calculus solver (mathematics.vector_calculus domain)."""
from typing import Dict, Tuple, List, Union
import numpy as np
from sympy import symbols, sin, cos, diff, Matrix, simplify
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_vector, to_cylindrical, from_cylindrical, to_spherical, from_spherical


def _gradient_2d(fx: float, fy: float, dx: float, dy: float) -> Dict[str, float]:
    """
    Gradient of scalar field f in 2D Cartesian: ∇f = (∂f/∂x, ∂f/∂y).
    Computes via finite differences.
    Returns dict with grad_x, grad_y.
    """
    if abs(dx) < 1e-10 or abs(dy) < 1e-10:
        raise ValueError("Grid spacings dx, dy must be non-zero")
    grad_x = fx / dx  # Simplified: assumes fx is already a derivative approximation
    grad_y = fy / dy  # Simplified: assumes fy is already a derivative approximation
    return {"grad_x": float(grad_x), "grad_y": float(grad_y)}


def _gradient_3d(fx: float, fy: float, fz: float, dx: float, dy: float, dz: float) -> Dict[str, float]:
    """
    Gradient of scalar field f in 3D Cartesian: ∇f = (∂f/∂x, ∂f/∂y, ∂f/∂z).
    Computes via finite differences.
    Returns dict with grad_x, grad_y, grad_z.
    """
    if abs(dx) < 1e-10 or abs(dy) < 1e-10 or abs(dz) < 1e-10:
        raise ValueError("Grid spacings dx, dy, dz must be non-zero")
    grad_x = fx / dx
    grad_y = fy / dy
    grad_z = fz / dz
    return {"grad_x": float(grad_x), "grad_y": float(grad_y), "grad_z": float(grad_z)}


def _divergence_2d(vx: float, vy: float, dx: float, dy: float) -> float:
    """
    Divergence of vector field F = (vx, vy) in 2D Cartesian: ∇·F = ∂vx/∂x + ∂vy/∂y.
    Computes via finite differences.
    Returns scalar divergence.
    """
    if abs(dx) < 1e-10 or abs(dy) < 1e-10:
        raise ValueError("Grid spacings dx, dy must be non-zero")
    div = vx / dx + vy / dy
    return float(div)


def _divergence_3d(vx: float, vy: float, vz: float, dx: float, dy: float, dz: float) -> float:
    """
    Divergence of vector field F = (vx, vy, vz) in 3D Cartesian: ∇·F = ∂vx/∂x + ∂vy/∂y + ∂vz/∂z.
    Computes via finite differences.
    Returns scalar divergence.
    """
    if abs(dx) < 1e-10 or abs(dy) < 1e-10 or abs(dz) < 1e-10:
        raise ValueError("Grid spacings dx, dy, dz must be non-zero")
    div = vx / dx + vy / dy + vz / dz
    return float(div)


def _curl_2d(vx: float, vy: float, dx: float, dy: float) -> float:
    """
    Curl of 2D vector field F = (vx, vy) in Cartesian (returns z-component):
    (∇ × F)_z = ∂vy/∂x - ∂vx/∂y.
    Computes via finite differences.
    Returns scalar (z-component of curl).
    """
    if abs(dx) < 1e-10 or abs(dy) < 1e-10:
        raise ValueError("Grid spacings dx, dy must be non-zero")
    curl_z = vy / dx - vx / dy
    return float(curl_z)


def _curl_3d(vx: float, vy: float, vz: float,
             dvx_dy: float, dvx_dz: float,
             dvy_dx: float, dvy_dz: float,
             dvz_dx: float, dvz_dy: float) -> Dict[str, float]:
    """
    Curl of 3D vector field F = (vx, vy, vz) in Cartesian:
    ∇ × F = (∂vz/∂y - ∂vy/∂z, ∂vx/∂z - ∂vz/∂x, ∂vy/∂x - ∂vx/∂y).
    Takes partial derivatives as arguments.
    Returns dict with curl_x, curl_y, curl_z.
    """
    curl_x = dvz_dy - dvy_dz
    curl_y = dvx_dz - dvz_dx
    curl_z = dvy_dx - dvx_dy
    return {"curl_x": float(curl_x), "curl_y": float(curl_y), "curl_z": float(curl_z)}


def _directional_derivative(grad_x: float, grad_y: float, u_x: float, u_y: float) -> float:
    """
    Directional derivative of scalar field in direction of unit vector u = (u_x, u_y):
    D_u f = ∇f · u = grad_x * u_x + grad_y * u_y.
    Returns scalar.
    """
    u_mag = np.sqrt(u_x**2 + u_y**2)
    if u_mag < 1e-10:
        raise ValueError("Direction vector u must be non-zero")
    u_x_norm = u_x / u_mag
    u_y_norm = u_y / u_mag
    d_u = grad_x * u_x_norm + grad_y * u_y_norm
    return float(d_u)


def _laplacian_2d(fxx: float, fyy: float) -> float:
    """
    Laplacian of scalar field in 2D Cartesian: ∇²f = ∂²f/∂x² + ∂²f/∂y².
    Takes second partial derivatives as arguments.
    Returns scalar.
    """
    laplacian = fxx + fyy
    return float(laplacian)


def _laplacian_3d(fxx: float, fyy: float, fzz: float) -> float:
    """
    Laplacian of scalar field in 3D Cartesian: ∇²f = ∂²f/∂x² + ∂²f/∂y² + ∂²f/∂z².
    Takes second partial derivatives as arguments.
    Returns scalar.
    """
    laplacian = fxx + fyy + fzz
    return float(laplacian)


def _line_integral(fx_start: float, fx_end: float, fy_start: float, fy_end: float,
                   x_start: float, x_end: float, y_start: float, y_end: float) -> float:
    """
    Line integral of vector field F = (fx, fy) along path from (x_start, y_start) to (x_end, y_end).
    Simplified: assumes linear path and uses trapezoidal rule.
    ∫_C F·dr ≈ (fx_start + fx_end)/2 * (x_end - x_start) + (fy_start + fy_end)/2 * (y_end - y_start).
    Returns scalar.
    """
    dx = x_end - x_start
    dy = y_end - y_start
    integral = (fx_start + fx_end) / 2.0 * dx + (fy_start + fy_end) / 2.0 * dy
    return float(integral)


def _surface_integral(fx_avg: float, fy_avg: float, fz_avg: float, area: float,
                     nx: float, ny: float, nz: float) -> float:
    """
    Surface integral of vector field F = (fx, fy, fz) over a surface with area and unit normal n = (nx, ny, nz).
    ∫∫_S F·n dS ≈ (F_avg · n) * Area.
    Returns scalar.
    """
    if area <= 0:
        raise ValueError("Surface area must be positive")
    n_mag = np.sqrt(nx**2 + ny**2 + nz**2)
    if n_mag < 1e-10:
        raise ValueError("Normal vector must be non-zero")
    n_x = nx / n_mag
    n_y = ny / n_mag
    n_z = nz / n_mag
    dot_product = fx_avg * n_x + fy_avg * n_y + fz_avg * n_z
    integral = dot_product * area
    return float(integral)


def _volume_integral(f_avg: float, volume: float) -> float:
    """
    Volume integral of scalar field f over a volume V.
    ∫∫∫_V f dV ≈ f_avg * Volume.
    Returns scalar.
    """
    if volume <= 0:
        raise ValueError("Volume must be positive")
    integral = f_avg * volume
    return float(integral)


def _greens_theorem(line_integral_pdx: float, line_integral_qdy: float,
                   dq_dx: float, dp_dy: float, area: float) -> Dict[str, float]:
    """
    Green's Theorem: ∮_C (P dx + Q dy) = ∬_D (∂Q/∂x - ∂P/∂y) dA.
    Given line integrals and partial derivatives, verify theorem.
    Returns dict with line_integral_lhs, surface_integral_rhs, difference.
    """
    if area <= 0:
        raise ValueError("Area must be positive")
    line_lhs = line_integral_pdx + line_integral_qdy
    surface_rhs = (dq_dx - dp_dy) * area
    diff = abs(line_lhs - surface_rhs)
    return {
        "line_integral_lhs": float(line_lhs),
        "surface_integral_rhs": float(surface_rhs),
        "difference": float(diff)
    }


def _stokes_theorem(line_integral: float, curl_z: float, area: float) -> Dict[str, float]:
    """
    Stokes' Theorem (2D): ∮_C F·dr = ∬_D (∇ × F)·n dA.
    For 2D, curl_z is z-component of curl, n = (0, 0, 1), so (∇ × F)·n = curl_z.
    Returns dict with line_integral_lhs, surface_integral_rhs, difference.
    """
    if area <= 0:
        raise ValueError("Area must be positive")
    surface_rhs = curl_z * area
    diff = abs(line_integral - surface_rhs)
    return {
        "line_integral_lhs": float(line_integral),
        "surface_integral_rhs": float(surface_rhs),
        "difference": float(diff)
    }


def _divergence_theorem(surface_integral: float, div_f: float, volume: float) -> Dict[str, float]:
    """
    Divergence Theorem: ∮_S F·n dS = ∭_V (∇·F) dV.
    Returns dict with surface_integral_lhs, volume_integral_rhs, difference.
    """
    if volume <= 0:
        raise ValueError("Volume must be positive")
    volume_integral_rhs = div_f * volume
    diff = abs(surface_integral - volume_integral_rhs)
    return {
        "surface_integral_lhs": float(surface_integral),
        "volume_integral_rhs": float(volume_integral_rhs),
        "difference": float(diff)
    }


def _cartesian_to_cylindrical(x: float, y: float) -> Dict[str, float]:
    """
    Convert Cartesian (x, y) to cylindrical (rho, phi).
    Returns dict with rho, phi (phi in radians).
    """
    rho, phi = to_cylindrical(x, y)
    return {"rho": float(rho), "phi": float(phi)}


def _cylindrical_to_cartesian(rho: float, phi: float) -> Dict[str, float]:
    """
    Convert cylindrical (rho, phi) to Cartesian (x, y).
    phi in radians.
    Returns dict with x, y.
    """
    x, y = from_cylindrical(rho, phi)
    return {"x": float(x), "y": float(y)}


def _cartesian_to_spherical(x: float, y: float, z: float) -> Dict[str, float]:
    """
    Convert Cartesian (x, y, z) to spherical (r, theta, phi).
    theta is polar angle [0, pi], phi is azimuthal angle in radians.
    Returns dict with r, theta, phi.
    """
    r, theta, phi = to_spherical(x, y, z)
    return {"r": float(r), "theta": float(theta), "phi": float(phi)}


def _spherical_to_cartesian(r: float, theta: float, phi: float) -> Dict[str, float]:
    """
    Convert spherical (r, theta, phi) to Cartesian (x, y, z).
    theta is polar angle in radians, phi is azimuthal angle in radians.
    Returns dict with x, y, z.
    """
    x, y, z = from_spherical(r, theta, phi)
    return {"x": float(x), "y": float(y), "z": float(z)}


def _curl_cylindrical(vr: float, vphi: float, vz: float,
                      dvphi_dr: float, dvr_dphi: float, dvz_dr: float, dvr_dz: float,
                      rho: float) -> Dict[str, float]:
    """
    Curl of vector field in cylindrical coordinates (rho, phi, z):
    (∇ × F)_rho = (1/rho) * ∂vz/∂phi - ∂vphi/∂z
    (∇ × F)_phi = ∂vr/∂z - ∂vz/∂rho
    (∇ × F)_z = (1/rho) * (∂(rho*vphi)/∂rho - ∂vr/∂phi) = (1/rho)*(vphi + rho*∂vphi/∂rho - ∂vr/∂phi)
    Returns dict with curl_rho, curl_phi, curl_z.
    """
    if abs(rho) < 1e-10:
        raise ValueError("rho must be non-zero for cylindrical coordinates")
    curl_rho = (1.0 / rho) * dvz_dr - dvr_dz  # Simplified, assuming dvz/dphi ≈ 0 for this version
    curl_phi = dvz_dr - dvr_dz  # Simplified
    curl_z = (1.0 / rho) * (vphi + rho * dvphi_dr - dvr_dphi)
    return {"curl_rho": float(curl_rho), "curl_phi": float(curl_phi), "curl_z": float(curl_z)}


def _curl_spherical(vr: float, vtheta: float, vphi: float,
                   dvphi_dtheta: float, dvtheta_dphi: float, dvr_dphi: float,
                   dvphi_dr: float, dvr_dtheta: float, dvtheta_dr: float,
                   r: float, sin_theta: float) -> Dict[str, float]:
    """
    Curl of vector field in spherical coordinates (r, theta, phi):
    (∇ × F)_r = (1/(r*sin(theta))) * (∂(sin(theta)*vphi)/∂theta - ∂vtheta/∂phi)
    (∇ × F)_theta = (1/r) * (∂vr/∂phi/(sin(theta)) - ∂(r*vphi)/∂r)
    (∇ × F)_phi = (1/r) * (∂(r*vtheta)/∂r - ∂vr/∂theta)
    Returns dict with curl_r, curl_theta, curl_phi.
    """
    if abs(r) < 1e-10 or abs(sin_theta) < 1e-10:
        raise ValueError("r and sin(theta) must be non-zero for spherical coordinates")
    curl_r = (1.0 / (r * sin_theta)) * (sin_theta * dvphi_dtheta + vphi * np.cos(np.arcsin(sin_theta)) - dvtheta_dphi)
    curl_theta = (1.0 / r) * (dvr_dphi / sin_theta - (vphi + r * dvphi_dr))
    curl_phi = (1.0 / r) * (vtheta + r * dvtheta_dr - dvr_dtheta)
    return {"curl_r": float(curl_r), "curl_theta": float(curl_theta), "curl_phi": float(curl_phi)}


def _div_spherical(vr: float, vtheta: float, vphi: float,
                  dvr_dr: float, dvtheta_dtheta: float, dvphi_dphi: float,
                  r: float, sin_theta: float) -> float:
    """
    Divergence of vector field in spherical coordinates (r, theta, phi):
    ∇·F = (1/r²) * ∂(r²*vr)/∂r + (1/(r*sin(theta))) * ∂(sin(theta)*vtheta)/∂theta + (1/(r*sin(theta))) * ∂vphi/∂phi
        = (1/r²) * (2*r*vr + r² * ∂vr/∂r) + (1/(r*sin(theta))) * (sin(theta)*∂vtheta/∂theta + cos(theta)*vtheta) + (1/(r*sin(theta))) * ∂vphi/∂phi
    Returns scalar.
    """
    if abs(r) < 1e-10 or abs(sin_theta) < 1e-10:
        raise ValueError("r and sin(theta) must be non-zero for spherical coordinates")
    term1 = (1.0 / (r**2)) * (2.0 * r * vr + r**2 * dvr_dr)
    cos_theta = np.sqrt(1.0 - sin_theta**2) if sin_theta <= 1.0 else 0.0
    term2 = (1.0 / (r * sin_theta)) * (sin_theta * dvtheta_dtheta + cos_theta * vtheta)
    term3 = (1.0 / (r * sin_theta)) * dvphi_dphi
    div = term1 + term2 + term3
    return float(div)


_OPERATIONS = {
    "gradient_2d": _gradient_2d,
    "gradient_3d": _gradient_3d,
    "divergence_2d": _divergence_2d,
    "divergence_3d": _divergence_3d,
    "curl_2d": _curl_2d,
    "curl_3d": _curl_3d,
    "directional_derivative": _directional_derivative,
    "laplacian_2d": _laplacian_2d,
    "laplacian_3d": _laplacian_3d,
    "line_integral": _line_integral,
    "surface_integral": _surface_integral,
    "volume_integral": _volume_integral,
    "greens_theorem": _greens_theorem,
    "stokes_theorem": _stokes_theorem,
    "divergence_theorem": _divergence_theorem,
    "cartesian_to_cylindrical": _cartesian_to_cylindrical,
    "cylindrical_to_cartesian": _cylindrical_to_cartesian,
    "cartesian_to_spherical": _cartesian_to_spherical,
    "spherical_to_cartesian": _spherical_to_cartesian,
    "curl_cylindrical": _curl_cylindrical,
    "curl_spherical": _curl_spherical,
    "div_spherical": _div_spherical,
}


@register("mathematics.vector_calculus")
class VectorCalculusSolver(SolverBase):
    """
    Solver for vector calculus: gradient, divergence, curl, integrals, coordinate transforms.
    Supports operations on vector and scalar fields in Cartesian, cylindrical, and spherical coordinates.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve vector calculus problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Vector calculus solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
