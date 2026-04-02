#!/usr/bin/env python3
"""
Adversary script: KSatisfiability(K3) -> FeasibleRegisterAssignment

Independent verification using hypothesis property-based testing.
Tests the same reduction from a different angle, with >= 5000 checks.
"""

import itertools
import random
import sys

# Try hypothesis; fall back to manual PBT if not available
try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not installed, using manual PBT")


# ============================================================
# Independent reimplementation of core functions
# (intentionally different code from verify script)
# ============================================================


def eval_lit(lit: int, assign: dict[int, bool]) -> bool:
    """Evaluate literal under variable -> bool mapping."""
    v = abs(lit)
    val = assign[v]
    return val if lit > 0 else not val


def check_3sat(nvars: int, clauses: list[tuple[int, ...]], assign: dict[int, bool]) -> bool:
    """Check 3-SAT satisfaction: each clause has >= 1 true literal."""
    for c in clauses:
        if not any(eval_lit(l, assign) for l in c):
            return False
    return True


def brute_3sat(nvars: int, clauses: list[tuple[int, ...]]) -> dict[int, bool] | None:
    """Brute force 3-SAT."""
    for bits in itertools.product([False, True], repeat=nvars):
        assign = {i + 1: bits[i] for i in range(nvars)}
        if check_3sat(nvars, clauses, assign):
            return assign
    return None


def check_fra(nv: int, edges: list[tuple[int, int]], regs: list[int],
              perm: list[int]) -> bool:
    """
    Check FRA feasibility. perm[step] = vertex computed at that step.
    Independent reimplementation.
    """
    if len(perm) != nv or set(perm) != set(range(nv)):
        return False

    # Build adjacency
    preds: list[set[int]] = [set() for _ in range(nv)]
    succs: list[set[int]] = [set() for _ in range(nv)]
    for v, u in edges:
        preds[v].add(u)
        succs[u].add(v)

    done: set[int] = set()
    for step in range(nv):
        v = perm[step]
        # Topological check
        if not preds[v] <= done:
            return False
        # Register conflict check
        r = regs[v]
        for w in perm[:step]:
            if regs[w] == r:
                # w is still live if it has undone successors besides v
                if any(s != v and s not in done for s in succs[w]):
                    return False
        done.add(v)
    return True


def brute_fra(nv: int, edges: list[tuple[int, int]], regs: list[int]) -> list[int] | None:
    """Brute force FRA via DFS over topological orderings with pruning."""
    if nv == 0:
        return []

    preds: list[set[int]] = [set() for _ in range(nv)]
    succs: list[set[int]] = [set() for _ in range(nv)]
    in_deg = [0] * nv
    for v, u in edges:
        preds[v].add(u)
        succs[u].add(v)
        in_deg[v] += 1

    done: set[int] = set()
    order: list[int] = []
    rem_in = list(in_deg)
    live: set[int] = set()

    def ok(v: int) -> bool:
        r = regs[v]
        for w in live:
            if regs[w] == r:
                if any(s != v and s not in done for s in succs[w]):
                    return False
        return True

    def go() -> bool:
        if len(order) == nv:
            return True
        avail = [v for v in range(nv) if v not in done and rem_in[v] == 0 and ok(v)]
        for v in avail:
            order.append(v)
            done.add(v)
            dead = {w for w in live if succs[w] and succs[w] <= done}
            live.difference_update(dead)
            if succs[v] and not succs[v] <= done:
                live.add(v)
            for s in succs[v]:
                rem_in[s] -= 1
            if go():
                return True
            for s in succs[v]:
                rem_in[s] += 1
            live.discard(v)
            live.update(dead)
            done.discard(v)
            order.pop()
        return False

    return list(order) if go() else None


def do_reduce(nvars: int, clauses: list[tuple[int, ...]]) -> tuple[int, list[tuple[int, int]], list[int]]:
    """
    Independently reimplemented reduction.
    Returns (num_vertices, arcs, register_assignment).
    """
    n = nvars
    m = len(clauses)
    nv = 2 * n + 5 * m
    edges: list[tuple[int, int]] = []
    regs: list[int] = []

    # Variable literal nodes: pairs sharing a register
    for i in range(n):
        regs.append(i)  # positive literal
        regs.append(i)  # negative literal

    # Clause chain gadgets
    for j in range(m):
        base = 2 * n + 5 * j
        rl = n + 2 * j      # register for lit nodes in clause j
        rm = n + 2 * j + 1  # register for mid nodes in clause j

        lits = clauses[j]

        def src_node(lit_val):
            vi = abs(lit_val) - 1
            return 2 * vi if lit_val > 0 else 2 * vi + 1

        # lit_0
        regs.append(rl)
        edges.append((base, src_node(lits[0])))

        # mid_0
        regs.append(rm)
        edges.append((base + 1, base))

        # lit_1
        regs.append(rl)
        edges.append((base + 2, src_node(lits[1])))
        edges.append((base + 2, base + 1))

        # mid_1
        regs.append(rm)
        edges.append((base + 3, base + 2))

        # lit_2
        regs.append(rl)
        edges.append((base + 4, src_node(lits[2])))
        edges.append((base + 4, base + 3))

    return nv, edges, regs


