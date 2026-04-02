#!/usr/bin/env python3
"""
Verification script: ExactCoverBy3Sets -> AcyclicPartition reduction.
Issue: #822
Reference: Garey & Johnson, Computers and Intractability, ND15, p.209

VERDICT: REFUTED -- the proposed reduction algorithm is incorrect.

Seven mandatory sections:
  1. reduce()         -- the reduction function (as proposed in issue #822)
  2. extract()        -- solution extraction (back-map)
  3. Brute-force solvers for source and target
  4. Forward: YES source -> YES target
  5. Backward: YES target -> YES source (via extract)
  6. Infeasible: NO source -> NO target
  7. Overhead check

Runs >=5000 checks total, demonstrating the reduction fails.
"""

import json
import sys
from itertools import combinations, product
from collections import defaultdict
from typing import Optional


# ---------------------------------------------------------------------
# Section 1: reduce()
# ---------------------------------------------------------------------

def reduce(universe_size: int, subsets: list[list[int]], K: int | None = None
           ) -> dict:
    """
    Reduce X3C(universe_size, subsets) -> AcyclicPartition.

    Implements the construction from issue #822:
    - Element vertices e_0..e_{3q-1}, weight 1
    - Selector vertices s_0..s_{m-1}, weight 1
    - Element chain: e_0->e_1->...->e_{3q-1}, cost 1
    - Membership arcs: s_i->e_a, s_i->e_b, s_i->e_c for C_i={a,b,c}, cost 1
    - B = 3 (weight bound)
    - K = provided or computed as 3*(m-q) + (3q-1) (generous default)
    """
    q = universe_size // 3
    m = len(subsets)
    n = universe_size + m

    arcs = []
    arc_costs = []

    # Element chain
    for i in range(universe_size - 1):
        arcs.append((i, i + 1))
        arc_costs.append(1)

    # Membership arcs
    for j, subset in enumerate(subsets):
        for elem in sorted(subset):
            arcs.append((universe_size + j, elem))
            arc_costs.append(1)

    vertex_weights = [1] * n
    B = 3

    if K is None:
        K = 3 * (m - q) + (universe_size - 1)

    return {
        "num_vertices": n,
        "arcs": arcs,
        "vertex_weights": vertex_weights,
        "arc_costs": arc_costs,
        "weight_bound": B,
        "cost_bound": K,
    }


# ---------------------------------------------------------------------
# Section 2: extract()
# ---------------------------------------------------------------------

def extract(universe_size: int, subsets: list[list[int]],
            ap_config: list[int]) -> list[int]:
    """
    Extract an X3C solution from an AcyclicPartition configuration.

    For each selector s_j, check if all 3 of its elements are in the same group.
    If so, mark subset j as selected.
    """
    m = len(subsets)
    x3c_config = [0] * m
    for j, subset in enumerate(subsets):
        sj = universe_size + j
        sj_label = ap_config[sj]
        if all(ap_config[elem] == sj_label for elem in subset):
            x3c_config[j] = 1
    return x3c_config


# ---------------------------------------------------------------------
# Section 3: Brute-force solvers
# ---------------------------------------------------------------------

def solve_x3c(universe_size: int, subsets: list[list[int]]) -> Optional[list[int]]:
    """Brute-force X3C solver. Returns binary config or None."""
    q = universe_size // 3
    m = len(subsets)
    for combo in combinations(range(m), q):
        covered = set()
        ok = True
        for idx in combo:
            s = set(subsets[idx])
            if s & covered:
                ok = False
                break
            covered |= s
        if ok and covered == set(range(universe_size)):
            config = [0] * m
            for idx in combo:
                config[idx] = 1
            return config
    return None


def is_dag(num_v: int, arcs) -> bool:
    """Check if directed graph is a DAG."""
    adj = defaultdict(set)
    in_deg = [0] * num_v
    for u, v in arcs:
        adj[u].add(v)
        in_deg[v] += 1
    queue = [n for n in range(num_v) if in_deg[n] == 0]
    count = 0
    while queue:
        n = queue.pop()
        count += 1
        for m_node in adj[n]:
            in_deg[m_node] -= 1
            if in_deg[m_node] == 0:
                queue.append(m_node)
    return count == num_v


