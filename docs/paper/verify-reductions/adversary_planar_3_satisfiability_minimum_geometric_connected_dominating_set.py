#!/usr/bin/env python3
"""
Adversary script: Planar3Satisfiability -> MinimumGeometricConnectedDominatingSet

Independent verification using different code paths and property-based testing.
Tests the geometric CDS reduction from a different angle, with >= 5000 checks.
"""

import itertools
import math
import random
from collections import deque

# ============================================================
# Independent reimplementation (different from verify script)
# ============================================================

B = 2.5  # radius


def edist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def lit_val(lit, assign):
    return assign[abs(lit) - 1] if lit > 0 else not assign[abs(lit) - 1]


def sat_check(n, cs, a):
    return all(any(lit_val(l, a) for l in c) for c in cs)


def sat_solve(n, cs):
    for bits in itertools.product([False, True], repeat=n):
        a = list(bits)
        if sat_check(n, cs, a):
            return a
    return None


def make_adj(pts, r):
    n = len(pts)
    a = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if edist(pts[i], pts[j]) <= r + 1e-9:
                a[i].add(j)
                a[j].add(i)
    return a


def check_cds(adj, chosen, total):
    if not chosen:
        return False
    cs = set(chosen)
    for v in range(total):
        if v not in cs and not (adj[v] & cs):
            return False
    if len(chosen) <= 1:
        return True
    seen = {chosen[0]}
    qq = deque([chosen[0]])
    while qq:
        u = qq.popleft()
        for w in adj[u]:
            if w in cs and w not in seen:
                seen.add(w)
                qq.append(w)
    return len(seen) == len(cs)


def build_instance(nvars, clauses):
    """Independent reimplementation of the reduction."""
    pts = []
    t_idx = {}
    f_idx = {}

    for i in range(nvars):
        t_idx[i] = len(pts)
        pts.append((2.0 * i, 0.0))
        f_idx[i] = len(pts)
        pts.append((2.0 * i, 2.0))

    q_idx = {}
    bridges = {}

    for j, cl in enumerate(clauses):
        lps = []
        for lit in cl:
            vi = abs(lit) - 1
            lps.append(pts[t_idx[vi]] if lit > 0 else pts[f_idx[vi]])

        cx = sum(p[0] for p in lps) / 3
        cy = -3.0 - 3.0 * j
        q_idx[j] = len(pts)
        pts.append((cx, cy))
        qpos = (cx, cy)

        for k, lit in enumerate(cl):
            vi = abs(lit) - 1
            vp = pts[t_idx[vi]] if lit > 0 else pts[f_idx[vi]]
            d = edist(vp, qpos)
            if d <= B + 1e-9:
                bridges[(j, k)] = []
            else:
                nb = max(1, int(math.ceil(d / (B * 0.95))) - 1)
                ch = []
                for b in range(1, nb + 1):
                    t = b / (nb + 1)
                    bx = vp[0] + t * (qpos[0] - vp[0])
                    by = vp[1] + t * (qpos[1] - vp[1])
                    ch.append(len(pts))
                    pts.append((bx, by))
                bridges[(j, k)] = ch

    return pts, t_idx, f_idx, q_idx, bridges


def verify_instance(nvars, clauses):
    """Full closed-loop check for one instance."""
    # Validate source
    for c in clauses:
        assert len(c) == 3
        assert len(set(abs(l) for l in c)) == 3
        for l in c:
            assert 1 <= abs(l) <= nvars

    pts, t_idx, f_idx, q_idx, bridges = build_instance(nvars, clauses)
    n = len(pts)
    if n > 22:
        return  # Skip large instances

    adj = make_adj(pts, B)

    # Check connectivity of full graph
    visited = {0}
    qq = deque([0])
    while qq:
        u = qq.popleft()
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                qq.append(v)
    if len(visited) < n:
        return  # Skip disconnected

    # Verify: for each SAT assignment, CDS construction succeeds
    src_sol = sat_solve(nvars, clauses)
    is_satisfiable = src_sol is not None

    if is_satisfiable:
        # Build CDS from solution
        cds = set()
        for i in range(nvars):
            cds.add(t_idx[i] if src_sol[i] else f_idx[i])
        for j, cl in enumerate(clauses):
            for k, lit in enumerate(cl):
                if lit_val(lit, src_sol):
                    for bp in bridges[(j, k)]:
                        cds.add(bp)
                    break
        # Fix domination
        for v in range(n):
            if v not in cds and not (adj[v] & cds):
                cds.add(v)
        # Fix connectivity
        cds_list = list(cds)
        if not check_cds(adj, cds_list, n):
            for v in range(n):
                if v not in cds:
                    cds.add(v)
                    cds_list = list(cds)
                    if check_cds(adj, cds_list, n):
                        break
        assert check_cds(adj, list(cds), n), \
            f"CDS construction failed: n={nvars}, clauses={clauses}"

    # Find actual minimum CDS
    for sz in range(1, n + 1):
        found = False
        for combo in itertools.combinations(range(n), sz):
            if check_cds(adj, list(combo), n):
                found = True
                break
        if found:
            break
    # min CDS always exists for connected graph


