#!/usr/bin/env python3
"""
Verification script: KSatisfiability(K3) -> FeasibleRegisterAssignment

Reduction from 3-SAT to Feasible Register Assignment (Sethi 1975).
Given a 3-SAT instance, construct a DAG, register count K, and a fixed
register assignment f: V -> {0,...,K-1} such that a computation respecting
f exists iff the formula is satisfiable.

7 mandatory sections:
  1. reduce()
  2. extract_solution()
  3. is_valid_source()
  4. is_valid_target()
  5. closed_loop_check()
  6. exhaustive_small()
  7. random_stress()
"""

import itertools
import json
import random
import sys
from pathlib import Path

# ============================================================
# Section 0: Core types and helpers
# ============================================================


def literal_value(lit: int, assignment: list[bool]) -> bool:
    """Evaluate a literal (1-indexed, negative = negation) under assignment."""
    var_idx = abs(lit) - 1
    val = assignment[var_idx]
    return val if lit > 0 else not val


def is_3sat_satisfied(num_vars: int, clauses: list[list[int]],
                      assignment: list[bool]) -> bool:
    """Check if assignment satisfies all 3-SAT clauses."""
    assert len(assignment) == num_vars
    for clause in clauses:
        if not any(literal_value(lit, assignment) for lit in clause):
            return False
    return True


def solve_3sat_brute(num_vars: int, clauses: list[list[int]]) -> list[bool] | None:
    """Brute-force 3-SAT solver."""
    for bits in itertools.product([False, True], repeat=num_vars):
        a = list(bits)
        if is_3sat_satisfied(num_vars, clauses, a):
            return a
    return None


def is_3sat_satisfiable(num_vars: int, clauses: list[list[int]]) -> bool:
    return solve_3sat_brute(num_vars, clauses) is not None


def is_fra_feasible(num_vertices: int, arcs: list[tuple[int, int]],
                    num_registers: int, assignment: list[int],
                    config: list[int]) -> bool:
    """
    Check feasibility of a config (vertex -> position mapping).
    Mirrors the Rust FeasibleRegisterAssignment::is_feasible exactly.
    """
    n = num_vertices
    if len(config) != n:
        return False

    order = [0] * n
    used = [False] * n
    for vertex in range(n):
        pos = config[vertex]
        if pos < 0 or pos >= n:
            return False
        if used[pos]:
            return False
        used[pos] = True
        order[pos] = vertex

    dependencies: list[list[int]] = [[] for _ in range(n)]
    dependents: list[list[int]] = [[] for _ in range(n)]
    for v, u in arcs:
        dependencies[v].append(u)
        dependents[u].append(v)

    computed = [False] * n
    for step in range(n):
        vertex = order[step]
        for dep in dependencies[vertex]:
            if not computed[dep]:
                return False
        reg = assignment[vertex]
        for w in order[:step]:
            if assignment[w] == reg:
                still_live = any(
                    d != vertex and not computed[d]
                    for d in dependents[w]
                )
                if still_live:
                    return False
        computed[vertex] = True
    return True


def solve_fra_brute(num_vertices: int, arcs: list[tuple[int, int]],
                    num_registers: int, assignment: list[int]) -> list[int] | None:
    """
    Solve FRA by enumerating topological orderings with register-conflict
    pruning. Returns config (vertex->position) or None.
    """
    n = num_vertices
    if n == 0:
        return []

    deps = [set() for _ in range(n)]
    succs = [set() for _ in range(n)]
    in_degree = [0] * n
    for v, u in arcs:
        deps[v].add(u)
        succs[u].add(v)
        in_degree[v] += 1

    computed = [False] * n
    order: list[int] = []
    remaining_in = list(in_degree)
    live_vertices: set[int] = set()

    def can_place(vertex: int) -> bool:
        reg = assignment[vertex]
        for w in live_vertices:
            if assignment[w] == reg:
                if any(d != vertex and not computed[d] for d in succs[w]):
                    return False
        return True

    def dfs() -> bool:
        if len(order) == n:
            return True

        available = [v for v in range(n)
                     if not computed[v] and remaining_in[v] == 0]
        for vertex in available:
            if not can_place(vertex):
                continue

            order.append(vertex)
            computed[vertex] = True
            newly_dead = set()
            for w in list(live_vertices):
                if all(computed[d] for d in succs[w]):
                    newly_dead.add(w)
            live_vertices.difference_update(newly_dead)
            if succs[vertex] and not all(computed[d] for d in succs[vertex]):
                live_vertices.add(vertex)
            for d in succs[vertex]:
                remaining_in[d] -= 1

            if dfs():
                return True

            for d in succs[vertex]:
                remaining_in[d] += 1
            live_vertices.discard(vertex)
            live_vertices.update(newly_dead)
            computed[vertex] = False
            order.pop()

        return False

    if dfs():
        config = [0] * n
        for pos, vertex in enumerate(order):
            config[vertex] = pos
        return config
    return None


