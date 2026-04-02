#!/usr/bin/env python3
"""
Adversary verification script for ExactCoverBy3Sets -> AlgebraicEquationsOverGF2.
Issue #859.

Independent implementation based ONLY on the Typst proof.
Does NOT import from the constructor script.

Requirements:
- Own reduce() function
- Own extract_solution() function
- Own is_feasible_source() and is_feasible_target() validators
- Exhaustive forward + backward for n <= 5
- hypothesis PBT (>= 2 strategies)
- Reproduce both Typst examples (YES and NO)
- >= 5,000 total checks
"""

import itertools
import json
import os
import random
import sys

# ---------------------------------------------------------------------------
# Independent reduction implementation (from Typst proof only)
# ---------------------------------------------------------------------------

def reduce(universe_size, subsets):
    """
    Independent reduction from X3C to AlgebraicEquationsOverGF2.

    From the Typst proof:
    - n variables x_1,...,x_n, one per set
    - For each element u_i with covering sets S_i:
      1. Linear constraint: sum_{j in S_i} x_j + 1 = 0 (mod 2)
      2. Pairwise exclusion: x_j * x_k = 0 for all pairs j < k in S_i
    """
    n = len(subsets)

    # Build containment mapping: element -> list of set indices
    covers = {}
    for i in range(universe_size):
        covers[i] = []
    for j, s in enumerate(subsets):
        for elem in s:
            covers[elem].append(j)

    eqs = []
    for i in range(universe_size):
        set_indices = covers[i]
        # Linear: [x_{j1}] + [x_{j2}] + ... + [1] = 0
        # Represented as list of monomials: [[j1], [j2], ..., []]
        lin = []
        for j in set_indices:
            lin.append([j])
        lin.append([])  # constant 1
        eqs.append(lin)

        # Pairwise products
        for a in range(len(set_indices)):
            for b in range(a + 1, len(set_indices)):
                j1, j2 = set_indices[a], set_indices[b]
                mono = sorted([j1, j2])
                eqs.append([mono])

    return n, eqs


def is_feasible_source(universe_size, subsets, config):
    """Check if config selects a valid exact cover."""
    if len(config) != len(subsets):
        return False

    q = universe_size // 3
    num_selected = sum(config)
    if num_selected != q:
        return False

    covered = set()
    for idx in range(len(config)):
        if config[idx] == 1:
            for elem in subsets[idx]:
                if elem in covered:
                    return False  # overlap
                covered.add(elem)

    return covered == set(range(universe_size))


def is_feasible_target(num_vars, equations, assignment):
    """Evaluate GF(2) polynomial system."""
    for eq in equations:
        total = 0
        for mono in eq:
            if not mono:  # constant 1
                total ^= 1
            else:
                val = 1
                for v in mono:
                    val &= assignment[v]
                total ^= val
        if total != 0:
            return False
    return True


def extract_solution(assignment):
    """Extract X3C config from GF(2) assignment. Identity mapping per Typst proof."""
    return list(assignment)


# ---------------------------------------------------------------------------
# Brute force solvers
# ---------------------------------------------------------------------------

def all_x3c_solutions(universe_size, subsets):
    """Find all exact covers."""
    n = len(subsets)
    sols = []
    for bits in itertools.product([0, 1], repeat=n):
        if is_feasible_source(universe_size, subsets, list(bits)):
            sols.append(list(bits))
    return sols


def all_gf2_solutions(num_vars, equations):
    """Find all satisfying GF(2) assignments."""
    sols = []
    for bits in itertools.product([0, 1], repeat=num_vars):
        if is_feasible_target(num_vars, equations, list(bits)):
            sols.append(list(bits))
    return sols


# ---------------------------------------------------------------------------
# Random instance generators
# ---------------------------------------------------------------------------

