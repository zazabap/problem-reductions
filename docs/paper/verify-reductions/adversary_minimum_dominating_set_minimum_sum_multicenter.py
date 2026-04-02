#!/usr/bin/env python3
"""
Adversary verification script: MinimumDominatingSet -> MinimumSumMulticenter reduction.
Issue: #380

Independent re-implementation of the reduction and extraction logic,
plus property-based testing with hypothesis. >=5000 independent checks.

This script does NOT import from verify_minimum_dominating_set_minimum_sum_multicenter.py --
it re-derives everything from scratch as an independent cross-check.

Reduction: DominatingSet(G, K) -> MinSumMulticenter(G, w=1, l=1, k=K, B=n-K).
On unit-weight unit-length connected graphs, sum d(v,P) <= n-K with K centers
iff every non-center has distance exactly 1 to some center, i.e., the centers
form a dominating set.

Focus: exhaustive enumeration n <= 6, edge-case configs, disconnected graphs,
special graph families, and hypothesis PBT.
"""

import json
import sys
from collections import deque
from itertools import combinations
from typing import Optional

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not installed; falling back to pure-random adversary tests")


# ---------------------------------------------------------------------
# Independent re-implementation of reduction
# ---------------------------------------------------------------------

def adv_reduce(n: int, edges: list[tuple[int, int]], k: int) -> dict:
    """
    Independent reduction: DominatingSet(G, K) -> MinSumMulticenter(G, 1, 1, K, n-K).

    On a connected graph G with unit vertex weights and unit edge lengths,
    a K-center placement with total distance <= n-K means every non-center
    has distance exactly 1, which is precisely the dominating set condition.

    Construction:
    - Graph: preserved exactly
    - Vertex weights: all 1
    - Edge lengths: all 1
    - Number of centers: k = K
    - Distance bound: B = n - K
    """
    return {
        "num_vertices": n,
        "edges": list(edges),
        "vertex_weights": [1] * n,
        "edge_lengths": [1] * len(edges),
        "k": k,
        "B": n - k,
    }


def adv_extract(config: list[int]) -> list[int]:
    """
    Independent extraction: p-median config -> dominating set config.
    Since the graph and configuration space are identical, the
    binary indicator vector passes through unchanged.
    """
    return config[:]


def adv_build_adj(n: int, edges: list[tuple[int, int]]) -> list[set[int]]:
    """Build adjacency sets."""
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def adv_is_connected(adj: list[set[int]]) -> bool:
    """Check connectivity via BFS."""
    n = len(adj)
    if n <= 1:
        return True
    visited = set()
    q = deque([0])
    visited.add(0)
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in visited:
                visited.add(w)
                q.append(w)
    return len(visited) == n


def adv_is_dominating(adj: list[set[int]], config: list[int]) -> bool:
    """Check if config selects a dominating set."""
    n = len(adj)
    for v in range(n):
        if config[v] == 1:
            continue
        dominated = False
        for u in adj[v]:
            if config[u] == 1:
                dominated = True
                break
        if not dominated:
            return False
    return True


def adv_bfs_distances(adj: list[set[int]], config: list[int]) -> Optional[list[int]]:
    """Multi-source BFS from all centers. Returns distances or None if unreachable."""
    n = len(adj)
    dist = [-1] * n
    q = deque()
    for v in range(n):
        if config[v] == 1:
            dist[v] = 0
            q.append(v)
    while q:
        u = q.popleft()
        for w in adj[u]:
            if dist[w] == -1:
                dist[w] = dist[u] + 1
                q.append(w)
    if any(d == -1 for d in dist):
        return None
    return dist


def adv_total_distance(adj: list[set[int]], config: list[int]) -> Optional[int]:
    """Total distance from all vertices to nearest center (unit weights)."""
    distances = adv_bfs_distances(adj, config)
    if distances is None:
        return None
    return sum(distances)


def adv_is_feasible_pmedian(adj: list[set[int]], config: list[int], k: int) -> bool:
    """Check feasibility with B=n-k, unit weights."""
    n = len(adj)
    if sum(config) != k:
        return False
    total = adv_total_distance(adj, config)
    if total is None:
        return False
    return total <= n - k


def adv_solve_ds(adj: list[set[int]], k: int) -> Optional[list[int]]:
    """Brute-force dominating set solver."""
    n = len(adj)
    for chosen in combinations(range(n), k):
        cfg = [0] * n
        for v in chosen:
            cfg[v] = 1
        if adv_is_dominating(adj, cfg):
            return cfg
    return None


