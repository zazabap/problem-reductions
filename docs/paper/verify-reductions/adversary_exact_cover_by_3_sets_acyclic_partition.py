#!/usr/bin/env python3
"""
Adversary verification script: ExactCoverBy3Sets -> AcyclicPartition reduction.
Issue: #822

VERDICT: REFUTED

Independent re-implementation of the reduction and extraction logic,
plus property-based testing with hypothesis. >=5000 independent checks.

This script does NOT import from verify_exact_cover_by_3_sets_acyclic_partition.py --
it re-derives everything from scratch as an independent cross-check.
"""

import json
import sys
from itertools import combinations, product
from collections import defaultdict
from typing import Optional

try:
    from hypothesis import given, settings, assume, HealthCheck
    from hypothesis import strategies as st
    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False
    print("WARNING: hypothesis not installed; falling back to pure-random adversary tests")


# ---------------------------------------------------------------------
# Independent re-implementation of reduction
# ---------------------------------------------------------------------

def adv_reduce(universe_size: int, subsets: list[list[int]]) -> dict:
    """Independent reduction: X3C -> AcyclicPartition (issue #822 spec)."""
    q = universe_size // 3
    m = len(subsets)
    n = universe_size + m

    arcs = []
    costs = []

    # Element chain
    for i in range(universe_size - 1):
        arcs.append((i, i + 1))
        costs.append(1)

    # Membership arcs
    for j in range(m):
        for elem in sorted(subsets[j]):
            arcs.append((universe_size + j, elem))
            costs.append(1)

    weights = [1] * n
    B = 3
    K = 3 * (m - q) + (universe_size - 1)

    return {"n": n, "arcs": arcs, "costs": costs, "weights": weights, "B": B, "K": K}


def adv_extract(universe_size: int, subsets: list[list[int]], config: list[int]) -> list[int]:
    """Independent extraction."""
    result = [0] * len(subsets)
    for j, sub in enumerate(subsets):
        sj = universe_size + j
        if all(config[elem] == config[sj] for elem in sub):
            result[j] = 1
    return result


def adv_eval_x3c(universe_size: int, subsets: list[list[int]], config: list[int]) -> bool:
    """Evaluate X3C solution."""
    q = universe_size // 3
    selected = [i for i, v in enumerate(config) if v == 1]
    if len(selected) != q:
        return False
    covered = set()
    for idx in selected:
        s = set(subsets[idx])
        if s & covered:
            return False
        covered |= s
    return covered == set(range(universe_size))


def adv_is_dag(num_v: int, arcs) -> bool:
    """DAG check."""
    adj = defaultdict(set)
    in_deg = [0] * num_v
    for u, v in arcs:
        adj[u].add(v)
        in_deg[v] += 1
    queue = [nd for nd in range(num_v) if in_deg[nd] == 0]
    count = 0
    while queue:
        nd = queue.pop()
        count += 1
        for m_node in adj[nd]:
            in_deg[m_node] -= 1
            if in_deg[m_node] == 0:
                queue.append(m_node)
    return count == num_v


def adv_eval_ap(ap: dict, config: list[int]) -> bool:
    """Evaluate AP solution."""
    n = ap["n"]
    if len(config) != n:
        return False
    pw = defaultdict(int)
    for v in range(n):
        pw[config[v]] += ap["weights"][v]
        if pw[config[v]] > ap["B"]:
            return False
    total_cost = 0
    q_arcs = set()
    for idx, (u, v) in enumerate(ap["arcs"]):
        if config[u] != config[v]:
            total_cost += ap["costs"][idx]
            if total_cost > ap["K"]:
                return False
            q_arcs.add((config[u], config[v]))
    labels = sorted(set(config))
    lmap = {l: i for i, l in enumerate(labels)}
    mapped = set((lmap[u], lmap[v]) for u, v in q_arcs)
    return adv_is_dag(len(labels), mapped)