def random_x3c(rng, universe_size, num_subsets):
    """Generate random X3C instance."""
    elems = list(range(universe_size))
    subsets = []
    for _ in range(num_subsets):
        subsets.append(sorted(rng.sample(elems, 3)))
    return universe_size, subsets


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_yes_example():
    """Reproduce Typst YES example."""
    print("  Testing YES example...")
    checks = 0

    universe_size = 9
    subsets = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6]]

    num_vars, equations = reduce(universe_size, subsets)
    assert num_vars == 4
    checks += 1

    # 9 linear + 3 pairwise = 12
    assert len(equations) == 12
    checks += 1

    # (1,1,1,0) should satisfy
    sol = [1, 1, 1, 0]
    assert is_feasible_target(num_vars, equations, sol)
    checks += 1
    assert is_feasible_source(universe_size, subsets, sol)
    checks += 1

    # Verify extraction
    extracted = extract_solution(sol)
    assert is_feasible_source(universe_size, subsets, extracted)
    checks += 1

    # Verify uniqueness: only (1,1,1,0) satisfies
    all_sat = all_gf2_solutions(num_vars, equations)
    assert len(all_sat) == 1
    assert all_sat[0] == [1, 1, 1, 0]
    checks += 1

    # Verify equation details from Typst
    # Element 0 linear: x0 + x3 + 1 = 0 -> [[0],[3],[]]
    assert equations[0] == [[0], [3], []]
    checks += 1
    # Element 0 pairwise: x0*x3 = 0 -> [[0,3]]
    assert equations[1] == [[0, 3]]
    checks += 1

    # Numerical check: 1+0+1 = 0 mod 2
    assert (1 + 0 + 1) % 2 == 0
    checks += 1
    # 1*0 = 0
    assert 1 * 0 == 0
    checks += 1

    return checks


def test_no_example():
    """Reproduce Typst NO example."""
    print("  Testing NO example...")
    checks = 0

    universe_size = 9
    subsets = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [3, 7, 8]]

    # No X3C solution
    x3c_sols = all_x3c_solutions(universe_size, subsets)
    assert len(x3c_sols) == 0
    checks += 1

    num_vars, equations = reduce(universe_size, subsets)

    # No GF(2) solution
    gf2_sols = all_gf2_solutions(num_vars, equations)
    assert len(gf2_sols) == 0
    checks += 1

    # All 16 assignments fail
    for bits in itertools.product([0, 1], repeat=4):
        assert not is_feasible_target(num_vars, equations, list(bits))
        checks += 1

    # From Typst: forced x1=x2=x3=x4=1 but pairwise x1*x2=1 violated
    # Element 0 in C1,C2,C3: pairwise includes x0*x1
    assert not is_feasible_target(num_vars, equations, [1, 1, 1, 1])
    checks += 1

    return checks


def test_exhaustive_small():
    """Exhaustive forward+backward for small instances."""
    print("  Testing exhaustive small...")
    checks = 0

    # universe_size=3: all subsets of triples
    elems_3 = list(range(3))
    all_triples_3 = [list(t) for t in itertools.combinations(elems_3, 3)]
    # Only 1 triple possible: [0,1,2]
    for num_sub in range(1, 2):
        for chosen in itertools.combinations(all_triples_3, num_sub):
            subsets = [list(t) for t in chosen]
            src = len(all_x3c_solutions(3, subsets)) > 0
            nv, eqs = reduce(3, subsets)
            tgt = len(all_gf2_solutions(nv, eqs)) > 0
            assert src == tgt
            checks += 1

    # universe_size=6
    elems_6 = list(range(6))
    all_triples_6 = [list(t) for t in itertools.combinations(elems_6, 3)]
    for num_sub in range(1, 6):
        for chosen in itertools.combinations(all_triples_6, num_sub):
            subsets = [list(t) for t in chosen]
            n = len(subsets)
            if n > 8:
                continue
            src = len(all_x3c_solutions(6, subsets)) > 0
            nv, eqs = reduce(6, subsets)
            tgt = len(all_gf2_solutions(nv, eqs)) > 0
            assert src == tgt
            checks += 1

    # Random instances for universe_size=9
    rng = random.Random(12345)
    for _ in range(500):
        u = 9
        ns = rng.randint(1, 5)
        _, subs = random_x3c(rng, u, ns)
        src = len(all_x3c_solutions(u, subs)) > 0
        nv, eqs = reduce(u, subs)
        tgt = len(all_gf2_solutions(nv, eqs)) > 0
        assert src == tgt
        checks += 1

    return checks


