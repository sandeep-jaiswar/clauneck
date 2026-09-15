"""
Tests for number theory solver.
Golden-file tests for determinism: same model → same output.
"""
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.number_theory import NumberTheorySolver


@pytest.fixture
def gcd_model():
    """GCD operation model: gcd(12, 18) = 6."""
    return ScientificModel(
        id="gcd-test",
        domain="mathematics.number_theory",
        description="Greatest common divisor of 12 and 18",
        quantities=[
            Quantity(
                name="a",
                value=12.0,
                siUnit="integer",
                description="First number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="b",
                value=18.0,
                siUnit="integer",
                description="Second number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="gcd(a, b)",
                rhs="gcd(12, 18)",
                type=EquationType.ALGEBRAIC,
                description="GCD operation"
            ),
        ],
        initialConditions={"a": 12.0, "b": 18.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="gcd of 12 and 18")
    )


@pytest.fixture
def ncr_model():
    """Combination operation model: nCr(5, 2) = 10."""
    return ScientificModel(
        id="ncr-test",
        domain="mathematics.number_theory",
        description="Combination: 5 choose 2",
        quantities=[
            Quantity(
                name="n",
                value=5.0,
                siUnit="integer",
                description="Total items",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="r",
                value=2.0,
                siUnit="integer",
                description="Items to choose",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="nCr(n, r)",
                rhs="C(5, 2)",
                type=EquationType.ALGEBRAIC,
                description="Combination operation"
            ),
        ],
        initialConditions={"n": 5.0, "r": 2.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="5 choose 2")
    )


@pytest.fixture
def prime_factors_model():
    """Prime factorization model: factors of 30 = [2, 3, 5]."""
    return ScientificModel(
        id="prime-factors-test",
        domain="mathematics.number_theory",
        description="Prime factorization of 30",
        quantities=[
            Quantity(
                name="n",
                value=30.0,
                siUnit="integer",
                description="Number to factor",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="prime_factors(n)",
                rhs="factors of 30",
                type=EquationType.ALGEBRAIC,
                description="Prime factorization"
            ),
        ],
        initialConditions={"n": 30.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="prime factorization of 30")
    )


@pytest.fixture
def lcm_model():
    """LCM operation model: lcm(12, 18) = 36."""
    return ScientificModel(
        id="lcm-test",
        domain="mathematics.number_theory",
        description="Least common multiple of 12 and 18",
        quantities=[
            Quantity(
                name="a",
                value=12.0,
                siUnit="integer",
                description="First number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="b",
                value=18.0,
                siUnit="integer",
                description="Second number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="lcm(a, b)",
                rhs="lcm(12, 18)",
                type=EquationType.ALGEBRAIC,
                description="LCM operation"
            ),
        ],
        initialConditions={"a": 12.0, "b": 18.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="lcm of 12 and 18")
    )


@pytest.fixture
def is_prime_model():
    """Primality test model: is_prime(17) = True."""
    return ScientificModel(
        id="is-prime-test",
        domain="mathematics.number_theory",
        description="Check if 17 is prime",
        quantities=[
            Quantity(
                name="n",
                value=17.0,
                siUnit="integer",
                description="Number to test",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="is_prime(n)",
                rhs="primality test",
                type=EquationType.ALGEBRAIC,
                description="Primality test"
            ),
        ],
        initialConditions={"n": 17.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="is 17 prime")
    )


@pytest.fixture
def npr_model():
    """Permutation model: nPr(5, 2) = 20."""
    return ScientificModel(
        id="npr-test",
        domain="mathematics.number_theory",
        description="Permutation: 5 permute 2",
        quantities=[
            Quantity(
                name="n",
                value=5.0,
                siUnit="integer",
                description="Total items",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="r",
                value=2.0,
                siUnit="integer",
                description="Items to arrange",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="nPr(n, r)",
                rhs="P(5, 2)",
                type=EquationType.ALGEBRAIC,
                description="Permutation operation"
            ),
        ],
        initialConditions={"n": 5.0, "r": 2.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-10
        ),
        metadata=Metadata(source="test", originalQuery="5 permute 2")
    )


def test_gcd_solvable(gcd_model):
    """Test that GCD operation solves successfully."""
    solver = NumberTheorySolver()
    result = solver.solve(gcd_model)

    assert result.success
    assert result.summary is not None
    assert "gcd(a, b)" in result.summary
    assert result.summary["gcd(a, b)"] == 6


def test_gcd_correct_result(gcd_model):
    """Test that GCD computation is correct: gcd(12, 18) = 6."""
    solver = NumberTheorySolver()
    result = solver.solve(gcd_model)

    assert result.success
    assert result.summary["gcd(a, b)"] == 6


def test_ncr_solvable(ncr_model):
    """Test that nCr operation solves successfully."""
    solver = NumberTheorySolver()
    result = solver.solve(ncr_model)

    assert result.success
    assert result.summary is not None
    assert "nCr(n, r)" in result.summary
    assert result.summary["nCr(n, r)"] == 10


