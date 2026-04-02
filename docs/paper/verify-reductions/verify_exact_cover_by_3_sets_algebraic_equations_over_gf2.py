#!/usr/bin/env python3
"""
Constructor verification script for ExactCoverBy3Sets -> AlgebraicEquationsOverGF2.
Issue #859.

7 mandatory sections, >= 5000 total checks.
"""

import itertools
import json
import random
import sys
from collections import defaultdict

# ---------------------------------------------------------------------------
# Reduction implementation
# ---------------------------------------------------------------------------

def reduce(universe_size, subsets):
    """
    Reduce X3C to AlgebraicEquationsOverGF2.

    Args:
        universe_size: size of universe (must be divisible by 3)
        subsets: list of 3-element tuples/lists, 0-indexed

    Returns:
        (num_variables, equations) where equations is list of polynomials,
        each polynomial is a list of monomials, each monomial is a sorted
        list of variable indices. Empty list = constant 1.
    """
    n = len(subsets)
    element_to_sets = defaultdict(list)
    for j, subset in enumerate(subsets):
        for elem in subset:
            element_to_sets[elem].append(j)

    equations = []
    for i in range(universe_size):
        s_i = element_to_sets[i]
        # Linear covering constraint: sum_{j in S_i} x_j + 1 = 0
        linear_eq = [[j] for j in s_i] + [[]]
        equations.append(linear_eq)

        # Pairwise exclusion: x_j * x_k = 0 for all pairs
        for a_idx in range(len(s_i)):
            for b_idx in range(a_idx + 1, len(s_i)):
                j, k = s_i[a_idx], s_i[b_idx]
                pairwise_eq = [sorted([j, k])]
                equations.append(pairwise_eq)

    return n, equations


def evaluate_gf2(num_variables, equations, assignment):
    """Evaluate all GF(2) equations. Returns True if all satisfied."""
    for eq in equations:
        val = 0
        for mono in eq:
            if len(mono) == 0:
                val ^= 1
            else:
                prod = 1
                for var in mono:
                    prod &= assignment[var]
                val ^= prod
        if val != 0:
            return False
    return True


def is_exact_cover(universe_size, subsets, config):
    """Check if config (list of 0/1) selects an exact cover."""
    if len(config) != len(subsets):
        return False
    q = universe_size // 3
    selected = [i for i, v in enumerate(config) if v == 1]
    if len(selected) != q:
        return False
    covered = set()
    for idx in selected:
        for elem in subsets[idx]:
            if elem in covered:
                return False
            covered.add(elem)
    return len(covered) == universe_size


def extract_solution(assignment):
    """Extract X3C solution from GF(2) solution. Direct identity mapping."""
    return list(assignment)


def brute_force_x3c(universe_size, subsets):
    """Find all exact covers by brute force."""
    n = len(subsets)
    solutions = []
    for bits in itertools.product([0, 1], repeat=n):
        config = list(bits)
        if is_exact_cover(universe_size, subsets, config):
            solutions.append(config)
    return solutions


def brute_force_gf2(num_variables, equations):
    """Find all satisfying assignments for GF(2) system."""
    solutions = []
    for bits in itertools.product([0, 1], repeat=num_variables):
        assignment = list(bits)
        if evaluate_gf2(num_variables, equations, assignment):
            solutions.append(assignment)
    return solutions


# ---------------------------------------------------------------------------
# Instance generators
# ---------------------------------------------------------------------------

def generate_all_x3c_small(universe_size, max_num_subsets):
    """Generate all X3C instances for a given universe size, up to max_num_subsets subsets."""
    elements = list(range(universe_size))
    all_triples = list(itertools.combinations(elements, 3))
    instances = []
    for num_subsets in range(1, min(max_num_subsets + 1, len(all_triples) + 1)):
        for chosen in itertools.combinations(all_triples, num_subsets):
            subsets = [list(t) for t in chosen]
            instances.append((universe_size, subsets))
    return instances


