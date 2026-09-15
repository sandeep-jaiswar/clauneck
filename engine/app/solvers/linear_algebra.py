"""Linear algebra solver (mathematics.linear_algebra domain)."""
from typing import Dict, Any, List, Union
import numpy as np
from sympy import Matrix as SymPyMatrix
from sympy import symbols, simplify

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register


@register("mathematics.linear_algebra")
class LinearAlgebraSolver(SolverBase):
    """
    Specialized solver for linear algebra operations.
    Supports: determinant, inverse, rank, transpose, eigenvalues, eigenvectors, solve Ax=b.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve linear algebra operations.
        Equations expected in form: "det(A)", "inv(A)", "rank(A)", "transpose(A)",
        "eigenvalues(A)", "eigenvectors(A)", "solve(A @ x, b)".
        """
        try:
            # Extract quantities
            quantities = {q.name: q for q in model.quantities}

            # Parse each equation as an operation
            operations = {}
            for equation in model.equations:
                # LHS is the operation name, RHS is the result variable (or ignored)
                op_expr = equation.lhs.strip()
                operations[op_expr] = equation

            # Compute results for each operation
            results = {}
            for op_name, equation in operations.items():
                try:
                    result = self._compute_operation(op_name, quantities)
                    results[op_name] = result
                except Exception as e:
                    return SolverResult(
                        success=False,
                        message=f"Failed to compute operation {op_name}: {str(e)}",
                        error=str(e)
                    )

            return SolverResult(
                success=True,
                message="Linear algebra operations computed successfully",
                summary=results
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )

    def _compute_operation(self, op_expr: str, quantities: Dict[str, Quantity]) -> Any:
        """
        Parse and compute a linear algebra operation.
        Supports: det(A), inv(A), rank(A), transpose(A),
                  eigenvalues(A), eigenvectors(A), solve(A @ x, b).
        """
        op_expr = op_expr.strip()

        # Parse operation type and arguments
        if op_expr.startswith("det(") and op_expr.endswith(")"):
            matrix_name = op_expr[4:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            result = float(np.linalg.det(matrix))
            return result

        elif op_expr.startswith("inv(") and op_expr.endswith(")"):
            matrix_name = op_expr[4:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            inv_matrix = np.linalg.inv(matrix)
            return inv_matrix.tolist()

        elif op_expr.startswith("rank(") and op_expr.endswith(")"):
            matrix_name = op_expr[5:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            rank = int(np.linalg.matrix_rank(matrix))
            return rank

        elif op_expr.startswith("transpose(") and op_expr.endswith(")"):
            matrix_name = op_expr[10:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            transposed = matrix.T
            return transposed.tolist()

        elif op_expr.startswith("eigenvalues(") and op_expr.endswith(")"):
            matrix_name = op_expr[12:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            eigenvals = np.linalg.eigvals(matrix)
            # Return as list of floats (real part if complex with negligible imaginary)
            result = []
            for ev in eigenvals:
                if np.isreal(ev):
                    result.append(float(np.real(ev)))
                else:
                    # For complex eigenvalues, return as dict with real and imag parts
                    result.append({"real": float(np.real(ev)), "imag": float(np.imag(ev))})
            return result

        elif op_expr.startswith("eigenvectors(") and op_expr.endswith(")"):
            matrix_name = op_expr[13:-1].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            eigenvals, eigenvecs = np.linalg.eig(matrix)
            # Return as dict with eigenvalues and eigenvectors
            evecs_list = []
            eigenvals_list = []
            for i, ev in enumerate(eigenvals):
                if np.isreal(ev):
                    eigenvals_list.append(float(np.real(ev)))
                else:
                    eigenvals_list.append({"real": float(np.real(ev)), "imag": float(np.imag(ev))})
                evec = eigenvecs[:, i]
                if np.iscomplexobj(evec):
                    evecs_list.append([{"real": float(np.real(x)), "imag": float(np.imag(x))} for x in evec])
                else:
                    evecs_list.append([float(x) for x in evec])
            return {
                "eigenvalues": eigenvals_list,
                "eigenvectors": evecs_list
            }

        elif "solve(" in op_expr and "@" in op_expr and op_expr.endswith(")"):
            # Parse "solve(A @ x, b)"
            parts = op_expr[6:-1].split(",")
            if len(parts) != 2:
                raise ValueError(f"Invalid solve syntax: {op_expr}")

            lhs_expr = parts[0].strip()  # "A @ x"
            rhs_name = parts[1].strip()  # "b"

            # Parse "A @ x"
            if " @ " not in lhs_expr:
                raise ValueError(f"Expected 'A @ x' in {lhs_expr}")

            matrix_name = lhs_expr.split(" @ ")[0].strip()
            matrix = self._get_matrix(quantities, matrix_name)
            vector = self._get_vector(quantities, rhs_name)

            # Solve Ax = b
            solution = np.linalg.solve(matrix, vector)
            return solution.tolist()

        else:
            raise ValueError(f"Unsupported operation: {op_expr}")

    def _get_matrix(self, quantities: Dict[str, Quantity], name: str) -> np.ndarray:
        """
        Extract a matrix from quantities.
        Matrix should have value as nested list [[...], [...], ...].
        """
        if name not in quantities:
            raise ValueError(f"Quantity '{name}' not found")

        quantity = quantities[name]
        if quantity.value is None:
            raise ValueError(f"Quantity '{name}' has no value")

        if not isinstance(quantity.value, list):
            raise ValueError(f"Expected matrix (nested list) for '{name}', got {type(quantity.value)}")

        # Convert to numpy array
        try:
            matrix = np.array(quantity.value, dtype=float)
            if matrix.ndim != 2:
                raise ValueError(f"Expected 2D matrix for '{name}', got {matrix.ndim}D")
            return matrix
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot convert '{name}' to matrix: {str(e)}")

    def _get_vector(self, quantities: Dict[str, Quantity], name: str) -> np.ndarray:
        """
        Extract a vector from quantities.
        Vector should have value as list [...]  or be a single column 2D array.
        """
        if name not in quantities:
            raise ValueError(f"Quantity '{name}' not found")

        quantity = quantities[name]
        if quantity.value is None:
            raise ValueError(f"Quantity '{name}' has no value")

        if not isinstance(quantity.value, list):
            raise ValueError(f"Expected vector (array) for '{name}', got {type(quantity.value)}")

        # Convert to numpy array
        try:
            vector = np.array(quantity.value, dtype=float)
            if vector.ndim == 1:
                return vector
            elif vector.ndim == 2 and vector.shape[1] == 1:
                return vector.flatten()
            else:
                raise ValueError(f"Expected 1D vector for '{name}', got shape {vector.shape}")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot convert '{name}' to vector: {str(e)}")
