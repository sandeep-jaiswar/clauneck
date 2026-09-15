"""
Tests for probability theory solver.
Covers Bayes' theorem, distributions, moments, and Markov chains.
"""
import numpy as np
import pytest
from scipy import stats as scipy_stats

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.probability import ProbabilitySolver


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def bayes_theorem_model():
    """Model for Bayes' theorem calculation."""
    return ScientificModel(
        id="prob-bayes",
        domain="mathematics.probability",
        description="Bayes theorem: P(disease|positive test)",
        quantities=[
            Quantity(name="prior", value=0.01, siUnit="dimensionless", isKnown=True),
            Quantity(name="likelihood", value=0.95, siUnit="dimensionless", isKnown=True),
            Quantity(name="evidence", value=0.0595, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="posterior",
                rhs="bayes_theorem(0.01, 0.95, 0.0595)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def conditional_prob_model():
    """Model for conditional probability calculation."""
    return ScientificModel(
        id="prob-conditional",
        domain="mathematics.probability",
        description="Conditional probability: P(A|B) = P(A,B) / P(B)",
        quantities=[
            Quantity(name="joint", value=0.2, siUnit="dimensionless", isKnown=True),
            Quantity(name="marginal", value=0.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="conditional",
                rhs="conditional_probability(0.2, 0.5)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def joint_prob_model():
    """Model for joint probability (independent events)."""
    return ScientificModel(
        id="prob-joint",
        domain="mathematics.probability",
        description="Joint probability of independent events",
        quantities=[
            Quantity(name="p_a", value=0.3, siUnit="dimensionless", isKnown=True),
            Quantity(name="p_b", value=0.4, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="joint",
                rhs="joint_probability(0.3, 0.4)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def expectation_model():
    """Model for computing expectation."""
    return ScientificModel(
        id="prob-expectation",
        domain="mathematics.probability",
        description="Expectation of discrete random variable",
        quantities=[
            Quantity(
                name="values",
                value=[1, 2, 3, 4, 5],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="probs",
                value=[0.1, 0.2, 0.4, 0.2, 0.1],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="expected_value",
                rhs="expectation(values, probs)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def variance_model():
    """Model for computing variance."""
    return ScientificModel(
        id="prob-variance",
        domain="mathematics.probability",
        description="Variance of discrete random variable",
        quantities=[
            Quantity(
                name="values",
                value=[1, 2, 3, 4, 5],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="probs",
                value=[0.1, 0.2, 0.4, 0.2, 0.1],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="variance_result",
                rhs="variance(values, probs)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def normal_pdf_model():
    """Model for normal distribution PDF."""
    return ScientificModel(
        id="prob-normal-pdf",
        domain="mathematics.probability",
        description="Normal distribution PDF",
        quantities=[
            Quantity(name="x", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="mu", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="sigma", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="pdf_result",
                rhs="normal_pdf(0.0, 0.0, 1.0)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def normal_cdf_model():
    """Model for normal distribution CDF."""
    return ScientificModel(
        id="prob-normal-cdf",
        domain="mathematics.probability",
        description="Normal distribution CDF",
        quantities=[
            Quantity(name="x", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="mu", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="sigma", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="cdf_result",
                rhs="normal_cdf(1.0, 0.0, 1.0)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def binomial_pdf_model():
    """Model for binomial distribution PDF."""
    return ScientificModel(
        id="prob-binomial-pdf",
        domain="mathematics.probability",
        description="Binomial distribution PDF",
        quantities=[
            Quantity(name="k", value=5.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="p", value=0.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="binomial_result",
                rhs="binomial_pdf(5, 10, 0.5)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def poisson_pdf_model():
    """Model for Poisson distribution PDF."""
    return ScientificModel(
        id="prob-poisson-pdf",
        domain="mathematics.probability",
        description="Poisson distribution PDF",
        quantities=[
            Quantity(name="k", value=3.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="lam", value=2.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="poisson_result",
                rhs="poisson_pdf(3, 2.5)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def exponential_pdf_model():
    """Model for exponential distribution PDF."""
    return ScientificModel(
        id="prob-exponential-pdf",
        domain="mathematics.probability",
        description="Exponential distribution PDF",
        quantities=[
            Quantity(name="x", value=2.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="lam", value=0.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="exp_result",
                rhs="exponential_pdf(2.0, 0.5)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def markov_transition_model():
    """Model for Markov chain transition."""
    return ScientificModel(
        id="prob-markov",
        domain="mathematics.probability",
        description="Markov chain state transition",
        quantities=[
            Quantity(
                name="state_probs",
                value=[0.6, 0.4],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="transition",
                value=[[0.7, 0.3], [0.4, 0.6]],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="next_state",
                rhs="markov_transition_matrix(state_probs, transition)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# ============================================================================
# SECTION 1: CORRECTNESS TESTS
# ============================================================================

def test_bayes_theorem_correctness(bayes_theorem_model):
    """Test Bayes' theorem correctness."""
    solver = ProbabilitySolver()
    result = solver.solve(bayes_theorem_model)

    assert result.success
    expected_posterior = (0.95 * 0.01) / 0.0595  # ≈ 0.1597
    actual_posterior = result.summary["posterior"]
    assert abs(actual_posterior - expected_posterior) < 1e-6


def test_conditional_probability_correctness(conditional_prob_model):
    """Test conditional probability calculation."""
    solver = ProbabilitySolver()
    result = solver.solve(conditional_prob_model)

    assert result.success
    expected_cond = 0.2 / 0.5  # = 0.4
    actual_cond = result.summary["conditional"]
    assert abs(actual_cond - expected_cond) < 1e-6


def test_joint_probability_correctness(joint_prob_model):
    """Test joint probability of independent events."""
    solver = ProbabilitySolver()
    result = solver.solve(joint_prob_model)

    assert result.success
    expected_joint = 0.3 * 0.4  # = 0.12
    actual_joint = result.summary["joint"]
    assert abs(actual_joint - expected_joint) < 1e-6


def test_expectation_correctness(expectation_model):
    """Test expectation calculation."""
    solver = ProbabilitySolver()
    result = solver.solve(expectation_model)

    assert result.success
    values = np.array([1, 2, 3, 4, 5])
    probs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
    expected_e = np.sum(values * probs)  # = 3.0
    actual_e = result.summary["expected_value"]
    assert abs(actual_e - expected_e) < 1e-6


def test_variance_correctness(variance_model):
    """Test variance calculation."""
    solver = ProbabilitySolver()
    result = solver.solve(variance_model)

    assert result.success
    values = np.array([1, 2, 3, 4, 5])
    probs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
    mean = np.sum(values * probs)
    expected_var = np.sum((values ** 2) * probs) - (mean ** 2)  # = 1.0
    actual_var = result.summary["variance_result"]
    assert abs(actual_var - expected_var) < 1e-6


def test_normal_pdf_at_mean(normal_pdf_model):
    """Test normal PDF at mean (x = mu)."""
    solver = ProbabilitySolver()
    result = solver.solve(normal_pdf_model)

    assert result.success
    # PDF at x=mu (0) with sigma=1 should be ≈ 0.3989
    expected_pdf = 1.0 / (1.0 * np.sqrt(2 * np.pi))
    actual_pdf = result.summary["pdf_result"]
    assert abs(actual_pdf - expected_pdf) < 1e-6


def test_normal_cdf_correctness(normal_cdf_model):
    """Test normal CDF correctness."""
    solver = ProbabilitySolver()
    result = solver.solve(normal_cdf_model)

    assert result.success
    expected_cdf = scipy_stats.norm.cdf(1.0, loc=0.0, scale=1.0)  # ≈ 0.8413
    actual_cdf = result.summary["cdf_result"]
    assert abs(actual_cdf - expected_cdf) < 1e-6


def test_binomial_pdf_correctness(binomial_pdf_model):
    """Test binomial PDF correctness."""
    solver = ProbabilitySolver()
    result = solver.solve(binomial_pdf_model)

    assert result.success
    expected_pmf = scipy_stats.binom.pmf(5, 10, 0.5)
    actual_pmf = result.summary["binomial_result"]
    assert abs(actual_pmf - expected_pmf) < 1e-6


def test_poisson_pdf_correctness(poisson_pdf_model):
    """Test Poisson PDF correctness."""
    solver = ProbabilitySolver()
    result = solver.solve(poisson_pdf_model)

    assert result.success
    expected_pmf = scipy_stats.poisson.pmf(3, 2.5)
    actual_pmf = result.summary["poisson_result"]
    assert abs(actual_pmf - expected_pmf) < 1e-6


def test_exponential_pdf_correctness(exponential_pdf_model):
    """Test exponential PDF correctness."""
    solver = ProbabilitySolver()
    result = solver.solve(exponential_pdf_model)

    assert result.success
    expected_pdf = scipy_stats.expon.pdf(2.0, scale=1/0.5)
    actual_pdf = result.summary["exp_result"]
    assert abs(actual_pdf - expected_pdf) < 1e-6


def test_binomial_cdf_correctness():
    """Test binomial CDF correctness."""
    model = ScientificModel(
        id="prob-binomial-cdf",
        domain="mathematics.probability",
        description="Binomial distribution CDF",
        quantities=[
            Quantity(name="k", value=7.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="p", value=0.6, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="binomial_cdf_result",
                rhs="binomial_cdf(7, 10, 0.6)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ProbabilitySolver()
    result = solver.solve(model)

    assert result.success
    expected_cdf = scipy_stats.binom.cdf(7, 10, 0.6)
    actual_cdf = result.summary["binomial_cdf_result"]
    assert abs(actual_cdf - expected_cdf) < 1e-6


def test_poisson_cdf_correctness():
    """Test Poisson CDF correctness."""
    model = ScientificModel(
        id="prob-poisson-cdf",
        domain="mathematics.probability",
        description="Poisson distribution CDF",
        quantities=[
            Quantity(name="k", value=5.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="lam", value=3.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="poisson_cdf_result",
                rhs="poisson_cdf(5, 3.0)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ProbabilitySolver()
    result = solver.solve(model)

    assert result.success
    expected_cdf = scipy_stats.poisson.cdf(5, 3.0)
    actual_cdf = result.summary["poisson_cdf_result"]
    assert abs(actual_cdf - expected_cdf) < 1e-6


def test_exponential_cdf_correctness():
    """Test exponential CDF correctness."""
    model = ScientificModel(
        id="prob-exponential-cdf",
        domain="mathematics.probability",
        description="Exponential distribution CDF",
        quantities=[
            Quantity(name="x", value=1.5, siUnit="dimensionless", isKnown=True),
            Quantity(name="lam", value=0.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="exp_cdf_result",
                rhs="exponential_cdf(1.5, 0.5)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ProbabilitySolver()
    result = solver.solve(model)

    assert result.success
    expected_cdf = scipy_stats.expon.cdf(1.5, scale=1/0.5)
    actual_cdf = result.summary["exp_cdf_result"]
    assert abs(actual_cdf - expected_cdf) < 1e-6


def test_covariance_correctness():
    """Test covariance calculation."""
    model = ScientificModel(
        id="prob-covariance",
        domain="mathematics.probability",
        description="Covariance between two variables",
        quantities=[
            Quantity(
                name="x_vals",
                value=[1, 2, 3],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="y_vals",
                value=[2, 4, 6],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="joint_probs",
                value=[0.2, 0.3, 0.5],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="cov_result",
                rhs="covariance(x_vals, y_vals, joint_probs)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    solver = ProbabilitySolver()
    result = solver.solve(model)

    assert result.success
    # Manual calculation: E[XY] = 1*2*0.2 + 2*4*0.3 + 3*6*0.5 = 0.4 + 2.4 + 9.0 = 11.8
    # E[X] = 1*0.2 + 2*0.3 + 3*0.5 = 0.2 + 0.6 + 1.5 = 2.3
    # E[Y] = 2*0.2 + 4*0.3 + 6*0.5 = 0.4 + 1.2 + 3.0 = 4.6
    # Cov = 11.8 - 2.3*4.6 = 11.8 - 10.58 = 1.22
    expected_cov = 1.22
    actual_cov = result.summary["cov_result"]
    assert abs(actual_cov - expected_cov) < 1e-6


def test_markov_transition_correctness(markov_transition_model):
    """Test Markov chain transition."""
    solver = ProbabilitySolver()
    result = solver.solve(markov_transition_model)

    assert result.success
    state = np.array([0.6, 0.4])
    trans = np.array([[0.7, 0.3], [0.4, 0.6]])
    expected_next = np.dot(state, trans)  # [0.58, 0.42]
    actual_next = result.summary["next_state"]

    assert len(actual_next) == 2
    assert abs(actual_next[0] - expected_next[0]) < 1e-6
    assert abs(actual_next[1] - expected_next[1]) < 1e-6


# ============================================================================
# SECTION 2: DETERMINISM TESTS
# ============================================================================

def test_determinism_bayes_theorem(bayes_theorem_model):
    """Test determinism: solving Bayes theorem twice gives identical results."""
    solver = ProbabilitySolver()

    result1 = solver.solve(bayes_theorem_model)
    result2 = solver.solve(bayes_theorem_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_expectation(expectation_model):
    """Test determinism for expectation calculation."""
    solver = ProbabilitySolver()

    result1 = solver.solve(expectation_model)
    result2 = solver.solve(expectation_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_variance(variance_model):
    """Test determinism for variance calculation."""
    solver = ProbabilitySolver()

    result1 = solver.solve(variance_model)
    result2 = solver.solve(variance_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_binomial(binomial_pdf_model):
    """Test determinism for binomial distribution."""
    solver = ProbabilitySolver()

    result1 = solver.solve(binomial_pdf_model)
    result2 = solver.solve(binomial_pdf_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_markov(markov_transition_model):
    """Test determinism for Markov chain."""
    solver = ProbabilitySolver()

    result1 = solver.solve(markov_transition_model)
    result2 = solver.solve(markov_transition_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# ============================================================================
# SECTION 3: ERROR-PATH TESTS
# ============================================================================

@pytest.mark.parametrize(
    ("operation", "values", "expected_error"),
    [
        ("bayes_theorem(1.5, 0.5, 0.5)", {}, "prior"),
        ("bayes_theorem(0.5, 1.5, 0.5)", {}, "likelihood"),
        ("bayes_theorem(0.5, 0.5, 0)", {}, "evidence"),
        ("conditional_probability(0.6, 0.5)", {}, "cannot exceed"),
        ("normal_pdf(1, 0, 0)", {}, "sigma"),
        ("binomial_pdf(11, 10, 0.5)", {}, "cannot be greater"),
        ("binomial_pdf(5, 10, 1.5)", {}, "success probability"),
        ("poisson_pdf(3, 0)", {}, "lambda"),
        ("exponential_pdf(-1, 0.5)", {}, "non-negative"),
        ("exponential_cdf(1, 0)", {}, "lambda"),
    ],
)
def test_probability_parameter_validation(bayes_theorem_model, operation, values, expected_error):
    """Test that invalid probability parameters are rejected."""
    equation = bayes_theorem_model.equations[0].model_copy(update={"rhs": operation})
    model = bayes_theorem_model.model_copy(update={"equations": [equation]})

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert expected_error in result.error


def test_error_expectation_mismatched_lengths():
    """Test that expectation with mismatched value/probability lengths fails."""
    model = ScientificModel(
        id="prob-expectation-mismatch",
        domain="mathematics.probability",
        description="Expectation with mismatched lengths",
        quantities=[
            Quantity(
                name="values",
                value=[1, 2, 3],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="probs",
                value=[0.5, 0.5],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="expected_value",
                rhs="expectation(values, probs)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert "same length" in result.error


def test_error_expectation_invalid_probabilities():
    """Test that expectation with invalid probabilities (not summing to 1) fails."""
    model = ScientificModel(
        id="prob-expectation-invalid",
        domain="mathematics.probability",
        description="Expectation with probabilities not summing to 1",
        quantities=[
            Quantity(
                name="values",
                value=[1, 2, 3],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="probs",
                value=[0.2, 0.2, 0.2],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="expected_value",
                rhs="expectation(values, probs)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert "sum to 1" in result.error


def test_error_markov_non_square_matrix():
    """Test that Markov transition with non-square matrix fails."""
    model = ScientificModel(
        id="prob-markov-nonsquare",
        domain="mathematics.probability",
        description="Markov with non-square transition matrix",
        quantities=[
            Quantity(
                name="state_probs",
                value=[0.6, 0.4],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="transition",
                value=[[0.7, 0.3, 0.2], [0.4, 0.6, 0.1]],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="next_state",
                rhs="markov_transition_matrix(state_probs, transition)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert "square" in result.error


def test_error_markov_non_stochastic_matrix():
    """Test that Markov transition with non-row-stochastic matrix fails."""
    model = ScientificModel(
        id="prob-markov-nonstochastic",
        domain="mathematics.probability",
        description="Markov with non-stochastic transition matrix",
        quantities=[
            Quantity(
                name="state_probs",
                value=[0.6, 0.4],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="transition",
                value=[[0.7, 0.2], [0.4, 0.5]],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="next_state",
                rhs="markov_transition_matrix(state_probs, transition)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert "sum to 1" in result.error


# ============================================================================
# SECTION 4: ROUTING TEST
# ============================================================================

def test_general_solver_routes_probability(bayes_theorem_model):
    """Test that GeneralSolver routes to probability solver."""
    result = GeneralSolver().solve(bayes_theorem_model)

    assert result.success
    assert "posterior" in result.summary


def test_operation_parser_rejects_malformed_call(bayes_theorem_model):
    """Test that malformed operation calls are rejected."""
    equation = bayes_theorem_model.equations[0].model_copy(
        update={"rhs": "bayes_theorem(0.01, 0.95, 0.0595) + 0.1"}
    )
    model = bayes_theorem_model.model_copy(update={"equations": [equation]})

    result = ProbabilitySolver().solve(model)

    assert not result.success
    assert "Invalid operation format" in result.error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
