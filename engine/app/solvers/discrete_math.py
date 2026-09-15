"""Discrete mathematics solver (mathematics.discrete_math domain)."""
from typing import Set, List, Union, Dict, Any
import numpy as np
import sympy as sp
from app.model import ScientificModel, SolverResult
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_value, get_vector


def _set_union(set_a: Union[List, Set], set_b: Union[List, Set]) -> List:
    """Union of two sets: A ∪ B."""
    if isinstance(set_a, (list, tuple)):
        set_a = set(set_a)
    if isinstance(set_b, (list, tuple)):
        set_b = set(set_b)
    result = sorted(list(set_a | set_b))
    return result


def _set_intersection(set_a: Union[List, Set], set_b: Union[List, Set]) -> List:
    """Intersection of two sets: A ∩ B."""
    if isinstance(set_a, (list, tuple)):
        set_a = set(set_a)
    if isinstance(set_b, (list, tuple)):
        set_b = set(set_b)
    result = sorted(list(set_a & set_b))
    return result


def _set_complement(universal_set: Union[List, Set], set_a: Union[List, Set]) -> List:
    """Complement of A in universal set U: A^c = U - A."""
    if isinstance(universal_set, (list, tuple)):
        universal_set = set(universal_set)
    if isinstance(set_a, (list, tuple)):
        set_a = set(set_a)
    if not set_a.issubset(universal_set):
        raise ValueError("Set A must be a subset of universal set")
    result = sorted(list(universal_set - set_a))
    return result


def _set_symmetric_difference(set_a: Union[List, Set], set_b: Union[List, Set]) -> List:
    """Symmetric difference: A △ B = (A - B) ∪ (B - A)."""
    if isinstance(set_a, (list, tuple)):
        set_a = set(set_a)
    if isinstance(set_b, (list, tuple)):
        set_b = set(set_b)
    result = sorted(list(set_a ^ set_b))
    return result


def _power_set(set_a: Union[List, Set]) -> List[List]:
    """Power set of A (all subsets of A)."""
    if isinstance(set_a, (list, tuple)):
        set_a = list(set_a)
    else:
        set_a = list(set_a)
    set_a = sorted(set_a)  # for determinism
    n = len(set_a)
    if n > 20:
        raise ValueError("Power set size limited to 2^20 for performance")
    result = []
    for i in range(2 ** n):
        subset = [set_a[j] for j in range(n) if (i >> j) & 1]
        result.append(sorted(subset))
    return sorted([sorted(s) for s in result])


def _linear_recurrence_1st_order(a: float, b: float, f0: float, n: int) -> float:
    """
    Solve 1st-order linear recurrence: F(n) = a*F(n-1) + b
    with initial condition F(0) = f0.
    Returns F(n).
    """
    if not isinstance(n, (int, float)) or n < 0 or int(n) != n:
        raise ValueError("n must be a non-negative integer")
    n = int(n)

    # Symbolic solution: F(n) = a^n*F(0) + b*(a^n - 1)/(a - 1) if a != 1
    # Otherwise F(n) = F(0) + b*n
    if abs(a - 1.0) < 1e-10:
        result = f0 + b * n
    else:
        result = a**n * f0 + b * (a**n - 1.0) / (a - 1.0)
    return float(result)


def _linear_recurrence_2nd_order(a: float, b: float, f0: float, f1: float, n: int) -> float:
    """
    Solve 2nd-order linear recurrence: F(n) = a*F(n-1) + b*F(n-2)
    with initial conditions F(0) = f0, F(1) = f1.
    Returns F(n).
    """
    if not isinstance(n, (int, float)) or n < 0 or int(n) != n:
        raise ValueError("n must be a non-negative integer")
    n = int(n)

    if n == 0:
        return float(f0)
    if n == 1:
        return float(f1)

    # Use SymPy's rsolve for symbolic solution
    k = sp.Symbol('k')
    F = sp.Function('F')
    recurrence = sp.Eq(F(k), a * F(k - 1) + b * F(k - 2))

    try:
        general_solution = sp.rsolve(recurrence, F(k), {F(0): f0, F(1): f1})
        if general_solution is None:
            # Fallback: compute iteratively
            fib = [f0, f1]
            for i in range(2, n + 1):
                fib.append(a * fib[i - 1] + b * fib[i - 2])
            return float(fib[n])
        result = general_solution.subs(k, n)
        return float(result)
    except Exception:
        # Fallback: compute iteratively
        fib = [f0, f1]
        for i in range(2, n + 1):
            fib.append(a * fib[i - 1] + b * fib[i - 2])
        return float(fib[n])


