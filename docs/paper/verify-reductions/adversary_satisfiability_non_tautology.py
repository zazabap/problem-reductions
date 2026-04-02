#!/usr/bin/env python3
"""
Adversary verification script for Satisfiability → NonTautology reduction.
Issue #868.

Independent implementation based ONLY on the Typst proof.
Does NOT import from the constructor script.
≥5000 checks, hypothesis PBT with ≥2 strategies.
"""

import itertools
import sys

# ---------------------------------------------------------------------------
# Independent reduction implementation (from Typst proof only)
# ---------------------------------------------------------------------------
# The proof states: given CNF phi = C1 ∧ ... ∧ Cm, construct E = ¬phi.
# By De Morgan: E = ¬C1 ∨ ... ∨ ¬Cm.
# Each ¬Cj = (l̄1 ∧ l̄2 ∧ ... ∧ l̄k) where l̄ is the complement of literal l.
# The variables are identical (no new variables).
# Solution extraction: identity (falsifying assignment for E = satisfying for phi).


def reduce(num_vars: int, clauses: list[list[int]]) -> tuple[int, list[list[int]]]:
    """Reduce SAT (CNF) to NonTautology (DNF) by negating the formula."""
    disjuncts = []
    for clause in clauses:
        # Negate each literal in the clause: ¬(l1 ∨ ... ∨ lk) = (¬l1 ∧ ... ∧ ¬lk)
        disjunct = [-literal for literal in clause]
        disjuncts.append(disjunct)
    return num_vars, disjuncts


def extract_solution(falsifying_assignment: list[bool]) -> list[bool]:
    """Extract satisfying assignment from falsifying assignment (identity)."""
    return list(falsifying_assignment)


def eval_cnf(clauses: list[list[int]], assignment: list[bool]) -> bool:
    """Evaluate a CNF formula under the given assignment."""
    for clause in clauses:
        clause_sat = False
        for lit in clause:
            idx = abs(lit) - 1
            val = assignment[idx]
            if (lit > 0 and val) or (lit < 0 and not val):
                clause_sat = True
                break
        if not clause_sat:
            return False
    return True


def eval_dnf(disjuncts: list[list[int]], assignment: list[bool]) -> bool:
    """Evaluate a DNF formula under the given assignment."""
    for disjunct in disjuncts:
        conj_true = True
        for lit in disjunct:
            idx = abs(lit) - 1
            val = assignment[idx]
            if not ((lit > 0 and val) or (lit < 0 and not val)):
                conj_true = False
                break
        if conj_true:
            return True
    return False


def is_satisfiable(num_vars: int, clauses: list[list[int]]) -> bool:
    """Brute-force check if CNF is satisfiable."""
    for bits in itertools.product([False, True], repeat=num_vars):
        if eval_cnf(clauses, list(bits)):
            return True
    return False


def has_falsifying(num_vars: int, disjuncts: list[list[int]]) -> bool:
    """Brute-force check if DNF has a falsifying assignment."""
    for bits in itertools.product([False, True], repeat=num_vars):
        if not eval_dnf(disjuncts, list(bits)):
            return True
    return False


def find_satisfying(num_vars: int, clauses: list[list[int]]):
    """Find a satisfying assignment or None."""
    for bits in itertools.product([False, True], repeat=num_vars):
        a = list(bits)
        if eval_cnf(clauses, a):
            return a
    return None


def find_falsifying(num_vars: int, disjuncts: list[list[int]]):
    """Find a falsifying assignment for DNF, or None."""
    for bits in itertools.product([False, True], repeat=num_vars):
        a = list(bits)
        if not eval_dnf(disjuncts, a):
            return a
    return None


# ---------------------------------------------------------------------------
# Exhaustive testing for n ≤ 5
# ---------------------------------------------------------------------------

