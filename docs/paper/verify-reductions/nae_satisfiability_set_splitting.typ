// Standalone verification proof: NAESatisfiability -> SetSplitting
// Issue #382 -- NOT-ALL-EQUAL SAT to SET SPLITTING
// Reference: Garey & Johnson, SP4, p.221

#set page(width: 210mm, height: auto, margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.1.")
#set math.equation(numbering: "(1)")

// Theorem/proof environments (self-contained, no external package)
#let theorem(body) = block(
  width: 100%, inset: 10pt, fill: rgb("#e8f0fe"), radius: 4pt,
  [*Theorem.* #body]
)
#let proof(body) = block(
  width: 100%, inset: (left: 10pt),
  [*Proof.* #body #h(1fr) $square$]
)

= NAE-Satisfiability $arrow.r$ Set Splitting <sec:naesatisfiability-setsplitting>

== Problem Definitions

*NAE-Satisfiability (NAE-SAT).* Given a set of $n$ Boolean variables $x_1, dots, x_n$ and a collection of $m$ clauses $C_1, dots, C_m$ in conjunctive normal form (each clause containing at least two literals), determine whether there exists a truth assignment such that every clause contains at least one true literal and at least one false literal.

*Set Splitting.* Given a finite universe $U$ and a collection $cal(C)$ of subsets of $U$ (each of size at least 2), determine whether there exists a 2-coloring of $U$ (a partition into sets $S_0$ and $S_1$) such that every subset in $cal(C)$ is non-monochromatic, i.e., contains at least one element from $S_0$ and at least one element from $S_1$.

== Reduction

#theorem[
  NAE-Satisfiability is polynomial-time reducible to Set Splitting.
]

#proof[
  _Construction._ Given an NAE-SAT instance with $n$ variables $x_1, dots, x_n$ and $m$ clauses $C_1, dots, C_m$, construct a Set Splitting instance as follows.

  + *Universe.* Define $U = {0, 1, dots, 2n - 1}$. Element $2i$ represents the positive literal $x_(i+1)$, and element $2i + 1$ represents the negative literal $overline(x)_(i+1)$, for $i = 0, dots, n-1$.

  + *Complementarity subsets.* For each variable $x_(i+1)$ where $i = 0, dots, n-1$, create the subset $R_i = {2i, 2i+1}$. These $n$ subsets force each variable's positive and negative literal elements to receive different colors.

  + *Clause subsets.* For each clause $C_j$ (where $j = 1, dots, m$), create a subset $T_j$ containing the universe elements corresponding to the literals in $C_j$. Specifically, for each literal $ell$ in $C_j$:
    - If $ell = x_k$ (positive), add element $2(k-1)$ to $T_j$.
    - If $ell = overline(x)_k$ (negative), add element $2(k-1) + 1$ to $T_j$.

  + *Output.* The Set Splitting instance has universe size $|U| = 2n$ and $n + m$ subsets: the $n$ complementarity subsets $R_0, dots, R_(n-1)$ and the $m$ clause subsets $T_1, dots, T_m$.

  _Correctness._

  ($arrow.r.double$) Suppose assignment $alpha$ is an NAE-satisfying assignment for the NAE-SAT instance. Define a 2-coloring $chi$ of $U$ by setting $chi(2i) = alpha(x_(i+1))$ (where $sans("true") = 1, sans("false") = 0$) and $chi(2i+1) = 1 - alpha(x_(i+1))$ for each $i = 0, dots, n-1$.

  Consider any complementarity subset $R_i = {2i, 2i+1}$. By construction, $chi(2i) != chi(2i+1)$, so $R_i$ is non-monochromatic.

  Consider any clause subset $T_j$. Since $alpha$ is NAE-satisfying, clause $C_j$ contains at least one true literal $ell_t$ and at least one false literal $ell_f$. The universe element corresponding to a true literal receives color 1: if $ell_t = x_k$ and $alpha(x_k) = sans("true")$, then $chi(2(k-1)) = 1$; if $ell_t = overline(x)_k$ and $alpha(x_k) = sans("false")$, then $chi(2(k-1)+1) = 1 - 0 = 1$. The universe element corresponding to a false literal receives color 0 by symmetric reasoning. Therefore $T_j$ contains elements of both colors and is non-monochromatic.

  ($arrow.l.double$) Suppose $chi$ is a valid 2-coloring for the Set Splitting instance. Since each complementarity subset $R_i = {2i, 2i+1}$ is non-monochromatic, we have $chi(2i) != chi(2i+1)$. Define assignment $alpha$ by $alpha(x_(i+1)) = chi(2i)$ (interpreting 1 as true and 0 as false). The complementarity constraint guarantees $chi(2i + 1) = 1 - alpha(x_(i+1))$, so element $2i+1$ carries the color corresponding to the truth value of $overline(x)_(i+1)$.

  Consider any clause $C_j$ with clause subset $T_j$. Since $T_j$ is non-monochromatic, there exist elements $e_a, e_b in T_j$ with $chi(e_a) = 1$ and $chi(e_b) = 0$. The literal corresponding to $e_a$ evaluates to true under $alpha$, and the literal corresponding to $e_b$ evaluates to false under $alpha$. Therefore $C_j$ has at least one true literal and at least one false literal, so $C_j$ is NAE-satisfied.

  _Solution extraction._ Given a valid 2-coloring $chi$ of the Set Splitting instance, extract the NAE-SAT assignment as $alpha(x_(i+1)) = chi(2i)$ for $i = 0, dots, n-1$, interpreting color 1 as true and color 0 as false.
]