def generate_random_x3c(universe_size, num_subsets, rng):
    """Generate a random X3C instance."""
    elements = list(range(universe_size))
    subsets = []
    for _ in range(num_subsets):
        triple = sorted(rng.sample(elements, 3))
        subsets.append(triple)
    return universe_size, subsets


# ---------------------------------------------------------------------------
# Section 1: Symbolic verification
# ---------------------------------------------------------------------------

def section_1_symbolic():
    """Verify overhead formulas symbolically."""
    print("=== Section 1: Symbolic verification ===")
    checks = 0

    # Overhead: num_variables = num_subsets
    # num_equations = universe_size + sum of C(|S_i|, 2) for each element
    for universe_size in [3, 6, 9, 12, 15]:
        for n_subsets in range(1, 10):
            rng = random.Random(universe_size * 100 + n_subsets)
            elems = list(range(universe_size))
            subsets = [sorted(rng.sample(elems, 3)) for _ in range(n_subsets)]

            n_vars, equations = reduce(universe_size, subsets)

            # num_variables = n
            assert n_vars == n_subsets, f"num_variables mismatch: {n_vars} != {n_subsets}"
            checks += 1

            # Count expected equations
            element_to_sets = defaultdict(list)
            for j, s in enumerate(subsets):
                for elem in s:
                    element_to_sets[elem].append(j)

            expected_linear = universe_size
            expected_pairwise = sum(
                len(s_i) * (len(s_i) - 1) // 2
                for s_i in element_to_sets.values()
            )
            expected_total = expected_linear + expected_pairwise

            assert len(equations) == expected_total, (
                f"num_equations mismatch for u={universe_size}, n={n_subsets}: "
                f"{len(equations)} != {expected_total}"
            )
            checks += 1

    # Verify overhead formula identity: for each element with d_i sets,
    # we get 1 linear + C(d_i,2) pairwise equations
    for _ in range(200):
        rng_test = random.Random(checks)
        universe_size = rng_test.choice([3, 6, 9])
        n_sub = rng_test.randint(1, 7)
        elems = list(range(universe_size))
        subsets = [sorted(rng_test.sample(elems, 3)) for _ in range(n_sub)]

        n_vars, equations = reduce(universe_size, subsets)
        element_to_sets = defaultdict(list)
        for j, s in enumerate(subsets):
            for elem in s:
                element_to_sets[elem].append(j)

        # Verify equation-by-equation structure
        eq_idx = 0
        for i in range(universe_size):
            d_i = len(element_to_sets[i])
            # Linear equation has d_i variable monomials + 1 constant
            assert len(equations[eq_idx]) == d_i + 1
            checks += 1
            eq_idx += 1
            # Pairwise equations
            for _ in range(d_i * (d_i - 1) // 2):
                assert len(equations[eq_idx]) == 1  # single product monomial
                assert len(equations[eq_idx][0]) == 2  # exactly 2 variables
                checks += 1
                eq_idx += 1
        assert eq_idx == len(equations)
        checks += 1

    print(f"  Symbolic checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 2: Exhaustive forward + backward
# ---------------------------------------------------------------------------

def section_2_exhaustive():
    """Exhaustive forward+backward: source feasible <=> target feasible for n<=5."""
    print("=== Section 2: Exhaustive forward + backward ===")
    checks = 0

    # Exhaustive for universe_size=3 (all possible subset collections up to 4 subsets)
    instances_3 = generate_all_x3c_small(3, 4)
    print(f"  universe_size=3: {len(instances_3)} instances")
    for universe_size, subsets in instances_3:
        n = len(subsets)
        source_feasible = len(brute_force_x3c(universe_size, subsets)) > 0
        num_vars, equations = reduce(universe_size, subsets)
        target_feasible = len(brute_force_gf2(num_vars, equations)) > 0
        assert source_feasible == target_feasible, (
            f"Mismatch u={universe_size}, subsets={subsets}: "
            f"source={source_feasible}, target={target_feasible}"
        )
        checks += 1

    # Exhaustive for universe_size=6 (up to 5 subsets)
    instances_6 = generate_all_x3c_small(6, 5)
    print(f"  universe_size=6: {len(instances_6)} instances")
    for universe_size, subsets in instances_6:
        n = len(subsets)
        if n > 8:
            continue
        source_feasible = len(brute_force_x3c(universe_size, subsets)) > 0
        num_vars, equations = reduce(universe_size, subsets)
        target_feasible = len(brute_force_gf2(num_vars, equations)) > 0
        assert source_feasible == target_feasible, (
            f"Mismatch u={universe_size}, subsets={subsets}: "
            f"source={source_feasible}, target={target_feasible}"
        )
        checks += 1

    # Random instances for universe_size=9,12,15 (limited brute force)
    rng = random.Random(42)
    for _ in range(1000):
        universe_size = rng.choice([3, 6, 9])
        max_sub = {3: 5, 6: 6, 9: 5}[universe_size]
        n_subsets = rng.randint(1, max_sub)
        u, subsets = generate_random_x3c(universe_size, n_subsets, rng)

        source_feasible = len(brute_force_x3c(u, subsets)) > 0
        num_vars, equations = reduce(u, subsets)
        target_feasible = len(brute_force_gf2(num_vars, equations)) > 0
        assert source_feasible == target_feasible, (
            f"Random mismatch u={u}, subsets={subsets}"
        )
        checks += 1

    print(f"  Exhaustive checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 3: Solution extraction
# ---------------------------------------------------------------------------

def section_3_extraction():
    """Extract source solution from every feasible target witness."""
    print("=== Section 3: Solution extraction ===")
    checks = 0

    # Check all instances from section 2 that are feasible
    for universe_size in [3, 6]:
        max_sub = {3: 4, 6: 5}[universe_size]
        instances = generate_all_x3c_small(universe_size, max_sub)
        for u, subsets in instances:
            n = len(subsets)
            if n > 8:
                continue
            source_solutions = brute_force_x3c(u, subsets)
            if not source_solutions:
                continue

            num_vars, equations = reduce(u, subsets)
            target_solutions = brute_force_gf2(num_vars, equations)

            # Every target solution must extract to a valid X3C cover
            for t_sol in target_solutions:
                extracted = extract_solution(t_sol)
                assert is_exact_cover(u, subsets, extracted), (
                    f"Extracted not valid: u={u}, subsets={subsets}, t_sol={t_sol}"
                )
                checks += 1

            # Number of target solutions must equal number of source solutions
            # (bijection: the variables are the same)
            source_set = {tuple(s) for s in source_solutions}
            target_set = {tuple(s) for s in target_solutions}
            assert source_set == target_set, (
                f"Solution sets differ: u={u}, subsets={subsets}"
            )
            checks += 1

    # Random feasible instances
    rng = random.Random(999)
    for _ in range(500):
        universe_size = rng.choice([3, 6, 9])
        n_subsets = rng.randint(1, min(5, 2 * universe_size // 3 + 2))
        u, subsets = generate_random_x3c(universe_size, n_subsets, rng)

        source_solutions = brute_force_x3c(u, subsets)
        if not source_solutions:
            continue

        num_vars, equations = reduce(u, subsets)
        target_solutions = brute_force_gf2(num_vars, equations)

        for t_sol in target_solutions:
            extracted = extract_solution(t_sol)
            assert is_exact_cover(u, subsets, extracted)
            checks += 1

    print(f"  Extraction checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 4: Overhead formula
# ---------------------------------------------------------------------------

def section_4_overhead():
    """Build target, measure actual size, compare against formula."""
    print("=== Section 4: Overhead formula ===")
    checks = 0

    rng = random.Random(456)
    for _ in range(1500):
        universe_size = rng.choice([3, 6, 9, 12, 15])
        n_subsets = rng.randint(1, min(10, 3 * universe_size))
        elems = list(range(universe_size))
        subsets = [sorted(rng.sample(elems, 3)) for _ in range(n_subsets)]

        num_vars, equations = reduce(universe_size, subsets)

        # num_variables = n
        assert num_vars == n_subsets
        checks += 1

        # num_equations = universe_size + sum C(d_i, 2)
        element_to_sets = defaultdict(list)
        for j, s in enumerate(subsets):
            for elem in s:
                element_to_sets[elem].append(j)

        expected_eq = universe_size + sum(
            len(s_i) * (len(s_i) - 1) // 2
            for s_i in element_to_sets.values()
        )
        assert len(equations) == expected_eq
        checks += 1

        # Verify equation structure detail
        eq_idx = 0
        for i in range(universe_size):
            s_i = element_to_sets[i]
            eq = equations[eq_idx]
            # Linear: |S_i| variable terms + 1 constant
            assert len(eq) == len(s_i) + 1
            assert eq[-1] == []  # constant 1
            for t, j in enumerate(s_i):
                assert eq[t] == [j]  # single variable monomial
            checks += 1
            eq_idx += 1

            # Pairwise: C(|S_i|, 2) equations
            pair_count = 0
            for a in range(len(s_i)):
                for b in range(a + 1, len(s_i)):
                    eq = equations[eq_idx]
                    assert eq == [sorted([s_i[a], s_i[b]])]
                    checks += 1
                    eq_idx += 1
                    pair_count += 1

    print(f"  Overhead checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 5: Structural properties
# ---------------------------------------------------------------------------

def section_5_structural():
    """Target well-formed, no degenerate cases."""
    print("=== Section 5: Structural properties ===")
    checks = 0

    rng = random.Random(789)
    for _ in range(800):
        universe_size = rng.choice([3, 6, 9, 12, 15])
        n_subsets = rng.randint(1, min(10, 3 * universe_size))
        elems = list(range(universe_size))
        subsets = [sorted(rng.sample(elems, 3)) for _ in range(n_subsets)]

        num_vars, equations = reduce(universe_size, subsets)

        # All variable indices in range
        for eq in equations:
            for mono in eq:
                for var in mono:
                    assert 0 <= var < num_vars, f"Variable {var} out of range"
                    checks += 1

        # Monomials sorted
        for eq in equations:
            for mono in eq:
                for w in range(len(mono) - 1):
                    assert mono[w] < mono[w + 1]
                    checks += 1

        # No duplicate variables in any monomial
        for eq in equations:
            for mono in eq:
                assert len(mono) == len(set(mono))
                checks += 1

        # Max degree is 2 (product terms)
        for eq in equations:
            for mono in eq:
                assert len(mono) <= 2
                checks += 1

        # At least universe_size equations (one linear per element)
        assert len(equations) >= universe_size
        checks += 1

    print(f"  Structural checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 6: YES example
# ---------------------------------------------------------------------------

def section_6_yes_example():
    """Reproduce exact Typst feasible example numbers."""
    print("=== Section 6: YES example ===")
    checks = 0

    # From Typst: X = {0,...,8}, q=3
    # C1={0,1,2}, C2={3,4,5}, C3={6,7,8}, C4={0,3,6}
    universe_size = 9
    subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6]]

    num_vars, equations = reduce(universe_size, subsets)

    # num_variables = 4
    assert num_vars == 4, f"Expected 4 variables, got {num_vars}"
    checks += 1

    # 9 linear + 3 pairwise = 12 equations
    assert len(equations) == 12, f"Expected 12 equations, got {len(equations)}"
    checks += 1

    # Satisfying assignment (1,1,1,0) = select C1, C2, C3
    assignment = [1, 1, 1, 0]
    assert evaluate_gf2(num_vars, equations, assignment)
    checks += 1

    assert is_exact_cover(universe_size, subsets, assignment)
    checks += 1

    # Verify specific equations from Typst:
    # Element 0 (in C1=0, C4=3): linear [[0],[3],[]]
    assert equations[0] == [[0], [3], []]
    checks += 1
    # Element 0 pairwise: [[0,3]]
    assert equations[1] == [[0, 3]]
    checks += 1

    # Element 1 (in C1=0): linear [[0],[]]
    assert equations[2] == [[0], []]
    checks += 1

    # Element 2 (in C1=0): linear [[0],[]]
    assert equations[3] == [[0], []]
    checks += 1

    # Element 3 (in C2=1, C4=3): linear [[1],[3],[]]
    assert equations[4] == [[1], [3], []]
    checks += 1
    # Pairwise [[1,3]]
    assert equations[5] == [[1, 3]]
    checks += 1

    # Element 4 (in C2=1): linear [[1],[]]
    assert equations[6] == [[1], []]
    checks += 1

    # Element 5 (in C2=1): linear [[1],[]]
    assert equations[7] == [[1], []]
    checks += 1

    # Element 6 (in C3=2, C4=3): linear [[2],[3],[]]
    assert equations[8] == [[2], [3], []]
    checks += 1
    # Pairwise [[2,3]]
    assert equations[9] == [[2, 3]]
    checks += 1

    # Element 7 (in C3=2): linear [[2],[]]
    assert equations[10] == [[2], []]
    checks += 1

    # Element 8 (in C3=2): linear [[2],[]]
    assert equations[11] == [[2], []]
    checks += 1

    # Verify (0,0,0,1) fails
    assert not evaluate_gf2(num_vars, equations, [0, 0, 0, 1])
    checks += 1

    # Verify (1,1,1,1) fails (pairwise violated)
    assert not evaluate_gf2(num_vars, equations, [1, 1, 1, 1])
    checks += 1

    # Verify (0,0,0,0) fails
    assert not evaluate_gf2(num_vars, equations, [0, 0, 0, 0])
    checks += 1

    # Verify all 16 assignments, only (1,1,1,0) satisfies
    sat_count = 0
    for bits in itertools.product([0, 1], repeat=4):
        a = list(bits)
        if evaluate_gf2(num_vars, equations, a):
            assert a == [1, 1, 1, 0]
            sat_count += 1
        checks += 1

    assert sat_count == 1
    checks += 1

    print(f"  YES example checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Section 7: NO example
# ---------------------------------------------------------------------------

def section_7_no_example():
    """Reproduce exact Typst infeasible example, verify both sides infeasible."""
    print("=== Section 7: NO example ===")
    checks = 0

    # From Typst: X = {0,...,8}, q=3
    # C1={0,1,2}, C2={0,3,4}, C3={0,5,6}, C4={3,7,8}
    universe_size = 9
    subsets = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [3, 7, 8]]

    # Verify no exact cover
    source_solutions = brute_force_x3c(universe_size, subsets)
    assert len(source_solutions) == 0
    checks += 1

    num_vars, equations = reduce(universe_size, subsets)

    # Verify no GF(2) solution
    target_solutions = brute_force_gf2(num_vars, equations)
    assert len(target_solutions) == 0
    checks += 1

    assert num_vars == 4
    checks += 1

    # From Typst: elements 1,2 force x1=1, element 4 forces x2=1,
    # elements 5,6 force x3=1, elements 7,8 force x4=1
    # Then pairwise x1*x2 = 1*1 = 1 != 0 violates

    # Check (1,1,1,1) violates pairwise
    assert not evaluate_gf2(num_vars, equations, [1, 1, 1, 1])
    checks += 1

    # Check all 16 assignments
    for bits in itertools.product([0, 1], repeat=4):
        a = list(bits)
        assert not evaluate_gf2(num_vars, equations, a)
        checks += 1

    # Verify structure: element 0 is in C1(0), C2(1), C3(2)
    # Linear: [[0],[1],[2],[]]
    assert equations[0] == [[0], [1], [2], []]
    checks += 1
    # Pairwise: [[0,1]], [[0,2]], [[1,2]]
    assert equations[1] == [[0, 1]]
    checks += 1
    assert equations[2] == [[0, 2]]
    checks += 1
    assert equations[3] == [[1, 2]]
    checks += 1

    print(f"  NO example checks: {checks}")
    return checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    total_checks = 0

    c1 = section_1_symbolic()
    total_checks += c1

    c2 = section_2_exhaustive()
    total_checks += c2

    c3 = section_3_extraction()
    total_checks += c3

    c4 = section_4_overhead()
    total_checks += c4

    c5 = section_5_structural()
    total_checks += c5

    c6 = section_6_yes_example()
    total_checks += c6

    c7 = section_7_no_example()
    total_checks += c7

    print(f"\n{'='*60}")
    print(f"CHECK COUNT AUDIT:")
    print(f"  Total checks:          {total_checks} (minimum: 5,000)")
    print(f"  Section 1 (symbolic):  {c1}")
    print(f"  Section 2 (exhaustive):{c2}")
    print(f"  Section 3 (extraction):{c3}")
    print(f"  Section 4 (overhead):  {c4}")
    print(f"  Section 5 (structural):{c5}")
    print(f"  Section 6 (YES):       {c6}")
    print(f"  Section 7 (NO):        {c7}")
    print(f"{'='*60}")

    if total_checks < 5000:
        print(f"FAIL: Total checks {total_checks} < 5000 minimum!")
        sys.exit(1)

    print("ALL CHECKS PASSED")

    # Export test vectors
    export_test_vectors()


def export_test_vectors():
    """Export test vectors JSON."""
    # YES instance
    yes_universe = 9
    yes_subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6]]
    yes_num_vars, yes_equations = reduce(yes_universe, yes_subsets)
    yes_assignment = [1, 1, 1, 0]

    # NO instance
    no_universe = 9
    no_subsets = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [3, 7, 8]]
    no_num_vars, no_equations = reduce(no_universe, no_subsets)

    test_vectors = {
        "source": "ExactCoverBy3Sets",
        "target": "AlgebraicEquationsOverGF2",
        "issue": 859,
        "yes_instance": {
            "input": {
                "universe_size": yes_universe,
                "subsets": yes_subsets
            },
            "output": {
                "num_variables": yes_num_vars,
                "equations": yes_equations
            },
            "source_feasible": True,
            "target_feasible": True,
            "source_solution": yes_assignment,
            "extracted_solution": yes_assignment
        },
        "no_instance": {
            "input": {
                "universe_size": no_universe,
                "subsets": no_subsets
            },
            "output": {
                "num_variables": no_num_vars,
                "equations": no_equations
            },
            "source_feasible": False,
            "target_feasible": False
        },
        "overhead": {
            "num_variables": "num_subsets",
            "num_equations": "universe_size + sum(C(|S_i|, 2) for each element)"
        },
        "claims": [
            {"tag": "variables_equal_subsets", "formula": "num_variables = num_subsets", "verified": True},
            {"tag": "linear_constraints_per_element", "formula": "one linear eq per universe element", "verified": True},
            {"tag": "pairwise_exclusion", "formula": "C(|S_i|,2) product eqs per element", "verified": True},
            {"tag": "forward_direction", "formula": "exact cover => GF2 satisfiable", "verified": True},
            {"tag": "backward_direction", "formula": "GF2 satisfiable => exact cover", "verified": True},
            {"tag": "solution_extraction", "formula": "target assignment = source config", "verified": True},
            {"tag": "odd_plus_at_most_one_equals_exactly_one", "formula": "odd count + no pair => exactly one", "verified": True}
        ]
    }

    import os
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_vectors_exact_cover_by_3_sets_algebraic_equations_over_gf2.json"
    )
    with open(out_path, "w") as f:
        json.dump(test_vectors, f, indent=2)
    print(f"Test vectors exported to {out_path}")


if __name__ == "__main__":
    main()
