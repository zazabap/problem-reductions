#!/usr/bin/env python3
"""
Verify the Ullman P4 reduction directly.

P4: variable-capacity scheduling.
Given n jobs, relation <, time limit t, capacities c_0..c_{t-1} with sum = n.
Find f: jobs -> {0..t-1} such that:
  - f^{-1}(i) has exactly c_i members
  - if J < J', then f(J) < f(J')

Note: P4 requires EXACTLY c_i jobs per slot (not "at most").
"""

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


def solve_3sat_brute(nvars, clauses):
    for bits in itertools.product([False, True], repeat=nvars):
        a = list(bits)
        if is_3sat_satisfied(nvars, clauses, a):
            return a
    return None


def is_p4_feasible_sched(ntasks, t_limit, capacities, precs, schedule):
    """Check P4 feasibility: EXACT capacities, precedence."""
    if len(schedule) != ntasks:
        return False
    slot_count = [0] * t_limit
    for s in schedule:
        if s < 0 or s >= t_limit:
            return False
        slot_count[s] += 1
    for i in range(t_limit):
        if slot_count[i] != capacities[i]:
            return False
    for (a, b) in precs:
        if schedule[a] >= schedule[b]:
            return False
    return True


def solve_p4_smart(ntasks, t_limit, capacities, precs):
    """Solve P4 with backtracking + constraint propagation."""
    succs = defaultdict(list)
    preds = defaultdict(list)
    for (a, b) in precs:
        succs[a].append(b)
        preds[b].append(a)

    # Topological sort
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
        return None  # cycle

    # Earliest and latest
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

    def backtrack(idx):
        if idx == ntasks:
            # Check exact capacities
            for i in range(t_limit):
                if slot_count[i] != capacities[i]:
                    return False
            return True
        t = topo[idx]
        remaining = ntasks - idx
        # Prune: check if remaining tasks can fill remaining capacity
        for slot in range(earliest[t], latest[t] + 1):
            if slot_count[slot] >= capacities[slot]:
                continue
            ok = True
            for p in preds[t]:
                if schedule[p] >= slot:
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


def build_p4(nvars, clauses):
    """
    Build Ullman P4 instance from 3-SAT.

    Variables: x_1..x_m (m=nvars), 1-indexed
    Clauses: D_1..D_n (n=len(clauses)), 1-indexed
    """
    m = nvars
    n = len(clauses)

    task_id = {}
    next_id = [0]

    def alloc(name):
        tid = next_id[0]
        task_id[name] = tid
        next_id[0] += 1
        return tid

    # x_{i,j} and xbar_{i,j} for i=1..m, j=0..m
    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('x', i, j))
    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('xbar', i, j))

    # y_i, ybar_i for i=1..m
    for i in range(1, m + 1):
        alloc(('y', i))
    for i in range(1, m + 1):
        alloc(('ybar', i))

    # D_{i,j} for i=1..n, j=1..7
    for i in range(1, n + 1):
        for j in range(1, 8):
            alloc(('D', i, j))

    ntasks = next_id[0]
    t_limit = m + 3

    # Capacities
    c = [0] * t_limit
    c[0] = m
    c[1] = 2 * m + 1
    for slot in range(2, m + 1):
        c[slot] = 2 * m + 2
    c[m + 1] = n + m + 1
    c[m + 2] = 6 * n

    assert sum(c) == ntasks, f"cap sum {sum(c)} != {ntasks}"

    # Precedences
    precs = []

    # (i) chains
    for i in range(1, m + 1):
        for j in range(0, m):
            precs.append((task_id[('x', i, j)], task_id[('x', i, j + 1)]))
            precs.append((task_id[('xbar', i, j)], task_id[('xbar', i, j + 1)]))

    # (ii) y connections
    for i in range(1, m + 1):
        precs.append((task_id[('x', i, i - 1)], task_id[('y', i)]))
        precs.append((task_id[('xbar', i, i - 1)], task_id[('ybar', i)]))

    # (iii) clause tasks
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
                    if is_pos:
                        pred = task_id[('x', var, m)]
                    else:
                        pred = task_id[('xbar', var, m)]
                else:
                    if is_pos:
                        pred = task_id[('xbar', var, m)]
                    else:
                        pred = task_id[('x', var, m)]

                precs.append((pred, task_id[('D', i, j)]))

    return ntasks, t_limit, c, precs, task_id