def _non_homogeneous_recurrence(a: float, b: float, f0: float, f1: float, n: int,
                                 forcing_func: str = "0") -> float:
    """
    Solve non-homogeneous 2nd-order recurrence: F(n) = a*F(n-1) + b*F(n-2) + g(n)
    with initial conditions F(0) = f0, F(1) = f1.
    forcing_func: string like "n", "2**n", "1" (constant), "n**2", etc.
    Returns F(n).
    """
    if not isinstance(n, (int, float)) or n < 0 or int(n) != n:
        raise ValueError("n must be a non-negative integer")
    n = int(n)

    if n == 0:
        return float(f0)
    if n == 1:
        return float(f1)

    # Use SymPy's rsolve for symbolic solution
    k = sp.Symbol('k')
    F = sp.Function('F')

    # Parse forcing function
    try:
        forcing_expr = sp.sympify(forcing_func)
    except:
        raise ValueError(f"Invalid forcing function: {forcing_func}")

    recurrence = sp.Eq(F(k), a * F(k - 1) + b * F(k - 2) + forcing_expr.subs(k, k))

    try:
        general_solution = sp.rsolve(recurrence, F(k), {F(0): f0, F(1): f1})
        if general_solution is None:
            # Fallback: compute iteratively
            f_vals = [f0, f1]
            for i in range(2, n + 1):
                g_i = float(forcing_expr.subs(k, i))
                f_vals.append(a * f_vals[i - 1] + b * f_vals[i - 2] + g_i)
            return float(f_vals[n])
        result = general_solution.subs(k, n)
        return float(result)
    except Exception:
        # Fallback: compute iteratively
        f_vals = [f0, f1]
        for i in range(2, n + 1):
            g_i = float(forcing_expr.subs(k, i))
            f_vals.append(a * f_vals[i - 1] + b * f_vals[i - 2] + g_i)
        return float(f_vals[n])


def _inclusion_exclusion(set_sizes: List[float], intersection_sizes: List[float] = None) -> float:
    """
    Inclusion-Exclusion Principle: |A₁ ∪ A₂ ∪ ... ∪ Aₙ|
    set_sizes: list of individual set sizes [|A₁|, |A₂|, ..., |Aₙ|]
    intersection_sizes: list of pairwise, triple, etc. intersection sizes
                        [|A₁∩A₂|, |A₁∩A₃|, ..., |A₁∩A₂∩A₃|, ...]
                        If None, assumes no intersections.
    Returns the size of the union.
    """
    set_sizes = list(set_sizes)
    n = len(set_sizes)

    if intersection_sizes is None:
        intersection_sizes = []
    else:
        intersection_sizes = list(intersection_sizes)

    # Basic inclusion-exclusion: |A∪B| = |A| + |B| - |A∩B|
    # For 2 sets
    if n == 2 and len(intersection_sizes) >= 1:
        return float(set_sizes[0] + set_sizes[1] - intersection_sizes[0])
    elif n == 2:
        return float(set_sizes[0] + set_sizes[1])

    # For 3 sets: |A∪B∪C| = |A| + |B| + |C| - |A∩B| - |A∩C| - |B∩C| + |A∩B∩C|
    if n == 3:
        result = set_sizes[0] + set_sizes[1] + set_sizes[2]
        if len(intersection_sizes) >= 3:
            result -= intersection_sizes[0] + intersection_sizes[1] + intersection_sizes[2]
        if len(intersection_sizes) >= 4:
            result += intersection_sizes[3]
        return float(result)

    # General n sets with provided intersection sizes
    # Assume intersection_sizes are provided in order:
    # [2-way intersections], [3-way], [4-way], ..., [n-way]
    result = sum(set_sizes)
    sign = -1
    idx = 0
    for k in range(2, n + 1):
        expected_count = sp.binomial(n, k)
        for i in range(min(int(expected_count), len(intersection_sizes) - idx)):
            if idx < len(intersection_sizes):
                result += sign * intersection_sizes[idx]
                idx += 1
        sign *= -1

    return float(result)


