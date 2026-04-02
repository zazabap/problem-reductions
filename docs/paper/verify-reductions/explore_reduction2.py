#!/usr/bin/env python3
"""Deeper exploration: test D and E constructions with UNSAT cases and n=4,5."""

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


def reduce_D(n, clauses):
    """Complement-predecessor, D=3, procs adjusted."""
    m = len(clauses)
    ntasks = 2 * n + m
    procs = max(n, (ntasks + 2) // 3)
    D = 3
    precs = []
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


def reduce_E(n, clauses):
    """Same-literal predecessor, D=3, procs adjusted."""
    m = len(clauses)
    ntasks = 2 * n + m
    procs = max(n, (ntasks + 2) // 3)
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


# Focus on UNSAT instances
print("=== Testing UNSAT instances ===")

# The only n=3 UNSAT with 3 vars and clauses on {1,2,3}: all 8 sign combos
all_8 = []
for signs in itertools.product([1, -1], repeat=3):
    all_8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])

# Confirm UNSAT
assert not is_3sat_satisfiable(3, all_8), "all 8 clauses should be UNSAT"
print(f"All 8 clauses on 3 vars: UNSAT confirmed")

# Test with all 8 clauses
ntasks, nproc, D, precs = reduce_D(3, all_8)
print(f"  Construction D: tasks={ntasks}, procs={nproc}, D={D}")
print(f"  Search space: {D}^{ntasks} = {D**ntasks}")
if D ** ntasks <= 2000000:
    result = is_pcs_feasible(ntasks, nproc, D, precs)
    print(f"  PCS feasible: {result} (should be False)")
else:
    print(f"  TOO LARGE to test")

ntasks, nproc, D, precs = reduce_E(3, all_8)
print(f"  Construction E: tasks={ntasks}, procs={nproc}, D={D}")
if D ** ntasks <= 2000000:
    result = is_pcs_feasible(ntasks, nproc, D, precs)
    print(f"  PCS feasible: {result} (should be False)")
else:
    print(f"  TOO LARGE to test")

# Generate UNSAT instances with n=4
print("\n=== n=4 UNSAT instances ===")
unsat_count = 0
random.seed(42)

# Generate random instances near phase transition (ratio ~4.27)
for trial in range(200):
    n = 4
    m = random.randint(8, 12)  # High clause ratio for UNSAT
    clauses = []
    for _ in range(m):
        vs = random.sample(range(1, n + 1), 3)
        lits = [v if random.random() < 0.5 else -v for v in vs]
        clauses.append(lits)

    if not is_3sat_satisfiable(n, clauses):
        unsat_count += 1
        ntasks_d, nproc_d, D_d, precs_d = reduce_D(n, clauses)
        ntasks_e, nproc_e, D_e, precs_e = reduce_E(n, clauses)

        if D_d ** ntasks_d <= 500000:
            result_d = is_pcs_feasible(ntasks_d, nproc_d, D_d, precs_d)
            if result_d:
                print(f"  D FALSE-POSITIVE: n={n}, m={m}, clauses={clauses[:3]}...")
        if D_e ** ntasks_e <= 500000:
            result_e = is_pcs_feasible(ntasks_e, nproc_e, D_e, precs_e)
            if result_e:
                print(f"  E FALSE-POSITIVE: n={n}, m={m}, clauses={clauses[:3]}...")

        if unsat_count >= 20:
            break

print(f"Tested {unsat_count} UNSAT instances for n=4")

# Test more carefully: n=3, small UNSAT
# Find all UNSAT subsets of all_8 with <= 8 clauses
print("\n=== Systematic n=3 UNSAT search ===")
tested = 0
d_fp = 0
e_fp = 0
for size in range(4, 9):
    for combo in itertools.combinations(range(8), size):
        cls = [all_8[c] for c in combo]
        if not is_3sat_satisfiable(3, cls):
            ntasks, nproc, D, precs = reduce_D(3, cls)
            if D ** ntasks <= 500000:
                if is_pcs_feasible(ntasks, nproc, D, precs):
                    d_fp += 1
                    if d_fp <= 3:
                        print(f"  D FALSE-POS: clauses={cls}")
                tested += 1

            ntasks, nproc, D, precs = reduce_E(3, cls)
            if D ** ntasks <= 500000:
                if is_pcs_feasible(ntasks, nproc, D, precs):
                    e_fp += 1
                    if e_fp <= 3:
                        print(f"  E FALSE-POS: clauses={cls}")

print(f"Tested {tested} UNSAT combos. D false-pos: {d_fp}, E false-pos: {e_fp}")

# n=3, SAT instances with 2 clauses (where D=2 constructions failed)
print("\n=== n=3 SAT, 2 clauses (problematic for D=2) ===")
problematic = [
    [[1, 2, 3], [-1, -2, -3]],
    [[1, 2, -3], [-1, -2, 3]],
    [[1, -2, 3], [-1, 2, -3]],
    [[1, -2, -3], [-1, 2, 3]],
]
for cls in problematic:
    assert is_3sat_satisfiable(3, cls)
    ntasks, nproc, D, precs = reduce_D(3, cls)
    result = is_pcs_feasible(ntasks, nproc, D, precs)
    print(f"  D: clauses={cls} -> feasible={result} (should be True)")

    ntasks, nproc, D, precs = reduce_E(3, cls)
    result = is_pcs_feasible(ntasks, nproc, D, precs)
    print(f"  E: clauses={cls} -> feasible={result} (should be True)")
