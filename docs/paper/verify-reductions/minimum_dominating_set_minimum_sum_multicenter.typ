// Verification proof: MinimumDominatingSet -> MinimumSumMulticenter
// Issue: #380
// Reference: Garey & Johnson, Computers and Intractability, ND51, p.220;
//   Kariv, O. and Hakimi, S.L. (1979). "An Algorithmic Approach to Network
//   Location Problems. II: The p-Medians." SIAM J. Appl. Math. 37(3), 539-560.

= Minimum Dominating Set $arrow.r$ Minimum Sum Multicenter <sec:mds-sum-multicenter>

== Problem Definitions

*Minimum Dominating Set (decision form).* Given a graph $G = (V, E)$ and a
positive integer $K lt.eq |V|$, determine whether there exists a subset
$D subset.eq V$ with $|D| lt.eq K$ such that every vertex $v in V$ satisfies
$v in D$ or $N(v) sect D eq.not emptyset$ (that is, $D$ dominates all of $V$).

*Min-Sum Multicenter ($p$-median).* Given a graph $G = (V, E)$ with vertex
weights $w: V arrow.r bb(Z)^+_0$, edge lengths $ell: E arrow.r bb(Z)^+_0$, a
positive integer $K lt.eq |V|$, and a rational bound $B gt.eq 0$, determine
whether there exists a set $P subset.eq V$ of $K$ vertex-centers such that
$ sum_(v in V) w(v) dot d(v, P) lt.eq B, $
where $d(v, P) = min_(p in P) d(v, p)$ is the shortest-path distance from $v$
to the nearest center.

== Reduction

Given a decision Dominating Set instance $(G = (V, E), K)$ where $G$ is
connected:

+ Set the target graph to $G' = G$ (same vertex set $V$ and edge set $E$).
+ Assign unit vertex weights: $w(v) = 1$ for every $v in V$.
+ Assign unit edge lengths: $ell(e) = 1$ for every $e in E$.
+ Set the number of centers $k = K$.
+ Set the distance bound $B = |V| - K$.

*Note.* The reduction requires $G$ to be connected. For disconnected graphs,
vertices in components without a center would have infinite distance, causing
the sum to exceed any finite $B$.

== Correctness Proof <thm:mds-sum-multicenter>

=== Forward ($arrow.r.double$): Dominating set implies feasible $p$-median

Suppose $D subset.eq V$ is a dominating set with $|D| lt.eq K$.
If $|D| < K$, extend $D$ to exactly $K$ vertices by adding arbitrary vertices.
Place centers at the $K$ vertices of $D$.

For any vertex $v in V$:
- If $v in D$, then $d(v, D) = 0$.
- If $v in.not D$, there exists $u in D$ with $(v, u) in E$ (by domination),
  so $d(v, D) lt.eq 1$.

Therefore:
$ sum_(v in V) w(v) dot d(v, D) = sum_(v in D) 0 + sum_(v in.not D) d(v, D)
  lt.eq 0 dot K + 1 dot (n - K) = n - K = B. $

=== Backward ($arrow.l.double$): Feasible $p$-median implies dominating set

Suppose $P subset.eq V$ with $|P| = K$ satisfies
$sum_(v in V) w(v) dot d(v, P) lt.eq n - K$.

Since all weights and lengths are 1, the sum is $sum_(v in V) d(v, P)$.
The $K$ centers each contribute $d(v, P) = 0$. The remaining $n - K$
non-center vertices each satisfy $d(v, P) gt.eq 1$ (they are not centers).
Thus:
$ sum_(v in V) d(v, P) gt.eq 0 dot K + 1 dot (n - K) = n - K. $

Combined with the bound $sum d(v, P) lt.eq n - K$, we get equality: every
non-center vertex $v$ has $d(v, P) = 1$. On a unit-length graph, $d(v, P) = 1$
means there exists $p in P$ with $(v, p) in E$, so $v$ is adjacent to a center.

Therefore $P$ is a dominating set of size $K$.

=== Infeasible Instances

If $G$ has no dominating set of size $K$ (when $K < gamma(G)$), the forward
direction has no valid input. Conversely, any feasible $K$-center solution with
$B = n - K$ would be a dominating set of size $K$ (by the backward direction),
contradicting the assumption. So the $p$-median instance is also infeasible.

== Solution Extraction

Given a $p$-median solution $P subset.eq V$ with $|P| = K$ and
$sum_(v in V) d(v, P) lt.eq n - K$, return $D = P$ as the dominating set.
By the backward proof, $P$ dominates all vertices.

In configuration form: $c'_v = c_v$ for all $v in V$ (the binary indicator
vector is preserved exactly).

== Overhead

#table(
  columns: (auto, auto),
  [*Target metric*], [*Expression*],
  [`num_vertices`], [`num_vertices`],
  [`num_edges`], [`num_edges`],
  [`k`], [`K` (domination bound from source)],
)

The graph is preserved identically. The only new parameters are $k = K$ and
$B = n - K$.

== YES Example

*Source (Dominating Set):* Graph $G$ with 6 vertices ${0, 1, 2, 3, 4, 5}$ and
7 edges: ${(0,1), (0,2), (1,3), (2,3), (3,4), (3,5), (4,5)}$. $K = 2$.

Dominating set $D = {0, 3}$:
- $N[0] = {0, 1, 2}$, $N[3] = {1, 2, 3, 4, 5}$
- $N[0] union N[3] = {0, 1, 2, 3, 4, 5} = V$ #sym.checkmark

*Target (MinimumSumMulticenter):* Same graph, $w(v) = 1$ for all $v$,
$ell(e) = 1$ for all $e$, $k = 2$, $B = 6 - 2 = 4$.

Centers $P = {0, 3}$:
- $d(0, P) = 0$ (center), $d(1, P) = 1$, $d(2, P) = 1$
- $d(3, P) = 0$ (center), $d(4, P) = 1$, $d(5, P) = 1$

$sum = 0 + 1 + 1 + 0 + 1 + 1 = 4 = B$ #sym.checkmark

*Extraction:* Centers ${0, 3}$ form a dominating set of size 2. #sym.checkmark

== NO Example

*Source (Dominating Set):* Same graph with $K = 1$.

No single vertex dominates this graph:
- $|N[3]| = 5$ (highest degree: $N[3] = {1, 2, 3, 4, 5}$), but vertex 0 is
  not in $N[3]$, so $N[3] eq.not V$.
- Any other vertex has even fewer neighbors.
Thus $gamma(G) = 2 > 1 = K$. No dominating set of size 1 exists.

*Target (MinimumSumMulticenter):* Same graph, $w(v) = 1$, $ell(e) = 1$,
$k = 1$, $B = 6 - 1 = 5$.

For any single center $p$, vertices far from $p$ contribute $d(v, {p}) gt.eq 2$:
- Center at 3: $d(0, {3}) = 2$ (path $0 dash.en 1 dash.en 3$ or
  $0 dash.en 2 dash.en 3$). $sum = 2 + 1 + 1 + 0 + 1 + 1 = 6 > 5$.
- Center at 0: $d(3, {0}) = 2$, $d(4, {0}) = 3$, $d(5, {0}) = 3$.
  $sum = 0 + 1 + 1 + 2 + 3 + 3 = 10 > 5$.

No single vertex achieves $sum d(v, {p}) lt.eq 5$. #sym.checkmark