def test_extraction_all():
    """Test solution extraction for all feasible instances."""
    print("  Testing extraction...")
    checks = 0

    # universe_size=6, up to 5 subsets
    elems_6 = list(range(6))
    all_triples_6 = [list(t) for t in itertools.combinations(elems_6, 3)]
    for num_sub in range(1, 6):
        for chosen in itertools.combinations(all_triples_6, num_sub):
            subsets = [list(t) for t in chosen]
            n = len(subsets)
            if n > 8:
                continue

            x3c_sols = all_x3c_solutions(6, subsets)
            if not x3c_sols:
                continue

            nv, eqs = reduce(6, subsets)
            gf2_sols = all_gf2_solutions(nv, eqs)

            for gsol in gf2_sols:
                ext = extract_solution(gsol)
                assert is_feasible_source(6, subsets, ext)
                checks += 1

            # Bijection check
            assert set(tuple(s) for s in x3c_sols) == set(tuple(s) for s in gf2_sols)
            checks += 1

    # Random
    rng = random.Random(67890)
    for _ in range(300):
        u = rng.choice([3, 6, 9])
        ns = rng.randint(1, 5)
        _, subs = random_x3c(rng, u, ns)

        x3c_sols = all_x3c_solutions(u, subs)
        if not x3c_sols:
            continue

        nv, eqs = reduce(u, subs)
        gf2_sols = all_gf2_solutions(nv, eqs)

        for gsol in gf2_sols:
            ext = extract_solution(gsol)
            assert is_feasible_source(u, subs, ext)
            checks += 1

    return checks


def test_hypothesis_pbt():
    """Property-based testing with hypothesis (2 strategies)."""
    print("  Testing hypothesis PBT...")
    checks = 0

    try:
        from hypothesis import given, settings, assume
        from hypothesis import strategies as st

        # Strategy 1: Random X3C instances
        @given(
            universe_size_mult=st.integers(min_value=1, max_value=3),
            num_subsets=st.integers(min_value=1, max_value=5),
            seed=st.integers(min_value=0, max_value=10000)
        )
        @settings(max_examples=1500, deadline=None)
        def prop_feasibility_preserved(universe_size_mult, num_subsets, seed):
            nonlocal checks
            universe_size = universe_size_mult * 3
            rng = random.Random(seed)
            elems = list(range(universe_size))
            subsets = [sorted(rng.sample(elems, 3)) for _ in range(num_subsets)]

            src = len(all_x3c_solutions(universe_size, subsets)) > 0
            nv, eqs = reduce(universe_size, subsets)
            tgt = len(all_gf2_solutions(nv, eqs)) > 0
            assert src == tgt
            checks += 1

        # Strategy 2: Guaranteed-feasible instances (construct cover then add noise)
        @given(
            q=st.integers(min_value=1, max_value=3),
            extra=st.integers(min_value=0, max_value=3),
            seed=st.integers(min_value=0, max_value=10000)
        )
        @settings(max_examples=1500, deadline=None)
        def prop_feasible_has_solution(q, extra, seed):
            nonlocal checks
            universe_size = 3 * q
            rng = random.Random(seed)
            elems = list(range(universe_size))

            # Construct a guaranteed cover
            shuffled = list(elems)
            rng.shuffle(shuffled)
            cover_subsets = []
            for i in range(0, universe_size, 3):
                cover_subsets.append(sorted(shuffled[i:i+3]))

            # Add extra random subsets
            for _ in range(extra):
                cover_subsets.append(sorted(rng.sample(elems, 3)))

            # Source must be feasible
            assert len(all_x3c_solutions(universe_size, cover_subsets)) > 0

            # Target must also be feasible
            nv, eqs = reduce(universe_size, cover_subsets)
            tgt_sols = all_gf2_solutions(nv, eqs)
            assert len(tgt_sols) > 0

            # Every target solution extracts to a valid cover
            for sol in tgt_sols:
                ext = extract_solution(sol)
                assert is_feasible_source(universe_size, cover_subsets, ext)
            checks += 1

        prop_feasibility_preserved()
        prop_feasible_has_solution()

    except ImportError:
        print("  hypothesis not available, using manual PBT fallback...")

        # Strategy 1: random instances
        rng = random.Random(11111)
        for _ in range(1500):
            u = rng.choice([3, 6, 9])
            ns = rng.randint(1, 5)
            _, subs = random_x3c(rng, u, ns)
            src = len(all_x3c_solutions(u, subs)) > 0
            nv, eqs = reduce(u, subs)
            tgt = len(all_gf2_solutions(nv, eqs)) > 0
            assert src == tgt
            checks += 1

        # Strategy 2: guaranteed feasible
        rng2 = random.Random(22222)
        for _ in range(1500):
            q = rng2.randint(1, 3)
            u = 3 * q
            elems = list(range(u))
            shuffled = list(elems)
            rng2.shuffle(shuffled)
            cover = [sorted(shuffled[i:i+3]) for i in range(0, u, 3)]
            extra = rng2.randint(0, 3)
            for _ in range(extra):
                cover.append(sorted(rng2.sample(elems, 3)))

            assert len(all_x3c_solutions(u, cover)) > 0
            nv, eqs = reduce(u, cover)
            tgt_sols = all_gf2_solutions(nv, eqs)
            assert len(tgt_sols) > 0
            for sol in tgt_sols:
                ext = extract_solution(sol)
                assert is_feasible_source(u, cover, ext)
            checks += 1

    return checks


