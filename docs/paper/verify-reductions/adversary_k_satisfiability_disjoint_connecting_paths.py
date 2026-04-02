#!/usr/bin/env python3
"""
Adversary script: KSatisfiability(K3) -> DisjointConnectingPaths

Independent verification of the flaw in issue #370's construction.
Reimplements the reduction from scratch and confirms the flaw using
hypothesis property-based testing (with manual fallback).

The flaw: the issue's linear clause chain makes the DCP always solvable.
"""

import itertools
import random
import sys
from collections import defaultdict

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not installed, using manual PBT")


# ============================================================
# Independent reimplementation (different code from verify script)
# ============================================================


def build_dcp_issue370(n: int, clauses: list[tuple[int, ...]]) -> tuple[
        int, list[tuple[int, int]], list[tuple[int, int]]]:
    """
    Independently reimplemented reduction from issue #370.
    Returns (num_vertices, edge_list, terminal_pairs).
    """
    m = len(clauses)
    nv = 2 * n * m + 8 * m
    E: list[tuple[int, int]] = []
    P: list[tuple[int, int]] = []

    # Variable chains: vertex (i, k) -> i * 2m + k
    for i in range(n):
        for k in range(2 * m - 1):
            u = i * 2 * m + k
            v = i * 2 * m + k + 1
            E.append((u, v))
        P.append((i * 2 * m, i * 2 * m + 2 * m - 1))

    # Clause gadgets
    var_count = n * 2 * m
    for j in range(m):
        base = var_count + j * 8
        sj = base
        # p_{j,r} at base+1, base+3, base+5; q_{j,r} at base+2, base+4, base+6
        pq = [(base + 1, base + 2), (base + 3, base + 4), (base + 5, base + 6)]
        tj = base + 7

        # Linear chain: s - p0 - q0 - p1 - q1 - p2 - q2 - t
        chain = [sj, pq[0][0], pq[0][1], pq[1][0], pq[1][1], pq[2][0], pq[2][1], tj]
        for idx in range(len(chain) - 1):
            E.append((chain[idx], chain[idx + 1]))
        P.append((sj, tj))

        # Interconnection
        for r in range(3):
            lit = clauses[j][r]
            vi = abs(lit) - 1
            p_r, q_r = pq[r]
            if lit > 0:
                E.append((vi * 2 * m + 2 * j, p_r))
                E.append((q_r, vi * 2 * m + 2 * j + 1))
            else:
                E.append((vi * 2 * m + 2 * j, q_r))
                E.append((p_r, vi * 2 * m + 2 * j + 1))

    return nv, E, P


def can_solve_dcp(nv: int, edges: list[tuple[int, int]],
                  pairs: list[tuple[int, int]]) -> bool:
    """Independent DCP solver (different implementation from verify script)."""
    # Build adjacency with dict of lists (not defaultdict of sets)
    adj: dict[int, list[int]] = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)

    def search(idx: int, blocked: set[int]) -> bool:
        if idx == len(pairs):
            return True
        src, dst = pairs[idx]
        if src in blocked or dst in blocked:
            return False
        # BFS/DFS to find path
        frontier = [(src, frozenset([src]))]
        while frontier:
            node, visited = frontier.pop()
            if node == dst:
                if search(idx + 1, blocked | visited):
                    return True
                continue
            for nb in adj.get(node, []):
                if nb not in visited and nb not in blocked:
                    frontier.append((nb, visited | frozenset([nb])))
        return False

    return search(0, set())


def brute_3sat(nvars: int, clauses: list[tuple[int, ...]]) -> bool:
    """Independent brute force 3-SAT (uses dict assignment)."""
    for bits in itertools.product([False, True], repeat=nvars):
        assign = {i + 1: bits[i] for i in range(nvars)}
        ok = True
        for c in clauses:
            if not any((assign[abs(l)] if l > 0 else not assign[abs(l)]) for l in c):
                ok = False
                break
        if ok:
            return True
    return False


def verify_flaw(nvars: int, clauses: list[tuple[int, ...]]) -> None:
    """
    Verify the flaw: DCP is always solvable under issue #370's construction.
    """
    assert nvars >= 3
    for c in clauses:
        assert len(c) == 3
        assert len(set(abs(l) for l in c)) == 3
        for l in c:
            assert 1 <= abs(l) <= nvars

    nv, edges, pairs = build_dcp_issue370(nvars, clauses)

    # Size checks
    m = len(clauses)
    assert nv == 2 * nvars * m + 8 * m
    assert len(edges) == nvars * (2 * m - 1) + 13 * m
    assert len(pairs) == nvars + m

    # The key assertion: DCP is ALWAYS solvable
    assert can_solve_dcp(nv, edges, pairs), \
        f"DCP not solvable (unexpected!): n={nvars}, clauses={clauses}"


# ============================================================
# Hypothesis-based tests
# ============================================================