def test_ncr_correct_result(ncr_model):
    """Test that nCr computation is correct: nCr(5, 2) = 10."""
    solver = NumberTheorySolver()
    result = solver.solve(ncr_model)

    assert result.success
    assert result.summary["nCr(n, r)"] == 10


def test_prime_factors_solvable(prime_factors_model):
    """Test that prime factorization solves successfully."""
    solver = NumberTheorySolver()
    result = solver.solve(prime_factors_model)

    assert result.success
    assert result.summary is not None
    assert "prime_factors(n)" in result.summary


def test_prime_factors_correct_result(prime_factors_model):
    """Test that prime factorization is correct: factors of 30 = [2, 3, 5]."""
    solver = NumberTheorySolver()
    result = solver.solve(prime_factors_model)

    assert result.success
    assert result.summary["prime_factors(n)"] == [2, 3, 5]


def test_lcm_correct_result(lcm_model):
    """Test that LCM computation is correct: lcm(12, 18) = 36."""
    solver = NumberTheorySolver()
    result = solver.solve(lcm_model)

    assert result.success
    assert result.summary["lcm(a, b)"] == 36


def test_is_prime_true(is_prime_model):
    """Test that primality test returns True for prime number."""
    solver = NumberTheorySolver()
    result = solver.solve(is_prime_model)

    assert result.success
    assert result.summary["is_prime(n)"] is True


def test_is_prime_false():
    """Test that primality test returns False for non-prime number."""
    model = ScientificModel(
        id="is-prime-false-test",
        domain="mathematics.number_theory",
        description="Check if 18 is prime",
        quantities=[
            Quantity(
                name="n",
                value=18.0,
                siUnit="integer",
                description="Number to test",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="is_prime(n)",
                rhs="primality test",
                type=EquationType.ALGEBRAIC
            ),
        ],
        initialConditions={"n": 18.0},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test")
    )

    solver = NumberTheorySolver()
    result = solver.solve(model)

    assert result.success
    assert result.summary["is_prime(n)"] is False


def test_npr_correct_result(npr_model):
    """Test that nPr computation is correct: nPr(5, 2) = 20."""
    solver = NumberTheorySolver()
    result = solver.solve(npr_model)

    assert result.success
    assert result.summary["nPr(n, r)"] == 20


def test_determinism_gcd(gcd_model):
    """
    Test determinism: solving the same GCD model twice produces identical results.
    Golden-file test: byte-identical output.
    """
    solver = NumberTheorySolver()

    result1 = solver.solve(gcd_model)
    result2 = solver.solve(gcd_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary
    assert result1.summary["gcd(a, b)"] == 6


def test_determinism_ncr(ncr_model):
    """Test determinism for nCr operation."""
    solver = NumberTheorySolver()

    result1 = solver.solve(ncr_model)
    result2 = solver.solve(ncr_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_prime_factors(prime_factors_model):
    """Test determinism for prime factorization."""
    solver = NumberTheorySolver()

    result1 = solver.solve(prime_factors_model)
    result2 = solver.solve(prime_factors_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_general_solver_routes_gcd(gcd_model):
    """Test that GeneralSolver routes to NumberTheorySolver for mathematics.number_theory domain."""
    result = GeneralSolver().solve(gcd_model)

    assert result.success
    assert result.summary["gcd(a, b)"] == 6


def test_general_solver_routes_ncr(ncr_model):
    """Test that GeneralSolver routes to NumberTheorySolver for nCr operation."""
    result = GeneralSolver().solve(ncr_model)

    assert result.success
    assert result.summary["nCr(n, r)"] == 10


def test_general_solver_routes_prime_factors(prime_factors_model):
    """Test that GeneralSolver routes to NumberTheorySolver for prime factorization."""
    result = GeneralSolver().solve(prime_factors_model)

    assert result.success
    assert result.summary["prime_factors(n)"] == [2, 3, 5]


def test_multiple_operations():
    """Test model with multiple number theory operations."""
    model = ScientificModel(
        id="multi-op-test",
        domain="mathematics.number_theory",
        description="Multiple number theory operations",
        quantities=[
            Quantity(
                name="a",
                value=12.0,
                siUnit="integer",
                description="First number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="b",
                value=18.0,
                siUnit="integer",
                description="Second number",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="gcd(a, b)",
                rhs="gcd(12, 18)",
                type=EquationType.ALGEBRAIC
            ),
            Equation(
                lhs="lcm(a, b)",
                rhs="lcm(12, 18)",
                type=EquationType.ALGEBRAIC
            ),
        ],
        initialConditions={"a": 12.0, "b": 18.0},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-10),
        metadata=Metadata(source="test")
    )

    result = GeneralSolver().solve(model)

    assert result.success
    assert result.summary["gcd(a, b)"] == 6
    assert result.summary["lcm(a, b)"] == 36


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
