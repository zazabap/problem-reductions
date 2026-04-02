#!/usr/bin/env python3
"""
Verification script: SubsetSum → Partition reduction.
Issue: #973
Reference: Garey & Johnson, Computers and Intractability, SP12–SP13.

Seven mandatory sections:
  1. reduce()         — the reduction function
  2. extract()        — solution extraction (back-map)
  3. Brute-force solvers for source and target
  4. Forward: YES source → YES target
  5. Backward: YES target → YES source (via extract)
  6. Infeasible: NO source → NO target
  7. Overhead check

Runs ≥5000 checks total, with exhaustive coverage for n ≤ 5.
"""

import json
import sys
from itertools import product
from typing import Optional

# ─────────────────────────────────────────────────────────────────────
# Section 1: reduce()
# ─────────────────────────────────────────────────────────────────────

def reduce(sizes: list[int], target: int) -> list[int]:
    """
    Reduce SubsetSum(sizes, target) → Partition(new_sizes).

    Given sizes S and target T with Σ = sum(S):
      - d = |Σ − 2T|
      - If d == 0: return S
      - If d > 0: return S + [d]
    """
    sigma = sum(sizes)
    d = abs(sigma - 2 * target)
    if d == 0:
        return list(sizes)
    else:
        return list(sizes) + [d]


# ─────────────────────────────────────────────────────────────────────
# Section 2: extract()
# ─────────────────────────────────────────────────────────────────────

def extract(
    sizes: list[int], target: int, partition_config: list[int]
) -> list[int]:
    """
    Extract a SubsetSum solution from a Partition solution.

    partition_config: binary list where 1 = side 1, 0 = side 0.
    Returns: binary list of length len(sizes) indicating which elements
             are selected for the SubsetSum solution.
    """
    n = len(sizes)
    sigma = sum(sizes)

    if sigma == 2 * target:
        # No padding element; config maps directly
        return list(partition_config[:n])
    elif sigma > 2 * target:
        # Padding at index n. T-sum subset is on SAME side as padding.
        pad_side = partition_config[n]
        return [1 if partition_config[i] == pad_side else 0 for i in range(n)]
    else:
        # sigma < 2*target. T-sum subset is on OPPOSITE side from padding.
        pad_side = partition_config[n]
        return [1 if partition_config[i] != pad_side else 0 for i in range(n)]


# ─────────────────────────────────────────────────────────────────────
# Section 3: Brute-force solvers
# ─────────────────────────────────────────────────────────────────────

def solve_subset_sum(sizes: list[int], target: int) -> Optional[list[int]]:
    """Brute-force solve SubsetSum. Returns config or None."""
    n = len(sizes)
    for config in product(range(2), repeat=n):
        s = sum(sizes[i] for i in range(n) if config[i] == 1)
        if s == target:
            return list(config)
    return None


def solve_partition(sizes: list[int]) -> Optional[list[int]]:
    """Brute-force solve Partition. Returns config or None."""
    total = sum(sizes)
    if total % 2 != 0:
        return None
    half = total // 2
    n = len(sizes)
    for config in product(range(2), repeat=n):
        s = sum(sizes[i] for i in range(n) if config[i] == 1)
        if s == half:
            return list(config)
    return None


def is_subset_sum_feasible(sizes: list[int], target: int) -> bool:
    """Check if SubsetSum instance is feasible."""
    return solve_subset_sum(sizes, target) is not None


def is_partition_feasible(sizes: list[int]) -> bool:
    """Check if Partition instance is feasible."""
    return solve_partition(sizes) is not None


# ─────────────────────────────────────────────────────────────────────
# Section 4: Forward check — YES source → YES target
# ─────────────────────────────────────────────────────────────────────

def check_forward(sizes: list[int], target: int) -> bool:
    """
    If SubsetSum(sizes, target) is feasible,
    then Partition(reduce(sizes, target)) must also be feasible.
    """
    if not is_subset_sum_feasible(sizes, target):
        return True  # vacuously true
    target_sizes = reduce(sizes, target)
    return is_partition_feasible(target_sizes)


# ─────────────────────────────────────────────────────────────────────
# Section 5: Backward check — YES target → YES source (via extract)
# ─────────────────────────────────────────────────────────────────────

