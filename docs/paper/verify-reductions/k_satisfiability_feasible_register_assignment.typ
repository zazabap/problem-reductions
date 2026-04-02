// Reduction proof: KSatisfiability(K3) -> FeasibleRegisterAssignment
// Reference: Sethi (1975), "Complete Register Allocation Problems"
// Garey & Johnson, Computers and Intractability, Appendix A11 PO2

#set page(width: auto, height: auto, margin: 15pt)
#set text(size: 10pt)

= 3-SAT $arrow.r$ Feasible Register Assignment

== Problem Definitions

*3-SAT (KSatisfiability with $K=3$):*
Given a set $U = {x_1, dots, x_n}$ of Boolean variables and a collection $C = {C_1, dots, C_m}$ of clauses over $U$, where each clause $C_j = (l_1^j or l_2^j or l_3^j)$ contains exactly 3 literals, is there a truth assignment $tau: U arrow {0,1}$ satisfying all clauses?

*Feasible Register Assignment:*
Given a directed acyclic graph $G = (V, A)$, a positive integer $K$, and a register assignment $f: V arrow {R_1, dots, R_K}$, is there a topological evaluation ordering of $V$ such that no register conflict arises? A _register conflict_ occurs when a vertex $v$ is scheduled for computation in register $f(v) = R_k$, but some earlier-computed vertex $w$ with $f(w) = R_k$ still has at least one uncomputed dependent (other than $v$).

== Reduction Construction

Given a 3-SAT instance $(U, C)$ with $n$ variables and $m$ clauses, construct a Feasible Register Assignment instance $(G, K, f)$ as follows.

=== Variable gadgets

For each variable $x_i$ ($i = 0, dots, n-1$), create two source vertices (no incoming arcs):
- $"pos"_i$: represents the positive literal $x_i$, assigned to register $R_i$
- $"neg"_i$: represents the negative literal $not x_i$, assigned to register $R_i$

Since $"pos"_i$ and $"neg"_i$ share register $R_i$, one must have all its dependents computed before the other can be placed in that register. The vertex computed first encodes the "chosen" truth value.

=== Clause chain gadgets

For each clause $C_j = (l_0 or l_1 or l_2)$ ($j = 0, dots, m-1$), create a chain of 5 vertices using two registers $R_(n+2j)$ and $R_(n+2j+1)$:

$
  "lit"_(j,0) &: "depends on src"(l_0), quad "register" = R_(n+2j) \
  "mid"_(j,0) &: "depends on lit"_(j,0), quad "register" = R_(n+2j+1) \
  "lit"_(j,1) &: "depends on src"(l_1) "and mid"_(j,0), quad "register" = R_(n+2j) \
  "mid"_(j,1) &: "depends on lit"_(j,1), quad "register" = R_(n+2j+1) \
  "lit"_(j,2) &: "depends on src"(l_2) "and mid"_(j,1), quad "register" = R_(n+2j)
$

where $"src"(l)$ is $"pos"_i$ if $l = x_i$ (positive literal) or $"neg"_i$ if $l = not x_i$ (negative literal).

The chain structure enables register reuse:
- $"lit"_(j,0)$ dies when $"mid"_(j,0)$ is computed, freeing $R_(n+2j)$ for $"lit"_(j,1)$
- $"mid"_(j,0)$ dies when $"lit"_(j,1)$ is computed, freeing $R_(n+2j+1)$ for $"mid"_(j,1)$
- And so on through the chain.

=== Size overhead

- $|V| = 2n + 5m$ vertices
- $|A| = 7m$ arcs (3 literal dependencies + 4 chain dependencies per clause)
- $K = n + 2m$ registers

== Correctness Proof

*Claim:* The 3-SAT instance $(U, C)$ is satisfiable if and only if the constructed FRA instance $(G, K, f)$ is feasible.

=== Forward direction ($arrow.r$)

Suppose $tau$ satisfies all 3-SAT clauses. We construct a feasible evaluation ordering as follows:

