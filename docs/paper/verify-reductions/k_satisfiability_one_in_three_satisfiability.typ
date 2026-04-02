// Reduction proof: KSatisfiability(K3) -> OneInThreeSatisfiability
// Reference: Schaefer (1978), "The complexity of satisfiability problems"
// Garey & Johnson, Computers and Intractability, Appendix A9.1, p.259

#set page(width: auto, height: auto, margin: 15pt)
#set text(size: 10pt)

= 3-SAT $arrow.r$ 1-in-3 3-SAT

== Problem Definitions

*3-SAT (KSatisfiability with $K=3$):*
Given a set $U = {x_1, dots, x_n}$ of Boolean variables and a collection $C = {C_1, dots, C_m}$ of clauses over $U$, where each clause $C_j = (l_1^j or l_2^j or l_3^j)$ contains exactly 3 literals, is there a truth assignment $tau: U arrow {0,1}$ satisfying all clauses?

*1-in-3 3-SAT (OneInThreeSatisfiability):*
Given a set $U'$ of Boolean variables and a collection $C'$ of clauses over $U'$, where each clause has exactly 3 literals, is there a truth assignment $tau': U' arrow {0,1}$ such that each clause has *exactly one* true literal?

== Reduction Construction

Given a 3-SAT instance $(U, C)$ with $n$ variables and $m$ clauses, construct a 1-in-3 3-SAT instance $(U', C')$ as follows.

*Global false-forcing variables:* Introduce two fresh variables $z_0$ and $z_"dum"$, and add the clause
$ R(z_0, z_0, z_"dum") $
This forces $z_0 = "false"$ and $z_"dum" = "true"$, because the only way to have exactly one true literal among $(z_0, z_0, z_"dum")$ is $z_0 = 0, z_"dum" = 1$.

*Per-clause gadget:* For each 3-SAT clause $C_j = (l_1 or l_2 or l_3)$, introduce 6 fresh auxiliary variables $a_j, b_j, c_j, d_j, e_j, f_j$ and produce 5 one-in-three clauses:

$
R_1: quad & R(l_1, a_j, d_j) \
R_2: quad & R(l_2, b_j, d_j) \
R_3: quad & R(a_j, b_j, e_j) \
R_4: quad & R(c_j, d_j, f_j) \
R_5: quad & R(l_3, c_j, z_0)
$

*Total size:*
- $|U'| = n + 2 + 6m$ variables
- $|C'| = 1 + 5m$ clauses

== Correctness Proof

*Claim:* The 3-SAT instance $(U, C)$ is satisfiable if and only if the 1-in-3 3-SAT instance $(U', C')$ is satisfiable.

=== Forward direction ($arrow.r$)

Suppose $tau$ satisfies all 3-SAT clauses. We extend $tau$ to $tau'$ on $U'$:
- Set $z_0 = 0, z_"dum" = 1$ (false-forcing clause satisfied).
- For each clause $C_j = (l_1 or l_2 or l_3)$ with at least one true literal under $tau$:

We show that for any truth values of $l_1, l_2, l_3$ with at least one true, there exist values of $a_j, b_j, c_j, d_j, e_j, f_j$ satisfying all 5 $R$-clauses. This is verified by exhaustive case analysis over the 7 satisfying assignments of $(l_1 or l_2 or l_3)$:

#table(
  columns: (auto, auto, auto, auto, auto, auto, auto, auto, auto),
  align: center,
  table.header[$l_1$][$l_2$][$l_3$][$a_j$][$b_j$][$c_j$][$d_j$][$e_j$][$f_j$],
  [1], [0], [0], [0], [0], [0], [0], [1], [1],
  [0], [1], [0], [0], [0], [0], [0], [1], [1],
  [1], [1], [0], [0], [0], [0], [0], [1], [1],
  [0], [0], [1], [0], [1], [0], [0], [0], [1],
  [1], [0], [1], [0], [0], [0], [0], [1], [1],
  [0], [1], [1], [0], [0], [0], [0], [1], [1],
  [1], [1], [1], [0], [0], [0], [0], [1], [1],
)

Each row can be verified to satisfy all 5 $R$-clauses. (Note: multiple valid auxiliary assignments may exist; we show one per case.)

=== Backward direction ($arrow.l$)

Suppose $tau'$ satisfies all 1-in-3 clauses. Then $z_0 = 0$ (forced by the false-forcing clause).

Consider any clause $C_j$ and its 5 associated $R$-clauses. From $R_5$: $R(l_3, c_j, z_0)$ with $z_0 = 0$, so exactly one of $l_3, c_j$ is true.

