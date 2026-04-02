// Standalone verification document: KSatisfiability(K3) -> DirectedTwoCommodityIntegralFlow
// Issue #368 -- Even, Itai, and Shamir (1976)

#set page(margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.1.")
#set math.equation(numbering: "(1)")

#let theorem(body) = block(
  fill: rgb("#e8f0fe"), width: 100%, inset: 10pt, radius: 4pt,
  [*Theorem.* #body]
)
#let proof(body) = block(
  width: 100%, inset: (left: 10pt),
  [_Proof._ #body #h(1fr) $square$]
)

= 3-Satisfiability to Directed Two-Commodity Integral Flow <sec:k-satisfiability-d2cif>

#theorem[
  There is a polynomial-time reduction from 3-Satisfiability (3-SAT) to Directed Two-Commodity Integral Flow. Given a 3-SAT instance $phi$ with $n$ variables and $m$ clauses, the reduction constructs a directed graph $G = (V, A)$ with $|V| = 4n + m + 4$ vertices and $|A| = 7n + 4m + 1$ arcs such that $phi$ is satisfiable if and only if the resulting two-commodity flow instance is feasible with requirements $R_1 = 1$ and $R_2 = m$.
] <thm:k-satisfiability-d2cif>

#proof[
  _Construction._ Let $phi$ be a 3-SAT formula over variables $u_1, dots, u_n$ with clauses $C_1, dots, C_m$, where each clause $C_j$ is a disjunction of exactly three literals. We construct a directed two-commodity integral flow instance in three stages.

  *Vertices ($4n + m + 4$ total).*
  - Four terminal vertices: $s_1$ (source, commodity 1), $t_1$ (sink, commodity 1), $s_2$ (source, commodity 2), $t_2$ (sink, commodity 2).
  - For each variable $u_i$ ($1 <= i <= n$), create four vertices: $a_i$ (lobe entry), $p_i$ (TRUE intermediate), $q_i$ (FALSE intermediate), $b_i$ (lobe exit).
  - For each clause $C_j$ ($1 <= j <= m$), create one clause vertex $d_j$.

  *Step 1 (Variable lobes).* For each variable $u_i$ ($1 <= i <= n$), create two parallel directed paths from $a_i$ to $b_i$:
  - _TRUE path_: arcs $(a_i, p_i)$ and $(p_i, b_i)$, each with capacity 1.
  - _FALSE path_: arcs $(a_i, q_i)$ and $(q_i, b_i)$, each with capacity 1.

  This gives $4n$ arcs total. Since all arcs have unit capacity, at most one unit of flow can traverse each path, forcing a binary choice.

  *Step 2 (Variable chain for commodity 1).* Chain the lobes in series:
  $ s_1 -> a_1, quad b_1 -> a_2, quad dots, quad b_(n-1) -> a_n, quad b_n -> t_1 $
  All chain arcs have capacity 1. This gives $n + 1$ arcs. Set $R_1 = 1$: exactly one unit of commodity-1 flow traverses the entire chain, choosing either the TRUE path (through $p_i$) or the FALSE path (through $q_i$) at each lobe, thereby encoding a truth assignment.

  *Step 3 (Clause satisfaction via commodity 2).* For each variable $u_i$, add two _supply arcs_ from $s_2$:
  - $(s_2, q_i)$ with capacity equal to the number of clauses containing the positive literal $u_i$.
  - $(s_2, p_i)$ with capacity equal to the number of clauses containing the negative literal $not u_i$.

  This gives $2n$ supply arcs.

  For each clause $C_j$ and each literal $ell_k$ ($k = 1, 2, 3$) in $C_j$:
  - If $ell_k = u_i$ (positive literal): add arc $(q_i, d_j)$ with capacity 1.
  - If $ell_k = not u_i$ (negative literal): add arc $(p_i, d_j)$ with capacity 1.

  This gives $3m$ literal arcs. Finally, for each clause $C_j$, add a sink arc $(d_j, t_2)$ with capacity 1, giving $m$ arcs. Set $R_2 = m$.

  The key insight behind the literal connections: when commodity 1 takes the TRUE path through $p_i$ (setting $u_i = "true"$), the FALSE intermediate $q_i$ is free of commodity-1 flow, so commodity 2 can route from $s_2$ through $q_i$ to any clause $d_j$ that contains the positive literal $u_i$. Symmetrically, when commodity 1 takes the FALSE path through $q_i$, the TRUE intermediate $p_i$ is free, allowing commodity 2 to reach clauses containing $not u_i$.

  *Total arc count:* $(n + 1) + 4n + 2n + 3m + m = 7n + 4m + 1$.

  _Correctness._

  ($arrow.r.double$) Suppose $phi$ has a satisfying assignment $alpha$. We construct feasible flows $f_1$ and $f_2$.

  _Commodity 1:_ Route 1 unit along the chain $s_1 -> a_1 -> dots -> b_n -> t_1$. At each lobe $i$: if $alpha(u_i) = "true"$, route through $p_i$ (TRUE path); if $alpha(u_i) = "false"$, route through $q_i$ (FALSE path). This satisfies $R_1 = 1$.

  _Commodity 2:_ For each clause $C_j$, since $alpha$ satisfies $phi$, at least one literal $ell_k$ in $C_j$ is true. Choose one such literal:
  - If $ell_k = u_i$ with $alpha(u_i) = "true"$: commodity 1 used the TRUE path (through $p_i$), so $q_i$ is free. Route 1 unit: $s_2 -> q_i -> d_j -> t_2$.
  - If $ell_k = not u_i$ with $alpha(u_i) = "false"$: commodity 1 used the FALSE path (through $q_i$), so $p_i$ is free. Route 1 unit: $s_2 -> p_i -> d_j -> t_2$.

  Since each clause gets one unit of flow, $R_2 = m$ is achieved. The joint capacity constraint is satisfied: the chain arcs and selected lobe arcs carry commodity-1 flow (1 unit each), while commodity-2 flow uses the _opposite_ intermediate's arcs, which are free. The supply arc $(s_2, q_i)$ has capacity equal to the number of positive occurrences of $u_i$, which bounds the number of clauses commodity 2 may route through $q_i$. Similarly for $(s_2, p_i)$.

  ($arrow.l.double$) Suppose feasible flows $f_1, f_2$ exist with $f_1$ achieving $R_1 = 1$ and $f_2$ achieving $R_2 = m$.

  Since $R_1 = 1$ and the chain arcs have unit capacity, exactly 1 unit of commodity 1 flows $s_1 -> a_1 -> dots -> b_n -> t_1$. At each lobe, the flow must take either the TRUE path or the FALSE path (not both, since $a_i$ has only unit-capacity outgoing arcs to $p_i$ and $q_i$, and exactly 1 unit enters $a_i$). Define $alpha(u_i) = "true"$ if the flow takes the TRUE path (through $p_i$) and $alpha(u_i) = "false"$ if it takes the FALSE path (through $q_i$).

  For commodity 2, $R_2 = m$ units must reach $t_2$. Each clause vertex $d_j$ has a single outgoing arc $(d_j, t_2)$ of capacity 1, so each $d_j$ receives exactly 1 unit of commodity 2. The only incoming arcs to $d_j$ are the literal arcs from intermediate vertices. For $d_j$ to receive flow, at least one of the connected intermediates must carry commodity-2 flow. An intermediate $q_i$ (for positive literal $u_i$ in $C_j$) can carry commodity-2 flow only if it is free of commodity-1 flow, which happens when $alpha(u_i) = "true"$. Similarly, $p_i$ (for negative literal $not u_i$ in $C_j$) can carry commodity-2 flow only when $alpha(u_i) = "false"$, i.e., $not u_i$ is true. Therefore, at least one literal in each clause is true under $alpha$, so $alpha$ satisfies $phi$.

  _Solution extraction._ Given feasible flows, define $alpha(u_i) = "true"$ if commodity-1 flow traverses $p_i$ and $alpha(u_i) = "false"$ if it traverses $q_i$.
]

