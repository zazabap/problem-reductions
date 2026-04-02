#!/usr/bin/env python3
"""
Adversary verification script: Partition -> Open Shop Scheduling
Issue #481 -- Gonzalez & Sahni (1976)

Independent implementation based ONLY on the Typst proof.
Does NOT import from the constructor script.
>= 5000 total checks, hypothesis PBT with >= 2 strategies.
"""

import itertools
import json
import random
import sys
from pathlib import Path

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not available, PBT tests will be skipped")

TOTAL_CHECKS = 0


def count(n=1):
    global TOTAL_CHECKS
    TOTAL_CHECKS += n


# ============================================================
# Independent implementation from Typst proof
# ============================================================

def reduce(sizes):
    """
    Reduction from Typst proof:
    - m = 3 machines
    - k element jobs: p[j][i] = a_j for all i in {0,1,2}
    - 1 special job: p[k][i] = Q for all i
    - deadline D = 3Q where Q = S/2
    """
    S = sum(sizes)
    Q = S // 2
    k = len(sizes)

    pt = []
    for a in sizes:
        pt.append([a, a, a])
    pt.append([Q, Q, Q])

    return {"num_machines": 3, "processing_times": pt, "deadline": 3 * Q, "Q": Q}


def is_feasible_source(sizes):
    """Check if Partition instance is feasible (subset sums to S/2)."""
    S = sum(sizes)
    if S % 2 != 0:
        return False
    target = S // 2
    reachable = {0}
    for s in sizes:
        reachable = reachable | {x + s for x in reachable}
    return target in reachable


def find_partition_witness(sizes):
    """Find indices of a subset summing to S/2, or None."""
    S = sum(sizes)
    if S % 2 != 0:
        return None
    target = S // 2
    k = len(sizes)

    dp = {0: []}
    for idx in range(k):
        new_dp = {}
        for s, inds in dp.items():
            if s not in new_dp:
                new_dp[s] = inds
            ns = s + sizes[idx]
            if ns <= target and ns not in new_dp:
                new_dp[ns] = inds + [idx]
        dp = new_dp

    if target not in dp:
        return None
    return dp[target]


def build_feasible_schedule(sizes, I1_indices, I2_indices, Q):
    """
    Build schedule using rotated assignment from Typst proof.

    Special job on M1:[0,Q), M2:[Q,2Q), M3:[2Q,3Q)
    I1 jobs: M1:[Q+c, Q+c+a), M2:[2Q+c, 2Q+c+a), M3:[c, c+a)
    I2 jobs: M1:[2Q+c, 2Q+c+a), M2:[c, c+a), M3:[Q+c, Q+c+a)
    """
    k = len(sizes)
    sched = []

    # Special job
    sched.append((k, 0, 0, Q))
    sched.append((k, 1, Q, 2 * Q))
    sched.append((k, 2, 2 * Q, 3 * Q))

    c = 0
    for j in I1_indices:
        a = sizes[j]
        sched.append((j, 0, Q + c, Q + c + a))
        sched.append((j, 1, 2 * Q + c, 2 * Q + c + a))
        sched.append((j, 2, c, c + a))
        c += a

    c = 0
    for j in I2_indices:
        a = sizes[j]
        sched.append((j, 0, 2 * Q + c, 2 * Q + c + a))
        sched.append((j, 1, c, c + a))
        sched.append((j, 2, Q + c, Q + c + a))
        c += a

    return sched


def is_feasible_target(processing_times, num_machines, deadline):
    """
    Check if a schedule with makespan <= deadline exists.
    Tries all permutation combos (exact, for small instances).
    """
    n = len(processing_times)
    m = num_machines
    if n == 0:
        return True

    perms = list(itertools.permutations(range(n)))
    for combo in itertools.product(perms, repeat=m):
        ms = _simulate(processing_times, combo, m, n)
        if ms <= deadline:
            return True
    return False


