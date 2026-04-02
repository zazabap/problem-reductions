#!/usr/bin/env python3
"""
Adversary verification script: SubsetSum → Partition reduction.
Issue: #973

Independent re-implementation of the reduction and extraction logic,
plus property-based testing with hypothesis. ≥5000 independent checks.

This script does NOT import from verify_subset_sum_partition.py —
it re-derives everything from scratch as an independent cross-check.
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

def adv_reduce(sizes: list[int], target: int) -> list[int]:
    """Independent reduction: SubsetSum → Partition."""
    total = sum(sizes)
    gap = abs(total - 2 * target)
    if gap == 0:
        return sizes[:]
    return sizes[:] + [gap]


def adv_extract(sizes: list[int], target: int, part_cfg: list[int]) -> list[int]:
    """Independent extraction: Partition solution → SubsetSum solution."""
    n = len(sizes)
    total = sum(sizes)

    if total == 2 * target:
        return part_cfg[:n]

    pad_side = part_cfg[n]

    if total > 2 * target:
        # T-sum elements are on SAME side as padding
        return [1 if part_cfg[i] == pad_side else 0 for i in range(n)]
    else:
        # T-sum elements are on OPPOSITE side from padding
        return [1 if part_cfg[i] != pad_side else 0 for i in range(n)]


def adv_eval_subset_sum(sizes: list[int], target: int, config: list[int]) -> bool:
    """Evaluate whether config is a valid SubsetSum solution."""
    return sum(sizes[i] for i in range(len(sizes)) if config[i] == 1) == target


def adv_eval_partition(sizes: list[int], config: list[int]) -> bool:
    """Evaluate whether config is a valid Partition solution."""
    total = sum(sizes)
    if total % 2 != 0:
        return False
    side1 = sum(sizes[i] for i in range(len(sizes)) if config[i] == 1)
    return side1 * 2 == total


def adv_solve_subset_sum(sizes: list[int], target: int) -> Optional[list[int]]:
    """Brute-force SubsetSum solver."""
    for cfg in product(range(2), repeat=len(sizes)):
        if sum(sizes[i] for i in range(len(sizes)) if cfg[i] == 1) == target:
            return list(cfg)
    return None


def adv_solve_partition(sizes: list[int]) -> Optional[list[int]]:
    """Brute-force Partition solver."""
    total = sum(sizes)
    if total % 2 != 0:
        return None
    half = total // 2
    for cfg in product(range(2), repeat=len(sizes)):
        if sum(sizes[i] for i in range(len(sizes)) if cfg[i] == 1) == half:
            return list(cfg)
    return None


# ─────────────────────────────────────────────────────────────────────
# Property checks
# ─────────────────────────────────────────────────────────────────────

def adv_check_all(sizes: list[int], target: int) -> int:
    """Run all adversary checks on a single instance. Returns check count."""
    checks = 0

    # 1. Overhead
    reduced = adv_reduce(sizes, target)
    assert len(reduced) <= len(sizes) + 1, \
        f"Overhead violation: {len(reduced)} > {len(sizes) + 1}"
    checks += 1

    # 2. Forward: feasible source → feasible target
    src_sol = adv_solve_subset_sum(sizes, target)
    tgt_sol = adv_solve_partition(reduced)
    if src_sol is not None:
        assert tgt_sol is not None, \
            f"Forward violation: sizes={sizes}, target={target}"
        checks += 1

    # 3. Backward: feasible target → valid extraction
    if tgt_sol is not None:
        extracted = adv_extract(sizes, target, tgt_sol)
        assert adv_eval_subset_sum(sizes, target, extracted), \
            f"Backward violation: sizes={sizes}, target={target}, extracted={extracted}"
        checks += 1

    # 4. Infeasible: NO source → NO target
    if src_sol is None:
        assert tgt_sol is None, \
            f"Infeasible violation: sizes={sizes}, target={target}"
        checks += 1

    # 5. Cross-check: source and target feasibility must agree
    src_feas = src_sol is not None
    tgt_feas = tgt_sol is not None
    assert src_feas == tgt_feas, \
        f"Feasibility mismatch: src={src_feas}, tgt={tgt_feas}, sizes={sizes}, target={target}"
    checks += 1

    return checks


# ─────────────────────────────────────────────────────────────────────
# Test drivers
# ─────────────────────────────────────────────────────────────────────

def adversary_exhaustive(max_n: int = 5, max_val: int = 8) -> int:
    """Exhaustive adversary tests."""
    checks = 0
    for n in range(1, max_n + 1):
        if n <= 3:
            vr = range(1, max_val + 1)
        elif n == 4:
            vr = range(1, min(max_val, 6) + 1)
        else:
            vr = range(1, min(max_val, 4) + 1)

        for sizes_tuple in product(vr, repeat=n):
            sizes = list(sizes_tuple)
            sigma = sum(sizes)
            for target in range(0, sigma + 2):
                checks += adv_check_all(sizes, target)
    return checks


def adversary_random(count: int = 1500, max_n: int = 12, max_val: int = 80) -> int:
    """Random adversary tests with independent RNG seed."""
    import random
    rng = random.Random(9999)  # Different seed from verify script
    checks = 0
    for _ in range(count):
        n = rng.randint(1, max_n)
        sizes = [rng.randint(1, max_val) for _ in range(n)]
        sigma = sum(sizes)
        target = rng.randint(0, sigma + 20)
        checks += adv_check_all(sizes, target)
    return checks


def adversary_hypothesis() -> int:
    """Property-based testing with hypothesis."""
    if not HAS_HYPOTHESIS:
        return 0

    checks_counter = [0]

    @given(
        sizes=st.lists(st.integers(min_value=1, max_value=50), min_size=1, max_size=10),
        target=st.integers(min_value=0, max_value=500),
    )
    @settings(
        max_examples=1000,
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
        ([1, 2], 3), ([1, 2], 0),
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
    print("Adversary verification: SubsetSum → Partition")
    print("=" * 60)

    print("\n[1/4] Edge cases...")
    n_edge = adversary_edge_cases()
    print(f"  Edge case checks: {n_edge}")

    print("\n[2/4] Exhaustive adversary (n ≤ 5)...")
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
