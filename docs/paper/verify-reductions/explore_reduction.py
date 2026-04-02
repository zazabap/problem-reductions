#!/usr/bin/env python3
"""Explore different reduction constructions for 3-SAT -> PCS."""

import itertools
import random


def literal_value(lit, assignment):
    v = abs(lit) - 1
    val = assignment[v]
    return val if lit > 0 else not val


def is_3sat_satisfied(n, clauses, assignment):
    for clause in clauses:
        if not any(literal_value(l, assignment) for l in clause):
            return False
    return True


def is_3sat_satisfiable(n, clauses):
    for bits in itertools.product([False, True], repeat=n):
        if is_3sat_satisfied(n, clauses, list(bits)):
            return True
    return False


def is_schedule_feasible(ntasks, nproc, D, precs, sched):
    if len(sched) != ntasks:
        return False
    for s in sched:
        if s < 0 or s >= D:
            return False
    slot_count = [0] * D
    for s in sched:
        slot_count[s] += 1
        if slot_count[s] > nproc:
            return False
    for (i, j) in precs:
        if sched[j] < sched[i] + 1:
            return False
    return True


def is_pcs_feasible(ntasks, nproc, D, precs):
    for sched in itertools.product(range(D), repeat=ntasks):
        if is_schedule_feasible(ntasks, nproc, D, precs, list(sched)):
            return True
    return False


# ========================================================
# CONSTRUCTION D: Complement-predecessor, D=3, procs=n
# Clause task depends on complement-literal tasks.
# With D=3 and procs=n, capacity=3n. Tasks=2n+m. Need m<=n.
# ========================================================
def reduce_D(n, clauses):
    m = len(clauses)
    ntasks = 2 * n + m
    procs = n
    if ntasks > 3 * procs:
        # Increase procs
        procs = (ntasks + 2) // 3
    D = 3
    precs = []
    for j, clause in enumerate(clauses):
        cl = 2 * n + j
        for lit in clause:
            v = abs(lit) - 1
            if lit > 0:
                comp = 2 * v + 1  # neg task
            else:
                comp = 2 * v      # pos task
            precs.append((comp, cl))
    return ntasks, procs, D, precs


# ========================================================
# CONSTRUCTION E: Same-literal predecessor, D=3, procs=n
# ========================================================
def reduce_E(n, clauses):
    m = len(clauses)
    ntasks = 2 * n + m
    procs = n
    if ntasks > 3 * procs:
        procs = (ntasks + 2) // 3
    D = 3
    precs = []
    for j, clause in enumerate(clauses):
        cl = 2 * n + j
        for lit in clause:
            v = abs(lit) - 1
            if lit > 0:
                task = 2 * v
            else:
                task = 2 * v + 1
            precs.append((task, cl))
    return ntasks, procs, D, precs


# ========================================================
# CONSTRUCTION F: Variable chains + complement-predecessor, D=3, procs=n
# pos_i -> neg_i chain for each variable.
# Clause depends on complement.
# ========================================================
def reduce_F(n, clauses):
    m = len(clauses)
    ntasks = 2 * n + m
    procs = n
    if ntasks > 3 * procs:
        procs = (ntasks + 2) // 3
    D = 3
    precs = []
    # Variable chains
    for i in range(n):
        precs.append((2 * i, 2 * i + 1))
    # Clause tasks depend on complement-literal tasks
    for j, clause in enumerate(clauses):
        cl = 2 * n + j
        for lit in clause:
            v = abs(lit) - 1
            if lit > 0:
                comp = 2 * v + 1
            else:
                comp = 2 * v
            precs.append((comp, cl))
    return ntasks, procs, D, precs


# ========================================================
# CONSTRUCTION G: Variable chains + same-literal predecessor, D=3, procs=n
# pos_i -> neg_i chain for each variable.
# Clause depends on same literal.
# ========================================================
def reduce_G(n, clauses):
    m = len(clauses)
    ntasks = 2 * n + m
    procs = n
    if ntasks > 3 * procs:
        procs = (ntasks + 2) // 3
    D = 3
    precs = []
    # Variable chains
    for i in range(n):
        precs.append((2 * i, 2 * i + 1))
    # Clause tasks depend on same-literal tasks
    for j, clause in enumerate(clauses):
        cl = 2 * n + j
        for lit in clause:
            v = abs(lit) - 1
            if lit > 0:
                task = 2 * v
            else:
                task = 2 * v + 1
            precs.append((task, cl))
    return ntasks, procs, D, precs


