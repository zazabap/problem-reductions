#!/usr/bin/env python3
"""Debug: why does [[1,2,3],[-1,-2,-3]] fail in P4?"""

import itertools
from collections import defaultdict


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


def solve_p4_brute(ntasks, t_limit, capacities, precs):
    """Brute-force P4 solver."""
    # Only feasible for very small instances
    for sched in itertools.product(range(t_limit), repeat=ntasks):
        s = list(sched)
        # Check capacities
        slot_count = [0] * t_limit
        for v in s:
            slot_count[v] += 1
        ok = True
        for i in range(t_limit):
            if slot_count[i] != capacities[i]:
                ok = False
                break
        if not ok:
            continue
        # Check precedences
        for (a, b) in precs:
            if s[a] >= s[b]:
                ok = False
                break
        if ok:
            return s
    return None


# Test [[1,2,3], [-1,-2,-3]]
clauses = [[1, 2, 3], [-1, -2, -3]]
ntasks, t_limit, c, precs, task_id = build_p4(3, clauses)
print(f"P4: {ntasks} tasks, {t_limit} slots, caps={c}")
print(f"  Total cap: {sum(c)}")
# 2*3*4+6+14 = 24+6+14=44, t=6, caps=[3,7,8,8,6,12]
# That's 44 tasks with 6 slots... brute force: 6^44 ~ 4e33. Impossible.

# Let me manually construct a valid P4 schedule for x1=T, x2=T, x3=T
# which satisfies (x1 OR x2 OR x3) AND (NOT x1 OR NOT x2 OR NOT x3)
# Assignment: x1=T, x2=T, x3=F satisfies both.
# In Ullman: x1 TRUE -> x_{1,0} at time 0
#            x2 TRUE -> x_{2,0} at time 0
#            x3 FALSE -> xbar_{3,0} at time 0

# Slot 0 (cap=3): x_{1,0}, x_{2,0}, xbar_{3,0}
# Slot 1 (cap=7): What goes here?

# From the paper: at time t (for t=1..m), we execute:
#   z_{i,t} if z_{i,0} was at time 0
#   z_{i,t-1} if z_{i,0} was NOT at time 0
# Plus y_t or ybar_t

# For x1=T: x_{1,0} at time 0, so x_{1,t} at time t for t=1..3
#           xbar_{1,0} NOT at time 0, so xbar_{1,0} at time 1, xbar_{1,1} at time 2, etc.

# For x3=F: xbar_{3,0} at time 0, so xbar_{3,t} at time t for t=1..3
#           x_{3,0} NOT at time 0, so x_{3,0} at time 1, x_{3,1} at time 2, etc.

schedule = [None] * ntasks
inv = {v: k for k, v in task_id.items()}

def assign(name, slot):
    schedule[task_id[name]] = slot

# Variable 1: x1=TRUE -> x_{1,0} at 0
true_vars = [True, True, False]  # x1=T, x2=T, x3=F

for i in range(1, 4):
    is_true = true_vars[i-1]
    if is_true:
        # x_{i,j} at time j for j=0..m
        for j in range(0, 4):  # m=3, so j=0..3
            assign(('x', i, j), j)
        # xbar_{i,0} at time 1, xbar_{i,1} at time 2, etc.
        for j in range(0, 4):
            assign(('xbar', i, j), j + 1)
        # y_i at time i (since x_{i,i-1} at time i-1, y_i after that)
        assign(('y', i), i)
        # ybar_i: xbar_{i,i-1} at time i, so ybar_i at time i+1? No...
        # Actually y_i depends on x_{i,i-1}. x_{i,i-1} is at time i-1.
        # So y_i >= i. And ybar_i depends on xbar_{i,i-1}.
        # xbar_{i,i-1} at time i (since offset by 1). So ybar_i >= i+1.
        # But we need to figure out when to place these.
    else:
        # xbar_{i,0} at time 0, xbar_{i,j} at time j
        for j in range(0, 4):
            assign(('xbar', i, j), j)
        # x_{i,0} at time 1, x_{i,j} at time j+1
        for j in range(0, 4):
            assign(('x', i, j), j + 1)
        # ybar_i at time i
        assign(('ybar', i), i)