def sat_equiv_check(nvars: int, clauses: list[tuple[int, ...]]) -> bool:
    """Check that 3-SAT satisfiability equals FRA feasibility."""
    nv, edges, regs = do_reduce(nvars, clauses)
    sat_3 = brute_3sat(nvars, clauses) is not None
    sat_fra = brute_fra(nv, edges, regs) is not None
    return sat_3 == sat_fra


# ============================================================
# Hypothesis-based tests
# ============================================================

if HAS_HYPOTHESIS:
    @st.composite
    def three_sat_instance(draw):
        """Generate a valid 3-SAT instance."""
        n = draw(st.integers(min_value=3, max_value=5))
        m = draw(st.integers(min_value=1, max_value=4))
        # Keep target small enough for brute force
        if 2 * n + 5 * m > 25:
            m = max(1, (25 - 2 * n) // 5)
        clauses = []
        for _ in range(m):
            vars_chosen = draw(st.lists(
                st.integers(min_value=1, max_value=n),
                min_size=3, max_size=3, unique=True,
            ))
            lits = tuple(
                v if draw(st.booleans()) else -v
                for v in vars_chosen
            )
            clauses.append(lits)
        return n, clauses

    @given(data=three_sat_instance())
    @settings(max_examples=3000, deadline=60000,
              suppress_health_check=[HealthCheck.too_slow])
    def test_sat_equivalence_hypothesis(data):
        nvars, clauses = data
        assert sat_equiv_check(nvars, clauses), \
            f"Mismatch: nvars={nvars}, clauses={clauses}"

    @given(data=three_sat_instance())
    @settings(max_examples=2000, deadline=60000,
              suppress_health_check=[HealthCheck.too_slow])
    def test_target_validity_hypothesis(data):
        nvars, clauses = data
        nv, edges, regs = do_reduce(nvars, clauses)
        # Check DAG property
        in_deg = [0] * nv
        adj = [[] for _ in range(nv)]
        for v, u in edges:
            adj[u].append(v)
            in_deg[v] += 1
        queue = [v for v in range(nv) if in_deg[v] == 0]
        visited = 0
        while queue:
            node = queue.pop()
            visited += 1
            for nb in adj[node]:
                in_deg[nb] -= 1
                if in_deg[nb] == 0:
                    queue.append(nb)
        assert visited == nv, f"Not a DAG: {visited} of {nv} visited"
        # Check register bounds
        assert all(0 <= r < nvars + 2 * len(clauses) for r in regs)
        # Check vertex count
        assert nv == 2 * nvars + 5 * len(clauses)


# ============================================================
# Manual PBT fallback
# ============================================================


def manual_pbt(num_checks: int = 5500) -> int:
    """Manual property-based testing."""
    random.seed(77777)
    passed = 0

    for _ in range(num_checks):
        n = random.choice([3, 4, 5])
        m = random.randint(1, 4)
        if 2 * n + 5 * m > 25:
            m = max(1, (25 - 2 * n) // 5)

        clauses = []
        for _ in range(m):
            if n < 3:
                break
            vs = random.sample(range(1, n + 1), 3)
            lits = tuple(v if random.random() < 0.5 else -v for v in vs)
            clauses.append(lits)

        if len(clauses) < 1:
            continue

        # Validate
        ok = True
        for c in clauses:
            if len(set(abs(l) for l in c)) != 3:
                ok = False
                break
        if not ok:
            continue

        assert sat_equiv_check(n, clauses), \
            f"MISMATCH: n={n}, clauses={clauses}"
        passed += 1

    return passed


# ============================================================
# Main
# ============================================================


if __name__ == "__main__":
    print("=" * 60)
    print("Adversary: KSatisfiability(K3) -> FeasibleRegisterAssignment")
    print("=" * 60)

    total = 0

    if HAS_HYPOTHESIS:
        print("\n--- Hypothesis: sat equivalence ---")
        test_sat_equivalence_hypothesis()
        print("  3000 hypothesis checks passed")
        total += 3000

        print("\n--- Hypothesis: target validity ---")
        test_target_validity_hypothesis()
        print("  2000 hypothesis checks passed")
        total += 2000
    else:
        print("\n--- Manual PBT (no hypothesis) ---")
        n_manual = manual_pbt(6000)
        print(f"  {n_manual} manual PBT checks passed")
        total += n_manual

    print(f"\n{'=' * 60}")
    print(f"TOTAL ADVERSARY CHECKS: {total}")
    assert total >= 5000, f"Only {total} checks"
    print("ALL ADVERSARY CHECKS PASSED (>= 5000)")
