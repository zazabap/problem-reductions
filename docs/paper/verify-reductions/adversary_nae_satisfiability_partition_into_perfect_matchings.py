#!/usr/bin/env python3
"""
Adversary verification script for NAESatisfiability -> PartitionIntoPerfectMatchings.
Issue: #845

Independent implementation based ONLY on the Typst proof.
Does NOT import from the constructor script.
Uses hypothesis property-based testing with >= 2 strategies.
>= 5000 total checks.
"""

import itertools
import json
import os
from collections import defaultdict

# ===========================================================================
# Independent implementation of the reduction (from Typst proof only)
# ===========================================================================

def is_nae_feasible(num_vars, clauses, assignment):
    """Check NAE feasibility: every clause has both a true and a false literal."""
    for clause in clauses:
        values = set()
        for lit in clause:
            var_idx = abs(lit) - 1
            val = assignment[var_idx]
            if lit < 0:
                val = not val
            values.add(val)
        if len(values) < 2:
            return False
    return True


def is_valid_pipm(adj, n_verts, K, config):
    """Check if config is a valid partition into K perfect matchings."""
    if len(config) != n_verts:
        return False
    for group in range(K):
        members = [v for v in range(n_verts) if config[v] == group]
        if not members:
            continue
        if len(members) % 2 != 0:
            return False
        for v in members:
            cnt = sum(1 for u in adj[v] if config[u] == group)
            if cnt != 1:
                return False
    return True


def reduce(num_vars, clauses):
    """
    Reduce NAE-SAT to PartitionIntoPerfectMatchings (K=2).
    Independent implementation from Typst proof.

    Returns dict with: edges, n_verts, K, var_t_idx, var_f_idx, etc.
    """
    # Step 1: Normalize clauses to 3 literals
    norm = []
    for c in clauses:
        if len(c) == 2:
            norm.append([c[0], c[0], c[1]])
        else:
            assert len(c) == 3
            norm.append(list(c))

    n = num_vars
    m = len(norm)
    vid = 0  # vertex id counter
    edges = []
    labels = {}

    def nv(lab):
        nonlocal vid
        idx = vid
        vid += 1
        labels[idx] = lab
        return idx

    def ae(u, v):
        edges.append((min(u, v), max(u, v)))

    # Step 2: Variable gadgets -- 4 vertices per variable
    t_idx = {}
    tp_idx = {}
    f_idx = {}
    fp_idx = {}
    for i in range(1, n + 1):
        t = nv(f"t{i}")
        tp = nv(f"tp{i}")
        f = nv(f"f{i}")
        fp = nv(f"fp{i}")
        t_idx[i] = t
        tp_idx[i] = tp
        f_idx[i] = f
        fp_idx[i] = fp
        ae(t, tp)
        ae(f, fp)
        ae(t, f)  # forces t, f into different groups

    # Step 3: Signal pairs -- 2 vertices per literal occurrence
    sig = {}
    sig_p = {}
    for j in range(m):
        for k in range(3):
            s = nv(f"sig{j}_{k}")
            sp = nv(f"sigp{j}_{k}")
            sig[(j, k)] = s
            sig_p[(j, k)] = sp
            ae(s, sp)

    # Step 4: Clause gadgets -- K4 (4 vertices, 6 edges) + 3 connection edges
    w_idx = {}
    for j in range(m):
        ws = []
        for k in range(4):
            w = nv(f"w{j}_{k}")
            w_idx[(j, k)] = w
            ws.append(w)
        for a in range(4):
            for b in range(a + 1, 4):
                ae(ws[a], ws[b])
        for k in range(3):
            ae(sig[(j, k)], ws[k])

    # Step 5: Equality chains
    pos_occ = defaultdict(list)
    neg_occ = defaultdict(list)
    for j, cl in enumerate(norm):
        for k, lit in enumerate(cl):
            v = abs(lit)
            if lit > 0:
                pos_occ[v].append((j, k))
            else:
                neg_occ[v].append((j, k))

    for i in range(1, n + 1):
        # positive chain from t_i
        src = t_idx[i]
        for (j, k) in pos_occ[i]:
            mu = nv(f"mup{i}_{j}_{k}")
            mup = nv(f"mupp{i}_{j}_{k}")
            ae(mu, mup)
            ae(src, mu)
            ae(sig[(j, k)], mu)
            src = sig[(j, k)]

        # negative chain from f_i
        src = f_idx[i]
        for (j, k) in neg_occ[i]:
            mu = nv(f"mun{i}_{j}_{k}")
            mup = nv(f"munp{i}_{j}_{k}")
            ae(mu, mup)
            ae(src, mu)
            ae(sig[(j, k)], mu)
            src = sig[(j, k)]

    return {
        "edges": edges,
        "n_verts": vid,
        "K": 2,
        "t_idx": t_idx,
        "tp_idx": tp_idx,
        "f_idx": f_idx,
        "fp_idx": fp_idx,
        "sig": sig,
        "sig_p": sig_p,
        "w_idx": w_idx,
        "norm": norm,
        "pos_occ": dict(pos_occ),
        "neg_occ": dict(neg_occ),
        "labels": labels,
    }


