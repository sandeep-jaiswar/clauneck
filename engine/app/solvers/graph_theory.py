"""Graph theory solver (mathematics.graph_theory domain)."""
from typing import Dict, List, Tuple, Any, Union
import numpy as np
import networkx as nx

from app.model import ScientificModel, SolverResult, Quantity
from app.solvers.base import SolverBase
from app.solvers.registry import register
from app.solvers.utils import run_dispatch


def _adjacency_matrix_from_edges(edges: List[List[float]],
                                  num_vertices: float) -> List[List[float]]:
    """
    Convert edge list to adjacency matrix.
    edges: list of [source, target, weight] or [source, target]
    num_vertices: number of vertices in the graph
    Returns adjacency matrix as nested list.
    """
    n = int(num_vertices)
    if n <= 0:
        raise ValueError("Number of vertices must be positive")

    adj_matrix = np.zeros((n, n), dtype=float)

    for edge in edges:
        if len(edge) == 2:
            # Unweighted edge
            u, v = int(edge[0]), int(edge[1])
            weight = 1.0
        elif len(edge) == 3:
            # Weighted edge
            u, v = int(edge[0]), int(edge[1])
            weight = float(edge[2])
        else:
            raise ValueError("Each edge must have 2 or 3 elements")

        if u < 0 or u >= n or v < 0 or v >= n:
            raise ValueError(f"Vertex indices must be in [0, {n-1}]")

        adj_matrix[u, v] = weight
        adj_matrix[v, u] = weight  # Assume undirected

    return adj_matrix.tolist()


def _connected_components(adj_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Find connected components in the graph.
    Returns dict with num_components and component_sizes.
    """
    adj = np.array(adj_matrix, dtype=float)
    # Create graph from adjacency matrix
    G = nx.from_numpy_array(adj)

    components = list(nx.connected_components(G))
    num_components = len(components)
    component_sizes = [len(c) for c in components]

    return {
        "num_components": num_components,
        "component_sizes": component_sizes
    }


def _is_bipartite(adj_matrix: List[List[float]]) -> bool:
    """
    Check if graph is bipartite.
    Returns True if bipartite, False otherwise.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)
    return nx.is_bipartite(G)


def _dijkstra_shortest_path(adj_matrix: List[List[float]],
                            source: float, target: float) -> Dict[str, Any]:
    """
    Find shortest path using Dijkstra's algorithm.
    Assumes non-negative weights.
    Returns dict with path and distance.
    """
    adj = np.array(adj_matrix, dtype=float)
    source, target = int(source), int(target)

    # Check for negative weights
    if np.any(adj < 0):
        raise ValueError("Dijkstra requires non-negative weights")

    G = nx.from_numpy_array(adj)

    try:
        path = nx.shortest_path(G, source=source, target=target, weight='weight')
        distance = nx.shortest_path_length(G, source=source, target=target, weight='weight')
        return {
            "path": [int(v) for v in path],
            "distance": float(distance)
        }
    except nx.NetworkXNoPath:
        raise ValueError(f"No path exists between {source} and {target}")
    except nx.NodeNotFound:
        raise ValueError(f"Invalid source or target vertex")


def _bellman_ford_shortest_path(adj_matrix: List[List[float]],
                                source: float, target: float) -> Dict[str, Any]:
    """
    Find shortest path using Bellman-Ford algorithm.
    Allows negative weights (no negative cycles).
    Returns dict with path and distance.
    """
    adj = np.array(adj_matrix, dtype=float)
    source, target = int(source), int(target)

    G = nx.from_numpy_array(adj)

    try:
        distance, path = nx.single_source_bellman_ford(G, source=source, weight='weight')
        if target not in distance:
            raise ValueError(f"No path exists between {source} and {target}")
        return {
            "path": [int(v) for v in path[target]],
            "distance": float(distance[target])
        }
    except nx.NetworkXError as e:
        raise ValueError(f"Bellman-Ford error: {str(e)}")


