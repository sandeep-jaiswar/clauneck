"""Probability theory solver (mathematics.probability domain)."""
from typing import Dict
import numpy as np
from scipy import stats as scipy_stats
from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_value, get_vector


def _bayes_theorem(prior: float, likelihood: float, evidence: float) -> float:
    """
    Bayes' theorem: P(A|B) = P(B|A) * P(A) / P(B).
    Args:
        prior: P(A) — prior probability of event A
        likelihood: P(B|A) — probability of B given A
        evidence: P(B) — marginal probability of event B
    Returns: posterior probability P(A|B)
    """
    if not (0 <= prior <= 1):
        raise ValueError("prior probability must be in [0, 1]")
    if not (0 <= likelihood <= 1):
        raise ValueError("likelihood probability must be in [0, 1]")
    if evidence <= 0 or evidence > 1:
        raise ValueError("evidence probability must be in (0, 1]")
    return float((likelihood * prior) / evidence)


def _conditional_probability(joint: float, marginal: float) -> float:
    """
    Conditional probability: P(A|B) = P(A,B) / P(B).
    Args:
        joint: P(A,B) — joint probability
        marginal: P(B) — marginal probability
    Returns: conditional probability P(A|B)
    """
    if not (0 <= joint <= 1):
        raise ValueError("joint probability must be in [0, 1]")
    if marginal <= 0 or marginal > 1:
        raise ValueError("marginal probability must be in (0, 1]")
    if joint > marginal:
        raise ValueError("joint probability cannot exceed marginal probability")
    return float(joint / marginal)


def _joint_probability(p_a: float, p_b: float) -> float:
    """
    Joint probability for independent events: P(A,B) = P(A) * P(B).
    Args:
        p_a: P(A) — probability of event A
        p_b: P(B) — probability of event B
    Returns: joint probability P(A,B)
    """
    if not (0 <= p_a <= 1):
        raise ValueError("P(A) must be in [0, 1]")
    if not (0 <= p_b <= 1):
        raise ValueError("P(B) must be in [0, 1]")
    return float(p_a * p_b)


def _expectation(values: list, probabilities: list) -> float:
    """
    Expected value: E[X] = Σ(x_i * P(X=x_i)).
    Args:
        values: list of values [x_1, x_2, ...]
        probabilities: list of corresponding probabilities [p_1, p_2, ...]
    Returns: E[X]
    """
    values_arr = np.array(values, dtype=float)
    probs_arr = np.array(probabilities, dtype=float)

    if len(values_arr) != len(probs_arr):
        raise ValueError("values and probabilities must have same length")

    if not np.allclose(np.sum(probs_arr), 1.0, atol=1e-6):
        raise ValueError("probabilities must sum to 1")
    if np.any(probs_arr < 0) or np.any(probs_arr > 1):
        raise ValueError("probabilities must be in [0, 1]")

    return float(np.sum(values_arr * probs_arr))


def _variance(values: list, probabilities: list) -> float:
    """
    Variance: Var[X] = E[X²] - (E[X])².
    Args:
        values: list of values [x_1, x_2, ...]
        probabilities: list of corresponding probabilities [p_1, p_2, ...]
    Returns: Var[X]
    """
    values_arr = np.array(values, dtype=float)
    probs_arr = np.array(probabilities, dtype=float)

    if len(values_arr) != len(probs_arr):
        raise ValueError("values and probabilities must have same length")

    if not np.allclose(np.sum(probs_arr), 1.0, atol=1e-6):
        raise ValueError("probabilities must sum to 1")
    if np.any(probs_arr < 0) or np.any(probs_arr > 1):
        raise ValueError("probabilities must be in [0, 1]")

    mean = np.sum(values_arr * probs_arr)
    var = np.sum((values_arr ** 2) * probs_arr) - (mean ** 2)
    # Return variance as-is; allow small negative values from numerical precision
    return float(var)