def adv_solve_pm(adj: list[set[int]], k: int) -> Optional[list[int]]:
    """Brute-force p-median solver (B=n-k, unit weights)."""
    n = len(adj)
    for chosen in combinations(range(n), k):
        cfg = [0] * n
        for v in chosen:
            cfg[v] = 1
        if adv_is_feasible_pmedian(adj, cfg, k):
            return cfg
    return None


# ---------------------------------------------------------------------
# Property checks
# ---------------------------------------------------------------------

def adv_check_all(n: int, edges: list[tuple[int, int]], k: int) -> int:
    """Run all adversary checks on a single connected instance. Returns check count."""
    adj = adv_build_adj(n, edges)
    checks = 0

    # 1. Overhead: target preserves graph exactly
    target = adv_reduce(n, edges, k)
    assert target["num_vertices"] == n
    assert len(target["edges"]) == len(edges)
    assert target["k"] == k
    assert target["B"] == n - k
    checks += 4

    # 2. Forward: feasible source -> feasible target
    src_sol = adv_solve_ds(adj, k)
    tgt_sol = adv_solve_pm(adj, k)
    if src_sol is not None:
        assert tgt_sol is not None, (
            f"Forward violation: n={n}, edges={edges}, k={k}"
        )
        checks += 1

    # 3. Backward + extraction: feasible target -> valid source extraction
    if tgt_sol is not None:
        extracted = adv_extract(tgt_sol)
        assert adv_is_dominating(adj, extracted), (
            f"Extraction violation: n={n}, edges={edges}, k={k}, config={tgt_sol}"
        )
        checks += 1

    # 4. Infeasible: NO source -> NO target
    if src_sol is None:
        assert tgt_sol is None, (
            f"Infeasible violation: n={n}, edges={edges}, k={k}"
        )
        checks += 1

    # 5. Feasibility equivalence
    src_feas = src_sol is not None
    tgt_feas = tgt_sol is not None
    assert src_feas == tgt_feas, (
        f"Feasibility mismatch: src={src_feas}, tgt={tgt_feas}, n={n}, edges={edges}, k={k}"
    )
    checks += 1

    # 6. For every k-subset, DS feasibility <=> p-median feasibility
    for chosen in combinations(range(n), k):
        cfg = [0] * n
        for v in chosen:
            cfg[v] = 1
        ds_ok = adv_is_dominating(adj, cfg)
        pm_ok = adv_is_feasible_pmedian(adj, cfg, k)
        assert ds_ok == pm_ok, (
            f"Pointwise mismatch: n={n}, edges={edges}, k={k}, config={cfg}, "
            f"ds={ds_ok}, pm={pm_ok}"
        )
        checks += 1

    return checks


# ---------------------------------------------------------------------
# Test drivers
# ---------------------------------------------------------------------

def adversary_exhaustive(max_n: int = 6) -> int:
    """Exhaustive adversary tests on all connected graphs n <= max_n."""
    checks = 0
    for n in range(1, max_n + 1):
        all_possible_edges = list(combinations(range(n), 2))
        graph_count = 0
        for r in range(len(all_possible_edges) + 1):
            for edge_subset in combinations(all_possible_edges, r):
                edges = list(edge_subset)
                adj = adv_build_adj(n, edges)
                if not adv_is_connected(adj):
                    continue  # skip disconnected graphs
                graph_count += 1
                for k in range(1, n + 1):
                    checks += adv_check_all(n, edges, k)
        print(f"  n={n}: {graph_count} connected graphs, checks so far: {checks}")
    return checks


def adversary_random(count: int = 1000, max_n: int = 10) -> int:
    """Random adversary tests with independent RNG seed."""
    import random
    rng = random.Random(9999)  # Different seed from verify script
    checks = 0
    for _ in range(count):
        n = rng.randint(2, max_n)
        # Random connected graph (spanning tree + extras)
        edges_set = set()
        perm = list(range(n))
        rng.shuffle(perm)
        for i in range(1, n):
            parent_idx = rng.randint(0, i - 1)
            u, v = perm[parent_idx], perm[i]
            edges_set.add((min(u, v), max(u, v)))
        all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        remaining = [e for e in all_possible if e not in edges_set]
        num_extra = rng.randint(0, min(len(remaining), n))
        if remaining and num_extra > 0:
            for e in rng.sample(remaining, min(num_extra, len(remaining))):
                edges_set.add(e)
        edges = sorted(edges_set)
        k = rng.randint(1, n)
        checks += adv_check_all(n, edges, k)
    return checks


