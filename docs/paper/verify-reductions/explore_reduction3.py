#!/usr/bin/env python3
"""
Test constructions D and E with a smarter PCS solver (topological + backtracking).
Focus on UNSAT detection.
"""

import itertools
import random
from collections import defaultdict


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


def solve_3sat_brute(n, clauses):
    for bits in itertools.product([False, True], repeat=n):
        a = list(bits)
        if is_3sat_satisfied(n, clauses, a):
            return a
    return None


def is_schedule_feasible(ntasks, nproc, D, precs, sched):
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


def solve_pcs_smart(ntasks, nproc, D, precs):
    """
    Smarter PCS solver using constraint propagation + backtracking.
    """
    # Build adjacency: for each task, list of (predecessor, successor) pairs
    successors = defaultdict(list)
    predecessors = defaultdict(list)
    for (i, j) in precs:
        successors[i].append(j)
        predecessors[j].append(i)

    # Compute earliest possible slot for each task (forward pass)
    earliest = [0] * ntasks
    # Topological order
    in_degree = [0] * ntasks
    for (i, j) in precs:
        in_degree[j] += 1
    queue = [i for i in range(ntasks) if in_degree[i] == 0]
    topo = []
    while queue:
        t = queue.pop(0)
        topo.append(t)
        for s in successors[t]:
            earliest[s] = max(earliest[s], earliest[t] + 1)
            in_degree[s] -= 1
            if in_degree[s] == 0:
                queue.append(s)

    if len(topo) != ntasks:
        return None  # Cycle in precedences

    # Check if earliest slots are feasible
    for t in range(ntasks):
        if earliest[t] >= D:
            return None  # Task can't be scheduled

    # Compute latest possible slot (backward pass)
    latest = [D - 1] * ntasks
    for t in reversed(topo):
        for s in successors[t]:
            latest[t] = min(latest[t], latest[s] - 1)
        if latest[t] < earliest[t]:
            return None  # Infeasible

    # Backtracking with constraint propagation
    schedule = [-1] * ntasks
    slot_count = [0] * D

    def backtrack(idx):
        if idx == ntasks:
            return True
        t = topo[idx]
        lo = earliest[t]
        hi = latest[t]
        for slot in range(lo, hi + 1):
            if slot_count[slot] >= nproc:
                continue
            # Check precedences
            ok = True
            for p in predecessors[t]:
                if schedule[p] < 0 or schedule[p] + 1 > slot:
                    ok = False
                    break
            if not ok:
                continue
            schedule[t] = slot
            slot_count[slot] += 1
            if backtrack(idx + 1):
                return True
            schedule[t] = -1
            slot_count[slot] -= 1
        return False

    if backtrack(0):
        return schedule
    return None


def reduce_D(n, clauses):
    """Complement-predecessor, D=3, procs adjusted, no chains."""
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
    """Same-literal predecessor, D=3, procs adjusted, no chains."""
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


# Test UNSAT: all 8 clauses on 3 vars
all_8 = []
for signs in itertools.product([1, -1], repeat=3):
    all_8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])

assert not is_3sat_satisfiable(3, all_8)

print("=== All 8 clauses (UNSAT) ===")
for name, reduce_fn in [("D", reduce_D), ("E", reduce_E)]:
    ntasks, nproc, D, precs = reduce_fn(3, all_8)
    sol = solve_pcs_smart(ntasks, nproc, D, precs)
    print(f"  {name}: tasks={ntasks}, procs={nproc}, D={D}, feasible={sol is not None}")
    if sol is not None:
        print(f"    FALSE POSITIVE! Schedule: {sol}")

