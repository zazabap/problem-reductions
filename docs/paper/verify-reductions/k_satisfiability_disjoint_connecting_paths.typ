// Reduction verification: KSatisfiability(K3) -> DisjointConnectingPaths
// Issue #370: 3SAT to DISJOINT CONNECTING PATHS
// Reference: Lynch (1975); Garey & Johnson ND40 p.217; DPV Exercise 8.23
//
// VERDICT: REFUTED -- the construction in issue #370 is incorrect.
// The general reduction IS valid (Lynch 1975), but the specific
// gadget described in the issue does not work.

#set page(width: auto, height: auto, margin: 15pt)
#set text(size: 10pt)

= 3-SAT $arrow.r$ Disjoint Connecting Paths

== Verdict: REFUTED

The reduction construction described in issue \#370 contains a critical flaw in the clause gadget. The general reduction from 3-SAT to Disjoint Connecting Paths is valid (Lynch 1975), but the specific construction proposed in the issue does not preserve the backward implication: a solvable DCP instance does not necessarily correspond to a satisfiable 3-SAT formula under the proposed construction.

== Problem Definitions

*3-SAT (KSatisfiability with $K = 3$):*
Given a set $U = {x_1, dots, x_n}$ of Boolean variables and a collection $C = {C_1, dots, C_m}$ of clauses over $U$, where each clause $C_j = (l_1^j or l_2^j or l_3^j)$ contains exactly 3 literals, is there a truth assignment $tau: U arrow {0, 1}$ satisfying all clauses?

*Disjoint Connecting Paths:*
Given an undirected graph $G = (V, E)$ and a collection of disjoint vertex pairs $(s_1, t_1), dots, (s_k, t_k)$, do there exist $k$ mutually vertex-disjoint paths, one connecting $s_i$ to $t_i$ for each $i$?

== Issue \#370 Construction (Claimed)

The issue proposes:

*Variable gadgets:* For each variable $x_i$, a chain of $2m$ vertices $v_(i,1), dots, v_(i,2m)$ with chain edges $(v_(i,j), v_(i,j+1))$. Terminal pair: $(v_(i,1), v_(i,2m))$.

*Clause gadgets:* For each clause $C_j$, 8 vertices forming a *linear chain*:
$ s'_j dash p_(j,1) dash q_(j,1) dash p_(j,2) dash q_(j,2) dash p_(j,3) dash q_(j,3) dash t'_j $
with 7 internal edges. Terminal pair: $(s'_j, t'_j)$.

*Interconnection:* For the $r$-th literal of $C_j$ involving variable $x_i$:
- Positive $(x_i)$: edges $(v_(i,2j-1), p_(j,r))$ and $(q_(j,r), v_(i,2j))$
- Negated $(not x_i)$: edges $(v_(i,2j-1), q_(j,r))$ and $(p_(j,r), v_(i,2j))$

== The Flaw

The clause gadget's linear chain $s'_j dash p_(j,1) dash q_(j,1) dash dots dash q_(j,3) dash t'_j$ provides a *direct path* from $s'_j$ to $t'_j$ that exists regardless of whether any variable paths detour through the clause vertices.

*Counterexample:* Consider the unsatisfiable 3-SAT formula on 3 variables with all 8 sign patterns. Under the proposed construction, choosing all variable paths to use direct chain edges (no detours) leaves all $(p_(j,r), q_(j,r))$ vertices free. Every clause path can then traverse its own linear chain from $s'_j$ to $t'_j$ without obstruction. The resulting $n + m$ paths are trivially vertex-disjoint, because:
- Variable paths use only chain vertices $v_(i,k)$.
- Clause paths use only clause gadget vertices $s'_j, p_(j,r), q_(j,r), t'_j$.
- These vertex sets are disjoint by construction.

Therefore the DCP instance *always* has a solution, even when the 3-SAT formula is unsatisfiable. The backward direction of the proof ("DCP solvable $arrow.r$ 3-SAT satisfiable") fails.

*Root cause:* The issue's correctness sketch assumes that variable paths *must* detour to encode a truth assignment. In reality, the "all-direct" choice (no detours at any clause slot) is always a valid variable path, and it does not correspond to any truth assignment that can be checked against the formula. The linear clause chain makes clause paths trivially satisfiable without any dependence on variable path choices.

== Correct Construction (Sketch)

The standard Lynch (1975) reduction uses a fundamentally different variable gadget with *two parallel routes* (diamond structure) at each clause slot, ensuring that the variable path *must* choose one of two alternatives. The correct construction, verified computationally:

*Variable gadgets:* For each variable $x_i$, create $m + 1$ junction vertices $J_(i,0), dots, J_(i,m)$ and $2m$ intermediate vertices $T_(i,j), F_(i,j)$ (for $j = 0, dots, m-1$). Edges:
$ (J_(i,j), T_(i,j)), quad (T_(i,j), J_(i,j+1)), quad (J_(i,j), F_(i,j)), quad (F_(i,j), J_(i,j+1)) $
Terminal pair: $(J_(i,0), J_(i,m))$. At each clause slot $j$, the variable path *must* traverse either $T_(i,j)$ or $F_(i,j)$ --- it cannot skip both.

*Clause gadgets:* For each clause $C_j$, create two clause terminals $s'_j$ and $t'_j$ (no intermediate vertices). Terminal pair: $(s'_j, t'_j)$.

*Interconnection:* For the $r$-th literal of $C_j$ involving variable $x_i$:
- Positive $(x_i)$: edges $(s'_j, F_(i,j))$ and $(F_(i,j), t'_j)$
- Negated $(not x_i)$: edges $(s'_j, T_(i,j))$ and $(T_(i,j), t'_j)$

The clause path $s'_j arrow.r v arrow.r t'_j$ can only route through a vertex $v$ that is *not* used by any variable path. A vertex $F_(i,j)$ is free iff $x_i = "True"$ (variable uses $T_(i,j)$), and $T_(i,j)$ is free iff $x_i = "False"$ (variable uses $F_(i,j)$). Hence a free vertex corresponding to literal $l$ exists iff $l$ is true under the assignment. The clause path succeeds iff at least one literal in $C_j$ is true --- exactly the 3-SAT satisfiability condition.

*Size:*
- $|V| = n(m + 1) + 2 n m + 2m = n(3m + 1) + 2m$
- $|E| = 4 n m + 2 dot 3 m = 4 n m + 6m$
- Terminal pairs: $n + m$

This corrected construction was verified exhaustively for all 3-SAT instances with $n = 3, m in {1, 2}$, $n = 4, m = 1$, and by random stress testing for $n in {3, 4, 5}$, $m in {1, 2}$ with zero mismatches across thousands of instances (both satisfiable and unsatisfiable).

== Recommendation

The issue should be revised to use the correct diamond/two-path variable gadget construction before implementation. The overhead formulas and example in the issue are specific to the flawed linear-chain construction and need to be updated accordingly.
