"""
Tests for statistical analysis solver.
Golden-file tests for determinism: same model → same output.
"""
import numpy as np
import pytest
from scipy import stats as scipy_stats

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.statistics import StatisticalAnalysisSolver


@pytest.fixture
def basic_dataset():
    """Simple dataset: [1, 2, 3, 4, 5]."""
    return [1.0, 2.0, 3.0, 4.0, 5.0]


@pytest.fixture
def descriptive_stats_model(basic_dataset):
    """Model for computing mean of basic dataset."""
    return ScientificModel(
        id="stats-descriptive-mean",
        domain="mathematics.statistics",
        description="Compute mean of dataset",
        quantities=[
            Quantity(
                name="data",
                value=basic_dataset,
                siUnit="dimensionless",
                description="Dataset",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="mean_result",
                rhs="mean(data)",
                type=EquationType.ALGEBRAIC,
                description="Mean of data"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test", originalQuery="compute mean of [1,2,3,4,5]")
    )


@pytest.fixture
def stdev_model(basic_dataset):
    """Model for computing standard deviation."""
    return ScientificModel(
        id="stats-stdev",
        domain="mathematics.statistics",
        description="Compute standard deviation",
        quantities=[
            Quantity(
                name="data",
                value=basic_dataset,
                siUnit="dimensionless",
                description="Dataset",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="stdev_result",
                rhs="stdev(data)",
                type=EquationType.ALGEBRAIC,
                description="Standard deviation"
            ),
        ],
        initialConditions={},
        solver=Solver(
            method=SolverMethod.SYMBOLIC_SOLVE,
            tolerance=1e-6
        ),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def quartiles_model(basic_dataset):
    """Model for computing quartiles."""
    return ScientificModel(
        id="stats-quartiles",
        domain="mathematics.statistics",
        description="Compute quartiles",
        quantities=[
            Quantity(
                name="data",
                value=basic_dataset,
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="quartiles_result",
                rhs="quartiles(data)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def normal_pdf_model():
    """Model for computing normal distribution PDF."""
    return ScientificModel(
        id="stats-normal-pdf",
        domain="mathematics.statistics",
        description="Normal distribution PDF",
        quantities=[
            Quantity(name="x", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="mu", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="sigma", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="pdf_result",
                rhs="normal_pdf(x, mu, sigma)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def normal_cdf_model():
    """Model for computing normal distribution CDF."""
    return ScientificModel(
        id="stats-normal-cdf",
        domain="mathematics.statistics",
        description="Normal distribution CDF",
        quantities=[
            Quantity(name="x", value=1.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="mu", value=0.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="sigma", value=1.0, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="cdf_result",
                rhs="normal_cdf(x, mu, sigma)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def ttest_model(basic_dataset):
    """Model for one-sample t-test."""
    return ScientificModel(
        id="stats-ttest",
        domain="mathematics.statistics",
        description="One-sample t-test",
        quantities=[
            Quantity(
                name="data",
                value=basic_dataset,
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="null_hypothesis",
                value=3.0,
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="ttest_result",
                rhs="ttest_1samp(data, null_hypothesis)",
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
        id="stats-binomial-pdf",
        domain="mathematics.statistics",
        description="Binomial distribution PDF",
        quantities=[
            Quantity(name="k", value=5.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="n", value=10.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="p", value=0.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="binomial_result",
                rhs="binomial_pdf(k, n, p)",
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
        id="stats-poisson-pdf",
        domain="mathematics.statistics",
        description="Poisson distribution PDF",
        quantities=[
            Quantity(name="k", value=3.0, siUnit="dimensionless", isKnown=True),
            Quantity(name="lam", value=2.5, siUnit="dimensionless", isKnown=True),
        ],
        equations=[
            Equation(
                lhs="poisson_result",
                rhs="poisson_pdf(k, lam)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


@pytest.fixture
def chi2_gof_model():
    """Model for chi-square goodness-of-fit test."""
    return ScientificModel(
        id="stats-chi2-gof",
        domain="mathematics.statistics",
        description="Chi-square goodness-of-fit",
        quantities=[
            Quantity(
                name="observed",
                value=[10, 20, 30, 40],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
            Quantity(
                name="expected",
                value=[25, 25, 25, 25],
                siUnit="dimensionless",
                isKnown=True,
                dimensionVector=DimensionVector()
            ),
        ],
        equations=[
            Equation(
                lhs="chi2_result",
                rhs="chi2_gof(observed, expected)",
                type=EquationType.ALGEBRAIC,
            ),
        ],
        initialConditions={},
        solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
        metadata=Metadata(source="test")
    )


# Descriptive Statistics Tests

def test_mean_solvable(descriptive_stats_model):
    """Test that mean computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(descriptive_stats_model)

    assert result.success
    assert result.summary is not None
    assert "mean" in result.summary


def test_mean_correctness(descriptive_stats_model):
    """Test that mean is computed correctly."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(descriptive_stats_model)

    assert result.success
    expected_mean = 3.0  # mean of [1, 2, 3, 4, 5]
    actual_mean = result.summary["mean"]
    assert abs(actual_mean - expected_mean) < 1e-6


def test_stdev_solvable(stdev_model):
    """Test that stdev computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(stdev_model)

    assert result.success
    assert result.summary is not None
    assert "stdev" in result.summary


def test_stdev_correctness(stdev_model):
    """Test that stdev is computed correctly."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(stdev_model)

    assert result.success
    expected_stdev = float(np.std([1, 2, 3, 4, 5]))
    actual_stdev = result.summary["stdev"]
    assert abs(actual_stdev - expected_stdev) < 1e-6


def test_quartiles_solvable(quartiles_model):
    """Test that quartile computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(quartiles_model)

    assert result.success
    assert result.summary is not None
    assert "q1" in result.summary
    assert "q2" in result.summary
    assert "q3" in result.summary


def test_quartiles_correctness(quartiles_model):
    """Test that quartiles are computed correctly."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(quartiles_model)

    assert result.success
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected_q1 = float(np.percentile(data, 25))
    expected_q2 = float(np.percentile(data, 50))
    expected_q3 = float(np.percentile(data, 75))

    assert abs(result.summary["q1"] - expected_q1) < 1e-6
    assert abs(result.summary["q2"] - expected_q2) < 1e-6
    assert abs(result.summary["q3"] - expected_q3) < 1e-6


# Distribution Tests

def test_normal_pdf_solvable(normal_pdf_model):
    """Test that normal PDF computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(normal_pdf_model)

    assert result.success
    assert result.summary is not None
    assert "pdf" in result.summary


def test_normal_pdf_at_mean(normal_pdf_model):
    """Test normal PDF value at mean (should be 1/sigma/sqrt(2*pi))."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(normal_pdf_model)

    assert result.success
    # PDF at x=mu (0) with sigma=1 should be ~0.3989
    expected_pdf = 1.0 / (1.0 * np.sqrt(2 * np.pi))
    actual_pdf = result.summary["pdf"]
    assert abs(actual_pdf - expected_pdf) < 1e-6


def test_normal_cdf_solvable(normal_cdf_model):
    """Test that normal CDF computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(normal_cdf_model)

    assert result.success
    assert result.summary is not None
    assert "cdf" in result.summary


def test_normal_cdf_correctness(normal_cdf_model):
    """Test normal CDF value."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(normal_cdf_model)

    assert result.success
    # CDF at x=1 with mu=0, sigma=1 should be ~0.8413
    expected_cdf = scipy_stats.norm.cdf(1.0, loc=0.0, scale=1.0)
    actual_cdf = result.summary["cdf"]
    assert abs(actual_cdf - expected_cdf) < 1e-6


def test_binomial_pdf_solvable(binomial_pdf_model):
    """Test that binomial PDF computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(binomial_pdf_model)

    assert result.success
    assert result.summary is not None
    assert "pmf" in result.summary


def test_binomial_pdf_correctness(binomial_pdf_model):
    """Test binomial PDF correctness."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(binomial_pdf_model)

    assert result.success
    expected_pmf = scipy_stats.binom.pmf(5, 10, 0.5)
    actual_pmf = result.summary["pmf"]
    assert abs(actual_pmf - expected_pmf) < 1e-6


def test_poisson_pdf_solvable(poisson_pdf_model):
    """Test that Poisson PDF computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(poisson_pdf_model)

    assert result.success
    assert result.summary is not None
    assert "pmf" in result.summary


def test_poisson_pdf_correctness(poisson_pdf_model):
    """Test Poisson PDF correctness."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(poisson_pdf_model)

    assert result.success
    expected_pmf = scipy_stats.poisson.pmf(3, 2.5)
    actual_pmf = result.summary["pmf"]
    assert abs(actual_pmf - expected_pmf) < 1e-6


# Hypothesis Tests

def test_ttest_solvable(ttest_model):
    """Test that t-test computation solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(ttest_model)

    assert result.success
    assert result.summary is not None
    assert "t_statistic" in result.summary
    assert "p_value" in result.summary


def test_ttest_correctness(ttest_model):
    """Test t-test correctness."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(ttest_model)

    assert result.success
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected_t, expected_p = scipy_stats.ttest_1samp(data, 3.0)

    assert abs(result.summary["t_statistic"] - expected_t) < 1e-6
    assert abs(result.summary["p_value"] - expected_p) < 1e-6


def test_chi2_gof_solvable(chi2_gof_model):
    """Test that chi-square goodness-of-fit test solves successfully."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(chi2_gof_model)

    assert result.success
    assert result.summary is not None
    assert "chi2_statistic" in result.summary
    assert "p_value" in result.summary


def test_chi2_gof_correctness(chi2_gof_model):
    """Test chi-square goodness-of-fit correctness."""
    solver = StatisticalAnalysisSolver()
    result = solver.solve(chi2_gof_model)

    assert result.success
    observed = np.array([10, 20, 30, 40])
    expected = np.array([25, 25, 25, 25])
    expected_chi2, expected_p = scipy_stats.chisquare(observed, expected)

    assert abs(result.summary["chi2_statistic"] - expected_chi2) < 1e-6
    assert abs(result.summary["p_value"] - expected_p) < 1e-6


# Determinism Tests

def test_determinism_mean(descriptive_stats_model):
    """Test determinism: solving same model twice produces identical results."""
    solver = StatisticalAnalysisSolver()

    result1 = solver.solve(descriptive_stats_model)
    result2 = solver.solve(descriptive_stats_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


def test_determinism_ttest(ttest_model):
    """Test determinism for t-test."""
    solver = StatisticalAnalysisSolver()

    result1 = solver.solve(ttest_model)
    result2 = solver.solve(ttest_model)

    assert result1.success and result2.success
    assert result1.summary == result2.summary


# General Solver Routing

def test_general_solver_routes_statistics_mean(descriptive_stats_model):
    """Test that GeneralSolver routes to statistics solver for mean."""
    result = GeneralSolver().solve(descriptive_stats_model)

    assert result.success
    assert result.summary is not None
    assert "mean" in result.summary


def test_general_solver_routes_statistics_ttest(ttest_model):
    """Test that GeneralSolver routes to statistics solver for t-test."""
    result = GeneralSolver().solve(ttest_model)

    assert result.success
    assert result.summary is not None
    assert "t_statistic" in result.summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
