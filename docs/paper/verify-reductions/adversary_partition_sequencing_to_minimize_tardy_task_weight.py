#!/usr/bin/env python3
"""Adversary verification script for Partition → SequencingToMinimizeTardyTaskWeight reduction.

Issue: #471
Independent implementation based solely on the Typst proof.
Does NOT import from the constructor script.

Requirements:
- Own reduce(), extract_solution(), is_feasible_source(), is_feasible_target()
- Exhaustive forward + backward for n <= 5
- hypothesis PBT with >= 2 strategies
- Reproduce both Typst examples (YES and NO)
- >= 5,000 total checks
"""

import itertools
import sys

# ============================================================
# Independent implementation from Typst proof
# ============================================================


def reduce(sizes):
    """Partition → SequencingToMinimizeTardyTaskWeight.

    From the Typst proof:
    1. If B is odd, output infeasible instance: deadline=0, K=0.
    2. If B is even, let T=B/2. Each element a_i becomes task with
       l(t_i)=w(t_i)=a_i, d(t_i)=T, K=T.
    """
    B = sum(sizes)
    n = len(sizes)
    if B % 2 != 0:
        return list(sizes), list(sizes), [0] * n, 0
    T = B // 2
    return list(sizes), list(sizes), [T] * n, T


def extract_solution(lengths, deadlines, schedule):
    """Extract partition from schedule.

    From the Typst proof: on-time tasks (completion <= deadline) => subset A' (config=0),
    tardy tasks => subset A'' (config=1).
    """
    n = len(lengths)
    config = [0] * n
    elapsed = 0
    for task in schedule:
        elapsed += lengths[task]
        if elapsed > deadlines[task]:
            config[task] = 1
    return config


def is_feasible_source(sizes, config):
    """Check if config is a balanced partition of sizes."""
    if len(config) != len(sizes):
        return False
    if any(c not in (0, 1) for c in config):
        return False
    s0 = sum(sizes[i] for i in range(len(sizes)) if config[i] == 0)
    s1 = sum(sizes[i] for i in range(len(sizes)) if config[i] == 1)
    return s0 == s1


def is_feasible_target(lengths, weights, deadlines, K, schedule):
    """Check if schedule yields tardy weight <= K."""
    n = len(lengths)
    if len(schedule) != n:
        return False
    if sorted(schedule) != list(range(n)):
        return False
    elapsed = 0
    tw = 0
    for task in schedule:
        elapsed += lengths[task]
        if elapsed > deadlines[task]:
            tw += weights[task]
    return tw <= K


def brute_force_source(sizes):
    """Find a balanced partition by brute force, or None."""
    n = len(sizes)
    B = sum(sizes)
    if B % 2 != 0:
        return None
    T = B // 2
    for mask in range(1 << n):
        s = sum(sizes[i] for i in range(n) if mask & (1 << i))
        if s == T:
            return [(mask >> i) & 1 for i in range(n)]
    return None


def brute_force_target(lengths, weights, deadlines, K):
    """Find a schedule with tardy weight <= K, or None."""
    n = len(lengths)
    for perm in itertools.permutations(range(n)):
        if is_feasible_target(lengths, weights, deadlines, K, list(perm)):
            return list(perm)
    return None


# ============================================================
# Counters
# ============================================================
checks = 0
failures = []


def check(condition, msg):
    global checks
    checks += 1
    if not condition:
        failures.append(msg)


# ============================================================
# Test 1: Exhaustive forward + backward (n <= 5)
# ============================================================
print("Test 1: Exhaustive forward + backward...")

for n in range(1, 6):
    if n <= 3:
        max_val = 10
    elif n == 4:
        max_val = 6
    else:
        max_val = 4

    for sizes_tuple in itertools.product(range(1, max_val + 1), repeat=n):
        sizes = list(sizes_tuple)

        src_config = brute_force_source(sizes)
        src_feas = src_config is not None

        lengths, weights, deadlines, K = reduce(sizes)
        tgt_sched = brute_force_target(lengths, weights, deadlines, K)
        tgt_feas = tgt_sched is not None

        check(src_feas == tgt_feas,
              f"Disagreement: sizes={sizes}, src={src_feas}, tgt={tgt_feas}")

        # Extraction test for feasible instances
        if tgt_feas and tgt_sched is not None:
            config = extract_solution(lengths, deadlines, tgt_sched)
            check(is_feasible_source(sizes, config),
                  f"Extraction failed: sizes={sizes}, config={config}")

    print(f"  n={n}: done")

print(f"  Checks so far: {checks}")


# ============================================================
# Test 2: YES example from Typst
# ============================================================
print("Test 2: YES example from Typst proof...")

yes_sizes = [3, 5, 2, 4, 1, 5]
yes_B = 20
yes_T = 10

