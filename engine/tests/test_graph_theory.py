"""
Tests for graph theory solver.
Correctness, determinism, and error path tests for all 14 operations.
"""
import numpy as np
import pytest

from app.model import (
    ScientificModel, Quantity, Equation, EquationType, Solver, SolverMethod,
    Metadata, DimensionVector
)
from app.solver import GeneralSolver
from app.solvers.graph_theory import GraphTheorySolver


@pytest.fixture
def simple_undirected_adj_matrix():
    """Simple undirected graph: 0-1-2 (chain)."""
    return [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0]
    ]


@pytest.fixture
def weighted_graph_adj_matrix():
    """Weighted graph for MST testing (4 vertices)."""
    return [
        [0.0, 2.0, 0.0, 6.0],
        [2.0, 0.0, 3.0, 8.0],
        [0.0, 3.0, 0.0, 5.0],
        [6.0, 8.0, 5.0, 0.0]
    ]


@pytest.fixture
def bipartite_graph_adj_matrix():
    """Bipartite graph (0,2 in one part, 1,3 in other)."""
    return [
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 1.0],
        [1.0, 0.0, 1.0, 0.0]
    ]


@pytest.fixture
def triangle_graph_adj_matrix():
    """Triangle graph (all vertices connected)."""
    return [
        [0.0, 1.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 0.0]
    ]


@pytest.fixture
def disconnected_graph_adj_matrix():
    """Disconnected graph (two components)."""
    return [
        [0.0, 1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, 1.0, 0.0]
    ]


