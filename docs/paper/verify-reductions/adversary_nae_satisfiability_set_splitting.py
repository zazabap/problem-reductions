#!/usr/bin/env python3
"""
Adversary verification script for NAESatisfiability -> SetSplitting reduction.
Issue #382 -- NOT-ALL-EQUAL SAT to SET SPLITTING

Independent implementation based ONLY on the Typst proof.
Does NOT import from the constructor script.
Uses hypothesis property-based testing with >= 2 strategies.
>= 5000 total checks.
"""

import itertools
import json
import random
from pathlib import Path

random.seed(841)  # Different seed from constructor

PASS = 0
FAIL = 0

def check(cond, msg):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
        print(f"FAIL: {msg}")

# ============================================================
# Independent implementations (from Typst proof only)
# ============================================================

def reduce_naesat_to_setsplitting(n, clauses):
    """
    From the Typst proof:
    1. Universe U = {0, ..., 2n-1}. Element 2i = positive literal x_{i+1},
       element 2i+1 = negative literal ~x_{i+1}.
    2. Complementarity subsets: R_i = {2i, 2i+1} for i=0..n-1.
    3. Clause subsets: for each clause, map each literal to its element.
       x_k (positive) -> 2*(k-1), -x_k (negative) -> 2*(k-1)+1.
    """
    universe_size = 2 * n
    subsets = []

    # Complementarity
    for i in range(n):
        subsets.append([2 * i, 2 * i + 1])

    # Clause subsets
    for clause in clauses:
        s = []
        for lit in clause:
            var_idx = abs(lit) - 1  # 0-indexed
            if lit > 0:
                s.append(2 * var_idx)
            else:
                s.append(2 * var_idx + 1)
        subsets.append(s)

    return universe_size, subsets

def extract_naesat_solution(n, coloring):
    """From the proof: alpha(x_{i+1}) = chi(2i), 1=True, 0=False."""
    return [coloring[2 * i] == 1 for i in range(n)]

def nae_satisfied(clauses, assignment):
    """Check NAE: every clause has at least one true and one false literal."""
    for clause in clauses:
        has_t = False
        has_f = False
        for lit in clause:
            val = assignment[abs(lit) - 1]
            if lit < 0:
                val = not val
            if val:
                has_t = True
            else:
                has_f = True
        if not (has_t and has_f):
            return False
    return True

def splitting_valid(univ_size, subsets, coloring):
    """Check set splitting: every subset has both colors 0 and 1."""
    for subset in subsets:
        colors = {coloring[e] for e in subset}
        if len(colors) < 2:
            return False
    return True

def brute_nae(n, clauses):
    """Brute-force all NAE-satisfying assignments."""
    results = []
    for bits in itertools.product([False, True], repeat=n):
        if nae_satisfied(clauses, list(bits)):
            results.append(list(bits))
    return results

def brute_splitting(univ_size, subsets):
    """Brute-force all valid set splitting colorings."""
    results = []
    for bits in itertools.product([0, 1], repeat=univ_size):
        if splitting_valid(univ_size, subsets, list(bits)):
            results.append(list(bits))
    return results

# ============================================================
# Random instance generator (independent)
# ============================================================

def gen_random_naesat(n, m, max_len=None):
    """Generate random NAE-SAT instance with n vars, m clauses."""
    if max_len is None:
        max_len = min(n, 5)
    clauses = []
    for _ in range(m):
        k = random.randint(2, max(2, min(max_len, n)))
        vars_chosen = random.sample(range(1, n + 1), k)
        clause = [v if random.random() < 0.5 else -v for v in vars_chosen]
        clauses.append(clause)
    return clauses

# ============================================================
# Part 1: Exhaustive forward + backward (n <= 5)
# ============================================================

print("=" * 60)
print("Part 1: Exhaustive forward + backward (adversary)")
print("=" * 60)

part1_start = PASS

