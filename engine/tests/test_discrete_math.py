"""
Tests for discrete mathematics solver.
Coverage: set operations, recurrence relations, combinatorics, Boolean algebra.
"""
import pytest
from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.discrete_math import DiscreteMathSolver


@pytest.fixture
def discrete_math_solver():
    """Instantiate the discrete math solver."""
    return DiscreteMathSolver()


# ============================================================================
# Set Operations Tests
# ============================================================================

class TestSetUnion:
    """Test set union operation."""

    def test_set_union_basic(self):
        """Basic union of two sets."""
        model = ScientificModel(
            id="union-basic",
            domain="mathematics.discrete_math",
            description="Union of {1,2,3} and {2,3,4}",
            quantities=[
                Quantity(name="set_a", value=[1, 2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="set_b", value=[2, 3, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="union_result", rhs="set_union(set_a, set_b)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["union_result"] == [1, 2, 3, 4]

    def test_set_union_disjoint(self):
        """Union of disjoint sets."""
        model = ScientificModel(
            id="union-disjoint",
            domain="mathematics.discrete_math",
            description="Union of {1,2} and {3,4}",
            quantities=[
                Quantity(name="set_a", value=[1, 2], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="set_b", value=[3, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="union_result", rhs="set_union(set_a, set_b)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["union_result"] == [1, 2, 3, 4]


class TestSetIntersection:
    """Test set intersection operation."""

    def test_set_intersection_basic(self):
        """Basic intersection of two sets."""
        model = ScientificModel(
            id="intersection-basic",
            domain="mathematics.discrete_math",
            description="Intersection of {1,2,3} and {2,3,4}",
            quantities=[
                Quantity(name="set_a", value=[1, 2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="set_b", value=[2, 3, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="inter_result", rhs="set_intersection(set_a, set_b)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["inter_result"] == [2, 3]


class TestSetComplement:
    """Test set complement operation."""

    def test_set_complement_basic(self):
        """Complement of a set in a universal set."""
        model = ScientificModel(
            id="complement-basic",
            domain="mathematics.discrete_math",
            description="Complement of {2,3} in {1,2,3,4}",
            quantities=[
                Quantity(name="universal", value=[1, 2, 3, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="set_a", value=[2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="comp_result", rhs="set_complement(universal, set_a)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["comp_result"] == [1, 4]


class TestSetSymmetricDifference:
    """Test set symmetric difference operation."""

    def test_set_symmetric_difference_basic(self):
        """Symmetric difference of two sets."""
        model = ScientificModel(
            id="sym-diff-basic",
            domain="mathematics.discrete_math",
            description="Symmetric difference of {1,2,3} and {2,3,4}",
            quantities=[
                Quantity(name="set_a", value=[1, 2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="set_b", value=[2, 3, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="sym_diff", rhs="set_symmetric_difference(set_a, set_b)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["sym_diff"] == [1, 4]


class TestPowerSet:
    """Test power set operation."""

    def test_power_set_basic(self):
        """Power set of {1,2}."""
        model = ScientificModel(
            id="powerset-basic",
            domain="mathematics.discrete_math",
            description="Power set of {1,2}",
            quantities=[
                Quantity(name="set_a", value=[1, 2], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="powerset", rhs="power_set(set_a)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        powerset = result.summary["powerset"]
        # P({1,2}) = {∅, {1}, {2}, {1,2}}
        assert len(powerset) == 4
        assert [] in powerset
        assert [1] in powerset
        assert [2] in powerset
        assert [1, 2] in powerset


# ============================================================================
# Recurrence Relation Tests
# ============================================================================

class TestLinearRecurrence1stOrder:
    """Test 1st-order linear recurrence."""

    def test_1st_order_recurrence_constant_forcing(self):
        """1st-order recurrence: F(n) = 0.5*F(n-1) + 1, F(0)=2."""
        model = ScientificModel(
            id="rec1-const",
            domain="mathematics.discrete_math",
            description="1st-order recurrence F(n)=0.5*F(n-1)+1",
            quantities=[],
            equations=[
                Equation(lhs="f5", rhs="linear_recurrence_1st_order(0.5, 1, 2, 5)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # Closed form: F(n) = 0.5^n*2 + 1*(0.5^n - 1)/(0.5 - 1) = 0.5^n*2 + 2*(1 - 0.5^n)
        # F(5) = 0.03125*2 + 2*(1 - 0.03125) = 0.0625 + 1.9375 = 2
        expected = 0.5**5 * 2 + 1 * (0.5**5 - 1) / (0.5 - 1)
        assert abs(result.summary["f5"] - expected) < 1e-6

    def test_1st_order_recurrence_a_equals_1(self):
        """1st-order recurrence with a=1: F(n) = F(n-1) + 1 (arithmetic progression)."""
        model = ScientificModel(
            id="rec1-a1",
            domain="mathematics.discrete_math",
            description="1st-order recurrence F(n)=F(n-1)+1",
            quantities=[],
            equations=[
                Equation(lhs="f5", rhs="linear_recurrence_1st_order(1, 1, 0, 5)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # F(n) = 0 + 1*n = n
        assert result.summary["f5"] == 5.0


class TestLinearRecurrence2ndOrder:
    """Test 2nd-order linear recurrence."""

    def test_fibonacci_sequence(self):
        """Fibonacci sequence: F(n) = F(n-1) + F(n-2), F(0)=0, F(1)=1."""
        model = ScientificModel(
            id="fib",
            domain="mathematics.discrete_math",
            description="Fibonacci sequence",
            quantities=[],
            equations=[
                Equation(lhs="f10", rhs="linear_recurrence_2nd_order(1, 1, 0, 1, 10)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # F(10) = 55
        assert abs(result.summary["f10"] - 55) < 1e-6

    def test_2nd_order_recurrence_base_cases(self):
        """Test base cases for 2nd-order recurrence."""
        model = ScientificModel(
            id="rec2-base",
            domain="mathematics.discrete_math",
            description="Base cases for 2nd-order",
            quantities=[],
            equations=[
                Equation(lhs="f0", rhs="linear_recurrence_2nd_order(1, 1, 5, 10, 0)",
                        type=EquationType.ALGEBRAIC),
                Equation(lhs="f1", rhs="linear_recurrence_2nd_order(1, 1, 5, 10, 1)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["f0"] == 5.0
        assert result.summary["f1"] == 10.0


class TestNonHomogeneousRecurrence:
    """Test non-homogeneous recurrence relation."""

    def test_non_homogeneous_constant_forcing(self):
        """Non-homogeneous: F(n) = F(n-1) + F(n-2) + 1."""
        model = ScientificModel(
            id="nonhom-const",
            domain="mathematics.discrete_math",
            description="Non-homogeneous recurrence",
            quantities=[
                Quantity(name="forcing", value="1", siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="f5", rhs="non_homogeneous_recurrence(1, 1, 0, 1, 5, forcing)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # Verify by iteration: F(0)=0, F(1)=1, F(2)=0+1+1=2, F(3)=1+2+1=4, F(4)=2+4+1=7, F(5)=4+7+1=12
        assert abs(result.summary["f5"] - 12) < 1e-3  # allow small numeric error


# ============================================================================
# Combinatorics Tests
# ============================================================================

class TestInclusionExclusion:
    """Test inclusion-exclusion principle."""

    def test_inclusion_exclusion_two_sets(self):
        """Union of two sets with intersection: |A∪B| = |A| + |B| - |A∩B|."""
        model = ScientificModel(
            id="ie-two",
            domain="mathematics.discrete_math",
            description="Inclusion-Exclusion for 2 sets",
            quantities=[
                Quantity(name="set_sizes", value=[30, 20], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="inter_sizes", value=[10], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="union_size", rhs="inclusion_exclusion(set_sizes, inter_sizes)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # |A∪B| = 30 + 20 - 10 = 40
        assert result.summary["union_size"] == 40.0


class TestStirlingNumbers:
    """Test Stirling numbers."""

    def test_stirling_1st_kind_basic(self):
        """Stirling number of the first kind s(3, 2)."""
        model = ScientificModel(
            id="stirling1",
            domain="mathematics.discrete_math",
            description="Stirling 1st kind s(3,2)",
            quantities=[],
            equations=[
                Equation(lhs="s32", rhs="stirling_number_1st(3, 2)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # s(3, 2) = 3 (permutations of 3 elements with 2 cycles)
        assert result.summary["s32"] == 3

    def test_stirling_2nd_kind_basic(self):
        """Stirling number of the second kind S(4, 2)."""
        model = ScientificModel(
            id="stirling2",
            domain="mathematics.discrete_math",
            description="Stirling 2nd kind S(4,2)",
            quantities=[],
            equations=[
                Equation(lhs="S42", rhs="stirling_number_2nd(4, 2)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # S(4, 2) = 7 (partitions of 4 elements into 2 non-empty subsets)
        assert result.summary["S42"] == 7


class TestPartitionFunction:
    """Test partition function."""

    def test_partition_function_total(self):
        """Total number of partitions p(5)."""
        model = ScientificModel(
            id="part-5",
            domain="mathematics.discrete_math",
            description="Partition function p(5)",
            quantities=[],
            equations=[
                Equation(lhs="p5", rhs="partition_function(5)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        # p(5) = 7 (partitions: 5, 4+1, 3+2, 3+1+1, 2+2+1, 2+1+1+1, 1+1+1+1+1)
        assert result.summary["p5"] == 7


# ============================================================================
# Boolean Algebra Tests
# ============================================================================

class TestBooleanAlgebra:
    """Test Boolean algebra operations."""

    def test_boolean_and(self):
        """Boolean AND operation."""
        from app.solvers.discrete_math import _boolean_algebra
        assert _boolean_algebra(1, 1, "AND") == 1
        assert _boolean_algebra(0, 1, "AND") == 0
        assert _boolean_algebra(1, 0, "AND") == 0
        assert _boolean_algebra(0, 0, "AND") == 0

    def test_boolean_or(self):
        """Boolean OR operation."""
        from app.solvers.discrete_math import _boolean_algebra
        assert _boolean_algebra(1, 1, "OR") == 1
        assert _boolean_algebra(0, 1, "OR") == 1
        assert _boolean_algebra(1, 0, "OR") == 1
        assert _boolean_algebra(0, 0, "OR") == 0

    def test_boolean_xor(self):
        """Boolean XOR operation."""
        from app.solvers.discrete_math import _boolean_algebra
        assert _boolean_algebra(1, 1, "XOR") == 0
        assert _boolean_algebra(0, 1, "XOR") == 1
        assert _boolean_algebra(1, 0, "XOR") == 1
        assert _boolean_algebra(0, 0, "XOR") == 0

    def test_boolean_not(self):
        """Boolean NOT operation."""
        from app.solvers.discrete_math import _boolean_algebra
        assert _boolean_algebra(1, 0, "NOT") == 0
        assert _boolean_algebra(0, 0, "NOT") == 1


# ============================================================================
# Determinism Tests
# ============================================================================

class TestDeterminism:
    """Test deterministic behavior (solve twice → identical results)."""

    def test_set_union_determinism(self):
        """Set union produces identical results when called twice."""
        model = ScientificModel(
            id="det-union",
            domain="mathematics.discrete_math",
            description="Determinism: set union",
            quantities=[
                Quantity(name="a", value=[3, 1, 2], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="b", value=[4, 2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="result", rhs="set_union(a, b)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)
        assert result1.success and result2.success
        assert result1.summary == result2.summary

    def test_fibonacci_determinism(self):
        """Fibonacci calculation is deterministic."""
        model = ScientificModel(
            id="det-fib",
            domain="mathematics.discrete_math",
            description="Determinism: Fibonacci",
            quantities=[],
            equations=[
                Equation(lhs="fib15", rhs="linear_recurrence_2nd_order(1, 1, 0, 1, 15)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)
        assert result1.success and result2.success
        assert result1.summary["fib15"] == result2.summary["fib15"]


# ============================================================================
# Error Path Tests
# ============================================================================

class TestErrorPaths:
    """Test error handling and invalid inputs."""

    def test_complement_not_subset(self):
        """Error when complement set is not a subset of universal set."""
        model = ScientificModel(
            id="err-comp",
            domain="mathematics.discrete_math",
            description="Error: invalid complement",
            quantities=[
                Quantity(name="u", value=[1, 2, 3], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
                Quantity(name="a", value=[2, 4], siUnit="dimensionless",
                         isKnown=True, dimensionVector=DimensionVector()),
            ],
            equations=[
                Equation(lhs="comp", rhs="set_complement(u, a)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert not result.success
        assert "error" in result.__dict__

    def test_invalid_recurrence_n(self):
        """Error when n is negative or non-integer."""
        model = ScientificModel(
            id="err-rec-n",
            domain="mathematics.discrete_math",
            description="Error: invalid n for recurrence",
            quantities=[],
            equations=[
                Equation(lhs="f_bad", rhs="linear_recurrence_1st_order(0.5, 1, 2, -1)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert not result.success

    def test_boolean_invalid_operation(self):
        """Error with invalid boolean operation."""
        from app.solvers.discrete_math import _boolean_algebra
        with pytest.raises(ValueError):
            _boolean_algebra(1, 0, "INVALID")

    def test_stirling_invalid_range(self):
        """Stirling numbers with k > n returns 0."""
        model = ScientificModel(
            id="stirling-range",
            domain="mathematics.discrete_math",
            description="Stirling k > n",
            quantities=[],
            equations=[
                Equation(lhs="s_result", rhs="stirling_number_2nd(3, 5)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        solver = DiscreteMathSolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["s_result"] == 0


# ============================================================================
# Routing Tests (via GeneralSolver)
# ============================================================================

class TestRouting:
    """Test that GeneralSolver routes to DiscreteMathSolver."""

    def test_routing_to_discrete_math(self):
        """Verify GeneralSolver routes mathematics.discrete_math to correct solver."""
        model = ScientificModel(
            id="route-test",
            domain="mathematics.discrete_math",
            description="Routing test",
            quantities=[],
            equations=[
                Equation(lhs="result", rhs="linear_recurrence_1st_order(2, 3, 1, 4)",
                        type=EquationType.ALGEBRAIC),
            ],
            initialConditions={},
            solver=Solver(method=SolverMethod.SYMBOLIC_SOLVE, tolerance=1e-6),
            metadata=Metadata(source="test")
        )
        general_solver = GeneralSolver()
        result = general_solver.solve(model)
        assert result.success
        # F(n) = 2^n*1 + 3*(2^n - 1)/(2 - 1) = 2^n + 3*(2^n - 1) = 4*2^n - 3
        # F(4) = 4*16 - 3 = 61
        expected = 4 * 2**4 - 3
        assert abs(result.summary["result"] - expected) < 1e-6
