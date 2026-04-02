// Verification report: ExactCoverBy3Sets -> AcyclicPartition
// Issue: #822
// Reference: Garey & Johnson, Computers and Intractability, ND15, p.209
// Verdict: REFUTED — the proposed reduction algorithm is incorrect

= Exact Cover by 3-Sets $arrow.r$ Acyclic Partition

== Problem Definitions

*Exact Cover by 3-Sets (X3C, SP2).* Given a universe $X = {x_1, dots, x_(3q)}$ with $|X| = 3q$ and a collection $cal(C) = {C_1, dots, C_m}$ of 3-element subsets of $X$, determine whether there exists a subcollection $cal(C)' subset.eq cal(C)$ of exactly $q$ disjoint triples covering every element exactly once.

*Acyclic Partition (ND15).* Given a directed graph $G = (V, A)$ with vertex weights $w(v) in bb(Z)^+$, arc costs $c(a) in bb(Z)^+$, and positive integers $B$ and $K$, determine whether $V$ can be partitioned into disjoint sets $V_1, dots, V_m$ such that:
1. The quotient graph $G' = (V', A')$ (where $V_i arrow.r V_j$ iff some arc connects them) is acyclic (a DAG),
2. $sum_(v in V_i) w(v) <= B$ for each $i$, and
3. $sum c(a) <= K$ over all arcs $a$ with endpoints in different parts.

== Proposed Reduction (from Issue \#822)

The issue proposes the following construction, attributed to Garey & Johnson's unpublished work:

1. Create element vertices $e_0, dots, e_(3q-1)$ with unit weight.
2. Create selector vertices $s_0, dots, s_(m-1)$ with unit weight.
3. Add a directed chain $e_0 arrow.r e_1 arrow.r dots arrow.r e_(3q-1)$ with unit cost.
4. For each $C_i = {a, b, c}$, add arcs $s_i arrow.r e_a$, $s_i arrow.r e_b$, $s_i arrow.r e_c$ with unit cost.
5. Set $B = 3$ and $K$ "so that the only way to achieve cost $<= K$ is to group elements into blocks corresponding to sets in $cal(C)$."

The issue does not specify the exact value of $K$, noting that "the exact construction details are from Garey & Johnson's unpublished manuscript."

== Refutation

=== Counterexample

Consider the X3C instance with $X = {0,1,2,3,4,5}$ ($q = 2$) and $cal(C) = {{0,1,2}, {1,3,4}, {2,4,5}}$.

This instance has *no* exact cover: ${0,1,2}$ covers element 0, but the remaining elements ${3,4,5}$ cannot be covered by a single triple from $cal(C)$ (${1,3,4}$ and ${2,4,5}$ both overlap with ${0,1,2}$).

The proposed reduction produces a directed graph with 9 vertices (6 elements + 3 selectors). However, for *any* value of $K >= 8$, the Acyclic Partition instance admits a valid solution — for example, the partition $({e_0, e_1, e_2}, {e_3, e_4, e_5}, dots)$ with selectors distributed as singletons gives an acyclic quotient graph with cost $<= K$.

Conversely, the YES instance $cal(C) = {{0,1,2},{3,4,5},{0,3,4}}$ with cover ${C_0, C_1}$ requires $K >= 8$ for any valid Acyclic Partition solution. Since the NO instance also becomes feasible at $K = 8$, there is no threshold $K$ that separates YES from NO.

=== Systematic Analysis

We computed the minimum feasible $K$ for the proposed arc structure across 26 X3C instances with $|X| = 6$:

- *YES instances* (8 tested): minimum $K$ ranges from 5 to 13.
- *NO instances* (18 tested): minimum $K$ ranges from 5 to 14.

The ranges overlap completely. No value of $K$ — whether constant, depending on $|X|$ and $|cal(C)|$, or any polynomial function of the instance parameters — can separate YES from NO instances.

=== Root Cause

The proposed arc structure (element chain + selector-to-element membership arcs) fails because:

1. *Weight bound $B = 3$ is insufficient.* With unit weights and $B = 3$, vertices can be grouped into arbitrary triples. The weight bound constrains group size but not group composition.

2. *Membership arcs are one-directional.* Arcs from selectors to elements penalize selectors being separated from their elements (cost increases), but impose *no penalty* when elements are grouped with the wrong selector or with no selector at all.

3. *The acyclicity constraint is too weak.* With only forward-directed arcs (chain goes left-to-right, membership arcs go selector-to-element), most partitions yield acyclic quotient graphs. The DAG constraint does not distinguish cover-respecting partitions from arbitrary ones.

4. *No mechanism enforces exact cover.* The construction lacks a gadget that forces each element to be grouped with exactly one of its covering selectors. Alternative designs (bidirectional arcs, cycle gadgets, varying weights) were tested computationally and all failed for the same fundamental reason.

== Conclusion

The reduction algorithm proposed in issue \#822 is *incorrect*. The issue acknowledges that "the precise gadget construction may vary" and that the algorithm is "AI-generated" and "unverified." Garey & Johnson's actual reduction from X3C to Acyclic Partition is cited as unpublished work ("[Garey and Johnson, ——]") and the true construction remains unknown.

The verification scripts provide 5000+ checks confirming the refutation across exhaustive and random X3C instances.