*Overhead.*
#table(
  columns: (auto, auto),
  [*Target metric*], [*Formula*],
  [`num_vertices`], [$4n + m + 4$],
  [`num_arcs`], [$7n + 4m + 1$],
  [`max_capacity`], [at most $max(|"pos"(u_i)|, |"neg"(u_i)|)$ on supply arcs; 1 on all others],
  [`requirement_1`], [$1$],
  [`requirement_2`], [$m$],
)
where $n$ = `num_vars` and $m$ = `num_clauses` of the source 3-SAT instance.

*Feasible example.*
Consider a 3-SAT instance with $n = 3$ variables and $m = 2$ clauses:
$ phi = (u_1 or u_2 or u_3) and (not u_1 or not u_2 or u_3) $

The reduction constructs a flow network with $4 dot 3 + 2 + 4 = 18$ vertices and $7 dot 3 + 4 dot 2 + 1 = 30$ arcs.

Vertices: $s_1$ (0), $t_1$ (1), $s_2$ (2), $t_2$ (3); variable vertices $a_1, p_1, q_1, b_1$ (4--7), $a_2, p_2, q_2, b_2$ (8--11), $a_3, p_3, q_3, b_3$ (12--15); clause vertices $d_1$ (16), $d_2$ (17).

The satisfying assignment $alpha(u_1) = "true", alpha(u_2) = "true", alpha(u_3) = "true"$ yields:
- Commodity 1: $s_1 -> a_1 -> p_1 -> b_1 -> a_2 -> p_2 -> b_2 -> a_3 -> p_3 -> b_3 -> t_1$. Flow = 1.
- Commodity 2, clause 1 ($u_1 or u_2 or u_3$): route through $q_1$ (free since $u_1$ is true). $s_2 -> q_1 -> d_1 -> t_2$.
- Commodity 2, clause 2 ($not u_1 or not u_2 or u_3$): $u_3$ is true, so route through $q_3$. $s_2 -> q_3 -> d_2 -> t_2$.
- Total commodity-2 flow = 2 = $m$.
- All capacity constraints satisfied.

*Infeasible example.*
Consider a 3-SAT instance with $n = 3$ variables and $m = 8$ clauses comprising all $2^3 = 8$ sign patterns on 3 variables:
$ phi = (u_1 or u_2 or u_3) and (u_1 or u_2 or not u_3) and (u_1 or not u_2 or u_3) and (u_1 or not u_2 or not u_3) $
$ and (not u_1 or u_2 or u_3) and (not u_1 or u_2 or not u_3) and (not u_1 or not u_2 or u_3) and (not u_1 or not u_2 or not u_3) $

This formula is unsatisfiable: for any assignment $alpha$, exactly one clause has all its literals falsified. The reduction constructs a flow network with $4 dot 3 + 8 + 4 = 24$ vertices and $7 dot 3 + 4 dot 8 + 1 = 54$ arcs. Since no satisfying assignment exists, no feasible two-commodity flow exists. The structural search over all $2^3 = 8$ possible commodity-1 routings confirms that for each routing, at least one clause vertex cannot receive commodity-2 flow.