def _floyd_warshall_apsp(adj_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    All-pairs shortest paths using Floyd-Warshall.
    Returns dict with distance_matrix and predecessor_matrix.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    # Floyd-Warshall
    distance_matrix = np.full(adj.shape, np.inf)
    n = len(adj)
    for i in range(n):
        distance_matrix[i, i] = 0

    # Initialize with adjacency matrix
    distance_matrix[adj > 0] = adj[adj > 0]

    # Run Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if distance_matrix[i, k] + distance_matrix[k, j] < distance_matrix[i, j]:
                    distance_matrix[i, j] = distance_matrix[i, k] + distance_matrix[k, j]

    # Convert inf to large value for serialization
    distance_matrix_list = []
    for row in distance_matrix:
        distance_matrix_list.append([float(x) if x != np.inf else 1e10 for x in row])

    return {
        "distance_matrix": distance_matrix_list
    }


def _prims_mst(adj_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Minimum spanning tree using Prim's algorithm.
    Returns dict with mst_edges and total_weight.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    if not nx.is_connected(G):
        raise ValueError("Graph must be connected for MST")

    mst = nx.minimum_spanning_tree(G, algorithm='prim', weight='weight')
    edges = [(int(u), int(v), float(mst[u][v]['weight'])) for u, v in mst.edges()]
    total_weight = float(mst.size(weight='weight'))

    return {
        "mst_edges": edges,
        "total_weight": total_weight
    }


def _kruskals_mst(adj_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Minimum spanning tree using Kruskal's algorithm.
    Returns dict with mst_edges and total_weight.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    if not nx.is_connected(G):
        raise ValueError("Graph must be connected for MST")

    mst = nx.minimum_spanning_tree(G, algorithm='kruskal', weight='weight')
    edges = [(int(u), int(v), float(mst[u][v]['weight'])) for u, v in mst.edges()]
    total_weight = float(mst.size(weight='weight'))

    return {
        "mst_edges": edges,
        "total_weight": total_weight
    }


def _graph_coloring(adj_matrix: List[List[float]]) -> Dict[str, Any]:
    """
    Graph coloring using greedy algorithm.
    Returns dict with coloring and chromatic_number.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    # Convert to undirected if not already
    if G.is_directed():
        G = G.to_undirected()

    coloring = nx.greedy_color(G, strategy='largest_first')
    chromatic_num = max(coloring.values()) + 1 if coloring else 0

    # Convert to list format: node -> color
    coloring_list = [coloring.get(i, 0) for i in range(len(adj))]

    return {
        "coloring": coloring_list,
        "chromatic_number": int(chromatic_num)
    }


def _chromatic_polynomial(adj_matrix: List[List[float]], k: float) -> float:
    """
    Evaluate chromatic polynomial at k.
    Computes P(G, k) = number of proper k-colorings.
    Uses NetworkX's chromatic_polynomial (available in newer versions).
    """
    adj = np.array(adj_matrix, dtype=float)
    k = int(k)

    if k <= 0:
        raise ValueError("k must be positive")

    G = nx.from_numpy_array(adj)

    # Convert to undirected
    if G.is_directed():
        G = G.to_undirected()

    # Use deletion-contraction to compute chromatic polynomial value
    # For small graphs, use brute force counting
    if len(G) <= 10:
        # Count valid k-colorings by brute force
        count = _count_k_colorings(G, k)
        return float(count)
    else:
        # For larger graphs, approximate or raise error
        raise ValueError("Chromatic polynomial computation limited to graphs with <=10 vertices")


def _count_k_colorings(G, k):
    """Helper: count valid k-colorings of G by brute force."""
    import itertools

    n = len(G)
    if n == 0:
        return 1

    valid_count = 0
    for coloring in itertools.product(range(k), repeat=n):
        # Check if this coloring is valid (no adjacent vertices same color)
        valid = True
        for u, v in G.edges():
            if coloring[u] == coloring[v]:
                valid = False
                break
        if valid:
            valid_count += 1

    return valid_count


def _degree_centrality(adj_matrix: List[List[float]]) -> Dict[str, List[float]]:
    """
    Compute degree centrality for each vertex.
    Returns dict with degree_centrality as list.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    centrality = nx.degree_centrality(G)
    # Convert to list indexed by vertex
    cent_list = [centrality.get(i, 0.0) for i in range(len(adj))]

    return {
        "degree_centrality": cent_list
    }


def _betweenness_centrality(adj_matrix: List[List[float]]) -> Dict[str, List[float]]:
    """
    Compute betweenness centrality for each vertex.
    Returns dict with betweenness_centrality as list.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    centrality = nx.betweenness_centrality(G, weight='weight')
    # Convert to list indexed by vertex
    cent_list = [centrality.get(i, 0.0) for i in range(len(adj))]

    return {
        "betweenness_centrality": cent_list
    }


def _closeness_centrality(adj_matrix: List[List[float]]) -> Dict[str, List[float]]:
    """
    Compute closeness centrality for each vertex.
    Returns dict with closeness_centrality as list.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    centrality = nx.closeness_centrality(G, distance='weight')
    # Convert to list indexed by vertex
    cent_list = [centrality.get(i, 0.0) for i in range(len(adj))]

    return {
        "closeness_centrality": cent_list
    }


def _graph_diameter(adj_matrix: List[List[float]]) -> float:
    """
    Compute graph diameter (longest shortest path).
    Returns diameter as float.
    """
    adj = np.array(adj_matrix, dtype=float)
    G = nx.from_numpy_array(adj)

    if not nx.is_connected(G):
        raise ValueError("Graph must be connected for diameter computation")

    diameter = nx.diameter(G, e=None)
    return float(diameter)


_OPERATIONS = {
    "adjacency_matrix_from_edges": _adjacency_matrix_from_edges,
    "connected_components": _connected_components,
    "is_bipartite": _is_bipartite,
    "dijkstra_shortest_path": _dijkstra_shortest_path,
    "bellman_ford_shortest_path": _bellman_ford_shortest_path,
    "floyd_warshall_apsp": _floyd_warshall_apsp,
    "prims_mst": _prims_mst,
    "kruskals_mst": _kruskals_mst,
    "graph_coloring": _graph_coloring,
    "chromatic_polynomial": _chromatic_polynomial,
    "degree_centrality": _degree_centrality,
    "betweenness_centrality": _betweenness_centrality,
    "closeness_centrality": _closeness_centrality,
    "graph_diameter": _graph_diameter,
}


@register("mathematics.graph_theory")
class GraphTheorySolver(SolverBase):
    """
    Specialized solver for graph theory: shortest paths, MST, centrality, coloring.
    Supports operations like dijkstra_shortest_path, prims_mst, degree_centrality, etc.
    Uses NetworkX for graph algorithms.
    """

    def solve(self, model: ScientificModel) -> SolverResult:
        """
        Solve graph theory problems using function-dispatch pattern.
        Equations expected: function_name(arg1, arg2, ...) format in rhs.
        """
        try:
            quantities = {q.name: q for q in model.quantities}

            # Dispatch to operations and accumulate results
            summary = run_dispatch(model, quantities, _OPERATIONS)

            return SolverResult(
                success=True,
                message="Graph theory solved successfully",
                summary=summary
            )

        except Exception as e:
            return SolverResult(
                success=False,
                message="Solver error",
                error=str(e)
            )