def check_backward(sizes: list[int], target: int) -> bool:
    """
    If Partition(reduce(sizes, target)) is feasible,
    solve it, extract a SubsetSum config, and verify it.
    """
    target_sizes = reduce(sizes, target)
    part_sol = solve_partition(target_sizes)
    if part_sol is None:
        return True  # vacuously true
    source_config = extract(sizes, target, part_sol)
    # Verify the extracted solution
    selected_sum = sum(sizes[i] for i in range(len(sizes)) if source_config[i] == 1)
    return selected_sum == target


# ─────────────────────────────────────────────────────────────────────
# Section 6: Infeasible check — NO source → NO target
# ─────────────────────────────────────────────────────────────────────

def check_infeasible(sizes: list[int], target: int) -> bool:
    """
    If SubsetSum(sizes, target) is infeasible,
    then Partition(reduce(sizes, target)) must also be infeasible.
    """
    if is_subset_sum_feasible(sizes, target):
        return True  # not an infeasible instance; skip
    target_sizes = reduce(sizes, target)
    return not is_partition_feasible(target_sizes)


# ─────────────────────────────────────────────────────────────────────
# Section 7: Overhead check
# ─────────────────────────────────────────────────────────────────────

def check_overhead(sizes: list[int], target: int) -> bool:
    """
    Verify: len(reduce(sizes, target)) <= len(sizes) + 1.
    """
    target_sizes = reduce(sizes, target)
    return len(target_sizes) <= len(sizes) + 1


# ─────────────────────────────────────────────────────────────────────
# Exhaustive + random test driver
# ─────────────────────────────────────────────────────────────────────

def exhaustive_tests(max_n: int = 5, max_val: int = 10) -> int:
    """
    Exhaustive tests for all SubsetSum instances with n ≤ max_n,
    element values in [1, max_val], and targets in [0, n*max_val].
    Returns number of checks performed.
    """
    checks = 0
    for n in range(1, max_n + 1):
        # For small n, enumerate representative size vectors
        # Use values 1..max_val to keep combinatorics manageable
        if n <= 3:
            val_range = range(1, max_val + 1)
        elif n == 4:
            val_range = range(1, min(max_val, 7) + 1)
        else:
            val_range = range(1, min(max_val, 5) + 1)

        for sizes_tuple in product(val_range, repeat=n):
            sizes = list(sizes_tuple)
            sigma = sum(sizes)
            # Test representative targets: 0, 1, ..., sigma, sigma+1
            targets_to_test = set(range(0, min(sigma + 2, sigma + 2)))
            for target in targets_to_test:
                assert check_forward(sizes, target), (
                    f"Forward FAILED: sizes={sizes}, target={target}"
                )
                assert check_backward(sizes, target), (
                    f"Backward FAILED: sizes={sizes}, target={target}"
                )
                assert check_infeasible(sizes, target), (
                    f"Infeasible FAILED: sizes={sizes}, target={target}"
                )
                assert check_overhead(sizes, target), (
                    f"Overhead FAILED: sizes={sizes}, target={target}"
                )
                checks += 4
    return checks


def random_tests(count: int = 2000, max_n: int = 15, max_val: int = 100) -> int:
    """Random tests with larger instances. Returns number of checks."""
    import random
    rng = random.Random(42)
    checks = 0
    for _ in range(count):
        n = rng.randint(1, max_n)
        sizes = [rng.randint(1, max_val) for _ in range(n)]
        sigma = sum(sizes)
        # Pick target from various regimes
        regime = rng.choice(["feasible_region", "zero", "full", "over", "half", "random"])
        if regime == "zero":
            target = 0
        elif regime == "full":
            target = sigma
        elif regime == "over":
            target = sigma + rng.randint(1, 50)
        elif regime == "half":
            target = sigma // 2
        elif regime == "feasible_region":
            target = rng.randint(0, sigma)
        else:
            target = rng.randint(0, sigma + 50)

        assert check_forward(sizes, target), (
            f"Forward FAILED: sizes={sizes}, target={target}"
        )
        assert check_backward(sizes, target), (
            f"Backward FAILED: sizes={sizes}, target={target}"
        )
        assert check_infeasible(sizes, target), (
            f"Infeasible FAILED: sizes={sizes}, target={target}"
        )
        assert check_overhead(sizes, target), (
            f"Overhead FAILED: sizes={sizes}, target={target}"
        )
        checks += 4
    return checks