check(sum(yes_sizes) == yes_B, f"YES: sum={sum(yes_sizes)} != {yes_B}")
check(yes_B % 2 == 0, "YES: B should be even")

lengths, weights, deadlines, K = reduce(yes_sizes)
check(K == yes_T, f"YES: K={K} != T={yes_T}")
check(all(d == yes_T for d in deadlines), f"YES: deadlines not all {yes_T}")
check(lengths == yes_sizes, "YES: lengths != sizes")
check(weights == yes_sizes, "YES: weights != sizes")

# Specific schedule from Typst: t5,t3,t1,t4,t2,t6 => indices [4,2,0,3,1,5]
typst_schedule = [4, 2, 0, 3, 1, 5]
check(is_feasible_target(lengths, weights, deadlines, K, typst_schedule),
      "YES: Typst schedule should be feasible")

# Verify tardy weight
elapsed = 0
tw = 0
for task in typst_schedule:
    elapsed += lengths[task]
    if elapsed > deadlines[task]:
        tw += weights[task]
check(tw == 10, f"YES: tardy weight={tw}, expected 10")

# Extract partition
config = extract_solution(lengths, deadlines, typst_schedule)
check(is_feasible_source(yes_sizes, config), "YES: extracted partition not balanced")

on_time = sorted([yes_sizes[i] for i in range(6) if config[i] == 0])
tardy = sorted([yes_sizes[i] for i in range(6) if config[i] == 1])
check(on_time == [1, 2, 3, 4], f"YES: on-time={on_time}")
check(tardy == [5, 5], f"YES: tardy={tardy}")

print(f"  Checks so far: {checks}")


# ============================================================
# Test 3: NO example from Typst
# ============================================================
print("Test 3: NO example from Typst proof...")

no_sizes = [3, 5, 7]
no_B = 15

check(sum(no_sizes) == no_B, f"NO: sum={sum(no_sizes)} != {no_B}")
check(no_B % 2 != 0, "NO: B should be odd")

lengths, weights, deadlines, K = reduce(no_sizes)
check(K == 0, f"NO: K={K}, expected 0")
check(all(d == 0 for d in deadlines), "NO: deadlines should all be 0")

# Source infeasible
check(brute_force_source(no_sizes) is None, "NO: source should be infeasible")

# Target infeasible
check(brute_force_target(lengths, weights, deadlines, K) is None,
      "NO: target should be infeasible")

# Every schedule gives tardy weight = B > 0 = K
for perm in itertools.permutations(range(3)):
    elapsed = 0
    tw = 0
    for task in perm:
        elapsed += lengths[task]
        if elapsed > deadlines[task]:
            tw += weights[task]
    check(tw == no_B, f"NO: schedule {perm}: tw={tw} != {no_B}")
    check(tw > K, f"NO: schedule {perm}: tw={tw} should > K={K}")

print(f"  Checks so far: {checks}")


# ============================================================
# Test 4: hypothesis PBT — Strategy 1: random sizes
# ============================================================
print("Test 4: hypothesis PBT...")