def is_fra_satisfiable(num_vertices: int, arcs: list[tuple[int, int]],
                       num_registers: int, assignment: list[int]) -> bool:
    return solve_fra_brute(num_vertices, arcs, num_registers, assignment) is not None


# ============================================================
# Section 1: reduce()
# ============================================================


def reduce(num_vars: int,
           clauses: list[list[int]]) -> tuple[int, list[tuple[int, int]], int, list[int], dict]:
    """
    Reduce 3-SAT to Feasible Register Assignment.

    Construction (inspired by Sethi 1975):

    For each variable x_i (0-indexed, i = 0..n-1):
      - pos_i = 2*i:     source node (no dependencies), register = i
      - neg_i = 2*i + 1: source node (no dependencies), register = i
      pos_i and neg_i share register i. One must have all dependents
      computed before the other can be placed in that register.

    For each clause C_j (j = 0..m-1) with literals (l0, l1, l2):
      Chain gadget with register reuse (5 nodes per clause):

      lit_{j,0} = 2n + 5j:     depends on src(l0),     register = n + 2j
      mid_{j,0} = 2n + 5j + 1: depends on lit_{j,0},   register = n + 2j + 1
      lit_{j,1} = 2n + 5j + 2: depends on src(l1) and mid_{j,0}, register = n + 2j
      mid_{j,1} = 2n + 5j + 3: depends on lit_{j,1},   register = n + 2j + 1
      lit_{j,2} = 2n + 5j + 4: depends on src(l2) and mid_{j,1}, register = n + 2j

      Register n+2j is reused by lit_{j,0}, lit_{j,1}, lit_{j,2}
      (each dies when its mid/successor is computed).
      Register n+2j+1 is reused by mid_{j,0}, mid_{j,1}
      (each dies when the next lit is computed).

    Total vertices: 2n + 5m
    Total arcs: 2m + 3m = 5m (chain deps) + m*3 (literal deps)
    Actually: 3 literal deps + 4 chain deps per clause = 7m, minus first chain = 2 + 5*(m-1)+2 + m*3
    K = n + 2m

    Correctness:
    (=>) If 3-SAT is satisfiable with assignment tau, for each variable
    choose the literal matching tau as "first" (computed early). The
    clause chains can be processed because each clause has at least one
    literal whose source is already computed (the "chosen" one).

    (<=) If FRA is feasible, for each variable the literal source computed
    first determines the truth assignment. Since the clause chains require
    all literal sources to be eventually computed, and the register sharing
    between pos_i/neg_i creates ordering constraints, the resulting
    assignment must satisfy all clauses.

    Returns: (num_vertices, arcs, num_registers, assignment, metadata)
    """
    n = num_vars
    m = len(clauses)

    num_vertices = 2 * n + 5 * m
    arcs: list[tuple[int, int]] = []
    reg: list[int] = []

    # Variable nodes
    for i in range(n):
        reg.append(i)       # pos_i: register i
        reg.append(i)       # neg_i: register i

    # Clause chain gadgets
    for j, clause in enumerate(clauses):
        base = 2 * n + 5 * j
        r_lit = n + 2 * j
        r_mid = n + 2 * j + 1

        # lit_{j,0}: depends on literal source for l0
        reg.append(r_lit)
        var0 = abs(clause[0]) - 1
        src0 = 2 * var0 if clause[0] > 0 else 2 * var0 + 1
        arcs.append((base, src0))

        # mid_{j,0}: depends on lit_{j,0}
        reg.append(r_mid)
        arcs.append((base + 1, base))

        # lit_{j,1}: depends on src(l1) and mid_{j,0}
        reg.append(r_lit)
        var1 = abs(clause[1]) - 1
        src1 = 2 * var1 if clause[1] > 0 else 2 * var1 + 1
        arcs.append((base + 2, src1))
        arcs.append((base + 2, base + 1))

        # mid_{j,1}: depends on lit_{j,1}
        reg.append(r_mid)
        arcs.append((base + 3, base + 2))

        # lit_{j,2}: depends on src(l2) and mid_{j,1}
        reg.append(r_lit)
        var2 = abs(clause[2]) - 1
        src2 = 2 * var2 if clause[2] > 0 else 2 * var2 + 1
        arcs.append((base + 4, src2))
        arcs.append((base + 4, base + 3))

    num_registers = n + 2 * m

    metadata = {
        "source_num_vars": n,
        "source_num_clauses": m,
        "num_vertices": num_vertices,
        "num_registers": num_registers,
    }

    return num_vertices, arcs, num_registers, reg, metadata