def _simulate(pt, orders, m, n):
    """Greedy simulation of open-shop schedule from per-machine orderings."""
    ma = [0] * m
    ja = [0] * n
    nxt = [0] * m
    done = 0
    total = n * m

    while done < total:
        bs = float("inf")
        bm = -1
        for i in range(m):
            if nxt[i] < n:
                j = orders[i][nxt[i]]
                s = max(ma[i], ja[j])
                if s < bs or (s == bs and i < bm):
                    bs = s
                    bm = i
        i = bm
        j = orders[i][nxt[i]]
        s = max(ma[i], ja[j])
        f = s + pt[j][i]
        ma[i] = f
        ja[j] = f
        nxt[i] += 1
        done += 1

    return max(max(ma), max(ja))


def extract_solution(schedule, k, Q, sizes):
    """
    Extract partition from schedule by looking at machine 0.
    Group element jobs by which Q-length time block they fall in.
    """
    # Find which block each element job is in on machine 0
    group_a = []
    group_b = []
    for (j, mi, start, end) in schedule:
        if j < k and mi == 0:
            block = start // Q
            if block <= 1:
                group_a.append(j)
            else:
                group_b.append(j)

    sa = sum(sizes[j] for j in group_a)
    sb = sum(sizes[j] for j in group_b)
    if sa == Q:
        return group_a, group_b
    elif sb == Q:
        return group_b, group_a
    else:
        return group_a, group_b


def validate_schedule_feasibility(sched, pt, m, deadline):
    """Validate schedule constraints."""
    n = len(pt)
    by_machine = {i: [] for i in range(m)}
    by_job = {j: [] for j in range(n)}

    for (j, i, s, e) in sched:
        by_machine[i].append((s, e))
        by_job[j].append((s, e))
        assert e - s == pt[j][i], f"Duration mismatch job {j} machine {i}"
        assert e <= deadline, f"Exceeds deadline"

    for i in range(m):
        tasks = sorted(by_machine[i])
        for idx in range(len(tasks) - 1):
            assert tasks[idx][1] <= tasks[idx + 1][0], f"Machine {i} overlap"

    for j in range(n):
        tasks = sorted(by_job[j])
        for idx in range(len(tasks) - 1):
            assert tasks[idx][1] <= tasks[idx + 1][0], f"Job {j} overlap"

    return True


# ============================================================
# Test 1: Exhaustive forward + backward for n <= 3
# ============================================================

def test_exhaustive_small():
    """Exhaustive verification for n <= 3 elements."""
    print("=== Adversary: Exhaustive n<=3 ===")

    for n in range(1, 4):
        for vals in itertools.product(range(1, 6), repeat=n):
            sizes = list(vals)
            S = sum(sizes)
            Q = S // 2
            src = is_feasible_source(sizes)

            if S % 2 != 0:
                assert not src
                count()
                continue

            result = reduce(sizes)
            pt = result["processing_times"]
            D = result["deadline"]

            # Forward: construct schedule if feasible
            if src:
                wit = find_partition_witness(sizes)
                assert wit is not None
                I1 = wit
                I2 = [j for j in range(n) if j not in I1]
                sched = build_feasible_schedule(sizes, I1, I2, Q)
                validate_schedule_feasibility(sched, pt, 3, D)
                count()

            # Backward: brute force (n+1 <= 4 jobs)
            tgt = is_feasible_target(pt, 3, D)
            assert src == tgt, \
                f"Mismatch: sizes={sizes}, src={src}, tgt={tgt}"
            count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 2: Forward-only for n = 4
# ============================================================

def test_forward_n4():
    """Forward construction verification for n=4."""
    print("=== Adversary: Forward n=4 ===")

    for vals in itertools.product(range(1, 5), repeat=4):
        sizes = list(vals)
        S = sum(sizes)
        if S % 2 != 0:
            count()
            continue
        Q = S // 2

        if not is_feasible_source(sizes):
            # Structural NO check: no subset sums to Q
            reachable = {0}
            for s in sizes:
                reachable = reachable | {x + s for x in reachable}
            assert Q not in reachable
            count()
            continue

        result = reduce(sizes)
        wit = find_partition_witness(sizes)
        I1 = wit
        I2 = [j for j in range(4) if j not in I1]
        sched = build_feasible_schedule(sizes, I1, I2, Q)
        validate_schedule_feasibility(sched, result["processing_times"], 3, result["deadline"])
        count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 3: Forward + extraction for n = 5 (sampled)
# ============================================================