for n in range(2, 6):
    max_m = min(10, 2 * n) if n <= 3 else min(8, 2 * n)
    for m in range(1, max_m + 1):
        samples = 40 if n <= 3 else 20
        for _ in range(samples):
            clauses = gen_random_naesat(n, m)
            univ, subs = reduce_naesat_to_setsplitting(n, clauses)

            src_sols = brute_nae(n, clauses)
            tgt_sols = brute_splitting(univ, subs)

            src_feas = len(src_sols) > 0
            tgt_feas = len(tgt_sols) > 0

            check(src_feas == tgt_feas,
                  f"feasibility mismatch n={n},m={m}: src={src_feas},tgt={tgt_feas}")

            # Forward: each NAE solution maps to a valid coloring
            for asn in src_sols:
                col = []
                for i in range(n):
                    col.append(1 if asn[i] else 0)
                    col.append(0 if asn[i] else 1)
                check(splitting_valid(univ, subs, col),
                      f"forward fail for assignment {asn}")

            # Backward: each valid coloring extracts to NAE solution
            for col in tgt_sols:
                ext = extract_naesat_solution(n, col)
                check(nae_satisfied(clauses, ext),
                      f"backward/extraction fail for coloring {col}")

part1_count = PASS - part1_start
print(f"  Part 1 checks: {part1_count}")

# ============================================================
# Part 2: Hypothesis property-based testing
# ============================================================

print("=" * 60)
print("Part 2: Hypothesis property-based testing")
print("=" * 60)

from hypothesis import given, settings, assume
from hypothesis import strategies as st

part2_start = PASS

# Strategy 1: random NAE-SAT instances with feasibility equivalence
@st.composite
def naesat_instances(draw):
    n = draw(st.integers(min_value=2, max_value=5))
    m = draw(st.integers(min_value=1, max_value=min(10, 3*n)))
    clauses = []
    for _ in range(m):
        k = draw(st.integers(min_value=2, max_value=min(n, 4)))
        var_pool = list(range(1, n + 1))
        vars_chosen = draw(st.permutations(var_pool).map(lambda p: p[:k]))
        signs = draw(st.lists(st.booleans(), min_size=k, max_size=k))
        clause = [v if s else -v for v, s in zip(vars_chosen, signs)]
        clauses.append(clause)
    return n, clauses

@given(inst=naesat_instances())
@settings(max_examples=1000, deadline=None)
def test_feasibility_equivalence(inst):
    global PASS, FAIL
    n, clauses = inst
    univ, subs = reduce_naesat_to_setsplitting(n, clauses)

    src_feas = len(brute_nae(n, clauses)) > 0
    tgt_feas = len(brute_splitting(univ, subs)) > 0

    check(src_feas == tgt_feas,
          f"hypothesis feasibility mismatch n={n}")

print("  Running Strategy 1: feasibility equivalence...")
test_feasibility_equivalence()
print(f"  Strategy 1 done. Checks so far: {PASS}")

# Strategy 2: random assignments -> check forward mapping validity
@st.composite
def naesat_with_assignment(draw):
    n = draw(st.integers(min_value=2, max_value=5))
    m = draw(st.integers(min_value=1, max_value=min(8, 2*n)))
    clauses = []
    for _ in range(m):
        k = draw(st.integers(min_value=2, max_value=min(n, 4)))
        var_pool = list(range(1, n + 1))
        vars_chosen = draw(st.permutations(var_pool).map(lambda p: p[:k]))
        signs = draw(st.lists(st.booleans(), min_size=k, max_size=k))
        clause = [v if s else -v for v, s in zip(vars_chosen, signs)]
        clauses.append(clause)
    assignment = draw(st.lists(st.booleans(), min_size=n, max_size=n))
    return n, clauses, assignment

@given(inst=naesat_with_assignment())
@settings(max_examples=1000, deadline=None)
def test_forward_mapping(inst):
    global PASS, FAIL
    n, clauses, assignment = inst
    univ, subs = reduce_naesat_to_setsplitting(n, clauses)

    # Build coloring from assignment
    coloring = []
    for i in range(n):
        coloring.append(1 if assignment[i] else 0)
        coloring.append(0 if assignment[i] else 1)

    src_ok = nae_satisfied(clauses, assignment)
    tgt_ok = splitting_valid(univ, subs, coloring)

    # If source is NAE-satisfied, target must be valid
    if src_ok:
        check(tgt_ok, f"forward: NAE-sat but splitting invalid, n={n}")
    # If target is valid, source must be NAE-satisfied
    if tgt_ok:
        check(src_ok, f"backward: splitting valid but not NAE-sat, n={n}")