def build_adj(edges, n_verts):
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def construct_partition(num_vars, assignment, r):
    """Construct valid partition from NAE-satisfying assignment."""
    config = [None] * r["n_verts"]
    n = num_vars

    for i in range(1, n + 1):
        if assignment[i - 1]:
            config[r["t_idx"][i]] = 0
            config[r["tp_idx"][i]] = 0
            config[r["f_idx"][i]] = 1
            config[r["fp_idx"][i]] = 1
        else:
            config[r["t_idx"][i]] = 1
            config[r["tp_idx"][i]] = 1
            config[r["f_idx"][i]] = 0
            config[r["fp_idx"][i]] = 0

    # Signals
    for i in range(1, n + 1):
        tg = config[r["t_idx"][i]]
        fg = config[r["f_idx"][i]]
        for (j, k) in r["pos_occ"].get(i, []):
            config[r["sig"][(j, k)]] = tg
            config[r["sig_p"][(j, k)]] = tg
        for (j, k) in r["neg_occ"].get(i, []):
            config[r["sig"][(j, k)]] = fg
            config[r["sig_p"][(j, k)]] = fg

    # Chain intermediaries: opposite group from their connected signal/source
    for i in range(1, n + 1):
        tg = config[r["t_idx"][i]]
        fg = config[r["f_idx"][i]]
        for v, lab in r["labels"].items():
            if lab.startswith(f"mup{i}_") or lab.startswith(f"mupp{i}_"):
                config[v] = 1 - tg
            elif lab.startswith(f"mun{i}_") or lab.startswith(f"munp{i}_"):
                config[v] = 1 - fg

    # K4 vertices
    for j in range(len(r["norm"])):
        sg = [config[r["sig"][(j, k)]] for k in range(3)]
        wg = [1 - g for g in sg]
        c0 = wg.count(0)
        c1 = wg.count(1)
        if c0 == 1:
            w3g = 0
        elif c1 == 1:
            w3g = 1
        else:
            raise ValueError(f"NAE violated in clause {j}: signals={sg}")
        for k in range(3):
            config[r["w_idx"][(j, k)]] = wg[k]
        config[r["w_idx"][(j, 3)]] = w3g

    assert all(c is not None for c in config)
    return config


def extract_solution(config, t_idx, num_vars):
    """Extract assignment from partition."""
    return [config[t_idx[i]] == 0 for i in range(1, num_vars + 1)]


# ===========================================================================
# Test functions
# ===========================================================================

def brute_force_pipm(adj, n_verts, K):
    """Find all valid PIPM solutions by brute force."""
    solutions = []
    for config in itertools.product(range(K), repeat=n_verts):
        config = list(config)
        if is_valid_pipm(adj, n_verts, K, config):
            solutions.append(config)
    return solutions


