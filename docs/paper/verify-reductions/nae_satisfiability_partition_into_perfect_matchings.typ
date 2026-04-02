// Standalone verification proof: NAESatisfiability -> PartitionIntoPerfectMatchings
// Issue: #845

#set page(margin: 2cm)
#set text(size: 10pt)
#set heading(numbering: "1.1.")

== NAE Satisfiability $arrow.r$ Partition into Perfect Matchings <sec:naesat-pipm>

*Theorem.* _Not-All-Equal Satisfiability (NAE-SAT) polynomial-time reduces to
Partition into Perfect Matchings with $K = 2$.
Given a NAE-SAT instance with $n$ variables and $m$ clauses
(each clause has at least 2 literals, padded to exactly 3),
the constructed graph has $4n + 16m$ vertices and $3n + 21m$ edges._ #label("thm:naesat-pipm")

*Proof.*

_Construction._
Let $F$ be a NAE-SAT instance with variables $x_1, dots, x_n$ and
clauses $C_1, dots, C_m$. We build a graph $G$ with $K = 2$ as follows.

+ *Normalise clauses.* If any clause has exactly 2 literals $(ell_1, ell_2)$,
  replace it with $(ell_1, ell_1, ell_2)$ by duplicating the first literal.
  After normalisation every clause has exactly 3 literals.

+ *Variable gadgets.* For each variable $x_i$ ($1 <= i <= n$), create
  four vertices $t_i, t'_i, f_i, f'_i$ with edges
  $(t_i, t'_i)$, $(f_i, f'_i)$, and $(t_i, f_i)$.
  In any valid 2-partition, $t_i$ and $t'_i$ must share a group
  (they are each other's unique same-group neighbour),
  and $f_i$ and $f'_i$ must share a group.
  The edge $(t_i, f_i)$ forces $t_i$ and $f_i$ into different groups
  (otherwise $t_i$ would have two same-group neighbours).
  Define: $x_i = "TRUE"$ when $t_i$ is in group 0.

+ *Signal pairs.* For each clause $C_j$ ($1 <= j <= m$) and
  literal position $k in {0, 1, 2}$, create two vertices
  $s_(j,k)$ and $s'_(j,k)$ with edge $(s_(j,k), s'_(j,k))$.
  These always share a group; the group of $s_(j,k)$ will
  encode the literal's truth value.

+ *Clause gadgets (K#sub[4]).* For each clause $C_j$, create four
  vertices $w_(j,0), w_(j,1), w_(j,2), w_(j,3)$ forming a complete graph
  $K_4$ (six edges). Add connection edges $(s_(j,k), w_(j,k))$ for
  $k = 0, 1, 2$. Each connection edge forces $s_(j,k)$ and $w_(j,k)$ into
  different groups. In any valid 2-partition the four $K_4$ vertices
  split exactly 2 + 2 (any other split gives a vertex with $!= 1$
  same-group neighbour). Among ${w_(j,0), w_(j,1), w_(j,2)}$,
  exactly one is paired with $w_(j,3)$ and the other two share a group.
  Hence exactly one of the three signals differs from the other two,
  enforcing the not-all-equal condition.

+ *Equality chains.* For each variable $x_i$, collect all clause-position
  pairs where $x_i$ appears. Order them arbitrarily. Process each
  occurrence in order:

  - Let $s_(j,k)$ be the signal vertex for this occurrence.
  - Let $"src"$ be the *chain source*: for the first positive occurrence,
    $"src" = t_i$; for the first negative occurrence, $"src" = f_i$;
    for subsequent occurrences of the same sign, $"src"$ is the signal
    vertex of the previous same-sign occurrence.
  - Create an intermediate pair $(mu, mu')$ with edge $(mu, mu')$.
  - Add edges $("src", mu)$ and $(s_(j,k), mu)$.
  - Since both $"src"$ and $s_(j,k)$ are forced into a different group
    from $mu$, they are forced into the same group.

  Positive-occurrence signals all propagate from $t_i$: they all share
  $t_i$'s group. Negative-occurrence signals all propagate from $f_i$:
  they share $f_i$'s group, which is the opposite of $t_i$'s group.
  So a positive literal $x_i$ in a clause has its signal in $t_i$'s group,
  and a negative literal $not x_i$ has its signal in $f_i$'s group
  (the complement), correctly encoding truth values.

_Correctness._

($arrow.r.double$) Suppose $F$ has a NAE-satisfying assignment $alpha$.
Assign group 0 to $t_i, t'_i$ if $alpha(x_i) = "TRUE"$, else group 1.
Assign $f_i, f'_i$ to the opposite group.
By the equality chains, each signal $s_(j,k)$ receives the group
corresponding to its literal's value under $alpha$.
For each clause $C_j$, not all three literals are equal under $alpha$,
so not all three signals are in the same group.
Equivalently, not all three $w_(j,k)$ ($k = 0, 1, 2$) are in the same group.
Since the $K_4$ must split 2 + 2, exactly one of $w_(j,0), w_(j,1), w_(j,2)$
is paired with $w_(j,3)$. This split exists because the NAE condition
guarantees at least one signal differs.
Specifically, let $k^*$ be a position where the literal's value differs
from the majority; pair $w_(j,k^*)$ with $w_(j,3)$.
Every vertex has exactly one same-group neighbour, so $G$ admits a valid
2-partition.

($arrow.l.double$) Suppose $G$ admits a partition into 2 perfect matchings.
The variable gadget forces $t_i$ and $f_i$ into different groups.
Define $alpha(x_i) = "TRUE"$ iff $t_i$ is in group 0.
The equality chains force each signal to carry the correct literal value.
The $K_4$ splits 2 + 2, so among $w_(j,0), w_(j,1), w_(j,2)$,
not all three are in the same group.
Since $w_(j,k)$ is in the opposite group from $s_(j,k)$,
not all three signals are in the same group,
hence not all three literals have the same value.
Every clause satisfies the NAE condition, so $alpha$ is a NAE-satisfying
assignment.

_Solution extraction._
Given a valid 2-partition (a configuration assigning each vertex to group 0 or 1),
read $alpha(x_i) = ("config"[t_i] == 0)$ for each variable $x_i$.
This runs in $O(n)$ time. $square$

=== Overhead

#table(
  columns: (auto, auto),
  [Target metric], [Formula],
  [`num_vertices`], [$4n + 16m$],
  [`num_edges`], [$3n + 21m$],
  [`num_matchings`], [$2$],
)
where $n$ = number of variables, $m$ = number of clauses (after padding 2-literal clauses).