def adv_solve_x3c(universe_size: int, subsets: list[list[int]]) -> Optional[list[int]]:
    """Brute-force X3C solver."""
    q = universe_size // 3
    m = len(subsets)
    for combo in combinations(range(m), q):
        covered = set()
        ok = True
        for idx in combo:
            if set(subsets[idx]) & covered:
                ok = False
                break
            covered |= set(subsets[idx])
        if ok and covered == set(range(universe_size)):
            cfg = [0] * m
            for idx in combo:
                cfg[idx] = 1
            return cfg
    return None


def _adv_gen_partitions(n: int, max_size: int):
    """Generate all partitions of {0..n-1} into groups of size <= max_size."""
    if n == 0:
        yield []
        return
    elements = list(range(n))

    def _gen(remaining):
        if not remaining:
            yield []
            return
        first = remaining[0]
        rest = remaining[1:]
        for extra_size in range(min(max_size - 1, len(rest)) + 1):
            for companions in combinations(rest, extra_size):
                group = frozenset([first] + list(companions))
                new_rest = [x for x in rest if x not in companions]
                for sub in _gen(new_rest):
                    yield [group] + sub

    yield from _gen(elements)


def adv_solve_ap(ap: dict) -> Optional[list[int]]:
    """Solve AP by partition enumeration."""
    n = ap["n"]
    B = ap["B"]
    for partition in _adv_gen_partitions(n, B):
        config = [0] * n
        for label, group in enumerate(partition):
            for v in group:
                config[v] = label
        if adv_eval_ap(ap, config):
            return config
    return None


# ---------------------------------------------------------------------
# Property checks
# ---------------------------------------------------------------------

def adv_check_all(universe_size: int, subsets: list[list[int]]) -> tuple[int, list[str]]:
    """Run all adversary checks. Returns (check_count, failure_list)."""
    checks = 0
    failures = []

    # 1. Overhead
    ap = adv_reduce(universe_size, subsets)
    m = len(subsets)
    exp_v = universe_size + m
    exp_a = 3 * m + universe_size - 1
    assert ap["n"] == exp_v
    assert len(ap["arcs"]) == exp_a
    checks += 1

    if ap["n"] > 10:
        return checks, failures

    # 2. Solve both
    src_sol = adv_solve_x3c(universe_size, subsets)
    tgt_sol = adv_solve_ap(ap)
    src_feas = src_sol is not None
    tgt_feas = tgt_sol is not None

    # 3. Forward
    if src_feas and not tgt_feas:
        failures.append(f"Forward: X3C YES but AP NO, subs={subsets}")
    checks += 1

    # 4. Backward
    if tgt_feas:
        extracted = adv_extract(universe_size, subsets, tgt_sol)
        if not adv_eval_x3c(universe_size, subsets, extracted):
            failures.append(f"Backward: extraction invalid, subs={subsets}")
        checks += 1

    # 5. Infeasible
    if not src_feas and tgt_feas:
        failures.append(f"Infeasible: X3C NO but AP YES, subs={subsets}, cfg={tgt_sol}")
    checks += 1

    # 6. Feasibility agreement
    if src_feas != tgt_feas:
        failures.append(f"Mismatch: X3C={'Y' if src_feas else 'N'}, "
                        f"AP={'Y' if tgt_feas else 'N'}, subs={subsets}")
    checks += 1

    return checks, failures


# ---------------------------------------------------------------------
# Test drivers
# ---------------------------------------------------------------------

def adversary_exhaustive() -> tuple[int, list[str]]:
    """Exhaustive adversary tests: universe=6, 2-3 subsets."""
    all_triples = list(combinations(range(6), 3))
    checks = 0
    all_failures = []

    for num_subs in range(2, 4):
        for combo in combinations(range(len(all_triples)), num_subs):
            subs = [list(all_triples[i]) for i in combo]
            c, f = adv_check_all(6, subs)
            checks += c
            all_failures.extend(f)

    return checks, all_failures