def _covariance(x_values: list, y_values: list, joint_probs: list) -> float:
    """
    Covariance: Cov(X,Y) = E[XY] - E[X]*E[Y].
    Args:
        x_values: list of X values
        y_values: list of Y values
        joint_probs: list of joint probabilities P(X=x_i, Y=y_i)
    Returns: Cov(X,Y)
    """
    x_arr = np.array(x_values, dtype=float)
    y_arr = np.array(y_values, dtype=float)
    joint_arr = np.array(joint_probs, dtype=float)

    if not (len(x_arr) == len(y_arr) == len(joint_arr)):
        raise ValueError("x_values, y_values, and joint_probs must have same length")

    if not np.allclose(np.sum(joint_arr), 1.0, atol=1e-6):
        raise ValueError("joint probabilities must sum to 1")
    if np.any(joint_arr < 0) or np.any(joint_arr > 1):
        raise ValueError("probabilities must be in [0, 1]")

    e_xy = np.sum(x_arr * y_arr * joint_arr)
    e_x = np.sum(x_arr * joint_arr)
    e_y = np.sum(y_arr * joint_arr)
    cov = e_xy - e_x * e_y
    return float(cov)


def _normal_pdf(x: float, mu: float, sigma: float) -> float:
    """
    Normal (Gaussian) distribution PDF: f(x) = (1/(sigma*sqrt(2π))) * exp(-(x-mu)²/(2σ²)).
    Args:
        x: value
        mu: mean
        sigma: standard deviation (must be > 0)
    Returns: PDF value at x
    """
    if sigma <= 0:
        raise ValueError("sigma (standard deviation) must be positive")
    return float(scipy_stats.norm.pdf(x, loc=mu, scale=sigma))


def _normal_cdf(x: float, mu: float, sigma: float) -> float:
    """
    Normal (Gaussian) distribution CDF: F(x) = P(X <= x).
    Args:
        x: value
        mu: mean
        sigma: standard deviation (must be > 0)
    Returns: CDF value at x
    """
    if sigma <= 0:
        raise ValueError("sigma (standard deviation) must be positive")
    return float(scipy_stats.norm.cdf(x, loc=mu, scale=sigma))


def _binomial_pdf(k: int, n: int, p: float) -> float:
    """
    Binomial distribution PDF: P(X=k) = C(n,k) * p^k * (1-p)^(n-k).
    Args:
        k: number of successes (must be non-negative integer ≤ n)
        n: number of trials (must be positive integer)
        p: probability of success (must be in [0, 1])
    Returns: PMF value at k
    """
    k = int(k)
    n = int(n)

    if k < 0 or n < 0:
        raise ValueError("k and n must be non-negative")
    if k > n:
        raise ValueError("k cannot be greater than n")
    if not (0 <= p <= 1):
        raise ValueError("p (success probability) must be in [0, 1]")

    return float(scipy_stats.binom.pmf(k, n, p))


def _binomial_cdf(k: int, n: int, p: float) -> float:
    """
    Binomial distribution CDF: F(k) = P(X <= k).
    Args:
        k: number of successes
        n: number of trials (must be positive integer)
        p: probability of success (must be in [0, 1])
    Returns: CDF value at k
    """
    k = int(k)
    n = int(n)

    if k < 0 or n < 0:
        raise ValueError("k and n must be non-negative")
    if k > n:
        raise ValueError("k cannot be greater than n")
    if not (0 <= p <= 1):
        raise ValueError("p (success probability) must be in [0, 1]")

    return float(scipy_stats.binom.cdf(k, n, p))


def _poisson_pdf(k: int, lam: float) -> float:
    """
    Poisson distribution PDF: P(X=k) = (λ^k * e^(-λ)) / k!.
    Args:
        k: number of events (non-negative integer)
        lam: rate parameter (must be positive)
    Returns: PMF value at k
    """
    k = int(k)

    if k < 0:
        raise ValueError("k must be non-negative")
    if lam <= 0:
        raise ValueError("lambda (rate parameter) must be positive")

    return float(scipy_stats.poisson.pmf(k, lam))


