"""
Tests for complex number operations solver.
Includes fixtures for modulus, polar conversion, and roots of unity.
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.complex_numbers import ComplexNumbersSolver


@pytest.fixture
def modulus_model_3_4j():
    """Model for computing modulus of 3+4j, expected result: 5"""
    return ScientificModel(
        id="complex-modulus-3-4j",
        domain="mathematics.complex_numbers",
        description="Compute modulus of 3+4j",
        quantities=[
            Quantity(
                name="z",
                siUnit="dimensionless",
                description="Complex number z = 3+4j",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="modulus",
                rhs="modulus(z)",
                type=EquationType.ALGEBRAIC,
                description="Compute modulus of z"
            ),
        ],
        initialConditions={"z": {"real": 3.0, "imag": 4.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test", originalQuery="modulus of 3+4j")
    )


@pytest.fixture
def polar_model_1_1j():
    """Model for converting 1+1j to polar, expected: (√2, π/4)"""
    return ScientificModel(
        id="complex-polar-1-1j",
        domain="mathematics.complex_numbers",
        description="Convert 1+1j to polar form",
        quantities=[
            Quantity(
                name="z",
                siUnit="dimensionless",
                description="Complex number z = 1+1j",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="polar",
                rhs="rect_to_polar(z)",
                type=EquationType.ALGEBRAIC,
                description="Convert to polar form"
            ),
        ],
        initialConditions={"z": {"real": 1.0, "imag": 1.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test", originalQuery="polar form of 1+1j")
    )


@pytest.fixture
def cube_roots_of_unity():
    """Model for computing cube roots of 1, expected: three complex roots"""
    return ScientificModel(
        id="complex-cube-roots-unity",
        domain="mathematics.complex_numbers",
        description="Compute cube roots of unity",
        quantities=[
            Quantity(
                name="z",
                siUnit="dimensionless",
                description="Real number 1",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="n",
                value=3.0,
                siUnit="dimensionless",
                description="Root degree",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="roots",
                rhs="nth_root(z, n)",
                type=EquationType.ALGEBRAIC,
                description="Compute nth roots"
            ),
        ],
        initialConditions={"z": {"real": 1.0, "imag": 0.0}, "n": 3.0},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test", originalQuery="cube roots of 1")
    )


@pytest.fixture
def arithmetic_model_add():
    """Model for complex addition: (3+4j) + (1+2j)"""
    return ScientificModel(
        id="complex-add",
        domain="mathematics.complex_numbers",
        description="Add two complex numbers",
        quantities=[
            Quantity(name="z1", siUnit="dimensionless", isKnown=False),
            Quantity(name="z2", siUnit="dimensionless", isKnown=False),
        ],
        equations=[Equation(lhs="sum", rhs="add(z1, z2)", type=EquationType.ALGEBRAIC)],
        initialConditions={"z1": {"real": 3.0, "imag": 4.0}, "z2": {"real": 1.0, "imag": 2.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def arithmetic_model_multiply():
    """Model for complex multiplication: (2+3j) * (4+5j)"""
    return ScientificModel(
        id="complex-multiply",
        domain="mathematics.complex_numbers",
        description="Multiply two complex numbers",
        quantities=[
            Quantity(name="z1", siUnit="dimensionless", isKnown=False),
            Quantity(name="z2", siUnit="dimensionless", isKnown=False),
        ],
        equations=[Equation(lhs="product", rhs="multiply(z1, z2)", type=EquationType.ALGEBRAIC)],
        initialConditions={"z1": {"real": 2.0, "imag": 3.0}, "z2": {"real": 4.0, "imag": 5.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def polar_to_rect_model():
    """Model for polar to rectangular conversion: (2, π/4)"""
    return ScientificModel(
        id="complex-polar-to-rect",
        domain="mathematics.complex_numbers",
        description="Convert polar to rectangular",
        quantities=[
            Quantity(name="r", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="theta", value=np.pi / 4, siUnit="rad", isKnown=True),
        ],
        equations=[Equation(lhs="rect", rhs="polar_to_rect(r, theta)", type=EquationType.ALGEBRAIC)],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test")
    )


# Tests for specific operations

def test_modulus_3_4j_equals_5(modulus_model_3_4j):
    """Test that modulus of 3+4j equals 5."""
    solver = ComplexNumbersSolver()
    result = solver.solve(modulus_model_3_4j)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "modulus" in result.summary
    assert abs(result.summary["modulus"] - 5.0) < 1e-9


def test_polar_1_1j_magnitude(polar_model_1_1j):
    """Test that polar form of 1+1j has magnitude √2 ≈ 1.41421356."""
    solver = ComplexNumbersSolver()
    result = solver.solve(polar_model_1_1j)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "modulus" in result.summary
    expected_mag = np.sqrt(2)
    assert abs(result.summary["modulus"] - expected_mag) < 1e-9


def test_polar_1_1j_argument(polar_model_1_1j):
    """Test that polar form of 1+1j has argument π/4."""
    solver = ComplexNumbersSolver()
    result = solver.solve(polar_model_1_1j)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "argument" in result.summary
    expected_arg = np.pi / 4
    assert abs(result.summary["argument"] - expected_arg) < 1e-9


def test_cube_roots_of_unity_count(cube_roots_of_unity):
    """Test that cube roots of 1 produces 3 roots."""
    solver = ComplexNumbersSolver()
    result = solver.solve(cube_roots_of_unity)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "count" in result.summary
    assert result.summary["count"] == 3


def test_cube_roots_of_unity_first_root(cube_roots_of_unity):
    """Test that first cube root of 1 is 1 (with tolerance)."""
    solver = ComplexNumbersSolver()
    result = solver.solve(cube_roots_of_unity)

    assert result.success
    assert "roots" in result.summary
    roots = result.summary["roots"]
    assert len(roots) == 3

    # First root should be 1 (within tolerance)
    first_root = complex(roots[0]["real"], roots[0]["imag"])
    assert abs(first_root - 1.0) < 1e-9


def test_cube_roots_of_unity_product_is_one(cube_roots_of_unity):
    """Test that product of all cube roots of unity is -1 or 1 (depending on phase)."""
    solver = ComplexNumbersSolver()
    result = solver.solve(cube_roots_of_unity)

    assert result.success
    roots = result.summary["roots"]

    # Each root raised to power 3 should equal 1
    for i, root in enumerate(roots):
        z = complex(root["real"], root["imag"])
        z_cubed = z ** 3
        # Allow some numerical error
        assert abs(z_cubed - 1.0) < 1e-8, f"Root {i}: {z}^3 = {z_cubed}, not 1"


def test_complex_addition(arithmetic_model_add):
    """Test complex addition: (3+4j) + (1+2j) = (4+6j)"""
    solver = ComplexNumbersSolver()
    result = solver.solve(arithmetic_model_add)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "result" in result.summary
    res = result.summary["result"]
    assert abs(res["real"] - 4.0) < 1e-9
    assert abs(res["imag"] - 6.0) < 1e-9


def test_complex_multiplication(arithmetic_model_multiply):
    """Test complex multiplication: (2+3j) * (4+5j) = (8-15) + (10+12)j = -7+22j"""
    solver = ComplexNumbersSolver()
    result = solver.solve(arithmetic_model_multiply)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "result" in result.summary
    res = result.summary["result"]
    # (2+3j) * (4+5j) = 8 + 10j + 12j + 15j^2 = 8 + 22j - 15 = -7 + 22j
    assert abs(res["real"] - (-7.0)) < 1e-9
    assert abs(res["imag"] - 22.0) < 1e-9


def test_polar_to_rectangular(polar_to_rect_model):
    """Test conversion from polar (2, π/4) to rectangular (√2 + √2j)"""
    solver = ComplexNumbersSolver()
    result = solver.solve(polar_to_rect_model)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None
    assert "result" in result.summary
    res = result.summary["result"]

    # 2 * e^(iπ/4) = 2 * (cos(π/4) + i*sin(π/4)) = 2 * (√2/2 + i*√2/2) = √2 + i*√2
    expected_real = np.sqrt(2)
    expected_imag = np.sqrt(2)
    assert abs(res["real"] - expected_real) < 1e-9
    assert abs(res["imag"] - expected_imag) < 1e-9


def test_determinism_modulus(modulus_model_3_4j):
    """Test determinism: solving the same model twice produces identical results."""
    solver = ComplexNumbersSolver()

    result1 = solver.solve(modulus_model_3_4j)
    result2 = solver.solve(modulus_model_3_4j)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_roots(cube_roots_of_unity):
    """Test determinism for nth roots computation."""
    solver = ComplexNumbersSolver()

    result1 = solver.solve(cube_roots_of_unity)
    result2 = solver.solve(cube_roots_of_unity)

    assert result1.success and result2.success
    assert result1.summary["roots"] == result2.summary["roots"]


def test_general_solver_routes_complex_numbers(modulus_model_3_4j):
    """Test that GeneralSolver correctly routes to ComplexNumbersSolver."""
    general_solver = GeneralSolver()
    result = general_solver.solve(modulus_model_3_4j)

    assert result.success, f"Solver failed: {result.error}"
    assert result.summary is not None


def test_modulus_of_real_number():
    """Test modulus of a real number (should be its absolute value)."""
    model = ScientificModel(
        id="complex-modulus-real",
        domain="mathematics.complex_numbers",
        description="Modulus of real number -5",
        quantities=[
            Quantity(name="z", siUnit="dimensionless", isKnown=False),
        ],
        equations=[Equation(lhs="mag", rhs="modulus(z)", type=EquationType.ALGEBRAIC)],
        initialConditions={"z": -5.0},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
    )

    solver = ComplexNumbersSolver()
    result = solver.solve(model)

    assert result.success
    assert abs(result.summary["modulus"] - 5.0) < 1e-9


def test_division_of_complex_numbers():
    """Test complex division: (1+1j) / (1-1j) = 1j"""
    model = ScientificModel(
        id="complex-divide",
        domain="mathematics.complex_numbers",
        description="Divide complex numbers",
        quantities=[
            Quantity(name="z1", siUnit="dimensionless", isKnown=False),
            Quantity(name="z2", siUnit="dimensionless", isKnown=False),
        ],
        equations=[Equation(lhs="quotient", rhs="divide(z1, z2)", type=EquationType.ALGEBRAIC)],
        initialConditions={"z1": {"real": 1.0, "imag": 1.0}, "z2": {"real": 1.0, "imag": -1.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
    )

    solver = ComplexNumbersSolver()
    result = solver.solve(model)

    assert result.success
    res = result.summary["result"]
    # (1+i)/(1-i) = (1+i)²/((1-i)(1+i)) = (1+2i-1)/(1+1) = 2i/2 = i
    assert abs(res["real"]) < 1e-9
    assert abs(res["imag"] - 1.0) < 1e-9


def test_argument_of_negative_real():
    """Test argument of a negative real number (should be π or -π)."""
    model = ScientificModel(
        id="complex-arg-neg-real",
        domain="mathematics.complex_numbers",
        description="Argument of -1",
        quantities=[
            Quantity(name="z", siUnit="dimensionless", isKnown=False),
        ],
        equations=[Equation(lhs="arg", rhs="argument(z)", type=EquationType.ALGEBRAIC)],
        initialConditions={"z": {"real": -1.0, "imag": 0.0}},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
    )

    solver = ComplexNumbersSolver()
    result = solver.solve(model)

    assert result.success
    # np.angle(-1) returns π
    assert abs(abs(result.summary["argument"]) - np.pi) < 1e-9


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
