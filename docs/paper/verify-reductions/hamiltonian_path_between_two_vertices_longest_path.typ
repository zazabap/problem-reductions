// Verification proof: HamiltonianPathBetweenTwoVertices -> LongestPath (#359)
#import "@preview/ctheorems:1.1.3": thmbox, thmplain, thmproof, thmrules

#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)
#set heading(numbering: "1.1")

#show: thmrules.with(qed-symbol: $square$)
#let theorem = thmbox("theorem", "Theorem", fill: rgb("#e8e8f8"))
#let proof = thmproof("proof", "Proof")

== Hamiltonian Path Between Two Vertices $arrow.r$ Longest Path <sec:hpbtv-longestpath>

#theorem[
  Hamiltonian Path Between Two Vertices is polynomial-time reducible to
  Longest Path. Given a source instance with $n$ vertices and $m$ edges, the
  constructed Longest Path instance has $n$ vertices, $m$ edges, unit edge
  lengths, and bound $K = n - 1$.
] <thm:hpbtv-longestpath>

#proof[
  _Construction._
  Let $(G, s, t)$ be a Hamiltonian Path Between Two Vertices instance, where
  $G = (V, E)$ is an undirected graph with $n = |V|$ vertices and $m = |E|$
  edges, and $s, t in V$ are two distinguished vertices with $s eq.not t$.

  Construct a Longest Path instance $(G', ell, s', t', K)$ as follows.

  + Set $G' = G$ (the same graph with $n$ vertices and $m$ edges).

  + For every edge $e in E$, set $ell(e) = 1$ (unit edge lengths).

  + Set $s' = s$ and $t' = t$ (same source and target vertices).

  + Set $K = n - 1$ (the number of edges in any Hamiltonian path on $n$ vertices).

  The Longest Path decision problem asks: does $G'$ contain a simple path
  from $s'$ to $t'$ whose total edge length is at least $K$?

  _Correctness._

  ($arrow.r.double$) Suppose there exists a Hamiltonian path $P = (v_0, v_1, dots, v_(n-1))$
  in $G$ from $s$ to $t$. Then $P$ visits all $n$ vertices exactly once and
  traverses $n - 1$ edges. Since $P$ is a path in $G = G'$, it is also a
  simple path from $s' = s$ to $t' = t$ in $G'$. Its total length is
  $sum_(i=0)^(n-2) ell({v_i, v_(i+1)}) = sum_(i=0)^(n-2) 1 = n - 1 = K$.
  Therefore the Longest Path instance is a YES instance.

  ($arrow.l.double$) Suppose $G'$ contains a simple path $P$ from $s'$ to $t'$
  with total length at least $K = n - 1$. Since all edge lengths equal $1$,
  the total length equals the number of edges in $P$. A simple path in a graph
  with $n$ vertices can traverse at most $n - 1$ edges (visiting each vertex
  at most once). Since $P$ has at least $n - 1$ edges and at most $n - 1$
  edges, the path has exactly $n - 1$ edges and visits all $n$ vertices
  exactly once. Therefore $P$ is a Hamiltonian path from $s = s'$ to $t = t'$
  in $G = G'$, and the source instance is a YES instance.

  _Solution extraction._
  Given a Longest Path witness (a binary edge-selection vector $x in {0, 1}^m$
  encoding a simple $s'$-$t'$ path of length at least $K$), we extract a
  Hamiltonian path configuration (a vertex permutation) as follows: start at
  $s$, and at each step follow the unique selected edge to the next unvisited
  vertex, continuing until $t$ is reached. The resulting vertex sequence is
  the Hamiltonian $s$-$t$ path.
]

*Overhead.*
#table(
  columns: (auto, auto),
  [*Target metric*], [*Formula*],
  [`num_vertices`], [$n$],
  [`num_edges`], [$m$],
  [edge lengths], [all $1$],
  [bound $K$], [$n - 1$],
)

*Feasible example (YES instance).*
Consider a graph $G$ on $5$ vertices ${0, 1, 2, 3, 4}$ with $7$ edges:
${0,1}, {0,2}, {1,2}, {1,3}, {2,4}, {3,4}, {0,3}$.
Let $s = 0$ and $t = 4$.

_Source:_ A Hamiltonian path from $0$ to $4$ exists: $0 arrow 1 arrow 3 arrow 0$... let us
verify more carefully. The path $0 arrow 3 arrow 1 arrow 2 arrow 4$ visits all $5$ vertices,
starts at $s = 0$, ends at $t = 4$, and uses edges ${0,3}, {3,1}, {1,2}, {2,4}$, all of
which are in $E$. This is a valid Hamiltonian $s$-$t$ path.

_Target:_ The Longest Path instance has $G' = G$ with $5$ vertices and $7$ edges, all
edge lengths $1$, $s' = 0$, $t' = 4$, $K = 5 - 1 = 4$. The path
$0 arrow 3 arrow 1 arrow 2 arrow 4$ has $4$ edges, each of length $1$, for total length
$4 = K$. The target is a YES instance.

_Extraction:_ The edge selection vector marks the $4$ edges
${0,3}, {1,3}, {1,2}, {2,4}$ as selected. Tracing from $s = 0$: the selected
neighbor of $0$ is $3$; from $3$, the unvisited selected neighbor is $1$;
from $1$, the unvisited selected neighbor is $2$; from $2$, the unvisited
selected neighbor is $4 = t$. Recovered path: $[0, 3, 1, 2, 4]$.

*Infeasible example (NO instance).*
Consider a graph $G$ on $5$ vertices ${0, 1, 2, 3, 4}$ with $4$ edges:
${0,1}, {1,2}, {2,3}, {0,3}$.
Let $s = 0$ and $t = 4$.

_Source:_ Vertex $4$ is isolated (has no incident edges). No path from $0$ to
$4$ exists, let alone a Hamiltonian path. The source is a NO instance.

_Target:_ The Longest Path instance has $G' = G$ with $5$ vertices and $4$ edges, all
edge lengths $1$, $s' = 0$, $t' = 4$, $K = 4$. Since vertex $4$ has degree $0$
in $G'$, no simple path from $s' = 0$ can reach $t' = 4$, so no path of
length $gt.eq K$ exists. The target is a NO instance.

_Verification:_ The longest simple path starting from vertex $0$ can visit at most
vertices ${0, 1, 2, 3}$ (the connected component of $0$), yielding at most $3$ edges.
Even ignoring the endpoint constraint, $3 < 4 = K$. Both source and target are infeasible.