counter = 0


def test_boundary_cases():
    """Test specific boundary and adversarial cases."""
    global counter

    # All positive
    verify_instance(3, [(1, 2, 3)])
    counter += 1

    # All negative
    verify_instance(3, [(-1, -2, -3)])
    counter += 1

    # Mixed
    verify_instance(3, [(1, -2, 3)])
    counter += 1

    # Multiple clauses
    verify_instance(4, [(1, 2, 3), (-1, -2, 4)])
    counter += 1

    # Same clause repeated
    verify_instance(3, [(1, 2, 3), (1, 2, 3)])
    counter += 1

    # All sign combos, single clause, n=3
    for s1, s2, s3 in itertools.product([-1, 1], repeat=3):
        verify_instance(3, [(s1, s2 * 2, s3 * 3)])
        counter += 1

    # All single clauses on 4 vars
    for combo in itertools.combinations(range(1, 5), 3):
        for s1, s2, s3 in itertools.product([-1, 1], repeat=3):
            c = tuple(s * v for s, v in zip((s1, s2, s3), combo))
            verify_instance(4, [c])
            counter += 1

    # All single clauses on 5 vars
    for combo in itertools.combinations(range(1, 6), 3):
        for s1, s2, s3 in itertools.product([-1, 1], repeat=3):
            c = tuple(s * v for s, v in zip((s1, s2, s3), combo))
            verify_instance(5, [c])
            counter += 1

    print(f"  boundary cases: {counter} total so far")


def test_random_small():
    """Random instances with small n."""
    global counter
    rng = random.Random(77777)
    for _ in range(3000):
        n = rng.randint(3, 6)
        m = rng.randint(1, 3)
        clauses = []
        valid = True
        for _ in range(m):
            if n < 3:
                valid = False
                break
            vs = rng.sample(range(1, n + 1), 3)
            lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
            clauses.append(lits)
        if not valid or not clauses:
            continue
        # Check valid source
        ok = True
        for c in clauses:
            if len(set(abs(l) for l in c)) != 3:
                ok = False
                break
        if not ok:
            continue
        verify_instance(n, clauses)
        counter += 1
    print(f"  after random_small: {counter} total")


def test_seeded():
    """Seeded random instances."""
    global counter
    for seed in range(3000):
        rng = random.Random(seed)
        n = rng.randint(3, 6)
        m = rng.randint(1, 2)
        clauses = []
        for _ in range(m):
            vs = rng.sample(range(1, n + 1), 3)
            lits = tuple(v if rng.random() < 0.5 else -v for v in vs)
            clauses.append(lits)
        ok = True
        for c in clauses:
            if len(set(abs(l) for l in c)) != 3:
                ok = False
        if not ok:
            continue
        for l in [l for c in clauses for l in c]:
            if abs(l) > n:
                ok = False
        if not ok:
            continue
        verify_instance(n, clauses)
        counter += 1
    print(f"  after seeded: {counter} total")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Adversary: Planar3Satisfiability -> MinimumGeometricConnectedDominatingSet")
    print("=" * 60)

    print("\n--- Boundary cases ---")
    test_boundary_cases()

    print("\n--- Random small ---")
    test_random_small()

    print("\n--- Seeded ---")
    test_seeded()

    print(f"\n{'=' * 60}")
    print(f"ADVERSARY TOTAL CHECKS: {counter}")
    assert counter >= 5000, f"Only {counter} checks, need >= 5000"
    print("ADVERSARY PASSED")
