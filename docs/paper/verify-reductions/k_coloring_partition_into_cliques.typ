// Standalone verification proof: KColoring → PartitionIntoCliques
// Issue: #844

== K-Coloring $arrow.r$ Partition Into Cliques <sec:kcoloring-partitionintocliques>

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
  There is a polynomial-time reduction from K-Coloring to Partition Into Cliques. Given a graph $G = (V, E)$ and a positive integer $K$, the reduction constructs the complement graph $overline(G) = (V, overline(E))$ with the same clique bound $K' = K$. A proper $K$-coloring of $G$ exists if and only if the vertices of $overline(G)$ can be partitioned into at most $K'$ cliques.
] <thm:kcoloring-partitionintocliques>

#proof[
  _Construction._

  Let $(G, K)$ be a K-Coloring instance where $G = (V, E)$ is an undirected graph with $n = |V|$ vertices and $m = |E|$ edges, and $K >= 1$ is the number of available colors.

  + Compute the complement graph $overline(G) = (V, overline(E))$ where $overline(E) = { {u, v} : u, v in V, u != v, {u, v} in.not E }$. The vertex set $V$ is unchanged.
  + Set the clique bound $K' = K$.
  + Output the Partition Into Cliques instance $(overline(G), K')$.

  _Correctness._

  ($arrow.r.double$) Suppose $G$ admits a proper $K$-coloring $c : V -> {0, 1, dots, K-1}$. For each color $i in {0, 1, dots, K-1}$, define $V_i = { v in V : c(v) = i }$. Since $c$ is a proper coloring, for any two vertices $u, v in V_i$ we have $c(u) = c(v) = i$, so ${u, v} in.not E$ (no edge in $G$ between same-color vertices). By the definition of complement, ${u, v} in overline(E)$, meaning every pair in $V_i$ is adjacent in $overline(G)$. Hence each $V_i$ is a clique in $overline(G)$. The sets $V_0, V_1, dots, V_(K-1)$ partition $V$ into at most $K = K'$ cliques. Therefore $(overline(G), K')$ is a YES instance of Partition Into Cliques.

  ($arrow.l.double$) Suppose the vertices of $overline(G)$ can be partitioned into $k <= K'$ cliques $V_0, V_1, dots, V_(k-1)$. For each $i$, every pair $u, v in V_i$ satisfies ${u, v} in overline(E)$, which means ${u, v} in.not E$. Hence $V_i$ is an independent set in $G$. Define a coloring $c : V -> {0, 1, dots, k-1}$ by $c(v) = i$ whenever $v in V_i$. For any edge ${u, v} in E$, vertices $u$ and $v$ cannot belong to the same $V_i$ (since $V_i$ is independent in $G$), so $c(u) != c(v)$. Therefore $c$ is a proper $k$-coloring of $G$ with $k <= K' = K$ colors. Hence $(G, K)$ is a YES instance of K-Coloring.

  _Solution extraction._ Given a partition $V_0, V_1, dots, V_(k-1)$ of $overline(G)$ into cliques, assign color $i$ to every vertex in $V_i$. The resulting assignment is a valid $K$-coloring of $G$.
]

*Overhead.*

#table(
  columns: (auto, auto),
  align: (left, left),
  [*Target metric*], [*Formula*],
  [`num_vertices`], [$n$],
  [`num_edges`], [$binom(n, 2) - m = n(n-1)/2 - m$],
  [`num_cliques`], [$K$],
)

where $n$ = `num_vertices` and $m$ = `num_edges` of the source graph $G$.

*Feasible example (YES instance).*

Source: $G$ has $n = 5$ vertices ${0, 1, 2, 3, 4}$ with edges $E = {(0,1), (1,2), (2,3), (3,0), (0,2)}$ and $K = 3$.

The graph contains the triangle ${0, 1, 2}$, so at least 3 colors are needed. A valid 3-coloring exists: $c = [0, 1, 2, 1, 0]$ (vertex 0 gets color 0, vertex 1 gets color 1, vertex 2 gets color 2, vertex 3 gets color 1, vertex 4 gets color 0).

Verification: edge $(0,1)$: colors $0 != 1$ #sym.checkmark; edge $(1,2)$: colors $1 != 2$ #sym.checkmark; edge $(2,3)$: colors $2 != 1$ #sym.checkmark; edge $(3,0)$: colors $1 != 0$ #sym.checkmark; edge $(0,2)$: colors $0 != 2$ #sym.checkmark.

Target: $overline(G)$ has $n = 5$ vertices. Total possible edges: $binom(5,2) = 10$. Complement edges: $overline(E) = {(0,4), (1,3), (1,4), (2,4), (3,4)}$. So $|overline(E)| = 10 - 5 = 5$. Clique bound $K' = 3$.

Color classes from the coloring $c = [0, 1, 2, 1, 0]$: $V_0 = {0, 4}$, $V_1 = {1, 3}$, $V_2 = {2}$.

Check cliques in $overline(G)$: $V_0 = {0, 4}$: edge $(0, 4) in overline(E)$ #sym.checkmark; $V_1 = {1, 3}$: edge $(1, 3) in overline(E)$ #sym.checkmark; $V_2 = {2}$: singleton #sym.checkmark.

Three cliques, $3 <= K' = 3$ #sym.checkmark. The target is a YES instance.

*Infeasible example (NO instance).*

Source: $G$ is the complete graph $K_4$ on 4 vertices ${0, 1, 2, 3}$ with all 6 edges, and $K = 3$.

Since $K_4$ has chromatic number 4, it cannot be 3-colored. Every vertex is adjacent to every other vertex, so all 4 vertices need distinct colors, but only 3 are available.

Target: $overline(G)$ has 4 vertices and $binom(4,2) - 6 = 0$ edges (the complement of a complete graph is an empty graph). Clique bound $K' = 3$.

In $overline(G)$, the only cliques are singletons (no edges exist). Partitioning 4 vertices into singletons requires 4 groups, but $K' = 3 < 4$. Therefore $(overline(G), K' = 3)$ is a NO instance.

Verification of infeasibility: any partition into at most 3 groups must place at least 2 vertices in one group. But those 2 vertices have no edge in $overline(G)$, so they do not form a clique. Hence no valid partition into $<= 3$ cliques exists #sym.checkmark.