# Wait, the paper says (for the TRUE case):
# "at time t we must execute z_{i,t} if z_{i,0} was executed at time 0
#  and z_{i,t-1} if not"
# and "y_t (or ybar_t) at time t if x_{t,0} (or xbar_{t,0}) was at time 0"

# For variable 1 (TRUE):
#   x_{1,0} at 0, x_{1,1} at 1, x_{1,2} at 2, x_{1,3} at 3
#   xbar_{1,0} at 1, xbar_{1,1} at 2, xbar_{1,2} at 3, xbar_{1,3} at 4
#   y_1 at 1 (since x_{1,0} was at 0)
#   ybar_1 at ? (paper says execute y_{t-1} at time t if not at 0)
#   Actually the paper says: "execute Y_t (respectively, Ybar_t) at time t
#   if X_{t,0} (respectively, Xbar_{t,0}) was executed at time 0"
#   AND "execute Y_{t-1} (respectively, Ybar_{t-1}) at time t if X_{t,0}
#   (respectively, Xbar_{t,0}) was executed at time 1."

# Let me re-read: For variable i:
#   If x_{i,0} at time 0 (TRUE): y_i at time i, ybar_i at some later time
#   If xbar_{i,0} at time 0 (FALSE): ybar_i at time i, y_i at some later time

# For var 1 (TRUE): y_1 at time 1
# For var 2 (TRUE): y_2 at time 2
# For var 3 (FALSE): ybar_3 at time 3

# The remaining y/ybar: Where do they go?
# At time m+1 = 4, the remaining y and ybar tasks are executed.
# "At time m+1 we can execute the m remaining x's and xbar's and the one
#  remaining y or ybar."

# For TRUE vars: xbar_{i,3} at time 4 (the last one), ybar_i at time 4
# For FALSE vars: x_{i,3} at time 4, y_i at time 4

# Let me fix the schedule:
schedule = [None] * ntasks

for i in range(1, 4):
    is_true = true_vars[i-1]
    if is_true:
        for j in range(0, 4):
            assign(('x', i, j), j)
        for j in range(0, 3):  # xbar 0,1,2 go to 1,2,3
            assign(('xbar', i, j), j + 1)
        assign(('xbar', i, 3), 4)  # last xbar goes to m+1=4
        assign(('y', i), i)
        assign(('ybar', i), 4)  # remaining ybar at m+1
    else:
        for j in range(0, 4):
            assign(('xbar', i, j), j)
        for j in range(0, 3):
            assign(('x', i, j), j + 1)
        assign(('x', i, 3), 4)
        assign(('ybar', i), i)
        assign(('y', i), 4)

# Now figure out D tasks.
# D tasks go to slots m+1 and m+2 (4 and 5).
# "At time m+1 we can execute... n of the D's"
# "for each i, at most one of D_{i,1},...,D_{i,7} can be executed at time m+1"

# Clause 1: (x1 OR x2 OR x3) = (x1 OR x2 OR x3)
# x1=T, x2=T, x3=F: all of x1,x2 are TRUE, x3 is FALSE
# Which D_{1,j} can go to time m+1?
# j is a 3-bit pattern. For D_{1,j}, the predecessors are:
#   For literal x1 (positive): bit position 0 (MSB? paper uses a1,a2,a3)
#   j = a1*4 + a2*2 + a3
#   If a_p=1: predecessor is literal task at time m
#   If a_p=0: predecessor is complement task at time m

# Clause 1 literals: x1, x2, x3 (all positive)
# For x1 TRUE: x_{1,3} at time 3, xbar_{1,3} at time 4
# For x2 TRUE: x_{2,3} at time 3, xbar_{2,3} at time 4
# For x3 FALSE: x_{3,3} at time 4, xbar_{3,3} at time 3