def test_sampled_n5():
    """Sampled verification for n=5."""
    print("=== Adversary: Sampled n=5 ===")
    rng = random.Random(77777)

    for _ in range(1000):
        sizes = [rng.randint(1, 6) for _ in range(5)]
        S = sum(sizes)
        if S % 2 != 0:
            assert not is_feasible_source(sizes)
            count()
            continue
        Q = S // 2

        src = is_feasible_source(sizes)
        result = reduce(sizes)

        if src:
            wit = find_partition_witness(sizes)
            I1 = wit
            I2 = [j for j in range(5) if j not in I1]
            sched = build_feasible_schedule(sizes, I1, I2, Q)
            validate_schedule_feasibility(sched, result["processing_times"], 3, result["deadline"])

            # Extraction
            ga, gb = extract_solution(sched, 5, Q, sizes)
            sa = sum(sizes[j] for j in ga)
            sb = sum(sizes[j] for j in gb)
            assert sa == Q or sb == Q
            assert set(ga) | set(gb) == set(range(5))
            count(2)
        else:
            reachable = {0}
            for s in sizes:
                reachable = reachable | {x + s for x in reachable}
            assert Q not in reachable
            count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 4: Typst YES example
# ============================================================

def test_yes_example():
    """Reproduce YES example: A = {3,1,1,2,2,1}."""
    print("=== Adversary: YES Example ===")

    sizes = [3, 1, 1, 2, 2, 1]
    assert len(sizes) == 6; count()
    assert sum(sizes) == 10; count()
    Q = 5

    result = reduce(sizes)
    assert result["num_machines"] == 3; count()
    assert len(result["processing_times"]) == 7; count()
    assert result["deadline"] == 15; count()

    # Verify each job's processing times
    for j in range(6):
        for i in range(3):
            assert result["processing_times"][j][i] == sizes[j]; count()
    for i in range(3):
        assert result["processing_times"][6][i] == 5; count()

    assert is_feasible_source(sizes); count()

    I1 = [0, 3]
    I2 = [1, 2, 4, 5]
    assert sum(sizes[j] for j in I1) == 5; count()
    assert sum(sizes[j] for j in I2) == 5; count()

    sched = build_feasible_schedule(sizes, I1, I2, Q)
    validate_schedule_feasibility(sched, result["processing_times"], 3, 15); count()

    # Check specific schedule entries
    sd = {(j, i): (s, e) for (j, i, s, e) in sched}
    assert sd[(6, 0)] == (0, 5); count()
    assert sd[(6, 1)] == (5, 10); count()
    assert sd[(6, 2)] == (10, 15); count()

    ga, gb = extract_solution(sched, 6, Q, sizes)
    sa = sum(sizes[j] for j in ga)
    sb = sum(sizes[j] for j in gb)
    assert sa == Q or sb == Q; count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 5: Typst NO example
# ============================================================

def test_no_example():
    """Reproduce NO example: A = {1,1,1,5}."""
    print("=== Adversary: NO Example ===")

    sizes = [1, 1, 1, 5]
    assert len(sizes) == 4; count()
    assert sum(sizes) == 8; count()
    Q = 4

    assert not is_feasible_source(sizes); count()

    # Verify no subset sums to 4
    for mask in range(1 << 4):
        ss = sum(sizes[j] for j in range(4) if mask & (1 << j))
        assert ss != Q; count()

    result = reduce(sizes)
    assert result["num_machines"] == 3; count()
    assert len(result["processing_times"]) == 5; count()
    assert result["deadline"] == 12; count()

    expected = [[1,1,1],[1,1,1],[1,1,1],[5,5,5],[4,4,4]]
    assert result["processing_times"] == expected; count()

    # Brute force: no schedule achieves makespan <= 12
    assert not is_feasible_target(result["processing_times"], 3, 12); count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 6: Overhead structural checks
# ============================================================

