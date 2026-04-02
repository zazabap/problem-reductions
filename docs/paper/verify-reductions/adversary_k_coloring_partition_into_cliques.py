#!/usr/bin/env python3
"""Adversary verification script for KColoring → PartitionIntoCliques reduction.

Issue: #844
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
import json
import sys
from pathlib import Path

# ============================================================
# Independent implementation from Typst proof
# ============================================================

def reduce(num_vertices, edges, num_colors):
    """
    KColoring(G, K) → PartitionIntoCliques(complement(G), K).

    From the Typst proof:
    1. Compute complement graph: same vertices, edge {u,v} iff {u,v} not in E.
    2. Set K' = K.
    """
    edge_set = set()
    for u, v in edges:
        a, b = min(u, v), max(u, v)
        edge_set.add((a, b))

    comp_edges = []
    for i in range(num_vertices):
        for j in range(i + 1, num_vertices):
            if (i, j) not in edge_set:
                comp_edges.append((i, j))

    return num_vertices, comp_edges, num_colors


def extract_solution(num_vertices, target_partition):
    """
    Extract K-coloring from clique partition.
    From proof: assign color i to all vertices in clique V_i.
    The partition config already assigns group indices = colors.
    """
    return list(target_partition)


def is_feasible_source(num_vertices, edges, num_colors, config):
    """Check if config is a valid K-coloring of G."""
    if len(config) != num_vertices:
        return False
    for c in config:
        if c < 0 or c >= num_colors:
            return False
    adj = set()
    for u, v in edges:
        adj.add((min(u, v), max(u, v)))
    for u, v in adj:
        if config[u] == config[v]:
            return False
    return True


def is_feasible_target(num_vertices, edges, num_cliques, config):
    """Check if config is a valid partition into <= num_cliques cliques."""
    if len(config) != num_vertices:
        return False
    for c in config:
        if c < 0 or c >= num_cliques:
            return False
    adj = set()
    for u, v in edges:
        adj.add((min(u, v), max(u, v)))
    for g in range(num_cliques):
        members = [v for v in range(num_vertices) if config[v] == g]
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                a, b = min(members[i], members[j]), max(members[i], members[j])
                if (a, b) not in adj:
                    return False
    return True


def brute_force_source(num_vertices, edges, num_colors):
    """Find any valid K-coloring, or None."""
    for config in itertools.product(range(num_colors), repeat=num_vertices):
        if is_feasible_source(num_vertices, edges, num_colors, list(config)):
            return list(config)
    return None


def brute_force_target(num_vertices, edges, num_cliques):
    """Find any valid clique partition, or None."""
    for config in itertools.product(range(num_cliques), repeat=num_vertices):
        if is_feasible_target(num_vertices, edges, num_cliques, list(config)):
            return list(config)
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
    all_possible = [(i, j) for i in range(n) for j in range(i + 1, n)]
    num_possible = len(all_possible)

    for mask in range(1 << num_possible):
        edges = [all_possible[i] for i in range(num_possible) if mask & (1 << i)]

        for k in range(1, n + 1):
            src_wit = brute_force_source(n, edges, k)
            src_feas = src_wit is not None

            tn, tedges, tk = reduce(n, edges, k)
            tgt_wit = brute_force_target(tn, tedges, tk)
            tgt_feas = tgt_wit is not None

            check(src_feas == tgt_feas,
                  f"Disagreement: n={n}, m={len(edges)}, k={k}: src={src_feas}, tgt={tgt_feas}")

            # Test extraction when target is feasible
            if tgt_feas and tgt_wit is not None:
                extracted = extract_solution(n, tgt_wit)
                check(is_feasible_source(n, edges, k, extracted),
                      f"Extraction failed: n={n}, m={len(edges)}, k={k}")

    print(f"  n={n}: done")

print(f"  Checks so far: {checks}")


# ============================================================
# Test 2: YES example from Typst
# ============================================================
print("Test 2: YES example from Typst proof...")

yes_n = 5
yes_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
yes_k = 3
yes_coloring = [0, 1, 2, 1, 0]

# Source feasible
check(is_feasible_source(yes_n, yes_edges, yes_k, yes_coloring),
      "YES: source coloring should be valid")

# Reduce
tn, tedges, tk = reduce(yes_n, yes_edges, yes_k)

# Complement edges from Typst: (0,4), (1,3), (1,4), (2,4), (3,4)
expected_comp = {(0, 4), (1, 3), (1, 4), (2, 4), (3, 4)}
actual_comp = {(min(u, v), max(u, v)) for u, v in tedges}
check(actual_comp == expected_comp,
      f"YES: complement edges mismatch: {actual_comp} vs {expected_comp}")

check(len(tedges) == 5, f"YES: expected 5 complement edges, got {len(tedges)}")
check(tn == 5, f"YES: expected 5 vertices")
check(tk == 3, f"YES: expected K'=3")

# Target feasible
tgt_wit = brute_force_target(tn, tedges, tk)
check(tgt_wit is not None, "YES: target should be feasible")

# Extract and verify
if tgt_wit is not None:
    extracted = extract_solution(yes_n, tgt_wit)
    check(is_feasible_source(yes_n, yes_edges, yes_k, extracted),
          "YES: extracted coloring should be valid")

# Color classes from Typst: V0={0,4}, V1={1,3}, V2={2}
V0 = sorted([v for v in range(yes_n) if yes_coloring[v] == 0])
V1 = sorted([v for v in range(yes_n) if yes_coloring[v] == 1])
V2 = sorted([v for v in range(yes_n) if yes_coloring[v] == 2])
check(V0 == [0, 4], f"YES: V0={V0}")
check(V1 == [1, 3], f"YES: V1={V1}")
check(V2 == [2], f"YES: V2={V2}")

# Verify color classes are cliques in complement
check((0, 4) in actual_comp, "YES: V0 not a clique")
check((1, 3) in actual_comp, "YES: V1 not a clique")

print(f"  YES example checks: {checks}")


# ============================================================
# Test 3: NO example from Typst
# ============================================================
print("Test 3: NO example from Typst proof...")

no_n = 4
no_edges = [(i, j) for i in range(4) for j in range(i + 1, 4)]  # K4
no_k = 3

# Source infeasible
check(brute_force_source(no_n, no_edges, no_k) is None,
      "NO: K4 should not be 3-colorable")

# Reduce
tn, tedges, tk = reduce(no_n, no_edges, no_k)

check(len(tedges) == 0, f"NO: complement of K4 should have 0 edges")
check(tn == 4, "NO: expected 4 vertices")
check(tk == 3, "NO: expected K'=3")

# Target infeasible
check(brute_force_target(tn, tedges, tk) is None,
      "NO: empty graph with 4 vertices cannot partition into 3 cliques")

# Exhaustively verify all 3^4 = 81 assignments are invalid
for config in itertools.product(range(no_k), repeat=no_n):
    check(not is_feasible_target(tn, tedges, tk, list(config)),
          f"NO: config {config} should be invalid")

print(f"  NO example checks: {checks}")


# ============================================================
# Test 4: hypothesis property-based testing
# ============================================================
print("Test 4: hypothesis property-based testing...")

try:
    from hypothesis import given, strategies as st, settings, assume

    @st.composite
    def graph_and_k(draw):
        """Strategy 1: random graph with random K."""
        n = draw(st.integers(min_value=1, max_value=6))
        all_e = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edge_mask = draw(st.lists(st.booleans(), min_size=len(all_e), max_size=len(all_e)))
        edges = [e for e, include in zip(all_e, edge_mask) if include]
        k = draw(st.integers(min_value=1, max_value=n))
        return n, edges, k

    @st.composite
    def dense_graph_and_k(draw):
        """Strategy 2: dense/sparse graph extremes."""
        n = draw(st.integers(min_value=2, max_value=6))
        density = draw(st.sampled_from([0.0, 0.1, 0.5, 0.9, 1.0]))
        all_e = [(i, j) for i in range(n) for j in range(i + 1, n)]
        import random as rng
        seed = draw(st.integers(min_value=0, max_value=10000))
        r = rng.Random(seed)
        edges = [e for e in all_e if r.random() < density]
        k = draw(st.integers(min_value=1, max_value=n))
        return n, edges, k

    @given(graph_and_k())
    @settings(max_examples=2000, deadline=None)
    def test_reduction_random(args):
        global checks
        n, edges, k = args
        src_wit = brute_force_source(n, edges, k)
        src_feas = src_wit is not None
        tn, tedges, tk = reduce(n, edges, k)
        tgt_wit = brute_force_target(tn, tedges, tk)
        tgt_feas = tgt_wit is not None
        check(src_feas == tgt_feas,
              f"PBT random: n={n}, m={len(edges)}, k={k}")
        if tgt_feas and tgt_wit is not None:
            extracted = extract_solution(n, tgt_wit)
            check(is_feasible_source(n, edges, k, extracted),
                  f"PBT random extraction: n={n}, m={len(edges)}, k={k}")

    @given(dense_graph_and_k())
    @settings(max_examples=2000, deadline=None)
    def test_reduction_dense(args):
        global checks
        n, edges, k = args
        src_wit = brute_force_source(n, edges, k)
        src_feas = src_wit is not None
        tn, tedges, tk = reduce(n, edges, k)
        tgt_wit = brute_force_target(tn, tedges, tk)
        tgt_feas = tgt_wit is not None
        check(src_feas == tgt_feas,
              f"PBT dense: n={n}, m={len(edges)}, k={k}")
        if tgt_feas and tgt_wit is not None:
            extracted = extract_solution(n, tgt_wit)
            check(is_feasible_source(n, edges, k, extracted),
                  f"PBT dense extraction: n={n}, m={len(edges)}, k={k}")

    test_reduction_random()
    print(f"  Strategy 1 (random graphs) done. Checks: {checks}")
    test_reduction_dense()
    print(f"  Strategy 2 (dense/sparse extremes) done. Checks: {checks}")

except ImportError:
    print("  WARNING: hypothesis not available, using manual PBT fallback")
    import random
    random.seed(123)
    for _ in range(4000):
        n = random.randint(1, 6)
        all_e = [(i, j) for i in range(n) for j in range(i + 1, n)]
        edges = [e for e in all_e if random.random() < random.random()]
        k = random.randint(1, n)

        src_wit = brute_force_source(n, edges, k)
        src_feas = src_wit is not None
        tn, tedges, tk = reduce(n, edges, k)
        tgt_wit = brute_force_target(tn, tedges, tk)
        tgt_feas = tgt_wit is not None
        check(src_feas == tgt_feas,
              f"Fallback PBT: n={n}, m={len(edges)}, k={k}")
        if tgt_feas and tgt_wit is not None:
            extracted = extract_solution(n, tgt_wit)
            check(is_feasible_source(n, edges, k, extracted),
                  f"Fallback PBT extraction: n={n}, m={len(edges)}, k={k}")


# ============================================================
# Test 5: Cross-comparison with constructor
# ============================================================
print("Test 5: Cross-comparison with constructor outputs...")

# Load test vectors from constructor and verify our reduce() agrees
vectors_path = Path(__file__).parent / "test_vectors_k_coloring_partition_into_cliques.json"
if vectors_path.exists():
    with open(vectors_path) as f:
        vectors = json.load(f)

    # YES instance
    yi = vectors["yes_instance"]
    inp = yi["input"]
    out = yi["output"]
    tn, tedges, tk = reduce(inp["num_vertices"], [tuple(e) for e in inp["edges"]], inp["num_colors"])
    check(tn == out["num_vertices"], "Cross: YES num_vertices mismatch")
    our_edges = {(min(u, v), max(u, v)) for u, v in tedges}
    their_edges = {(min(u, v), max(u, v)) for u, v in [tuple(e) for e in out["edges"]]}
    check(our_edges == their_edges, "Cross: YES edges mismatch")
    check(tk == out["num_cliques"], "Cross: YES num_cliques mismatch")

    # NO instance
    ni = vectors["no_instance"]
    inp = ni["input"]
    out = ni["output"]
    tn, tedges, tk = reduce(inp["num_vertices"], [tuple(e) for e in inp["edges"]], inp["num_colors"])
    check(tn == out["num_vertices"], "Cross: NO num_vertices mismatch")
    our_edges = {(min(u, v), max(u, v)) for u, v in tedges}
    their_edges = {(min(u, v), max(u, v)) for u, v in [tuple(e) for e in out["edges"]]}
    check(our_edges == their_edges, "Cross: NO edges mismatch")
    check(tk == out["num_cliques"], "Cross: NO num_cliques mismatch")

    print(f"  Cross-comparison checks passed")
else:
    print(f"  WARNING: test vectors not found at {vectors_path}, skipping cross-comparison")


# ============================================================
# Summary
# ============================================================
print(f"\n{'=' * 60}")
print(f"ADVERSARY VERIFICATION SUMMARY")
print(f"  Total checks: {checks} (minimum: 5,000)")
print(f"  Failures:     {len(failures)}")
print(f"{'=' * 60}")

if failures:
    print(f"\nFAILED:")
    for f in failures[:20]:
        print(f"  {f}")
    sys.exit(1)
else:
    print(f"\nPASSED: All {checks} adversary checks passed.")

if checks < 5000:
    print(f"\nWARNING: Total checks ({checks}) below minimum (5,000).")
    sys.exit(1)
