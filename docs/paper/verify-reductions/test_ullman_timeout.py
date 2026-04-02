#!/usr/bin/env python3
"""Test Ullman P4 with large timeout."""

import itertools
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


def solve_p4(ntasks, t_limit, caps, precs, max_calls=50000000):
    """P4 solver with high timeout."""
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
        return "cycle"

    earliest = [0] * ntasks
    for t in topo:
        for s in succs[t]:
            earliest[s] = max(earliest[s], earliest[t] + 1)
    latest = [t_limit - 1] * ntasks
    for t in reversed(topo):
        for s in succs[t]:
            latest[t] = min(latest[t], latest[s] - 1)
        if latest[t] < earliest[t]:
            return "infeasible_bounds"

    schedule = [-1] * ntasks
    slot_count = [0] * t_limit
    calls = [0]

    # Remaining capacity tracking for pruning
    remaining_tasks = [0] * t_limit
    for t in range(ntasks):
        for s in range(earliest[t], latest[t] + 1):
            remaining_tasks[s] += 1  # Not exact but gives upper bound

    def backtrack(idx):
        calls[0] += 1
        if calls[0] > max_calls:
            return "timeout"
        if idx == ntasks:
            for i in range(t_limit):
                if slot_count[i] != caps[i]:
                    return False
            return True
        t = topo[idx]
        for slot in range(earliest[t], latest[t] + 1):
            if slot_count[slot] >= caps[slot]:
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
            if result == "timeout":
                schedule[t] = -1
                slot_count[slot] -= 1
                return "timeout"
            schedule[t] = -1
            slot_count[slot] -= 1
        return False

    result = backtrack(0)
    if result is True:
        return list(schedule)
    return result


# Test the problematic case
print("Testing [[1,2,3], [-1,-2,-3]] (SAT, assignment x1=T x2=T x3=F)")
clauses = [[1, 2, 3], [-1, -2, -3]]
sat = is_3sat_satisfiable(3, clauses)
print(f"  Source SAT: {sat}")

ntasks, t_limit, c, precs, task_id = build_p4(3, clauses)
print(f"  P4: {ntasks} tasks, {t_limit} slots, caps={c}")
print(f"  Precs: {len(precs)}")

result = solve_p4(ntasks, t_limit, c, precs, max_calls=10000000)
if isinstance(result, list):
    print(f"  FEASIBLE! (calls used)")
    assignment = [result[task_id[('x', i, 0)]] == 0 for i in range(1, 4)]
    print(f"  Assignment: {assignment}")
    print(f"  Satisfies: {is_3sat_satisfied(3, clauses, assignment)}")
elif result == "timeout":
    print(f"  TIMEOUT")
else:
    print(f"  Result: {result}")

# Also test single clause with high timeout
print("\nTesting [[1,2,3]] (trivially SAT)")
clauses2 = [[1, 2, 3]]
ntasks2, t2, c2, precs2, tid2 = build_p4(3, clauses2)
result2 = solve_p4(ntasks2, t2, c2, precs2, max_calls=10000000)
if isinstance(result2, list):
    print(f"  FEASIBLE")
else:
    print(f"  Result: {result2}")

# Test all 8 clauses (UNSAT) with high timeout
print("\nTesting all 8 clauses (UNSAT)")
all_8 = []
for signs in itertools.product([1, -1], repeat=3):
    all_8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])
ntasks8, t8, c8, precs8, tid8 = build_p4(3, all_8)
print(f"  P4: {ntasks8} tasks, {t8} slots, caps={c8}")
result8 = solve_p4(ntasks8, t8, c8, precs8, max_calls=10000000)
if isinstance(result8, list):
    print(f"  FEASIBLE (FALSE POSITIVE!)")
elif result8 == "timeout":
    print(f"  TIMEOUT")
else:
    print(f"  Result: {result8}")