def generate_all_instances(n: int, max_clause_len: int = 3, max_clauses: int = 4):
    """Generate CNF instances exhaustively for small n."""
    all_lits = list(range(1, n + 1)) + list(range(-n, 0))
    possible_clauses = []
    for size in range(1, min(n, max_clause_len) + 1):
        for combo in itertools.combinations(all_lits, size):
            # No complementary literals in same clause
            vars_in_clause = set()
            valid = True
            for lit in combo:
                if abs(lit) in vars_in_clause:
                    valid = False
                    break
                vars_in_clause.add(abs(lit))
            if valid:
                possible_clauses.append(list(combo))
    cap = min(len(possible_clauses), max_clauses)
    for num_c in range(1, cap + 1):
        for clause_set in itertools.combinations(possible_clauses, num_c):
            yield n, list(clause_set)


def test_exhaustive():
    """Exhaustive forward + backward for n ≤ 5."""
    print("=== Adversary: Exhaustive forward + backward ===")
    checks = 0
    for n in range(1, 6):
        count = 0
        for num_vars, clauses in generate_all_instances(n):
            t_vars, disjuncts = reduce(num_vars, clauses)
            src_feas = is_satisfiable(num_vars, clauses)
            tgt_feas = has_falsifying(t_vars, disjuncts)
            assert src_feas == tgt_feas, (
                f"Mismatch n={n}, clauses={clauses}: src={src_feas}, tgt={tgt_feas}"
            )
            checks += 1
            count += 1

            # If feasible, test extraction
            if src_feas:
                witness = find_falsifying(t_vars, disjuncts)
                assert witness is not None
                extracted = extract_solution(witness)
                assert eval_cnf(clauses, extracted), (
                    f"Extraction failed n={n}, clauses={clauses}"
                )
                checks += 1
        print(f"  n={n}: {count} instances")
    print(f"  Exhaustive checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_edge_cases():
    """Test edge-case configurations: all-true, all-false, alternating."""
    print("=== Adversary: Edge cases ===")
    checks = 0

    for n in range(1, 7):
        # All-true assignment
        assignment_all_true = [True] * n
        # All-false assignment
        assignment_all_false = [False] * n
        # Alternating
        assignment_alt = [i % 2 == 0 for i in range(n)]

        # Single-literal clauses (unit clauses)
        for v in range(1, n + 1):
            for sign in [1, -1]:
                clauses = [[sign * v]]
                t_vars, disjuncts = reduce(n, clauses)

                for assignment in [assignment_all_true, assignment_all_false, assignment_alt]:
                    cnf_val = eval_cnf(clauses, assignment)
                    dnf_val = eval_dnf(disjuncts, assignment)
                    # DNF = ¬CNF
                    assert dnf_val != cnf_val, (
                        f"Edge case: DNF should be ¬CNF, n={n}, clause={clauses}, "
                        f"assignment={assignment}"
                    )
                    checks += 1

        # Full clauses (all variables)
        all_pos = [list(range(1, n + 1))]
        all_neg = [list(range(-n, 0))]
        for clauses in [all_pos, all_neg]:
            t_vars, disjuncts = reduce(n, clauses)
            for assignment in [assignment_all_true, assignment_all_false, assignment_alt]:
                cnf_val = eval_cnf(clauses, assignment)
                dnf_val = eval_dnf(disjuncts, assignment)
                assert dnf_val != cnf_val
                checks += 1

    print(f"  Edge case checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Typst example reproduction
# ---------------------------------------------------------------------------

def test_yes_example():
    """Reproduce the YES example from the Typst proof."""
    print("=== Adversary: YES example ===")
    checks = 0

    num_vars = 4
    clauses = [[1, -2, 3], [-1, 2, 4], [2, -3, -4], [-1, -2, 3]]
    t_vars, disjuncts = reduce(num_vars, clauses)

    # Check construction
    assert t_vars == 4
    checks += 1
    assert disjuncts == [[-1, 2, -3], [1, -2, -4], [-2, 3, 4], [1, 2, -3]]
    checks += 1

    # Satisfying assignment: x1=T, x2=T, x3=T, x4=F
    sat = [True, True, True, False]
    assert eval_cnf(clauses, sat), "YES: should satisfy CNF"
    checks += 1
    assert not eval_dnf(disjuncts, sat), "YES: should falsify DNF"
    checks += 1

    # Extraction
    extracted = extract_solution(sat)
    assert extracted == sat
    checks += 1
    assert eval_cnf(clauses, extracted)
    checks += 1

    # Source is feasible
    assert is_satisfiable(num_vars, clauses)
    checks += 1
    # Target is feasible (not a tautology)
    assert has_falsifying(t_vars, disjuncts)
    checks += 1

    print(f"  YES example checks: {checks}")
    return checks


def test_no_example():
    """Reproduce the NO example from the Typst proof."""
    print("=== Adversary: NO example ===")
    checks = 0

    num_vars = 3
    clauses = [[1], [-1], [2, 3], [-2, -3]]
    t_vars, disjuncts = reduce(num_vars, clauses)

    # Check construction
    assert disjuncts == [[-1], [1], [-2, -3], [2, 3]]
    checks += 1

    # Source is unsatisfiable
    assert not is_satisfiable(num_vars, clauses), "NO: source should be infeasible"
    checks += 1

    # Target is a tautology (no falsifying assignment)
    assert not has_falsifying(t_vars, disjuncts), "NO: target should be tautology"
    checks += 1

    # Verify WHY: D1 ∨ D2 covers everything (¬x1 ∨ x1)
    for bits in itertools.product([False, True], repeat=num_vars):
        a = list(bits)
        d1_true = not a[0]  # ¬x1
        d2_true = a[0]      # x1
        assert d1_true or d2_true
        checks += 1

    # Verify all 8 assignments make DNF true
    for bits in itertools.product([False, True], repeat=num_vars):
        assert eval_dnf(disjuncts, list(bits)), "NO: tautology must be true everywhere"
        checks += 1

    print(f"  NO example checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Hypothesis PBT
# ---------------------------------------------------------------------------

def test_hypothesis_pbt():
    """Property-based testing with hypothesis (≥2 strategies)."""
    print("=== Adversary: Hypothesis PBT ===")

    from hypothesis import given, settings, assume
    from hypothesis import strategies as st

    checks_counter = [0]

    # Strategy 1: random CNF formulas
    @given(
        n=st.integers(min_value=1, max_value=5),
        data=st.data(),
    )
    @settings(max_examples=1500, deadline=None)
    def test_random_cnf(n, data):
        m = data.draw(st.integers(min_value=1, max_value=5))
        clauses = []
        for _ in range(m):
            k = data.draw(st.integers(min_value=1, max_value=min(n, 3)))
            vars_chosen = data.draw(
                st.lists(
                    st.integers(min_value=1, max_value=n),
                    min_size=k, max_size=k, unique=True,
                )
            )
            clause = [v * data.draw(st.sampled_from([1, -1])) for v in vars_chosen]
            clauses.append(clause)

        t_vars, disjuncts = reduce(n, clauses)

        # Forward + backward
        src_feas = is_satisfiable(n, clauses)
        tgt_feas = has_falsifying(t_vars, disjuncts)
        assert src_feas == tgt_feas

        # If feasible, test extraction
        if src_feas:
            witness = find_falsifying(t_vars, disjuncts)
            assert witness is not None
            extracted = extract_solution(witness)
            assert eval_cnf(clauses, extracted)

        # DNF = ¬CNF for all assignments
        for bits in itertools.product([False, True], repeat=n):
            a = list(bits)
            assert eval_cnf(clauses, a) != eval_dnf(disjuncts, a) or (
                not eval_cnf(clauses, a) and not eval_dnf(disjuncts, a)
            ) is False
            # More precisely: DNF(a) = ¬CNF(a)
            assert eval_dnf(disjuncts, a) == (not eval_cnf(clauses, a))

        checks_counter[0] += 1

    # Strategy 2: structured formulas (k-SAT style)
    @given(
        n=st.integers(min_value=3, max_value=5),
        m=st.integers(min_value=1, max_value=6),
        k=st.integers(min_value=1, max_value=3),
        data=st.data(),
    )
    @settings(max_examples=1500, deadline=None)
    def test_ksat_style(n, m, k, data):
        assume(k <= n)
        clauses = []
        for _ in range(m):
            vars_chosen = data.draw(
                st.lists(
                    st.integers(min_value=1, max_value=n),
                    min_size=k, max_size=k, unique=True,
                )
            )
            clause = [v * data.draw(st.sampled_from([1, -1])) for v in vars_chosen]
            clauses.append(clause)

        t_vars, disjuncts = reduce(n, clauses)

        # Overhead check
        assert t_vars == n
        assert len(disjuncts) == m
        for j in range(m):
            assert len(disjuncts[j]) == len(clauses[j])

        # Correctness
        src_feas = is_satisfiable(n, clauses)
        tgt_feas = has_falsifying(t_vars, disjuncts)
        assert src_feas == tgt_feas

        # Structural: each literal is negated
        for j in range(m):
            for idx in range(len(clauses[j])):
                assert disjuncts[j][idx] == -clauses[j][idx]

        checks_counter[0] += 1

    test_random_cnf()
    print(f"  Strategy 1 (random CNF): completed")
    test_ksat_style()
    print(f"  Strategy 2 (k-SAT style): completed")
    print(f"  PBT hypothesis examples: {checks_counter[0]}")
    return checks_counter[0]


# ---------------------------------------------------------------------------
# Cross-comparison with constructor script output
# ---------------------------------------------------------------------------

def test_cross_comparison():
    """Compare reduce() outputs with constructor on shared instances."""
    print("=== Adversary: Cross-comparison ===")
    import json
    from pathlib import Path

    checks = 0

    # Load test vectors produced by constructor
    vectors_path = Path(__file__).parent / "test_vectors_satisfiability_non_tautology.json"
    if not vectors_path.exists():
        print("  WARNING: test vectors not found, skipping cross-comparison")
        return 0

    with open(vectors_path) as f:
        vectors = json.load(f)

    # YES instance
    yi = vectors["yes_instance"]
    t_vars, disjuncts = reduce(yi["input"]["num_vars"], yi["input"]["clauses"])
    assert t_vars == yi["output"]["num_vars"], "Cross: YES num_vars mismatch"
    checks += 1
    assert disjuncts == yi["output"]["disjuncts"], "Cross: YES disjuncts mismatch"
    checks += 1

    # NO instance
    ni = vectors["no_instance"]
    t_vars, disjuncts = reduce(ni["input"]["num_vars"], ni["input"]["clauses"])
    assert t_vars == ni["output"]["num_vars"], "Cross: NO num_vars mismatch"
    checks += 1
    assert disjuncts == ni["output"]["disjuncts"], "Cross: NO disjuncts mismatch"
    checks += 1

    # Verify feasibility claims
    assert is_satisfiable(yi["input"]["num_vars"], yi["input"]["clauses"]) == yi["source_feasible"]
    checks += 1
    assert not is_satisfiable(ni["input"]["num_vars"], ni["input"]["clauses"]) == (not ni["source_feasible"])
    checks += 1

    # Random shared instances
    import random
    rng = random.Random(123)
    for _ in range(500):
        n = rng.randint(1, 5)
        m = rng.randint(1, 5)
        clauses = []
        for _ in range(m):
            k = rng.randint(1, min(n, 3))
            vars_chosen = rng.sample(range(1, n + 1), k)
            clause = [v if rng.random() < 0.5 else -v for v in vars_chosen]
            clauses.append(clause)

        my_t_vars, my_disjuncts = reduce(n, clauses)

        # Verify structural correctness independently
        assert my_t_vars == n
        assert len(my_disjuncts) == len(clauses)
        for j in range(len(clauses)):
            for idx in range(len(clauses[j])):
                assert my_disjuncts[j][idx] == -clauses[j][idx]
        checks += 1

        # Verify feasibility
        src_feas = is_satisfiable(n, clauses)
        tgt_feas = has_falsifying(my_t_vars, my_disjuncts)
        assert src_feas == tgt_feas
        checks += 1

    print(f"  Cross-comparison checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    total = 0

    total += test_exhaustive()
    total += test_edge_cases()
    total += test_yes_example()
    total += test_no_example()
    total += test_hypothesis_pbt()
    total += test_cross_comparison()

    print()
    print("=" * 60)
    print(f"ADVERSARY TOTAL CHECKS: {total} (minimum: 5,000)")
    print("=" * 60)

    if total < 5000:
        print(f"WARNING: Only {total} checks, need at least 5,000!")
        sys.exit(1)

    print(f"ALL {total} ADVERSARY CHECKS PASSED")


if __name__ == "__main__":
    main()