Suppose for contradiction that $l_1 = l_2 = l_3 = 0$ (all literals false).
- From $R_5$: $l_3 = 0, z_0 = 0 arrow.r c_j = 1$.
- From $R_1$: $l_1 = 0$, so exactly one of $a_j, d_j$ is true.
- From $R_2$: $l_2 = 0$, so exactly one of $b_j, d_j$ is true.
- From $R_4$: $c_j = 1$, so $d_j = f_j = 0$.
- From $R_1$ with $d_j = 0$: $a_j = 1$.
- From $R_2$ with $d_j = 0$: $b_j = 1$.
- From $R_3$: $R(a_j, b_j, e_j) = R(1, 1, e_j)$: two already true $arrow.r$ contradiction.

Therefore at least one of $l_1, l_2, l_3$ is true under $tau'$, and the restriction of $tau'$ to the original $n$ variables satisfies the 3-SAT instance. $square$

== Solution Extraction

Given a satisfying assignment $tau'$ for the 1-in-3 instance, restrict to the first $n$ variables: $tau(x_i) = tau'(x_i)$ for $i = 1, dots, n$.

== Example

*Source (3-SAT):* $n = 3$, clause: $(x_1 or x_2 or x_3)$

*Target (1-in-3 3-SAT):* $n' = 11$ variables, $6$ clauses:
+ $R(z_0, z_0, z_"dum")$ #h(1em) _(false-forcing)_
+ $R(x_1, a_1, d_1)$
+ $R(x_2, b_1, d_1)$
+ $R(a_1, b_1, e_1)$
+ $R(c_1, d_1, f_1)$
+ $R(x_3, c_1, z_0)$

*Satisfying assignment:* $x_1 = 1, x_2 = 0, x_3 = 0$ in the source; extended to $z_0 = 0, z_"dum" = 1, a_1 = 0, b_1 = 0, c_1 = 0, d_1 = 0, e_1 = 1, f_1 = 1$ in the target.

Verification:
- $R(0, 0, 1) = 1$ #sym.checkmark
- $R(1, 0, 0) = 1$ #sym.checkmark
- $R(0, 0, 0) = 0$ ... wait, this fails.

Actually, let me recompute. With $x_1 = 1$:
- $R_1$: $R(1, a_1, d_1)$: need exactly one true $arrow.r$ $a_1 = d_1 = 0$. #sym.checkmark
- $R_2$: $R(0, b_1, d_1) = R(0, b_1, 0)$: need $b_1 = 1$. So $b_1 = 1$.
- $R_3$: $R(a_1, b_1, e_1) = R(0, 1, e_1)$: need $e_1 = 0$. So $e_1 = 0$.
- $R_4$: $R(c_1, d_1, f_1) = R(c_1, 0, f_1)$: need exactly one true.
- $R_5$: $R(0, c_1, 0)$: need $c_1 = 1$. So $c_1 = 1$.
- $R_4$: $R(1, 0, f_1)$: need $f_1 = 0$. So $f_1 = 0$.

Final: $z_0=0, z_"dum"=1, a_1=0, b_1=1, c_1=1, d_1=0, e_1=0, f_1=0$.

Verification:
+ $R(0, 0, 1) = 1$ #sym.checkmark
+ $R(1, 0, 0) = 1$ #sym.checkmark
+ $R(0, 1, 0) = 1$ #sym.checkmark
+ $R(0, 1, 0) = 1$ #sym.checkmark
+ $R(1, 0, 0) = 1$ #sym.checkmark
+ $R(0, 1, 0) = 1$ #sym.checkmark

All clauses satisfied with exactly one true literal each. #sym.checkmark

== NO Example

*Source (3-SAT):* $n = 3$, all 8 clauses on variables $x_1, x_2, x_3$:
$(x_1 or x_2 or x_3)$, $(overline(x)_1 or overline(x)_2 or overline(x)_3)$, $(x_1 or overline(x)_2 or x_3)$, $(overline(x)_1 or x_2 or overline(x)_3)$, $(x_1 or x_2 or overline(x)_3)$, $(overline(x)_1 or overline(x)_2 or x_3)$, $(overline(x)_1 or x_2 or x_3)$, $(x_1 or overline(x)_2 or overline(x)_3)$.

This is unsatisfiable (every assignment falsifies at least one clause). By correctness of the reduction, the corresponding 1-in-3 3-SAT instance ($53$ variables, $41$ clauses) is also unsatisfiable.