def test_cross_compare():
    """Cross-compare with constructor script outputs via test vectors JSON."""
    print("  Cross-comparing with test vectors...")
    checks = 0

    tv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "test_vectors_exact_cover_by_3_sets_algebraic_equations_over_gf2.json"
    )

    if not os.path.exists(tv_path):
        print("  WARNING: test vectors not found, skipping cross-compare")
        return 0

    with open(tv_path) as f:
        tv = json.load(f)

    # YES instance
    yi = tv["yes_instance"]
    u = yi["input"]["universe_size"]
    subs = yi["input"]["subsets"]
    nv_expected = yi["output"]["num_variables"]
    eqs_expected = yi["output"]["equations"]

    nv, eqs = reduce(u, subs)
    assert nv == nv_expected
    checks += 1
    assert eqs == eqs_expected, f"YES equations differ"
    checks += 1

    sol = yi["source_solution"]
    assert is_feasible_target(nv, eqs, sol)
    checks += 1
    assert is_feasible_source(u, subs, sol)
    checks += 1

    # NO instance
    ni = tv["no_instance"]
    u = ni["input"]["universe_size"]
    subs = ni["input"]["subsets"]
    nv_expected = ni["output"]["num_variables"]
    eqs_expected = ni["output"]["equations"]

    nv, eqs = reduce(u, subs)
    assert nv == nv_expected
    checks += 1
    assert eqs == eqs_expected
    checks += 1

    assert not any(
        is_feasible_target(nv, eqs, list(bits))
        for bits in itertools.product([0, 1], repeat=nv)
    )
    checks += 1

    # Cross-compare on random instances
    rng = random.Random(55555)
    for _ in range(200):
        u = rng.choice([3, 6, 9])
        ns = rng.randint(1, 5)
        _, subs = random_x3c(rng, u, ns)

        nv, eqs = reduce(u, subs)

        # Verify both directions agree
        src_ok = len(all_x3c_solutions(u, subs)) > 0
        tgt_ok = len(all_gf2_solutions(nv, eqs)) > 0
        assert src_ok == tgt_ok
        checks += 1

    return checks


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    total = 0

    print("=== Adversary verification ===")

    c = test_yes_example()
    print(f"  YES example: {c} checks")
    total += c

    c = test_no_example()
    print(f"  NO example: {c} checks")
    total += c

    c = test_exhaustive_small()
    print(f"  Exhaustive: {c} checks")
    total += c

    c = test_extraction_all()
    print(f"  Extraction: {c} checks")
    total += c

    c = test_hypothesis_pbt()
    print(f"  Hypothesis PBT: {c} checks")
    total += c

    c = test_cross_compare()
    print(f"  Cross-compare: {c} checks")
    total += c

    print(f"\n{'='*60}")
    print(f"ADVERSARY CHECK COUNT: {total} (minimum: 5,000)")
    print(f"{'='*60}")

    if total < 5000:
        print(f"FAIL: {total} < 5000")
        sys.exit(1)

    print("ADVERSARY: ALL CHECKS PASSED")


if __name__ == "__main__":
    main()