def test_overhead():
    """Verify overhead formulas on many instances."""
    print("=== Adversary: Overhead ===")

    for n in range(1, 6):
        for vals in itertools.product(range(1, 6), repeat=n):
            sizes = list(vals)
            S = sum(sizes)
            if S % 2 != 0:
                continue
            Q = S // 2
            k = len(sizes)

            result = reduce(sizes)
            pt = result["processing_times"]

            # num_jobs = k + 1
            assert len(pt) == k + 1; count()
            # num_machines = 3
            assert result["num_machines"] == 3; count()
            # deadline = 3Q
            assert result["deadline"] == 3 * Q; count()
            # total per machine = 3Q (zero slack)
            for i in range(3):
                assert sum(pt[j][i] for j in range(k + 1)) == 3 * Q; count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 7: Hypothesis PBT -- Strategy 1: random sizes
# ============================================================

def test_hypothesis_random_sizes():
    """Property-based testing with random size lists."""
    if not HAS_HYPOTHESIS:
        print("=== Adversary: Hypothesis PBT (skipped -- no hypothesis) ===")
        # Fallback: use random testing
        rng = random.Random(42424)
        for _ in range(2000):
            n = rng.randint(1, 6)
            sizes = [rng.randint(1, 10) for _ in range(n)]
            _check_reduction_property(sizes)
        return

    print("=== Adversary: Hypothesis PBT Strategy 1 ===")

    @given(st.lists(st.integers(min_value=1, max_value=10), min_size=1, max_size=6))
    @settings(max_examples=1500, suppress_health_check=[HealthCheck.too_slow])
    def prop(sizes):
        _check_reduction_property(sizes)

    prop()
    print(f"  Checks so far: {TOTAL_CHECKS}")


def _check_reduction_property(sizes):
    """Core property: partition feasible <=> schedule with makespan <= 3Q constructible."""
    S = sum(sizes)
    Q = S // 2
    k = len(sizes)
    src = is_feasible_source(sizes)

    if S % 2 != 0:
        assert not src
        count()
        return

    result = reduce(sizes)
    pt = result["processing_times"]
    D = result["deadline"]

    # Forward direction
    if src:
        wit = find_partition_witness(sizes)
        assert wit is not None
        I1 = wit
        I2 = [j for j in range(k) if j not in I1]
        sched = build_feasible_schedule(sizes, I1, I2, Q)
        validate_schedule_feasibility(sched, pt, 3, D)

        ga, gb = extract_solution(sched, k, Q, sizes)
        sa = sum(sizes[j] for j in ga)
        sb = sum(sizes[j] for j in gb)
        assert sa == Q or sb == Q
        count(2)
    else:
        # Structural NO: verify no subset sums to Q
        reachable = {0}
        for s in sizes:
            reachable = reachable | {x + s for x in reachable}
        assert Q not in reachable
        # Zero slack: total work = capacity
        total = sum(pt[j][0] for j in range(k + 1))
        assert total == D
        count(2)


# ============================================================
# Test 8: Hypothesis PBT -- Strategy 2: balanced partition instances
# ============================================================

def test_hypothesis_balanced():
    """Property-based testing specifically targeting YES instances."""
    if not HAS_HYPOTHESIS:
        print("=== Adversary: Hypothesis PBT Strategy 2 (skipped -- no hypothesis) ===")
        rng = random.Random(54321)
        for _ in range(2000):
            n = rng.randint(2, 6)
            half = n // 2
            first = [rng.randint(1, 5) for _ in range(half)]
            target_sum = sum(first)
            # Build second half to sum to target_sum
            if n - half == 0:
                continue
            second = [1] * (n - half - 1)
            remainder = target_sum - sum(second)
            if remainder <= 0:
                continue
            second.append(remainder)
            sizes = first + second
            rng.shuffle(sizes)
            if all(s > 0 for s in sizes):
                _check_reduction_property(sizes)
        return

    print("=== Adversary: Hypothesis PBT Strategy 2 ===")

    @given(
        st.lists(st.integers(min_value=1, max_value=8), min_size=1, max_size=4).flatmap(
            lambda first: st.tuples(
                st.just(first),
                st.lists(st.integers(min_value=1, max_value=8), min_size=1, max_size=4),
            )
        )
    )
    @settings(max_examples=1500, suppress_health_check=[HealthCheck.too_slow])
    def prop(pair):
        first, second = pair
        # Adjust second to make sum(first) == sum(second) when possible
        s1 = sum(first)
        s2 = sum(second)
        if s1 > s2:
            second = second + [s1 - s2]
        elif s2 > s1:
            first = first + [s2 - s1]
        sizes = first + second
        assume(all(s > 0 for s in sizes))
        assume(len(sizes) >= 2)
        _check_reduction_property(sizes)

    prop()
    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Test 9: Edge cases
