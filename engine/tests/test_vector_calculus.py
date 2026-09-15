"""Tests for vector calculus solver."""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.vector_calculus import VectorCalculusSolver
from app.solvers.utils import to_cylindrical, from_cylindrical, to_spherical, from_spherical


@pytest.fixture
def basic_model():
    """Basic model template for vector calculus."""
    return ScientificModel(
        id="vector-calc-test",
        domain="mathematics.vector_calculus",
        description="Vector calculus test",
        quantities=[],
        equations=[],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============ Coordinate Transform Tests ============

class TestCoordinateTransforms:
    """Test coordinate transform utility functions."""

    def test_cylindrical_transform_forward(self):
        """Test Cartesian to cylindrical conversion."""
        rho, phi = to_cylindrical(3.0, 4.0)
        assert abs(rho - 5.0) < 1e-10  # sqrt(9+16) = 5
        assert abs(phi - np.arctan2(4.0, 3.0)) < 1e-10

    def test_cylindrical_transform_reverse(self):
        """Test cylindrical to Cartesian conversion."""
        x, y = from_cylindrical(5.0, np.arctan2(4.0, 3.0))
        assert abs(x - 3.0) < 1e-10
        assert abs(y - 4.0) < 1e-10

    def test_cylindrical_transform_roundtrip(self):
        """Test roundtrip Cartesian → cylindrical → Cartesian."""
        x_orig, y_orig = 7.5, 2.3
        rho, phi = to_cylindrical(x_orig, y_orig)
        x_new, y_new = from_cylindrical(rho, phi)
        assert abs(x_new - x_orig) < 1e-10
        assert abs(y_new - y_orig) < 1e-10

    def test_spherical_transform_forward(self):
        """Test Cartesian to spherical conversion."""
        # Point (1, 1, 1): r = sqrt(3), theta = arccos(1/sqrt(3)), phi = pi/4
        r, theta, phi = to_spherical(1.0, 1.0, 1.0)
        assert abs(r - np.sqrt(3.0)) < 1e-10
        assert abs(theta - np.arccos(1.0 / np.sqrt(3.0))) < 1e-10
        assert abs(phi - np.pi / 4.0) < 1e-10

    def test_spherical_transform_reverse(self):
        """Test spherical to Cartesian conversion."""
        r, theta, phi = np.sqrt(3.0), np.arccos(1.0 / np.sqrt(3.0)), np.pi / 4.0
        x, y, z = from_spherical(r, theta, phi)
        assert abs(x - 1.0) < 1e-10
        assert abs(y - 1.0) < 1e-10
        assert abs(z - 1.0) < 1e-10

    def test_spherical_transform_roundtrip(self):
        """Test roundtrip Cartesian → spherical → Cartesian."""
        x_orig, y_orig, z_orig = 2.1, 3.5, 1.2
        r, theta, phi = to_spherical(x_orig, y_orig, z_orig)
        x_new, y_new, z_new = from_spherical(r, theta, phi)
        assert abs(x_new - x_orig) < 1e-10
        assert abs(y_new - y_orig) < 1e-10
        assert abs(z_new - z_orig) < 1e-10

    def test_spherical_origin_error(self):
        """Test that spherical conversion fails for origin."""
        with pytest.raises(ValueError, match="Cannot convert"):
            to_spherical(0.0, 0.0, 0.0)


# ============ Gradient Tests ============

class TestGradient:
    """Test gradient operations."""

    def test_gradient_2d_solvable(self, basic_model):
        """Test that gradient_2d solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="grad", rhs="gradient_2d(fx, fy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "grad_grad_x" in result.summary
        assert "grad_grad_y" in result.summary

    def test_gradient_3d_solvable(self, basic_model):
        """Test that gradient_3d solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fz", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dz", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="grad", rhs="gradient_3d(fx, fy, fz, dx, dy, dz)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "grad_grad_x" in result.summary
        assert "grad_grad_y" in result.summary
        assert "grad_grad_z" in result.summary


# ============ Divergence Tests ============

class TestDivergence:
    """Test divergence operations."""

    def test_divergence_2d_solvable(self, basic_model):
        """Test that divergence_2d solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="vx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="vy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="div", rhs="divergence_2d(vx, vy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "div" in result.summary

    def test_divergence_2d_correctness(self, basic_model):
        """Test divergence_2d correctness: ∇·F = ∂vx/∂x + ∂vy/∂y."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="vx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="vy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="div", rhs="divergence_2d(vx, vy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        expected = 2.0 / 0.1 + 3.0 / 0.1  # 20 + 30 = 50
        assert abs(result.summary["div"] - expected) < 1e-6


# ============ Curl Tests ============

class TestCurl:
    """Test curl operations."""

    def test_curl_2d_solvable(self, basic_model):
        """Test that curl_2d solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="vx", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="vy", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="curl", rhs="curl_2d(vx, vy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "curl" in result.summary

    def test_curl_2d_correctness(self, basic_model):
        """Test curl_2d correctness: (∇ × F)_z = ∂vy/∂x - ∂vx/∂y."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="vx", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="vy", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="curl", rhs="curl_2d(vx, vy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        expected = 2.0 / 0.1 - 1.0 / 0.1  # 20 - 10 = 10
        assert abs(result.summary["curl"] - expected) < 1e-6


# ============ Laplacian Tests ============

class TestLaplacian:
    """Test Laplacian operations."""

    def test_laplacian_2d_solvable(self, basic_model):
        """Test that laplacian_2d solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fxx", value=4.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fyy", value=2.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="laplacian", rhs="laplacian_2d(fxx, fyy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "laplacian" in result.summary

    def test_laplacian_2d_correctness(self, basic_model):
        """Test laplacian_2d correctness: ∇²f = ∂²f/∂x² + ∂²f/∂y²."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fxx", value=4.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fyy", value=2.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="laplacian", rhs="laplacian_2d(fxx, fyy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        expected = 4.0 + 2.0  # 6.0
        assert abs(result.summary["laplacian"] - expected) < 1e-6


# ============ Integral Tests ============

class TestIntegrals:
    """Test integral operations."""

    def test_line_integral_solvable(self, basic_model):
        """Test that line_integral solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx_start", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fx_end", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy_start", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy_end", value=4.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="x_start", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="x_end", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y_start", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y_end", value=1.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="line_integral(fx_start, fx_end, fy_start, fy_end, x_start, x_end, y_start, y_end)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "integral" in result.summary

    def test_surface_integral_solvable(self, basic_model):
        """Test that surface_integral solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx_avg", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy_avg", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fz_avg", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="area", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="nx", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="ny", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="nz", value=0.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="surface_integral(fx_avg, fy_avg, fz_avg, area, nx, ny, nz)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "integral" in result.summary

    def test_volume_integral_solvable(self, basic_model):
        """Test that volume_integral solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="f_avg", value=2.5, siUnit="dimensionless", isKnown=True),
                Quantity(name="volume", value=4.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="volume_integral(f_avg, volume)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "integral" in result.summary

    def test_volume_integral_correctness(self, basic_model):
        """Test volume_integral correctness: ∫∫∫ f dV ≈ f_avg * Volume."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="f_avg", value=2.5, siUnit="dimensionless", isKnown=True),
                Quantity(name="volume", value=4.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="volume_integral(f_avg, volume)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        expected = 2.5 * 4.0  # 10.0
        assert abs(result.summary["integral"] - expected) < 1e-6


# ============ Theorem Tests ============

class TestTheorems:
    """Test Green's theorem, Stokes' theorem, divergence theorem."""

    def test_greens_theorem_solvable(self, basic_model):
        """Test that greens_theorem solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="line_pdx", value=5.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="line_qdy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dq_dx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dp_dy", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="area", value=2.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="greens", rhs="greens_theorem(line_pdx, line_qdy, dq_dx, dp_dy, area)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "greens_line_integral_lhs" in result.summary
        assert "greens_surface_integral_rhs" in result.summary

    def test_stokes_theorem_solvable(self, basic_model):
        """Test that stokes_theorem solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="line_integral", value=4.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="curl_z", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="area", value=2.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="stokes", rhs="stokes_theorem(line_integral, curl_z, area)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "stokes_line_integral_lhs" in result.summary
        assert "stokes_surface_integral_rhs" in result.summary

    def test_divergence_theorem_solvable(self, basic_model):
        """Test that divergence_theorem solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="surface_integral", value=6.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="div_f", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="volume", value=2.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="div_th", rhs="divergence_theorem(surface_integral, div_f, volume)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "div_th_surface_integral_lhs" in result.summary
        assert "div_th_volume_integral_rhs" in result.summary


# ============ Coordinate Transform Operation Tests ============

class TestCoordinateTransformOperations:
    """Test coordinate transform solver operations."""

    def test_cartesian_to_cylindrical_solvable(self, basic_model):
        """Test that cartesian_to_cylindrical solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="x", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y", value=4.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="cyl", rhs="cartesian_to_cylindrical(x, y)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "cyl_rho" in result.summary
        assert "cyl_phi" in result.summary

    def test_cartesian_to_cylindrical_correctness(self, basic_model):
        """Test cartesian_to_cylindrical correctness."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="x", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y", value=4.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="cyl", rhs="cartesian_to_cylindrical(x, y)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert abs(result.summary["cyl_rho"] - 5.0) < 1e-6  # sqrt(9+16)
        assert abs(result.summary["cyl_phi"] - np.arctan2(4.0, 3.0)) < 1e-6

    def test_cylindrical_to_cartesian_solvable(self, basic_model):
        """Test that cylindrical_to_cartesian solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="rho", value=5.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="phi", value=np.arctan2(4.0, 3.0), siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="cart", rhs="cylindrical_to_cartesian(rho, phi)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "cart_x" in result.summary
        assert "cart_y" in result.summary

    def test_cartesian_to_spherical_solvable(self, basic_model):
        """Test that cartesian_to_spherical solves successfully."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="x", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="z", value=1.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="sph", rhs="cartesian_to_spherical(x, y, z)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "sph_r" in result.summary
        assert "sph_theta" in result.summary
        assert "sph_phi" in result.summary

    def test_spherical_to_cartesian_solvable(self, basic_model):
        """Test that spherical_to_cartesian solves successfully."""
        r, theta, phi = np.sqrt(3.0), np.arccos(1.0 / np.sqrt(3.0)), np.pi / 4.0
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="r", value=r, siUnit="dimensionless", isKnown=True),
                Quantity(name="theta", value=theta, siUnit="dimensionless", isKnown=True),
                Quantity(name="phi", value=phi, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="cart", rhs="spherical_to_cartesian(r, theta, phi)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert result.success
        assert "cart_x" in result.summary
        assert "cart_y" in result.summary
        assert "cart_z" in result.summary


# ============ Determinism Tests ============

class TestDeterminism:
    """Test determinism: solving same model twice produces identical results."""

    def test_determinism_gradient(self, basic_model):
        """Test determinism for gradient_2d."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="grad", rhs="gradient_2d(fx, fy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        solver = VectorCalculusSolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)
        assert result1.success and result2.success
        assert result1.summary == result2.summary

    def test_determinism_divergence(self, basic_model):
        """Test determinism for divergence_2d."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="vx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="vy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="div", rhs="divergence_2d(vx, vy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        solver = VectorCalculusSolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)
        assert result1.success and result2.success
        assert result1.summary == result2.summary

    def test_determinism_transforms(self, basic_model):
        """Test determinism for coordinate transforms."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="x", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="y", value=4.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="cyl", rhs="cartesian_to_cylindrical(x, y)", type=EquationType.ALGEBRAIC)],
        })
        solver = VectorCalculusSolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)
        assert result1.success and result2.success
        assert result1.summary == result2.summary


# ============ Error Path Tests ============

class TestErrorPaths:
    """Test error handling for invalid inputs."""

    def test_error_zero_grid_spacing(self, basic_model):
        """Test error for zero grid spacing."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="grad", rhs="gradient_2d(fx, fy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert not result.success
        assert "Grid spacings" in result.error

    def test_error_zero_area(self, basic_model):
        """Test error for zero area in surface integral."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx_avg", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy_avg", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fz_avg", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="area", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="nx", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="ny", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="nz", value=0.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="surface_integral(fx_avg, fy_avg, fz_avg, area, nx, ny, nz)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert not result.success
        assert "area must be positive" in result.error.lower()

    def test_error_zero_volume(self, basic_model):
        """Test error for zero volume in volume integral."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="f_avg", value=2.5, siUnit="dimensionless", isKnown=True),
                Quantity(name="volume", value=0.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="integral", rhs="volume_integral(f_avg, volume)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert not result.success
        assert "Volume must be positive" in result.error

    def test_error_zero_direction_vector(self, basic_model):
        """Test error for zero direction vector in directional derivative."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="grad_x", value=1.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="grad_y", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="u_x", value=0.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="u_y", value=0.0, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="d_u", rhs="directional_derivative(grad_x, grad_y, u_x, u_y)", type=EquationType.ALGEBRAIC)],
        })
        result = VectorCalculusSolver().solve(model)
        assert not result.success
        assert "Direction vector u must be non-zero" in result.error


# ============ Routing Tests ============

class TestRouting:
    """Test that GeneralSolver routes to VectorCalculusSolver."""

    def test_general_solver_routes_vector_calculus(self, basic_model):
        """Test that GeneralSolver routes to vector calculus solver."""
        model = basic_model.model_copy(update={
            "quantities": [
                Quantity(name="fx", value=2.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="fy", value=3.0, siUnit="dimensionless", isKnown=True),
                Quantity(name="dx", value=0.1, siUnit="dimensionless", isKnown=True),
                Quantity(name="dy", value=0.1, siUnit="dimensionless", isKnown=True),
            ],
            "equations": [Equation(lhs="grad", rhs="gradient_2d(fx, fy, dx, dy)", type=EquationType.ALGEBRAIC)],
        })
        result = GeneralSolver().solve(model)
        assert result.success
        assert "grad_grad_x" in result.summary
