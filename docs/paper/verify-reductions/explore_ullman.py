#!/usr/bin/env python3
"""
Implement the ACTUAL Ullman 1975 reduction: 3-SAT -> P4 -> P2 (PCS).

P4: variable processor count per time slot.
P2: fixed processor count, unit execution times.

The P4 construction from Lemma 2:
Given 3-SAT with m variables, n clauses:

Jobs:
  x_{i,j} for i=1..m, j=0..m  : (m+1)*m jobs
  xbar_{i,j} for i=1..m, j=0..m : (m+1)*m jobs
  y_i for i=1..m : m jobs
  ybar_i for i=1..m : m jobs
  D_{i,j} for i=1..n, j=1..7 : 7n jobs

Total: 2m(m+1) + 2m + 7n = 2m^2 + 4m + 7n

Time limit: m+3 (slots 0..m+2)
Capacities: c_0=m, c_1=2m+1, c_2..c_m=2m+2, c_{m+1}=n+m+1, c_{m+2}=6n

Total capacity check: m + (2m+1) + (m-1)(2m+2) + (n+m+1) + 6n
  = m + 2m+1 + 2m^2+2m-2m-2 + n+m+1 + 6n
  = m + 2m+1 + 2m^2-2 + n+m+1 + 6n
  = 2m^2 + 4m + 7n = total jobs ✓

P4 -> P2 (Lemma 1):
  Add padding jobs I_{i,j} for 0<=i<t, 0<=j<n_total-c_i
  where n_total is the total number of original jobs.
  Set processors = n_total + 1, time limit = t = m+3.
  Padding jobs: I_{i,j} < I_{i+1,k} for all j,k (chains between time steps).
"""

import itertools
from collections import defaultdict


def literal_value(lit, assignment):
    v = abs(lit) - 1
    val = assignment[v]
    return val if lit > 0 else not val


def is_3sat_satisfied(nvars, clauses, assignment):
    for clause in clauses:
        if not any(literal_value(l, assignment) for l in clause):
            return False
    return True


def is_3sat_satisfiable(nvars, clauses):
    for bits in itertools.product([False, True], repeat=nvars):
        if is_3sat_satisfied(nvars, clauses, list(bits)):
            return True
    return False


def solve_pcs_smart(ntasks, nproc, D, precs):
    """Smarter PCS solver using topological order + backtracking."""
    successors = defaultdict(list)
    predecessors = defaultdict(list)
    for (i, j) in precs:
        successors[i].append(j)
        predecessors[j].append(i)

    # Topological order
    in_degree = [0] * ntasks
    for (i, j) in precs:
        in_degree[j] += 1
    queue = [i for i in range(ntasks) if in_degree[i] == 0]
    topo = []
    temp_deg = list(in_degree)
    while queue:
        t = queue.pop(0)
        topo.append(t)
        for s in successors[t]:
            temp_deg[s] -= 1
            if temp_deg[s] == 0:
                queue.append(s)

    if len(topo) != ntasks:
        return None  # Cycle

    # Compute earliest/latest
    earliest = [0] * ntasks
    for t in topo:
        for s in successors[t]:
            earliest[s] = max(earliest[s], earliest[t] + 1)

    latest = [D - 1] * ntasks
    for t in reversed(topo):
        for s in successors[t]:
            latest[t] = min(latest[t], latest[s] - 1)
        if latest[t] < earliest[t]:
            return None

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