def eval_ap(ap: dict, config: list[int]) -> bool:
    """Evaluate AcyclicPartition solution."""
    num_v = ap["num_vertices"]
    arcs = ap["arcs"]
    vw = ap["vertex_weights"]
    ac = ap["arc_costs"]
    B = ap["weight_bound"]
    K = ap["cost_bound"]

    if len(config) != num_v:
        return False

    pw = defaultdict(int)
    for v in range(num_v):
        pw[config[v]] += vw[v]
        if pw[config[v]] > B:
            return False

    total_cost = 0
    q_arcs = set()
    for idx, (u, v) in enumerate(arcs):
        if config[u] != config[v]:
            total_cost += ac[idx]
            if total_cost > K:
                return False
            q_arcs.add((config[u], config[v]))

    labels = sorted(set(config))
    lmap = {l: i for i, l in enumerate(labels)}
    mapped = set((lmap[u], lmap[v]) for u, v in q_arcs)
    return is_dag(len(labels), mapped)


def _generate_partitions(n: int, max_size: int):
    """Generate all partitions of {0..n-1} into groups of size <= max_size.

    Yields list-of-frozensets.
    Uses recursive approach: first element goes with some subset of remaining.
    """
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
        # first goes with 0..max_size-1 other elements from rest
        for extra_size in range(min(max_size - 1, len(rest)) + 1):
            for companions in combinations(rest, extra_size):
                group = frozenset([first] + list(companions))
                new_rest = [x for x in rest if x not in companions]
                for sub in _gen(new_rest):
                    yield [group] + sub

    yield from _gen(elements)


def solve_ap(ap: dict) -> Optional[list[int]]:
    """Solve AP by generating all valid partitions and checking each."""
    num_v = ap["num_vertices"]
    B = ap["weight_bound"]

    for partition in _generate_partitions(num_v, B):
        config = [0] * num_v
        for label, group in enumerate(partition):
            for v in group:
                config[v] = label
        if eval_ap(ap, config):
            return config
    return None


def find_min_K(universe_size: int, subsets: list[list[int]], max_K: int = 50) -> int | None:
    """Find minimum K for which AP instance is feasible."""
    q = universe_size // 3
    m = len(subsets)
    n = universe_size + m
    B = 3

    ap_template = reduce(universe_size, subsets, K=max_K)
    arcs = ap_template["arcs"]
    vw = ap_template["vertex_weights"]
    ac = ap_template["arc_costs"]

    best_cost = max_K + 1

    for partition in _generate_partitions(n, B):
        config = [0] * n
        for label, group in enumerate(partition):
            for v in group:
                config[v] = label

        # Weight check
        pw = defaultdict(int)
        ok = True
        for v in range(n):
            pw[config[v]] += vw[v]
            if pw[config[v]] > B:
                ok = False
                break
        if not ok:
            continue

        # Cost computation
        total_cost = 0
        q_arcs = set()
        for idx, (u, v) in enumerate(arcs):
            if config[u] != config[v]:
                total_cost += ac[idx]
                q_arcs.add((config[u], config[v]))

        if total_cost >= best_cost:
            continue

        # DAG check
        labels = sorted(set(config))
        lmap = {l: i for i, l in enumerate(labels)}
        mapped = set((lmap[u], lmap[v]) for u, v in q_arcs)
        if is_dag(len(labels), mapped):
            best_cost = total_cost

    return best_cost if best_cost <= max_K else None


# ---------------------------------------------------------------------
# Section 4: Forward check -- YES source -> YES target
# ---------------------------------------------------------------------

def check_forward(universe_size: int, subsets: list[list[int]]) -> tuple[bool, str]:
    """If X3C is feasible, AP must also be feasible."""
    x3c_sol = solve_x3c(universe_size, subsets)
    if x3c_sol is None:
        return True, "vacuously true"

    ap = reduce(universe_size, subsets)
    ap_sol = solve_ap(ap)
    if ap_sol is not None:
        return True, "AP feasible"
    else:
        return False, "FORWARD VIOLATION"


# ---------------------------------------------------------------------
# Section 5: Backward check -- YES target -> YES source (via extract)
# ---------------------------------------------------------------------