=== Feasible example

NAE-SAT with $n = 3$ variables ${x_1, x_2, x_3}$ and $m = 2$ clauses:
- $C_1 = (x_1, x_2, x_3)$
- $C_2 = (not x_1, x_2, not x_3)$

Assignment $alpha = (x_1 = "TRUE", x_2 = "TRUE", x_3 = "FALSE")$:
- $C_1$: values $("TRUE", "TRUE", "FALSE")$ --- not all equal. $checkmark$
- $C_2$: values $("FALSE", "TRUE", "TRUE")$ --- not all equal. $checkmark$

Constructed graph $G$: $4 dot 3 + 16 dot 2 = 44$ vertices, $3 dot 3 + 21 dot 2 = 51$ edges, $K = 2$.
- Variable gadgets: $(t_1, t'_1, f_1, f'_1), (t_2, t'_2, f_2, f'_2), (t_3, t'_3, f_3, f'_3)$
  with 3 edges each = 9 edges.
- Signal pairs: 6 pairs ($s_(1,0), s'_(1,0)$ through $s_(2,2), s'_(2,2)$) = 6 edges.
- $K_4$ gadgets: 2 gadgets $times$ 6 edges = 12 edges.
- Connection edges: 6 edges.
- Equality chain: 6 links (one per literal occurrence) $times$ 3 edges = 18 edges.
  Total: $9 + 6 + 12 + 6 + 18 = 51$ edges. $checkmark$

Under $alpha = ("TRUE", "TRUE", "FALSE")$:
- $t_1, t'_1$ in group 0; $f_1, f'_1$ in group 1.
- $t_2, t'_2$ in group 0; $f_2, f'_2$ in group 1.
- $t_3, t'_3$ in group 1; $f_3, f'_3$ in group 0.
- Clause 1 signals: $s_(1,0)$ (pos $x_1$) in group 0, $s_(1,1)$ (pos $x_2$) in group 0,
  $s_(1,2)$ (pos $x_3$) in group 1. Not all equal. $checkmark$
- Clause 2 signals: $s_(2,0)$ (neg $x_1$) in group 1, $s_(2,1)$ (pos $x_2$) in group 0,
  $s_(2,2)$ (neg $x_3$) in group 0. Not all equal. $checkmark$
- $K_4$ gadgets can be completed: each splits 2+2 consistently.

=== Infeasible example

NAE-SAT with $n = 3$ variables ${x_1, x_2, x_3}$ and $m = 4$ clauses:
- $C_1 = (x_1, x_2, x_3)$
- $C_2 = (x_1, x_2, not x_3)$
- $C_3 = (x_1, not x_2, x_3)$
- $C_4 = (not x_1, x_2, x_3)$

This instance is NAE-unsatisfiable. Checking all $2^3 = 8$ assignments:
- $(0,0,0)$: $C_1 = (F,F,F)$ all false. $times$
- $(0,0,1)$: $C_1 = (F,F,T)$ OK; $C_2 = (F,F,F)$ all false. $times$
- $(0,1,0)$: $C_1 = (F,T,F)$ OK; $C_3 = (F,F,F)$ all false. $times$
- $(0,1,1)$: $C_1 = (F,T,T)$ OK; $C_2 = (F,T,F)$ OK; $C_3 = (F,F,T)$ OK; $C_4 = (T,T,T)$ all true. $times$
- $(1,0,0)$: $C_1 = (T,F,F)$ OK; $C_4 = (F,F,F)$ all false. $times$
- $(1,0,1)$: $C_1 = (T,F,T)$ OK; $C_2 = (T,F,F)$ OK; $C_3 = (T,T,T)$ all true. $times$
- $(1,1,0)$: $C_1 = (T,T,F)$ OK; $C_2 = (T,T,T)$ all true. $times$
- $(1,1,1)$: $C_1 = (T,T,T)$ all true. $times$

No assignment satisfies all four clauses simultaneously.
The constructed graph $G$ has $4 dot 3 + 16 dot 4 = 76$ vertices,
$3 dot 3 + 21 dot 4 = 93$ edges, $K = 2$.
Since the NAE-SAT instance is unsatisfiable, $G$ admits no partition into 2 perfect matchings.