if HAS_HYPOTHESIS:
    HC_SUPPRESS = [HealthCheck.too_slow, HealthCheck.filter_too_much]

    @given(
        nvars=st.integers(min_value=3, max_value=6),
        clause_data=st.lists(
            st.tuples(
                st.tuples(
                    st.integers(min_value=1, max_value=6),
                    st.integers(min_value=1, max_value=6),
                    st.integers(min_value=1, max_value=6),
                ),
                st.tuples(
                    st.sampled_from([-1, 1]),
                    st.sampled_from([-1, 1]),
                    st.sampled_from([-1, 1]),
                ),
            ),
            min_size=1, max_size=3,
        ),
    )
    @settings(max_examples=3000, deadline=None, suppress_health_check=HC_SUPPRESS)
    def test_flaw_property(nvars, clause_data):
        global counter
        clauses = []
        for (v1, v2, v3), (s1, s2, s3) in clause_data:
            assume(v1 <= nvars and v2 <= nvars and v3 <= nvars)
            assume(len({v1, v2, v3}) == 3)
            clauses.append((s1 * v1, s2 * v2, s3 * v3))
        if not clauses:
            return
        target_nv = 2 * nvars * len(clauses) + 8 * len(clauses)
        assume(target_nv <= 60)
        verify_flaw(nvars, clauses)
        counter += 1

    @given(
        nvars=st.integers(min_value=3, max_value=6),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=2500, deadline=None, suppress_health_check=HC_SUPPRESS)
    def test_flaw_seeded(nvars, seed):
        global counter
        rng = random.Random(seed)
        m = rng.randint(1, 3)
        clauses = []
        for _ in range(m):
            vs = rng.sample(range(1, nvars + 1), 3)
            lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
            clauses.append(lits)
        target_nv = 2 * nvars * m + 8 * m
        assume(target_nv <= 60)
        verify_flaw(nvars, clauses)
        counter += 1

else:
    def test_flaw_property():
        global counter
        rng = random.Random(99999)
        for _ in range(3000):
            nvars = rng.randint(3, 6)
            m = rng.randint(1, 3)
            clauses = []
            for _ in range(m):
                vs = rng.sample(range(1, nvars + 1), 3)
                lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
                clauses.append(lits)
            target_nv = 2 * nvars * m + 8 * m
            if target_nv > 60:
                continue
            verify_flaw(nvars, clauses)
            counter += 1

    def test_flaw_seeded():
        global counter
        for seed in range(2500):
            rng = random.Random(seed)
            nvars = rng.randint(3, 6)
            m = rng.randint(1, 3)
            clauses = []
            for _ in range(m):
                vs = rng.sample(range(1, nvars + 1), 3)
                lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
                clauses.append(lits)
            target_nv = 2 * nvars * m + 8 * m
            if target_nv > 60:
                continue
            verify_flaw(nvars, clauses)
            counter += 1


# ============================================================
# Adversarial boundary cases
# ============================================================


def test_boundary_cases():
    """Adversarial boundary cases confirming the flaw."""
    global counter

    # All positive
    verify_flaw(3, [(1, 2, 3)])
    counter += 1

    # All negative
    verify_flaw(3, [(-1, -2, -3)])
    counter += 1

    # Mixed
    verify_flaw(3, [(1, -2, 3)])
    counter += 1

    # Multiple clauses with shared variables
    verify_flaw(4, [(1, 2, 3), (-1, -2, 4)])
    counter += 1

    # Same clause repeated
    verify_flaw(3, [(1, 2, 3), (1, 2, 3)])
    counter += 1

    # Contradictory pair
    verify_flaw(4, [(1, 2, 3), (-1, -2, -3)])
    counter += 1

    # All sign combos for single clause
    for s1, s2, s3 in itertools.product([-1, 1], repeat=3):
        verify_flaw(3, [(s1, s2 * 2, s3 * 3)])
        counter += 1

    # All single clauses on 4 vars
    for combo in itertools.combinations(range(1, 5), 3):
        for s1, s2, s3 in itertools.product([-1, 1], repeat=3):
            c = tuple(s * v for s, v in zip((s1, s2, s3), combo))
            verify_flaw(4, [c])
            counter += 1

    # Multi-clause instances
    for _ in range(200):
        rng = random.Random(counter)
        n = rng.randint(3, 5)
        m = rng.randint(2, 3)
        clauses = []
        for _ in range(m):
            vs = rng.sample(range(1, n + 1), 3)
            lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
            clauses.append(lits)
        verify_flaw(n, clauses)
        counter += 1

    print(f"  boundary cases: {counter} total so far")


# ============================================================
# Main
# ============================================================

counter = 0

if __name__ == "__main__":
    print("=" * 60)
    print("Adversary: KSatisfiability(K3) -> DisjointConnectingPaths")
    print("Confirming REFUTED verdict for issue #370")
    print("=" * 60)

    print("\n--- Boundary cases ---")
    test_boundary_cases()

    print("\n--- Property-based test 1 ---")
    test_flaw_property()
    print(f"  after PBT1: {counter} total")

    print("\n--- Property-based test 2 ---")
    test_flaw_seeded()
    print(f"  after PBT2: {counter} total")

    print(f"\n{'=' * 60}")
    print(f"ADVERSARY TOTAL CHECKS: {counter}")
    assert counter >= 5000, f"Only {counter} checks, need >= 5000"
    print("ADVERSARY CONFIRMED: REFUTED")
    print("Issue #370's DCP construction is always solvable.")
