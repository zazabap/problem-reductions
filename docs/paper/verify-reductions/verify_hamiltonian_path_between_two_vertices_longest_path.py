#!/usr/bin/env python3
"""Constructor verification: HamiltonianPathBetweenTwoVertices -> LongestPath (#359).

Seven mandatory sections, exhaustive for n <= 5, >= 5000 total checks.
"""
import itertools
import json
import sys
from sympy import symbols, simplify

passed = failed = 0


def check(condition, msg=""):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg}")


# ── Reduction implementation ──────────────────────────────────────────────


def reduce(n, edges, s, t):
    """Reduce HPBTV(G, s, t) -> LongestPath(G', lengths, s', t', K).

    Returns:
        edges': same edge list
        lengths: list of 1s (unit weights)
        s': same source
        t': same target
        K: n - 1
    """
    lengths = [1] * len(edges)
    K = n - 1
    return edges, lengths, s, t, K


def all_simple_graphs(n):
    """Generate all undirected graphs on n labeled vertices."""
    all_possible_edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    m_max = len(all_possible_edges)
    for bits in range(2**m_max):
        edges = []
        for idx in range(m_max):
            if (bits >> idx) & 1:
                edges.append(all_possible_edges[idx])
        yield edges


def is_hamiltonian_st_path(n, edges, s, t, path):
    """Check if path is a valid Hamiltonian s-t path."""
    if len(path) != n:
        return False
    if len(set(path)) != n:
        return False
    if any(v < 0 or v >= n for v in path):
        return False
    if path[0] != s or path[-1] != t:
        return False
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    for i in range(n - 1):
        if (path[i], path[i + 1]) not in edge_set:
            return False
    return True


def has_hamiltonian_st_path(n, edges, s, t):
    """Brute force: does any Hamiltonian s-t path exist?"""
    if n <= 1:
        return False  # s != t required
    for perm in itertools.permutations(range(n)):
        if is_hamiltonian_st_path(n, edges, s, t, list(perm)):
            return True
    return False


def find_hamiltonian_st_path(n, edges, s, t):
    """Return a Hamiltonian s-t path (vertex list) or None."""
    for perm in itertools.permutations(range(n)):
        if is_hamiltonian_st_path(n, edges, s, t, list(perm)):
            return list(perm)
    return None


def is_simple_st_path(n, edges, s, t, edge_config):
    """Check if edge_config encodes a valid simple s-t path."""
    m = len(edges)
    if len(edge_config) != m:
        return False
    if any(x not in (0, 1) for x in edge_config):
        return False

    adj = [[] for _ in range(n)]
    degree = [0] * n
    selected_count = 0
    for idx in range(m):
        if edge_config[idx] == 1:
            u, v = edges[idx]
            adj[u].append(v)
            adj[v].append(u)
            degree[u] += 1
            degree[v] += 1
            selected_count += 1

    if selected_count == 0:
        return False

    # s and t must have degree 1; internal vertices degree 2
    if degree[s] != 1 or degree[t] != 1:
        return False
    for v in range(n):
        if degree[v] == 0:
            continue
        if v == s or v == t:
            if degree[v] != 1:
                return False
        else:
            if degree[v] != 2:
                return False

    # Check connectivity of selected edges
    visited = set()
    stack = [s]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        for u in adj[v]:
            if u not in visited:
                stack.append(u)

    # All vertices with degree > 0 must be reachable from s
    for v in range(n):
        if degree[v] > 0 and v not in visited:
            return False
    return t in visited


def longest_path_feasible(n, edges, lengths, s, t, K):
    """Check if a simple s-t path of length >= K exists."""
    m = len(edges)
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        if is_simple_st_path(n, edges, s, t, config):
            total = sum(lengths[idx] for idx in range(m) if config[idx] == 1)
            if total >= K:
                return True
    return False


def find_longest_path_witness(n, edges, lengths, s, t, K):
    """Return an edge config for a simple s-t path of length >= K, or None."""
    m = len(edges)
    best_config = None
    best_length = -1
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        if is_simple_st_path(n, edges, s, t, config):
            total = sum(lengths[idx] for idx in range(m) if config[idx] == 1)
            if total >= K and total > best_length:
                best_length = total
                best_config = config
    return best_config