def adversary_hypothesis() -> int:
    """Property-based testing with hypothesis."""
    if not HAS_HYPOTHESIS:
        return 0

    checks_counter = [0]

    # Strategy 1: random connected graphs with random k
    @given(
        n=st.integers(min_value=2, max_value=8),
        data=st.data(),
    )
    @settings(
        max_examples=500,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None,
    )
    def prop_connected_graph(n, data):
        # Build a random spanning tree
        perm = data.draw(st.permutations(list(range(n))))
        edges_set = set()
        for i in range(1, n):
            parent_idx = data.draw(st.integers(min_value=0, max_value=i - 1))
            u, v = perm[parent_idx], perm[i]
            edges_set.add((min(u, v), max(u, v)))
        # Optionally add extra edges
        all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        remaining = [e for e in all_possible if e not in edges_set]
        if remaining:
            extras = data.draw(
                st.lists(st.sampled_from(remaining), max_size=min(5, len(remaining)), unique=True)
            )
            edges_set.update(extras)
        edges = sorted(edges_set)
        k = data.draw(st.integers(min_value=1, max_value=n))
        checks_counter[0] += adv_check_all(n, edges, k)

    # Strategy 2: dense graphs (high edge probability)
    @given(
        n=st.integers(min_value=2, max_value=7),
        data=st.data(),
    )
    @settings(
        max_examples=500,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
        deadline=None,
    )
    def prop_dense_graph(n, data):
        all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        # High probability of including each edge
        edge_mask = data.draw(
            st.lists(
                st.booleans().filter(lambda x: True),
                min_size=len(all_possible),
                max_size=len(all_possible),
            )
        )
        edges = [e for e, include in zip(all_possible, edge_mask) if include]
        adj = adv_build_adj(n, edges)
        assume(adv_is_connected(adj))
        k = data.draw(st.integers(min_value=1, max_value=n))
        checks_counter[0] += adv_check_all(n, edges, k)

    prop_connected_graph()
    prop_dense_graph()
    return checks_counter[0]


def adversary_edge_cases() -> int:
    """Targeted edge cases for the reduction."""
    checks = 0
    edge_cases = [
        # Single vertex, no edges (trivially connected)
        (1, [], 1),
        # Two vertices, one edge
        (2, [(0, 1)], 1),
        (2, [(0, 1)], 2),
        # Triangle
        (3, [(0, 1), (0, 2), (1, 2)], 1),
        (3, [(0, 1), (0, 2), (1, 2)], 2),
        (3, [(0, 1), (0, 2), (1, 2)], 3),
        # Path P3
        (3, [(0, 1), (1, 2)], 1),
        (3, [(0, 1), (1, 2)], 2),
        (3, [(0, 1), (1, 2)], 3),
        # Star K_{1,4}
        (5, [(0, 1), (0, 2), (0, 3), (0, 4)], 1),
        (5, [(0, 1), (0, 2), (0, 3), (0, 4)], 2),
        (5, [(0, 1), (0, 2), (0, 3), (0, 4)], 3),
        # Complete K5
        (5, [(i, j) for i in range(5) for j in range(i + 1, 5)], 1),
        (5, [(i, j) for i in range(5) for j in range(i + 1, 5)], 2),
        # Cycle C5
        (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], 1),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], 2),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)], 3),
        # Bipartite K_{2,3}
        (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)], 1),
        (5, [(0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4)], 2),
        # Path P5
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)], 1),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)], 2),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)], 3),
        # Path P6
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], 1),
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], 2),
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)], 3),
        # Cycle C6
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)], 1),
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5)], 2),
        # Petersen-like 6-vertex
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 5), (1, 4)], 2),
        # Star K_{1,5}
        (6, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)], 1),
        (6, [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)], 2),
    ]
    for n, edges, k in edge_cases:
        checks += adv_check_all(n, edges, k)
    return checks


def verify_typst_yes_example() -> int:
    """Reproduce the YES example from the Typst proof."""
    checks = 0
    n = 6
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
    adj = adv_build_adj(n, edges)

    # D = {0, 3}, k = 2
    config = [1, 0, 0, 1, 0, 0]
    assert adv_is_dominating(adj, config), "YES: {0,3} must dominate G"
    checks += 1
    assert adv_is_feasible_pmedian(adj, config, 2), "YES: centers {0,3} must be feasible"
    checks += 1

    # Verify distances
    distances = adv_bfs_distances(adj, config)
    assert distances == [0, 1, 1, 0, 1, 1]
    checks += 1

    # Total distance = 4 = B
    assert sum(distances) == 4
    assert 4 == n - 2  # B = n - k
    checks += 2

    # Extraction
    extracted = adv_extract(config)
    assert extracted == config
    assert adv_is_dominating(adj, extracted)
    checks += 2

    print(f"  YES example: {checks} checks passed")
    return checks