# D_{1,j} has predecessors:
# For literal x1 (a1 position):
#   a1=1: x_{1,3} (at time 3) -> D can be at 4 or 5
#   a1=0: xbar_{1,3} (at time 4) -> D must be at 5
# For literal x2 (a2 position):
#   a2=1: x_{2,3} (at time 3) -> D can be at 4 or 5
#   a2=0: xbar_{2,3} (at time 4) -> D must be at 5
# For literal x3 (a3 position):
#   a3=1: x_{3,3} (at time 4) -> D must be at 5
#   a3=0: xbar_{3,3} (at time 3) -> D can be at 4 or 5

# Since x1=T and x2=T, their "true" predecessors (x_{i,m}) are at time m=3.
# Since x3=F, x_{3,m}=x_{3,3} at time 4, xbar_{3,m}=xbar_{3,3} at time 3.

# So for D_{1,j}: need ALL predecessors at time <= m+1-1 = 3 to go to slot 4.
# a1=1 (x_{1,3} at 3), a2=1 (x_{2,3} at 3), a3=0 (xbar_{3,3} at 3) -> all at 3 -> D at 4 or 5
# j = 1*4 + 1*2 + 0 = 6
# So D_{1,6} can go to slot 4!

# For the unsatisfied assignments of the clause:
# j=0 is excluded (can't have a1=a2=a3=0 as paper says "j cannot be 0" since j ranges 1..7)
# Actually j ranges from 1 to 7, and binary(0)=000 is excluded.

# Clause 2: (-x1 OR -x2 OR -x3) = (xbar1 OR xbar2 OR xbar3)
# x1=T -> xbar1 FALSE, x2=T -> xbar2 FALSE, x3=F -> xbar3 TRUE
# Literals: -1 (xbar1), -2 (xbar2), -3 (xbar3)
# For -1 (xbar1): x1=T means xbar_{1,3} at 4, x_{1,3} at 3
# For -2 (xbar2): x2=T means xbar_{2,3} at 4, x_{2,3} at 3
# For -3 (xbar3): x3=F means xbar_{3,3} at 3, x_{3,3} at 4

# D_{2,j} predecessors:
# For literal -1: is_pos=False
#   a1=1: xbar_{1,3} (at 4) -> D at 5
#   a1=0: x_{1,3} (at 3) -> D at 4 or 5
# For literal -2: is_pos=False
#   a2=1: xbar_{2,3} (at 4) -> D at 5
#   a2=0: x_{2,3} (at 3) -> D at 4 or 5
# For literal -3: is_pos=False
#   a3=1: xbar_{3,3} (at 3) -> D at 4 or 5
#   a3=0: x_{3,3} (at 4) -> D at 5

# Want D_{2,j} at slot 4: need all predecessors at <= 3
# a1=0 (x_{1,3} at 3), a2=0 (x_{2,3} at 3), a3=1 (xbar_{3,3} at 3) -> all at 3
# j = 0*4 + 0*2 + 1 = 1
# So D_{2,1} can go to slot 4!

# Place D_{1,6} and D_{2,1} at slot 4
assign(('D', 1, 6), 4)
assign(('D', 2, 1), 4)

# All other D tasks go to slot 5
for i in range(1, 3):
    for j in range(1, 8):
        if schedule[task_id[('D', i, j)]] is None:
            assign(('D', i, j), 5)

# Check for None values
for tid in range(ntasks):
    if schedule[tid] is None:
        name = inv[tid]
        print(f"  UNASSIGNED: {name}")

# Verify
slot_count = [0] * t_limit
for s in schedule:
    slot_count[s] += 1

print(f"Schedule slot counts: {slot_count}")
print(f"Required capacities: {c}")
print(f"Match: {slot_count == c}")

# Check precedences
ok = True
for (a, b) in precs:
    if schedule[a] >= schedule[b]:
        ok = False
        print(f"  PREC VIOLATION: {inv[a]} at {schedule[a]} >= {inv[b]} at {schedule[b]}")
        break
print(f"Precedences OK: {ok}")

# Print slot contents
inv = {v: k for k, v in task_id.items()}
for slot in range(t_limit):
    tasks = [inv[tid] for tid in range(ntasks) if schedule[tid] == slot]
    print(f"  Slot {slot} ({c[slot]}): {tasks}")