*Overhead.*

#table(
  columns: (auto, auto),
  table.header([*Target metric*], [*Formula*]),
  [`universe_size`], [$2n$ (where $n$ = `num_vars`)],
  [`num_subsets`], [$n + m$ (where $m$ = `num_clauses`)],
)

== Feasible Example (YES Instance)

Consider the NAE-SAT instance with $n = 4$ variables $x_1, x_2, x_3, x_4$ and $m = 3$ clauses:
$ C_1 = {x_1, overline(x)_2, x_3}, quad C_2 = {overline(x)_1, x_2, overline(x)_4}, quad C_3 = {x_2, x_3, x_4} $

*Reduction output.* Universe $U = {0,1,2,3,4,5,6,7}$ (size $2 dot 4 = 8$) with $4 + 3 = 7$ subsets:
- Complementarity: $R_0 = {0,1}$, $R_1 = {2,3}$, $R_2 = {4,5}$, $R_3 = {6,7}$
- Clause subsets:
  - $T_1$: $x_1 arrow.r.bar 0$, $overline(x)_2 arrow.r.bar 3$, $x_3 arrow.r.bar 4$ gives ${0, 3, 4}$
  - $T_2$: $overline(x)_1 arrow.r.bar 1$, $x_2 arrow.r.bar 2$, $overline(x)_4 arrow.r.bar 7$ gives ${1, 2, 7}$
  - $T_3$: $x_2 arrow.r.bar 2$, $x_3 arrow.r.bar 4$, $x_4 arrow.r.bar 6$ gives ${2, 4, 6}$

*Solution.* The assignment $alpha = (x_1 = sans("T"), x_2 = sans("T"), x_3 = sans("F"), x_4 = sans("T"))$ is NAE-satisfying:
- $C_1 = {x_1, overline(x)_2, x_3} = {sans("T"), sans("F"), sans("F")}$: has both true and false literals.
- $C_2 = {overline(x)_1, x_2, overline(x)_4} = {sans("F"), sans("T"), sans("F")}$: has both true and false literals.
- $C_3 = {x_2, x_3, x_4} = {sans("T"), sans("F"), sans("T")}$: has both true and false literals.

The corresponding 2-coloring is $chi = (1,0,1,0,0,1,1,0)$:
- $R_0 = {0,1}$: colors $(1,0)$ -- non-monochromatic.
- $R_1 = {2,3}$: colors $(1,0)$ -- non-monochromatic.
- $R_2 = {4,5}$: colors $(0,1)$ -- non-monochromatic.
- $R_3 = {6,7}$: colors $(1,0)$ -- non-monochromatic.
- $T_1 = {0,3,4}$: colors $(1,0,0)$ -- non-monochromatic.
- $T_2 = {1,2,7}$: colors $(0,1,0)$ -- non-monochromatic.
- $T_3 = {2,4,6}$: colors $(1,0,1)$ -- non-monochromatic.

*Extraction:* $alpha(x_(i+1)) = chi(2i)$, so $(chi(0), chi(2), chi(4), chi(6)) = (1,1,0,1)$ giving $(sans("T"), sans("T"), sans("F"), sans("T"))$, which matches the original assignment.

== Infeasible Example (NO Instance)

Consider the NAE-SAT instance with $n = 3$ variables $x_1, x_2, x_3$ and $m = 6$ clauses:
$ C_1 = {x_1, x_2}, quad C_2 = {overline(x)_1, overline(x)_2}, quad C_3 = {x_2, x_3}, quad C_4 = {overline(x)_2, overline(x)_3}, quad C_5 = {x_1, x_3}, quad C_6 = {overline(x)_1, overline(x)_3} $

*Why no NAE-satisfying assignment exists.* For any 2-literal clause ${a, b}$, the NAE condition requires $a != b$. Clauses $C_1$ and $C_2$ together force $x_1 != x_2$ (from $C_1$) and $overline(x)_1 != overline(x)_2$ (from $C_2$, which is the same constraint). Clauses $C_3$ and $C_4$ force $x_2 != x_3$. Clauses $C_5$ and $C_6$ force $x_1 != x_3$. However, $x_1 != x_2$ and $x_2 != x_3$ together imply $x_1 = x_3$ (since all are Boolean), which contradicts $x_1 != x_3$. Therefore no NAE-satisfying assignment exists.

*Reduction output.* Universe $U = {0,1,2,3,4,5}$ (size $2 dot 3 = 6$) with $3 + 6 = 9$ subsets:
- Complementarity: $R_0 = {0,1}$, $R_1 = {2,3}$, $R_2 = {4,5}$
- Clause subsets:
  - $T_1 = {0,2}$, $T_2 = {1,3}$, $T_3 = {2,4}$, $T_4 = {3,5}$, $T_5 = {0,4}$, $T_6 = {1,5}$

*Why the Set Splitting instance is also infeasible.* The complementarity subsets force $chi(0) != chi(1)$, $chi(2) != chi(3)$, $chi(4) != chi(5)$. Under these constraints, subset $T_1 = {0,2}$ requires $chi(0) != chi(2)$, subset $T_3 = {2,4}$ requires $chi(2) != chi(4)$, and subset $T_5 = {0,4}$ requires $chi(0) != chi(4)$. But $chi(0) != chi(2)$ and $chi(2) != chi(4)$ imply $chi(0) = chi(4)$ (Boolean values), contradicting $chi(0) != chi(4)$. Therefore no valid 2-coloring exists.