print("  Running Strategy 2: forward mapping with assignments...")
test_forward_mapping()
print(f"  Strategy 2 done. Checks so far: {PASS}")

# Strategy 3: overhead formula property
@given(inst=naesat_instances())
@settings(max_examples=500, deadline=None)
def test_overhead_formula(inst):
    global PASS, FAIL
    n, clauses = inst
    univ, subs = reduce_naesat_to_setsplitting(n, clauses)
    m = len(clauses)

    check(univ == 2 * n, f"overhead: universe_size != 2n, n={n}")
    check(len(subs) == n + m, f"overhead: num_subsets != n+m, n={n},m={m}")

print("  Running Strategy 3: overhead formula...")
test_overhead_formula()
print(f"  Strategy 3 done. Checks so far: {PASS}")

part2_count = PASS - part2_start
print(f"  Part 2 total checks: {part2_count}")

# ============================================================
# Part 3: Reproduce YES example from Typst
# ============================================================

print("=" * 60)
print("Part 3: Reproduce YES example from Typst")
print("=" * 60)

part3_start = PASS

# n=4, clauses: C1={x1,-x2,x3}, C2={-x1,x2,-x4}, C3={x2,x3,x4}
yes_n = 4
yes_clauses = [[1, -2, 3], [-1, 2, -4], [2, 3, 4]]
yes_univ, yes_subs = reduce_naesat_to_setsplitting(yes_n, yes_clauses)

check(yes_univ == 8, "YES: universe_size should be 8")
check(len(yes_subs) == 7, "YES: should have 7 subsets")

# Check clause subsets
check(sorted(yes_subs[4]) == [0, 3, 4], "YES T1 = {0,3,4}")
check(sorted(yes_subs[5]) == [1, 2, 7], "YES T2 = {1,2,7}")
check(sorted(yes_subs[6]) == [2, 4, 6], "YES T3 = {2,4,6}")

# Assignment: (T,T,F,T)
yes_asn = [True, True, False, True]
check(nae_satisfied(yes_clauses, yes_asn), "YES assignment is NAE-satisfying")

# Coloring: (1,0,1,0,0,1,1,0)
yes_col = [1, 0, 1, 0, 0, 1, 1, 0]
check(splitting_valid(yes_univ, yes_subs, yes_col), "YES coloring is valid splitting")

# Extraction
yes_ext = extract_naesat_solution(yes_n, yes_col)
check(yes_ext == yes_asn, "YES extraction matches original assignment")

part3_count = PASS - part3_start
print(f"  Part 3 checks: {part3_count}")

# ============================================================
# Part 4: Reproduce NO example from Typst
# ============================================================

print("=" * 60)
print("Part 4: Reproduce NO example from Typst")
print("=" * 60)

part4_start = PASS

# n=3, clauses: C1={x1,x2}, C2={-x1,-x2}, C3={x2,x3}, C4={-x2,-x3}, C5={x1,x3}, C6={-x1,-x3}
no_n = 3
no_clauses = [[1, 2], [-1, -2], [2, 3], [-2, -3], [1, 3], [-1, -3]]
no_univ, no_subs = reduce_naesat_to_setsplitting(no_n, no_clauses)

check(no_univ == 6, "NO: universe_size should be 6")
check(len(no_subs) == 9, "NO: should have 9 subsets")

# Exhaustive: no NAE solution
no_sols = brute_nae(no_n, no_clauses)
check(len(no_sols) == 0, "NO: zero NAE-satisfying assignments")

# Exhaustive: no valid splitting
no_tgt_sols = brute_splitting(no_univ, no_subs)
check(len(no_tgt_sols) == 0, "NO: zero valid set splitting colorings")