def check_backward(universe_size: int, subsets: list[list[int]]) -> tuple[bool, str]:
    """If AP is feasible, extraction should give valid X3C solution."""
    ap = reduce(universe_size, subsets)
    ap_sol = solve_ap(ap)
    if ap_sol is None:
        return True, "vacuously true"

    x3c_config = extract(universe_size, subsets, ap_sol)
    q = universe_size // 3
    selected = [i for i, v in enumerate(x3c_config) if v == 1]
    if len(selected) != q:
        return False, f"BACKWARD VIOLATION: {len(selected)} selected, expected {q}"

    covered = set()
    for idx in selected:
        s = set(subsets[idx])
        if s & covered:
            return False, "BACKWARD VIOLATION: overlap"
        covered |= s

    if covered != set(range(universe_size)):
        return False, f"BACKWARD VIOLATION: incomplete cover"

    return True, "extraction valid"


# ---------------------------------------------------------------------
# Section 6: Infeasible check -- NO source -> NO target
# ---------------------------------------------------------------------

def check_infeasible(universe_size: int, subsets: list[list[int]]) -> tuple[bool, str]:
    """If X3C is infeasible, AP must also be infeasible."""
    x3c_sol = solve_x3c(universe_size, subsets)
    if x3c_sol is not None:
        return True, "vacuously true"

    ap = reduce(universe_size, subsets)
    ap_sol = solve_ap(ap)
    if ap_sol is None:
        return True, "AP infeasible (correct)"
    else:
        return False, f"INFEASIBLE VIOLATION: X3C infeasible but AP feasible, config={ap_sol}"


# ---------------------------------------------------------------------
# Section 7: Overhead check
# ---------------------------------------------------------------------

def check_overhead(universe_size: int, subsets: list[list[int]]) -> tuple[bool, str]:
    """Verify overhead: vertices = |X|+|C|, arcs = 3|C|+|X|-1."""
    ap = reduce(universe_size, subsets)
    n = ap["num_vertices"]
    na = len(ap["arcs"])
    exp_v = universe_size + len(subsets)
    exp_a = 3 * len(subsets) + universe_size - 1
    ok = n == exp_v and na == exp_a
    return ok, f"v={n}/{exp_v}, a={na}/{exp_a}"


# ---------------------------------------------------------------------
# Test drivers
# ---------------------------------------------------------------------

def exhaustive_tests() -> dict:
    """Exhaustive tests for universe=6, 2-3 subsets."""
    all_triples = list(combinations(range(6), 3))
    checks = 0
    failures = {"forward": 0, "backward": 0, "infeasible": 0, "overhead": 0}
    counterexamples = []

    for num_subs in range(2, 4):  # 2 and 3 subsets only (manageable)
        for combo in combinations(range(len(all_triples)), num_subs):
            subs = [list(all_triples[i]) for i in combo]

            ok_f, _ = check_forward(6, subs)
            if not ok_f:
                failures["forward"] += 1
            checks += 1

            ok_b, detail_b = check_backward(6, subs)
            if not ok_b:
                failures["backward"] += 1
            checks += 1

            ok_i, detail_i = check_infeasible(6, subs)
            if not ok_i:
                failures["infeasible"] += 1
                if len(counterexamples) < 5:
                    counterexamples.append({"subsets": subs, "detail": detail_i})
            checks += 1

            ok_o, _ = check_overhead(6, subs)
            if not ok_o:
                failures["overhead"] += 1
            checks += 1

    return {"checks": checks, "failures": failures, "counterexamples": counterexamples}


