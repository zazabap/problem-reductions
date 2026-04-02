#!/usr/bin/env python3
"""
Adversary verification: HamiltonianPathBetweenTwoVertices -> LongestPath (#359).

Independent implementation based solely on the Typst proof specification.
Does NOT import from the constructor script.
"""

import itertools
import sys
from typing import List, Optional, Tuple

try:
    from hypothesis import given, settings, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

# ---------------------------------------------------------------------------
# Feasibility checkers (independent implementations)
# ---------------------------------------------------------------------------


def is_hamiltonian_st_path(n: int, edges: List[Tuple[int, int]], s: int, t: int,
                           path: List[int]) -> bool:
    """Check if path is a valid Hamiltonian s-t path."""
    if len(path) != n or len(set(path)) != n:
        return False
    if path[0] != s or path[-1] != t:
        return False
    if any(v < 0 or v >= n for v in path):
        return False
    edge_set = set()
    for u, v in edges:
        edge_set.add((u, v))
        edge_set.add((v, u))
    for i in range(n - 1):
        if (path[i], path[i + 1]) not in edge_set:
            return False
    return True


def is_feasible_source(n: int, edges: List[Tuple[int, int]], s: int, t: int) -> bool:
    """Brute-force: does a Hamiltonian s-t path exist?"""
    for perm in itertools.permutations(range(n)):
        if is_hamiltonian_st_path(n, edges, s, t, list(perm)):
            return True
    return False


def find_source_witness(n: int, edges: List[Tuple[int, int]], s: int, t: int) -> Optional[List[int]]:
    """Return a Hamiltonian s-t path or None."""
    for perm in itertools.permutations(range(n)):
        if is_hamiltonian_st_path(n, edges, s, t, list(perm)):
            return list(perm)
    return None


def is_simple_st_path_config(n: int, edges: List[Tuple[int, int]], s: int, t: int,
                             config: List[int]) -> bool:
    """Check if config (edge selection) encodes a valid simple s-t path."""
    m = len(edges)
    if len(config) != m:
        return False

    adj = [[] for _ in range(n)]
    deg = [0] * n
    sel = 0
    for idx in range(m):
        if config[idx] == 1:
            u, v = edges[idx]
            adj[u].append(v)
            adj[v].append(u)
            deg[u] += 1
            deg[v] += 1
            sel += 1

    if sel == 0:
        return False
    if deg[s] != 1 or deg[t] != 1:
        return False
    for v in range(n):
        if deg[v] == 0:
            continue
        if v != s and v != t and deg[v] != 2:
            return False

    # Connectivity check via BFS
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

    for v in range(n):
        if deg[v] > 0 and v not in visited:
            return False
    return t in visited


def is_feasible_target(n: int, edges: List[Tuple[int, int]], lengths: List[int],
                       s: int, t: int, K: int) -> bool:
    """Brute-force: does a simple s-t path of length >= K exist?"""
    m = len(edges)
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        if is_simple_st_path_config(n, edges, s, t, config):
            total = sum(lengths[idx] for idx in range(m) if config[idx] == 1)
            if total >= K:
                return True
    return False


def find_target_witness(n: int, edges: List[Tuple[int, int]], lengths: List[int],
                        s: int, t: int, K: int) -> Optional[List[int]]:
    """Return an edge config for a simple s-t path with length >= K, or None."""
    m = len(edges)
    best = None
    best_len = -1
    for bits in range(2**m):
        config = [(bits >> idx) & 1 for idx in range(m)]
        if is_simple_st_path_config(n, edges, s, t, config):
            total = sum(lengths[idx] for idx in range(m) if config[idx] == 1)
            if total >= K and total > best_len:
                best_len = total
                best = config
    return best


# ---------------------------------------------------------------------------
# Reduction (from Typst proof, independent implementation)
# ---------------------------------------------------------------------------


def reduce(n: int, edges: List[Tuple[int, int]], s: int, t: int):
    """
    Construction from the Typst proof:
    1. G' = G (same graph)
    2. l(e) = 1 for every edge
    3. s' = s, t' = t
    4. K = n - 1
    """
    lengths = [1] * len(edges)
    K = n - 1
    return edges, lengths, s, t, K


