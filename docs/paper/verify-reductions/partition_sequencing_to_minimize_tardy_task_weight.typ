// Standalone verification proof: Partition → SequencingToMinimizeTardyTaskWeight
// Issue: #471

== Partition $arrow.r$ Sequencing to Minimize Tardy Task Weight <sec:partition-sequencingtominimizetardytaskweight>

#let theorem(body) = block(
  width: 100%,
  inset: 8pt,
  stroke: 0.5pt,
  radius: 4pt,
  [*Theorem.* #body],
)

#let proof(body) = block(
  width: 100%,
  inset: 8pt,
  [*Proof.* #body #h(1fr) $square$],
)

#theorem[
  There is a polynomial-time reduction from Partition to Sequencing to Minimize Tardy Task Weight. Given a multiset $A = {a_1, a_2, dots, a_n}$ of positive integers with total sum $B = sum_(i=1)^n a_i$, the reduction constructs $n$ tasks with a common deadline $D = floor(B\/2)$, identical lengths and weights $l(t_i) = w(t_i) = a_i$, and a tardiness bound $K = B - floor(B\/2)$. A balanced partition of $A$ exists if and only if there is a schedule with total tardy weight at most $K$.
] <thm:partition-sequencingtominimizetardytaskweight>

#proof[
  _Construction._

  Let $A = {a_1, a_2, dots, a_n}$ be a Partition instance with $n >= 1$ positive integers and total sum $B = sum_(i=1)^n a_i$.

  + If $B$ is odd, no balanced partition exists. Output a trivially infeasible instance: $n$ tasks with $l(t_i) = w(t_i) = a_i$, all deadlines $d(t_i) = 0$, and bound $K = 0$. In any schedule, every task completes after time $0$, so total tardy weight equals $B > 0 = K$.
  + If $B$ is even, let $T = B \/ 2$. For each $a_i in A$, create task $t_i$ with:
    - Length: $l(t_i) = a_i$
    - Weight: $w(t_i) = a_i$
    - Deadline: $d(t_i) = T$
  + Set the tardiness weight bound $K = T = B \/ 2$.

  _Correctness._

  ($arrow.r.double$) Suppose $A$ has a balanced partition, so there exist disjoint $A', A''$ with $A' union A'' = A$ and $sum_(a in A') a = sum_(a in A'') a = T = B\/2$. Schedule the tasks corresponding to $A'$ first (in any order among themselves), followed by the tasks corresponding to $A''$. The tasks in $A'$ have total processing time $T$, so the last task in $A'$ completes at time $T$. Since every task has deadline $T$, all tasks in $A'$ complete by the deadline and are on-time. The tasks in $A''$ begin processing at time $T$ and complete after $T$, so they are all tardy. The total tardy weight is $sum_(a in A'') a = T = K$. Therefore the schedule achieves total tardy weight equal to $K$, confirming the target is a YES instance.

  ($arrow.l.double$) Suppose there exists a schedule $sigma$ with total tardy weight at most $K = T$. All tasks share the same deadline $T$, and the total processing time is $B = 2T$. Let $S$ be the set of on-time tasks (those completing by time $T$) and $overline(S)$ the set of tardy tasks (those completing after time $T$). Since tasks are non-preemptive and must run sequentially, the on-time tasks occupy an initial segment of time from $0$ to some time $C <= T$. Hence $sum_(t in S) l(t) <= T$. The tardy tasks have total weight $sum_(t in overline(S)) w(t) = sum_(t in overline(S)) a_i = B - sum_(t in S) a_i$. Since this must be at most $K = T$, we have $B - sum_(t in S) a_i <= T$, which gives $sum_(t in S) a_i >= B - T = T$. Combined with $sum_(t in S) l(t) <= T$ (since on-time tasks fit before the deadline), we get $sum_(t in S) a_i = T$. The elements corresponding to $S$ and $overline(S)$ then form a balanced partition of $A$ with each half summing to $T$.

  _Solution extraction._ Given a schedule $sigma$ with tardy weight at most $K$, the on-time tasks (those completing by the deadline $T$) form one half of the partition $A'$, and the tardy tasks form the other half $A'' = A without A'$. The partition assignment is: $x_i = 0$ if task $t_i$ is on-time, $x_i = 1$ if task $t_i$ is tardy.
]

