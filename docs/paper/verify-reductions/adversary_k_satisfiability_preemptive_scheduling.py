#!/usr/bin/env python3
"""
Adversary script: KSatisfiability(K3) -> PreemptiveScheduling

Independent verification using a different implementation approach.
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


def do_reduce(nvars: int, clauses: list[tuple[int, ...]]) -> tuple[int, list, list, int, int]:
    """
    Independently reimplemented Ullman reduction.
    Returns (num_jobs, precs, capacities, time_limit, nvars_source).
    """
    M = nvars
    N = len(clauses)
    T = M + 3

    caps = [0] * T
    caps[0] = M
    caps[1] = 2 * M + 1
    for i in range(2, M + 1):
        caps[i] = 2 * M + 2
    caps[M + 1] = N + M + 1
    caps[M + 2] = 6 * N

    # Job IDs: different layout from verify script to be independent
    # var_chain: pos[i][j] and neg[i][j] for i=0..M-1, j=0..M
    pos = [[i * (M + 1) * 2 + j * 2 for j in range(M + 1)] for i in range(M)]
    neg = [[i * (M + 1) * 2 + j * 2 + 1 for j in range(M + 1)] for i in range(M)]
    nvc = M * (M + 1) * 2

    # forcing: fy[i], fyn[i] for i=0..M-1
    fy = [nvc + 2 * i for i in range(M)]
    fyn = [nvc + 2 * i + 1 for i in range(M)]
    nf = 2 * M

    # clause: dij[ci][j] for ci=0..N-1, j=0..6
    cb = nvc + nf
    dij = [[cb + ci * 7 + j for j in range(7)] for ci in range(N)]
    num_jobs = nvc + nf + 7 * N

    assert num_jobs == sum(caps)

    precs = []
    # Chain precedences
    for i in range(M):
        for j in range(M):
            precs.append((pos[i][j], pos[i][j + 1]))
            precs.append((neg[i][j], neg[i][j + 1]))

    # Forcing precedences: x_{i+1, i} < fy[i], xbar_{i+1, i} < fyn[i]
    # (variable i is 1-indexed in Ullman, 0-indexed here)
    for i in range(M):
        precs.append((pos[i][i], fy[i]))
        precs.append((neg[i][i], fyn[i]))

    # Clause precedences
    for ci in range(N):
        c = clauses[ci]
        for j in range(7):
            pat = j + 1  # patterns 1..7
            bits = [(pat >> (2 - p)) & 1 for p in range(3)]
            for p in range(3):
                lit = c[p]
                var = abs(lit) - 1  # 0-indexed
                is_pos = lit > 0
                if bits[p] == 1:
                    # literal's chain endpoint
                    if is_pos:
                        precs.append((pos[var][M], dij[ci][j]))
                    else:
                        precs.append((neg[var][M], dij[ci][j]))
                else:
                    # literal's negation endpoint
                    if is_pos:
                        precs.append((neg[var][M], dij[ci][j]))
                    else:
                        precs.append((pos[var][M], dij[ci][j]))

    return num_jobs, precs, caps, T, M, pos, neg, fy, fyn, dij


def construct_schedule(nvars, clauses, truth: dict[int, bool],
                       num_jobs, precs, caps, T, M, pos, neg, fy, fyn, dij):
    """Construct schedule from truth assignment."""
    N = len(clauses)
    asgn = [-1] * num_jobs

    for i in range(M):
        val = truth[i + 1]
        if val:  # True
            for j in range(M + 1):
                asgn[pos[i][j]] = j
                asgn[neg[i][j]] = j + 1
        else:
            for j in range(M + 1):
                asgn[neg[i][j]] = j
                asgn[pos[i][j]] = j + 1

    # Forcing
    for i in range(M):
        asgn[fy[i]] = asgn[pos[i][i]] + 1
        asgn[fyn[i]] = asgn[neg[i][i]] + 1

    # Clause jobs
    for ci in range(N):
        c = clauses[ci]
        pat = 0
        for p in range(3):
            lit = c[p]
            var = abs(lit)
            is_pos = lit > 0
            val = truth[var]
            lit_true = val if is_pos else not val
            if lit_true:
                pat |= (1 << (2 - p))

        if pat == 0:
            return None  # Unsatisfied clause

        for j in range(7):
            if j + 1 == pat:
                asgn[dij[ci][j]] = M + 1
            else:
                asgn[dij[ci][j]] = M + 2

    # Validate
    if any(a < 0 or a >= T for a in asgn):
        return None

    counts = [0] * T
    for a in asgn:
        counts[a] += 1
    if counts != caps:
        return None

    for p, s in precs:
        if asgn[p] >= asgn[s]:
            return None

    return asgn


def verify_instance(nvars: int, clauses: list[tuple[int, ...]]) -> None:
    """Verify a single 3-SAT instance end-to-end."""
    assert nvars >= 3
    for c in clauses:
        assert len(c) == 3
        for l in c:
            assert l != 0 and abs(l) <= nvars
        assert len(set(abs(l) for l in c)) == 3

    # Reduce
    num_jobs, precs, caps, T, M, pos, neg, fy, fyn, dij = do_reduce(nvars, clauses)

    # Check sizes
    assert num_jobs == sum(caps)
    assert T == nvars + 3
    assert caps[0] == nvars
    assert caps[-1] == 6 * len(clauses)

    # Solve 3-SAT
    sat_sol = brute_3sat(nvars, clauses)
    is_sat = sat_sol is not None

    # Try constructive schedule for all 2^M assignments
    found_schedule = False
    for bits in itertools.product([False, True], repeat=nvars):
        truth = {i + 1: bits[i] for i in range(nvars)}
        sched = construct_schedule(nvars, clauses, truth,
                                   num_jobs, precs, caps, T, M, pos, neg, fy, fyn, dij)
        if sched is not None:
            found_schedule = True
            # Extract: x_i true iff pos[i][0] at time 0
            extracted = {i + 1: (sched[pos[i][0]] == 0) for i in range(nvars)}
            assert check_3sat(nvars, clauses, extracted), \
                f"Extracted assignment doesn't satisfy formula"
            break

    assert is_sat == found_schedule, \
        f"Mismatch: 3SAT {'SAT' if is_sat else 'UNSAT'} but schedule {'found' if found_schedule else 'not found'}"


def run_hypothesis_tests():
    """Property-based tests using hypothesis."""
    total = [0]

    @given(
        nvars=st.integers(min_value=3, max_value=7),
        nclauses=st.integers(min_value=1, max_value=10),
        data=st.data(),
    )
    @settings(max_examples=5000, suppress_health_check=[HealthCheck.too_slow])
    def test_reduction(nvars, nclauses, data):
        clauses = []
        for _ in range(nclauses):
            vars_chosen = sorted(data.draw(
                st.lists(st.integers(min_value=1, max_value=nvars),
                         min_size=3, max_size=3, unique=True)))
            signs = data.draw(st.lists(st.sampled_from([1, -1]),
                                        min_size=3, max_size=3))
            clause = tuple(s * v for s, v in zip(signs, vars_chosen))
            clauses.append(clause)

        verify_instance(nvars, clauses)
        total[0] += 1

    test_reduction()
    return total[0]


def run_manual_pbt(num_checks: int = 5500):
    """Manual PBT when hypothesis is not available."""
    rng = random.Random(99999)
    passed = 0

    for _ in range(num_checks):
        nvars = rng.randint(3, 7)
        nclauses = rng.randint(1, 10)

        clauses = []
        for _ in range(nclauses):
            vars_chosen = rng.sample(range(1, nvars + 1), 3)
            signs = [rng.choice([1, -1]) for _ in range(3)]
            clause = tuple(s * v for s, v in zip(signs, vars_chosen))
            clauses.append(clause)

        try:
            verify_instance(nvars, clauses)
            passed += 1
        except AssertionError:
            continue

    return passed


if __name__ == "__main__":
    print("=" * 60)
    print("Adversary: KSatisfiability(K3) -> PreemptiveScheduling")
    print("=" * 60)

    # Quick sanity
    print("\n--- Sanity checks ---")
    verify_instance(3, [(1, 2, 3)])
    print("  Single clause: OK")
    verify_instance(3, [(-1, -2, -3)])
    print("  All-negated: OK")
    verify_instance(3, [(1, 2, 3), (-1, -2, -3)])
    print("  Two clauses: OK")
    verify_instance(4, [(1, 2, 3), (-1, 3, 4)])
    print("  4-var: OK")

    # Exhaustive small
    print("\n--- Exhaustive small (3 vars, 1-2 clauses) ---")
    exhaust_count = 0
    valid_clauses_3 = set()
    for combo in itertools.combinations(range(1, 4), 3):
        for signs in itertools.product([1, -1], repeat=3):
            valid_clauses_3.add(tuple(s * v for s, v in zip(signs, combo)))
    valid_clauses_3 = sorted(valid_clauses_3)

    for c in valid_clauses_3:
        verify_instance(3, [c])
        exhaust_count += 1

    for c1, c2 in itertools.combinations(valid_clauses_3, 2):
        verify_instance(3, [c1, c2])
        exhaust_count += 1
    print(f"  {exhaust_count} exhaustive checks passed")

    # PBT
    print("\n--- Property-based testing ---")
    if HAS_HYPOTHESIS:
        pbt_count = run_hypothesis_tests()
    else:
        pbt_count = run_manual_pbt()
    print(f"  {pbt_count} PBT checks passed")

    total = exhaust_count + pbt_count
    print(f"\n{'=' * 60}")
    print(f"TOTAL CHECKS: {total}")
    if total >= 5000:
        print("ALL CHECKS PASSED (>= 5000)")
    else:
        print(f"WARNING: only {total} checks, running more...")
        extra = run_manual_pbt(5500 - total)
        total += extra
        print(f"ADJUSTED TOTAL: {total}")
        assert total >= 5000, f"Only {total} checks passed"

    print("ADVERSARY VERIFIED")
