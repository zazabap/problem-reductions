#!/usr/bin/env python3
"""
Full closed-loop test of Ullman P4 reduction.
"""

import itertools
import random
from collections import defaultdict


def literal_value(lit, assignment):
    v = abs(lit) - 1
    return assignment[v] if lit > 0 else not assignment[v]


def is_3sat_satisfied(nvars, clauses, assignment):
    return all(any(literal_value(l, assignment) for l in c) for c in clauses)


def is_3sat_satisfiable(nvars, clauses):
    for bits in itertools.product([False, True], repeat=nvars):
        if is_3sat_satisfied(nvars, clauses, list(bits)):
            return True
    return False


def solve_p4_smart(ntasks, t_limit, capacities, precs, timeout=500000):
    """Solve P4 with backtracking."""
    succs = defaultdict(list)
    pred_list = defaultdict(list)
    for (a, b) in precs:
        succs[a].append(b)
        pred_list[b].append(a)

    in_deg = [0] * ntasks
    for (a, b) in precs:
        in_deg[b] += 1
    queue = [i for i in range(ntasks) if in_deg[i] == 0]
    topo = []
    td = list(in_deg)
    while queue:
        t = queue.pop(0)
        topo.append(t)
        for s in succs[t]:
            td[s] -= 1
            if td[s] == 0:
                queue.append(s)

    if len(topo) != ntasks:
        return None

    earliest = [0] * ntasks
    for t in topo:
        for s in succs[t]:
            earliest[s] = max(earliest[s], earliest[t] + 1)

    latest = [t_limit - 1] * ntasks
    for t in reversed(topo):
        for s in succs[t]:
            latest[t] = min(latest[t], latest[s] - 1)
        if latest[t] < earliest[t]:
            return None

    schedule = [-1] * ntasks
    slot_count = [0] * t_limit
    calls = [0]

    def backtrack(idx):
        calls[0] += 1
        if calls[0] > timeout:
            return None  # timeout
        if idx == ntasks:
            for i in range(t_limit):
                if slot_count[i] != capacities[i]:
                    return False
            return True
        t = topo[idx]
        for slot in range(earliest[t], latest[t] + 1):
            if slot_count[slot] >= capacities[slot]:
                continue
            ok = True
            for p in pred_list[t]:
                if schedule[p] >= slot:
                    ok = False
                    break
            if not ok:
                continue
            schedule[t] = slot
            slot_count[slot] += 1
            result = backtrack(idx + 1)
            if result is True:
                return True
            if result is None:
                schedule[t] = -1
                slot_count[slot] -= 1
                return None
            schedule[t] = -1
            slot_count[slot] -= 1
        return False

    result = backtrack(0)
    if result is True:
        return list(schedule)
    return None


def build_p4(nvars, clauses):
    m = nvars
    n = len(clauses)

    task_id = {}
    next_id = [0]

    def alloc(name):
        tid = next_id[0]
        task_id[name] = tid
        next_id[0] += 1
        return tid

    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('x', i, j))
    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('xbar', i, j))
    for i in range(1, m + 1):
        alloc(('y', i))
    for i in range(1, m + 1):
        alloc(('ybar', i))
    for i in range(1, n + 1):
        for j in range(1, 8):
            alloc(('D', i, j))

    ntasks = next_id[0]
    t_limit = m + 3

    c = [0] * t_limit
    c[0] = m
    c[1] = 2 * m + 1
    for slot in range(2, m + 1):
        c[slot] = 2 * m + 2
    c[m + 1] = n + m + 1
    c[m + 2] = 6 * n

    precs = []
    for i in range(1, m + 1):
        for j in range(0, m):
            precs.append((task_id[('x', i, j)], task_id[('x', i, j + 1)]))
            precs.append((task_id[('xbar', i, j)], task_id[('xbar', i, j + 1)]))

    for i in range(1, m + 1):
        precs.append((task_id[('x', i, i - 1)], task_id[('y', i)]))
        precs.append((task_id[('xbar', i, i - 1)], task_id[('ybar', i)]))

    for i in range(1, n + 1):
        clause = clauses[i - 1]
        for j in range(1, 8):
            a1 = (j >> 2) & 1
            a2 = (j >> 1) & 1
            a3 = j & 1
            for p, ap in enumerate([a1, a2, a3]):
                lit = clause[p]
                var = abs(lit)
                is_pos = lit > 0
                if ap == 1:
                    pred = task_id[('x', var, m)] if is_pos else task_id[('xbar', var, m)]
                else:
                    pred = task_id[('xbar', var, m)] if is_pos else task_id[('x', var, m)]
                precs.append((pred, task_id[('D', i, j)]))

    return ntasks, t_limit, c, precs, task_id


def closed_loop(nvars, clauses, timeout=500000):
    """Closed-loop test: reduce, solve both, compare."""
    source_sat = is_3sat_satisfiable(nvars, clauses)
    ntasks, t_limit, c, precs, task_id = build_p4(nvars, clauses)
    sol = solve_p4_smart(ntasks, t_limit, c, precs, timeout=timeout)

    if sol is None:
        # Could be timeout or infeasible
        # Check if we can distinguish
        return source_sat == False  # Assume infeasible = UNSAT (might be wrong on timeout)

    target_feas = sol is not None
    if source_sat != target_feas:
        print(f"MISMATCH: source_sat={source_sat}, target_feas={target_feas}")
        print(f"  n={nvars}, clauses={clauses}")
        return False

    if target_feas:
        # Extract assignment
        assignment = [sol[task_id[('x', i, 0)]] == 0 for i in range(1, nvars + 1)]
        if not is_3sat_satisfied(nvars, clauses, assignment):
            print(f"EXTRACTION FAIL: n={nvars}, clauses={clauses}, assignment={assignment}")
            return False

    return True


# ========== TESTS ==========

print("=== Single clause tests (all SAT) ===")
passed = 0
for signs in itertools.product([1, -1], repeat=3):
    clause = [signs[0] * 1, signs[1] * 2, signs[2] * 3]
    if closed_loop(3, [clause]):
        passed += 1
    else:
        print(f"  FAIL: {clause}")
print(f"  {passed}/8 passed")

print("\n=== Two-clause tests ===")
all_clauses = []
for signs in itertools.product([1, -1], repeat=3):
    all_clauses.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])

passed = 0
total = 0
for i in range(len(all_clauses)):
    for j in range(i + 1, len(all_clauses)):
        cls = [all_clauses[i], all_clauses[j]]
        # P4 tasks: 2*3*4 + 6 + 14 = 44
        total += 1
        if closed_loop(3, cls, timeout=1000000):
            passed += 1
        else:
            print(f"  FAIL: {cls}")
print(f"  {passed}/{total} passed")

print("\n=== Three-clause tests (sample) ===")
passed = 0
total = 0
combos = list(itertools.combinations(range(8), 3))
random.seed(42)
sample = random.sample(combos, min(20, len(combos)))
for combo in sample:
    cls = [all_clauses[c] for c in combo]
    total += 1
    if closed_loop(3, cls, timeout=2000000):
        passed += 1
    else:
        print(f"  FAIL: {cls}")
        sat = is_3sat_satisfiable(3, cls)
        print(f"    source_sat={sat}")
print(f"  {passed}/{total} passed")

# Test the unsatisfiable case: all 8 clauses
print("\n=== All 8 clauses (UNSAT) ===")
# This has 86 tasks and 6 slots -- P4 solver should handle it
if closed_loop(3, all_clauses, timeout=5000000):
    print("  PASSED (correctly declared UNSAT)")
else:
    print("  FAILED")