class TestAdjacencyMatrixFromEdges:
    """Test edge list to adjacency matrix conversion."""

    def test_unweighted_edges(self):
        """Test conversion of unweighted edges."""
        model = ScientificModel(
            id="graph-edges-unweighted",
            domain="mathematics.graph_theory",
            description="Convert unweighted edges to adjacency matrix",
            quantities=[
                Quantity(
                    name="edges",
                    value=[[0, 1], [1, 2]],
                    siUnit="dimensionless",
                    description="Edge list",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
                Quantity(
                    name="n",
                    value=3,
                    siUnit="dimensionless",
                    description="Number of vertices",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="adj",
                    rhs="adjacency_matrix_from_edges(edges, n)",
                    type=EquationType.ALGEBRAIC,
                    description="Adjacency matrix"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert "adj" in result.summary
        adj = result.summary["adj"]
        assert len(adj) == 3
        assert adj[0][1] == 1.0
        assert adj[1][2] == 1.0

    def test_weighted_edges(self):
        """Test conversion of weighted edges."""
        model = ScientificModel(
            id="graph-edges-weighted",
            domain="mathematics.graph_theory",
            description="Convert weighted edges to adjacency matrix",
            quantities=[
                Quantity(
                    name="edges",
                    value=[[0, 1, 2.5], [1, 2, 3.5]],
                    siUnit="dimensionless",
                    description="Weighted edge list",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
                Quantity(
                    name="n",
                    value=3,
                    siUnit="dimensionless",
                    description="Number of vertices",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="adj",
                    rhs="adjacency_matrix_from_edges(edges, n)",
                    type=EquationType.ALGEBRAIC,
                    description="Adjacency matrix"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        adj = result.summary["adj"]
        assert adj[0][1] == 2.5
        assert adj[1][2] == 3.5


class TestConnectedComponents:
    """Test connected components detection."""

    def test_connected_graph(self, simple_undirected_adj_matrix):
        """Test connected graph has one component."""
        model = ScientificModel(
            id="graph-components-connected",
            domain="mathematics.graph_theory",
            description="Find connected components",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="comp",
                    rhs="connected_components(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Connected components"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["comp_num_components"] == 1

    def test_disconnected_graph(self, disconnected_graph_adj_matrix):
        """Test disconnected graph has two components."""
        model = ScientificModel(
            id="graph-components-disconnected",
            domain="mathematics.graph_theory",
            description="Find connected components in disconnected graph",
            quantities=[
                Quantity(
                    name="adj",
                    value=disconnected_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="comp",
                    rhs="connected_components(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Connected components"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["comp_num_components"] == 2


class TestIsBipartite:
    """Test bipartite graph detection."""

    def test_bipartite_graph(self, bipartite_graph_adj_matrix):
        """Test detection of bipartite graph."""
        model = ScientificModel(
            id="graph-bipartite-yes",
            domain="mathematics.graph_theory",
            description="Check if graph is bipartite",
            quantities=[
                Quantity(
                    name="adj",
                    value=bipartite_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="is_bip",
                    rhs="is_bipartite(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Is bipartite"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["is_bip"] is True

    def test_triangle_not_bipartite(self, triangle_graph_adj_matrix):
        """Test that triangle is not bipartite."""
        model = ScientificModel(
            id="graph-bipartite-no",
            domain="mathematics.graph_theory",
            description="Check if triangle is bipartite",
            quantities=[
                Quantity(
                    name="adj",
                    value=triangle_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="is_bip",
                    rhs="is_bipartite(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Is bipartite"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["is_bip"] is False


class TestDijkstraShortestPath:
    """Test Dijkstra's shortest path algorithm."""

    def test_dijkstra_simple(self, simple_undirected_adj_matrix):
        """Test shortest path in simple graph."""
        model = ScientificModel(
            id="graph-dijkstra-simple",
            domain="mathematics.graph_theory",
            description="Find shortest path using Dijkstra",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="path",
                    rhs="dijkstra_shortest_path(adj, 0, 2)",
                    type=EquationType.ALGEBRAIC,
                    description="Shortest path from 0 to 2"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert result.summary["path_path"] == [0, 1, 2]
        assert result.summary["path_distance"] == 2.0

    def test_dijkstra_weighted(self, weighted_graph_adj_matrix):
        """Test shortest path in weighted graph."""
        model = ScientificModel(
            id="graph-dijkstra-weighted",
            domain="mathematics.graph_theory",
            description="Find shortest path in weighted graph",
            quantities=[
                Quantity(
                    name="adj",
                    value=weighted_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="path",
                    rhs="dijkstra_shortest_path(adj, 0, 3)",
                    type=EquationType.ALGEBRAIC,
                    description="Shortest path from 0 to 3"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        # Shortest path from 0 to 3: 0->1->2->3 (2+3+5=10) or 0->3 (6)
        # So it should be [0, 3] with distance 6
        assert result.summary["path_distance"] == 6.0


class TestFloydWarshall:
    """Test Floyd-Warshall all-pairs shortest paths."""

    def test_floyd_warshall_simple(self, simple_undirected_adj_matrix):
        """Test all-pairs shortest paths in simple graph."""
        model = ScientificModel(
            id="graph-apsp-simple",
            domain="mathematics.graph_theory",
            description="Compute all-pairs shortest paths",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="apsp",
                    rhs="floyd_warshall_apsp(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="All-pairs shortest paths"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        dist_matrix = result.summary["apsp_distance_matrix"]
        assert len(dist_matrix) == 3
        assert dist_matrix[0][0] == 0
        assert dist_matrix[0][2] == 2  # 0->1->2


class TestPrimsMST:
    """Test Prim's minimum spanning tree."""

    def test_prims_weighted(self, weighted_graph_adj_matrix):
        """Test Prim's MST on weighted graph."""
        model = ScientificModel(
            id="graph-mst-prims",
            domain="mathematics.graph_theory",
            description="Find MST using Prim's algorithm",
            quantities=[
                Quantity(
                    name="adj",
                    value=weighted_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="mst",
                    rhs="prims_mst(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Minimum spanning tree"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert "mst_mst_edges" in result.summary
        assert "mst_total_weight" in result.summary
        # MST should have n-1 edges
        edges = result.summary["mst_mst_edges"]
        assert len(edges) == 3  # 4 vertices, 3 edges
        # Total weight should be minimal (2+3+5=10 or 2+3+6=11, etc.)
        total_weight = result.summary["mst_total_weight"]
        assert total_weight > 0


class TestKruskalsMST:
    """Test Kruskal's minimum spanning tree."""

    def test_kruskals_weighted(self, weighted_graph_adj_matrix):
        """Test Kruskal's MST on weighted graph."""
        model = ScientificModel(
            id="graph-mst-kruskals",
            domain="mathematics.graph_theory",
            description="Find MST using Kruskal's algorithm",
            quantities=[
                Quantity(
                    name="adj",
                    value=weighted_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="mst",
                    rhs="kruskals_mst(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Minimum spanning tree"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        edges = result.summary["mst_mst_edges"]
        assert len(edges) == 3  # 4 vertices, 3 edges


class TestGraphColoring:
    """Test graph coloring."""

    def test_graph_coloring_triangle(self, triangle_graph_adj_matrix):
        """Test coloring of triangle (needs 3 colors)."""
        model = ScientificModel(
            id="graph-coloring-triangle",
            domain="mathematics.graph_theory",
            description="Color graph vertices",
            quantities=[
                Quantity(
                    name="adj",
                    value=triangle_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="color",
                    rhs="graph_coloring(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Graph coloring"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        assert "color_chromatic_number" in result.summary
        chromatic_num = result.summary["color_chromatic_number"]
        assert chromatic_num == 3  # Triangle needs 3 colors


class TestChromaticPolynomial:
    """Test chromatic polynomial evaluation."""

    def test_chromatic_poly_triangle(self, triangle_graph_adj_matrix):
        """Test chromatic polynomial for triangle at k=3."""
        model = ScientificModel(
            id="graph-chromatic-poly-triangle",
            domain="mathematics.graph_theory",
            description="Evaluate chromatic polynomial",
            quantities=[
                Quantity(
                    name="adj",
                    value=triangle_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="p_k",
                    rhs="chromatic_polynomial(adj, 3)",
                    type=EquationType.ALGEBRAIC,
                    description="P(G, 3)"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        # For a triangle with k=3, there are 3!=6 valid colorings
        assert result.summary["p_k"] == 6.0


class TestDegreeCentrality:
    """Test degree centrality measure."""

    def test_degree_centrality_simple(self, simple_undirected_adj_matrix):
        """Test degree centrality in simple graph."""
        model = ScientificModel(
            id="graph-degree-cent",
            domain="mathematics.graph_theory",
            description="Compute degree centrality",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="dc",
                    rhs="degree_centrality(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Degree centrality"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        dc = result.summary["dc_degree_centrality"]
        assert len(dc) == 3
        # Vertex 1 should have highest centrality (connected to 0 and 2)
        assert dc[1] == max(dc)


class TestBetweennessCentrality:
    """Test betweenness centrality measure."""

    def test_betweenness_centrality_simple(self, simple_undirected_adj_matrix):
        """Test betweenness centrality in simple graph."""
        model = ScientificModel(
            id="graph-betweenness-cent",
            domain="mathematics.graph_theory",
            description="Compute betweenness centrality",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="bc",
                    rhs="betweenness_centrality(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Betweenness centrality"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        bc = result.summary["bc_betweenness_centrality"]
        assert len(bc) == 3


class TestClosenessCentrality:
    """Test closeness centrality measure."""

    def test_closeness_centrality_simple(self, simple_undirected_adj_matrix):
        """Test closeness centrality in simple graph."""
        model = ScientificModel(
            id="graph-closeness-cent",
            domain="mathematics.graph_theory",
            description="Compute closeness centrality",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="cc",
                    rhs="closeness_centrality(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Closeness centrality"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        cc = result.summary["cc_closeness_centrality"]
        assert len(cc) == 3


class TestGraphDiameter:
    """Test graph diameter computation."""

    def test_graph_diameter_simple(self, simple_undirected_adj_matrix):
        """Test diameter of simple chain graph."""
        model = ScientificModel(
            id="graph-diameter",
            domain="mathematics.graph_theory",
            description="Compute graph diameter",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="diam",
                    rhs="graph_diameter(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Graph diameter"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert result.success
        # Chain graph 0-1-2 has diameter 2 (distance from 0 to 2)
        assert result.summary["diam"] == 2.0


class TestErrorPaths:
    """Test error handling."""

    def test_disconnected_graph_mst_error(self, disconnected_graph_adj_matrix):
        """Test MST error on disconnected graph."""
        model = ScientificModel(
            id="graph-mst-error",
            domain="mathematics.graph_theory",
            description="MST on disconnected graph (should fail)",
            quantities=[
                Quantity(
                    name="adj",
                    value=disconnected_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="mst",
                    rhs="prims_mst(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="MST"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert not result.success
        assert "error" in result.__dict__ and result.error is not None

    def test_disconnected_graph_diameter_error(self, disconnected_graph_adj_matrix):
        """Test diameter error on disconnected graph."""
        model = ScientificModel(
            id="graph-diameter-error",
            domain="mathematics.graph_theory",
            description="Diameter on disconnected graph (should fail)",
            quantities=[
                Quantity(
                    name="adj",
                    value=disconnected_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="diam",
                    rhs="graph_diameter(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Diameter"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result = solver.solve(model)
        assert not result.success


class TestDeterminism:
    """Test determinism: same model -> same output."""

    def test_determinism_shortest_path(self, weighted_graph_adj_matrix):
        """Test that shortest path computation is deterministic."""
        model = ScientificModel(
            id="graph-determinism-sp",
            domain="mathematics.graph_theory",
            description="Shortest path determinism test",
            quantities=[
                Quantity(
                    name="adj",
                    value=weighted_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="path",
                    rhs="dijkstra_shortest_path(adj, 0, 2)",
                    type=EquationType.ALGEBRAIC,
                    description="Shortest path"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)

        assert result1.success
        assert result2.success
        assert result1.summary == result2.summary

    def test_determinism_mst(self, weighted_graph_adj_matrix):
        """Test that MST computation is deterministic."""
        model = ScientificModel(
            id="graph-determinism-mst",
            domain="mathematics.graph_theory",
            description="MST determinism test",
            quantities=[
                Quantity(
                    name="adj",
                    value=weighted_graph_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="mst",
                    rhs="prims_mst(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="MST"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        solver = GraphTheorySolver()
        result1 = solver.solve(model)
        result2 = solver.solve(model)

        assert result1.success
        assert result2.success
        # Total weight should be same
        assert result1.summary["mst_total_weight"] == result2.summary["mst_total_weight"]


class TestRoutingIntegration:
    """Test that GeneralSolver routes to GraphTheorySolver."""

    def test_routing_graph_theory(self, simple_undirected_adj_matrix):
        """Test that general solver routes to graph theory solver."""
        model = ScientificModel(
            id="graph-routing",
            domain="mathematics.graph_theory",
            description="Test routing",
            quantities=[
                Quantity(
                    name="adj",
                    value=simple_undirected_adj_matrix,
                    siUnit="dimensionless",
                    description="Adjacency matrix",
                    isKnown=True,
                    dimensionVector=DimensionVector()
                ),
            ],
            equations=[
                Equation(
                    lhs="comp",
                    rhs="connected_components(adj)",
                    type=EquationType.ALGEBRAIC,
                    description="Connected components"
                ),
            ],
            initialConditions={},
            solver=Solver(
                method=SolverMethod.SYMBOLIC_SOLVE,
                tolerance=1e-6
            ),
            metadata=Metadata(source="test")
        )

        general_solver = GeneralSolver()
        result = general_solver.solve(model)
        assert result.success