def reduce_ullman(nvars, clauses):
    """
    Full Ullman reduction: 3-SAT -> P4 -> P2 (PCS).

    Variables are 1-indexed: x_1 .. x_m (m = nvars)
    Clauses are 1-indexed: D_1 .. D_n (n = len(clauses))
    Clauses use 1-indexed literals (positive for x, negative for xbar).

    Returns: (ntasks, nproc, deadline, precedences, metadata)
    """
    m = nvars  # number of variables
    n = len(clauses)  # number of clauses

    # === P4 CONSTRUCTION ===

    # Task naming: We'll assign task IDs sequentially.
    task_id = {}
    next_id = [0]

    def alloc(name):
        tid = next_id[0]
        task_id[name] = tid
        next_id[0] += 1
        return tid

    # x_{i,j} for i=1..m, j=0..m
    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('x', i, j))

    # xbar_{i,j} for i=1..m, j=0..m
    for i in range(1, m + 1):
        for j in range(0, m + 1):
            alloc(('xbar', i, j))

    # y_i for i=1..m
    for i in range(1, m + 1):
        alloc(('y', i))

    # ybar_i for i=1..m
    for i in range(1, m + 1):
        alloc(('ybar', i))

    # D_{i,j} for i=1..n, j=1..7
    for i in range(1, n + 1):
        for j in range(1, 8):
            alloc(('D', i, j))

    n_p4_tasks = next_id[0]
    t_limit = m + 3  # time slots 0..m+2

    # Capacities
    c = [0] * t_limit
    c[0] = m
    c[1] = 2 * m + 1
    for i in range(2, m + 1):
        c[i] = 2 * m + 2
    c[m + 1] = n + m + 1
    c[m + 2] = 6 * n

    # Verify total capacity = total tasks
    total_cap = sum(c)
    expected_tasks = 2 * m * (m + 1) + 2 * m + 7 * n
    assert n_p4_tasks == expected_tasks, f"{n_p4_tasks} != {expected_tasks}"
    assert total_cap == n_p4_tasks, f"cap {total_cap} != tasks {n_p4_tasks}"

    # Precedences (P4)
    p4_precs = []

    # Rule (i): x_{i,j} < x_{i,j+1} and xbar_{i,j} < xbar_{i,j+1}
    for i in range(1, m + 1):
        for j in range(0, m):
            p4_precs.append((task_id[('x', i, j)], task_id[('x', i, j + 1)]))
            p4_precs.append((task_id[('xbar', i, j)], task_id[('xbar', i, j + 1)]))

    # Rule (ii): x_{i,i-1} < y_i and xbar_{i,i-1} < ybar_i
    for i in range(1, m + 1):
        p4_precs.append((task_id[('x', i, i - 1)], task_id[('y', i)]))
        p4_precs.append((task_id[('xbar', i, i - 1)], task_id[('ybar', i)]))

    # Rule (iii): Clause tasks D_{i,j}
    # For clause D_i with literals z_{k1}, z_{k2}, z_{k3} (in order),
    # j ranges from 1 to 7. Binary representation of j = a1*4 + a2*2 + a3.
    # If a_p = 1: z_{k_p,m} < D_{i,j}
    # If a_p = 0: complement of z_{k_p,m} < D_{i,j}
    for i in range(1, n + 1):
        clause = clauses[i - 1]  # List of 3 literals (1-indexed, signed)
        for j in range(1, 8):
            a1 = (j >> 2) & 1
            a2 = (j >> 1) & 1
            a3 = j & 1

            for p, ap in enumerate([a1, a2, a3]):
                lit = clause[p]
                var = abs(lit)
                is_positive = lit > 0  # True if literal is x_k, False if xbar_k

                if ap == 1:
                    # z_{k_p,m} < D_{i,j}
                    # z is x if literal is positive, xbar if negative
                    if is_positive:
                        pred = task_id[('x', var, m)]
                    else:
                        pred = task_id[('xbar', var, m)]
                else:
                    # complement of z_{k_p,m} < D_{i,j}
                    # complement: if z=x then zbar=xbar, and vice versa
                    if is_positive:
                        pred = task_id[('xbar', var, m)]
                    else:
                        pred = task_id[('x', var, m)]

                p4_precs.append((pred, task_id[('D', i, j)]))

    # === P4 -> P2 (Lemma 1) ===
    # Add padding jobs I_{i,j} for 0<=i<t, 0<=j<n_total-c_i
    # Chain: I_{i,j} < I_{i+1,k} for all j,k and 0<=i<t-1
    # Processors: n_total + 1

    padding_tasks = {}
    for i in range(t_limit):
        pad_count = n_p4_tasks - c[i]
        for j in range(pad_count):
            tid = next_id[0]
            padding_tasks[(i, j)] = tid
            next_id[0] += 1

    total_tasks = next_id[0]
    nproc = n_p4_tasks + 1

    # Padding precedences: I_{i,j} < I_{i+1,k}
    all_precs = list(p4_precs)
    for i in range(t_limit - 1):
        pad_i_count = n_p4_tasks - c[i]
        pad_i1_count = n_p4_tasks - c[i + 1]
        for j in range(pad_i_count):
            for k in range(pad_i1_count):
                all_precs.append((padding_tasks[(i, j)], padding_tasks[(i + 1, k)]))

    metadata = {
        "source_num_vars": nvars,
        "source_num_clauses": n,
        "n_p4_tasks": n_p4_tasks,
        "total_tasks": total_tasks,
        "nproc": nproc,
        "deadline": t_limit,
        "capacities": c,
        "task_id": task_id,
    }

    return total_tasks, nproc, t_limit, all_precs, metadata