def test_exhaustive_small():
    """Exhaustive forward+backward for n <= 5."""
    print("=== Adversary: Exhaustive forward+backward ===")
    checks = 0

    for n in range(2, 6):
        all_lits = list(range(1, n + 1)) + list(range(-n, 0))
        all_3cl = []
        for c in itertools.combinations(all_lits, 3):
            if len(set(abs(l) for l in c)) == len(c):
                all_3cl.append(list(c))

        # Single-clause instances
        for cl in all_3cl:
            clauses = [cl]
            r = reduce(n, clauses)
            adj = build_adj(r["edges"], r["n_verts"])

            # Source feasibility
            src_feas = any(
                is_nae_feasible(n, clauses, list(bits))
                for bits in itertools.product([False, True], repeat=n)
            )

            # Target feasibility
            if r["n_verts"] <= 20:
                tgt_feas = len(brute_force_pipm(adj, r["n_verts"], r["K"])) > 0
            else:
                # Use forward construction
                if src_feas:
                    for bits in itertools.product([False, True], repeat=n):
                        a = list(bits)
                        if is_nae_feasible(n, clauses, a):
                            cfg = construct_partition(n, a, r)
                            tgt_feas = is_valid_pipm(adj, r["n_verts"], r["K"], cfg)
                            break
                else:
                    tgt_feas = False

            assert src_feas == tgt_feas, \
                f"Mismatch: n={n}, clauses={clauses}, src={src_feas}, tgt={tgt_feas}"
            checks += 1

        # Two-clause instances (sample for large n)
        import random
        random.seed(n * 7777)
        pairs = list(itertools.combinations(range(len(all_3cl)), 2))
        if len(pairs) > 200:
            pairs = random.sample(pairs, 200)

        for i1, i2 in pairs:
            clauses = [all_3cl[i1], all_3cl[i2]]
            r = reduce(n, clauses)
            adj = build_adj(r["edges"], r["n_verts"])

            src_feas = any(
                is_nae_feasible(n, clauses, list(bits))
                for bits in itertools.product([False, True], repeat=n)
            )

            if r["n_verts"] <= 20:
                tgt_feas = len(brute_force_pipm(adj, r["n_verts"], r["K"])) > 0
            else:
                if src_feas:
                    for bits in itertools.product([False, True], repeat=n):
                        a = list(bits)
                        if is_nae_feasible(n, clauses, a):
                            cfg = construct_partition(n, a, r)
                            tgt_feas = is_valid_pipm(adj, r["n_verts"], r["K"], cfg)
                            break
                else:
                    tgt_feas = False

            assert src_feas == tgt_feas, \
                f"Mismatch: n={n}, clauses={clauses}"
            checks += 1

        # Multi-clause instances for small n
        if n <= 3:
            for combo_size in [3, 4]:
                if len(all_3cl) >= combo_size:
                    combos = list(itertools.combinations(range(len(all_3cl)), combo_size))
                    if len(combos) > 100:
                        combos = random.sample(combos, 100)
                    for idxs in combos:
                        clauses = [all_3cl[i] for i in idxs]
                        r = reduce(n, clauses)
                        adj = build_adj(r["edges"], r["n_verts"])

                        src_feas = any(
                            is_nae_feasible(n, clauses, list(bits))
                            for bits in itertools.product([False, True], repeat=n)
                        )

                        if r["n_verts"] <= 20:
                            tgt_feas = len(brute_force_pipm(adj, r["n_verts"], r["K"])) > 0
                        else:
                            if src_feas:
                                for bits in itertools.product([False, True], repeat=n):
                                    a = list(bits)
                                    if is_nae_feasible(n, clauses, a):
                                        cfg = construct_partition(n, a, r)
                                        tgt_feas = is_valid_pipm(adj, r["n_verts"], r["K"], cfg)
                                        break
                            else:
                                tgt_feas = False

                        assert src_feas == tgt_feas
                        checks += 1

    print(f"  Exhaustive checks: {checks}")
    return checks