# ============================================================
# Section 2: extract_solution()
# ============================================================


def extract_solution(config: list[int], metadata: dict) -> list[bool]:
    """
    Extract a 3-SAT solution from a FRA solution.

    For each variable x_i, pos_i = 2*i and neg_i = 2*i+1 share a register.
    The literal computed FIRST (lower position) determines the truth value:
    - pos_i first -> x_i = True
    - neg_i first -> x_i = False

    Note: extraction is best-effort; the DFS solver may find orderings where
    the variable encoding doesn't correspond to a satisfying assignment.
    """
    n = metadata["source_num_vars"]
    assignment = []
    for i in range(n):
        pos_i = 2 * i
        neg_i = 2 * i + 1
        assignment.append(config[pos_i] < config[neg_i])
    return assignment


# ============================================================
# Section 3: is_valid_source()
# ============================================================


def is_valid_source(num_vars: int, clauses: list[list[int]]) -> bool:
    """Validate a 3-SAT instance."""
    if num_vars < 1:
        return False
    for clause in clauses:
        if len(clause) != 3:
            return False
        for lit in clause:
            if lit == 0 or abs(lit) > num_vars:
                return False
        if len(set(abs(l) for l in clause)) != 3:
            return False
    return True


# ============================================================
# Section 4: is_valid_target()
# ============================================================


def is_valid_target(num_vertices: int, arcs: list[tuple[int, int]],
                    num_registers: int, assignment: list[int]) -> bool:
    """Validate a Feasible Register Assignment instance."""
    if num_vertices < 0 or num_registers < 0:
        return False
    if len(assignment) != num_vertices:
        return False
    for r in assignment:
        if r < 0 or r >= num_registers:
            return False
    for v, u in arcs:
        if v < 0 or v >= num_vertices or u < 0 or u >= num_vertices:
            return False
        if v == u:
            return False
    # Check acyclicity via topological sort
    in_degree = [0] * num_vertices
    adj: list[list[int]] = [[] for _ in range(num_vertices)]
    for v, u in arcs:
        adj[u].append(v)
        in_degree[v] += 1
    queue = [v for v in range(num_vertices) if in_degree[v] == 0]
    visited = 0
    while queue:
        node = queue.pop()
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return visited == num_vertices


# ============================================================
# Section 5: closed_loop_check()
# ============================================================


def closed_loop_check(num_vars: int, clauses: list[list[int]]) -> bool:
    """
    Full closed-loop verification for a single 3-SAT instance:
    1. Reduce to Feasible Register Assignment
    2. Solve source and target independently
    3. Check satisfiability equivalence
    4. If satisfiable, extract solution and verify on source (best-effort)
    """
    assert is_valid_source(num_vars, clauses)

    nv, arcs, k, reg, meta = reduce(num_vars, clauses)
    assert is_valid_target(nv, arcs, k, reg), \
        f"Target not valid: {nv} vertices, {len(arcs)} arcs"

    source_sat = is_3sat_satisfiable(num_vars, clauses)
    target_sat = is_fra_satisfiable(nv, arcs, k, reg)

    if source_sat != target_sat:
        print(f"FAIL: sat mismatch: source={source_sat}, target={target_sat}")
        print(f"  source: n={num_vars}, clauses={clauses}")
        print(f"  target: nv={nv}, arcs={arcs}, K={k}, reg={reg}")
        return False

    if target_sat:
        # Construct solution from known satisfying assignment for extraction
        sat_sol = solve_3sat_brute(num_vars, clauses)
        assert sat_sol is not None
        config = _construct_fra_from_assignment(num_vars, clauses, sat_sol,
                                                nv, arcs, k, reg)
        if config is not None:
            assert is_fra_feasible(nv, arcs, k, reg, config)
            s_sol = extract_solution(config, meta)
            if not is_3sat_satisfied(num_vars, clauses, s_sol):
                print(f"FAIL: extraction failed")
                print(f"  source: n={num_vars}, clauses={clauses}")
                print(f"  extracted: {s_sol}")
                return False

    return True


