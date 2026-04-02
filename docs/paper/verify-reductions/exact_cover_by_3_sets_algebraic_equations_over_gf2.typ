// Standalone Typst proof: ExactCoverBy3Sets -> AlgebraicEquationsOverGF2
// Issue #859

#set page(width: auto, height: auto, margin: 20pt)
#set text(size: 10pt)

#import "@preview/ctheorems:1.1.3": thmbox, thmplain, thmproof, thmrules
#show: thmrules.with(qed-symbol: $square$)

#let theorem = thmbox("theorem", "Theorem")
#let proof = thmproof("proof", "Proof")

== Exact Cover by 3-Sets $arrow.r$ Algebraic Equations over GF(2) <sec:x3c-gf2>

#theorem[
  Exact Cover by 3-Sets (X3C) is polynomial-time reducible to Algebraic Equations over GF(2).
] <thm:x3c-gf2>

#proof[
  _Construction._
  Let $(X, cal(C))$ be an X3C instance where $X = {0, 1, dots, 3q - 1}$ is the universe with $|X| = 3q$,
  and $cal(C) = {C_1, C_2, dots, C_n}$ is a collection of 3-element subsets of $X$.
  Define $n$ binary variables $x_1, x_2, dots, x_n$ over GF(2), one for each set $C_j in cal(C)$.

  For each element $u_i in X$ (where $0 <= i <= 3q - 1$), let $S_i = {j : u_i in C_j}$ denote
  the set of indices of subsets containing $u_i$.
  Construct the following polynomial equations over GF(2):

  + *Linear covering constraint* for each element $u_i$:
    $ sum_(j in S_i) x_j + 1 = 0 quad (mod 2) $
    This requires that an odd number of the sets containing $u_i$ are selected.

  + *Pairwise exclusion constraint* for each element $u_i$ and each pair $j, k in S_i$ with $j < k$:
    $ x_j dot x_k = 0 quad (mod 2) $
    This forbids selecting two sets that both contain $u_i$.

  The target instance has $n$ variables and at most $3q + sum_(i=0)^(3q-1) binom(|S_i|, 2)$ equations.

  _Correctness._

  ($arrow.r.double$)
  Suppose ${C_(j_1), C_(j_2), dots, C_(j_q)}$ is an exact cover of $X$.
  Set $x_(j_ell) = 1$ for $ell = 1, dots, q$ and $x_j = 0$ for all other $j$.
  For each element $u_i$, exactly one index $j in S_i$ has $x_j = 1$,
  so $sum_(j in S_i) x_j = 1$ and thus $1 + 1 = 0$ in GF(2), satisfying the linear constraint.
  For the pairwise constraints: since at most one $x_j = 1$ among the indices in $S_i$,
  every product $x_j dot x_k = 0$ is satisfied.

  ($arrow.l.double$)
  Suppose $(x_1, dots, x_n) in {0,1}^n$ satisfies all equations.
  For each element $u_i$, the linear constraint $sum_(j in S_i) x_j + 1 = 0$ (mod 2)
  means $sum_(j in S_i) x_j equiv 1$ (mod 2), so an odd number of sets containing $u_i$ are selected.
  The pairwise constraints $x_j dot x_k = 0$ for all pairs in $S_i$ mean that no two selected sets
  both contain $u_i$. An odd number with no two selected means exactly one set covers $u_i$.
  Since every element is covered exactly once and each set has 3 elements,
  the total number of selected elements is $3 dot (text("number of selected sets"))$.
  But every element is covered once, so $3 dot (text("number of selected sets")) = 3q$,
  giving exactly $q$ selected sets. These sets form an exact cover.

  _Solution extraction._
  Given a satisfying assignment $(x_1, dots, x_n)$ to the GF(2) system,
  define the subcollection $cal(C)' = {C_j : x_j = 1}$.
  By the backward direction above, $cal(C)'$ is an exact cover of $X$.
]

*Overhead.*

#table(
  columns: (auto, auto),
  stroke: 0.5pt,
  [*Target metric*], [*Formula*],
  [`num_variables`], [$n$ (`num_subsets`)],
  [`num_equations`], [$3q + sum_(i=0)^(3q-1) binom(|S_i|, 2)$ (at most `universe_size` $+$ `universe_size` $dot d^2 slash 2$)],
)

where $d = max_i |S_i|$ is the maximum number of sets containing any single element.

*Feasible example (YES).*

Source X3C instance: $X = {0, 1, 2, 3, 4, 5, 6, 7, 8}$ (so $q = 3$), with subsets:
- $C_1 = {0, 1, 2}$, $C_2 = {3, 4, 5}$, $C_3 = {6, 7, 8}$, $C_4 = {0, 3, 6}$