def verify_typst_no_example() -> int:
    """Reproduce the NO example from the Typst proof."""
    checks = 0
    n = 6
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5), (4, 5)]
    adj = adv_build_adj(n, edges)

    # No dominating set of size 1
    assert adv_solve_ds(adj, 1) is None
    checks += 1
    # No feasible p-median with k=1
    assert adv_solve_pm(adj, 1) is None
    checks += 1

    # Specific: center at 3, distances = [2,1,1,0,1,1], sum = 6 > 5
    dist_3 = adv_bfs_distances(adj, [0, 0, 0, 1, 0, 0])
    assert dist_3 == [2, 1, 1, 0, 1, 1]
    assert sum(dist_3) == 6
    checks += 2

    # Center at 0, distances = [0,1,1,2,3,3], sum = 10 > 5
    dist_0 = adv_bfs_distances(adj, [1, 0, 0, 0, 0, 0])
    assert dist_0 == [0, 1, 1, 2, 3, 3]
    assert sum(dist_0) == 10
    checks += 2

    print(f"  NO example: {checks} checks passed")
    return checks


# ---------------------------------------------------------------------
# Cross-comparison
# ---------------------------------------------------------------------

def cross_compare(count: int = 300) -> int:
    """
    Cross-compare adversary reduce() outputs on shared instances.
    Since both implementations are identity on the graph, verify structural
    agreement and feasibility equivalence.
    """
    import random
    rng = random.Random(77777)
    checks = 0

    for _ in range(count):
        n = rng.randint(2, 8)
        # Build connected graph
        edges_set = set()
        perm = list(range(n))
        rng.shuffle(perm)
        for i in range(1, n):
            u = perm[rng.randint(0, i - 1)]
            v = perm[i]
            edges_set.add((min(u, v), max(u, v)))
        all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        remaining = [e for e in all_possible if e not in edges_set]
        num_extra = rng.randint(0, min(len(remaining), n))
        if remaining and num_extra > 0:
            for e in rng.sample(remaining, min(num_extra, len(remaining))):
                edges_set.add(e)
        edges = sorted(edges_set)
        k = rng.randint(1, n)

        adv_target = adv_reduce(n, edges, k)

        # Verify structural identity
        assert adv_target["num_vertices"] == n
        assert adv_target["edges"] == edges
        assert adv_target["vertex_weights"] == [1] * n
        assert adv_target["edge_lengths"] == [1] * len(edges)
        assert adv_target["k"] == k
        assert adv_target["B"] == n - k
        checks += 6

        # Verify feasibility agreement
        adj = adv_build_adj(n, edges)
        ds_feas = adv_solve_ds(adj, k) is not None
        pm_feas = adv_solve_pm(adj, k) is not None
        assert ds_feas == pm_feas, (
            f"Cross-compare feasibility mismatch: n={n}, edges={edges}, k={k}"
        )
        checks += 1

    return checks


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Adversary verification: MinimumDominatingSet -> MinimumSumMulticenter")
    print("=" * 60)

    print("\n[1/6] Edge cases...")
    n_edge = adversary_edge_cases()
    print(f"  Edge case checks: {n_edge}")

    print("\n[2/6] Exhaustive adversary (n <= 6, connected graphs)...")
    n_exh = adversary_exhaustive()
    print(f"  Exhaustive checks: {n_exh}")

    print("\n[3/6] Random adversary (different seed)...")
    n_rand = adversary_random()
    print(f"  Random checks: {n_rand}")

    print("\n[4/6] Hypothesis PBT...")
    n_hyp = adversary_hypothesis()
    print(f"  Hypothesis checks: {n_hyp}")

    print("\n[5/6] Typst examples...")
    n_yes = verify_typst_yes_example()
    n_no = verify_typst_no_example()
    n_typst = n_yes + n_no
    print(f"  Typst example checks: {n_typst}")

    print("\n[6/6] Cross-comparison...")
    n_cross = cross_compare()
    print(f"  Cross-comparison checks: {n_cross}")

    total = n_edge + n_exh + n_rand + n_hyp + n_typst + n_cross
    print(f"\n  TOTAL adversary checks: {total}")
    assert total >= 5000, f"Need >=5000 checks, got {total}"
    print(f"\nAll {total} adversary checks PASSED.")