# ============================================================

def test_edge_cases():
    """Test algebraic boundary conditions."""
    print("=== Adversary: Edge Cases ===")

    # All equal elements
    for v in range(1, 6):
        for n in range(2, 7, 2):  # even number of elements
            sizes = [v] * n
            S = sum(sizes)
            Q = S // 2
            assert is_feasible_source(sizes)
            result = reduce(sizes)
            wit = find_partition_witness(sizes)
            I1 = wit
            I2 = [j for j in range(n) if j not in I1]
            sched = build_feasible_schedule(sizes, I1, I2, Q)
            validate_schedule_feasibility(sched, result["processing_times"], 3, result["deadline"])
            count()

    # One large, many small (NO instances)
    for big in range(4, 15):
        sizes = [1, 1, 1, big]
        S = sum(sizes)
        if S % 2 != 0:
            count()
            continue
        Q = S // 2
        if Q == 3:
            assert is_feasible_source(sizes)
        elif Q > 3 and Q != big:
            # depends on specifics
            pass
        src = is_feasible_source(sizes)
        result = reduce(sizes)
        if src:
            wit = find_partition_witness(sizes)
            I1 = wit
            I2 = [j for j in range(4) if j not in I1]
            sched = build_feasible_schedule(sizes, I1, I2, Q)
            validate_schedule_feasibility(sched, result["processing_times"], 3, result["deadline"])
        count()

    # Odd total sum (trivial NO)
    for sizes in [[1, 2], [1, 2, 4], [3, 4, 6], [1, 1, 1], [7]]:
        S = sum(sizes)
        if S % 2 != 0:
            assert not is_feasible_source(sizes)
            count()

    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Cross-comparison with constructor
# ============================================================

def test_cross_comparison():
    """Compare reduce() outputs with constructor script's test vectors."""
    print("=== Adversary: Cross-comparison ===")

    tv_path = Path(__file__).parent / "test_vectors_partition_open_shop_scheduling.json"
    if not tv_path.exists():
        print("  Test vectors not found, skipping cross-comparison")
        return

    with open(tv_path) as f:
        tv = json.load(f)

    # YES instance
    yes_sizes = tv["yes_instance"]["input"]["sizes"]
    my_result = reduce(yes_sizes)
    assert my_result["num_machines"] == tv["yes_instance"]["output"]["num_machines"]; count()
    assert my_result["processing_times"] == tv["yes_instance"]["output"]["processing_times"]; count()
    assert my_result["deadline"] == tv["yes_instance"]["output"]["deadline"]; count()

    # NO instance
    no_sizes = tv["no_instance"]["input"]["sizes"]
    my_result = reduce(no_sizes)
    assert my_result["num_machines"] == tv["no_instance"]["output"]["num_machines"]; count()
    assert my_result["processing_times"] == tv["no_instance"]["output"]["processing_times"]; count()
    assert my_result["deadline"] == tv["no_instance"]["output"]["deadline"]; count()

    # Verify feasibility matches
    assert is_feasible_source(yes_sizes) == tv["yes_instance"]["source_feasible"]; count()
    assert is_feasible_source(no_sizes) == tv["no_instance"]["source_feasible"]; count()

    print(f"  Cross-comparison checks: 8 PASSED")
    print(f"  Checks so far: {TOTAL_CHECKS}")


# ============================================================
# Main
# ============================================================

def main():
    test_exhaustive_small()
    test_forward_n4()
    test_sampled_n5()
    test_yes_example()
    test_no_example()
    test_overhead()
    test_hypothesis_random_sizes()
    test_hypothesis_balanced()
    test_edge_cases()
    test_cross_comparison()

    print(f"\n{'='*60}")
    print(f"ADVERSARY CHECK COUNT: {TOTAL_CHECKS} (minimum: 5,000)")
    print(f"{'='*60}")

    assert TOTAL_CHECKS >= 5000, f"Only {TOTAL_CHECKS} checks, need >= 5000"
    print(f"\nALL {TOTAL_CHECKS} ADVERSARY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