def _stirling_number_1st(n: int, k: int) -> int:
    """
    Stirling number of the first kind s(n, k).
    Counts permutations of n elements with k cycles.
    """
    if not isinstance(n, (int, float)) or not isinstance(k, (int, float)):
        raise ValueError("n and k must be integers")
    n, k = int(n), int(k)

    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    if k > n:
        return 0
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0

    # Use SymPy's stirling function
    result = int(sp.functions.combinatorial.numbers.stirling(n, k, kind=1))
    return result


def _stirling_number_2nd(n: int, k: int) -> int:
    """
    Stirling number of the second kind S(n, k).
    Counts ways to partition n elements into k non-empty subsets.
    """
    if not isinstance(n, (int, float)) or not isinstance(k, (int, float)):
        raise ValueError("n and k must be integers")
    n, k = int(n), int(k)

    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    if k > n:
        return 0
    if n == 0 and k == 0:
        return 1
    if n == 0 or k == 0:
        return 0

    # Use SymPy's stirling function
    result = int(sp.functions.combinatorial.numbers.stirling(n, k, kind=2))
    return result


def _partition_function(n: int, k: int = None) -> int:
    """
    Partition function p(n): number of ways to partition n into positive integers.
    If k is provided, returns p(n, k): partitions of n into exactly k parts.
    """
    if not isinstance(n, (int, float)):
        raise ValueError("n must be an integer")
    n = int(n)

    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 1

    if k is not None:
        if not isinstance(k, (int, float)):
            raise ValueError("k must be an integer")
        k = int(k)
        if k <= 0 or k > n:
            return 0 if k != n else 1

        # Use SymPy's partition function with k parts
        result = int(sp.functions.combinatorial.numbers.partition(n, k))
        return result
    else:
        # Total partitions of n
        result = int(sp.functions.combinatorial.numbers.partition(n))
        return result


def _boolean_algebra(value_a: Union[float, int], value_b: Union[float, int],
                      operation: str) -> int:
    """
    Boolean algebra operations: AND, OR, XOR, NOT.
    Treats non-zero as True (1), zero as False (0).
    operation: "AND", "OR", "XOR", "NOT"
    For NOT, only value_a is used.
    """
    a = 1 if value_a != 0 else 0
    b = 1 if value_b != 0 else 0

    operation = operation.upper().strip()

    if operation == "AND":
        return int(a & b)
    elif operation == "OR":
        return int(a | b)
    elif operation == "XOR":
        return int(a ^ b)
    elif operation == "NOT":
        return int(~a & 1)  # Bitwise NOT, mask to 1 bit
    else:
        raise ValueError(f"Unknown boolean operation: {operation}. Expected AND, OR, XOR, or NOT.")


_OPERATIONS = {
    "set_union": _set_union,
    "set_intersection": _set_intersection,
    "set_complement": _set_complement,
    "set_symmetric_difference": _set_symmetric_difference,
    "power_set": _power_set,
    "linear_recurrence_1st_order": _linear_recurrence_1st_order,
    "linear_recurrence_2nd_order": _linear_recurrence_2nd_order,
    "non_homogeneous_recurrence": _non_homogeneous_recurrence,
    "inclusion_exclusion": _inclusion_exclusion,
    "stirling_number_1st": _stirling_number_1st,
    "stirling_number_2nd": _stirling_number_2nd,
    "partition_function": _partition_function,
    "boolean_algebra": _boolean_algebra,
}


@register("mathematics.discrete_math")
class DiscreteMathSolver(SolverBase):
    """Solver for discrete mathematics: set operations, recurrences, combinatorics."""

    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            quantities = {q.name: q for q in model.quantities}
            summary = run_dispatch(model, quantities, _OPERATIONS)
            return SolverResult(success=True, message="Discrete math solved successfully", summary=summary)
        except Exception as e:
            return SolverResult(success=False, message="Solver error", error=str(e))