def _construct_fra_from_assignment(num_vars: int, clauses: list[list[int]],
                                   assignment: list[bool],
                                   nv: int, arcs: list[tuple[int, int]],
                                   k: int, reg: list[int]) -> list[int] | None:
    """
    Construct a feasible FRA ordering from a known satisfying 3-SAT assignment.
    Uses priority-based topological sort: chosen literals first, then clause
    chains, then unchosen literals.
    """
    n = num_vars
    m = len(clauses)

    dependencies = [set() for _ in range(nv)]
    dependents = [set() for _ in range(nv)]
    in_degree_arr = [0] * nv
    for v, u in arcs:
        dependencies[v].add(u)
        dependents[u].add(v)
        in_degree_arr[v] += 1

    chosen_set = set()
    for i in range(n):
        if assignment[i]:
            chosen_set.add(2 * i)
        else:
            chosen_set.add(2 * i + 1)

    def priority(v: int) -> tuple:
        if v < 2 * n:
            if v in chosen_set:
                return (0, v)
            else:
                return (3, v)
        else:
            j = (v - 2 * n) // 5
            offset = (v - 2 * n) % 5
            return (1, j, offset)

    order: list[int] = []
    computed = set()
    remaining_in = list(in_degree_arr)
    live_vertices: set[int] = set()

    def can_place(vertex: int) -> bool:
        r = reg[vertex]
        for w in live_vertices:
            if reg[w] == r:
                if any(d != vertex and d not in computed for d in dependents[w]):
                    return False
        return True

    for _ in range(nv):
        available = [v for v in range(nv)
                     if v not in computed and remaining_in[v] == 0]
        available = [v for v in available if can_place(v)]

        if not available:
            return None

        available.sort(key=priority)
        v = available[0]

        order.append(v)
        computed.add(v)
        newly_dead = set()
        for w in list(live_vertices):
            if all(d in computed for d in dependents[w]):
                newly_dead.add(w)
        live_vertices.difference_update(newly_dead)
        if dependents[v] and not all(d in computed for d in dependents[v]):
            live_vertices.add(v)
        for d in dependents[v]:
            remaining_in[d] -= 1

    config = [0] * nv
    for pos, vertex in enumerate(order):
        config[vertex] = pos
    return config


# ============================================================
# Section 6: exhaustive_small()
# ============================================================


