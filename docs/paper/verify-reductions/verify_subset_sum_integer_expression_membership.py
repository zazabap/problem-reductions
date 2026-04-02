#!/usr/bin/env python3
"""
Verification script: SubsetSum → IntegerExpressionMembership reduction.
Issue: #569
Reference: Stockmeyer and Meyer (1973); Garey & Johnson, Appendix A7.3, p.253.

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

# Expression tree nodes (mirroring the Rust IntExpr enum)
# Represented as nested tuples:
#   ("atom", value)
#   ("union", left, right)
#   ("sum", left, right)

def reduce(sizes: list[int], target: int) -> tuple:
    """
    Reduce SubsetSum(sizes, target) → IntegerExpressionMembership(expr, K).

    For each element s_i, create choice expression c_i = Union(Atom(1), Atom(s_i + 1)).
    Chain all choices with Minkowski sum. Target K = target + n.

    Returns (expression_tree, K).
    """
    n = len(sizes)
    assert n >= 1, "Need at least one element"
    assert all(s > 0 for s in sizes), "All sizes must be positive"

    # Build choice expressions
    choices = []
    for s in sizes:
        c = ("union", ("atom", 1), ("atom", s + 1))
        choices.append(c)

    # Chain with sum nodes (left-associative)
    expr = choices[0]
    for i in range(1, n):
        expr = ("sum", expr, choices[i])

    K = target + n
    return expr, K


# ─────────────────────────────────────────────────────────────────────
# Section 2: extract()
# ─────────────────────────────────────────────────────────────────────

def extract(sizes: list[int], target: int, iem_config: list[int]) -> list[int]:
    """
    Extract a SubsetSum solution from an IntegerExpressionMembership solution.

    iem_config: binary list of length n (one per union node, DFS order).
      0 = left branch (Atom(1), skip), 1 = right branch (Atom(s_i+1), select).

    Returns: binary list of length n for SubsetSum.
    """
    # The IEM config directly encodes the SubsetSum selection:
    # config[i] = 1 means we chose right branch = Atom(s_i + 1) = "select element i"
    # config[i] = 0 means we chose left branch = Atom(1) = "skip element i"
    return list(iem_config)


# ─────────────────────────────────────────────────────────────────────
# Section 3: Brute-force solvers
# ─────────────────────────────────────────────────────────────────────

def eval_expr(expr: tuple, config: list[int], counter: list[int]) -> Optional[int]:
    """
    Evaluate an IntExpr tree given union choices from config.
    counter[0] tracks which union node we're at (DFS order).
    Returns the integer value or None if config is invalid.
    """
    tag = expr[0]
    if tag == "atom":
        return expr[1]
    elif tag == "union":
        idx = counter[0]
        counter[0] += 1
        if idx >= len(config):
            return None
        if config[idx] == 0:
            return eval_expr(expr[1], config, counter)
        elif config[idx] == 1:
            return eval_expr(expr[2], config, counter)
        else:
            return None
    elif tag == "sum":
        left_val = eval_expr(expr[1], config, counter)
        if left_val is None:
            return None
        right_val = eval_expr(expr[2], config, counter)
        if right_val is None:
            return None
        return left_val + right_val
    return None


def count_union_nodes(expr: tuple) -> int:
    """Count the number of union nodes in the expression tree."""
    tag = expr[0]
    if tag == "atom":
        return 0
    elif tag == "union":
        return 1 + count_union_nodes(expr[1]) + count_union_nodes(expr[2])
    elif tag == "sum":
        return count_union_nodes(expr[1]) + count_union_nodes(expr[2])
    return 0


def count_atoms(expr: tuple) -> int:
    """Count the number of atom nodes."""
    tag = expr[0]
    if tag == "atom":
        return 1
    return count_atoms(expr[1]) + count_atoms(expr[2])


def tree_size(expr: tuple) -> int:
    """Count total number of nodes."""
    tag = expr[0]
    if tag == "atom":
        return 1
    return 1 + tree_size(expr[1]) + tree_size(expr[2])


def eval_set(expr: tuple) -> set[int]:
    """Evaluate the full set represented by the expression (brute-force)."""
    tag = expr[0]
    if tag == "atom":
        return {expr[1]}
    elif tag == "union":
        return eval_set(expr[1]) | eval_set(expr[2])
    elif tag == "sum":
        left = eval_set(expr[1])
        right = eval_set(expr[2])
        return {a + b for a in left for b in right}
    return set()


def solve_subset_sum(sizes: list[int], target: int) -> Optional[list[int]]:
    """Brute-force solve SubsetSum. Returns config or None."""
    n = len(sizes)
    for config in product(range(2), repeat=n):
        s = sum(sizes[i] for i in range(n) if config[i] == 1)
        if s == target:
            return list(config)
    return None


def solve_iem(expr: tuple, K: int) -> Optional[list[int]]:
    """Brute-force solve IntegerExpressionMembership. Returns config or None."""
    n_unions = count_union_nodes(expr)
    for config in product(range(2), repeat=n_unions):
        config_list = list(config)
        val = eval_expr(expr, config_list, [0])
        if val == K:
            return config_list
    return None


def is_subset_sum_feasible(sizes: list[int], target: int) -> bool:
    return solve_subset_sum(sizes, target) is not None


def is_iem_feasible(expr: tuple, K: int) -> bool:
    return solve_iem(expr, K) is not None


# ─────────────────────────────────────────────────────────────────────
# Section 4: Forward check — YES source → YES target
# ─────────────────────────────────────────────────────────────────────

def check_forward(sizes: list[int], target: int) -> bool:
    """
    If SubsetSum(sizes, target) is feasible,
    then IEM(reduce(sizes, target)) must also be feasible.
    """
    if not is_subset_sum_feasible(sizes, target):
        return True  # vacuously true
    expr, K = reduce(sizes, target)
    return is_iem_feasible(expr, K)


# ─────────────────────────────────────────────────────────────────────
# Section 5: Backward check — YES target → YES source (via extract)
# ─────────────────────────────────────────────────────────────────────

def check_backward(sizes: list[int], target: int) -> bool:
    """
    If IEM(reduce(sizes, target)) is feasible,
    solve it, extract a SubsetSum config, and verify it.
    """
    expr, K = reduce(sizes, target)
    iem_sol = solve_iem(expr, K)
    if iem_sol is None:
        return True  # vacuously true
    source_config = extract(sizes, target, iem_sol)
    selected_sum = sum(sizes[i] for i in range(len(sizes)) if source_config[i] == 1)
    return selected_sum == target


# ─────────────────────────────────────────────────────────────────────
# Section 6: Infeasible check — NO source → NO target
# ─────────────────────────────────────────────────────────────────────

def check_infeasible(sizes: list[int], target: int) -> bool:
    """
    If SubsetSum(sizes, target) is infeasible,
    then IEM(reduce(sizes, target)) must also be infeasible.
    """
    if is_subset_sum_feasible(sizes, target):
        return True  # not infeasible; skip
    expr, K = reduce(sizes, target)
    return not is_iem_feasible(expr, K)


# ─────────────────────────────────────────────────────────────────────
# Section 7: Overhead check
# ─────────────────────────────────────────────────────────────────────

def check_overhead(sizes: list[int], target: int) -> bool:
    """
    Verify:
      - num_union_nodes == n
      - num_atoms == 2n
      - expression_size == 4n - 1 (for n >= 2)
      - K == target + n
      - all atoms are positive
    """
    n = len(sizes)
    expr, K = reduce(sizes, target)

    # Target value
    if K != target + n:
        return False

    # Union count
    if count_union_nodes(expr) != n:
        return False

    # Atom count
    if count_atoms(expr) != 2 * n:
        return False

    # Tree size: n unions + (n-1) sums + 2n atoms = 4n - 1 for n >= 2
    # For n == 1: 1 union + 0 sums + 2 atoms = 3
    expected_size = 4 * n - 1 if n >= 2 else 3
    if tree_size(expr) != expected_size:
        return False

    # All atoms positive
    def all_positive(e):
        if e[0] == "atom":
            return e[1] > 0
        return all_positive(e[1]) and all_positive(e[2])

    if not all_positive(expr):
        return False

    return True


# Also cross-check that the set computed by full enumeration matches
# the set computed via brute-force config evaluation
def check_set_consistency(sizes: list[int], target: int) -> bool:
    """Verify that eval_set and config-based evaluation agree."""
    expr, K = reduce(sizes, target)
    full_set = eval_set(expr)
    n_unions = count_union_nodes(expr)
    config_set = set()
    for config in product(range(2), repeat=n_unions):
        val = eval_expr(expr, list(config), [0])
        if val is not None:
            config_set.add(val)
    return full_set == config_set


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
            for t in range(0, min(sigma + 2, sigma + 2)):
                assert check_forward(sizes, t), (
                    f"Forward FAILED: sizes={sizes}, target={t}"
                )
                assert check_backward(sizes, t), (
                    f"Backward FAILED: sizes={sizes}, target={t}"
                )
                assert check_infeasible(sizes, t), (
                    f"Infeasible FAILED: sizes={sizes}, target={t}"
                )
                assert check_overhead(sizes, t), (
                    f"Overhead FAILED: sizes={sizes}, target={t}"
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


def consistency_tests(count: int = 200) -> int:
    """Cross-check set evaluation methods on small instances."""
    import random
    rng = random.Random(77)
    checks = 0
    for _ in range(count):
        n = rng.randint(1, 6)
        sizes = [rng.randint(1, 15) for _ in range(n)]
        sigma = sum(sizes)
        target = rng.randint(0, sigma + 5)
        assert check_set_consistency(sizes, target), (
            f"Set consistency FAILED: sizes={sizes}, target={target}"
        )
        checks += 1
    return checks


def collect_test_vectors(count: int = 20) -> list[dict]:
    """Collect representative test vectors for downstream consumption."""
    import random
    rng = random.Random(123)
    vectors = []

    hand_crafted = [
        # YES: basic feasible
        {"sizes": [3, 5, 7], "target": 8, "label": "yes_basic"},
        # YES: single element selected
        {"sizes": [5], "target": 5, "label": "yes_single"},
        # YES: all elements selected
        {"sizes": [2, 3, 5], "target": 10, "label": "yes_all_selected"},
        # YES: empty subset (target 0)
        {"sizes": [1, 2, 3], "target": 0, "label": "yes_target_zero"},
        # YES: two elements
        {"sizes": [4, 6], "target": 10, "label": "yes_two_all"},
        # YES: larger instance
        {"sizes": [1, 2, 4, 8], "target": 7, "label": "yes_powers_of_2"},
        # NO: target exceeds sum
        {"sizes": [1, 2, 3], "target": 100, "label": "no_target_exceeds_sum"},
        # NO: no subset works
        {"sizes": [3, 7, 11], "target": 5, "label": "no_no_subset"},
        # NO: single element mismatch
        {"sizes": [5], "target": 3, "label": "no_single_mismatch"},
        # YES: uniform elements
        {"sizes": [4, 4, 4, 4], "target": 8, "label": "yes_uniform"},
    ]

    for hc in hand_crafted:
        sizes = hc["sizes"]
        target = hc["target"]
        expr, K = reduce(sizes, target)
        src_sol = solve_subset_sum(sizes, target)
        iem_sol = solve_iem(expr, K)
        extracted = None
        if iem_sol is not None:
            extracted = extract(sizes, target, iem_sol)
        full_set = sorted(eval_set(expr))
        vectors.append({
            "label": hc["label"],
            "source": {"sizes": sizes, "target": target},
            "target": {"K": K, "set_represented": full_set},
            "source_feasible": src_sol is not None,
            "target_feasible": iem_sol is not None,
            "source_solution": src_sol,
            "target_solution": iem_sol,
            "extracted_solution": extracted,
        })

    # Random vectors
    for i in range(count - len(hand_crafted)):
        n = rng.randint(1, 8)
        sizes = [rng.randint(1, 20) for _ in range(n)]
        sigma = sum(sizes)
        target = rng.randint(0, sigma + 5)
        expr, K = reduce(sizes, target)
        src_sol = solve_subset_sum(sizes, target)
        iem_sol = solve_iem(expr, K)
        extracted = None
        if iem_sol is not None:
            extracted = extract(sizes, target, iem_sol)
        full_set = sorted(eval_set(expr))
        vectors.append({
            "label": f"random_{i}",
            "source": {"sizes": sizes, "target": target},
            "target": {"K": K, "set_represented": full_set},
            "source_feasible": src_sol is not None,
            "target_feasible": iem_sol is not None,
            "source_solution": src_sol,
            "target_solution": iem_sol,
            "extracted_solution": extracted,
        })

    return vectors


if __name__ == "__main__":
    print("=" * 60)
    print("SubsetSum → IntegerExpressionMembership verification")
    print("=" * 60)

    print("\n[1/4] Exhaustive tests (n ≤ 5)...")
    n_exhaustive = exhaustive_tests()
    print(f"  Exhaustive checks: {n_exhaustive}")

    print("\n[2/4] Random tests...")
    n_random = random_tests(count=2000)
    print(f"  Random checks: {n_random}")

    print("\n[3/4] Set consistency tests...")
    n_consistency = consistency_tests()
    print(f"  Consistency checks: {n_consistency}")

    total = n_exhaustive + n_random + n_consistency
    print(f"\n  TOTAL checks: {total}")
    assert total >= 5000, f"Need ≥5000 checks, got {total}"

    print("\n[4/4] Generating test vectors...")
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
    out_path = "docs/paper/verify-reductions/test_vectors_subset_sum_integer_expression_membership.json"
    with open(out_path, "w") as f:
        json.dump({"vectors": vectors, "total_checks": total}, f, indent=2)
    print(f"  Wrote {len(vectors)} test vectors to {out_path}")

    print(f"\nAll {total} checks PASSED.")
