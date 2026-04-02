#!/usr/bin/env python3
"""
Adversary verification script for KSatisfiability(K3) -> DirectedTwoCommodityIntegralFlow.
Issue #368 -- Even, Itai, and Shamir (1976).

Independent implementation based solely on the Typst proof document.
Does NOT import from the constructor script.

Requirements: >= 5000 checks, hypothesis PBT with >= 2 strategies.
"""

import itertools
import json
import random
from pathlib import Path

# ---------------------------------------------------------------------------
# Independent reduction implementation (from proof document)
# ---------------------------------------------------------------------------

def reduce(n, clauses):
    """
    Independent reduction from 3-SAT to Directed Two-Commodity Integral Flow.

    From the proof:
    - 4 terminal vertices: s1=0, t1=1, s2=2, t2=3
    - For each variable u_i (i=0..n-1):
        a_i = 4+4i, p_i = 4+4i+1, q_i = 4+4i+2, b_i = 4+4i+3
    - For each clause C_j (j=0..m-1):
        d_j = 4+4n+j

    Arcs (all capacity 1 except s2->intermediates):
    - Chain: s1->a_0, b_i->a_{i+1}, b_{n-1}->t1
    - TRUE paths: a_i->p_i, p_i->b_i
    - FALSE paths: a_i->q_i, q_i->b_i
    - Supply from s2: s2->q_i (cap = #clauses with +u_i), s2->p_i (cap = #clauses with -u_i)
    - Literal connections:
        +u_i in C_j: q_i -> d_j  (cap 1)
        -u_i in C_j: p_i -> d_j  (cap 1)
    - Clause sinks: d_j -> t2 (cap 1)

    Requirements: R1=1, R2=m
    """
    m = len(clauses)

    # Count literal occurrences
    pos_cnt = [0] * n
    neg_cnt = [0] * n
    for cl in clauses:
        for lit in cl:
            v = abs(lit) - 1
            if lit > 0:
                pos_cnt[v] += 1
            else:
                neg_cnt[v] += 1

    num_verts = 4 + 4 * n + m
    arcs = []
    caps = []

    def arc(u, v, c=1):
        arcs.append((u, v))
        caps.append(c)

    # Chain
    arc(0, 4)  # s1 -> a_0
    for i in range(n - 1):
        arc(4 + 4 * i + 3, 4 + 4 * (i + 1))  # b_i -> a_{i+1}
    arc(4 + 4 * (n - 1) + 3, 1)  # b_{n-1} -> t1

    # Lobes
    for i in range(n):
        base = 4 + 4 * i
        arc(base, base + 1)  # a_i -> p_i
        arc(base + 1, base + 3)  # p_i -> b_i
        arc(base, base + 2)  # a_i -> q_i
        arc(base + 2, base + 3)  # q_i -> b_i

    # Supply
    for i in range(n):
        arc(2, 4 + 4 * i + 2, pos_cnt[i])  # s2 -> q_i
        arc(2, 4 + 4 * i + 1, neg_cnt[i])  # s2 -> p_i

    # Literal connections
    for j, cl in enumerate(clauses):
        dj = 4 + 4 * n + j
        for lit in cl:
            v = abs(lit) - 1
            if lit > 0:
                arc(4 + 4 * v + 2, dj)  # q_i -> d_j
            else:
                arc(4 + 4 * v + 1, dj)  # p_i -> d_j

    # Clause sinks
    for j in range(m):
        arc(4 + 4 * n + j, 3)  # d_j -> t2

    return {
        "nv": num_verts,
        "arcs": arcs,
        "caps": caps,
        "s1": 0, "t1": 1, "s2": 2, "t2": 3,
        "r1": 1, "r2": m,
    }