def extract_p4(schedule, task_id, nvars):
    """Extract assignment: x_i = TRUE if x_{i,0} is at time 0."""
    assignment = []
    for i in range(1, nvars + 1):
        assignment.append(schedule[task_id[('x', i, 0)]] == 0)
    return assignment


# ============================================================
# TEST
# ============================================================

# Smallest possible: m=3, n=1
print("=== m=3 (3 variables), n=1 (1 clause) ===")
clauses = [[1, 2, 3]]  # (x1 OR x2 OR x3)
m = 3
ntasks, t_limit, c, precs, task_id = build_p4(m, clauses)
print(f"P4 instance: {ntasks} tasks, {t_limit} slots, caps={c}")
print(f"Precedences: {len(precs)}")
# ntasks = 2*3*4 + 2*3 + 7 = 24+6+7 = 37
# t_limit = 6
# Search: about 6^37 ~ 1e29 -- too large for brute force even with smart solver

# Let's try m=2 with a "degenerate" 3-SAT
# We need 3 distinct variables per clause, so m >= 3.
# m=3 is the minimum.

# Can we test the P4 solver on this?
print("\nAttempting to solve P4 directly...")
sol = solve_p4_smart(ntasks, t_limit, c, precs)
if sol is not None:
    print(f"FEASIBLE! Schedule found.")
    assignment = extract_p4(sol, task_id, m)
    print(f"  Extracted assignment: {assignment}")
    sat = is_3sat_satisfied(m, clauses, assignment)
    print(f"  Satisfies 3-SAT: {sat}")
else:
    print("INFEASIBLE (or solver timeout)")

# Try UNSAT: all 8 clauses on 3 vars
print("\n=== m=3, all 8 clauses (UNSAT) ===")
all_8 = []
for signs in itertools.product([1, -1], repeat=3):
    all_8.append([signs[0] * 1, signs[1] * 2, signs[2] * 3])

assert not is_3sat_satisfiable(3, all_8)
ntasks, t_limit, c, precs, task_id = build_p4(3, all_8)
print(f"P4 instance: {ntasks} tasks, {t_limit} slots, caps={c}")
# ntasks = 2*3*4 + 6 + 56 = 24+6+56 = 86
# Way too large.

# Let's try a minimal 2-variable problem with 2 clauses (can't have 3-SAT
# with 2 vars since each clause needs 3 distinct vars). Need m >= 3.

# OK, the Ullman construction is O(m^2) tasks even for m=3.
# Let me test it with the smart solver for the SAT case.

print("\n=== Detailed test: m=3, single clause ===")
# (x1 OR x2 OR x3) -- satisfiable
clauses = [[1, 2, 3]]
ntasks, t_limit, c, precs, task_id = build_p4(3, clauses)

# Print what happens at each time slot
print("Expected slot assignments:")
print("  Slot 0 (cap=3): x_{1,0}, x_{2,0}, x_{3,0} OR their xbar counterparts")
print("  Slot 1 (cap=7): 2m+1=7 tasks")
print("  Slot 2 (cap=8): 2m+2=8 tasks")
print("  Slot 3 (cap=8): 2m+2=8 tasks")
print("  Slot 4 (cap=5): n+m+1=5 tasks")
print("  Slot 5 (cap=6): 6n=6 tasks (clause D tasks)")

# Actually solve it
print("\nSolving...")
sol = solve_p4_smart(ntasks, t_limit, c, precs)
if sol:
    print("FOUND solution!")
    # Print slot assignments
    for slot in range(t_limit):
        tasks_in_slot = [tid for tid, s in enumerate(sol) if s == slot]
        names = []
        inv_map = {v: k for k, v in task_id.items()}
        for tid in tasks_in_slot:
            names.append(str(inv_map.get(tid, f"?{tid}")))
        print(f"  Slot {slot} ({c[slot]}): {', '.join(names)}")

    assignment = extract_p4(sol, task_id, 3)
    print(f"  Extracted: x1={assignment[0]}, x2={assignment[1]}, x3={assignment[2]}")
    print(f"  Satisfies: {is_3sat_satisfied(3, clauses, assignment)}")
else:
    print("NO solution found (solver may have timed out)")