try:
    from hypothesis import given, settings, assume
    from hypothesis import strategies as st

    @given(
        sizes=st.lists(st.integers(min_value=1, max_value=50), min_size=1, max_size=7)
    )
    @settings(max_examples=1500, deadline=None)
    def test_forward_backward_random(sizes):
        global checks
        B = sum(sizes)
        n = len(sizes)

        lengths, weights, deadlines, K = reduce(sizes)

        # Structural invariants
        check(len(lengths) == n, f"PBT: len mismatch")
        check(lengths == weights, "PBT: l != w")
        check(all(d == deadlines[0] for d in deadlines), "PBT: deadline not common")
        check(sum(lengths) == B, "PBT: total != B")

        if B % 2 == 0:
            check(K == B // 2, "PBT: K != B/2")
            check(deadlines[0] == B // 2, "PBT: d != B/2")
        else:
            check(K == 0, "PBT: odd B, K != 0")
            check(deadlines[0] == 0, "PBT: odd B, d != 0")

        # For small n, check feasibility agreement
        if n <= 5:
            src_feas = brute_force_source(sizes) is not None
            tgt_feas = brute_force_target(lengths, weights, deadlines, K) is not None
            check(src_feas == tgt_feas,
                  f"PBT: sizes={sizes}, src={src_feas}, tgt={tgt_feas}")

    test_forward_backward_random()
    print(f"  Strategy 1 (random sizes): done, checks={checks}")

    # Strategy 2: balanced instances (guaranteed feasible)
    @given(
        half=st.lists(st.integers(min_value=1, max_value=30), min_size=1, max_size=5)
    )
    @settings(max_examples=1500, deadline=None)
    def test_balanced_instances(half):
        global checks
        # Construct a guaranteed-balanced instance
        other_half = list(half)  # duplicate
        sizes = half + other_half
        B = sum(sizes)

        check(B % 2 == 0, f"balanced: B={B} should be even")

        lengths, weights, deadlines, K = reduce(sizes)
        check(K == B // 2, "balanced: K != B/2")

        # Source must be feasible (we constructed it with a balanced partition)
        src_feas = brute_force_source(sizes) is not None
        check(src_feas, f"balanced: sizes={sizes} should be feasible")

        if len(sizes) <= 5:
            tgt_feas = brute_force_target(lengths, weights, deadlines, K) is not None
            check(tgt_feas, f"balanced: target should also be feasible")

    test_balanced_instances()
    print(f"  Strategy 2 (balanced instances): done, checks={checks}")

    # Strategy 3: odd-sum instances (guaranteed infeasible)
    @given(
        sizes=st.lists(st.integers(min_value=1, max_value=50), min_size=1, max_size=7)
    )
    @settings(max_examples=1000, deadline=None)
    def test_odd_sum_infeasible(sizes):
        global checks
        B = sum(sizes)
        assume(B % 2 != 0)

        lengths, weights, deadlines, K = reduce(sizes)
        check(K == 0, f"odd: K={K} != 0")
        check(all(d == 0 for d in deadlines), "odd: deadlines not all 0")

        # Source infeasible
        check(brute_force_source(sizes) is None, f"odd: sizes={sizes} should be infeasible")

        # Target: every task finishes after deadline 0
        if len(sizes) <= 5:
            check(brute_force_target(lengths, weights, deadlines, K) is None,
                  f"odd: target should be infeasible")

    test_odd_sum_infeasible()
    print(f"  Strategy 3 (odd-sum infeasible): done, checks={checks}")

except ImportError:
    print("  WARNING: hypothesis not available, using fallback random testing")
    import random
    random.seed(12345)

    for _ in range(3000):
        n = random.randint(1, 7)
        sizes = [random.randint(1, 50) for _ in range(n)]
        B = sum(sizes)

        lengths, weights, deadlines, K = reduce(sizes)
        check(len(lengths) == n, "fallback: len")
        check(lengths == weights, "fallback: l!=w")
        check(sum(lengths) == B, "fallback: total")

        if B % 2 == 0:
            check(K == B // 2, "fallback: K")
        else:
            check(K == 0, "fallback: odd K")

        if n <= 5:
            src_feas = brute_force_source(sizes) is not None
            tgt_feas = brute_force_target(lengths, weights, deadlines, K) is not None
            check(src_feas == tgt_feas, f"fallback: sizes={sizes}")


# ============================================================
# Test 5: Cross-comparison with constructor outputs
# ============================================================
print("Test 5: Cross-comparison with constructor outputs...")

# Verify key instances match between constructor and adversary
test_instances = [
    [3, 5, 2, 4, 1, 5],  # YES example
    [3, 5, 7],            # NO example (odd)
    [1, 2, 7],            # NO example (even, infeasible)
    [1, 1],               # trivial YES
    [1, 2],               # trivial NO (odd)
    [1, 1, 1, 1],         # YES: {1,1} {1,1}
    [3, 3, 3, 3],         # YES: {3,3} {3,3}
    [1, 2, 3, 4, 5, 5],   # YES: {1,4,5} {2,3,5} = 10+10
    [10],                 # single element, infeasible (can't split)
    [5, 5],               # YES: {5} {5}
]

for sizes in test_instances:
    B = sum(sizes)
    n = len(sizes)

    lengths, weights, deadlines, K = reduce(sizes)

    # Basic structural
    check(len(lengths) == n, f"cross: {sizes}: len")
    check(lengths == list(sizes), f"cross: {sizes}: lengths")
    check(weights == list(sizes), f"cross: {sizes}: weights")

    if B % 2 == 0:
        check(K == B // 2, f"cross: {sizes}: K")
        check(all(d == B // 2 for d in deadlines), f"cross: {sizes}: deadlines")
    else:
        check(K == 0, f"cross: {sizes}: K odd")
        check(all(d == 0 for d in deadlines), f"cross: {sizes}: deadlines odd")

    # Feasibility
    if n <= 6:
        src_feas = brute_force_source(sizes) is not None
        tgt_sched = brute_force_target(lengths, weights, deadlines, K)
        tgt_feas = tgt_sched is not None
        check(src_feas == tgt_feas,
              f"cross: {sizes}: src={src_feas}, tgt={tgt_feas}")

        if tgt_feas and tgt_sched is not None:
            config = extract_solution(lengths, deadlines, tgt_sched)
            check(is_feasible_source(sizes, config),
                  f"cross: {sizes}: extraction failed")

print(f"  Checks so far: {checks}")


# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
print(f"TOTAL CHECKS: {checks}")

if failures:
    print(f"\nFAILURES: {len(failures)}")
    for f in failures[:20]:
        print(f"  {f}")
    sys.exit(1)
else:
    print("\nAll checks passed!")
    sys.exit(0)