def random_tests(count: int = 500) -> dict:
    """Random tests."""
    import random
    rng = random.Random(42)
    all_triples = list(combinations(range(6), 3))

    checks = 0
    failures = {"forward": 0, "backward": 0, "infeasible": 0, "overhead": 0}
    counterexamples = []

    for _ in range(count):
        num_subs = rng.randint(2, 5)
        chosen = rng.sample(all_triples, min(num_subs, len(all_triples)))
        subs = [list(t) for t in chosen]

        ok_f, _ = check_forward(6, subs)
        if not ok_f:
            failures["forward"] += 1
        checks += 1

        # Only run expensive checks for small instances
        if num_subs <= 3:
            ok_b, _ = check_backward(6, subs)
            if not ok_b:
                failures["backward"] += 1
            checks += 1

            ok_i, detail_i = check_infeasible(6, subs)
            if not ok_i:
                failures["infeasible"] += 1
                if len(counterexamples) < 3:
                    counterexamples.append({"subsets": subs, "detail": detail_i})
            checks += 1

        ok_o, _ = check_overhead(6, subs)
        if not ok_o:
            failures["overhead"] += 1
        checks += 1

    return {"checks": checks, "failures": failures, "counterexamples": counterexamples}


def min_K_analysis(count: int = 20) -> dict:
    """Minimum-K analysis showing YES/NO ranges overlap."""
    import random
    rng = random.Random(123)
    all_triples = list(combinations(range(6), 3))

    results = {"yes_min_Ks": [], "no_min_Ks": [], "checks": 0}

    instances = [
        (6, [[0,1,2],[3,4,5]]),
        (6, [[0,1,2],[3,4,5],[0,3,4]]),
        (6, [[0,1,2],[1,3,4],[2,4,5]]),
        (6, [[0,1,3],[2,4,5],[0,2,4],[1,3,5]]),
        (6, [[0,1,2],[0,3,4],[1,2,5]]),
        (6, [[0,1,2],[0,3,4],[0,1,5]]),
    ]

    for _ in range(count - len(instances)):
        k = rng.randint(2, 4)
        chosen = rng.sample(all_triples, k)
        instances.append((6, [list(t) for t in chosen]))

    for us, subs in instances:
        x3c = solve_x3c(us, subs)
        min_k = find_min_K(us, subs, max_K=30)
        results["checks"] += 1

        if min_k is not None:
            if x3c is not None:
                results["yes_min_Ks"].append(min_k)
            else:
                results["no_min_Ks"].append(min_k)

    return results


def collect_test_vectors(count: int = 20) -> list[dict]:
    """Collect representative test vectors."""
    import random
    rng = random.Random(456)
    all_triples = list(combinations(range(6), 3))

    vectors = []
    hand_crafted = [
        {"universe_size": 6, "subsets": [[0,1,2],[3,4,5]],
         "label": "yes_trivial"},
        {"universe_size": 6, "subsets": [[0,1,2],[3,4,5],[0,3,4]],
         "label": "yes_with_extra"},
        {"universe_size": 6, "subsets": [[0,1,2],[1,3,4],[2,4,5]],
         "label": "no_overlapping"},
        {"universe_size": 6, "subsets": [[0,1,2],[0,3,4]],
         "label": "no_incomplete"},
        {"universe_size": 6, "subsets": [[0,1,2],[0,1,3],[0,1,4]],
         "label": "no_heavy_overlap"},
        {"universe_size": 3, "subsets": [[0,1,2]],
         "label": "yes_minimal"},
        {"universe_size": 6, "subsets": [[0,1,3],[2,4,5],[0,2,4],[1,3,5]],
         "label": "yes_two_covers"},
    ]

    for hc in hand_crafted:
        us = hc["universe_size"]
        subs = hc["subsets"]
        x3c_sol = solve_x3c(us, subs)
        ap = reduce(us, subs)
        ap_sol = solve_ap(ap)
        extracted = extract(us, subs, ap_sol) if ap_sol else None

        vectors.append({
            "label": hc["label"],
            "source": {"universe_size": us, "subsets": subs},
            "target": {
                "num_vertices": ap["num_vertices"],
                "num_arcs": len(ap["arcs"]),
                "weight_bound": ap["weight_bound"],
                "cost_bound": ap["cost_bound"],
            },
            "source_feasible": x3c_sol is not None,
            "target_feasible": ap_sol is not None,
            "source_solution": x3c_sol,
            "target_solution": ap_sol,
            "extracted_solution": extracted,
        })

    for i in range(count - len(hand_crafted)):
        k = rng.randint(2, 3)
        chosen = rng.sample(all_triples, k)
        subs = [list(t) for t in chosen]
        us = 6
        x3c_sol = solve_x3c(us, subs)
        ap = reduce(us, subs)
        ap_sol = solve_ap(ap)
        extracted = extract(us, subs, ap_sol) if ap_sol else None
        vectors.append({
            "label": f"random_{i}",
            "source": {"universe_size": us, "subsets": subs},
            "target": {
                "num_vertices": ap["num_vertices"],
                "num_arcs": len(ap["arcs"]),
                "weight_bound": ap["weight_bound"],
                "cost_bound": ap["cost_bound"],
            },
            "source_feasible": x3c_sol is not None,
            "target_feasible": ap_sol is not None,
            "source_solution": x3c_sol,
            "target_solution": ap_sol,
            "extracted_solution": extracted,
        })

    return vectors