def extract_solution(n: int, edges: List[Tuple[int, int]], edge_config: List[int],
                     s: int) -> List[int]:
    """
    Extract vertex path from edge selection by tracing from s.
    From Typst: start at s, follow the unique selected edge to the next
    unvisited vertex, continuing until t is reached.
    """
    m = len(edges)
    adj = {}
    for idx in range(m):
        if edge_config[idx] == 1:
            u, v = edges[idx]
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)

    path = [s]
    visited = {s}
    cur = s
    while True:
        nbs = [v for v in adj.get(cur, []) if v not in visited]
        if not nbs:
            break
        nxt = nbs[0]
        path.append(nxt)
        visited.add(nxt)
        cur = nxt
    return path


# ---------------------------------------------------------------------------
# Check counter
# ---------------------------------------------------------------------------

passed = 0
failed = 0


def check(condition, msg=""):
    global passed, failed
    if condition:
        passed += 1
    else:
        failed += 1
        print(f"  FAIL: {msg}")


# ---------------------------------------------------------------------------
# Exhaustive verification
# ---------------------------------------------------------------------------


def all_simple_graphs(n: int):
    """Generate all undirected graphs on n labeled vertices."""
    possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for bits in range(2**len(possible)):
        yield [possible[idx] for idx in range(len(possible)) if (bits >> idx) & 1]


def test_exhaustive():
    """Exhaustive forward + backward for n <= 5."""
    global passed, failed
    print("=== Exhaustive verification (n <= 5) ===")

    for n in range(2, 6):
        count = 0
        for edges in all_simple_graphs(n):
            for s in range(n):
                for t in range(n):
                    if s == t:
                        continue

                    src_feas = is_feasible_source(n, edges, s, t)
                    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
                    tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)

                    check(src_feas == tgt_feas,
                          f"n={n}, m={len(edges)}, s={s}, t={t}: "
                          f"src={src_feas} tgt={tgt_feas}")

                    # Solution extraction for feasible instances
                    if src_feas:
                        witness = find_target_witness(n, edges_t, lengths, s_t, t_t, K)
                        check(witness is not None,
                              f"n={n}, s={s}, t={t}: feasible but no witness")
                        if witness is not None:
                            vpath = extract_solution(n, edges_t, witness, s_t)
                            check(is_hamiltonian_st_path(n, edges, s, t, vpath),
                                  f"n={n}, s={s}, t={t}: extracted path invalid")

                    count += 1
        print(f"  n={n}: {count} instances tested")


# ---------------------------------------------------------------------------
# Typst example reproduction
# ---------------------------------------------------------------------------


def test_yes_example():
    """Reproduce YES example from Typst proof."""
    global passed, failed
    print("\n=== YES example (Typst) ===")

    n = 5
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 4), (3, 4), (0, 3)]
    s, t = 0, 4

    check(n == 5, "YES: n = 5")
    check(len(edges) == 7, "YES: m = 7")

    # Hamiltonian path: 0 -> 3 -> 1 -> 2 -> 4
    ham = [0, 3, 1, 2, 4]
    check(is_hamiltonian_st_path(n, edges, s, t, ham),
          "YES: 0->3->1->2->4 is Hamiltonian")

    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
    check(K == 4, f"YES: K={K}, expected 4")
    check(all(l == 1 for l in lengths), "YES: unit lengths")
    check(s_t == 0 and t_t == 4, "YES: endpoints preserved")

    tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
    check(tgt_feas, "YES: target feasible")

    witness = find_target_witness(n, edges_t, lengths, s_t, t_t, K)
    check(witness is not None, "YES: target witness found")
    if witness:
        total = sum(lengths[i] for i in range(len(edges_t)) if witness[i] == 1)
        check(total == 4, f"YES: witness length = {total}")
        vpath = extract_solution(n, edges_t, witness, s_t)
        check(is_hamiltonian_st_path(n, edges, s, t, vpath),
              f"YES: extracted path {vpath} is Hamiltonian")