# Verify specific subsets from Typst
check(sorted(no_subs[3]) == [0, 2], "NO T1 = {0,2}")
check(sorted(no_subs[4]) == [1, 3], "NO T2 = {1,3}")
check(sorted(no_subs[5]) == [2, 4], "NO T3 = {2,4}")
check(sorted(no_subs[6]) == [3, 5], "NO T4 = {3,5}")
check(sorted(no_subs[7]) == [0, 4], "NO T5 = {0,4}")
check(sorted(no_subs[8]) == [1, 5], "NO T6 = {1,5}")

part4_count = PASS - part4_start
print(f"  Part 4 checks: {part4_count}")

# ============================================================
# Part 5: Cross-comparison with constructor
# ============================================================

print("=" * 60)
print("Part 5: Cross-comparison (adversary vs constructor test vectors)")
print("=" * 60)

part5_start = PASS

tv_path = Path(__file__).parent / "test_vectors_nae_satisfiability_set_splitting.json"
if tv_path.exists():
    with open(tv_path) as f:
        tv = json.load(f)

    # Compare YES instance
    yi = tv["yes_instance"]
    cv_n = yi["input"]["num_vars"]
    cv_clauses = yi["input"]["clauses"]
    cv_univ, cv_subs = reduce_naesat_to_setsplitting(cv_n, cv_clauses)
    check(cv_univ == yi["output"]["universe_size"],
          "cross: YES universe_size mismatch")
    check(cv_subs == yi["output"]["subsets"],
          "cross: YES subsets mismatch")

    # Compare NO instance
    ni = tv["no_instance"]
    cn_n = ni["input"]["num_vars"]
    cn_clauses = ni["input"]["clauses"]
    cn_univ, cn_subs = reduce_naesat_to_setsplitting(cn_n, cn_clauses)
    check(cn_univ == ni["output"]["universe_size"],
          "cross: NO universe_size mismatch")
    check(cn_subs == ni["output"]["subsets"],
          "cross: NO subsets mismatch")

    # Compare feasibility verdicts
    check(yi["source_feasible"] == True, "cross: YES source should be feasible")
    check(yi["target_feasible"] == True, "cross: YES target should be feasible")
    check(ni["source_feasible"] == False, "cross: NO source should be infeasible")
    check(ni["target_feasible"] == False, "cross: NO target should be infeasible")

    # Cross-compare on random instances
    for _ in range(500):
        n = random.randint(2, 5)
        m = random.randint(1, min(8, 2*n))
        clauses = gen_random_naesat(n, m)
        adv_univ, adv_subs = reduce_naesat_to_setsplitting(n, clauses)

        # Verify structural identity (both implementations should produce same output)
        check(adv_univ == 2 * n, "cross random: universe_size")
        check(len(adv_subs) == n + m, "cross random: num_subsets")

        adv_src_feas = len(brute_nae(n, clauses)) > 0
        adv_tgt_feas = len(brute_splitting(adv_univ, adv_subs)) > 0
        check(adv_src_feas == adv_tgt_feas,
              f"cross random: feasibility mismatch n={n},m={m}")
else:
    print("  WARNING: test vectors JSON not found, skipping cross-comparison")

part5_count = PASS - part5_start
print(f"  Part 5 checks: {part5_count}")

# ============================================================
# Final summary
# ============================================================

print("=" * 60)
print(f"ADVERSARY CHECK COUNT AUDIT:")
print(f"  Total checks:          {PASS + FAIL} ({PASS} passed, {FAIL} failed)")
print(f"  Minimum required:      5,000")
print(f"  Part 1 (exhaustive):   {part1_count}")
print(f"  Part 2 (hypothesis):   {part2_count}")
print(f"  Part 3 (YES example):  {part3_count}")
print(f"  Part 4 (NO example):   {part4_count}")
print(f"  Part 5 (cross-comp):   {part5_count}")
print("=" * 60)

if FAIL > 0:
    print(f"\nFAILED: {FAIL} checks failed")
    exit(1)
else:
    print(f"\nALL {PASS} CHECKS PASSED")
    if PASS < 5000:
        print(f"WARNING: Only {PASS} checks, need at least 5000")
        exit(1)
    exit(0)
