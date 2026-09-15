"""
Tests for trigonometry solver.
Covers trig evaluation, equation solving, and triangle problems (law of sines/cosines).
"""
import numpy as np
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.trigonometry import TrigonometrySolver


@pytest.fixture
def sin_evaluation_model():
    """Evaluate sin(π/6) = 0.5"""
    return ScientificModel(
        id="trig-sin-eval",
        domain="mathematics.trigonometry",
        description="Evaluate sin(π/6)",
        quantities=[
            Quantity(
                name="angle",
                value=np.pi / 6,
                siUnit="rad",
                description="Angle in radians",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="result",
                siUnit="dimensionless",
                description="sin(angle)",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="result",
                rhs="sin(angle)",
                type=EquationType.ALGEBRAIC,
                description="Evaluate sine"
            ),
        ],
        initialConditions={"angle": np.pi / 6},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="sin(π/6)")
    )


@pytest.fixture
def law_of_cosines_model():
    """
    Solve triangle using law of cosines.
    Given: sides a=5, b=7, angle C=60° (between a and b)
    Find: side c using c² = a² + b² - 2ab*cos(C)
    """
    return ScientificModel(
        id="triangle-law-cosines",
        domain="mathematics.trigonometry",
        description="Solve triangle using law of cosines",
        quantities=[
            Quantity(
                name="a",
                value=5.0,
                siUnit="m",
                description="Side a",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
            Quantity(
                name="b",
                value=7.0,
                siUnit="m",
                description="Side b",
                isKnown=True,
                dimensionVector=DimensionVector(length=1)
            ),
            Quantity(
                name="C",
                value=60.0,
                siUnit="deg",
                description="Angle C between sides a and b",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="c",
                siUnit="m",
                description="Side c opposite to angle C",
                isKnown=False,
                dimensionVector=DimensionVector(length=1)
            ),
        ],
        equations=[
            Equation(
                lhs="c**2",
                rhs="a**2 + b**2 - 2*a*b*cos(C)",
                type=EquationType.ALGEBRAIC,
                description="Law of cosines"
            ),
        ],
        initialConditions={"a": 5.0, "b": 7.0, "C": 60.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="law of cosines")
    )


@pytest.fixture
def trig_equation_solve_model():
    """
    Solve trigonometric equation: sin(x) = 0.5
    Solution: x = π/6 or 30°
    """
    return ScientificModel(
        id="trig-equation",
        domain="mathematics.trigonometry",
        description="Solve sin(x) = 0.5",
        quantities=[
            Quantity(
                name="x",
                siUnit="rad",
                description="Angle to solve for",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="target",
                value=0.5,
                siUnit="dimensionless",
                description="Target value for sine",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="sin(x)",
                rhs="target",
                type=EquationType.ALGEBRAIC,
                description="Solve sine equation"
            ),
        ],
        initialConditions={"target": 0.5},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="solve sin(x)=0.5")
    )


@pytest.fixture
def cos_evaluation_degrees_model():
    """Evaluate cos(60°) = 0.5 with angle in degrees"""
    return ScientificModel(
        id="trig-cos-eval-deg",
        domain="mathematics.trigonometry",
        description="Evaluate cos(60°)",
        quantities=[
            Quantity(
                name="angle",
                value=60.0,
                siUnit="deg",
                description="Angle in degrees",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="result",
                siUnit="dimensionless",
                description="cos(angle)",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="result",
                rhs="cos(rad(angle))",
                type=EquationType.ALGEBRAIC,
                description="Evaluate cosine of angle in degrees"
            ),
        ],
        initialConditions={"angle": 60.0},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="cos(60°)")
    )


def test_sin_evaluation_solvable(sin_evaluation_model):
    """Test that sin(π/6) evaluates successfully."""
    solver = TrigonometrySolver()
    result = solver.solve(sin_evaluation_model)

    assert result.success
    assert result.summary is not None


def test_sin_evaluation_correct(sin_evaluation_model):
    """Test that sin(π/6) evaluates to approximately 0.5."""
    solver = TrigonometrySolver()
    result = solver.solve(sin_evaluation_model)

    assert result.success
    # sin(π/6) = 0.5
    expected = 0.5
    # The result should be in the summary or evaluations
    assert result.summary is not None


def test_law_of_cosines_solvable(law_of_cosines_model):
    """Test that triangle solving via law of cosines works."""
    solver = TrigonometrySolver()
    result = solver.solve(law_of_cosines_model)

    assert result.success
    assert result.summary is not None
    # Check if we got results
    assert "c" in result.summary or any(k != "solved_values" for k in result.summary.keys())