def test_no_example():
    """Reproduce NO example from Typst proof."""
    global passed, failed
    print("\n=== NO example (Typst) ===")

    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    s, t = 0, 4

    check(n == 5, "NO: n = 5")
    check(len(edges) == 4, "NO: m = 4")

    # Vertex 4 isolated
    verts_in_edges = set()
    for u, v in edges:
        verts_in_edges.add(u)
        verts_in_edges.add(v)
    check(4 not in verts_in_edges, "NO: vertex 4 isolated")

    src_feas = is_feasible_source(n, edges, s, t)
    check(not src_feas, "NO: source infeasible")

    edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
    check(K == 4, f"NO: K={K}, expected 4")

    tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
    check(not tgt_feas, "NO: target infeasible")


# ---------------------------------------------------------------------------
# Edge-case configs
# ---------------------------------------------------------------------------


def test_edge_cases():
    """Test edge-case configurations: complete graphs, empty graphs, etc."""
    global passed, failed
    print("\n=== Edge-case configs ===")

    # Complete graph K5: always has Hamiltonian path for any s, t
    n = 5
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            check(is_feasible_source(n, edges, s, t),
                  f"K5: Ham path {s}->{t} must exist")
            edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
            check(is_feasible_target(n, edges_t, lengths, s_t, t_t, K),
                  f"K5: target feasible for {s}->{t}")

    # Empty graph (no edges): never feasible for n >= 2
    for n in range(2, 6):
        for s in range(n):
            for t in range(n):
                if s == t:
                    continue
                check(not is_feasible_source(n, [], s, t),
                      f"Empty graph n={n}: infeasible {s}->{t}")
                edges_t, lengths, s_t, t_t, K = reduce(n, [], s, t)
                check(not is_feasible_target(n, edges_t, lengths, s_t, t_t, K),
                      f"Empty graph n={n}: target infeasible {s}->{t}")

    # Star graph K1,4: no Hamiltonian path for n > 3 (center has degree n-1 but
    # leaves have degree 1, so path can visit at most 3 vertices via center)
    n = 5
    edges = [(0, 1), (0, 2), (0, 3), (0, 4)]
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            src_feas = is_feasible_source(n, edges, s, t)
            check(not src_feas, f"Star K1,4: no Ham path {s}->{t}")
            edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
            tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
            check(src_feas == tgt_feas,
                  f"Star K1,4: equivalence for {s}->{t}")

    # Cycle graph C5: Hamiltonian path exists only between certain pairs
    # (adjacent vertices can be endpoints of the path traversing the long way)
    n = 5
    edges = [(min(i, (i + 1) % n), max(i, (i + 1) % n)) for i in range(n)]
    for s in range(n):
        for t in range(n):
            if s == t:
                continue
            src_feas = is_feasible_source(n, edges, s, t)
            edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
            tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
            check(src_feas == tgt_feas,
                  f"C5: equivalence for {s}->{t} (src={src_feas}, tgt={tgt_feas})")

    # All-one config test: selecting all edges is not a valid simple path
    n = 4
    edges = [(0, 1), (1, 2), (2, 3), (0, 3)]
    all_ones = [1, 1, 1, 1]
    check(not is_simple_st_path_config(n, edges, 0, 3, all_ones),
          "All-ones is not a valid simple path (cycle)")

    # All-zero config: never valid
    check(not is_simple_st_path_config(n, edges, 0, 3, [0, 0, 0, 0]),
          "All-zeros is not a valid simple path")


# ---------------------------------------------------------------------------
# Hypothesis PBT
# ---------------------------------------------------------------------------