# Test all subsets of size 4-8 of all_8
print("\n=== Subsets of all_8 (UNSAT subsets) ===")
d_fp = 0
e_fp = 0
d_total = 0
e_total = 0
for size in range(4, 9):
    for combo in itertools.combinations(range(8), size):
        cls = [all_8[c] for c in combo]
        sat = is_3sat_satisfiable(3, cls)
        if not sat:
            for name, reduce_fn, fp_counter in [("D", reduce_D, "d"), ("E", reduce_E, "e")]:
                ntasks, nproc, D, precs = reduce_fn(3, cls)
                sol = solve_pcs_smart(ntasks, nproc, D, precs)
                if name == "D":
                    d_total += 1
                    if sol is not None:
                        d_fp += 1
                        if d_fp <= 3:
                            print(f"  D FALSE-POS: size={size}, clauses={cls}")
                            print(f"    Schedule: {sol}")
                else:
                    e_total += 1
                    if sol is not None:
                        e_fp += 1
                        if e_fp <= 3:
                            print(f"  E FALSE-POS: size={size}, clauses={cls}")
                            print(f"    Schedule: {sol}")

print(f"\nD: {d_total} UNSAT tested, {d_fp} false positives")
print(f"E: {e_total} UNSAT tested, {e_fp} false positives")

# Test n=4 random UNSAT
print("\n=== n=4 random instances ===")
random.seed(42)
sat_ok = 0
unsat_ok = 0
d_fp4 = 0
e_fp4 = 0
d_fn4 = 0
e_fn4 = 0

for trial in range(500):
    n = 4
    m = random.randint(1, 8)
    clauses = []
    valid = True
    for _ in range(m):
        vs = random.sample(range(1, n + 1), 3)
        lits = [v if random.random() < 0.5 else -v for v in vs]
        clauses.append(lits)

    sat = is_3sat_satisfiable(n, clauses)

    for name, reduce_fn in [("D", reduce_D), ("E", reduce_E)]:
        ntasks, nproc, D, precs = reduce_fn(n, clauses)
        sol = solve_pcs_smart(ntasks, nproc, D, precs)
        pcs_feasible = sol is not None

        if sat and not pcs_feasible:
            if name == "D":
                d_fn4 += 1
                if d_fn4 <= 2:
                    print(f"  {name} FALSE-NEG: n={n}, m={m}, sat={sat}, clauses={clauses}")
            else:
                e_fn4 += 1
        elif not sat and pcs_feasible:
            if name == "D":
                d_fp4 += 1
                if d_fp4 <= 2:
                    print(f"  {name} FALSE-POS: n={n}, m={m}, sat={sat}, clauses={clauses}")
                    print(f"    Schedule: {sol}")
            else:
                e_fp4 += 1
                if e_fp4 <= 2:
                    print(f"  {name} FALSE-POS: n={n}, m={m}, sat={sat}, clauses={clauses}")
                    print(f"    Schedule: {sol}")

print(f"\nn=4: D false-pos={d_fp4}, D false-neg={d_fn4}")
print(f"n=4: E false-pos={e_fp4}, E false-neg={e_fn4}")

# Also test extraction for E (same-literal)
print("\n=== Extraction test for E ===")
for trial in range(100):
    n = random.randint(3, 5)
    m = random.randint(1, 3)
    clauses = []
    for _ in range(m):
        vs = random.sample(range(1, n + 1), 3)
        lits = [v if random.random() < 0.5 else -v for v in vs]
        clauses.append(lits)

    sat = is_3sat_satisfiable(n, clauses)
    if not sat:
        continue

    ntasks, nproc, D, precs = reduce_E(n, clauses)
    sol = solve_pcs_smart(ntasks, nproc, D, precs)
    if sol is None:
        print(f"  E: SHOULD BE FEASIBLE but got None: n={n}, clauses={clauses}")
        continue

    # Extract: x_i = TRUE if pos_i in slot 0
    assignment = [sol[2 * i] == 0 for i in range(n)]
    if not is_3sat_satisfied(n, clauses, assignment):
        # Try: x_i = TRUE if pos_i <= neg_i
        assignment2 = [sol[2*i] <= sol[2*i+1] for i in range(n)]
        if not is_3sat_satisfied(n, clauses, assignment2):
            print(f"  E EXTRACTION FAIL: n={n}, clauses={clauses}")
            print(f"    Schedule: {sol}")
            print(f"    Assignment1: {assignment}")
            print(f"    Assignment2: {assignment2}")

print("Extraction test done.")
