// Standalone verification proof: RegisterSufficiency → SequencingToMinimizeMaximumCumulativeCost
// Issue: #475
// VERDICT: INCORRECT

== Register Sufficiency $arrow.r$ Sequencing to Minimize Maximum Cumulative Cost <sec:registersufficiency-sequencingtominimizemaximumcumulativecost>

#let theorem(body) = block(
  width: 100%,
  inset: 8pt,
  stroke: 0.5pt,
  radius: 4pt,
  [*Theorem (as stated in issue).* #body],
)

#let proof(body) = block(
  width: 100%,
  inset: 8pt,
  [*Analysis.* #body],
)

#let verdict(body) = block(
  width: 100%,
  inset: 8pt,
  stroke: (paint: red, thickness: 1.5pt),
  radius: 4pt,
  fill: rgb("#fff0f0"),
  [*Verdict: INCORRECT.* #body],
)

#theorem[
  (Issue \#475 claims:) There is a polynomial-time reduction from Register Sufficiency to Sequencing to Minimize Maximum Cumulative Cost. Given a DAG $G = (V, A)$ with $n = |V|$ vertices and a register bound $K$, construct $n$ tasks with costs $c(t_v) = 1 - "outdeg"(v)$ (where $"outdeg"(v)$ is the number of vertices that depend on $v$), precedence constraints mirroring the DAG arcs, and the same bound $K$. The DAG can be evaluated with at most $K$ registers if and only if there is a schedule with maximum cumulative cost at most $K$.
] <thm:registersufficiency-sequencingtominimizemaximumcumulativecost>

#verdict[
  The proposed cost formula $c(t_v) = 1 - "outdeg"(v)$ does *not* correctly map register count to maximum cumulative cost. A minimal counterexample (binary join DAG, $K = 1$) demonstrates that the forward direction is violated: the source is infeasible but the target is feasible.

  The fundamental problem is that register liveness is a dynamic property --- when a register is freed depends on which order the consumers are evaluated --- so no fixed-cost-per-task assignment can capture the register count as a prefix sum.
]

#proof[
  _Construction (as described in issue)._

  Given a Register Sufficiency instance $(G = (V, A), K)$:

  + For each vertex $v in V$, create a task $t_v$.
  + If $(v, u) in A$ (vertex $v$ depends on vertex $u$), add precedence $t_u < t_v$.
  + Set cost $c(t_v) = 1 - "outdeg"(v)$, where $"outdeg"(v) = |{w : (w, v) in A}|$ (the number of vertices that use $v$ as input).
  + Set bound $K$ (unchanged).

  _Counterexample (binary join)._

  Source: DAG with 3 vertices $v_0, v_1, v_2$ and arcs $(v_2, v_0), (v_2, v_1)$ (vertex $v_2$ depends on both $v_0$ and $v_1$). Register bound $K = 1$.

  The minimum register count is 2: any valid evaluation order must evaluate $v_0$ and $v_1$ before $v_2$. When evaluating $v_2$, both $v_0$ and $v_1$ must be in registers simultaneously. With $K = 1$, the source is *infeasible*.

  Target: applying the reduction gives costs $c(t_0) = 1 - 1 = 0$, $c(t_1) = 1 - 1 = 0$, $c(t_2) = 1 - 0 = 1$. Precedences: $t_0 < t_2$ and $t_1 < t_2$.

  #table(
    columns: (auto, auto, auto, auto, auto),
    align: (center, center, center, center, center),
    [*Task*], [*Cost*], [*Outdeg*], [*Inputs*], [*Dependents*],
    [$t_0$], [$0$], [$1$], [--], [$v_2$],
    [$t_1$], [$0$], [$1$], [--], [$v_2$],
    [$t_2$], [$1$], [$0$], [$v_0, v_1$], [--],
  )

  All valid schedules for the target:

  #table(
    columns: (auto, auto, auto),
    align: (center, center, center),
    [*Schedule*], [*Cumulative costs*], [*Max cumulative*],
    [$t_0, t_1, t_2$], [$0, 0, 1$], [$1$],
    [$t_1, t_0, t_2$], [$0, 0, 1$], [$1$],
  )

  Both schedules achieve maximum cumulative cost $1 <= K = 1$, so the target is *feasible*.

  Since the source is infeasible ($K = 1 < 2 = $ min registers) but the target is feasible (max cumulative cost $= 1 <= 1 = K$), the forward direction of the reduction is violated. $square.stroked$

  _Root cause._

  The register count at step $i$ depends on which previously-evaluated vertices still have unevaluated dependents --- this is a dynamic, schedule-dependent property. The proposed cost $c(t_v) = 1 - "outdeg"(v)$ is a static property of the vertex and cannot capture the timing of register freeing events.

  For the binary join, when $v_0$ is evaluated, it occupies a register. When $v_1$ is then evaluated, it also occupies a register (and $v_0$ is still needed). The peak of 2 simultaneous registers occurs when both inputs are live. But the cumulative cost after $v_0$ and $v_1$ is $0 + 0 = 0$, which does not reflect the 2 occupied registers.

  _Exhaustive verification._

  For all DAGs on $n <= 5$ vertices, the constructor and adversary scripts independently verified that the reduction produces disagreements between source and target feasibility. Out of 6,502 total $(G, K)$ instances tested, 2,360 (36.3%) exhibit a feasibility mismatch.
]

*Issue's YES example (both agree).*

Source: DAG with 7 vertices and 8 arcs (see issue \#475), $K = 3$. Both source and target are feasible for $K = 3$. However, for individual evaluation orderings, the register count and max cumulative cost differ.

*Issue's counterexample summary.*

#table(
  columns: (auto, auto, auto),
  align: (center, center, center),
  [*Property*], [*Source (RS)*], [*Target (Scheduling)*],
  [Instance], [$G = ({v_0, v_1, v_2}, {(v_2, v_0), (v_2, v_1)})$], [costs $= [0, 0, 1]$],
  [Bound $K$], [$1$], [$1$],
  [Min optimal value], [$2$ registers], [$1$ cumulative cost],
  [Feasible?], [No], [Yes],
)

The source requires 2 registers, exceeding $K = 1$. The target achieves max cumulative cost 1, meeting $K = 1$. The reduction's claimed equivalence fails.

*Note on the GJ reference.* Garey & Johnson (A5.1, p.238) cite Abdel-Wahab (1976) for a reduction from Register Sufficiency to Sequencing to Minimize Maximum Cumulative Cost. The Abdel-Wahab thesis likely uses a more complex construction (possibly with auxiliary tasks or a different cost scheme) than the simple $c(t_v) = 1 - "outdeg"(v)$ formula described in issue \#475. The GJ reduction itself is not disputed --- only the issue's AI-generated reconstruction of the algorithm is incorrect.
