"""Statistical analysis solver (mathematics.statistics domain)."""
from typing import Dict, List, Union
import re
import numpy as np
from scipy import stats

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.statistics")
class StatisticalAnalysisSolver(SolverBase):
    """
    Solver for descriptive statistics, distributions, and hypothesis tests.
    Supports operations like mean, stdev, pdf, cdf, and t-tests.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve statistical queries based on equations.
        Equations expected: stat operation names (e.g., "mean(data)", "stdev(data)",
        "normal_pdf(x, mu, sigma)", "ttest_1samp(data, null_hypothesis)").
        """
        try:
            # Extract quantities
            quantities = {q.name: q for q in model.quantities}

            # Parse the equation to determine the operation
            if not model.equations:
                return SolverResult(
                    success=False,
                    message="No equations provided",
                    error="At least one equation required"
                )

            equation = model.equations[0]
            operation_str = equation.rhs.strip()

            # Parse and execute the operation
            result = self._execute_operation(operation_str, quantities)

            if not isinstance(result, dict) or "success" not in result:
                return SolverResult(
                    success=False,
                    message="Invalid operation result",
                    error="Operation did not return valid result"
                )

            if not result["success"]:
                return SolverResult(
                    success=False,
                    message=result.get("message", "Operation failed"),
                    error=result.get("error", "Unknown error")
                )

            # Extract summary (remove success/message/error fields)
            summary = {k: v for k, v in result.items()
                      if k not in ("success", "message", "error")}

            return SolverResult(
                success=True,
                message="Statistical analysis completed successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _execute_operation(self, operation_str: str, quantities: Dict[str, Quantity]) -> dict:
        """
        Parse and execute a statistical operation.
        Returns a dict with success flag and results.
        """
        # Parse function call pattern: func_name(arg1, arg2, ...)
        match = re.match(r'(\w+)\((.*)\)', operation_str)
        if not match:
            return {"success": False, "error": f"Invalid operation format: {operation_str}"}

        func_name = match.group(1)
        args_str = match.group(2).strip()

        # Parse arguments
        args = [arg.strip() for arg in args_str.split(',')]

        # Resolve arguments (quantity names to values)
        resolved_args = []
        for arg in args:
            resolved = self._resolve_argument(arg, quantities)
            if resolved is None:
                return {"success": False, "error": f"Could not resolve argument: {arg}"}
            resolved_args.append(resolved)

        # Dispatch to appropriate function
        try:
            if func_name == "mean":
                return self._stat_mean(resolved_args)
            elif func_name == "median":
                return self._stat_median(resolved_args)
            elif func_name == "mode":
                return self._stat_mode(resolved_args)
            elif func_name == "variance":
                return self._stat_variance(resolved_args)
            elif func_name == "stdev":
                return self._stat_stdev(resolved_args)
            elif func_name == "quartiles":
                return self._stat_quartiles(resolved_args)
            elif func_name == "normal_pdf":
                return self._dist_normal_pdf(resolved_args)
            elif func_name == "normal_cdf":
                return self._dist_normal_cdf(resolved_args)
            elif func_name == "normal_quantile":
                return self._dist_normal_quantile(resolved_args)
            elif func_name == "binomial_pdf":
                return self._dist_binomial_pdf(resolved_args)
            elif func_name == "binomial_cdf":
                return self._dist_binomial_cdf(resolved_args)
            elif func_name == "poisson_pdf":
                return self._dist_poisson_pdf(resolved_args)
            elif func_name == "poisson_cdf":
                return self._dist_poisson_cdf(resolved_args)
            elif func_name == "ttest_1samp":
                return self._test_ttest_1samp(resolved_args)
            elif func_name == "chi2_gof":
                return self._test_chi2_gof(resolved_args)
            else:
                return {"success": False, "error": f"Unknown operation: {func_name}"}
        except Exception as e:
            return {"success": False, "error": f"Operation error: {str(e)}"}

    def _resolve_argument(self, arg: str, quantities: Dict[str, Quantity]) -> Union[float, List[float], None]:
        """
        Resolve an argument: either a quantity name or a numeric value.
        """
        # Try to parse as a float
        try:
            return float(arg)
        except ValueError:
            pass

        # Try to look up as a quantity
        if arg in quantities:
            qty = quantities[arg]
            if qty.value is not None:
                return qty.value

        return None

    # Descriptive statistics operations

    def _stat_mean(self, args: List) -> dict:
        """Compute mean of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "mean() requires exactly 1 argument"}
        data = np.array(args[0])
        return {"success": True, "mean": float(np.mean(data))}

    def _stat_median(self, args: List) -> dict:
        """Compute median of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "median() requires exactly 1 argument"}
        data = np.array(args[0])
        return {"success": True, "median": float(np.median(data))}

    def _stat_mode(self, args: List) -> dict:
        """Compute mode of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "mode() requires exactly 1 argument"}
        data = np.array(args[0])
        mode_result = stats.mode(data, keepdims=True)
        return {"success": True, "mode": float(mode_result.mode[0])}

    def _stat_variance(self, args: List) -> dict:
        """Compute variance of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "variance() requires exactly 1 argument"}
        data = np.array(args[0])
        return {"success": True, "variance": float(np.var(data))}

    def _stat_stdev(self, args: List) -> dict:
        """Compute standard deviation of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "stdev() requires exactly 1 argument"}
        data = np.array(args[0])
        return {"success": True, "stdev": float(np.std(data))}

    def _stat_quartiles(self, args: List) -> dict:
        """Compute quartiles (Q1, Q2/median, Q3) of a dataset."""
        if len(args) != 1:
            return {"success": False, "error": "quartiles() requires exactly 1 argument"}
        data = np.array(args[0])
        q1 = float(np.percentile(data, 25))
        q2 = float(np.percentile(data, 50))
        q3 = float(np.percentile(data, 75))
        return {
            "success": True,
            "q1": q1,
            "q2": q2,
            "q3": q3
        }

    # Distribution operations

    def _dist_normal_pdf(self, args: List) -> dict:
        """Compute PDF of normal distribution at x with mean mu and std sigma."""
        if len(args) != 3:
            return {"success": False, "error": "normal_pdf() requires exactly 3 arguments: x, mu, sigma"}
        x, mu, sigma = args
        pdf_value = float(stats.norm.pdf(x, loc=mu, scale=sigma))
        return {"success": True, "pdf": pdf_value}

    def _dist_normal_cdf(self, args: List) -> dict:
        """Compute CDF of normal distribution at x with mean mu and std sigma."""
        if len(args) != 3:
            return {"success": False, "error": "normal_cdf() requires exactly 3 arguments: x, mu, sigma"}
        x, mu, sigma = args
        cdf_value = float(stats.norm.cdf(x, loc=mu, scale=sigma))
        return {"success": True, "cdf": cdf_value}

    def _dist_normal_quantile(self, args: List) -> dict:
        """Compute quantile of normal distribution at probability p with mean mu and std sigma."""
        if len(args) != 3:
            return {"success": False, "error": "normal_quantile() requires exactly 3 arguments: p, mu, sigma"}
        p, mu, sigma = args
        q_value = float(stats.norm.ppf(p, loc=mu, scale=sigma))
        return {"success": True, "quantile": q_value}

    def _dist_binomial_pdf(self, args: List) -> dict:
        """Compute PDF of binomial distribution: P(X=k) with n trials and p probability."""
        if len(args) != 3:
            return {"success": False, "error": "binomial_pdf() requires exactly 3 arguments: k, n, p"}
        k, n, p = args
        pdf_value = float(stats.binom.pmf(k, int(n), p))
        return {"success": True, "pmf": pdf_value}

    def _dist_binomial_cdf(self, args: List) -> dict:
        """Compute CDF of binomial distribution: P(X<=k) with n trials and p probability."""
        if len(args) != 3:
            return {"success": False, "error": "binomial_cdf() requires exactly 3 arguments: k, n, p"}
        k, n, p = args
        cdf_value = float(stats.binom.cdf(k, int(n), p))
        return {"success": True, "cdf": cdf_value}

    def _dist_poisson_pdf(self, args: List) -> dict:
        """Compute PDF of Poisson distribution: P(X=k) with rate lambda."""
        if len(args) != 2:
            return {"success": False, "error": "poisson_pdf() requires exactly 2 arguments: k, lambda"}
        k, lam = args
        pdf_value = float(stats.poisson.pmf(k, lam))
        return {"success": True, "pmf": pdf_value}

    def _dist_poisson_cdf(self, args: List) -> dict:
        """Compute CDF of Poisson distribution: P(X<=k) with rate lambda."""
        if len(args) != 2:
            return {"success": False, "error": "poisson_cdf() requires exactly 2 arguments: k, lambda"}
        k, lam = args
        cdf_value = float(stats.poisson.cdf(k, lam))
        return {"success": True, "cdf": cdf_value}

    # Hypothesis tests

    def _test_ttest_1samp(self, args: List) -> dict:
        """
        Perform one-sample t-test: H0: mean(data) = null_hypothesis.
        Returns t-statistic and p-value (two-tailed).
        """
        if len(args) != 2:
            return {"success": False, "error": "ttest_1samp() requires exactly 2 arguments: data, null_hypothesis"}
        data, null_hyp = args
        data = np.array(data)
        t_stat, p_value = stats.ttest_1samp(data, null_hyp)
        return {
            "success": True,
            "t_statistic": float(t_stat),
            "p_value": float(p_value)
        }

    def _test_chi2_gof(self, args: List) -> dict:
        """
        Perform chi-square goodness-of-fit test.
        Compares observed frequencies (data) to expected frequencies (expected).
        Returns chi2 statistic and p-value.
        """
        if len(args) != 2:
            return {"success": False, "error": "chi2_gof() requires exactly 2 arguments: observed, expected"}
        observed, expected = args
        observed = np.array(observed)
        expected = np.array(expected)
        chi2_stat, p_value = stats.chisquare(observed, expected)
        return {
            "success": True,
            "chi2_statistic": float(chi2_stat),
            "p_value": float(p_value)
        }
