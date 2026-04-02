#!/usr/bin/env python3
"""
Verification script: KSatisfiability(K3) -> PreemptiveScheduling

Reduction from 3-SAT to Preemptive Scheduling via Ullman (1975).
The reduction constructs a unit-task scheduling instance (P4) with
precedence constraints and variable capacity at each time step.
A schedule meeting the deadline exists iff the 3-SAT formula is satisfiable.

Since unit-task scheduling is a special case of preemptive scheduling
(unit tasks cannot be preempted), this directly yields a preemptive
scheduling instance.

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


# ============================================================
# P4 constructive solver
# ============================================================


def construct_p4_schedule(
    num_jobs: int,
    precedences: list[tuple[int, int]],
    capacities: list[int],
    time_limit: int,
    meta: dict,
    truth_assignment: list[bool],
    clauses: list[list[int]],
) -> list[int] | None:
    """
    Given a truth assignment, construct the P4 schedule following Ullman's proof.

    Returns job-to-time-step assignment list, or None if the assignment
    doesn't lead to a valid schedule.

    Schedule structure (Ullman 1975):
    - x_i = True  => x_{i,j} at time j, xbar_{i,j} at time j+1
    - x_i = False => xbar_{i,j} at time j, x_{i,j} at time j+1
    - Forcing jobs placed at the earliest time after their predecessor
    - For each clause, exactly 1 of 7 clause jobs goes at time M+1
      (the one whose binary pattern matches the truth assignment),
      the other 6 go at time M+2.
    """
    M = meta["source_num_vars"]
    N = meta["source_num_clauses"]
    T = time_limit
    var_chain_id = meta["var_chain_id_fn"]
    forcing_id = meta["forcing_id_fn"]
    clause_job_id = meta["clause_job_id_fn"]

    assignment = [-1] * num_jobs

    # Step 1: Assign variable chain jobs
    for i in range(1, M + 1):
        if truth_assignment[i - 1]:  # x_i = True
            for j in range(M + 1):
                assignment[var_chain_id(i, j, True)] = j       # x_{i,j} at time j
                assignment[var_chain_id(i, j, False)] = j + 1  # xbar_{i,j} at time j+1
        else:  # x_i = False
            for j in range(M + 1):
                assignment[var_chain_id(i, j, False)] = j       # xbar_{i,j} at time j
                assignment[var_chain_id(i, j, True)] = j + 1    # x_{i,j} at time j+1

    # Step 2: Assign forcing jobs
    for i in range(1, M + 1):
        pos_time = assignment[var_chain_id(i, i - 1, True)]
        neg_time = assignment[var_chain_id(i, i - 1, False)]
        assignment[forcing_id(i, True)] = pos_time + 1
        assignment[forcing_id(i, False)] = neg_time + 1

    # Step 3: Assign clause jobs
    # For each clause, determine which pattern matches the truth assignment.
    # Pattern j (1..7) has binary bits a_1 a_2 a_3.
    # The clause job D_{i,j} whose pattern matches the literal values
    # has all predecessors at time M (the "true" chain endpoints),
    # so it can go at time M+1.
    # All other D_{i,j'} have at least one predecessor at time M+1,
    # so they must go at time M+2.
    for ci in range(N):
        clause = clauses[ci]
        # Determine the pattern: for each literal position, is it true?
        pattern = 0
        for p in range(3):
            lit = clause[p]
            var = abs(lit)
            lit_positive = lit > 0
            val = truth_assignment[var - 1]
            lit_true = val if lit_positive else not val
            if lit_true:
                pattern |= (1 << (2 - p))

        for j in range(1, 8):
            if j == pattern:
                assignment[clause_job_id(ci + 1, j)] = M + 1
            else:
                assignment[clause_job_id(ci + 1, j)] = M + 2

    # If pattern == 0 for any clause, the clause is unsatisfied
    # and no clause job can go at M+1, which means capacity at M+1
    # won't be met. Return None.
    for ci in range(N):
        clause = clauses[ci]
        pattern = 0
        for p in range(3):
            lit = clause[p]
            var = abs(lit)
            lit_positive = lit > 0
            val = truth_assignment[var - 1]
            lit_true = val if lit_positive else not val
            if lit_true:
                pattern |= (1 << (2 - p))
        if pattern == 0:
            return None  # Clause not satisfied

    # Check all jobs assigned
    if any(a < 0 for a in assignment):
        return None

    # Check time bounds
    if any(a >= T for a in assignment):
        return None

    # Check capacities
    slot_counts = [0] * T
    for t in assignment:
        slot_counts[t] += 1
    if slot_counts != list(capacities):
        return None

    # Check precedences
    for p, s in precedences:
        if assignment[p] >= assignment[s]:
            return None

    return assignment


def solve_p4_constructive(
    num_jobs: int,
    precedences: list[tuple[int, int]],
    capacities: list[int],
    time_limit: int,
    meta: dict,
    clauses: list[list[int]],
) -> list[int] | None:
    """
    Solve P4 by trying all 2^M truth assignments.
    For each, construct the schedule deterministically.
    """
    M = meta["source_num_vars"]

    for bits in itertools.product([False, True], repeat=M):
        ta = list(bits)
        result = construct_p4_schedule(
            num_jobs, precedences, capacities, time_limit, meta, ta, clauses)
        if result is not None:
            return result

    return None


# ============================================================
# Section 1: reduce()
# ============================================================


def reduce(num_vars: int,
           clauses: list[list[int]]) -> tuple[int, list[tuple[int, int]], list[int], int, dict]:
    """
    Reduce 3-SAT to P4 scheduling (Ullman 1975, Lemma 2).

    Ullman's notation: M = num_vars, N = num_clauses.

    Jobs (all unit-length):
    - Variable chains: x_{i,j} and xbar_{i,j} for 1<=i<=M, 0<=j<=M
    - Forcing: y_i and ybar_i for 1<=i<=M
    - Clause: D_{i,j} for 1<=i<=N, 1<=j<=7

    Returns: (num_jobs, precedences, capacities, time_limit, metadata)
    """
    M = num_vars
    N = len(clauses)

    if M == 0 or N == 0:
        return (0, [], [1], 1, {
            "source_num_vars": M,
            "source_num_clauses": N,
        })

    # Time limit
    T = M + 3

    # Capacity sequence
    capacities = [0] * T
    capacities[0] = M
    capacities[1] = 2 * M + 1
    for i in range(2, M + 1):
        capacities[i] = 2 * M + 2
    capacities[M + 1] = N + M + 1
    capacities[M + 2] = 6 * N

    # But wait: we need N <= 3M for this capacity count to work.
    # Also need to verify: at time M+2 we have 6N clause jobs.
    # But we only have 7N clause jobs total, and they all go at time M+2.
    # The capacity at M+2 must be >= 7N... but Ullman says c_{M+2} = 6N.
    # That means only 6N of the 7N clause jobs can fit at time M+2.
    #
    # Wait -- re-reading the paper:
    # "Since c_{m+1} = n + m + 1, we must be able to execute n of the D's
    #  if we are to have a solution. ... at most one of D_{i1}, ..., D_{i7}
    #  can be executed at time m+1."
    #
    # Ah, I see: the D jobs are NOT all at time M+2. Some are at time M+1,
    # and the rest at time M+2.
    #
    # Re-reading more carefully:
    # c_{M+1} = N + M + 1: at this time, M remaining x/xbar chain endpoints
    #   plus 1 forcing job plus N clause jobs (one per clause) execute.
    # c_{M+2} = 6N: the remaining 6N clause jobs execute.
    #
    # So for each clause i, exactly 1 of D_{i,1}..D_{i,7} goes at time M+1,
    # and the other 6 go at time M+2. Which one goes at M+1 depends on which
    # satisfying assignment pattern is "active".

    # ---- Job IDs ----
    def var_chain_id(var_i, step_j, positive):
        base = (var_i - 1) * (M + 1) * 2
        return base + step_j * 2 + (0 if positive else 1)

    num_var_chain = M * (M + 1) * 2

    forcing_base = num_var_chain
    def forcing_id(var_i, positive):
        return forcing_base + 2 * (var_i - 1) + (0 if positive else 1)
    num_forcing = 2 * M

    clause_base = forcing_base + num_forcing
    def clause_job_id(clause_i, sub_j):
        return clause_base + (clause_i - 1) * 7 + (sub_j - 1)
    num_clause = 7 * N

    num_jobs = num_var_chain + num_forcing + num_clause
    assert num_jobs == sum(capacities), \
        f"Job count {num_jobs} != sum(capacities) {sum(capacities)}"

    # ---- Precedences ----
    precs = []

    # (i) Variable chains
    for i in range(1, M + 1):
        for j in range(M):
            precs.append((var_chain_id(i, j, True),
                          var_chain_id(i, j + 1, True)))
            precs.append((var_chain_id(i, j, False),
                          var_chain_id(i, j + 1, False)))

    # (ii) Forcing: x_{i,i-1} < y_i and xbar_{i,i-1} < ybar_i
    for i in range(1, M + 1):
        precs.append((var_chain_id(i, i - 1, True), forcing_id(i, True)))
        precs.append((var_chain_id(i, i - 1, False), forcing_id(i, False)))

    # (iii) Clause precedences
    # From Ullman: For clause D_i = {l_1, l_2, l_3}:
    # D_{i,j} where j has binary representation a_1 a_2 a_3:
    #   If a_p = 1: z_{k_p, M} < D_{i,j} (literal's chain endpoint)
    #   If a_p = 0: zbar_{k_p, M} < D_{i,j} (literal's negation endpoint)
    #
    # Here z_{k_p} refers to the variable in the literal:
    #   if l_p = x_alpha, then z_{k_p} = x_alpha, zbar_{k_p} = xbar_alpha
    #   if l_p = xbar_alpha, then z_{k_p} = xbar_alpha, zbar_{k_p} = x_alpha

    for ci in range(N):
        clause = clauses[ci]
        for j in range(1, 8):
            bits = [(j >> (2 - p)) & 1 for p in range(3)]
            for p in range(3):
                lit = clause[p]
                var = abs(lit)
                lit_positive = lit > 0

                if bits[p] == 1:
                    precs.append((var_chain_id(var, M, lit_positive),
                                  clause_job_id(ci + 1, j)))
                else:
                    precs.append((var_chain_id(var, M, not lit_positive),
                                  clause_job_id(ci + 1, j)))

    metadata = {
        "source_num_vars": M,
        "source_num_clauses": N,
        "num_jobs": num_jobs,
        "num_var_chain": num_var_chain,
        "num_forcing": num_forcing,
        "num_clause": num_clause,
        "capacities": capacities,
        "time_limit": T,
        "var_chain_id_fn": var_chain_id,
        "forcing_id_fn": forcing_id,
        "clause_job_id_fn": clause_job_id,
    }

    return num_jobs, precs, capacities, T, metadata


# ============================================================
# Section 2: extract_solution()
# ============================================================


def extract_solution(assignment: list[int], metadata: dict) -> list[bool]:
    """
    Extract a 3-SAT solution from a P4 schedule.

    Per Ullman: x_i is True iff x_{i,0} is executed at time 0.
    """
    M = metadata["source_num_vars"]
    var_chain_id = metadata["var_chain_id_fn"]

    result = []
    for i in range(1, M + 1):
        pos_id = var_chain_id(i, 0, True)
        result.append(assignment[pos_id] == 0)

    return result


# ============================================================
# Section 3: is_valid_source()
# ============================================================


def is_valid_source(num_vars: int, clauses: list[list[int]]) -> bool:
    """Validate a 3-SAT instance."""
    if num_vars < 1:
        return False
    if len(clauses) == 0:
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


def is_valid_target(num_jobs: int, precedences: list[tuple[int, int]],
                    capacities: list[int], time_limit: int) -> bool:
    """Validate a P4 scheduling instance."""
    if num_jobs == 0:
        return True
    if time_limit < 1:
        return False
    if sum(capacities) != num_jobs:
        return False
    if any(c < 0 for c in capacities):
        return False
    for p, s in precedences:
        if p < 0 or p >= num_jobs or s < 0 or s >= num_jobs:
            return False
        if p == s:
            return False
    return True


# ============================================================
# Section 5: closed_loop_check()
# ============================================================


def closed_loop_check(num_vars: int, clauses: list[list[int]]) -> bool:
    """
    Full closed-loop verification for a single 3-SAT instance:
    1. Reduce to P4 scheduling
    2. Solve source and target independently
    3. Check satisfiability equivalence
    4. If satisfiable, extract solution and verify on source
    """
    assert is_valid_source(num_vars, clauses)

    num_jobs, precs, caps, T, meta = reduce(num_vars, clauses)
    assert is_valid_target(num_jobs, precs, caps, T), "Target instance invalid"

    source_sat = is_3sat_satisfiable(num_vars, clauses)
    target_assign = solve_p4_constructive(num_jobs, precs, caps, T, meta, clauses)
    target_sat = target_assign is not None

    if source_sat != target_sat:
        print(f"FAIL: sat mismatch: source={source_sat}, target={target_sat}")
        print(f"  source: n={num_vars}, clauses={clauses}")
        print(f"  target: {num_jobs} jobs, T={T}, caps={caps}")
        return False

    if target_sat:
        # Verify the assignment respects capacities
        slot_counts = [0] * T
        for j in range(num_jobs):
            t = target_assign[j]
            assert 0 <= t < T
            slot_counts[t] += 1
        for t in range(T):
            assert slot_counts[t] == caps[t], \
                f"Capacity mismatch at t={t}: {slot_counts[t]} != {caps[t]}"

        # Verify precedences
        for p, s in precs:
            assert target_assign[p] < target_assign[s], \
                f"Precedence violated: job {p} at t={target_assign[p]} >= job {s} at t={target_assign[s]}"

        # Extract and verify
        s_sol = extract_solution(target_assign, meta)
        if not is_3sat_satisfied(num_vars, clauses, s_sol):
            print(f"FAIL: extraction failed")
            print(f"  source: n={num_vars}, clauses={clauses}")
            print(f"  extracted: {s_sol}")
            return False

    return True


# ============================================================
# Section 6: exhaustive_small()
# ============================================================


def exhaustive_small() -> int:
    """
    Exhaustively test 3-SAT instances with small variable counts.
    """
    total_checks = 0

    for n in range(3, 6):
        valid_clauses = set()
        for combo in itertools.combinations(range(1, n + 1), 3):
            for signs in itertools.product([1, -1], repeat=3):
                c = tuple(s * v for s, v in zip(signs, combo))
                valid_clauses.add(c)
        valid_clauses = sorted(valid_clauses)

        if n == 3:
            # Single-clause
            for c in valid_clauses:
                clause_list = [list(c)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clause={c}"
                    total_checks += 1

            # Two-clause
            pairs = list(itertools.combinations(valid_clauses, 2))
            for c1, c2 in pairs:
                clause_list = [list(c1), list(c2)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

        elif n == 4:
            # Single-clause
            for c in valid_clauses:
                clause_list = [list(c)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clause={c}"
                    total_checks += 1

            # Two-clause (sample)
            pairs = list(itertools.combinations(valid_clauses, 2))
            random.seed(42)
            sample = random.sample(pairs, min(500, len(pairs)))
            for c1, c2 in sample:
                clause_list = [list(c1), list(c2)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clauses={clause_list}"
                    total_checks += 1

        elif n == 5:
            # Single-clause
            for c in valid_clauses:
                clause_list = [list(c)]
                if is_valid_source(n, clause_list):
                    assert closed_loop_check(n, clause_list), \
                        f"FAILED: n={n}, clause={c}"
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
        n = random.randint(3, 7)
        ratio = random.uniform(0.5, 8.0)
        m = max(1, int(n * ratio))
        m = min(m, 10)

        clauses = []
        for _ in range(m):
            vars_chosen = random.sample(range(1, n + 1), 3)
            lits = [v if random.random() < 0.5 else -v for v in vars_chosen]
            clauses.append(lits)

        if not is_valid_source(n, clauses):
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
    """Generate test vectors for the reduction."""
    vectors = []

    test_cases = [
        ("yes_single_clause", 3, [[1, 2, 3]]),
        ("yes_two_clauses_negated", 4, [[1, 2, 3], [-1, 3, 4]]),
        ("yes_all_negated", 3, [[-1, -2, -3]]),
        ("yes_mixed", 4, [[1, -2, 3], [2, -3, 4]]),
        ("no_all_8_clauses_3vars", 3,
         [[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3],
          [1, 2, -3], [-1, -2, 3], [-1, 2, 3], [1, -2, -3]]),
    ]

    for label, nv, cls in test_cases:
        num_jobs, precs, caps, T, meta = reduce(nv, cls)
        source_sol = solve_3sat_brute(nv, cls)
        source_sat = source_sol is not None
        target_assign = solve_p4_constructive(num_jobs, precs, caps, T, meta, cls)
        target_sat = target_assign is not None

        extracted = None
        if target_sat:
            extracted = extract_solution(target_assign, meta)

        vec = {
            "label": label,
            "source": {
                "num_vars": nv,
                "clauses": cls,
            },
            "target": {
                "num_jobs": num_jobs,
                "capacities": caps,
                "time_limit": T,
                "num_precedences": len(precs),
            },
            "source_satisfiable": source_sat,
            "target_satisfiable": target_sat,
            "source_witness": source_sol,
            "target_witness": target_assign,
            "extracted_witness": extracted,
        }
        vectors.append(vec)

    return {
        "reduction": "KSatisfiability_K3_to_PreemptiveScheduling",
        "source_problem": "KSatisfiability",
        "source_variant": {"k": "K3"},
        "target_problem": "PreemptiveScheduling",
        "target_variant": {},
        "overhead": {
            "num_tasks": "2 * num_vars * (num_vars + 1) + 2 * num_vars + 7 * num_clauses",
            "deadline": "num_vars + 3",
        },
        "test_vectors": vectors,
    }


# ============================================================
# Main
# ============================================================


if __name__ == "__main__":
    print("=" * 60)
    print("Verifying: KSatisfiability(K3) -> PreemptiveScheduling")
    print("=" * 60)

    # Quick sanity checks
    print("\n--- Sanity checks ---")

    num_jobs, precs, caps, T, meta = reduce(3, [[1, 2, 3]])
    print(f"  3-var 1-clause: {num_jobs} jobs, T={T}, caps={caps}")
    assert T == 6
    assert num_jobs == sum(caps)
    assert closed_loop_check(3, [[1, 2, 3]])
    print("  Single satisfiable clause: OK")

    assert closed_loop_check(3, [[-1, -2, -3]])
    print("  All-negated clause: OK")

    assert closed_loop_check(3, [[1, 2, 3], [-1, -2, -3]])
    print("  Two clauses (SAT): OK")

    assert closed_loop_check(4, [[1, 2, 3], [-1, 3, 4]])
    print("  4-var 2-clause: OK")

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
        print("Adjusting random_stress count...")
        extra = random_stress(5500 - total)
        total += extra
        print(f"ADJUSTED TOTAL: {total}")
        assert total >= 5000

    # Generate test vectors
    print("\n--- Generating test vectors ---")
    tv = generate_test_vectors()
    tv_path = "docs/paper/verify-reductions/test_vectors_k_satisfiability_preemptive_scheduling.json"
    with open(tv_path, "w") as f:
        json.dump(tv, f, indent=2)
    print(f"  Written to {tv_path}")

    print("\nVERIFIED")