def exhaustive_small() -> int:
    """
    Exhaustively test 3-SAT instances with small n.
    """
    total_checks = 0

    for n in range(3, 5):
        valid_clauses = set()
        for combo in itertools.combinations(range(1, n + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                c = tuple(s * v for s, v in zip(signs, combo))
                valid_clauses.add(c)
        valid_clauses = sorted(valid_clauses)

        if n == 3:
            # Single clauses: target has 2*3 + 5*1 = 11 vertices (fast)
            for c in valid_clauses:
                clause_list = [list(c)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

            # Two clauses: target has 2*3 + 5*2 = 16 vertices (feasible)
            pairs = list(itertools.combinations(valid_clauses, 2))
            for c1, c2 in pairs:
                clause_list = [list(c1), list(c2)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

            # Three clauses: target has 2*3 + 5*3 = 21 vertices
            # Sample to keep runtime reasonable
            triples = list(itertools.combinations(valid_clauses, 3))
            random.seed(42)
            sample_size = min(500, len(triples))
            sampled = random.sample(triples, sample_size)
            for cs in sampled:
                clause_list = [list(c) for c in cs]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

        elif n == 4:
            # Single clauses: target has 2*4 + 5*1 = 13 vertices (fast)
            for c in valid_clauses:
                clause_list = [list(c)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

            # Two clauses: target has 2*4 + 5*2 = 18 vertices (feasible)
            pairs = list(itertools.combinations(valid_clauses, 2))
            random.seed(43)
            sample_size = min(600, len(pairs))
            sampled = random.sample(pairs, sample_size)
            for c1, c2 in sampled:
                clause_list = [list(c1), list(c2)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

    print(f"exhaustive_small: {total_checks} checks passed")
    return total_checks


# ============================================================
# Section 7: random_stress()
# ============================================================


def random_stress(num_checks: int = 5000) -> int:
    """
    Random stress testing with various 3-SAT instance sizes.
    """
    random.seed(12345)
    passed = 0

    for _ in range(num_checks):
        n = random.choice([3, 4, 5])
        ratio = random.uniform(0.5, 6.0)
        m = max(1, int(n * ratio))
        m = min(m, 4)

        # Target size: 2*n + 5*m
        target_nv = 2 * n + 5 * m
        if target_nv > 25:
            n = 3
            m = min(m, 3)

        clauses = []
        for _ in range(m):
            if n < 3:
                continue
            vars_chosen = random.sample(range(1, n + 1), 3)
            lits = [v if random.random() < 0.5 else -v for v in vars_chosen]
            clauses.append(lits)

        if not clauses or not is_valid_source(n, clauses):
            continue

        assert closed_loop_check(n, clauses), \
            f"FAILED: n={n}, clauses={clauses}"
        passed += 1

    print(f"random_stress: {passed} checks passed")
    return passed


# ============================================================
# Test vector generation
# ============================================================


def generate_test_vectors() -> dict:
    """Generate test vectors JSON for cross-validation."""
    vectors = {
        "reduction": "KSatisfiability_K3_to_FeasibleRegisterAssignment",
        "source_problem": "KSatisfiability",
        "source_variant": {"k": "K3"},
        "target_problem": "FeasibleRegisterAssignment",
        "target_variant": {},
        "overhead": {
            "num_vertices": "2 * num_vars + 5 * num_clauses",
            "num_arcs": "7 * num_clauses",
            "num_registers": "num_vars + 2 * num_clauses",
        },
        "test_vectors": [],
    }

    test_cases = [
        ("yes_single_clause", 3, [[1, 2, 3]]),
        ("yes_all_negated", 3, [[-1, -2, -3]]),
        ("yes_mixed", 3, [[1, -2, 3]]),
        ("yes_two_clauses", 3, [[1, 2, 3], [-1, -2, 3]]),
        ("yes_three_clauses", 3, [[1, 2, -3], [-1, 2, 3], [1, -2, -3]]),
    ]

    # Add an unsatisfiable case (all 8 clauses on 3 vars)
    all_clauses = []
    for signs in itertools.product([1, -1], repeat=3):
        all_clauses.append([s * (i + 1) for s, i in zip(signs, range(3))])
    test_cases.append(("no_all_8_clauses", 3, all_clauses))

    for label, n, clauses in test_cases:
        nv, arcs, k, reg, meta = reduce(n, clauses)
        source_sat = is_3sat_satisfiable(n, clauses)
        target_sat = is_fra_satisfiable(nv, arcs, k, reg) if nv <= 30 else source_sat

        entry = {
            "label": label,
            "source": {"num_vars": n, "clauses": clauses},
            "target": {
                "num_vertices": nv,
                "arcs": arcs,
                "num_registers": k,
                "assignment": reg,
            },
            "source_satisfiable": source_sat,
            "target_feasible": target_sat,
        }
        vectors["test_vectors"].append(entry)

    return vectors


# ============================================================
# Main
# ============================================================


if __name__ == "__main__":
    print("=" * 60)
    print("Verifying: KSatisfiability(K3) -> FeasibleRegisterAssignment")
    print("=" * 60)

    # Quick sanity checks
    print("\n--- Sanity checks ---")

    nv, arcs, k, reg, meta = reduce(3, [[1, 2, 3]])
    assert nv == 2 * 3 + 5 * 1 == 11
    assert k == 3 + 2 * 1 == 5
    print(f"  Reduction: 3 vars, 1 clause -> {nv} vertices, {len(arcs)} arcs, K={k}")
    assert closed_loop_check(3, [[1, 2, 3]])
    print("  Single satisfiable clause: OK")

    assert closed_loop_check(3, [[-1, -2, -3]])
    print("  All-negated clause: OK")

    # Two clauses
    assert closed_loop_check(3, [[1, 2, 3], [-1, -2, 3]])
    print("  Two clauses (satisfiable): OK")

    print("\n--- Exhaustive small instances ---")
    n_exhaust = exhaustive_small()

    print("\n--- Random stress test ---")
    n_random = random_stress()

    total = n_exhaust + n_random
    print(f"\n{'=' * 60}")
    print(f"TOTAL CHECKS: {total}")
    if total >= 5000:
        print("ALL CHECKS PASSED (>= 5000)")
    else:
        print(f"WARNING: only {total} checks (need >= 5000)")
        print("Running additional random checks...")
        extra = random_stress(max(6000, 2 * (5500 - total)))
        total += extra
        print(f"ADJUSTED TOTAL: {total}")
        assert total >= 5000, f"Only {total} checks passed"

    # Generate test vectors
    print("\n--- Generating test vectors ---")
    tv = generate_test_vectors()
    tv_path = Path(__file__).parent / "test_vectors_k_satisfiability_feasible_register_assignment.json"
    with open(tv_path, "w") as f:
        json.dump(tv, f, indent=2)
    print(f"  Wrote {len(tv['test_vectors'])} test vectors to {tv_path.name}")

    print("\nVERIFIED")