*Overhead.*

#table(
  columns: (auto, auto),
  align: (left, left),
  [*Target metric*], [*Formula*],
  [`num_tasks`], [$n$ (`num_elements`)],
  [`lengths[i]`], [$a_i$ (`sizes[i]`)],
  [`weights[i]`], [$a_i$ (`sizes[i]`)],
  [`deadlines[i]`], [$B\/2$ (`total_sum / 2`) when $B$ even; $0$ when $B$ odd],
  [`K` (bound)], [$B\/2$ when $B$ even; $0$ when $B$ odd],
)

where $n$ = `num_elements` and $B$ = `total_sum` of the source Partition instance.

*Feasible example (YES instance).*

Source: $A = {3, 5, 2, 4, 1, 5}$ with $n = 6$ elements and $B = 3 + 5 + 2 + 4 + 1 + 5 = 20$, $T = B\/2 = 10$.

A balanced partition exists: $A' = {3, 2, 4, 1}$ (sum $= 10$) and $A'' = {5, 5}$ (sum $= 10$).

Constructed scheduling instance: 6 tasks with $l(t_i) = w(t_i) = a_i$ and common deadline $d = 10$, bound $K = 10$.

#table(
  columns: (auto, auto, auto, auto),
  align: (center, center, center, center),
  [*Task*], [*Length*], [*Weight*], [*Deadline*],
  [$t_1$], [3], [3], [10],
  [$t_2$], [5], [5], [10],
  [$t_3$], [2], [2], [10],
  [$t_4$], [4], [4], [10],
  [$t_5$], [1], [1], [10],
  [$t_6$], [5], [5], [10],
)

Schedule: $t_5, t_3, t_1, t_4, t_2, t_6$ (on-time tasks first, then tardy).

#table(
  columns: (auto, auto, auto, auto, auto, auto),
  align: (center, center, center, center, center, center),
  [*Pos*], [*Task*], [*Start*], [*Finish*], [*Tardy?*], [*Tardy wt*],
  [1], [$t_5$], [0], [1], [No], [--],
  [2], [$t_3$], [1], [3], [No], [--],
  [3], [$t_1$], [3], [6], [No], [--],
  [4], [$t_4$], [6], [10], [No], [--],
  [5], [$t_2$], [10], [15], [Yes], [5],
  [6], [$t_6$], [15], [20], [Yes], [5],
)

On-time: ${t_5, t_3, t_1, t_4}$ with total length $1 + 2 + 3 + 4 = 10 = T$ #sym.checkmark \
Tardy: ${t_2, t_6}$ with total tardy weight $5 + 5 = 10 = K$ #sym.checkmark \
Total tardy weight $10 <= K = 10$ #sym.checkmark

Extracted partition: on-time $arrow.r A' = {a_5, a_3, a_1, a_4} = {1, 2, 3, 4}$ (sum $= 10$), tardy $arrow.r A'' = {a_2, a_6} = {5, 5}$ (sum $= 10$) #sym.checkmark

*Infeasible example (NO instance).*

Source: $A = {3, 5, 7}$ with $n = 3$ elements and $B = 3 + 5 + 7 = 15$ (odd).

Since $B$ is odd, no balanced partition exists: any subset sums to an integer, but $B\/2 = 7.5$ is not an integer.

Constructed scheduling instance: 3 tasks with $l(t_i) = w(t_i) = a_i$, all deadlines $d(t_i) = 0$, bound $K = 0$.

#table(
  columns: (auto, auto, auto, auto),
  align: (center, center, center, center),
  [*Task*], [*Length*], [*Weight*], [*Deadline*],
  [$t_1$], [3], [3], [0],
  [$t_2$], [5], [5], [0],
  [$t_3$], [7], [7], [0],
)

In any schedule, the first task starts at time $0$ and completes at time $l(t_i) > 0$, so every task finishes after deadline $0$. All tasks are tardy. Total tardy weight $= 3 + 5 + 7 = 15 > 0 = K$. No schedule achieves tardy weight $<= 0$ #sym.checkmark

Both source and target are infeasible #sym.checkmark