def extract_ullman(schedule, metadata):
    """Extract 3-SAT assignment from PCS schedule."""
    task_id = metadata["task_id"]
    nvars = metadata["source_num_vars"]
    assignment = []
    for i in range(1, nvars + 1):
        # x_i is TRUE if x_{i,0} is at time 0
        x_i_0 = task_id[('x', i, 0)]
        assignment.append(schedule[x_i_0] == 0)
    return assignment


# Test with a small example
print("=== Ullman reduction test ===")

# Example from the paper: (x1 + xbar2 + x3)(xbar1 + x3 + x4)
# m=4 variables, n=2 clauses
# Clause 1: (x1 OR NOT x2 OR x3) -> [1, -2, 3]
# Clause 2: (NOT x1 OR x3 OR x4) -> [-1, 3, 4]

m, n = 4, 2
clauses = [[1, -2, 3], [-1, 3, 4]]

sat = is_3sat_satisfiable(m, clauses)
print(f"3-SAT satisfiable: {sat}")

ntasks, nproc, deadline, precs, meta = reduce_ullman(m, clauses)
print(f"P2 instance: tasks={ntasks}, procs={nproc}, D={deadline}")
print(f"P4 tasks: {meta['n_p4_tasks']}")
print(f"Capacities: {meta['capacities']}")

# This is too large for brute force even with smart solver
# P4 tasks = 2*4*5 + 2*4 + 7*2 = 40+8+14 = 62
# Total with padding: huge
print(f"Search space too large for brute force: {deadline}^{ntasks}")

# Try very small: m=2, n=1
print("\n=== Tiny test: m=2, n=1 ===")
clauses_tiny = [[1, -1, 2]]  # Wait, need 3 DISTINCT vars per clause
# With m=3 (need at least 3 vars for 3-SAT): (x1 OR x2 OR x3)
clauses_tiny = [[1, 2, 3]]
m_tiny = 3
n_tiny = 1

sat = is_3sat_satisfiable(m_tiny, clauses_tiny)
print(f"3-SAT satisfiable: {sat}")

ntasks, nproc, deadline, precs, meta = reduce_ullman(m_tiny, clauses_tiny)
print(f"P2 instance: tasks={ntasks}, procs={nproc}, D={deadline}")
print(f"P4 tasks: {meta['n_p4_tasks']}")
print(f"Capacities: {meta['capacities']}")
print(f"Total with padding: {ntasks}")
print(f"Precs: {len(precs)}")

# P4 tasks = 2*3*4 + 2*3 + 7*1 = 24+6+7 = 37
# Capacities: [3, 7, 8, 8, 4, 7] (for t=6 slots)
# Wait, m+3 = 6 slots
# c_0=3, c_1=7, c_2=8, c_3=8, c_4=1+3+1=4+1=4, c_5=6*1=6... let me check
# c_0=m=3, c_1=2m+1=7, c_2=2m+2=8, c_3=2m+2=8 (for i=2..m=3)
# Wait m=3, so c_2=8, c_3=8. But i ranges from 2 to m=3, so just c_2 and c_3.
# c_{m+1}=c_4=n+m+1=1+3+1=5
# c_{m+2}=c_5=6n=6
# Check: 3+7+8+8+5+6 = 37 ✓

# Padding per slot: 37-c_i
# Slot 0: 37-3=34 padding
# Slot 1: 37-7=30 padding
# etc.
# Total padding: 6*37 - 37 = 5*37 = 185
# Total tasks: 37 + 185 = 222
# Procs: 37+1 = 38
# D = 6
# Search: 6^222 -- impossibly large

print(f"\nThis is way too large. The Ullman P4->P2 transform blows up.")
print(f"Total padding tasks: {ntasks - meta['n_p4_tasks']}")

