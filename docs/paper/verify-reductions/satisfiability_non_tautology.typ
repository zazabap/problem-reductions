// Standalone verification proof: Satisfiability → NonTautology
// Issue: #868

#import "@preview/ctheorems:1.1.3": thmbox, thmplain, thmproof, thmrules
#show: thmrules.with(qed-symbol: $square$)
#let theorem = thmbox("theorem", "Theorem")
#let proof = thmproof("proof", "Proof")

#set page(width: 6in, height: auto, margin: 1cm)
#set text(size: 10pt)

== Satisfiability $arrow.r$ Non-Tautology <sec:satisfiability-nontautology>

#theorem[
  Satisfiability reduces to Non-Tautology in polynomial time. Given a CNF
  formula $phi$ over $n$ variables with $m$ clauses, the reduction constructs a
  DNF formula $E$ over the same $n$ variables with $m$ disjuncts such that
  $phi$ is satisfiable if and only if $E$ is not a tautology.
] <thm:satisfiability-nontautology>

#proof[
  _Construction._

  Let $phi = C_1 and C_2 and dots and C_m$ be a CNF formula over variables
  $U = {x_1, dots, x_n}$, where each clause $C_j$ is a disjunction of
  literals.

  + Define $E = not phi$. By De Morgan's laws:
    $
      E = not C_1 or not C_2 or dots or not C_m
    $
  + For each clause $C_j = (l_1 or l_2 or dots or l_k)$, its negation is:
    $
      not C_j = (overline(l_1) and overline(l_2) and dots and overline(l_k))
    $
    where $overline(l)$ denotes the complement of literal $l$ (i.e., $overline(x_i) = not x_i$ and $overline(not x_i) = x_i$).
  + The result is a DNF formula $E = D_1 or D_2 or dots or D_m$ where each
    disjunct $D_j = (overline(l_1) and overline(l_2) and dots and overline(l_k))$
    is the conjunction of the negated literals from clause $C_j$.

  _Correctness._

  ($arrow.r.double$) Suppose $phi$ is satisfiable, witnessed by an assignment
  $alpha$ with $alpha models phi$. Then $alpha$ makes every clause $C_j$ true.
  Since $E = not phi$, we have $alpha models not(not phi)$, so $alpha$ makes
  $E$ false. Therefore $E$ has a falsifying assignment, and $E$ is not a
  tautology.

  ($arrow.l.double$) Suppose $E$ is not a tautology, witnessed by a falsifying
  assignment $beta$ with $beta tack.r.not E$. Since $E = not phi$, we have
  $beta tack.r.not not phi$, which means $beta models phi$. Therefore $phi$ is
  satisfiable.

  _Solution extraction._

  Given a falsifying assignment $beta$ for $E$ (the Non-Tautology witness),
  return $beta$ directly as the satisfying assignment for $phi$. No
  transformation is needed: the variables are identical and the truth values
  are unchanged.
]

*Overhead.*
#table(
  columns: (auto, auto),
  [Target metric], [Formula],
  [`num_vars`], [$n$ (same variables)],
  [`num_disjuncts`], [$m$ (one disjunct per clause)],
  [total literals], [$sum_j |C_j|$ (same count)],
)

*Feasible (YES) example.*

Source (SAT, CNF) with $n = 4$ variables and $m = 4$ clauses:
$
  phi = (x_1 or not x_2 or x_3) and (not x_1 or x_2 or x_4) and (x_2 or not x_3 or not x_4) and (not x_1 or not x_2 or x_3)
$

Applying the construction, negate each clause:
- $D_1 = not C_1 = (not x_1 and x_2 and not x_3)$
- $D_2 = not C_2 = (x_1 and not x_2 and not x_4)$
- $D_3 = not C_3 = (not x_2 and x_3 and x_4)$
- $D_4 = not C_4 = (x_1 and x_2 and not x_3)$

Target (Non-Tautology, DNF):
$
  E = D_1 or D_2 or D_3 or D_4
$

Satisfying assignment for $phi$: $x_1 = top, x_2 = top, x_3 = top, x_4 = bot$.
- $C_1 = top or bot or top = top$
- $C_2 = bot or top or bot = top$
- $C_3 = top or bot or top = top$
- $C_4 = bot or bot or top = top$

This assignment falsifies $E$:
- $D_1 = bot and top and bot = bot$
- $D_2 = top and bot and top = bot$
- $D_3 = bot and top and bot = bot$
- $D_4 = top and top and bot = bot$
- $E = bot or bot or bot or bot = bot$ $checkmark$

*Infeasible (NO) example.*

Source (SAT, CNF) with $n = 3$ variables and $m = 4$ clauses:
$
  phi = (x_1) and (not x_1) and (x_2 or x_3) and (not x_2 or not x_3)
$

This formula is unsatisfiable: $C_1$ requires $x_1 = top$ and $C_2$ requires $x_1 = bot$, a contradiction.

Applying the construction:
- $D_1 = (not x_1)$
- $D_2 = (x_1)$
- $D_3 = (not x_2 and not x_3)$
- $D_4 = (x_2 and x_3)$

Target: $E = (not x_1) or (x_1) or (not x_2 and not x_3) or (x_2 and x_3)$

$E$ is a tautology: for any assignment, either $x_1 = top$ (making $D_2$ true) or $x_1 = bot$ (making $D_1$ true). Therefore $E$ has no falsifying assignment, confirming that Non-Tautology reports "no" and $phi$ is indeed unsatisfiable.