def collect_test_vectors(count: int = 20) -> list[dict]:
    """Collect representative test vectors for downstream consumption."""
    import random
    rng = random.Random(123)
    vectors = []

    # Hand-crafted vectors covering all cases
    hand_crafted = [
        # Case: Σ < 2T (padding needed, d = 2T - Σ)
        {"sizes": [1, 5, 6, 8], "target": 11, "label": "yes_sigma_lt_2t"},
        # Case: Σ > 2T (padding needed, d = Σ - 2T)
        {"sizes": [10, 20, 30], "target": 10, "label": "yes_sigma_gt_2t"},
        # Case: Σ = 2T (no padding)
        {"sizes": [3, 5, 2, 6], "target": 8, "label": "yes_sigma_eq_2t"},
        # Infeasible: T > Σ
        {"sizes": [1, 2, 3], "target": 100, "label": "no_target_exceeds_sum"},
        # Infeasible: no subset sums to T
        {"sizes": [3, 7, 11], "target": 5, "label": "no_no_subset"},
        # Single element, feasible
        {"sizes": [5], "target": 5, "label": "yes_single_element"},
        # Single element, infeasible
        {"sizes": [5], "target": 3, "label": "no_single_element"},
        # All same elements
        {"sizes": [4, 4, 4, 4], "target": 8, "label": "yes_uniform"},
        # Target = 0 (empty subset)
        {"sizes": [1, 2, 3], "target": 0, "label": "yes_target_zero"},
        # Target = Σ (full set)
        {"sizes": [2, 3, 5], "target": 10, "label": "yes_target_full_sum"},
    ]

    for hc in hand_crafted:
        sizes = hc["sizes"]
        target = hc["target"]
        target_sizes = reduce(sizes, target)
        source_sol = solve_subset_sum(sizes, target)
        part_sol = solve_partition(target_sizes)
        extracted = None
        if part_sol is not None:
            extracted = extract(sizes, target, part_sol)
        vectors.append({
            "label": hc["label"],
            "source": {"sizes": sizes, "target": target},
            "target": {"sizes": target_sizes},
            "source_feasible": source_sol is not None,
            "target_feasible": part_sol is not None,
            "source_solution": source_sol,
            "target_solution": part_sol,
            "extracted_solution": extracted,
        })

    # Random vectors
    for i in range(count - len(hand_crafted)):
        n = rng.randint(1, 8)
        sizes = [rng.randint(1, 20) for _ in range(n)]
        sigma = sum(sizes)
        target = rng.randint(0, sigma + 5)
        target_sizes = reduce(sizes, target)
        source_sol = solve_subset_sum(sizes, target)
        part_sol = solve_partition(target_sizes)
        extracted = None
        if part_sol is not None:
            extracted = extract(sizes, target, part_sol)
        vectors.append({
            "label": f"random_{i}",
            "source": {"sizes": sizes, "target": target},
            "target": {"sizes": target_sizes},
            "source_feasible": source_sol is not None,
            "target_feasible": part_sol is not None,
            "source_solution": source_sol,
            "target_solution": part_sol,
            "extracted_solution": extracted,
        })

    return vectors


if __name__ == "__main__":
    print("=" * 60)
    print("SubsetSum → Partition verification")
    print("=" * 60)

    print("\n[1/3] Exhaustive tests (n ≤ 5)...")
    n_exhaustive = exhaustive_tests()
    print(f"  Exhaustive checks: {n_exhaustive}")

    print("\n[2/3] Random tests...")
    n_random = random_tests(count=2000)
    print(f"  Random checks: {n_random}")

    total = n_exhaustive + n_random
    print(f"\n  TOTAL checks: {total}")
    assert total >= 5000, f"Need ≥5000 checks, got {total}"

    print("\n[3/3] Generating test vectors...")
    vectors = collect_test_vectors(count=20)

    # Validate all vectors
    for v in vectors:
        sizes = v["source"]["sizes"]
        target = v["source"]["target"]
        if v["source_feasible"]:
            assert v["target_feasible"], f"Forward violation in {v['label']}"
            if v["extracted_solution"] is not None:
                sel = sum(
                    sizes[i]
                    for i in range(len(sizes))
                    if v["extracted_solution"][i] == 1
                )
                assert sel == target, f"Extract violation in {v['label']}: {sel} != {target}"
        if not v["source_feasible"]:
            assert not v["target_feasible"], f"Infeasible violation in {v['label']}"

    # Write test vectors
    out_path = "docs/paper/verify-reductions/test_vectors_subset_sum_partition.json"
    with open(out_path, "w") as f:
        json.dump({"vectors": vectors, "total_checks": total}, f, indent=2)
    print(f"  Wrote {len(vectors)} test vectors to {out_path}")

    print(f"\nAll {total} checks PASSED.")