# The P4->P2 transform adds O(n^2) padding tasks due to the cross-product
# precedences. For our PCS problem, we should reduce DIRECTLY to P4
# formulation or find a simpler equivalent.

# Since the PCS in the codebase uses FIXED processor count (P2-style),
# but Ullman's native reduction targets P4 (variable processors per slot),
# a direct 3SAT->PCS reduction is more involved than described in issue #476.

# Let me try an alternative: use the P4 formulation directly by setting
# num_processors = max(c_i), which gives a sound overapproximation.
# Then some UNSAT instances might wrongly be declared feasible.

print("\n=== Testing P4 with max-processor approximation ===")
# Use P4's precedences directly, set nproc = max(c_i), D = t_limit
# This is UNSOUND because capacity varies per slot.
# But it's a lower bound on feasibility.

# Actually, to encode P4 into P2, we don't need the cross-product padding.
# We can use a SIMPLER encoding:
# For each time slot i with c_i < max_c:
#   Create (max_c - c_i) "slot-specific filler" tasks that MUST go to slot i.
#   Force them to slot i using chains.

print("\n=== Simpler P4->P2 encoding ===")
# For each pair of consecutive slots i and i+1:
#   Create a chain of filler tasks that forces fillers to their slot.
# Actually, we can force filler for slot i by:
#   (a) making it a successor of a task that must be in slot i-1
#   (b) making it a predecessor of a task that must be in slot i+1
# This requires building a "backbone" chain through all slots.

# BACKBONE: one task per slot, chained: B_0 < B_1 < ... < B_{t-1}
# This forces B_i to slot i (with tight capacity at each level).
# For slot i, create (max_c - c_i - 1) filler tasks F_{i,j}.
# Force F_{i,j} to slot i: B_{i-1} < F_{i,j} < B_{i+1}
# (so F must be in a slot > B_{i-1} and < B_{i+1}, i.e., exactly slot i)

# Hmm, but the backbone tasks take up 1 processor slot each.
# max_c processors per slot.
# Backbone uses 1 per slot. Original P4 uses c_i per slot.
# Fillers use (max_c - c_i - 1) per slot.
# Total per slot: 1 + c_i + (max_c - c_i - 1) = max_c ✓

# This is MUCH better: only O(t * max_c) total tasks.

m_test = 3
clauses_test = [[1, 2, 3]]
n_test = 1
t_limit = m_test + 3  # 6

# Capacities
c_cap = [0] * t_limit
c_cap[0] = m_test
c_cap[1] = 2 * m_test + 1
for i in range(2, m_test + 1):
    c_cap[i] = 2 * m_test + 2
c_cap[m_test + 1] = n_test + m_test + 1
c_cap[m_test + 2] = 6 * n_test

max_c = max(c_cap)
print(f"Capacities: {c_cap}, max = {max_c}")

# Total backbone tasks: t_limit
# Total filler tasks: sum(max_c - c_i - 1 for i in range(t_limit))
#                   = t_limit * (max_c - 1) - sum(c_i)
# P4 tasks: sum(c_i)
# Total: P4_tasks + backbone + fillers
#       = sum(c_i) + t_limit + t_limit*(max_c-1) - sum(c_i)
#       = t_limit * max_c

total_p2 = t_limit * max_c
print(f"Total P2 tasks (backbone encoding): {total_p2}")
print(f"Processors: {max_c}")
print(f"Search space: {t_limit}^{total_p2} = {t_limit**total_p2:.2e}")
# 6^48 ~ 2.8e37 -- still way too large for brute force!

# Even the SMART solver can't handle this in reasonable time.
# The Ullman reduction produces instances that are too large for
# exhaustive verification.

print("\n=== CONCLUSION ===")
print("The Ullman 1975 reduction (3SAT -> P4 -> P2) produces")
print("instances that are O(m^2 + n) in the P4 formulation and")
print("even larger when converted to fixed-processor PCS (P2).")
print("This makes exhaustive computational verification infeasible")
print("for any non-trivial 3-SAT instance.")
print()
print("The issue #476 description appears to give a simplified/incorrect")
print("version of the reduction that doesn't properly encode the")
print("variable choice mechanism.")