Variables: $x_1, x_2, x_3, x_4$.

Covering constraints (linear):
- Element 0 ($in C_1, C_4$): $x_1 + x_4 + 1 = 0$
- Element 1 ($in C_1$ only): $x_1 + 1 = 0$
- Element 2 ($in C_1$ only): $x_1 + 1 = 0$
- Element 3 ($in C_2, C_4$): $x_2 + x_4 + 1 = 0$
- Element 4 ($in C_2$ only): $x_2 + 1 = 0$
- Element 5 ($in C_2$ only): $x_2 + 1 = 0$
- Element 6 ($in C_3, C_4$): $x_3 + x_4 + 1 = 0$
- Element 7 ($in C_3$ only): $x_3 + 1 = 0$
- Element 8 ($in C_3$ only): $x_3 + 1 = 0$

Pairwise exclusion constraints:
- Element 0: $x_1 dot x_4 = 0$
- Element 3: $x_2 dot x_4 = 0$
- Element 6: $x_3 dot x_4 = 0$

After deduplication: 6 linear equations + 3 pairwise equations = 9 equations (before dedup: 9 + 3 = 12).

Assignment $(x_1, x_2, x_3, x_4) = (1, 1, 1, 0)$:

Linear: $1+0+1=0$ #sym.checkmark, $1+1=0$ #sym.checkmark, $1+0+1=0$ #sym.checkmark, $1+1=0$ #sym.checkmark, $1+0+1=0$ #sym.checkmark, $1+1=0$ #sym.checkmark.

Pairwise: $1 dot 0 = 0$ #sym.checkmark, $1 dot 0 = 0$ #sym.checkmark, $1 dot 0 = 0$ #sym.checkmark.

This corresponds to selecting ${C_1, C_2, C_3}$, an exact cover.

*Infeasible example (NO).*

Source X3C instance: $X = {0, 1, 2, 3, 4, 5, 6, 7, 8}$ (so $q = 3$), with subsets:
- $C_1 = {0, 1, 2}$, $C_2 = {0, 3, 4}$, $C_3 = {0, 5, 6}$, $C_4 = {7, 8, 3}$

No exact cover exists because element 0 appears in $C_1, C_2, C_3$.
Selecting any one of these leaves at most 6 remaining elements to cover,
but $C_4$ is the only set not containing element 0, and it covers only 3 elements.
So at most 6 elements can be covered, but we need all 9 covered.
Concretely: if we pick $C_1$ (covering {0,1,2}), then to cover {3,4,5,6,7,8} we need two more disjoint triples from ${C_2, C_3, C_4}$.
$C_2 = {0,3,4}$ overlaps with $C_1$ on element 0. Similarly $C_3 = {0,5,6}$ overlaps.
Only $C_4 = {7,8,3}$ is disjoint with $C_1$, but then {4,5,6} remains uncovered with no available set.
The same argument applies symmetrically for choosing $C_2$ or $C_3$ first.

Variables: $x_1, x_2, x_3, x_4$.

Covering constraints (linear):
- Element 0 ($in C_1, C_2, C_3$): $x_1 + x_2 + x_3 + 1 = 0$
- Element 1 ($in C_1$ only): $x_1 + 1 = 0$
- Element 2 ($in C_1$ only): $x_1 + 1 = 0$
- Element 3 ($in C_2, C_4$): $x_2 + x_4 + 1 = 0$
- Element 4 ($in C_2$ only): $x_2 + 1 = 0$
- Element 5 ($in C_3$ only): $x_3 + 1 = 0$
- Element 6 ($in C_3$ only): $x_3 + 1 = 0$
- Element 7 ($in C_4$ only): $x_4 + 1 = 0$
- Element 8 ($in C_4$ only): $x_4 + 1 = 0$

Pairwise exclusion constraints:
- Element 0: $x_1 dot x_2 = 0$, $x_1 dot x_3 = 0$, $x_2 dot x_3 = 0$
- Element 3: $x_2 dot x_4 = 0$

The linear constraints for elements 1, 2 force $x_1 = 1$.
Elements 4 force $x_2 = 1$. Elements 5, 6 force $x_3 = 1$. Elements 7, 8 force $x_4 = 1$.
But then element 0: $x_1 + x_2 + x_3 + 1 = 1 + 1 + 1 + 1 = 0$ (mod 2) -- the linear constraint is satisfied!
However, the pairwise constraint $x_1 dot x_2 = 1 dot 1 = 1 != 0$ is violated.
No satisfying assignment exists, confirming no exact cover.