def _poisson_cdf(k: int, lam: float) -> float:
    """
    Poisson distribution CDF: F(k) = P(X <= k).
    Args:
        k: number of events
        lam: rate parameter (must be positive)
    Returns: CDF value at k
    """
    k = int(k)

    if k < 0:
        raise ValueError("k must be non-negative")
    if lam <= 0:
        raise ValueError("lambda (rate parameter) must be positive")

    return float(scipy_stats.poisson.cdf(k, lam))


def _exponential_pdf(x: float, lam: float) -> float:
    """
    Exponential distribution PDF: f(x) = λ * e^(-λx) for x ≥ 0.
    Args:
        x: value (must be non-negative)
        lam: rate parameter (must be positive)
    Returns: PDF value at x
    """
    if x < 0:
        raise ValueError("x must be non-negative")
    if lam <= 0:
        raise ValueError("lambda (rate parameter) must be positive")

    return float(scipy_stats.expon.pdf(x, scale=1/lam))


def _exponential_cdf(x: float, lam: float) -> float:
    """
    Exponential distribution CDF: F(x) = 1 - e^(-λx) for x ≥ 0.
    Args:
        x: value (must be non-negative)
        lam: rate parameter (must be positive)
    Returns: CDF value at x
    """
    if x < 0:
        raise ValueError("x must be non-negative")
    if lam <= 0:
        raise ValueError("lambda (rate parameter) must be positive")

    return float(scipy_stats.expon.cdf(x, scale=1/lam))


def _markov_transition_matrix(state_probs: list, transition_matrix: list) -> list:
    """
    Markov chain state transition: π_{n+1} = π_n * P.
    Args:
        state_probs: current state probability distribution [π_1, π_2, ...]
        transition_matrix: transition probability matrix (list of lists), P[i][j] = P(state_j | state_i)
    Returns: next state probability distribution
    """
    state_arr = np.array(state_probs, dtype=float)
    trans_arr = np.array(transition_matrix, dtype=float)

    if trans_arr.ndim != 2 or trans_arr.shape[0] != trans_arr.shape[1]:
        raise ValueError("transition matrix must be square")
    if trans_arr.shape[0] != len(state_arr):
        raise ValueError("transition matrix dimension must match state vector length")

    # Validate row stochasticity
    row_sums = np.sum(trans_arr, axis=1)
    if not np.allclose(row_sums, 1.0, atol=1e-6):
        raise ValueError("transition matrix rows must sum to 1 (row-stochastic)")

    if not np.allclose(np.sum(state_arr), 1.0, atol=1e-6):
        raise ValueError("state probabilities must sum to 1")
    if np.any(state_arr < 0) or np.any(state_arr > 1):
        raise ValueError("state probabilities must be in [0, 1]")

    # Multiply: next_state = state * transition_matrix
    next_state = np.dot(state_arr, trans_arr)
    return next_state.tolist()


_OPERATIONS = {
    "bayes_theorem": _bayes_theorem,
    "conditional_probability": _conditional_probability,
    "joint_probability": _joint_probability,
    "expectation": _expectation,
    "variance": _variance,
    "covariance": _covariance,
    "normal_pdf": _normal_pdf,
    "normal_cdf": _normal_cdf,
    "binomial_pdf": _binomial_pdf,
    "binomial_cdf": _binomial_cdf,
    "poisson_pdf": _poisson_pdf,
    "poisson_cdf": _poisson_cdf,
    "exponential_pdf": _exponential_pdf,
    "exponential_cdf": _exponential_cdf,
    "markov_transition_matrix": _markov_transition_matrix,
}


@register("mathematics.probability")
class ProbabilitySolver(SolverBase):
    """
    Specialized solver for probability theory: Bayes' theorem, conditional/joint probability,
    expectations, variance, distributions (normal, binomial, Poisson, exponential),
    and Markov chains.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve probability problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Probability problem solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
