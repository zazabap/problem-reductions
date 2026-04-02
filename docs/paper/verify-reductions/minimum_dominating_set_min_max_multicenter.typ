// Verification proof: MinimumDominatingSet → MinMaxMulticenter
// Issue: #379
// Reference: Garey & Johnson, Computers and Intractability, ND50, p.220;
//   Kariv, O. and Hakimi, S.L. (1979). "An Algorithmic Approach to Network
//   Location Problems. I: The p-Centers." SIAM J. Appl. Math. 37(3), 513–538.

= Minimum Dominating Set $arrow.r$ Min-Max Multicenter <sec:mds-multicenter>

== Problem Definitions

*Minimum Dominating Set.* Given a graph $G = (V, E)$ with vertex weights
$w: V arrow.r bb(Z)^+$ and a positive integer $K lt.eq |V|$, determine whether
there exists a subset $D subset.eq V$ with $|D| lt.eq K$ such that every vertex
$v in V$ satisfies $v in D$ or $N(v) sect D eq.not emptyset$
(that is, $D$ dominates all of $V$).

*Min-Max Multicenter (vertex $p$-center).* Given a graph $G = (V, E)$
with vertex weights $w: V arrow.r bb(Z)^+_0$, edge lengths
$ell: E arrow.r bb(Z)^+_0$, a positive integer $K lt.eq |V|$, and a
rational bound $B gt.eq 0$, determine whether there exists a set $P subset.eq V$
of $K$ vertex-centers such that
$ max_(v in V) w(v) dot d(v, P) lt.eq B, $
where $d(v, P) = min_(p in P) d(v, p)$ is the shortest-path distance from $v$ to
the nearest center.

== Reduction

Given a decision Dominating Set instance $(G = (V, E), K)$:

+ Set the target graph to $G' = G$ (same vertex set $V$ and edge set $E$).
+ Assign unit vertex weights: $w(v) = 1$ for every $v in V$.
+ Assign unit edge lengths: $ell(e) = 1$ for every $e in E$.
+ Set the number of centers $k = K$.
+ Set the distance bound $B = 1$.

== Correctness Proof <thm:mds-multicenter>

=== Forward ($arrow.r.double$): Dominating set implies feasible multicenter

Suppose $D subset.eq V$ is a dominating set with $|D| lt.eq K$.
If $|D| < K$, extend $D$ to exactly $K$ vertices by adding arbitrary vertices
(this does not violate any constraint since extra centers can only decrease
distances). Place centers at the $K$ vertices of $D$.

For any vertex $v in V$:
- If $v in D$, then $d(v, D) = 0$, so $w(v) dot d(v, D) = 1 dot 0 = 0 lt.eq 1$.
- If $v in.not D$, there exists $u in D$ with $(v, u) in E$ (by domination).
  The single edge $(v, u)$ has length 1, so $d(v, D) lt.eq 1$,
  giving $w(v) dot d(v, D) = 1 dot 1 = 1 lt.eq 1$.

Therefore $max_(v in V) w(v) dot d(v, D) lt.eq 1 = B$.

=== Backward ($arrow.l.double$): Feasible multicenter implies dominating set

Suppose $P subset.eq V$ with $|P| = K$ satisfies
$max_(v in V) w(v) dot d(v, P) lt.eq 1$.

Since all weights are 1, this means $d(v, P) lt.eq 1$ for every vertex $v$.
For any vertex $v in V$:
- If $d(v, P) = 0$, then $v in P$, so $v$ is dominated by itself.
- If $d(v, P) = 1$, there exists $p in P$ with $d(v, p) = 1$. Since edge
  lengths are all 1, a shortest path of length 1 means $(v, p) in E$.
  So $v$ has a neighbor in $P$ and is dominated.

Therefore $P$ is a dominating set of size $K$.

=== Infeasible Instances

If $G$ has no dominating set of size $K$ (for example, when $K < gamma(G)$,
the domination number), the forward direction has no valid input.
Conversely, any $K$-center solution with $B = 1$ would be a dominating
set of size $K$, contradicting the assumption. So the multicenter instance
is also infeasible.

== Solution Extraction

Given a multicenter solution $P subset.eq V$ with $|P| = K$ and
$max_(v in V) d(v, P) lt.eq 1$, return $D = P$ as the dominating set.
By the backward proof above, $P$ dominates all vertices.

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

The graph is preserved identically. The only new parameter is $k = K$.

== YES Example

*Source (Dominating Set):* Graph $G$ with 5 vertices ${0, 1, 2, 3, 4}$ and 5 edges:
${(0,1), (1,2), (2,3), (3,4), (0,4)}$ (a 5-cycle). $K = 2$.

Dominating set $D = {1, 3}$:
- $N[1] = {0, 1, 2}$, $N[3] = {2, 3, 4}$
- $N[1] union N[3] = {0, 1, 2, 3, 4} = V$ #sym.checkmark

*Target (MinMaxMulticenter):* Same graph, $w(v) = 1$ for all $v$,
$ell(e) = 1$ for all $e$, $k = 2$, $B = 1$.

Centers $P = {1, 3}$:
- $d(0, P) = 1$ (edge to vertex 1), $w(0) dot d(0, P) = 1$
- $d(1, P) = 0$ (center), $w(1) dot d(1, P) = 0$
- $d(2, P) = 1$ (edge to vertex 1 or 3), $w(2) dot d(2, P) = 1$
- $d(3, P) = 0$ (center), $w(3) dot d(3, P) = 0$
- $d(4, P) = 1$ (edge to vertex 3), $w(4) dot d(4, P) = 1$

$max = 1 lt.eq 1 = B$ #sym.checkmark

*Extraction:* Centers ${1, 3}$ form a dominating set of size 2. #sym.checkmark

== NO Example

*Source (Dominating Set):* Graph $G$ with 5 vertices ${0, 1, 2, 3, 4}$ and 5 edges:
${(0,1), (1,2), (2,3), (3,4), (0,4)}$ (same 5-cycle). $K = 1$.

No single vertex dominates the entire 5-cycle. For each vertex $v$:
- $|N[v]| = 3$ (the vertex and its two neighbors), but $|V| = 5$.
Thus $gamma(C_5) = 2 > 1 = K$. No dominating set of size 1 exists.

*Target (MinMaxMulticenter):* Same graph, $w(v) = 1$, $ell(e) = 1$, $k = 1$, $B = 1$.

For any single center $p$, the farthest vertex is at distance 2
(the vertex diametrically opposite in $C_5$):
- Center at 0: $d(2, {0}) = 2 > 1$.
- Center at 1: $d(3, {1}) = 2 > 1$.
- (and similarly for any other choice)

No single vertex achieves $max_(v) d(v, {p}) lt.eq 1$. #sym.checkmark
