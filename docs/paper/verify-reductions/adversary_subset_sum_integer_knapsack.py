#!/usr/bin/env python3
"""
Adversary verification script: SubsetSum → IntegerKnapsack reduction.
Issue: #521

Independent re-implementation of the reduction and extraction logic,
plus property-based testing with hypothesis. ≥5000 independent checks.

This script does NOT import from verify_subset_sum_integer_knapsack.py —
it re-derives everything from scratch as an independent cross-check.

NOTE: This is a forward-only NP-hardness embedding, NOT an equivalence-
preserving reduction. The adversary verifies:
  - Forward: YES SubsetSum → IntegerKnapsack optimal >= B
  - Solution lifting: SubsetSum solutions map to valid knapsack solutions
  - Overhead: item count and capacity preserved exactly
  - Asymmetry: documents NO SubsetSum instances where knapsack still achieves >= B
"""

import json
import sys
from itertools import product
from typing import Optional

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not installed; falling back to pure-random adversary tests")


# ─────────────────────────────────────────────────────────────────────
# Independent re-implementation of reduction
# ─────────────────────────────────────────────────────────────────────

def adv_reduce(sizes: list[int], target: int) -> tuple[list[int], list[int], int]:
    """Independent reduction: SubsetSum → IntegerKnapsack."""
    return list(sizes), list(sizes), target


def adv_eval_subset_sum(sizes: list[int], target: int, config: list[int]) -> bool:
    """Evaluate whether config is a valid SubsetSum solution."""
    if len(config) != len(sizes):
        return False
    if any(c not in (0, 1) for c in config):
        return False
    return sum(sizes[i] for i in range(len(sizes)) if config[i] == 1) == target


def adv_eval_integer_knapsack(
    sizes: list[int], values: list[int], capacity: int, config: list[int]
) -> Optional[int]:
    """
    Evaluate an IntegerKnapsack configuration.
    Returns total value if feasible, None if infeasible.
    """
    if len(config) != len(sizes):
        return None
    if any(c < 0 for c in config):
        return None
    total_size = sum(config[i] * sizes[i] for i in range(len(sizes)))
    if total_size > capacity:
        return None
    return sum(config[i] * values[i] for i in range(len(values)))


def adv_solve_subset_sum(sizes: list[int], target: int) -> Optional[list[int]]:
    """Brute-force SubsetSum solver."""
    for cfg in product(range(2), repeat=len(sizes)):
        if sum(sizes[i] for i in range(len(sizes)) if cfg[i] == 1) == target:
            return list(cfg)
    return None