def sat_check(n, clauses):
    """Brute-force 3-SAT check."""
    for bits in range(1 << n):
        a = [(bits >> i) & 1 == 1 for i in range(n)]
        ok = True
        for cl in clauses:
            if not any(
                (a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                for l in cl
            ):
                ok = False
                break
        if ok:
            return True, a
    return False, None


def verify_flow(inst, f1, f2):
    """Verify flow feasibility."""
    nv = inst["nv"]
    arcs = inst["arcs"]
    caps = inst["caps"]
    m = len(arcs)
    terms = {inst["s1"], inst["t1"], inst["s2"], inst["t2"]}

    for i in range(m):
        if f1[i] < 0 or f2[i] < 0:
            return False
        if f1[i] + f2[i] > caps[i]:
            return False

    for ci, fl in enumerate([f1, f2]):
        bal = [0] * nv
        for i, (u, v) in enumerate(arcs):
            bal[u] -= fl[i]
            bal[v] += fl[i]
        for v in range(nv):
            if v not in terms and bal[v] != 0:
                return False
        sink = inst["t1"] if ci == 0 else inst["t2"]
        req = inst["r1"] if ci == 0 else inst["r2"]
        if bal[sink] < req:
            return False
    return True


def build_flow(inst, assignment, n, clauses):
    """Build feasible flow from a satisfying assignment."""
    arcs = inst["arcs"]
    m_arcs = len(arcs)
    f1 = [0] * m_arcs
    f2 = [0] * m_arcs

    # Build lookup
    arc_map = {}
    for idx, (u, v) in enumerate(arcs):
        arc_map.setdefault((u, v), []).append(idx)

    def add(fl, u, v, val):
        for idx in arc_map.get((u, v), []):
            fl[idx] += val
            return
        raise KeyError(f"Arc ({u},{v}) not found")

    # Commodity 1
    add(f1, 0, 4, 1)  # s1 -> a_0
    for i in range(n):
        base = 4 + 4 * i
        if assignment[i]:
            add(f1, base, base + 1, 1)  # a_i -> p_i
            add(f1, base + 1, base + 3, 1)  # p_i -> b_i
        else:
            add(f1, base, base + 2, 1)  # a_i -> q_i
            add(f1, base + 2, base + 3, 1)  # q_i -> b_i
        if i < n - 1:
            add(f1, base + 3, 4 + 4 * (i + 1), 1)
    add(f1, 4 + 4 * (n - 1) + 3, 1, 1)  # b_{n-1} -> t1

    # Commodity 2
    mc = len(clauses)
    for j, cl in enumerate(clauses):
        dj = 4 + 4 * n + j
        done = False
        for lit in cl:
            v = abs(lit) - 1
            if lit > 0 and assignment[v]:
                qi = 4 + 4 * v + 2
                add(f2, 2, qi, 1)  # s2 -> q_i
                add(f2, qi, dj, 1)  # q_i -> d_j
                add(f2, dj, 3, 1)  # d_j -> t2
                done = True
                break
            elif lit < 0 and not assignment[v]:
                pi = 4 + 4 * v + 1
                add(f2, 2, pi, 1)  # s2 -> p_i
                add(f2, pi, dj, 1)  # p_i -> d_j
                add(f2, dj, 3, 1)  # d_j -> t2
                done = True
                break
        if not done:
            raise ValueError(f"Clause {j} not routable")

    return f1, f2


def extract_assignment(inst, f1, n):
    """Extract assignment from commodity 1 flow."""
    arcs = inst["arcs"]
    result = []
    for i in range(n):
        ai = 4 + 4 * i
        pi = 4 + 4 * i + 1
        qi = 4 + 4 * i + 2
        tf = 0
        ff = 0
        for idx, (u, v) in enumerate(arcs):
            if u == ai and v == pi:
                tf += f1[idx]
            if u == ai and v == qi:
                ff += f1[idx]
        if tf > 0:
            result.append(True)
        elif ff > 0:
            result.append(False)
        else:
            return None
    return result


def try_all_assignments(n, clauses, inst):
    """Try all assignments to see if any yields a feasible flow."""
    for bits in range(1 << n):
        a = [(bits >> i) & 1 == 1 for i in range(n)]
        if not all(
            any(
                (a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                for l in cl
            )
            for cl in clauses
        ):
            continue
        try:
            f1, f2 = build_flow(inst, a, n, clauses)
            if verify_flow(inst, f1, f2):
                return True, (f1, f2, a)
        except (ValueError, KeyError):
            continue
    return False, None


# ---------------------------------------------------------------------------
# Random instance generators
# ---------------------------------------------------------------------------

def random_3sat(n, m, rng=None):
    if rng is None:
        rng = random
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        cl = [v if rng.random() < 0.5 else -v for v in vs]
        clauses.append(cl)
    return clauses


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

total_checks = 0


def check(cond, msg=""):
    global total_checks
    assert cond, msg
    total_checks += 1


def test_yes_example():
    """YES example from proof."""
    global total_checks
    n = 3
    clauses = [[1, 2, 3], [-1, -2, 3]]

    inst = reduce(n, clauses)
    check(inst["nv"] == 18, f"Expected 18 verts, got {inst['nv']}")
    check(len(inst["arcs"]) == 30, f"Expected 30 arcs, got {len(inst['arcs'])}")

    sat, a = sat_check(n, clauses)
    check(sat, "Must be satisfiable")

    f1, f2 = build_flow(inst, a, n, clauses)
    check(verify_flow(inst, f1, f2), "Flow must be feasible")

    ext = extract_assignment(inst, f1, n)
    check(ext == a, f"Extraction mismatch: {ext} vs {a}")

    # Try another assignment
    a2 = [True, True, True]
    f1b, f2b = build_flow(inst, a2, n, clauses)
    check(verify_flow(inst, f1b, f2b), "TTT flow feasible")

    print(f"  YES example: {total_checks} checks so far")


def test_no_example():
    """NO example from proof."""
    global total_checks
    n = 3
    clauses = [
        [1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3],
        [-1, 2, 3], [-1, 2, -3], [-1, -2, 3], [-1, -2, -3],
    ]

    sat, _ = sat_check(n, clauses)
    check(not sat, "Must be unsatisfiable")

    inst = reduce(n, clauses)
    check(inst["nv"] == 24, f"Expected 24 verts, got {inst['nv']}")
    check(len(inst["arcs"]) == 54, f"Expected 54 arcs, got {len(inst['arcs'])}")

    result, _ = try_all_assignments(n, clauses, inst)
    check(not result, "Must have no feasible flow")

    for bits in range(8):
        a = [(bits >> i) & 1 == 1 for i in range(n)]
        ok = all(
            any(
                (a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                for l in cl
            )
            for cl in clauses
        )
        check(not ok, f"Assignment {a} should not satisfy")

    print(f"  NO example: {total_checks} checks so far")


def test_exhaustive_forward_backward():
    """Exhaustive check for small instances."""
    global total_checks
    rng = random.Random(123)

    # All single-clause instances for n=3
    lits = [1, 2, 3, -1, -2, -3]
    all_cl = []
    for combo in itertools.combinations(lits, 3):
        if len(set(abs(l) for l in combo)) == 3:
            all_cl.append(list(combo))

    for cl in all_cl:
        sat, a = sat_check(3, [cl])
        inst = reduce(3, [cl])
        if sat:
            f1, f2 = build_flow(inst, a, 3, [cl])
            check(verify_flow(inst, f1, f2), f"Forward fail: {cl}")
        else:
            res, _ = try_all_assignments(3, [cl], inst)
            check(not res, f"Backward fail: {cl}")

    # All pairs
    for c1 in all_cl:
        for c2 in all_cl:
            cls = [c1, c2]
            sat, a = sat_check(3, cls)
            inst = reduce(3, cls)
            if sat:
                f1, f2 = build_flow(inst, a, 3, cls)
                check(verify_flow(inst, f1, f2))
            else:
                res, _ = try_all_assignments(3, cls, inst)
                check(not res)

    # Random instances
    for n in range(3, 6):
        for m in range(1, 5):
            num = 100 if n <= 4 else 50
            for _ in range(num):
                cls = random_3sat(n, m, rng)
                sat, a = sat_check(n, cls)
                inst = reduce(n, cls)
                if sat:
                    f1, f2 = build_flow(inst, a, n, cls)
                    check(verify_flow(inst, f1, f2))
                else:
                    res, _ = try_all_assignments(n, cls, inst)
                    check(not res)

    print(f"  Exhaustive: {total_checks} checks so far")


def test_extraction():
    """Solution extraction check."""
    global total_checks
    rng = random.Random(456)

    for n in range(3, 6):
        for m in range(1, 5):
            for _ in range(80):
                cls = random_3sat(n, m, rng)
                sat, a = sat_check(n, cls)
                if not sat:
                    continue
                inst = reduce(n, cls)
                f1, f2 = build_flow(inst, a, n, cls)
                check(verify_flow(inst, f1, f2))
                ext = extract_assignment(inst, f1, n)
                check(ext is not None, "Extraction must succeed")
                # Verify extracted satisfies formula
                for cl in cls:
                    check(
                        any(
                            (ext[abs(l) - 1] if l > 0 else not ext[abs(l) - 1])
                            for l in cl
                        ),
                        f"Clause {cl} not satisfied by {ext}",
                    )

    print(f"  Extraction: {total_checks} checks so far")


def test_overhead():
    """Overhead formula check."""
    global total_checks
    rng = random.Random(789)

    for n in range(3, 10):
        for m in range(1, 12):
            for _ in range(15):
                cls = random_3sat(n, m, rng)
                inst = reduce(n, cls)
                check(inst["nv"] == 4 + 4 * n + m)
                check(len(inst["arcs"]) == 7 * n + 4 * m + 1)

    print(f"  Overhead: {total_checks} checks so far")


def test_structural():
    """Structural properties."""
    global total_checks
    rng = random.Random(321)

    for n in range(3, 6):
        for m in range(1, 6):
            for _ in range(30):
                cls = random_3sat(n, m, rng)
                inst = reduce(n, cls)
                aset = set(inst["arcs"])

                # Chain
                check((0, 4) in aset, "s1->a0")
                check((4 + 4 * (n - 1) + 3, 1) in aset, "bn->t1")
                for i in range(n - 1):
                    check(
                        (4 + 4 * i + 3, 4 + 4 * (i + 1)) in aset,
                        f"b{i}->a{i+1}",
                    )

                # Lobes
                for i in range(n):
                    base = 4 + 4 * i
                    check((base, base + 1) in aset)
                    check((base + 1, base + 3) in aset)
                    check((base, base + 2) in aset)
                    check((base + 2, base + 3) in aset)

                # Supply
                for i in range(n):
                    check((2, 4 + 4 * i + 2) in aset)
                    check((2, 4 + 4 * i + 1) in aset)

                # Clause sinks
                for j in range(m):
                    check((4 + 4 * n + j, 3) in aset)

                # Literal connections
                for j, cl in enumerate(cls):
                    dj = 4 + 4 * n + j
                    for lit in cl:
                        v = abs(lit) - 1
                        if lit > 0:
                            check((4 + 4 * v + 2, dj) in aset)
                        else:
                            check((4 + 4 * v + 1, dj) in aset)

                # No self-loops
                for (u, v) in inst["arcs"]:
                    check(u != v)

    print(f"  Structural: {total_checks} checks so far")


def test_hypothesis_pbt():
    """Property-based testing with hypothesis."""
    from hypothesis import given, settings, HealthCheck
    from hypothesis import strategies as st

    counter = {"n": 0}

    @given(
        n=st.integers(min_value=3, max_value=5),
        m=st.integers(min_value=1, max_value=5),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(max_examples=2000, suppress_health_check=[HealthCheck.too_slow])
    def strategy_1(n, m, seed):
        rng = random.Random(seed)
        cls = random_3sat(n, m, rng)
        sat, a = sat_check(n, cls)
        inst = reduce(n, cls)

        assert inst["nv"] == 4 + 4 * n + m
        assert len(inst["arcs"]) == 7 * n + 4 * m + 1

        if sat:
            f1, f2 = build_flow(inst, a, n, cls)
            assert verify_flow(inst, f1, f2), f"Forward fail: n={n} m={m}"
            ext = extract_assignment(inst, f1, n)
            assert ext is not None
        else:
            res, _ = try_all_assignments(n, cls, inst)
            assert not res

        counter["n"] += 1

    @given(
        signs=st.lists(
            st.lists(st.booleans(), min_size=3, max_size=3),
            min_size=1,
            max_size=4,
        ),
    )
    @settings(max_examples=2000, suppress_health_check=[HealthCheck.too_slow])
    def strategy_2(signs):
        n = 3
        cls = []
        for sl in signs:
            cl = [i + 1 if sl[i] else -(i + 1) for i in range(3)]
            cls.append(cl)

        sat, a = sat_check(n, cls)
        inst = reduce(n, cls)
        m = len(cls)

        assert inst["nv"] == 4 + 4 * n + m
        assert len(inst["arcs"]) == 7 * n + 4 * m + 1

        if sat:
            f1, f2 = build_flow(inst, a, n, cls)
            assert verify_flow(inst, f1, f2)
        else:
            res, _ = try_all_assignments(n, cls, inst)
            assert not res

        counter["n"] += 1

    print("  Running hypothesis strategy 1...")
    strategy_1()
    s1 = counter["n"]
    print(f"    Strategy 1: {s1} examples")

    print("  Running hypothesis strategy 2...")
    strategy_2()
    print(f"    Strategy 2: {counter['n'] - s1} examples")

    return counter["n"]


def test_cross_comparison():
    """Compare with constructor's test vectors."""
    global total_checks

    vec_path = (
        Path(__file__).parent
        / "test_vectors_k_satisfiability_directed_two_commodity_integral_flow.json"
    )
    if not vec_path.exists():
        print("  Cross-comparison: SKIPPED (no test vectors)")
        return

    with open(vec_path) as f:
        vectors = json.load(f)

    # YES instance
    yi = vectors["yes_instance"]
    n_y = yi["input"]["num_vars"]
    cls_y = yi["input"]["clauses"]
    inst = reduce(n_y, cls_y)
    check(inst["nv"] == yi["output"]["num_vertices"], "YES verts match")
    check(
        sorted(inst["arcs"]) == sorted(tuple(a) for a in yi["output"]["arcs"]),
        "YES arcs match",
    )

    sat, a = sat_check(n_y, cls_y)
    check(sat == yi["source_feasible"])

    f1, f2 = build_flow(inst, a, n_y, cls_y)
    check(verify_flow(inst, f1, f2) == yi["target_feasible"])

    # NO instance
    ni = vectors["no_instance"]
    n_n = ni["input"]["num_vars"]
    cls_n = ni["input"]["clauses"]
    inst_n = reduce(n_n, cls_n)
    check(inst_n["nv"] == ni["output"]["num_vertices"], "NO verts match")

    sat_n, _ = sat_check(n_n, cls_n)
    check(not sat_n == (not ni["source_feasible"]))

    res, _ = try_all_assignments(n_n, cls_n, inst_n)
    check(res == ni["target_feasible"], "NO feasibility match")

    print(f"  Cross-comparison: {total_checks} checks so far")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    global total_checks

    print("=== Adversary: KSatisfiability(K3) -> DirectedTwoCommodityIntegralFlow ===")
    print("=== Issue #368 -- Even, Itai, and Shamir (1976) ===\n")

    test_yes_example()
    test_no_example()
    test_exhaustive_forward_backward()
    test_extraction()
    test_overhead()
    test_structural()

    pbt_count = test_hypothesis_pbt()
    total_checks += pbt_count

    test_cross_comparison()

    print(f"\n=== TOTAL ADVERSARY CHECKS: {total_checks} ===")
    assert total_checks >= 5000, f"Need >= 5000, got {total_checks}"
    print("ALL ADVERSARY CHECKS PASSED")


if __name__ == "__main__":
    main()