def run_hypothesis_tests():
    """Run hypothesis PBT if available."""
    global passed, failed

    if not HAS_HYPOTHESIS:
        print("\n=== Hypothesis PBT: SKIPPED (hypothesis not installed) ===")
        # Fall back to additional random testing
        import random
        random.seed(42)
        print("\n=== Fallback random testing (3000 instances) ===")
        count = 0
        for _ in range(3000):
            n = random.randint(3, 6)
            possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
            edges = [e for e in possible if random.random() < 0.5]
            s = random.randint(0, n - 1)
            t = random.randint(0, n - 1)
            if s == t:
                t = (s + 1) % n

            src_feas = is_feasible_source(n, edges, s, t)
            edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
            tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
            check(src_feas == tgt_feas,
                  f"Random: n={n}, m={len(edges)}, s={s}, t={t}")

            if src_feas:
                witness = find_target_witness(n, edges_t, lengths, s_t, t_t, K)
                check(witness is not None, f"Random: feasible no witness")
                if witness:
                    vpath = extract_solution(n, edges_t, witness, s_t)
                    check(is_hamiltonian_st_path(n, edges, s, t, vpath),
                          f"Random: extraction failed")
            count += 1
        print(f"  {count} random instances tested")
        return

    @st.composite
    def graph_with_endpoints(draw):
        n = draw(st.integers(min_value=3, max_value=6))
        possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edge_mask = draw(st.lists(st.booleans(), min_size=len(possible), max_size=len(possible)))
        edges = [possible[i] for i in range(len(possible)) if edge_mask[i]]
        s = draw(st.integers(min_value=0, max_value=n - 1))
        t = draw(st.integers(min_value=0, max_value=n - 1).filter(lambda x: x != s))
        return n, edges, s, t

    @st.composite
    def path_graph_with_endpoints(draw):
        n = draw(st.integers(min_value=3, max_value=7))
        edges = [(i, i + 1) for i in range(n - 1)]
        possible_extra = [(i, j) for i in range(n) for j in range(i + 2, n)
                          if (i, j) not in set(edges)]
        if possible_extra:
            extra_mask = draw(st.lists(st.booleans(), min_size=len(possible_extra),
                                       max_size=len(possible_extra)))
            edges += [possible_extra[i] for i in range(len(possible_extra)) if extra_mask[i]]
        return n, edges, 0, n - 1

    @given(data=graph_with_endpoints())
    @settings(max_examples=2000, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_pbt_random_graphs(data):
        n, edges, s, t = data
        src_feas = is_feasible_source(n, edges, s, t)
        edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
        tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
        assert src_feas == tgt_feas, f"Mismatch: n={n}, m={len(edges)}, s={s}, t={t}"
        if src_feas:
            witness = find_target_witness(n, edges_t, lengths, s_t, t_t, K)
            assert witness is not None
            vpath = extract_solution(n, edges_t, witness, s_t)
            assert is_hamiltonian_st_path(n, edges, s, t, vpath)

    @given(data=path_graph_with_endpoints())
    @settings(max_examples=2000, deadline=None, suppress_health_check=[HealthCheck.too_slow])
    def test_pbt_path_graphs(data):
        n, edges, s, t = data
        src_feas = is_feasible_source(n, edges, s, t)
        assert src_feas, f"Path graph n={n} should have Ham path 0->{n-1}"
        edges_t, lengths, s_t, t_t, K = reduce(n, edges, s, t)
        tgt_feas = is_feasible_target(n, edges_t, lengths, s_t, t_t, K)
        assert tgt_feas
        witness = find_target_witness(n, edges_t, lengths, s_t, t_t, K)
        assert witness is not None
        total = sum(lengths[i] for i in range(len(edges_t)) if witness[i] == 1)
        assert total == n - 1

    print("\n=== Hypothesis PBT: random graphs ===")
    try:
        test_pbt_random_graphs()
        print("  PASSED")
        passed += 2000
    except Exception as e:
        print(f"  FAILED: {e}")
        failed += 1

    print("\n=== Hypothesis PBT: path graphs ===")
    try:
        test_pbt_path_graphs()
        print("  PASSED")
        passed += 2000
    except Exception as e:
        print(f"  FAILED: {e}")
        failed += 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    global passed, failed

    # Exhaustive verification (bulk of checks)
    test_exhaustive()

    # Typst examples
    test_yes_example()
    test_no_example()

    # Edge cases
    test_edge_cases()

    # Hypothesis PBT (or fallback)
    run_hypothesis_tests()

    # Final report
    print(f"\n[Adversary] HamiltonianPathBetweenTwoVertices -> LongestPath: "
          f"{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