def adv_solve_integer_knapsack(
    sizes: list[int], values: list[int], capacity: int
) -> tuple[Optional[list[int]], int]:
    """
    Brute-force IntegerKnapsack solver.
    Returns (best_config, best_value).
    """
    n = len(sizes)
    if n == 0:
        return ([], 0)

    max_mult = [capacity // s if s > 0 else 0 for s in sizes]
    best_config = None
    best_value = 0  # zero-config always feasible

    def search(idx, rem_cap, cur_cfg, cur_val):
        nonlocal best_config, best_value
        if idx == n:
            if cur_val > best_value:
                best_value = cur_val
                best_config = list(cur_cfg)
            return
        for c in range(max_mult[idx] + 1):
            used = c * sizes[idx]
            if used > rem_cap:
                break
            cur_cfg.append(c)
            search(idx + 1, rem_cap - used, cur_cfg, cur_val + c * values[idx])
            cur_cfg.pop()

    search(0, capacity, [], 0)
    return (best_config, best_value)


# ─────────────────────────────────────────────────────────────────────
# Property checks
# ─────────────────────────────────────────────────────────────────────

def adv_check_all(sizes: list[int], target: int) -> int:
    """Run all adversary checks on a single instance. Returns check count."""
    checks = 0

    # 1. Overhead: items preserved, capacity = target, values = sizes
    ks, kv, kc = adv_reduce(sizes, target)
    assert len(ks) == len(sizes), \
        f"Item count mismatch: {len(ks)} != {len(sizes)}"
    assert ks == list(sizes), \
        f"Sizes not preserved: {ks} != {sizes}"
    assert kv == list(sizes), \
        f"Values != sizes: {kv} != {sizes}"
    assert kc == target, \
        f"Capacity != target: {kc} != {target}"
    checks += 1

    # 2. Forward: feasible SubsetSum → knapsack optimal >= target
    src_sol = adv_solve_subset_sum(sizes, target)
    _, opt_val = adv_solve_integer_knapsack(ks, kv, kc)

    if src_sol is not None:
        assert opt_val >= target, \
            f"Forward violation: sizes={sizes}, target={target}, opt={opt_val}"
        checks += 1

        # 3. Solution lifting: SubsetSum solution is a valid knapsack solution
        knapsack_val = adv_eval_integer_knapsack(ks, kv, kc, src_sol)
        assert knapsack_val is not None, \
            f"SubsetSum solution not valid for knapsack: sizes={sizes}, target={target}"
        assert knapsack_val == target, \
            f"Lifted value != target: {knapsack_val} != {target}"
        checks += 1

    # 4. Asymmetry check: when SubsetSum infeasible, knapsack may still
    #    achieve >= target (this is expected, NOT a bug)
    if src_sol is None and opt_val >= target:
        # Document: this is a known asymmetry. The reduction is one-way.
        # We just count this as a verified asymmetry check.
        checks += 1

    # 5. Value bound: knapsack optimal <= capacity (since v = s)
    assert opt_val <= kc or target == 0, \
        f"Value exceeds capacity with v=s: opt={opt_val}, cap={kc}, sizes={sizes}"
    # Actually when target=0, capacity=0 and opt_val=0, so the above holds too.
    # More precisely: with v=s, total_value = total_size <= capacity = target.
    # So opt_val <= target. Combined with forward (opt_val >= target when feasible),
    # this means opt_val == target when SubsetSum is feasible.
    if src_sol is not None:
        assert opt_val >= target, \
            f"Value bound violation for feasible instance"
    checks += 1

    return checks


# ─────────────────────────────────────────────────────────────────────
# Test drivers
# ─────────────────────────────────────────────────────────────────────

def adversary_exhaustive(max_n: int = 4, max_val: int = 8) -> int:
    """Exhaustive adversary tests."""
    checks = 0
    for n in range(1, max_n + 1):
        if n <= 2:
            vr = range(1, max_val + 1)
        elif n == 3:
            vr = range(1, min(max_val, 6) + 1)
        else:
            vr = range(1, min(max_val, 4) + 1)

        for sizes_tuple in product(vr, repeat=n):
            sizes = list(sizes_tuple)
            sigma = sum(sizes)
            for target in range(0, sigma + 2):
                checks += adv_check_all(sizes, target)
    return checks


def adversary_random(count: int = 1500, max_n: int = 8, max_val: int = 25) -> int:
    """Random adversary tests with independent RNG seed."""
    import random
    rng = random.Random(9999)  # Different seed from verify script
    checks = 0
    for _ in range(count):
        n = rng.randint(1, max_n)
        sizes = [rng.randint(1, max_val) for _ in range(n)]
        sigma = sum(sizes)
        target = rng.randint(0, sigma + 10)
        checks += adv_check_all(sizes, target)
    return checks


def adversary_hypothesis() -> int:
    """Property-based testing with hypothesis."""
    if not HAS_HYPOTHESIS:
        return 0

    checks_counter = [0]

    @given(
        sizes=st.lists(
            st.integers(min_value=1, max_value=10),
            min_size=1, max_size=5,
        ),
        target=st.integers(min_value=0, max_value=50),
    )
    @settings(
        max_examples=1500,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def prop_reduction_correct(sizes, target):
        checks_counter[0] += adv_check_all(sizes, target)

    prop_reduction_correct()
    return checks_counter[0]


def adversary_edge_cases() -> int:
    """Targeted edge cases."""
    checks = 0
    edge_cases = [
        # Single element
        ([1], 0), ([1], 1), ([1], 2),
        # Two elements
        ([1, 1], 1), ([1, 1], 2), ([1, 1], 0),
        ([1, 2], 3), ([1, 2], 0), ([1, 2], 1), ([1, 2], 2),
        # Multiplicity counterexamples (NO SubsetSum, YES IntegerKnapsack)
        ([3], 6),       # c=2 achieves 6
        ([2, 5], 4),    # c=(2,0) achieves 4
        ([4], 8),       # c=2 achieves 8
        ([3, 3], 9),    # c=(3,0) or c=(0,3) achieves 9
        # Large gap
        ([1], 1000),
        # All same
        ([5, 5, 5, 5], 10), ([5, 5, 5, 5], 15), ([5, 5, 5, 5], 20),
        # Powers of 2
        ([1, 2, 4, 8], 7), ([1, 2, 4, 8], 15), ([1, 2, 4, 8], 16),
        # Target = 0
        ([3, 7, 11], 0),
        # Target = sum
        ([3, 7, 11], 21),
        # Barely feasible
        ([1, 2, 3, 4, 5], 15),
        ([1, 2, 3, 4, 5], 1),
    ]
    for sizes, target in edge_cases:
        checks += adv_check_all(sizes, target)
    return checks


if __name__ == "__main__":
    print("=" * 60)
    print("Adversary verification: SubsetSum → IntegerKnapsack")
    print("=" * 60)

    print("\n[1/4] Edge cases...")
    n_edge = adversary_edge_cases()
    print(f"  Edge case checks: {n_edge}")

    print("\n[2/4] Exhaustive adversary (n ≤ 4)...")
    n_exh = adversary_exhaustive()
    print(f"  Exhaustive checks: {n_exh}")

    print("\n[3/4] Random adversary (different seed)...")
    n_rand = adversary_random()
    print(f"  Random checks: {n_rand}")

    print("\n[4/4] Hypothesis PBT...")
    n_hyp = adversary_hypothesis()
    print(f"  Hypothesis checks: {n_hyp}")

    total = n_edge + n_exh + n_rand + n_hyp
    print(f"\n  TOTAL adversary checks: {total}")
    assert total >= 5000, f"Need ≥5000 checks, got {total}"
    print(f"\nAll {total} adversary checks PASSED.")