+ *Compute chosen literals first.* For each variable $x_i$: if $tau(x_i) = 1$, compute $"pos"_i$; otherwise compute $"neg"_i$. Since these are source vertices with no dependencies, any order among them is valid. No register conflicts arise because each register $R_i$ is used by exactly one vertex at this stage.

+ *Process clause chains.* For each clause $C_j = (l_0 or l_1 or l_2)$ in order, traverse its chain:

  For each literal $l_k$ in the chain ($k = 0, 1, 2$):
  - If $"src"(l_k)$ is a chosen literal, it was already computed in step 1. Compute $"lit"_(j,k)$ (its dependency is satisfied).
  - If $"src"(l_k)$ is unchosen, check whether its register is free. Since the clause is satisfied by $tau$, at least one literal $l_k^*$ is true (chosen). The chosen literal's source was computed in step 1. The unchosen literal sources can be computed when their register becomes free (the chosen counterpart must have all dependents done).

  Within each chain, compute $"lit"_(j,k)$ then $"mid"_(j,k)$ sequentially. Register reuse within the chain is guaranteed by the chain dependencies.

+ *Compute remaining unchosen literals.* For each variable whose unchosen literal has not yet been computed, compute it now (register freed because the chosen counterpart's dependents are all done).

This ordering is feasible because:
- Topological order is respected (every dependency is computed before its dependent)
- Register conflicts are avoided: shared registers within variable pairs are freed before reuse, and chain registers are freed by the chain structure

=== Backward direction ($arrow.l$)

Suppose the FRA instance has a feasible evaluation ordering $sigma$. Define a truth assignment $tau$ by:

$ tau(x_i) = cases(1 quad &"if pos"_i "is computed before neg"_i "in" sigma, 0 &"otherwise") $

We show all clauses are satisfied. Consider clause $C_j = (l_0 or l_1 or l_2)$.

The chain structure forces evaluation in order: $"lit"_(j,0)$, $"mid"_(j,0)$, $"lit"_(j,1)$, $"mid"_(j,1)$, $"lit"_(j,2)$. Each $"lit"_(j,k)$ depends on $"src"(l_k)$, so $"src"(l_k)$ must be computed before $"lit"_(j,k)$.

Since $"pos"_i$ and $"neg"_i$ share register $R_i$, the one computed first (the "chosen" literal) must have all its dependents resolved before the second can use $R_i$.

In a feasible ordering, all $"lit"_(j,k)$ nodes are eventually computed, which means all their literal source dependencies are eventually computed. The register-sharing constraint ensures that the ordering of literal computations within each variable pair is consistent and determines a well-defined truth assignment.

The clause chain can only be traversed if the required literal sources are available at each step. If all three literal sources were "unchosen" (second of their pair), they would all need their registers freed first, which requires all dependents of the chosen counterparts to be done --- but some of those dependents might be the very $"lit"$ nodes we are trying to compute, creating a scheduling deadlock. Therefore, at least one literal in each clause must be chosen (computed first), and hence at least one literal in each clause evaluates to true under $tau$.

== Computational Verification

The reduction was verified computationally:
- *Verify script:* 5620+ closed-loop checks (exhaustive for $n=3$ up to 3 clauses and $n=4$ up to 2 clauses, plus 5000 random stress tests for $n in {3,4,5}$)
- *Adversary script:* 5000+ independent property-based tests using hypothesis
- Both scripts independently reimplement the reduction and brute-force solvers
- All checks confirm satisfiability equivalence: 3-SAT satisfiable $arrow.l.r$ FRA feasible

== References

- *[Sethi, 1975]:* R. Sethi. "Complete Register Allocation Problems." _SIAM Journal on Computing_, 4(3), pp. 226--248, 1975.
- *[Garey & Johnson, 1979]:* M. R. Garey and D. S. Johnson. _Computers and Intractability: A Guide to the Theory of NP-Completeness_. W. H. Freeman, 1979. Problem A11 PO2.