def adversary_random(count: int = 800) -> tuple[int, list[str]]:
    """Random adversary tests with independent seed."""
    import random
    rng = random.Random(9999)
    all_triples = list(combinations(range(6), 3))
    checks = 0
    all_failures = []

    for _ in range(count):
        k = rng.randint(2, 4)
        chosen = rng.sample(all_triples, k)
        subs = [list(t) for t in chosen]
        c, f = adv_check_all(6, subs)
        checks += c
        all_failures.extend(f)

    return checks, all_failures


def adversary_hypothesis() -> tuple[int, list[str]]:
    """Property-based testing with hypothesis."""
    if not HAS_HYPOTHESIS:
        return 0, []

    checks_counter = [0]
    all_failures_list = []

    @given(
        num_subs=st.integers(min_value=2, max_value=3),
        seed=st.integers(min_value=0, max_value=10000),
    )
    @settings(
        max_examples=300,
        suppress_health_check=[HealthCheck.too_slow],
        deadline=None,
    )
    def prop_reduction(num_subs, seed):
        import random
        rng = random.Random(seed)
        all_triples = list(combinations(range(6), 3))
        chosen = rng.sample(all_triples, num_subs)
        subs = [list(t) for t in chosen]
        c, f = adv_check_all(6, subs)
        checks_counter[0] += c
        all_failures_list.extend(f)

    prop_reduction()
    return checks_counter[0], all_failures_list


def adversary_edge_cases() -> tuple[int, list[str]]:
    """Targeted edge cases."""
    checks = 0
    all_failures = []

    edge_cases = [
        (3, [[0, 1, 2]]),
        (6, [[0, 1, 2], [3, 4, 5]]),
        (6, [[0, 1, 2], [3, 4, 5], [0, 3, 4]]),
        (6, [[0, 1, 2], [1, 3, 4], [2, 4, 5]]),
        (6, [[0, 1, 2], [0, 3, 4]]),
        (6, [[0, 1, 2], [0, 1, 3], [0, 1, 4]]),
        (6, [[0, 1, 2], [3, 4, 5], [0, 1, 3]]),
        (6, [[0, 1, 3], [2, 4, 5], [0, 2, 4], [1, 3, 5]]),
        (6, [[0, 1, 2], [0, 3, 4], [1, 3, 5], [2, 4, 5], [0, 1, 5]]),
    ]

    for us, subs in edge_cases:
        c, f = adv_check_all(us, subs)
        checks += c
        all_failures.extend(f)

    return checks, all_failures


if __name__ == "__main__":
    print("=" * 60)
    print("Adversary verification: ExactCoverBy3Sets -> AcyclicPartition")
    print("Issue #822 -- REFUTATION")
    print("=" * 60)

    total_checks = 0
    total_failures = []

    print("\n[1/4] Edge cases...")
    c, f = adversary_edge_cases()
    total_checks += c
    total_failures.extend(f)
    print(f"  Checks: {c}, failures: {len(f)}")

    print("\n[2/4] Exhaustive (universe=6, 2-3 subsets)...")
    c, f = adversary_exhaustive()
    total_checks += c
    total_failures.extend(f)
    print(f"  Checks: {c}, failures: {len(f)}")

    print("\n[3/4] Random (different seed)...")
    c, f = adversary_random(count=800)
    total_checks += c
    total_failures.extend(f)
    print(f"  Checks: {c}, failures: {len(f)}")

    print("\n[4/4] Hypothesis PBT...")
    c, f = adversary_hypothesis()
    total_checks += c
    total_failures.extend(f)
    print(f"  Checks: {c}, failures: {len(f)}")

    unique_failures = list(set(total_failures))
    print(f"\n  TOTAL checks: {total_checks}")
    assert total_checks >= 5000, f"Need >=5000 checks, got {total_checks}"

    print(f"  Unique failures: {len(unique_failures)}")
    if unique_failures[:5]:
        print("  Sample:")
        for fail in unique_failures[:5]:
            print(f"    {fail}")

    infeasible = [f for f in total_failures if "Infeasible" in f]
    assert len(infeasible) > 0, "Expected infeasible violations!"

    print(f"\n{'='*60}")
    print(f"VERDICT: REFUTED ({len(unique_failures)} distinct failures)")
    print(f"{'='*60}")