if __name__ == "__main__":
    print("=" * 60)
    print("ExactCoverBy3Sets -> AcyclicPartition verification")
    print("Issue #822 -- REFUTATION")
    print("=" * 60)

    print("\n[1/4] Exhaustive tests (universe=6, 2-3 subsets)...")
    exh = exhaustive_tests()
    print(f"  Checks: {exh['checks']}")
    print(f"  Forward violations: {exh['failures']['forward']}")
    print(f"  Backward violations: {exh['failures']['backward']}")
    print(f"  Infeasible violations: {exh['failures']['infeasible']}")
    print(f"  Overhead violations: {exh['failures']['overhead']}")
    if exh["counterexamples"]:
        print("  Sample counterexamples:")
        for ce in exh["counterexamples"][:3]:
            print(f"    {ce['subsets']}: {ce['detail']}")

    print("\n[2/4] Random tests...")
    rand = random_tests(count=500)
    print(f"  Checks: {rand['checks']}")
    print(f"  Forward violations: {rand['failures']['forward']}")
    print(f"  Backward violations: {rand['failures']['backward']}")
    print(f"  Infeasible violations: {rand['failures']['infeasible']}")

    print("\n[3/4] Min-K analysis...")
    analysis = min_K_analysis(count=20)
    print(f"  Checks: {analysis['checks']}")
    if analysis["yes_min_Ks"]:
        print(f"  YES min_K range: [{min(analysis['yes_min_Ks'])}, {max(analysis['yes_min_Ks'])}]")
    if analysis["no_min_Ks"]:
        print(f"  NO min_K range: [{min(analysis['no_min_Ks'])}, {max(analysis['no_min_Ks'])}]")
    if analysis["yes_min_Ks"] and analysis["no_min_Ks"]:
        overlap = max(analysis["yes_min_Ks"]) >= min(analysis["no_min_Ks"])
        print(f"  Ranges overlap: {overlap} -> {'REFUTED' if overlap else 'could work'}")

    total = exh["checks"] + rand["checks"] + analysis["checks"]
    print(f"\n  TOTAL checks: {total}")
    assert total >= 5000, f"Need >=5000 checks, got {total}"

    total_infeasible = exh["failures"]["infeasible"] + rand["failures"]["infeasible"]
    assert total_infeasible > 0, "Expected counterexamples but found none!"

    print("\n[4/4] Generating test vectors...")
    vectors = collect_test_vectors(count=20)

    incorrect = sum(1 for v in vectors
                    if not v["source_feasible"] and v["target_feasible"])
    print(f"  Vectors with reduction failure: {incorrect}/{len(vectors)}")

    out_path = "docs/paper/verify-reductions/test_vectors_exact_cover_by_3_sets_acyclic_partition.json"
    with open(out_path, "w") as f:
        json.dump({
            "verdict": "REFUTED",
            "issue": 822,
            "total_checks": total,
            "infeasible_violations": total_infeasible,
            "min_K_analysis": {
                "yes_range": sorted(analysis["yes_min_Ks"]) if analysis["yes_min_Ks"] else None,
                "no_range": sorted(analysis["no_min_Ks"]) if analysis["no_min_Ks"] else None,
            },
            "vectors": vectors,
        }, f, indent=2)
    print(f"  Wrote {len(vectors)} vectors to {out_path}")

    print(f"\n{'='*60}")
    print(f"VERDICT: REFUTED ({total_infeasible} infeasible violations)")
    print(f"All {total} checks completed.")
    print(f"{'='*60}")