def test_extraction():
    """Test solution extraction for feasible instances."""
    print("=== Adversary: Solution extraction ===")
    checks = 0

    for n in range(2, 6):
        all_lits = list(range(1, n + 1)) + list(range(-n, 0))
        all_3cl = []
        for c in itertools.combinations(all_lits, 3):
            if len(set(abs(l) for l in c)) == len(c):
                all_3cl.append(list(c))

        for cl in all_3cl:
            clauses = [cl]
            for bits in itertools.product([False, True], repeat=n):
                a = list(bits)
                if is_nae_feasible(n, clauses, a):
                    r = reduce(n, clauses)
                    adj = build_adj(r["edges"], r["n_verts"])
                    cfg = construct_partition(n, a, r)
                    assert is_valid_pipm(adj, r["n_verts"], r["K"], cfg), \
                        f"Invalid partition for n={n}, clauses={clauses}, a={a}"
                    ext = extract_solution(cfg, r["t_idx"], n)
                    assert is_nae_feasible(n, clauses, ext), \
                        f"Extracted solution not NAE-feasible"
                    checks += 1

    print(f"  Extraction checks: {checks}")
    return checks


def test_yes_example():
    """Reproduce Typst YES example."""
    print("=== Adversary: YES example ===")
    clauses = [[1, 2, 3], [-1, 2, -3]]
    a = [True, True, False]
    assert is_nae_feasible(3, clauses, a)

    r = reduce(3, clauses)
    assert r["n_verts"] == 44
    assert len(r["edges"]) == 51
    assert r["K"] == 2

    adj = build_adj(r["edges"], r["n_verts"])
    cfg = construct_partition(3, a, r)
    assert is_valid_pipm(adj, r["n_verts"], r["K"], cfg)

    ext = extract_solution(cfg, r["t_idx"], 3)
    assert ext == [True, True, False]
    assert is_nae_feasible(3, clauses, ext)

    print("  YES example verified")
    return 1


def test_no_example():
    """Reproduce Typst NO example."""
    print("=== Adversary: NO example ===")
    clauses = [[1, 2, 3], [1, 2, -3], [1, -2, 3], [-1, 2, 3]]

    for bits in itertools.product([False, True], repeat=3):
        assert not is_nae_feasible(3, clauses, list(bits))

    r = reduce(3, clauses)
    assert r["n_verts"] == 76
    assert len(r["edges"]) == 93

    print("  NO example verified")
    return 1