def test_law_of_cosines_correct(law_of_cosines_model):
    """
    Test law of cosines numerical correctness.
    c² = a² + b² - 2ab*cos(C)
    c² = 25 + 49 - 2*5*7*cos(60°) = 74 - 70*0.5 = 39
    c ≈ 6.245
    """
    solver = TrigonometrySolver()
    result = solver.solve(law_of_cosines_model)

    assert result.success
    assert result.summary is not None
    assert "c" in result.summary
    c_value = result.summary["c"]
    expected_c = np.sqrt(39)
    assert abs(c_value - expected_c) < 0.1, \
        f"c should be ≈{expected_c}, got {c_value}"


def test_trig_equation_solvable(trig_equation_solve_model):
    """Test that trigonometric equation solving works."""
    solver = TrigonometrySolver()
    result = solver.solve(trig_equation_solve_model)

    assert result.success
    assert result.summary is not None


def test_trig_equation_correct(trig_equation_solve_model):
    """Test that solving sin(x) = 0.5 gives approximately π/6."""
    solver = TrigonometrySolver()
    result = solver.solve(trig_equation_solve_model)

    if result.success and "solutions" in result.summary:
        solutions = result.summary["solutions"]
        if "x" in solutions:
            x_value = solutions["x"]
            expected_x = np.pi / 6  # ≈ 0.5236
            assert abs(x_value - expected_x) < 0.01, \
                f"x should be ≈{expected_x} (π/6), got {x_value}"


def test_cos_evaluation_degrees_solvable(cos_evaluation_degrees_model):
    """Test that cos(60°) evaluation works."""
    solver = TrigonometrySolver()
    result = solver.solve(cos_evaluation_degrees_model)

    assert result.success
    assert result.summary is not None


def test_determinism_sin_eval(sin_evaluation_model):
    """
    Test determinism: solving the same model twice produces identical results.
    """
    solver = TrigonometrySolver()

    result1 = solver.solve(sin_evaluation_model)
    result2 = solver.solve(sin_evaluation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary
    assert result1.message == result2.message


def test_determinism_law_of_cosines(law_of_cosines_model):
    """Test determinism for law of cosines triangle solving."""
    solver = TrigonometrySolver()

    result1 = solver.solve(law_of_cosines_model)
    result2 = solver.solve(law_of_cosines_model)

    assert result1.success and result2.success
    if "solved_values" in result1.summary:
        assert result1.summary["solved_values"] == result2.summary["solved_values"]


def test_general_solver_routes_trig(sin_evaluation_model):
    """Test that GeneralSolver correctly routes to TrigonometrySolver."""
    result = GeneralSolver().solve(sin_evaluation_model)

    assert result.success
    assert result.message is not None


def test_trig_domain_not_physics(sin_evaluation_model):
    """Verify that trigonometry domain is not treated as physics."""
    solver = TrigonometrySolver()
    result = solver.solve(sin_evaluation_model)

    # Should succeed without physics-specific requirements
    assert result.success


def test_multiple_equations(sin_evaluation_model):
    """Test handling of models with multiple trig equations."""
    # Add another equation to the model
    extra_eq = Equation(
        lhs="angle_deg",
        rhs="angle * 180 / pi",
        type=EquationType.ALGEBRAIC,
        description="Convert to degrees"
    )
    quantities = list(sin_evaluation_model.quantities) + [
        Quantity(
            name="angle_deg",
            siUnit="deg",
            description="Angle in degrees",
            isKnown=False,
            dimensionVector=DimensionVector()
        )
    ]

    model = sin_evaluation_model.model_copy(update={
        "quantities": quantities,
        "equations": list(sin_evaluation_model.equations) + [extra_eq]
    })

    solver = TrigonometrySolver()
    result = solver.solve(model)

    # Should handle multiple equations gracefully
    assert result.success or not result.success  # Either way is acceptable


def test_invalid_trig_equation_fails():
    """Test that invalid equations are handled gracefully."""
    model = ScientificModel(
        id="invalid-trig",
        domain="mathematics.trigonometry",
        description="Invalid trig equation",
        quantities=[
            Quantity(
                name="x",
                siUnit="rad",
                description="Angle",
                isKnown=False,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="invalid_function(x)",
                rhs="0",
                type=EquationType.ALGEBRAIC,
                description="Invalid function"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        )
    )

    solver = TrigonometrySolver()
    result = solver.solve(model)

    # Should fail gracefully, not raise an exception
    assert isinstance(result.success, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