# ========================================================
# CONSTRUCTION H: Variable chains, clause depends on complement,
# D=3, procs=n, ADD PADDING to fill capacity exactly
# ========================================================
def reduce_H(n, clauses):
    m = len(clauses)
    procs = n
    D = 3
    real_tasks = 2 * n + m
    total_capacity = D * procs
    if real_tasks > total_capacity:
        procs = (real_tasks + D - 1) // D
        total_capacity = D * procs
    padding = total_capacity - real_tasks
    ntasks = real_tasks + padding

    precs = []
    # Variable chains
    for i in range(n):
        precs.append((2 * i, 2 * i + 1))
    # Clause tasks depend on complement-literal tasks
    for j, clause in enumerate(clauses):
        cl = 2 * n + j
        for lit in clause:
            v = abs(lit) - 1
            if lit > 0:
                comp = 2 * v + 1
            else:
                comp = 2 * v
            precs.append((comp, cl))
    # Padding tasks (2n+m .. ntasks-1) have no precedences
    return ntasks, procs, D, precs


def test_construction(name, reduce_fn, test_cases):
    """Test a construction against known test cases."""
    passed = 0
    failed = 0
    false_pos = 0  # PCS says feasible but formula is UNSAT
    false_neg = 0  # PCS says infeasible but formula is SAT
    for n, clauses, expected_sat in test_cases:
        result = reduce_fn(n, clauses)
        if result is None:
            continue
        ntasks, nproc, D, precs = result
        # Skip if too large
        if D ** ntasks > 500000:
            continue
        target_feasible = is_pcs_feasible(ntasks, nproc, D, precs)
        if target_feasible == expected_sat:
            passed += 1
        else:
            failed += 1
            if target_feasible and not expected_sat:
                false_pos += 1
            else:
                false_neg += 1
            if failed <= 3:
                print(f"  {name}: FAIL n={n}, clauses={clauses} "
                      f"expected_sat={expected_sat}, pcs_feasible={target_feasible}")
    print(f"  {name}: {passed} passed, {failed} failed "
          f"(false_pos={false_pos}, false_neg={false_neg})")
    return failed == 0


# Generate test cases including UNSAT instances
test_cases = []
n = 3

# All 8 possible sign patterns for a single clause on vars {1,2,3}
all_clauses_3 = []
for signs in itertools.product([1, -1], repeat=3):
    c = [signs[0] * 1, signs[1] * 2, signs[2] * 3]
    all_clauses_3.append(c)

# Single clause (all SAT)
for c in all_clauses_3:
    test_cases.append((3, [c], True))

# Two clauses
for i in range(len(all_clauses_3)):
    for j in range(i + 1, len(all_clauses_3)):
        cls = [all_clauses_3[i], all_clauses_3[j]]
        sat = is_3sat_satisfiable(3, cls)
        test_cases.append((3, cls, sat))

# Three clauses (sampled)
for i in range(len(all_clauses_3)):
    for j in range(i + 1, len(all_clauses_3)):
        for k in range(j + 1, len(all_clauses_3)):
            cls = [all_clauses_3[i], all_clauses_3[j], all_clauses_3[k]]
            sat = is_3sat_satisfiable(3, cls)
            test_cases.append((3, cls, sat))

# Four and more clauses (more UNSAT likely)
for size in [4, 5, 6, 7, 8]:
    for combo in itertools.combinations(range(len(all_clauses_3)), size):
        cls = [all_clauses_3[c] for c in combo]
        sat = is_3sat_satisfiable(3, cls)
        test_cases.append((3, cls, sat))

# n=4 single clause
for combo in itertools.combinations(range(1, 5), 3):
    for signs in itertools.product([1, -1], repeat=3):
        c = [s * v for s, v in zip(signs, combo)]
        test_cases.append((4, [c], True))

print(f"Generated {len(test_cases)} test cases")
sat_count = sum(1 for _, _, s in test_cases if s)
unsat_count = sum(1 for _, _, s in test_cases if not s)
print(f"  SAT: {sat_count}, UNSAT: {unsat_count}")

print("\nTesting Construction D (complement-pred, D=3, procs=n):")
test_construction("D", reduce_D, test_cases)

print("\nTesting Construction E (same-literal-pred, D=3, procs=n):")
test_construction("E", reduce_E, test_cases)

print("\nTesting Construction F (chains + complement-pred, D=3, procs=n):")
test_construction("F", reduce_F, test_cases)

print("\nTesting Construction G (chains + same-literal-pred, D=3, procs=n):")
test_construction("G", reduce_G, test_cases)

print("\nTesting Construction H (chains + complement-pred, D=3, procs=n, PADDING):")
test_construction("H", reduce_H, test_cases)