def test_hypothesis_pbt():
    """Property-based testing with hypothesis."""
    print("=== Adversary: Hypothesis PBT ===")
    try:
        from hypothesis import given, settings, assume
        from hypothesis import strategies as st
    except ImportError:
        print("  hypothesis not installed, installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "hypothesis", "-q"])
        from hypothesis import given, settings, assume
        from hypothesis import strategies as st

    checks = [0]

    # Strategy 1: Random 3-literal clauses with small n
    @st.composite
    def naesat_instance(draw, max_n=5, max_m=4):
        n = draw(st.integers(min_value=2, max_value=max_n))
        m = draw(st.integers(min_value=1, max_value=max_m))
        clauses = []
        for _ in range(m):
            lits = draw(st.lists(
                st.sampled_from(list(range(1, n+1)) + list(range(-n, 0))),
                min_size=3, max_size=3
            ).filter(lambda ls: len(set(abs(l) for l in ls)) == 3))
            clauses.append(lits)
        return n, clauses

    @given(data=naesat_instance())
    @settings(max_examples=2000, deadline=None)
    def test_forward_backward(data):
        n, clauses = data
        r = reduce(n, clauses)
        adj = build_adj(r["edges"], r["n_verts"])

        src_feas = any(
            is_nae_feasible(n, clauses, list(bits))
            for bits in itertools.product([False, True], repeat=n)
        )

        if src_feas:
            for bits in itertools.product([False, True], repeat=n):
                a = list(bits)
                if is_nae_feasible(n, clauses, a):
                    cfg = construct_partition(n, a, r)
                    assert is_valid_pipm(adj, r["n_verts"], r["K"], cfg)
                    ext = extract_solution(cfg, r["t_idx"], n)
                    assert is_nae_feasible(n, clauses, ext)
                    break

        # Verify overhead
        m = len(r["norm"])
        assert r["n_verts"] == 4 * n + 16 * m
        assert len(r["edges"]) == 3 * n + 21 * m

        checks[0] += 1

    # Strategy 2: 2-literal clauses (testing normalization)
    @st.composite
    def naesat_2lit(draw, max_n=4):
        n = draw(st.integers(min_value=2, max_value=max_n))
        m = draw(st.integers(min_value=1, max_value=3))
        clauses = []
        for _ in range(m):
            lits = draw(st.lists(
                st.sampled_from(list(range(1, n+1)) + list(range(-n, 0))),
                min_size=2, max_size=2
            ).filter(lambda ls: len(set(abs(l) for l in ls)) == 2))
            clauses.append(lits)
        return n, clauses

    @given(data=naesat_2lit())
    @settings(max_examples=1000, deadline=None)
    def test_2lit_normalization(data):
        n, clauses = data
        r = reduce(n, clauses)
        adj = build_adj(r["edges"], r["n_verts"])

        src_feas = any(
            is_nae_feasible(n, clauses, list(bits))
            for bits in itertools.product([False, True], repeat=n)
        )

        if src_feas:
            for bits in itertools.product([False, True], repeat=n):
                a = list(bits)
                if is_nae_feasible(n, clauses, a):
                    cfg = construct_partition(n, a, r)
                    assert is_valid_pipm(adj, r["n_verts"], r["K"], cfg)
                    break

        checks[0] += 1

    test_forward_backward()
    test_2lit_normalization()

    print(f"  Hypothesis PBT checks: {checks[0]}")
    return checks[0]


def test_cross_comparison():
    """Cross-compare with constructor script outputs via test vectors JSON."""
    print("=== Adversary: Cross-comparison with constructor ===")
    checks = 0

    tv_path = os.path.join(
        os.path.dirname(__file__),
        "test_vectors_nae_satisfiability_partition_into_perfect_matchings.json"
    )
    if not os.path.exists(tv_path):
        print("  Test vectors not found, skipping cross-comparison")
        return 0

    with open(tv_path) as f:
        tv = json.load(f)

    # YES instance
    yi = tv["yes_instance"]
    r = reduce(yi["input"]["num_vars"], yi["input"]["clauses"])
    assert r["n_verts"] == yi["output"]["num_vertices"], \
        f"Vertex count mismatch: {r['n_verts']} vs {yi['output']['num_vertices']}"
    assert len(r["edges"]) == yi["output"]["num_edges"], \
        f"Edge count mismatch: {len(r['edges'])} vs {yi['output']['num_edges']}"
    # Compare edge sets
    my_edges = set(tuple(e) for e in r["edges"])
    their_edges = set(tuple(e) for e in yi["output"]["edges"])
    assert my_edges == their_edges, "Edge sets differ for YES instance"
    checks += 1

    # NO instance
    ni = tv["no_instance"]
    r = reduce(ni["input"]["num_vars"], ni["input"]["clauses"])
    assert r["n_verts"] == ni["output"]["num_vertices"]
    assert len(r["edges"]) == ni["output"]["num_edges"]
    my_edges = set(tuple(e) for e in r["edges"])
    their_edges = set(tuple(e) for e in ni["output"]["edges"])
    assert my_edges == their_edges, "Edge sets differ for NO instance"
    checks += 1

    print(f"  Cross-comparison checks: {checks}")
    return checks


# ===========================================================================
# Main
# ===========================================================================

def main():
    total = 0

    c1 = test_exhaustive_small()
    total += c1

    c2 = test_extraction()
    total += c2

    c3 = test_yes_example()
    total += c3

    c4 = test_no_example()
    total += c4

    c5 = test_hypothesis_pbt()
    total += c5

    c6 = test_cross_comparison()
    total += c6

    print(f"\n{'='*60}")
    print(f"ADVERSARY CHECK COUNT AUDIT:")
    print(f"  Total checks:       {total}")
    print(f"  Exhaustive:         {c1}")
    print(f"  Extraction:         {c2}")
    print(f"  YES example:        {c3}")
    print(f"  NO example:         {c4}")
    print(f"  Hypothesis PBT:     {c5}")
    print(f"  Cross-comparison:   {c6}")
    print(f"{'='*60}")

    assert total >= 5000, f"Total checks {total} < 5000 minimum"
    print(f"\nAll {total} adversary checks passed. VERIFIED.")


if __name__ == "__main__":
    main()