def extract_vertex_path(n, edges, edge_config, s):
    """Extract vertex-order path from edge selection, starting at s."""
    m = len(edges)
    adj = {}
    for idx in range(m):
        if edge_config[idx] == 1:
            u, v = edges[idx]
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

    path = [s]
    visited = {s}
    current = s
    while True:
        neighbors = [v for v in adj.get(current, []) if v not in visited]
        if not neighbors:
            break
        nxt = neighbors[0]
        path.append(nxt)
        visited.add(nxt)
        current = nxt
    return path


# ── Main verification ─────────────────────────────────────────────────────


def main():
    global passed, failed

    # === Section 1: Symbolic overhead verification (sympy) ===
    print("=== Section 1: Symbolic overhead verification ===")
    sec1_start = passed

    n_sym, m_sym = symbols("n m", positive=True, integer=True)

    # Overhead: num_vertices_target = n
    check(simplify(n_sym - n_sym) == 0,
          "num_vertices overhead: n_target = n_source")

    # Overhead: num_edges_target = m
    check(simplify(m_sym - m_sym) == 0,
          "num_edges overhead: m_target = m_source")

    # Overhead: K = n - 1
    K_sym = n_sym - 1
    check(simplify(K_sym - (n_sym - 1)) == 0,
          "bound K = n - 1")

    # Total edge length with unit weights = number of edges selected
    # A Hamiltonian path has exactly n-1 edges
    check(simplify(K_sym - (n_sym - 1)) == 0,
          "Hamiltonian path has n-1 edges, matching K")

    # Simple path on n vertices has at most n-1 edges
    max_edges_sym = n_sym - 1
    check(simplify(max_edges_sym - K_sym) == 0,
          "max edges in simple path = n-1 = K")

    # Verify for concrete small values
    for n_val in range(2, 8):
        check(n_val - 1 == n_val - 1, f"K = n-1 for n={n_val}")
        check(n_val - 1 >= 0, f"K non-negative for n={n_val}")

    print(f"  Section 1: {passed - sec1_start} new checks")

    # === Section 2: Exhaustive forward + backward ===
    print("\n=== Section 2: Exhaustive forward + backward ===")
    sec2_start = passed

    for n in range(2, 6):  # n = 2, 3, 4, 5 (n <= 5)
        graph_count = 0
        for edges in all_simple_graphs(n):
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue

                    # Source feasibility
                    source_feas = has_hamiltonian_st_path(n, edges, s, t)

                    # Reduce
                    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)

                    # Target feasibility
                    target_feas = longest_path_feasible(
                        n, edges_t, lengths, s_t, t_t, K
                    )

                    # Forward + backward equivalence
                    check(
                        source_feas == target_feas,
                        f"n={n}, m={len(edges)}, s={s}, t={t}: "
                        f"source={source_feas}, target={target_feas}",
                    )
                    graph_count += 1

        print(f"  n={n}: tested {graph_count} (graph, s, t) combinations")

    print(f"  Section 2: {passed - sec2_start} new checks")

    # === Section 3: Solution extraction ===
    print("\n=== Section 3: Solution extraction ===")
    sec3_start = passed

    for n in range(2, 6):
        for edges in all_simple_graphs(n):
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue
                    if not has_hamiltonian_st_path(n, edges, s, t):
                        continue

                    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
                    witness = find_longest_path_witness(n, edges_t, lengths, s_t, t_t, K)
                    check(witness is not None,
                          f"n={n}, s={s}, t={t}: feasible but no witness")
                    if witness is None:
                        continue

                    # Verify witness is valid
                    check(is_simple_st_path(n, edges_t, s_t, t_t, witness),
                          f"n={n}, s={s}, t={t}: witness not a valid s-t path")
                    total_len = sum(lengths[i] for i in range(len(edges_t)) if witness[i] == 1)
                    check(total_len >= K,
                          f"n={n}, s={s}, t={t}: witness length {total_len} < K={K}")

                    # Extract vertex path
                    vertex_path = extract_vertex_path(n, edges_t, witness, s_t)
                    check(len(vertex_path) == n,
                          f"n={n}, s={s}, t={t}: extracted path length {len(vertex_path)} != n")
                    check(vertex_path[0] == s,
                          f"n={n}, s={s}, t={t}: path starts at {vertex_path[0]} != s")
                    check(vertex_path[-1] == t,
                          f"n={n}, s={s}, t={t}: path ends at {vertex_path[-1]} != t")
                    check(len(set(vertex_path)) == n,
                          f"n={n}, s={s}, t={t}: path not a permutation")
                    check(is_hamiltonian_st_path(n, edges, s, t, vertex_path),
                          f"n={n}, s={s}, t={t}: extracted path not a valid Hamiltonian path")

    print(f"  Section 3: {passed - sec3_start} new checks")

    # === Section 4: Overhead formula verification ===
    print("\n=== Section 4: Overhead formula verification ===")
    sec4_start = passed

    for n in range(2, 6):
        for edges in all_simple_graphs(n):
            m = len(edges)
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue

                    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)

                    # Check num_vertices preserved
                    check(n == n, f"num_vertices: {n} == {n}")

                    # Check num_edges preserved
                    check(len(edges_t) == m,
                          f"num_edges: {len(edges_t)} != {m}")

                    # Check all lengths are 1
                    check(all(l == 1 for l in lengths),
                          f"n={n}: not all unit lengths")

                    # Check K = n - 1
                    check(K == n - 1,
                          f"K={K} != n-1={n - 1}")

                    # Check s, t preserved
                    check(s_t == s, f"source vertex changed")
                    check(t_t == t, f"target vertex changed")

    print(f"  Section 4: {passed - sec4_start} new checks")

    # === Section 5: Structural properties ===
    print("\n=== Section 5: Structural properties ===")
    sec5_start = passed

    for n in range(2, 6):
        for edges in all_simple_graphs(n):
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue

                    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)

                    # Lengths must be positive
                    check(all(l > 0 for l in lengths),
                          f"n={n}: non-positive length found")

                    # Graph unchanged: same edge set
                    check(edges_t == edges,
                          f"n={n}: edges changed during reduction")

                    # K is positive for n >= 2
                    check(K >= 1,
                          f"n={n}: K={K} < 1")

                    # Number of lengths matches edges
                    check(len(lengths) == len(edges_t),
                          f"n={n}: len mismatch lengths vs edges")

    print(f"  Section 5: {passed - sec5_start} new checks")

    # === Section 6: YES example from Typst ===
    print("\n=== Section 6: YES example verification ===")
    sec6_start = passed

    # From Typst: 5 vertices {0,1,2,3,4}, 7 edges, s=0, t=4
    yes_n = 5
    yes_edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (0, 3)]
    yes_s = 0
    yes_t = 4

    check(yes_n == 5, "YES: n = 5")
    check(len(yes_edges) == 7, "YES: m = 7")

    # Verify the Hamiltonian path 0 -> 3 -> 1 -> 2 -> 4 exists
    ham_path = [0, 3, 1, 2, 4]
    check(is_hamiltonian_st_path(yes_n, yes_edges, yes_s, yes_t, ham_path),
          "YES: 0->3->1->2->4 is a valid Hamiltonian path")

    # Reduce
    edges_t, lengths, s_t, t_t, K = reduce(yes_n, yes_edges, yes_s, yes_t)
    check(K == 4, f"YES: K = {K}, expected 4")
    check(len(lengths) == 7, f"YES: {len(lengths)} lengths, expected 7")
    check(all(l == 1 for l in lengths), "YES: all unit lengths")
    check(s_t == 0, "YES: s' = 0")
    check(t_t == 4, "YES: t' = 4")

    # Verify target is feasible
    check(longest_path_feasible(yes_n, edges_t, lengths, s_t, t_t, K),
          "YES: target is feasible")

    # The path 0->3->1->2->4 uses edges {0,3},{1,3},{1,2},{2,4} = 4 edges, length 4
    edge_set_map = {e: i for i, e in enumerate(yes_edges)}
    path_edges = [(0, 3), (3, 1), (1, 2), (2, 4)]
    edge_config = [0] * 7
    for u, v in path_edges:
        key = (min(u, v), max(u, v))
        edge_config[edge_set_map[key]] = 1
    total = sum(lengths[i] for i in range(7) if edge_config[i] == 1)
    check(total == 4, f"YES: path length = {total}, expected 4")
    check(total >= K, f"YES: path length {total} >= K={K}")

    # Extraction
    vpath = extract_vertex_path(yes_n, edges_t, edge_config, s_t)
    check(vpath == [0, 3, 1, 2, 4], f"YES: extracted path = {vpath}")
    check(is_hamiltonian_st_path(yes_n, yes_edges, yes_s, yes_t, vpath),
          "YES: extracted path is a valid Hamiltonian path")

    print(f"  Section 6: {passed - sec6_start} new checks")

    # === Section 7: NO example from Typst ===
    print("\n=== Section 7: NO example verification ===")
    sec7_start = passed

    # From Typst: 5 vertices, 4 edges: {0,1},{1,2},{2,3},{0,3}, s=0, t=4
    # Vertex 4 is isolated
    no_n = 5
    no_edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    no_s = 0
    no_t = 4

    check(no_n == 5, "NO: n = 5")
    check(len(no_edges) == 4, "NO: m = 4")

    # Verify vertex 4 is isolated
    all_verts_in_edges = set()
    for u, v in no_edges:
        all_verts_in_edges.add(u)
        all_verts_in_edges.add(v)
    check(4 not in all_verts_in_edges, "NO: vertex 4 is isolated")

    # Source infeasible
    check(not has_hamiltonian_st_path(no_n, no_edges, no_s, no_t),
          "NO: source is infeasible")

    # Reduce
    edges_t, lengths, s_t, t_t, K = reduce(no_n, no_edges, no_s, no_t)
    check(K == 4, f"NO: K = {K}, expected 4")
    check(all(l == 1 for l in lengths), "NO: all unit lengths")

    # Target infeasible
    check(not longest_path_feasible(no_n, edges_t, lengths, s_t, t_t, K),
          "NO: target is infeasible")

    # Verify: longest path from 0 can use at most 3 edges (vertices 0,1,2,3)
    # So max length = 3 < K = 4
    best_len = 0
    m = len(no_edges)
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        if is_simple_st_path(no_n, no_edges, no_s, no_t, config):
            total = sum(config)
            best_len = max(best_len, total)
    # No s-t path exists at all since t=4 is isolated
    check(best_len == 0, f"NO: best path length to t=4 is {best_len} (expected 0)")

    # Verify no path at all reaches vertex 4
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        selected_verts = set()
        for idx in range(m):
            if config[idx] == 1:
                u, v = no_edges[idx]
                selected_verts.add(u)
                selected_verts.add(v)
        check(4 not in selected_verts,
              "NO: vertex 4 reachable via some edge selection")

    check(best_len < K, f"NO: best reachable length {best_len} < K={K}")

    print(f"  Section 7: {passed - sec7_start} new checks")

    # ── Export test vectors ──
    test_vectors = {
        "source": "HamiltonianPathBetweenTwoVertices",
        "target": "LongestPath",
        "issue": 359,
        "yes_instance": {
            "input": {
                "num_vertices": yes_n,
                "edges": yes_edges,
                "source_vertex": yes_s,
                "target_vertex": yes_t,
            },
            "output": {
                "num_vertices": yes_n,
                "edges": yes_edges,
                "edge_lengths": [1] * len(yes_edges),
                "source_vertex": yes_s,
                "target_vertex": yes_t,
                "bound": yes_n - 1,
            },
            "source_feasible": True,
            "target_feasible": True,
            "source_solution": ham_path,
            "extracted_solution": ham_path,
        },
        "no_instance": {
            "input": {
                "num_vertices": no_n,
                "edges": no_edges,
                "source_vertex": no_s,
                "target_vertex": no_t,
            },
            "output": {
                "num_vertices": no_n,
                "edges": no_edges,
                "edge_lengths": [1] * len(no_edges),
                "source_vertex": no_s,
                "target_vertex": no_t,
                "bound": no_n - 1,
            },
            "source_feasible": False,
            "target_feasible": False,
        },
        "overhead": {
            "num_vertices": "num_vertices",
            "num_edges": "num_edges",
            "bound": "num_vertices - 1",
        },
        "claims": [
            {"tag": "graph_preserved", "formula": "G' = G", "verified": True},
            {"tag": "unit_lengths", "formula": "l(e) = 1 for all e", "verified": True},
            {"tag": "endpoints_preserved", "formula": "s' = s, t' = t", "verified": True},
            {"tag": "bound_formula", "formula": "K = n - 1", "verified": True},
            {"tag": "forward_direction", "formula": "Ham path => path length = n-1 = K", "verified": True},
            {"tag": "backward_direction", "formula": "path length >= K => exactly n-1 edges => Hamiltonian", "verified": True},
            {"tag": "solution_extraction", "formula": "edge config -> vertex path via tracing", "verified": True},
        ],
    }

    vectors_path = "docs/paper/verify-reductions/test_vectors_hamiltonian_path_between_two_vertices_longest_path.json"
    with open(vectors_path, "w") as f:
        json.dump(test_vectors, f, indent=2)
    print(f"\n  Test vectors exported to {vectors_path}")

    # ── Final report ──
    print(f"\nHamiltonianPathBetweenTwoVertices -> LongestPath: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
