// Remaining Tier 1 Reduction Rules — 56 rules with mathematical content
// From issue #770, both models exist. Excludes the 34 verified in PR #992.

#set page(paper: "a4", margin: (x: 2cm, y: 2.5cm))
#set text(font: "New Computer Modern", size: 10pt)
#set par(justify: true)
#set heading(numbering: "1.1")
#set math.equation(numbering: "(1)")

#import "@preview/ctheorems:1.1.3": thmbox, thmplain, thmproof, thmrules
#show: thmrules.with(qed-symbol: $square$)

#let theorem = thmbox("theorem", "Theorem", stroke: 0.5pt)
#let lemma = thmbox("lemma", "Lemma", stroke: 0.5pt)
#let proof = thmproof("proof", "Proof")

#align(center)[
  #text(size: 18pt, weight: "bold")[Remaining Tier 1 Reduction Rules]

  #v(0.5em)
  #text(size: 12pt)[56 Proposed NP-Hardness Reductions]

  #v(0.3em)
  #text(size: 10pt, fill: gray)[From issue \#770 — both models exist, not yet implemented]
]

#v(1em)
#outline(indent: 1.5em, depth: 2)
#pagebreak()


= 3-DIMENSIONAL MATCHING


== 3-DIMENSIONAL MATCHING $arrow.r$ NUMERICAL 3-DIMENSIONAL MATCHING #text(size: 8pt, fill: orange)[ \[Blocked\] ] #text(size: 8pt, fill: gray)[(\#390)]


=== Specialization Note

````
This rule's source problem (3-DIMENSIONAL MATCHING / 3DM) is a specialization of SET PACKING (MaximumSetPacking). Implementation should wait until 3DM is available as a codebase model.
````


#pagebreak()


= 3-SATISFIABILITY


== 3-SATISFIABILITY $arrow.r$ MULTIPLE CHOICE BRANCHING #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#243)]


=== Reference

````
> [ND11] MULTIPLE CHOICE BRANCHING
> INSTANCE: Directed graph G=(V,A), a weight w(a)∈Z^+ for each arc a∈A, a partition of A into disjoint sets A_1,A_2,...,A_m, and a positive integer K.
> QUESTION: Is there a subset A'⊆A with ∑_{a∈A'} w(a)≥K such that no two arcs in A' enter the same vertex, A' contains no cycles, and A' contains at most one arc from each of the A_i, 1≤i≤m?
> Reference: [Garey and Johnson, ——]. Transformation from 3SAT.
> Comment: Remains NP-complete even if G is strongly connected and all weights are equal. If all A_i have |A_i|=1, the problem becomes simply that of finding a "maximum weight branching," a 2-matroid intersection problem that can be solved in polynomial time (e.g., see [Tarjan, 1977]). (In a strongly connected graph, a maximum weight branching can be viewed as a maximum weight directed spanning tree.) Similarly, if the graph is symmetric, the problem becomes equivalent to the "multiple choice spanning tree" problem, another 2-matroid intersection proble
...(truncated)
````


#theorem[
  3-SATISFIABILITY polynomial-time reduces to MULTIPLE CHOICE BRANCHING.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with variables x_1, ..., x_n and clauses C_1, ..., C_p (each clause having exactly 3 literals), construct a MULTIPLE CHOICE BRANCHING instance as follows:

1. **Variable gadgets:** For each variable x_i, create a pair of arcs representing the true and false assignments. These two arcs form a partition group A_i (|A_i| = 2). The "at most one arc from each A_i" constraint forces exactly one truth assignment per variable.

2. **Clause gadgets:** For each clause C_j = (l_1 OR l_2 OR l_3), create a vertex v_j (clause vertex). For each literal l_k in C_j, add an arc from the corresponding variable gadget vertex to v_j. The in-degree constraint ("no two arcs enter the same vertex") interacts with the variable arc choices.

3. **Graph structure:** Create a directed graph where:
   - There is a root vertex r.
   - For each variable x_i, there are vertices representing the positive and negative literal states, with arcs from the root to these vertices.
   - Clause vertices receive arcs from literal vertices corresponding to their literals.
   - Additional arcs connect the structure to ensure the branching (acyclicity) property encodes the dependency structure.

4. **Weights:** Assign weights to arcs such that selecting arcs corresponding to a satisfying assignment yields total weight >= K. Arcs entering clause vertices have weight 1, and K is set to p (the number of clauses), so all clauses must be "reached" by the branching.

5. **Partition groups:** A_1 through A_n correspond to variable choices (true/false arcs). Additional partition groups may encode auxiliary structural constraints.

**Key invariant:** The branching structure (acyclic, in-degree at most 1) enforces that the selected arcs form a forest of in-arborescences. Combined with the partition constraint (one arc per variable group), this forces a consistent truth assignment. The weight threshold K = p ensures every clause vertex is reached by at least one literal arc, corresponding to clause satisfaction.
````


=== Overhead

````


**Symbols:**
- n = number of variables in the 3SAT instance
- p = number of clauses (= `num_clauses`)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | `O(n + p)` (variable, literal, and clause vertices plus root) |
| `num_arcs` | `O(n + 3*p)` (2 arcs per variable gadget + 3 arcs per clause for literals) |
| `num_partition_groups` (m) | `n` (one group per variable, plus possibly auxiliary groups) |
| `threshold` (K) | `p` (number of clauses) |

**Derivation:** Each variable contributes O(1) vertices and 2 arcs (for true/false). Each clause contributes 1 vertex and 3 incoming arcs (one per literal). The total is linear in the formula size.
````


=== Correctness

````

- Closed-loop test: reduce a small 3SAT instance to MULTIPLE CHOICE BRANCHING, solve the target with BruteForce (enumerate branching subsets respecting partition constraints), extract the variable assignments from the selected partition group arcs, verify the extracted assignment satisfies all clauses of the original 3SAT formula.
- Negative test: use an unsatisfiable 3SAT formula (e.g., all 8 clauses on 3 variables forming a contradiction), verify the target MCB instance has no branching meeting the weight threshold.
- Structural checks: verify that the constructed graph has the correct number of vertices, arcs, and partition groups; verify arc weights sum correctly.
````


=== Example

````


**Source instance (3SAT / KSatisfiability with k=3):**
Variables: x_1, x_2, x_3, x_4
Clauses (6 clauses):
- C_1 = (x_1 OR x_2 OR NOT x_3)
- C_2 = (NOT x_1 OR x_3 OR x_4)
- C_3 = (x_2 OR NOT x_3 OR NOT x_4)
- C_4 = (NOT x_1 OR NOT x_2 OR x_4)
- C_5 = (x_1 OR x_3 OR NOT x_4)
- C_6 = (NOT x_2 OR x_3 OR x_4)

Satisfying assignment: x_1 = T, x_2 = T, x_3 = T, x_4 = T
- C_1: x_1=T -> satisfied
- C_2: x_3=T -> satisfied
- C_3: NOT x_4=F, but x_2=T -> satisfied
- C_4: x_4=T -> satisfied
- C_5: x_1=T -> satisfied
- C_6: x_3=T -> satisfied

**Constructed target instance (MultipleChoiceBranching):**
Directed graph with vertices: root r, literal vertices {p1, n1, p2, n2, p3, n3, p4, n4}, clause vertices {c1, c2, c3, c4, c5, c6}.
Total: 1 + 8 + 6 = 15 vertices.

Arcs (with partition groups):
- Group A_1 (variable x_1): {r -> p1 (w=1), r -> n1 (w=1)} -- choose true or false for x_1
- Group A_2 (variable x_2): {r -> p2 (w=1), r -> n2 (w=1)}
- Group A_3 (variable x_3): {r -> p3 (w=1), r -> n3 (w=1)}
- Group A_4 (variable x_4): {r -> p4 (w=1), r -> n4 (w=1)}

Clause arcs (each in its own singleton group or ungrouped):
- p1 -> c1 (w=1), p2 -> c1 (w=1), n3 -> c1 (w=1) [for C_1]
- n1 -> c2 (w=1), p3 -> c2 (w=1), p4 -> c2 (w=1) [for C_2]
- p2 -> c3 (w=1), n3 -> c3 (w=1), n4 -> c3 (w=1) [for C_3]
- n1 -> c4 (w=1), n2 -> c4 (w=1), p4 -> c4 (w=1) [for C_4]
- p1 -> c5 (w=1), p3 -> c5 (w=1), n4 -> c5 (w=1) [for C_5]
- n2 -> c6 (w=1), p3 -> c6 (w=1), p4 -> c6 (w=1) [for C_6]

K = 6 + 4 = 10 (must select enough arcs to cover all clauses plus variable assignments).

**Solution mapping:**
- Select variable arcs: r->p1 (x_1=T), r->p2 (x_2=T), r->p3 (x_3=T), r->p4 (x_4=T) from groups A_1 through A_4.
- Select clause arcs (one entering each clause vertex, respecting in-degree 1):
  - p1 -> c1 (C_1 satisfied by x_1)
  - p3 -> c2 (C_2 satisfied by x_3)
  - p2 -> c3 (C_3 satisfied by x_2)
  - p4 -> c4 (C_4 satisfied by x_4)
  - p1 -> c5 (C_5 satisfied by x_1) -- but p1 already used for c1! In-degree
...(truncated)
````


#pagebreak()


== 3-SATISFIABILITY $arrow.r$ ACYCLIC PARTITION #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#247)]


=== Reference

````
> [ND15] ACYCLIC PARTITION
> INSTANCE: Directed graph G=(V,A), positive integer K.
> QUESTION: Can V be partitioned into K disjoint sets V_1,...,V_K such that the subgraph of G induced by each V_i is acyclic?
> Reference: [Garey and Johnson, 1979]. Transformation from 3SAT.
> Comment: NP-complete even for K=2.
````


#theorem[
  3-SATISFIABILITY polynomial-time reduces to ACYCLIC PARTITION.
]


=== Construction

````


**Summary:**
Given a KSatisfiability instance with n variables U = {u_1, ..., u_n} and m clauses C = {c_1, ..., c_m}, construct an AcyclicPartition instance (G = (V, A), K = 2) as follows:

1. **Variable gadgets:** For each variable u_i, create a directed cycle of length 3 on vertices {v_i, v_i', v_i''}. The arcs are (v_i -> v_i'), (v_i' -> v_i''), (v_i'' -> v_i). In any partition of V into two sets where each induced subgraph is acyclic, at least one arc of this 3-cycle must cross between the two sets -- meaning at least one vertex from each 3-cycle must be in a different partition set. This encodes the binary truth assignment: if v_i is in V_1, interpret u_i = True; if v_i is in V_2, interpret u_i = False.

2. **Clause gadgets:** For each clause c_j = (l_1 OR l_2 OR l_3) where each l_k is a literal (u_i or NOT u_i), create a directed 3-cycle on fresh clause vertices {a_j, b_j, c_j_vertex}. The arcs are (a_j -> b_j), (b_j -> c_j_vertex), (c_j_vertex -> a_j).

3. **Connection arcs (literal to clause):** For each literal l_k in clause c_j, add a pair of arcs connecting the variable gadget vertex corresponding to l_k to the clause gadget. Specifically:
   - If l_k = u_i (positive literal): add arcs (v_i -> a_j) and (a_j -> v_i) creating a 2-cycle that forces v_i and a_j into different partition sets, or alternatively add directed paths that propagate the partition assignment.
   - If l_k = NOT u_i (negated literal): the connection is made to the complementary vertex in the variable gadget.

   The connection structure ensures that if all three literals of a clause are false (i.e., all corresponding variable vertices are on the same side as the clause gadget), the clause gadget together with the connections forms a directed cycle entirely within one partition set, violating the acyclicity constraint.

4. **Partition parameter:** K = 2.

5. **Solution extraction:** Given a valid 2-partition (V_1, V_2) where both induced subgraphs are acyclic, read off the truth assignment from which partition set each variable vertex v_i belongs to. The acyclicity constraint on the clause gadgets guarantees that each clause has at least one satisfied literal.

**Note:** The GJ entry references this as a transformation from 3SAT (or equivalently X3C in some printings). The key insight is that directed cycles of length 3 within each partition set are forbidden, so the partition must "break" every 3-cycle by placing at least one vertex on each side. The clause gadgets are designed so that a clause is satisfied if and only if its 3-cycle can be broken by the partition implied by the truth assignment.
````


=== Overhead

````


**Symbols:**
- n = `num_vars` of source 3SAT instance (number of variables)
- m = `num_clauses` of source 3SAT instance (number of clauses)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_vertices` | `3 * num_vars + 3 * num_clauses` |
| `num_arcs` | `3 * num_vars + 3 * num_clauses + 6 * num_clauses` |

**Derivation:**
- Vertices: 3 per variable gadget (3-cycle) + 3 per clause gadget (3-cycle) = 3n + 3m
- Arcs: 3 per variable cycle + 3 per clause cycle + 2 connection arcs per literal (3 literals per clause, so 6 per clause) = 3n + 3m + 6m = 3n + 9m
````


=== Correctness

````


- Closed-loop test: reduce a KSatisfiability instance to AcyclicPartition, solve target with BruteForce (enumerate all 2-partitions, check acyclicity of each induced subgraph), extract truth assignment from partition, verify it satisfies all clauses
- Test with both satisfiable and unsatisfiable 3SAT instances to verify bidirectional correctness
- Verify that for K=2, the constructed graph has a valid acyclic 2-partition iff the 3SAT instance is satisfiable
- Check vertex and arc counts match the overhead formulas
````


=== Example

````


**Source instance (KSatisfiability):**
3 variables: u_1, u_2, u_3 (n = 3)
2 clauses (m = 2):
- c_1 = (u_1 OR u_2 OR NOT u_3)
- c_2 = (NOT u_1 OR u_2 OR u_3)

**Constructed target instance (AcyclicPartition):**

Vertices (3n + 3m = 9 + 6 = 15 total):
- Variable gadget for u_1: {v_1, v_1', v_1''} with cycle (v_1 -> v_1' -> v_1'' -> v_1)
- Variable gadget for u_2: {v_2, v_2', v_2''} with cycle (v_2 -> v_2' -> v_2'' -> v_2)
- Variable gadget for u_3: {v_3, v_3', v_3''} with cycle (v_3 -> v_3' -> v_3'' -> v_3)
- Clause gadget for c_1: {a_1, b_1, d_1} with cycle (a_1 -> b_1 -> d_1 -> a_1)
- Clause gadget for c_2: {a_2, b_2, d_2} with cycle (a_2 -> b_2 -> d_2 -> a_2)

Connection arcs (linking literals to clause gadgets):
- c_1 literal u_1 (positive): arcs connecting v_1 to clause-1 gadget
- c_1 literal u_2 (positive): arcs connecting v_2 to clause-1 gadget
- c_1 literal NOT u_3 (negative): arcs connecting v_3' to clause-1 gadget
- c_2 literal NOT u_1 (negative): arcs connecting v_1' to clause-2 gadget
- c_2 literal u_2 (positive): arcs connecting v_2 to clause-2 gadget
- c_2 literal u_3 (positive): arcs connecting v_3 to clause-2 gadget

Partition parameter: K = 2

**Solution mapping:**
- Satisfying assignment: u_1 = True, u_2 = True, u_3 = True
- Partition V_1 (True side): {v_1, v_2, v_3} plus clause vertices as needed
- Partition V_2 (False side): {v_1', v_1'', v_2', v_2'', v_3', v_3''} plus remaining clause vertices
- Each variable 3-cycle is split across V_1 and V_2, so no complete cycle in either induced subgraph
- Each clause has at least one true literal, so clause gadget cycles are also properly split
- Both induced subgraphs are acyclic
````


#pagebreak()


== 3-SATISFIABILITY $arrow.r$ CHINESE POSTMAN FOR MIXED GRAPHS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#260)]


=== Reference

````
> [ND25] CHINESE POSTMAN FOR MIXED GRAPHS
> INSTANCE: Mixed graph G=(V,A,E), where A is a set of directed edges and E is a set of undirected edges on V, length l(e)∈Z_0^+ for each e∈A∪E, bound B∈Z^+.
> QUESTION: Is there a cycle in G that includes each directed and undirected edge at least once, traversing directed edges only in the specified direction, and that has total length no more than B?
> Reference: [Papadimitriou, 1976b]. Transformation from 3SAT.
> Comment: Remains NP-complete even if all edge lengths are equal, G is planar, and the maximum vertex degree is 3. Can be solved in polynomial time if either A or E is empty (i.e., if G is either a directed or an undirected graph) [Edmonds and Johnson, 1973].
````


#theorem[
  3-SATISFIABILITY polynomial-time reduces to CHINESE POSTMAN FOR MIXED GRAPHS.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct a mixed graph G = (V, A, E) with unit edge/arc lengths as follows (per Papadimitriou, 1976):

1. **Variable gadgets:** For each variable x_i, construct a gadget consisting of a cycle that can be traversed in two ways — one corresponding to x_i = TRUE and the other to x_i = FALSE. The gadget uses a mix of directed arcs and undirected edges such that:
   - The undirected edges can be traversed in either direction, representing the two truth assignments.
   - The directed arcs enforce that once a direction is chosen for the undirected edges (to form an Euler tour through the gadget), it must be consistent throughout the entire variable gadget.
   - Each variable gadget has "ports" — one for each occurrence of x_i or ¬x_i in the clauses.

2. **Clause gadgets:** For each clause C_j = (l_{j1} ∨ l_{j2} ∨ l_{j3}), construct a small subgraph that is connected to the three variable gadgets corresponding to the literals l_{j1}, l_{j2}, l_{j3}. The clause gadget is designed so that:
   - It can be traversed at minimum cost if and only if at least one of the three connected variable gadgets is set to the truth value that satisfies the literal.
   - If none of the three literals is satisfied, the clause gadget requires at least one extra edge traversal (increasing the total cost beyond the bound).

3. **Connections:** The variable gadgets and clause gadgets are connected via edges at the "ports." The direction chosen for traversing the variable gadget's undirected edges determines which literal connections can be used for "free" (without extra traversals).

4. **Edge/arc lengths:** All edges and arcs have length 1 (unit lengths). The construction works even in this restricted setting.

5. **Bound B:** Set B equal to the total number of arcs and edges in the constructed graph (i.e., the minimum possible traversal cost if the graph were Eulerian or could be made Eulerian with no extra traversals). The mixed graph is constructed so that a postman tour of cost exactly B exists if and only if the 3SAT formula is satisfiable.

6. **Correctness:**
   - **(Forward):** If the 3SAT instance is satisfiable, set each variable gadget's traversal direction according to the satisfying assignment. For each clause, at least one literal is satisfied, allowing the clause gadget to be traversed without extra cost. The total traversal cost equals B.
   - **(Reverse):** If a postman tour of cost ≤ B exists, the traversal directions of the variable gadgets encode a consistent truth assignment (due to the directed arcs enforcing consistency). Since the cost is at most B, no clause gadget requires extra traversals, meaning each clause has at least one satisfied literal.

**Key invariant:** The interplay between directed arcs (enforcing consistency of truth assignment) and undirected edges (allowing choice of traversal direction) encodes the 3SAT structure. The bound B is tight: it equals the minimum possible tour length when all clauses are satisfied.

**Construction size:** The mixed graph has O(n + m) vertices and O(n + m) edges/arcs (polynomial in the input size).
````


=== Overhead

````


**Symbols:**
- n = `num_variables` of source 3SAT instance
- m = `num_clauses` of source 3SAT instance
- L = total number of literal occurrences across all clauses (≤ 3m)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_vertices` | O(n + m) — linear in the formula size |
| `num_arcs` | O(L + n) — arcs in variable gadgets plus connections |
| `num_edges` | O(L + n) — undirected edges in variable and clause gadgets |
| `bound` | `num_arcs + num_edges` (unit-length case) |

**Derivation:** Each variable gadget contributes O(degree(x_i)) vertices and edges/arcs, where degree is the number of clause occurrences. Each clause gadget adds O(1) vertices and edges. The total is O(sum of degrees + m) = O(L + m) = O(L) since L ≥ m. With unit lengths, B = |A| + |E| (traverse each exactly once if possible).

**Note:** The exact constants depend on the specific gadget design from Papadimitriou (1976). The construction in the original paper achieves planarity and max degree 3, which constrains the gadget design.
````


=== Correctness

````

- Closed-loop test: reduce a small 3SAT instance to MCPP, enumerate all possible Euler tours or postman tours on the mixed graph, verify that a tour of cost ≤ B exists iff the formula is satisfiable.
- Test with a known satisfiable instance: (x_1 ∨ x_2 ∨ x_3) with the trivial satisfying assignment x_1 = TRUE. The MCPP instance should have a postman tour of cost B.
- Test with a known unsatisfiable instance: (x_1 ∨ x_2) ∧ (¬x_1 ∨ ¬x_2) ∧ (x_1 ∨ ¬x_2) ∧ (¬x_1 ∨ x_2) — unsatisfiable (requires x_1 = x_2 = TRUE and x_1 = x_2 = FALSE simultaneously). Pad to 3SAT and verify no tour of cost ≤ B exists.
- Verify graph properties: planarity, max degree 3 (if using the restricted construction), unit lengths.
````


=== Example

````


**Source instance (3SAT):**
3 variables {x_1, x_2, x_3} and 3 clauses:
- C_1 = (x_1 ∨ ¬x_2 ∨ x_3)
- C_2 = (¬x_1 ∨ x_2 ∨ ¬x_3)
- C_3 = (x_1 ∨ x_2 ∨ x_3)
- Satisfying assignment: x_1 = TRUE, x_2 = TRUE, x_3 = TRUE (satisfies C_1 via x_1, C_2 via x_2, C_3 via all three)

**Constructed target instance (ChinesePostmanForMixedGraphs) — schematic:**
Mixed graph G = (V, A, E) with unit lengths:

*Variable gadgets (schematic for x_1 with 2 occurrences as positive literal, 1 as negative):*
- Vertices: v_{1,1}, v_{1,2}, v_{1,3}, v_{1,4}, v_{1,5}, v_{1,6}
- Arcs (directed): (v_{1,1} → v_{1,2}), (v_{1,3} → v_{1,4}), (v_{1,5} → v_{1,6}) — enforce consistency
- Edges (undirected): {v_{1,2}, v_{1,3}}, {v_{1,4}, v_{1,5}}, {v_{1,6}, v_{1,1}} — allow choice of direction
- Traversing undirected edges "clockwise" encodes x_1 = TRUE; "counterclockwise" encodes x_1 = FALSE.
- Port vertices connect to clause gadgets: v_{1,2} links to C_1 (positive), v_{1,4} links to C_3 (positive), v_{1,6} links to C_2 (negative).

*Clause gadgets (schematic for C_1 = (x_1 ∨ ¬x_2 ∨ x_3)):*
- Small subgraph with 3 connection vertices, one per literal port.
- If at least one literal's variable gadget is traversed in the "satisfying" direction, the clause gadget can be Euler-toured at base cost. Otherwise, an extra traversal (cost +1) is forced.

*Total construction:*
- Approximately 6×3 = 18 vertices for variable gadgets + 3×O(1) vertices for clause gadgets ≈ 24 vertices
- Approximately 9 arcs + 9 edges for variable gadgets + clause connections ≈ 30 arcs/edges total
- Bound B = 30 (one traversal per arc/edge)

**Solution mapping:**
- Satisfying assignment: x_1 = T, x_2 = T, x_3 = T
- Variable gadget x_1: traverse undirected edges clockwise → encodes TRUE
- Variable gadget x_2: traverse undirected edges clockwise → encodes TRUE
- Variable gadget x_3: traverse undirected edges clockwise → encodes TRUE
- Each clause gadget has at least one satisfied literal → no extra traversals needed
- Postman tour cost = B
...(truncated)
````


#pagebreak()


= 3SAT


== 3SAT $arrow.r$ PATH CONSTRAINED NETWORK FLOW #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#364)]


=== Reference

````
> [ND34] PATH CONSTRAINED NETWORK FLOW
> INSTANCE: Directed graph G=(V,A), specified vertices s and t, a capacity c(a)∈Z^+ for each a∈A, a collection P of directed paths in G, and a requirement R∈Z^+.
> QUESTION: Is there a function g: P->Z_0^+ such that if f: A->Z_0^+ is the flow function defined by f(a)=Sum_{p∈P(a)} g(p), where P(a)⊆P is the set of all paths in P containing the arc a, then f is such that
> (1) f(a) (2) for each v∈V-{s,t}, flow is conserved at v, and
> (3) the net flow into t is at least R?
> Reference: [Promel, 1978]. Transformation from 3SAT.
> Comment: Remains NP-complete even if all c(a)=1. The corresponding problem with non-integral flows is equivalent to LINEAR PROGRAMMING, but the question of whether the best rational flow fails to exceed the best integral flow is NP-complete.
````


#theorem[
  3SAT polynomial-time reduces to PATH CONSTRAINED NETWORK FLOW.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct a PATH CONSTRAINED NETWORK FLOW instance as follows:

1. **Variable gadgets:** For each variable x_i, create a "variable arc" e_i in the graph. Create two paths: p_{x_i} (representing x_i = true) and p_{~x_i} (representing x_i = false). Both paths traverse arc e_i, ensuring that at most one of them can carry flow (since arc e_i has capacity 1).

2. **Clause gadgets:** For each clause C_j (containing three literals l_{j,1}, l_{j,2}, l_{j,3}), create a "clause arc" e_{n+j}. Also create three arcs c_{j,1}, c_{j,2}, c_{j,3}, one for each literal position in the clause. Create three paths p~_{j,1}, p~_{j,2}, p~_{j,3} where p~_{j,k} traverses both arc e_{n+j} and arc c_{j,k}.

3. **Linking literals to variables:** Arc c_{j,k} is also traversed by the variable path p_{x_i} (or p_{~x_i}) if literal l_{j,k} is x_i (or ~x_i, respectively). This creates a conflict: if variable x_i is set to true (p_{x_i} carries flow), then the clause path p~_{j,k} corresponding to literal ~x_i cannot carry flow through the shared arc.

4. **Capacities:** Set all arc capacities to 1.

5. **Requirement:** Set R such that we need flow from all variable gadgets (n units for variable selection) plus at least one satisfied literal per clause (m units from clause satisfaction), giving R = n + m.

6. **Correctness (forward):** A satisfying assignment selects one path per variable (n units of flow). For each clause, at least one literal is true, so the corresponding clause path can carry flow without conflicting with the variable paths. Total flow >= n + m = R.

7. **Correctness (reverse):** If a feasible flow achieving R = n + m exists, the variable arcs force exactly one truth value per variable (binary choice), and the clause arcs force each clause to have at least one satisfied literal.

**Key invariant:** Shared arcs between variable paths and clause paths enforce consistency between variable assignments and clause satisfaction. Unit capacities enforce binary choices.

**Time complexity of reduction:** O(n + m) for graph construction (polynomial in the 3SAT formula size).
````


=== Overhead

````


**Symbols:**
- n = number of variables in 3SAT instance
- m = number of clauses in 3SAT instance

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | O(n + m) |
| `num_arcs` | `n + m + 3 * m` = `n + 4 * m` |
| `num_paths` | `2 * n + 3 * m` |
| `requirement` (R) | `n + m` |

**Derivation:** The graph has O(n + m) vertices. There are n variable arcs, m clause arcs, and 3m literal arcs, for n + 4m arcs total. The path collection has 2n variable paths and 3m clause-literal paths. All capacities are 1.
````


=== Correctness

````


- Closed-loop test: reduce a 3SAT instance to PathConstrainedNetworkFlow, solve target with BruteForce (enumerate path flow assignments), extract solution, verify on source
- Test with known YES instance: a satisfiable 3SAT formula
- Test with known NO instance: an unsatisfiable 3SAT formula (e.g., a small unsatisfiable core)
- Compare with known results from literature
````


=== Example

````


**Source instance (3SAT):**
Variables: x_1, x_2, x_3, x_4
Clauses (m = 4):
- C_1 = (x_1 v x_2 v ~x_3)
- C_2 = (~x_1 v x_3 v x_4)
- C_3 = (x_2 v ~x_3 v ~x_4)
- C_4 = (~x_1 v ~x_2 v x_4)

Satisfying assignment: x_1 = T, x_2 = T, x_3 = F, x_4 = T
- C_1: x_1=T -> satisfied
- C_2: x_4=T -> satisfied
- C_3: ~x_3=T -> satisfied
- C_4: x_4=T -> satisfied

**Constructed target instance (PathConstrainedNetworkFlow):**
- Variable arcs: e_1, e_2, e_3, e_4 (capacity 1 each)
- Clause arcs: e_5, e_6, e_7, e_8 (capacity 1 each)
- Literal arcs: c_{1,1}, c_{1,2}, c_{1,3}, c_{2,1}, c_{2,2}, c_{2,3}, c_{3,1}, c_{3,2}, c_{3,3}, c_{4,1}, c_{4,2}, c_{4,3} (capacity 1 each)
- Variable paths (8 total): p_{x_1}, p_{~x_1}, p_{x_2}, p_{~x_2}, p_{x_3}, p_{~x_3}, p_{x_4}, p_{~x_4}
- Clause paths (12 total): 3 per clause
- R = 4 + 4 = 8

**Solution mapping:**
- Assignment x_1=T, x_2=T, x_3=F, x_4=T:
  - Select paths p_{x_1}, p_{x_2}, p_{~x_3}, p_{x_4} (flow = 1 each, 4 units)
  - For C_1: x_1 satisfies it, select clause path p~_{1,1} (1 unit)
  - For C_2: x_4 satisfies it, select clause path p~_{2,3} (1 unit)
  - For C_3: ~x_3 satisfies it, select clause path p~_{3,2} (1 unit)
  - For C_4: x_4 satisfies it, select clause path p~_{4,3} (1 unit)
  - Total flow into t = 4 + 4 = 8 = R
````


#pagebreak()


== 3SAT $arrow.r$ INTEGRAL FLOW WITH HOMOLOGOUS ARCS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#365)]


=== Reference

````
> [ND35] INTEGRAL FLOW WITH HOMOLOGOUS ARCS
> INSTANCE: Directed graph G=(V,A), specified vertices s and t, capacity c(a)∈Z^+ for each a∈A, requirement R∈Z^+, set H⊆A×A of "homologous" pairs of arcs.
> QUESTION: Is there a flow function f: A→Z_0^+ such that
> (1) f(a)≤c(a) for all a∈A,
> (2) for each v∈V−{s,t}, flow is conserved at v,
> (3) for all pairs ∈H, f(a)=f(a'), and
> (4) the net flow into t is at least R?
> Reference: [Sahni, 1974]. Transformation from 3SAT.
> Comment: Remains NP-complete if c(a)=1 for all a∈A (by modifying the construction in [Even, Itai, and Shamir, 1976]). Corresponding problem with non-integral flows is polynomially equivalent to LINEAR PROGRAMMING [Itai, 1977].
````


#theorem[
  3SAT polynomial-time reduces to INTEGRAL FLOW WITH HOMOLOGOUS ARCS.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct an INTEGRAL FLOW WITH HOMOLOGOUS ARCS instance as follows:

1. **Variable gadgets:** For each variable x_i, create a "diamond" subnetwork with two parallel paths from a node u_i to a node v_i. The upper path (arc a_i^T) represents x_i = TRUE, the lower path (arc a_i^F) represents x_i = FALSE. Set capacity 1 on each arc.

2. **Chain the variable gadgets:** Connect s -> u_1, v_1 -> u_2, ..., v_n -> t_0 in series, so that exactly one unit of flow passes through each variable gadget. The path chosen (upper or lower) encodes the truth assignment.

3. **Clause gadgets:** For each clause C_j, create an additional arc from s to t (or a small subnetwork) that requires one unit of flow. This flow must be "validated" by a literal satisfying C_j.

4. **Homologous arc pairs:** For each literal occurrence x_i in clause C_j, create a pair of homologous arcs: one arc in the variable gadget for x_i (the TRUE arc) and one arc in the clause gadget for C_j. The equal-flow constraint ensures that if the literal's truth path carries flow 1, then the clause gadget also receives flow validation. Similarly for negated literals using the FALSE arcs.

5. **Requirement:** Set R = n + m (n units for the assignment path through variable gadgets plus m units for clause satisfaction).

The 3SAT formula is satisfiable if and only if there exists an integral flow of value at least R satisfying all capacity and homologous-arc constraints.
````


=== Overhead

````


| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | O(n + m) where n = num_variables, m = num_clauses |
| `num_arcs` | O(n + m + L) where L = total literal occurrences (at most 3m) |
| `num_homologous_pairs` | O(L) = O(m) (one pair per literal occurrence) |
| `max_capacity` | 1 (unit capacities suffice) |
| `requirement` | n + m |
````


=== Correctness

````


- Closed-loop test: reduce source 3SAT instance, solve target integral flow with homologous arcs using BruteForce, extract solution, verify on source
- Compare with known results from literature
- Verify that satisfiable 3SAT instances yield flow >= R and unsatisfiable instances do not
````


=== Example

````


**Source (3SAT):**
Variables: x_1, x_2, x_3
Clauses:
- C_1 = (x_1 ∨ x_2 ∨ x_3)
- C_2 = (¬x_1 ∨ ¬x_2 ∨ x_3)
- C_3 = (x_1 ∨ ¬x_2 ∨ ¬x_3)

**Constructed Target (Integral Flow with Homologous Arcs):**

Vertices: s, u_1, v_1, u_2, v_2, u_3, v_3, t, plus clause nodes c_1, c_2, c_3.

Arcs and structure:
- Variable chain: s->u_1, u_1->v_1 (TRUE arc a_1^T), u_1->v_1 (FALSE arc a_1^F), v_1->u_2, u_2->v_2 (TRUE arc a_2^T), u_2->v_2 (FALSE arc a_2^F), v_2->u_3, u_3->v_3 (TRUE arc a_3^T), u_3->v_3 (FALSE arc a_3^F), v_3->t.
- Clause arcs: For each clause C_j, an arc from s through c_j to t carrying 1 unit.
- All capacities = 1.

Homologous pairs (linking literals to clauses):
- (a_1^T, clause_1_lit1) — x_1 in C_1
- (a_2^T, clause_1_lit2) — x_2 in C_1
- (a_3^T, clause_1_lit3) — x_3 in C_1
- (a_1^F, clause_2_lit1) — ¬x_1 in C_2
- (a_2^F, clause_2_lit2) — ¬x_2 in C_2
- (a_3^T, clause_2_lit3) — x_3 in C_2
- (a_1^T, clause_3_lit1) — x_1 in C_3
- (a_2^F, clause_3_lit2) — ¬x_2 in C_3
- (a_3^F, clause_3_lit3) — ¬x_3 in C_3

Requirement R = 3 + 3 = 6.

**Solution mapping:**
Assignment x_1=TRUE, x_2=FALSE, x_3=TRUE satisfies all clauses.
- Variable path: flow goes through a_1^T, a_2^F, a_3^T (each with flow 1).
- C_1 satisfied by x_1=TRUE: clause_1_lit1 gets flow 1 (homologous with a_1^T).
- C_2 satisfied by ¬x_2 (x_2=FALSE): clause_2_lit2 gets flow 1 (homologous with a_2^F).
- C_3 satisfied by x_1=TRUE: clause_3_lit1 gets flow 1 (homologous with a_1^T).
- Total flow = 3 (variable chain) + 3 (clauses) = 6 = R.
````


#pagebreak()


== 3SAT $arrow.r$ DISJOINT CONNECTING PATHS #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#370)]


=== Reference

````
> [ND40] DISJOINT CONNECTING PATHS
> INSTANCE: Graph G=(V,E), collection of disjoint vertex pairs (s_1,t_1),(s_2,t_2),…,(s_k,t_k).
> QUESTION: Does G contain k mutually vertex-disjoint paths, one connecting s_i and t_i for each i, 1≤i≤k?
> Reference: [Knuth, 1974c], [Karp, 1975a], [Lynch, 1974]. Transformation from 3SAT.
````


#theorem[
  3SAT polynomial-time reduces to DISJOINT CONNECTING PATHS.
]


=== Construction

````
**Input:** A 3SAT formula with n variables x_1, ..., x_n and m clauses c_1, ..., c_m (each clause contains exactly 3 literals).

Let n = `num_vars` and m = `num_clauses` of the source KSatisfiability instance.

### Step 1 — Variable gadgets

For each variable x_i (i = 1, ..., n), create a chain of 2m vertices:

  v_{i,1}, v_{i,2}, ..., v_{i,2m}

Add chain edges (v_{i,j}, v_{i,j+1}) for j = 1, ..., 2m−1.

Register terminal pair (s_i, t_i) = (v_{i,1}, v_{i,2m}).

This gives n chains, each with 2m vertices and 2m−1 edges.

### Step 2 — Clause gadgets

For each clause c_j (j = 1, ..., m), create 8 new vertices:
- Two terminal vertices: s'_j and t'_j
- Six intermediate vertices: p_{j,1}, q_{j,1}, p_{j,2}, q_{j,2}, p_{j,3}, q_{j,3}

Add clause chain edges forming the path:

  s'_j — p_{j,1} — q_{j,1} — p_{j,2} — q_{j,2} — p_{j,3} — q_{j,3} — t'_j

That is, edges: (s'_j, p_{j,1}), (p_{j,1}, q_{j,1}), (q_{j,1}, p_{j,2}), (p_{j,2}, q_{j,2}), (q_{j,2}, p_{j,3}), (p_{j,3}, q_{j,3}), (q_{j,3}, t'_j) — seven edges per clause.

Register terminal pair (s'_j, t'_j).

### Step 3 — Interconnection edges

For each clause c_j and each literal position r = 1, 2, 3:

Let the r-th literal of c_j involve variable x_i.

- **If the literal is positive (x_i):** add edges (v_{i,2j−1}, p_{j,r}) and (q_{j,r}, v_{i,2j}).
- **If the literal is negated (¬x_i):** add edges (v_{i,2j−1}, q_{j,r}) and (p_{j,r}, v_{i,2j}).

This adds exactly 2 × 3 = 6 interconnection edges per clause.

### Step 4 — Output

Return the constructed graph G and the n + m terminal pairs.

### Correctness sketch

Each variable terminal pair (s_i, t_i) must be connected by a path through the chain v_{i,1}, ..., v_{i,2m}. At each clause slot j, the variable path can either traverse the direct chain edge (v_{i,2j−1}, v_{i,2j}) or detour through the clause gadget vertices (p_{j,r}, q_{j,r}) via the interconnection edges. The choice of detour at all slots for a single variable is consistent and encodes a truth assignment: if x_i's path detours through clause c_j's gadget at the "positive" side, this corresponds to x_i = True.

Each clause terminal pair (s'_j, t'_j) must route through the clause chain. When a variable path detours through one of the (p_{j,r}, q_{j,r}) pairs, those vertices become unavailable for the clause path. The clause path can still succeed if at least one literal position r has its (p_{j,r}, q_{j,r}) pair free — corresponding to a satisfying literal.

Thus n + m vertex-disjoint paths exist if and only if the 3SAT formula is satisfiable.

### Solution extraction

Given n + m vertex-disjoint paths in the target graph, read off the truth assignment from the variable paths:
- For each variable x_i, examine the variable path from s_i = v_{i,1} to t_i = v_{i,2m}.
- At clause slot j, if the path traverses the direct chain edge (v_{i,2j−1}, v_{i,2j}), the variable path did NOT detour through clause c_j.
- If the path instead visits clause gadget vertices at a positive-literal position, set x_i = True; if at a negated-literal position, set x_i = False. Consistency across all slots gives a satisfying assignment.
- For each variable i, output: config[i] = 1 (True) if x_i = True, 0 (False) otherwise.
````


=== Overhead

````
**Symbols:**
- n = `num_vars` of source KSatisfiability instance
- m = `num_clauses` of source KSatisfiability instance

| Target metric | Formula | Derivation |
|---------------|---------|------------|
| `num_vertices` | `2 * num_vars * num_clauses + 8 * num_clauses` | n variable chains × 2m vertices + m clause gadgets × 8 vertices each |
| `num_edges` | `num_vars * (2 * num_clauses - 1) + 13 * num_clauses` | n chains × (2m−1) chain edges + m clauses × (7 chain + 6 interconnection) edges |
| `num_pairs` | `num_vars + num_clauses` | n variable pairs + m clause pairs |
````


=== Correctness

````
- **Closed-loop test:** Reduce a KSatisfiability instance to DisjointConnectingPaths, solve the target with BruteForce, extract the solution back, and verify the truth assignment satisfies all clauses of the source formula.
- **Negative test:** Reduce an unsatisfiable 3SAT instance and confirm the target has no solution (BruteForce returns `Or(false)`).
- **Overhead verification:** Construct a source instance with known n and m, run the reduction, and check that the target's `num_vertices()`, `num_edges()`, and `num_pairs()` match the formulas above.
````


=== Example

````
**Source instance (3SAT):**

3 variables: x_1, x_2, x_3 (n = 3, m = 2)

- c_1 = (x_1 ∨ ¬x_2 ∨ x_3)
- c_2 = (¬x_1 ∨ x_2 ∨ ¬x_3)

**Step 1 — Variable chains** (2m = 4 vertices each, 3 chain edges each):

| Variable | Vertices | Chain edges | Terminal pair |
|----------|----------|-------------|--------------|
| x_1 | v_{1,1}, v_{1,2}, v_{1,3}, v_{1,4} | (v_{1,1},v_{1,2}), (v_{1,2},v_{1,3}), (v_{1,3},v_{1,4}) | (v_{1,1}, v_{1,4}) |
| x_2 | v_{2,1}, v_{2,2}, v_{2,3}, v_{2,4} | (v_{2,1},v_{2,2}), (v_{2,2},v_{2,3}), (v_{2,3},v_{2,4}) | (v_{2,1}, v_{2,4}) |
| x_3 | v_{3,1}, v_{3,2}, v_{3,3}, v_{3,4} | (v_{3,1},v_{3,2}), (v_{3,2},v_{3,3}), (v_{3,3},v_{3,4}) | (v_{3,1}, v_{3,4}) |

**Step 2 — Clause gadgets** (8 vertices each, 7 chain edges each):

| Clause | Terminal vertices | Intermediate vertices | Clause chain |
|--------|-------------------|-----------------------|--------------|
| c_1 | s'_1, t'_1 | p_{1,1}, q_{1,1}, p_{1,2}, q_{1,2}, p_{1,3}, q_{1,3} | s'_1 — p_{1,1} — q_{1,1} — p_{1,2} — q_{1,2} — p_{1,3} — q_{1,3} — t'_1 |
| c_2 | s'_2, t'_2 | p_{2,1}, q_{2,1}, p_{2,2}, q_{2,2}, p_{2,3}, q_{2,3} | s'_2 — p_{2,1} — q_{2,1} — p_{2,2} — q_{2,2} — p_{2,3} — q_{2,3} — t'_2 |

**Step 3 — Interconnection edges:**

Clause c_1 = (x_1 ∨ ¬x_2 ∨ x_3), j = 1:
- r=1, literal x_1 (positive, i=1): edges **(v_{1,1}, p_{1,1})** and **(q_{1,1}, v_{1,2})**
- r=2, literal ¬x_2 (negated, i=2): edges **(v_{2,1}, q_{1,2})** and **(p_{1,2}, v_{2,2})**
- r=3, literal x_3 (positive, i=3): edges **(v_{3,1}, p_{1,3})** and **(q_{1,3}, v_{3,2})**

Clause c_2 = (¬x_1 ∨ x_2 ∨ ¬x_3), j = 2:
- r=1, literal ¬x_1 (negated, i=1): edges **(v_{1,3}, q_{2,1})** and **(p_{2,1}, v_{1,4})**
- r=2, literal x_2 (positive, i=2): edges **(v_{2,3}, p_{2,2})** and **(q_{2,2}, v_{2,4})**
- r=3, literal ¬x_3 (negated, i=3): edges **(v_{3,3}, q_{2,3})** and **(p_{2,3}, v_{3,4})**

**Target instance summary:**
- Vertices: 2 × 3 × 2 + 8 × 2 = 12 + 16 = **28**
- Edges: 3 × (2 × 2 − 1) + 13 × 2 = 9 + 26 = **35**
- Termi
...(truncated)
````


#pagebreak()


== 3SAT $arrow.r$ MAXIMUM LENGTH-BOUNDED DISJOINT PATHS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#371)]


=== Reference

````
> [ND41] MAXIMUM LENGTH-BOUNDED DISJOINT PATHS
> INSTANCE: Graph G=(V,E), specified vertices s and t, positive integers J,K≤|V|.
> QUESTION: Does G contain J or more mutually vertex-disjoint paths from s to t, none involving more than K edges?
> Reference: [Itai, Perl, and Shiloach, 1977]. Transformation from 3SAT.
> Comment: Remains NP-complete for all fixed K≥5. Solvable in polynomial time for K≤4. Problem where paths need only be edge-disjoint is NP-complete for all fixed K≥5, polynomially solvable for K≤3, and open for K=4. The same results hold if G is a directed graph and the paths must be directed paths. The problem of finding the maximum number of disjoint paths from s to t, under no length constraint, is solvable in polynomial time by standard network flow techniques in both the vertex-disjoint and edge-disjoint cases.
````


#theorem[
  3SAT polynomial-time reduces to MAXIMUM LENGTH-BOUNDED DISJOINT PATHS.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with n variables U = {u_1, ..., u_n} and m clauses C = {c_1, ..., c_m}, construct a MAXIMUM LENGTH-BOUNDED DISJOINT PATHS instance (G, s, t, J, K) as follows:

1. **Source and sink:** Create two distinguished vertices s (source) and t (sink).

2. **Variable gadgets:** For each variable u_i, create two parallel paths of length K from s to t — a "true path" and a "false path." Each path passes through K-1 intermediate vertices. The path chosen for u_i encodes whether u_i is set to True or False. The two paths share only the endpoints s and t (plus possibly some clause-junction vertices).

3. **Clause enforcement:** For each clause c_j = (l_1 ∨ l_2 ∨ l_3), create an additional path structure connecting s to t that can be completed as a length-K path only if at least one of its literals is satisfied. This is done by inserting "crossing vertices" at specific positions along the variable paths. The clause path borrows a vertex from a satisfied literal's variable path, forcing the variable path to detour and thus become longer than K if the literal is false.

4. **Length bound:** Set K to a specific value (K ≥ 5 for the NP-complete case) that is determined by the construction to ensure that exactly one of the two variable paths (true or false) can stay within length K, while the other is forced to exceed K if a clause borrows its vertex.

5. **Path count:** Set J = n + m (one path per variable plus one per clause). The n variable paths encode the truth assignment; the m clause paths verify that each clause is satisfied.

6. **Correctness:** J vertex-disjoint s-t paths of length ≤ K exist if and only if the 3SAT formula is satisfiable. The length constraint K forces consistency in the truth assignment, and the clause paths can only be routed when at least one literal per clause is true.

7. **Solution extraction:** Given J vertex-disjoint paths of length ≤ K, for each variable u_i, check whether the "true path" or "false path" was used; set u_i accordingly.
````


=== Overhead

````


**Symbols:**
- n = `num_vars` of source 3SAT instance (number of variables)
- m = `num_clauses` of source 3SAT instance (number of clauses)
- K = length bound (fixed constant ≥ 5 in the construction)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | O(K * (n + m)) — O(n + m) paths each of length O(K) |
| `num_edges` | O(K * (n + m)) — edges along paths plus crossing edges |
| `num_paths_required` (J) | `num_vars + num_clauses` |
| `length_bound` (K) | O(1) — fixed constant ≥ 5 |

**Derivation:**
- Each of the n variable gadgets has 2 paths of O(K) vertices = O(Kn) vertices
- Each of the m clause gadgets has O(K) vertices = O(Km) vertices
- Plus 2 vertices for s and t
- Total vertices: O(K(n + m)) + 2
````


=== Correctness

````


- Closed-loop test: reduce KSatisfiability instance to MaximumLengthBoundedDisjointPaths, solve target with BruteForce, extract solution, verify truth assignment satisfies all clauses on source
- Compare with known results from literature
- Test with both satisfiable and unsatisfiable 3SAT instances
- Verify that the length bound K is respected by all paths in the solution
````


=== Example

````


**Source instance (3SAT):**
3 variables: u_1, u_2, u_3 (n = 3)
2 clauses (m = 2):
- c_1 = (u_1 ∨ u_2 ∨ ¬u_3)
- c_2 = (¬u_1 ∨ ¬u_2 ∨ u_3)

**Constructed target instance (MAXIMUM LENGTH-BOUNDED DISJOINT PATHS):**

Parameters: J = n + m = 5 paths required, K = 5 (length bound).

Graph structure:
- Vertices s and t (source and sink)
- For each variable u_i (i = 1,2,3): a true-path and false-path from s to t, each of length 5
  - True path for u_1: s — a_{1,1} — a_{1,2} — a_{1,3} — a_{1,4} — t
  - False path for u_1: s — b_{1,1} — b_{1,2} — b_{1,3} — b_{1,4} — t
  - (Similarly for u_2 and u_3)
- For each clause c_j (j = 1,2): a clause path from s to t that shares crossing vertices with the appropriate literal paths

**Solution mapping:**
- Satisfying assignment: u_1 = True, u_2 = True, u_3 = True
  - c_1: u_1 = True ✓
  - c_2: u_3 = True ✓
- Variable u_1 uses true-path, u_2 uses true-path, u_3 uses true-path
- Clause c_1 borrows a vertex from u_1's false-path (available since u_1 takes true-path)
- Clause c_2 borrows a vertex from u_3's false-path (available since u_3 takes true-path)
- All 5 paths are vertex-disjoint and each has length ≤ 5 ✓
````


#pagebreak()


== 3SAT $arrow.r$ Rectilinear Picture Compression #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#458)]


=== Reference

````
> [SR25] RECTILINEAR PICTURE COMPRESSION
> INSTANCE: An n×n matrix M of 0's and 1's, and a positive integer K.
> QUESTION: Is there a collection of K or fewer rectangles that covers precisely those entries in M that are 1's, i.e., is there a sequence of quadruples (a_i, b_i, c_i, d_i), 1  Reference: [Masek, 1978]. Transformation from 3SAT.
````


#theorem[
  3SAT polynomial-time reduces to Rectilinear Picture Compression.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct a binary matrix M and budget K as follows (based on the approach described in Masek's 1978 manuscript):

1. **Variable gadgets:** For each variable x_i, construct a rectangular region in M representing the two possible truth values. The region contains a pattern of 1-entries that can be covered by exactly 2 rectangles in two distinct ways: one way corresponds to setting x_i = TRUE, the other to x_i = FALSE. Each variable gadget occupies a separate row band of the matrix.

2. **Clause gadgets:** For each clause C_j, construct a region that contains 1-entries arranged so that it can be covered by a single rectangle only if at least one of the literal choices from the variable gadgets "aligns" with the clause. Specifically, the clause gadget has 1-entries that extend into the variable gadget regions corresponding to the three literals in C_j. If a variable assignment satisfies a literal in C_j, the corresponding variable gadget's rectangle choice will cover part of the clause gadget; otherwise, an additional rectangle is needed.

3. **Matrix assembly:** The overall matrix M is assembled by placing variable gadgets in distinct row bands and clause gadgets in distinct column bands, with connecting 1-entries that link clauses to their literals. The matrix dimensions are polynomial in n and m.

4. **Budget:** Set K = 2n + m. Each variable requires exactly 2 rectangles (regardless of truth assignment), and each satisfied clause contributes 0 extra rectangles (its 1-entries are already covered by the variable rectangles). An unsatisfied clause would require at least 1 additional rectangle.

5. **Correctness (forward):** If the 3SAT instance is satisfiable, choose rectangle placements in each variable gadget according to the satisfying assignment. Since every clause has at least one satisfied literal, the literal's variable rectangle extends to cover the clause gadget's connecting entries. Total rectangles = 2n + m (at most) since the clause connectors are already covered.

6. **Correctness (reverse):** If K or fewer rectangles cover M, then each variable gadget uses exactly 2 rectangles (which determines a truth assignment), and each clause gadget must be covered without additional rectangles beyond the budget, meaning each clause must be satisfied by at least one literal.

**Time complexity of reduction:** O(poly(n, m)) to construct the matrix M (polynomial in the number of variables and clauses).
````


=== Overhead

````


**Symbols:**
- n = `num_variables` of source 3SAT instance (number of Boolean variables)
- m = `num_clauses` of source 3SAT instance (number of clauses)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `matrix_rows` | O(`num_variables` * `num_clauses`) |
| `matrix_cols` | O(`num_variables` * `num_clauses`) |
| `budget` | 2 * `num_variables` + `num_clauses` |

**Derivation:** The matrix dimensions are polynomial in n and m; the exact constants depend on the gadget sizes. Each variable gadget contributes a constant-height row band and each clause gadget contributes a constant-width column band, but connecting regions require additional rows/columns proportional to the number of connections. The budget is 2n (two rectangles per variable gadget) plus at most m (one rectangle per clause gadget that can be "absorbed" if the clause is satisfied).
````


=== Correctness

````


- Closed-loop test: reduce a KSatisfiability(k=3) instance to RectilinearPictureCompression, solve the target by brute-force enumeration of rectangle collections, extract solution, verify on source
- Test with a known satisfiable 3SAT instance and verify the constructed matrix can be covered with 2n + m rectangles
- Test with a known unsatisfiable 3SAT instance and verify 2n + m rectangles are insufficient
- Verify the matrix M has 1-entries only where expected (variable gadgets, clause gadgets, and connecting regions)
````


=== Example

````


**Source instance (3SAT / KSatisfiability k=3):**
Variables: x_1, x_2, x_3 (n = 3)
Clauses (m = 2):
- C_1: (x_1 v x_2 v ~x_3)
- C_2: (~x_1 v x_2 v x_3)

**Constructed target instance (RectilinearPictureCompression):**
We construct a binary matrix with variable gadgets for x_1, x_2, x_3 and clause gadgets for C_1, C_2.

Schematic layout (simplified):

---
Variable gadgets (row bands):
  x_1 band: rows 1-3    | TRUE choice: rectangles covering cols 1-4, 7-8
                         | FALSE choice: rectangles covering cols 1-2, 5-8
  x_2 band: rows 4-6    | TRUE choice: rectangles covering cols 1-4, 9-10
                         | FALSE choice: rectangles covering cols 1-2, 5-10
  x_3 band: rows 7-9    | TRUE choice: rectangles covering cols 3-6, 9-10
                         | FALSE choice: rectangles covering cols 3-4, 7-10

Clause connectors:
  C_1 connector region: cols 7-8 (x_1 TRUE), cols 9-10 (x_2 TRUE), cols 7-8 (x_3 FALSE)
  C_2 connector region: cols 5-6 (x_1 FALSE), cols 9-10 (x_2 TRUE), cols 9-10 (x_3 TRUE)
---

Budget K = 2(3) + 2 = 8

**Solution mapping:**
Consider the truth assignment: x_1 = TRUE, x_2 = TRUE, x_3 = TRUE.
- C_1: (T v T v F) = TRUE (satisfied by x_1 and x_2)
- C_2: (F v T v T) = TRUE (satisfied by x_2 and x_3)

In the matrix covering:
- x_1 TRUE choice uses 2 rectangles that extend to cover C_1's x_1-connector
- x_2 TRUE choice uses 2 rectangles that extend to cover both C_1's and C_2's x_2-connectors
- x_3 TRUE choice uses 2 rectangles that extend to cover C_2's x_3-connector
- Total: 6 variable rectangles + clause gadgets already covered = 6 + 2 = 8 = K

**Reverse mapping:**
The rectangle placement forces a unique truth assignment per variable gadget. If a clause gadget requires an extra rectangle, the budget is exceeded, proving the formula is unsatisfiable.
````


#pagebreak()


== 3SAT $arrow.r$ Consistency of Database Frequency Tables #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#468)]


=== Reference

````
> [SR35] CONSISTENCY OF DATABASE FREQUENCY TABLES
> INSTANCE: Set A of attribute names, domain set D_a for each a E A, set V of objects, collection F of frequency tables for some pairs a,b E A (where a frequency table for a,b E A is a function f_{a,b}: D_a × D_b → Z+ with the sum, over all pairs x E D_a and y E D_b, of f_{a,b}(x,y) equal to |V|), and a set K of triples (v,a,x) with v E V, a E A, and x E D_a, representing the known attribute values.
> QUESTION: Are the frequency tables in F consistent with the known attribute values in K, i.e., is there a collection of functions g_a: V → D_a, for each a E A, such that g_a(v) = x if (v,a,x) E K and such that, for each f_{a,b} E F, x E D_a, and y E D_b, the number of v E V for which g_a(v) = x and g_b(v) = y is exactly f_{a,b}(x,y)?
> Reference: [Reiss, 1977b]. Transformation from 3SAT.
> Comment: Above result implies that no polynomial time algorithm can be given for "compromising" a data base from its frequency tables by deducing prespe
...(truncated)
````


#theorem[
  3SAT polynomial-time reduces to Consistency of Database Frequency Tables.
]


=== Construction

````


**Summary:**
Given a 3SAT instance with variables x_1, ..., x_n and clauses C_1, ..., C_m (each clause having exactly 3 literals), construct a Consistency of Database Frequency Tables instance as follows:

1. **Object construction:** Create one object v_i for each variable x_i in the 3SAT formula. Thus |V| = n (the number of variables).

2. **Attribute construction for variables:** Create one attribute a_i for each variable x_i, with domain D_{a_i} = {T, F} (representing True and False). The assignment g_{a_i}(v_i) encodes the truth value of variable x_i.

3. **Attribute construction for clauses:** For each clause C_j = (l_{j1} ∨ l_{j2} ∨ l_{j3}), create an attribute b_j with domain D_{b_j} = {1, 2, 3, ..., 7} representing which of the 7 satisfying truth assignments for the 3 literals in C_j is realized. (There are 2^3 - 1 = 7 ways to satisfy a 3-literal clause.)

4. **Frequency table construction:** For each clause C_j involving variables x_{p}, x_{q}, x_{r}:
   - Create frequency tables f_{a_p, b_j}, f_{a_q, b_j}, and f_{a_r, b_j} that encode the relationship between the truth value of each variable and the satisfying assignment chosen for clause C_j.
   - The frequency table f_{a_p, b_j}(T, k) = 1 if the k-th satisfying assignment of C_j has x_p = True, and 0 otherwise (similarly for F). These tables enforce that the attribute value of object v_p (the truth value of x_p) is consistent with the satisfying assignment chosen for clause C_j.

5. **Known attribute values (K):** The set K is initially empty (no attribute values are pre-specified), or may contain specific triples to encode unit propagation constraints.

6. **Marginal consistency constraints:** Additional frequency tables between variable-attributes a_p and a_q for variables appearing together in clauses enforce that each object v_i has a unique, globally consistent truth value.

7. **Solution extraction:** The frequency tables in F are consistent with K if and only if there exists an assignment of truth values to x_1, ..., x_n that satisfies all clauses. A consistent set of functions g_a corresponds directly to a satisfying assignment.

**Key invariant:** Each object represents a Boolean variable, each variable-attribute encodes {T, F}, and the frequency tables between variable-attributes and clause-attributes ensure that every clause has at least one true literal — which is exactly the 3SAT satisfiability condition.
````


=== Overhead

````


**Symbols:**
- n = number of variables in the 3SAT instance
- m = number of clauses in the 3SAT instance

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_objects` | `num_variables` |
| `num_attributes` | `num_variables + num_clauses` |
| `num_frequency_tables` | `3 * num_clauses` |

**Derivation:**
- Objects: one per Boolean variable -> |V| = n
- Attributes: one per variable (domain {T, F}) plus one per clause (domain {1,...,7}) -> |A| = n + m
- Frequency tables: 3 tables per clause (one for each literal's variable paired with the clause attribute) -> |F| = 3m
- Domain sizes: variable attributes have |D| = 2; clause attributes have |D| <= 7
- Known values: |K| = O(n) at most (possibly empty)
````


=== Correctness

````


- Closed-loop test: reduce a 3SAT instance to a Consistency of Database Frequency Tables instance, solve the consistency problem by brute-force enumeration of all possible attribute-value assignments, extract the truth assignment, and verify it satisfies all original clauses
- Check that the number of objects, attributes, and frequency tables matches the overhead formula
- Test with a 3SAT instance that is satisfiable and verify that at least one consistent assignment exists
- Test with an unsatisfiable 3SAT instance and verify that no consistent assignment exists
- Verify that frequency table marginals sum to |V| as required by the problem definition
````


=== Example

````


**Source instance (3SAT):**
Variables: x_1, x_2, x_3, x_4, x_5, x_6
Clauses (7 clauses):
- C_1 = (x_1 ∨ x_2 ∨ x_3)
- C_2 = (¬x_1 ∨ x_4 ∨ x_5)
- C_3 = (¬x_2 ∨ ¬x_3 ∨ x_6)
- C_4 = (x_1 ∨ ¬x_4 ∨ ¬x_6)
- C_5 = (¬x_1 ∨ x_3 ∨ ¬x_5)
- C_6 = (x_2 ∨ ¬x_5 ∨ x_6)
- C_7 = (¬x_3 ∨ x_4 ∨ ¬x_6)

Satisfying assignment: x_1=T, x_2=T, x_3=F, x_4=T, x_5=F, x_6=T
- C_1: x_1=T ✓
- C_2: ¬x_1=F, x_4=T ✓
- C_3: ¬x_2=F, ¬x_3=T ✓
- C_4: x_1=T ✓
- C_5: ¬x_1=F, x_3=F, ¬x_5=T ✓
- C_6: x_2=T ✓
- C_7: ¬x_3=T ✓

**Constructed target instance (Consistency of Database Frequency Tables):**
Objects V = {v_1, v_2, v_3, v_4, v_5, v_6} (6 objects, one per variable)
Attributes A:
- Variable attributes: a_1, a_2, a_3, a_4, a_5, a_6 (domain {T, F} each)
- Clause attributes: b_1, b_2, b_3, b_4, b_5, b_6, b_7 (domain {1,...,7} each)

Total: 13 attributes

Frequency tables F (21 tables, 3 per clause):
- For C_1 = (x_1 ∨ x_2 ∨ x_3): tables f_{a_1,b_1}, f_{a_2,b_1}, f_{a_3,b_1}
- For C_2 = (¬x_1 ∨ x_4 ∨ x_5): tables f_{a_1,b_2}, f_{a_4,b_2}, f_{a_5,b_2}
- (... similarly for C_3 through C_7 ...)

Example frequency table f_{a_1, b_1} (for variable x_1 in clause C_1 = (x_1 ∨ x_2 ∨ x_3)):
The 7 satisfying assignments of (x_1 ∨ x_2 ∨ x_3) are:
1: (T,T,T), 2: (T,T,F), 3: (T,F,T), 4: (T,F,F), 5: (F,T,T), 6: (F,T,F), 7: (F,F,T)

| a_1 \ b_1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|-----------|---|---|---|---|---|---|---|
| T         | * | * | * | * | 0 | 0 | 0 |
| F         | 0 | 0 | 0 | 0 | * | * | * |

(Entries marked * are determined by the assignment; each column sums to the number of objects that realize that satisfying pattern.)

Known values K = {} (empty)

**Solution mapping:**
- The satisfying assignment x_1=T, x_2=T, x_3=F, x_4=T, x_5=F, x_6=T corresponds to:
  - g_{a_1}(v_1) = T, g_{a_2}(v_2) = T, g_{a_3}(v_3) = F, g_{a_4}(v_4) = T, g_{a_5}(v_5) = F, g_{a_6}(v_6) = T
- For clause C_1 = (x_1 ∨ x_2 ∨ x_3) with assignment (T, T, F): this matches satisfying pattern #2 (T,T,F)
- The frequency tables are consistent with th
...(truncated)
````


#pagebreak()


== 3SAT $arrow.r$ Timetable Design #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#486)]


=== Reference

````
> [SS19] TIMETABLE DESIGN
> INSTANCE: Set H of "work periods," set C of "craftsmen," set T of "tasks," a subset A(c) ⊆ H of "available hours" for each craftsman c E C, a subset A(t) ⊆ H of "available hours" for each task t E T, and, for each pair (c,t) E C×T, a number R(c,t) E Z_0+ of "required work periods."
> QUESTION: Is there a timetable for completing all the tasks, i.e., a function f: C×T×H → {0,1} (where f(c,t,h) = 1 means that craftsman c works on task t during period h) such that (1) f(c,t,h) = 1 only if h E A(c) ∩ A(t), (2) for each h E H and c E C there is at most one t E T for which f(c,t,h) = 1, (3) for each h E H and t E T there is at most one c E C for which f(c,t,h) = 1, and (4) for each pair (c,t) E C×T there are exactly R(c,t) values of h for which f(c,t,h) = 1?
> Reference: [Even, Itai, and Shamir, 1976]. Transformation from 3SAT.
> Comment: Remains NP-complete even if |H| = 3, A(t) = H for all t E T, and each R(c,t) E {0,1}. The general problem can be solved in poly
...(truncated)
````


#theorem[
  3SAT polynomial-time reduces to Timetable Design.
]


=== Construction

````


**Summary:**

Given a 3-CNF formula phi with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct a TIMETABLE DESIGN instance with |H| = 3 work periods, A(t) = H for all tasks, and all R(c,t) in {0,1} as follows:

1. **Work periods:** H = {h_1, h_2, h_3} (three periods).
2. **Variable gadgets:** For each variable x_i, create two craftsmen c_i^+ (representing x_i = true) and c_i^- (representing x_i = false). Create three tasks for each variable: t_i^1, t_i^2, t_i^3. Set up requirements so that exactly one of c_i^+ or c_i^- works during each period, encoding a truth assignment.
3. **Clause gadgets:** For each clause C_j = (l_a ∨ l_b ∨ l_c), create a task t_j^clause that must be performed exactly once. The three literals' craftsmen are made available for this task in distinct periods. If a literal's craftsman is "free" in the period corresponding to its clause task (i.e., the variable is set to satisfy that literal), it can cover the clause task.
4. **Availability constraints:** Craftsmen for variable x_i have availability sets that force a binary choice (true/false) across the three periods. Clause tasks are available in all three periods, but only a craftsman whose literal satisfies the clause is required to work on it.
5. **Correctness:** The timetable exists if and only if there is a truth assignment satisfying phi. A satisfying assignment frees at least one literal-craftsman per clause to cover the clause task. Conversely, a valid timetable implies an assignment where each clause has a covering literal.
6. **Solution extraction:** From a valid timetable f, set x_i = true if c_i^+ is used in the "positive" pattern, x_i = false otherwise.
````


=== Overhead

````


**Symbols:**
- n = number of variables in the 3SAT instance (`num_variables`)
- m = number of clauses (`num_clauses`)

| Target metric (code name)   | Polynomial (using symbols above) |
|-----------------------------|----------------------------------|
| `num_work_periods`          | 3 (constant)                     |
| `num_craftsmen`             | O(n + m) = 2 * n + m            |
| `num_tasks`                 | O(n + m) = 3 * n + m            |

**Derivation:** Each variable contributes 2 craftsmen and 3 tasks for the variable gadget. Each clause contributes 1 task and potentially 1 auxiliary craftsman. The number of work periods is fixed at 3 (as noted in the GJ comment, NP-completeness holds even with |H| = 3). Construction is O(n + m).
````


=== Correctness

````


- Closed-loop test: construct a 3SAT instance, reduce to TIMETABLE DESIGN, solve the timetable by brute-force enumeration of all possible assignment functions f: C x T x H -> {0,1} satisfying constraints (1)-(4), verify that a valid timetable exists iff the original formula is satisfiable.
- Check that the constructed instance has |H| = 3, all R(c,t) in {0,1}, and A(t) = H for all tasks.
- Edge cases: unsatisfiable formula (expect no valid timetable), formula with single clause (minimal instance), all-positive or all-negative literals.
````


=== Example

````


**Source instance (3SAT):**
Variables: x_1, x_2, x_3, x_4, x_5
Clauses (m = 5):
- C_1 = (x_1 ∨ x_2 ∨ ¬x_3)
- C_2 = (¬x_1 ∨ x_3 ∨ x_4)
- C_3 = (x_2 ∨ ¬x_4 ∨ x_5)
- C_4 = (¬x_2 ∨ ¬x_3 ∨ ¬x_5)
- C_5 = (x_1 ∨ x_4 ∨ x_5)

Satisfying assignment: x_1 = T, x_2 = T, x_3 = F, x_4 = T, x_5 = T.

**Constructed TIMETABLE DESIGN instance:**
- H = {h_1, h_2, h_3}
- Craftsmen: c_1^+, c_1^-, c_2^+, c_2^-, c_3^+, c_3^-, c_4^+, c_4^-, c_5^+, c_5^- (10 variable craftsmen) + auxiliary clause craftsmen (15 total)
- Tasks: t_1^1, t_1^2, t_1^3, ..., t_5^1, t_5^2, t_5^3 (15 variable tasks) + t_C1, t_C2, t_C3, t_C4, t_C5 (5 clause tasks) = 20 tasks total
- All R(c,t) in {0,1}, A(t) = H for all tasks

**Solution:**
The satisfying assignment x_1=T, x_2=T, x_3=F, x_4=T, x_5=T determines which craftsmen take the "positive" vs "negative" pattern. For each clause, at least one literal is true, so its craftsman is free to cover the clause task:
- C_1: x_1=T covers it (c_1^+ is free)
- C_2: x_4=T covers it (c_4^+ is free)
- C_3: x_2=T covers it (c_2^+ is free)
- C_4: x_3=F means ¬x_3=T covers it (c_3^- is free)
- C_5: x_1=T covers it (c_1^+ is free)

A valid timetable exists. ✓
````


#pagebreak()


== 3SAT $arrow.r$ NON-LIVENESS OF FREE CHOICE PETRI NETS #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#920)]


=== Reference

````
> [MS3] NON-LIVENESS OF FREE CHOICE PETRI NETS
> INSTANCE: Petri net P = (S, T, F, M_0) satisfying the free-choice property.
> QUESTION: Is P not live?
>
> Reference: [Jones, Landweber, and Lien, 1977]. Transformation from 3-SATISFIABILITY.
> Comment: The proof that this problem belongs to NP is nontrivial [Hack, 1972].
````


#theorem[
  3SAT polynomial-time reduces to NON-LIVENESS OF FREE CHOICE PETRI NETS.
]


=== Construction

````


**Summary:**
Given a 3SAT instance phi with variables x_1, ..., x_n and clauses C_1, ..., C_m, construct a free-choice Petri net P = (S, T, F, M_0) as follows:

1. **Variable gadgets:** For each variable x_i, create two places p_i (representing x_i = true) and p_i' (representing x_i = false), and two transitions: t_i^+ that consumes from a "choice place" c_i and produces a token in p_i, and t_i^- that consumes from c_i and produces a token in p_i'. The choice place c_i gets one token in M_0. This ensures exactly one truth value is selected per variable, and the free-choice property holds because c_i is the sole input to both t_i^+ and t_i^-.

2. **Clause gadgets:** For each clause C_j = (l_1 OR l_2 OR l_3), create a "clause place" q_j that needs at least one token to enable a transition t_j^check. For each literal l_k in C_j, add an arc from the corresponding literal place (p_i if positive, p_i' if negative) to q_j via an intermediate transition. The free-choice property is maintained by ensuring each place feeds into at most one transition, or all transitions sharing an input place have identical input sets.

3. **Deadlock encoding:** The clause-checking transition t_j^check can only fire if clause C_j is satisfied (at least one literal place has a token routed to q_j). If all clauses are satisfiable, the net can continue firing (is live). If some clause is unsatisfied, the corresponding clause transition is permanently dead, making the net not live.

4. **Initial marking M_0:** Place one token in each choice place c_i. All other places start empty.

**Correctness:**
- (=>) If phi is unsatisfiable, then for every truth assignment (token routing choice), at least one clause has no satisfied literal, so its clause transition is dead. The net is not live. Answer: YES.
- (<=) If phi is satisfiable, the token routing corresponding to the satisfying assignment enables all clause transitions. The net can be shown to be live. Answer: NO.

Note: The actual construction by Jones, Landweber, and Lien (1977) is more intricate to ensure the free-choice property holds globally. The above is a simplified sketch.
````


=== Overhead

````


**Symbols:**
- n = number of variables in the 3SAT instance
- m = number of clauses (= `num_clauses`)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_places` | O(n + m) |
| `num_transitions` | O(n + m) |

**Derivation:**
- Variable gadgets: 2 literal places + 1 choice place per variable = 3n places, 2 transitions per variable = 2n transitions.
- Clause gadgets: O(1) places and transitions per clause = O(m).
- Intermediate routing places/transitions for free-choice compliance: O(m) additional.
- Total: O(n + m) places, O(n + m) transitions.
````


=== Correctness

````


- Closed-loop test: reduce a KSatisfiability instance to NonLivenessFreePetriNet, solve target with BruteForce (explore reachability graph for dead transitions), verify that the answer matches the satisfiability of the original formula.
- Test with a satisfiable 3SAT instance (e.g., (x1 OR x2 OR x3)): net should be live, answer NO.
- Test with an unsatisfiable 3SAT instance (e.g., (x) AND (NOT x) padded to 3 literals): net should not be live, answer YES.
- Verify the free-choice property holds in all constructed nets.
````


=== Example

````


**Source instance (KSatisfiability):**
2 variables {x1, x2}, 2 clauses:
- C1 = (x1 OR x2 OR x2) -- x1 or x2
- C2 = (NOT x1 OR NOT x2 OR NOT x2) -- not x1 or not x2

This is satisfiable (e.g., x1 = true, x2 = false satisfies both).

**Constructed target instance (NonLivenessFreePetriNet):**
Places: {c1, c2, p1, p1', p2, p2', q1, q2} (8 places)
Transitions:
- t1+: c1 -> p1 (assign x1 = true)
- t1-: c1 -> p1' (assign x1 = false)
- t2+: c2 -> p2 (assign x2 = true)
- t2-: c2 -> p2' (assign x2 = false)
- t_c1: checks clause 1 (enabled if p1 or p2 has token routed to q1)
- t_c2: checks clause 2 (enabled if p1' or p2' has token routed to q2)

Initial marking: M_0(c1) = 1, M_0(c2) = 1, all others = 0.

Since phi is satisfiable, the net is live. Answer: NO (the net IS live, so it is NOT the case that it is not live).

If we change to phi = (x1) AND (NOT x1) (unsatisfiable, padded to 3 literals), the net would not be live. Answer: YES.
````


#pagebreak()


= CLIQUE


== CLIQUE $arrow.r$ PARTIALLY ORDERED KNAPSACK #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#523)]


=== Reference

````
> [MP12] PARTIALLY ORDERED KNAPSACK
> INSTANCE: Finite set U, partial order  QUESTION: Is there a subset U' ⊆ U such that if u E U' and u'  Reference: [Garey and Johnson, ——]. Transformation from CLIQUE. Problem is discussed in [Ibarra and Kim, 1975b].
> Comment: NP-complete in the strong sense, even if s(u) = v(u) for all u E U. General problem is solvable in pseudo-polynomial time if < is a "tree" partial order [Garey and Johnson, ——].
````


#theorem[
  CLIQUE polynomial-time reduces to PARTIALLY ORDERED KNAPSACK.
]


=== Construction

````


**Summary:**
Given a CLIQUE instance: a graph G = (V, E) with |V| = n vertices and |E| = m edges, and a positive integer J, construct a PARTIALLY ORDERED KNAPSACK instance as follows:

1. **Items for vertices:** For each vertex vᵢ ∈ V, create an item uᵢ with size s(uᵢ) = 1 and value v(uᵢ) = 1. These are "vertex-items."

2. **Items for edges:** For each edge eₖ = {vᵢ, vⱼ} ∈ E, create an item wₖ with size s(wₖ) = 1 and value v(wₖ) = 1. These are "edge-items."

3. **Partial order (precedences):** For each edge eₖ = {vᵢ, vⱼ}, impose the precedences uᵢ  J, then B - p < C(J,2) and we'd need fewer edge-items, but the constraint still requires the total to be B. So p ≥ J and the p selected vertices must have at least J + C(J,2) - p edges. When p = J, this requires C(J,2) edges, meaning the J vertices form a clique.
   - Hence V' with |V'| = J forms a clique in G.

8. **Solution extraction:** Given a POK solution U', the clique is C = {vᵢ : uᵢ ∈ U'}.

**Key invariant:** All sizes and values are 1 (hence strong NP-completeness). The precedence structure encodes the graph: edge-items depend on vertex-items. The capacity/value target B = K = J + C(J,2) forces exactly J vertices and C(J,2) edges, which is only achievable if the J vertices form a clique.

**Time complexity of reduction:** O(n + m) to construct vertex-items, edge-items, and precedence relations.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G = |V|
- m = `num_edges` of source graph G = |E|
- J = clique size parameter

| Target metric (code name)   | Polynomial (using symbols above) |
|-----------------------------|----------------------------------|
| `num_items`                 | `num_vertices + num_edges`       |
| `num_precedences`           | `2 * num_edges`                  |
| `capacity`                  | `J + J*(J-1)/2`                  |

**Derivation:** Each vertex becomes one item, each edge becomes one item (total n + m items). Each edge creates 2 precedence constraints (one per endpoint), yielding 2m precedences. The capacity is a function of J only.
````


=== Correctness

````


- Closed-loop test: construct a CLIQUE instance (graph + target J), reduce to PARTIALLY ORDERED KNAPSACK, solve target by brute-force (enumerate all downward-closed subsets satisfying capacity), extract clique from vertex-items in the solution, verify it is a clique of size ≥ J in the original graph.
- Test with known YES instance: triangle graph K₃ with J = 3. POK has 3 vertex-items + 3 edge-items = 6 items, B = K = 3 + 3 = 6. Solution: all 6 items.
- Test with known NO instance: path P₃ (3 vertices, 2 edges) with J = 3. POK has 5 items, B = K = 6. Maximum downward-closed set: all 5 items (size 5 < 6). No solution.
- Verify that all sizes and values are 1 (confirming strong NP-completeness).
- Verify that precedence constraints correctly reflect the edge-endpoint relationships.
````


=== Example

````


**Source instance (Clique):**
Graph G with 5 vertices {v₁, v₂, v₃, v₄, v₅} and 7 edges:
- Edges: e₁={v₁,v₂}, e₂={v₁,v₃}, e₃={v₂,v₃}, e₄={v₂,v₄}, e₅={v₃,v₄}, e₆={v₃,v₅}, e₇={v₄,v₅}
- Target clique size J = 3
- Known clique of size 3: {v₂, v₃, v₄} (edges e₃, e₄, e₅ all present ✓)

**Constructed target instance (PartiallyOrderedKnapsack):**
Items: 5 vertex-items {u₁, u₂, u₃, u₄, u₅} + 7 edge-items {w₁, w₂, w₃, w₄, w₅, w₆, w₇} = 12 items total
All sizes = 1, all values = 1.

Precedences:
- w₁ (edge {v₁,v₂}): u₁  J = 3. We need to extract a clique: the 5 vertices induce 7 edges, but only 1 edge-item is selected. The issue is whether this is truly optimal. In fact, U' = {u₁,...,u₅,w₁} is downward-closed and achieves value 6. But this does NOT mean G has no clique of size 3 — it just means the POK has multiple optimal solutions, some of which don't directly encode a size-3 clique. The correctness argument shows that a solution with exactly J vertex-items and C(J,2) edge-items must exist if and only if a clique exists. The above solution works too but contains more vertex-items than needed. To extract the clique, find any J-subset of the selected vertices that forms a clique.
````


#pagebreak()


= Clique


== Clique $arrow.r$ Minimum Tardiness Sequencing #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#206)]


#theorem[
  Clique polynomial-time reduces to Minimum Tardiness Sequencing.
]


=== Construction

````
> MINIMUM TARDINESS SEQUENCING
> INSTANCE: A set T of "tasks," each t ∈ T having "length" 1 and a "deadline" d(t) ∈ Z+, a partial order ≤ on T, and a non-negative integer K ≤ |T|.
> QUESTION: Is there a "schedule" σ: T → {0,1, . . . , |T|−1} such that σ(t) ≠ σ(t') whenever t ≠ t', such that σ(t)  d(t)}| ≤ K?
>
> Theorem 3.10 MINIMUM TARDINESS SEQUENCING is NP-complete.
> Proof: Let the graph G = (V,E) and the positive integer J ≤ |V| constitute an arbitrary instance of CLIQUE. The corresponding instance of MINIMUM TARDINESS SEQUENCING has task set T = V ∪ E, K = |E|−(J(J−1)/2), and partial order and deadlines defined as follows:
>
>     t ≤ t'  ⟺  t ∈ V, t' ∈ E, and vertex t is an endpoint of edge t'
>
>     d(t) = { J(J+1)/2    if t ∈ E
>             { |V|+|E|    if t ∈ V
>
> Thus the "component" corresponding to each vertex is a single task with deadline |V|+|E|, and the "component" corresponding to each edge is a single task with deadline J(J+1)/2. The task corresponding to an edge is forced by the partial order to occur after the tasks corresponding to its two endpoints in the desired schedule, and only edge tasks are in danger of being tardy (being completed after their deadlines).
>
> It is convenient to view the desired schedule schematically, as shown in Figure 3.10. We can think of the portion of the schedule before the edge task deadline as our "clique selection component." There is room for J(J+1)/2 tasks before this deadline. In order to have no more than the specified number of tardy tasks, at least J(J−1)/2 of these "early" tasks must be edge tasks. However, if an edge task precedes this deadline, then so must the vertex tasks corresponding to its endpoints. The minimum possible number of vertices that can be involved in J(J−1)/2 distinct edges is J (which can happen if and only if those edges form a complete graph on those J vertices). This implies that there must be at least J vertex tasks among the "early" tasks. However, there is room for at most
>
>     (J(J+1)/2) − (J(J−1)/2) = J
>
> vertex tasks before the edge task deadline. Therefore, any such schedule must have exactly J vertex tasks and exactly J(J−1)/2 edge tasks before this deadline, and these must correspond to a J-vertex clique in G. Conversely, if G contains a complete subgraph of size J, the desired schedule can be constructed as in Figure 3.10. ∎



**Summary:**
Given a MaximumClique instance (G, J) where G = (V, E), construct a MinimumTardinessSequencing instance as follows:

1. **Task set:** Create one task t_v for each vertex v ∈ V and one task t_e for each edge e ∈ E. Thus |T| = |V| + |E|.
2. **Deadlines:** Set d(t_v) = |V| + |E| for all vertex tasks (very late, never tardy in practice) and d(t_e) = J(J+1)/2 for all edge tasks (an early "clique selection" deadline).
3. **Partial order:** For each edge e = {u, v} ∈ E, add precedence constraints t_u ≤ t_e and t_v ≤ t_e (both endpoints must be scheduled before the edge task).
4. **Tardiness bound:** Set K = |E| − J(J−1)/2. This is the maximum allowed number of tardy tasks (edge tasks that miss their early deadline).
5. **Solution extraction:** In any valid schedule with ≤ K tardy tasks, at least J(J−1)/2 edge tasks must be scheduled before time J(J+1)/2. The precedence constraints force their endpoints (vertex tasks) to also be early. A counting argument shows exactly J vertex tasks and J(J−1)/2 edge tasks are early, and those edges must form a complete subgraph on those J vertices — a J-clique in G.

**Key invariant:** G has a J-clique if and only if T has a valid schedule (respecting partial order) with at most K = |E| − J(J−1)/2 tardy tasks.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G
- J = clique size parameter from source instance

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_tasks` | `num_vertices + num_edges` |
| `num_precedences` | `2 * num_edges` |

**Derivation:**
- One task per vertex in G plus one task per edge in G → |T| = n + m
- The partial order has exactly 2·m precedence pairs (two vertex tasks per edge task)
- K = m − J(J−1)/2 is derived from the source instance parameters; the maximum possible K (when J=1) is m − 0 = m, and minimum K (when J=|V|) is m − |V|(|V|−1)/2 which may be 0 if G is complete

> **Note:** The overhead expressions depend on J (the clique size parameter), which is not a size field of `MaximumClique`. The `num_tasks` and `num_precedences` metrics are not currently registered as `size_fields` on `MinimumTardinessSequencing`. Both issues are blocked on resolving the decision/optimization mismatch noted above.
````


=== Correctness

````


- Closed-loop test: reduce a MaximumClique instance (G, J) to MinimumTardinessSequencing, solve the target with BruteForce (try all permutations σ respecting the partial order), check whether any valid schedule has at most K tardy tasks
- Verify the counting argument: in a satisfying schedule, identify the J vertex-tasks and J(J−1)/2 edge-tasks scheduled before time J(J+1)/2, confirm the corresponding subgraph is a complete graph on J vertices
- Test with K₄ (complete graph on 4 vertices) and J = 3: should find a valid schedule (any 3-clique works)
- Test with a triangle-free graph (e.g., C₅) and J = 3: should find no valid schedule since no 3-clique exists
- Verify the partial order is respected in all candidate schedules by checking that every edge task is scheduled after both its endpoint vertex tasks
````


=== Example

````


**Source instance (MaximumClique):**
Graph G with 4 vertices {0, 1, 2, 3} and 5 edges:
- Edges: {0,1}, {0,2}, {1,2}, {1,3}, {2,3}
- (K₄ minus the edge {0,3}: vertices 0,1,2 form a triangle, plus vertex 3 connected to 1 and 2)
- G contains a 3-clique: {0, 1, 2} (edges {0,1}, {0,2}, {1,2} all present)
- Clique parameter: J = 3

**Constructed target instance (MinimumTardinessSequencing):**

Tasks (|V| + |E| = 4 + 5 = 9 total):
- Vertex tasks: t₀, t₁, t₂, t₃ (deadlines d = |V| + |E| = 9)
- Edge tasks: t₀₁, t₀₂, t₁₂, t₁₃, t₂₃ (deadlines d = J(J+1)/2 = 3·4/2 = 6)

Partial order (endpoints must precede edge task):
- t₀ ≤ t₀₁, t₁ ≤ t₀₁
- t₀ ≤ t₀₂, t₂ ≤ t₀₂
- t₁ ≤ t₁₂, t₂ ≤ t₁₂
- t₁ ≤ t₁₃, t₃ ≤ t₁₃
- t₂ ≤ t₂₃, t₃ ≤ t₂₃

Tardiness bound: K = |E| − J(J−1)/2 = 5 − 3·2/2 = 5 − 3 = 2

**Constructed schedule (from clique {0, 1, 2}):**

Early portion (positions 0–5, before deadline 6 for edge tasks):

Schedule σ:
- σ(t₀) = 0 (position 0, finishes at 1 ≤ d=9 ✓)
- σ(t₁) = 1 (position 1, finishes at 2 ≤ d=9 ✓)
- σ(t₂) = 2 (position 2, finishes at 3 ≤ d=9 ✓)
- σ(t₀₁) = 3 (finishes at 4 ≤ d=6 ✓, not tardy — endpoints t₀,t₁ scheduled earlier ✓)
- σ(t₀₂) = 4 (finishes at 5 ≤ d=6 ✓, not tardy — endpoints t₀,t₂ scheduled earlier ✓)
- σ(t₁₂) = 5 (finishes at 6 ≤ d=6 ✓, not tardy — endpoints t₁,t₂ scheduled earlier ✓)

Late portion (positions 6–8, after deadline 6 for edge tasks):
- σ(t₃) = 6 (finishes at 7 ≤ d=9 ✓, not tardy)
- σ(t₁₃) = 7 (finishes at 8 > d=6 — TARDY ✗)
- σ(t₂₃) = 8 (finishes at 9 > d=6 — TARDY ✗)

Tardy tasks: {t₁₃, t₂₃}, count = 2 ≤ K = 2 ✓
Partial order respected: all vertex tasks precede their edge tasks ✓

**Solution extraction:**
The J(J−1)/2 = 3 edge tasks scheduled before deadline 6 are t₀₁, t₀₂, t₁₂. Their endpoint vertex tasks are {t₀, t₁, t₂}. These correspond to vertices {0, 1, 2} forming a triangle (complete subgraph) in G — a 3-clique ✓.
````


#pagebreak()


= DIRECTED TWO-COMMODITY INTEGRAL FLOW


== DIRECTED TWO-COMMODITY INTEGRAL FLOW $arrow.r$ UNDIRECTED TWO-COMMODITY INTEGRAL FLOW #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#277)]


#pagebreak()


= ExactCoverBy3Sets


== ExactCoverBy3Sets $arrow.r$ BoundedDiameterSpanningTree #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#913)]


=== Reference

````
> [ND4] BOUNDED DIAMETER SPANNING TREE
> INSTANCE: Graph G = (V, E), a weight w(e) in Z+ for each e in E, positive integers B and D.
> QUESTION: Is there a spanning tree T = (V, E') for G such that sum_{e in E'} w(e)  Reference: [Garey and Johnson, ----]. Transformation from X3C.
> Comment: NP-complete for any fixed D >= 4, even if w(e) in {1, 2} for all e in E. Can be solved in polynomial time for D <= 3 or if all weights are equal.
````


#theorem[
  ExactCoverBy3Sets polynomial-time reduces to BoundedDiameterSpanningTree.
]


=== Construction

````


Given an X3C instance with universe X = {x_1, ..., x_{3q}} and collection C = {C_1, ..., C_m} where each C_i is a 3-element subset of X:

1. **Central hub construction:** Create a central vertex r that will serve as the "center" of the bounded-diameter tree. All paths in the tree must pass within D/2 hops of r.

2. **Element vertices:** For each element x_j in X, create an element vertex e_j.

3. **Set vertices:** For each set C_i in C, create a set vertex s_i.

4. **Edge construction and weights:**
   - Connect r to each set vertex s_i with weight 1.
   - Connect each set vertex s_i to the element vertices in C_i with weight 1 or 2 (encoding the selection cost).
   - Add additional edges with weight 2 between element vertices and the hub to ensure connectivity.

5. **Parameter setting:**
   - Diameter bound D = 4 (the base case; elements reach through set vertices within 2 hops of r, so diameter is at most 4).
   - Weight bound B is set so that the minimum weight is achievable only if the selected set vertices form an exact cover (using weight-1 edges for covered elements).

6. **Solution extraction:** From a feasible bounded-diameter spanning tree, the set vertices adjacent to element vertices via weight-1 edges correspond to the exact cover.

**Key idea:** The weight constraint forces choosing exactly q set vertices to cover all elements cheaply (weight 1), while the diameter constraint D = 4 ensures the tree structure remains hub-and-spoke. Choosing fewer than q sets leaves uncovered elements requiring expensive (weight 2) direct connections, exceeding the weight bound.
````


=== Overhead

````


**Symbols:**
- q = |X|/3 (universe size / 3)
- m = number of sets in C
- |X| = 3q (universe size)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | O(q + m) = O(|X| + m) |
| `num_edges` | O(3m + |X|) = O(m + q) |

**Derivation:** One hub vertex, m set vertices, 3q element vertices. Edges: m hub-to-set edges, 3m set-to-element edges, plus possibly q direct hub-to-element backup edges.
````


=== Correctness

````

- Closed-loop test: reduce an X3C instance to BoundedDiameterSpanningTree, solve with BruteForce, extract the exact cover from the spanning tree structure.
- Negative test: use an X3C instance with no exact cover, verify no spanning tree satisfies both weight and diameter bounds.
- Diameter check: verify that the solution tree has no path with more than D edges.
- Weight check: verify total edge weight <= B.
- Special case: with D = 3 or equal weights, verify polynomial-time solvability (no NP-hardness expected).
````


=== Example

````


**Source instance (X3C):**
Universe X = {1, 2, 3, 4, 5, 6}, q = 2.
Sets: C_1 = {1, 2, 3}, C_2 = {4, 5, 6}, C_3 = {1, 4, 5}, C_4 = {2, 3, 6}.
Exact cover: {C_1, C_2} (covers all elements exactly once).
Alternative exact cover: {C_3, C_4} also works.

**Constructed target instance (BoundedDiameterSpanningTree):**
- Vertices: r (hub), s_1, s_2, s_3, s_4 (set vertices), e_1, ..., e_6 (element vertices). Total: 11 vertices.
- Edges with weights:
  - {r, s_i}: w=1 for i=1,2,3,4
  - {s_1, e_1}, {s_1, e_2}, {s_1, e_3}: w=1
  - {s_2, e_4}, {s_2, e_5}, {s_2, e_6}: w=1
  - {s_3, e_1}, {s_3, e_4}, {s_3, e_5}: w=1
  - {s_4, e_2}, {s_4, e_3}, {s_4, e_6}: w=1
  - {r, e_j}: w=2 for j=1,...,6 (backup direct connections)
- D = 4, B = 2*1 + 6*1 = 8 (2 hub-to-set edges + 6 set-to-element edges, all weight 1)

**Solution mapping:**
- Spanning tree using exact cover {C_1, C_2}: edges {r,s_1}, {r,s_2}, {s_1,e_1}, {s_1,e_2}, {s_1,e_3}, {s_2,e_4}, {s_2,e_5}, {s_2,e_6}, plus edges to connect remaining set vertices (not needed if s_3, s_4 are connected directly to r or via element vertices).
- Wait: we need to span all 11 vertices. Add {r,s_3} and {r,s_4}: weight += 2, total = 10. But B = 8 won't work.
- Revised: exclude s_3, s_4 from the graph, or set B appropriately. The exact construction depends on Garey and Johnson's specific gadgets. The core idea is that B is calibrated to allow exactly q set vertices with weight-1 coverage.
````


#pagebreak()


= FEEDBACK EDGE SET


== FEEDBACK EDGE SET $arrow.r$ GROUPING BY SWAPPING #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#454)]


=== Reference

````
> [SR21] GROUPING BY SWAPPING
> INSTANCE: Finite alphabet Σ, string x E Σ*, and a positive integer K.
> QUESTION: Is there a sequence of K or fewer adjacent symbol interchanges that converts x into a string y in which all occurrences of each symbol a E Σ are in a single block, i.e., y has no subsequences of the form aba for a,b E Σ and a ≠ b?
> Reference: [Howell, 1977]. Transformation from FEEDBACK EDGE SET.
````


#theorem[
  FEEDBACK EDGE SET polynomial-time reduces to GROUPING BY SWAPPING.
]


=== Construction

````


**Summary:**
Given a FEEDBACK EDGE SET instance (G, K) where G = (V, E) is an undirected graph and K is a budget for edge removal to make G acyclic, construct a GROUPING BY SWAPPING instance as follows:

1. **Alphabet construction:** Create an alphabet Sigma with one symbol for each vertex v in V. That is, |Sigma| = |V|.

2. **String construction:** Construct the string x from the graph G by encoding the edge structure. For each edge {u, v} in E, the symbols u and v must be interleaved in x so that grouping them requires adjacent swaps. The string is constructed by traversing the edges and creating a sequence where vertices sharing an edge have their symbols interleaved -- specifically, for each cycle in G, the symbols of the cycle's vertices appear in an order that requires swaps proportional to the cycle length to unscramble.

3. **Budget parameter:** Set the swap budget K' to be a function of K and the graph structure. The key insight is that each edge in a feedback edge set corresponds to a "crossing" in the string that must be resolved by a swap. Removing an edge from a cycle in G corresponds to performing swaps to separate the interleaved occurrences of the corresponding vertex symbols.

4. **Solution extraction:** Given a sequence of at most K' adjacent swaps that groups the string, identify which "crossings" were resolved. The edges corresponding to these crossings form a feedback edge set of size at most K in G.

**Key invariant:** G has a feedback edge set of size at most K if and only if the string x can be grouped (all occurrences of each symbol contiguous) using at most K' adjacent transpositions. Cycles in G correspond to interleaving patterns in x that require swaps to resolve, and breaking each cycle requires resolving at least one crossing.
````


=== Overhead

````


**Symbols:**
- n = |V| = number of vertices in G
- m = |E| = number of edges in G

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `alphabet_size` | n |
| `string_length` | O(m + n) |
| `budget` | polynomial in K, n, m |

**Derivation:** The alphabet has one symbol per vertex. Each edge contributes a constant number of symbol occurrences to the string, so the string length is O(m + n). The budget K' is derived from K and the graph structure, maintaining the correspondence between feedback edges and swap operations needed to resolve interleaving patterns.
````


=== Correctness

````


- Closed-loop test: reduce a Feedback Edge Set instance to GroupingBySwapping, solve the grouping problem via brute-force enumeration of swap sequences, extract the implied feedback edge set, verify it makes the original graph acyclic
- Check that the minimum number of swaps to group the string corresponds to the minimum feedback edge set size
- Test with a graph containing multiple independent cycles (each cycle requires at least one feedback edge) to verify the budget is correctly computed
- Verify with a tree (acyclic graph) that zero swaps are needed (string is already groupable or trivially groupable)
````


=== Example

````


**Source instance (Feedback Edge Set):**
Graph G with 6 vertices {a, b, c, d, e, f} and 7 edges:
- Edges: {a,b}, {b,c}, {c,a}, {c,d}, {d,e}, {e,f}, {f,d}
- Two triangles: (a,b,c) and (d,e,f), connected by edge {c,d}
- Minimum feedback edge set size: K = 2 (remove one edge from each triangle, e.g., {c,a} and {f,d})

**Constructed target instance (GroupingBySwapping):**
Using the reduction:
- Alphabet Sigma = {a, b, c, d, e, f}
- String x is constructed from the graph structure. The triangles create interleaving patterns:
  - Triangle (a,b,c): symbols a, b, c are interleaved, e.g., subsequence "abcabc"
  - Triangle (d,e,f): symbols d, e, f are interleaved, e.g., subsequence "defdef"
  - Edge {c,d} links the two groups
- The resulting string x might look like: "a b c a b c d e f d e f" with careful interleaving of shared edges
- Budget K' is set based on K=2 and the encoding

**Solution mapping:**
- A minimum swap sequence groups the string by resolving exactly 2 interleaving crossings
- These crossings correspond to feedback edges {c,a} and {f,d}
- Removing {c,a} from triangle (a,b,c) and {f,d} from triangle (d,e,f) makes G acyclic
- The resulting graph is a tree/forest, confirming a valid feedback edge set of size 2

**Note:** The exact string encoding depends on Howell's 1977 construction, which carefully maps cycle structure to symbol interleaving patterns.
````


#pagebreak()


= GRAPH 3-COLORABILITY


== GRAPH 3-COLORABILITY $arrow.r$ PARTITION INTO FORESTS #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#843)]


=== Reference

````
> [GT14] PARTITION INTO FORESTS
> INSTANCE: Graph G = (V,E), positive integer K ≤ |V|.
> QUESTION: Can the vertices of G be partitioned into k ≤ K disjoint sets V_1, V_2, . . . , V_k such that, for 1 ≤ i ≤ k, the subgraph induced by V_i contains no circuits?
> Reference: [Garey and Johnson, ——]. Transformation from GRAPH 3-COLORABILITY.
````


#theorem[
  GRAPH 3-COLORABILITY polynomial-time reduces to PARTITION INTO FORESTS.
]


=== Construction

````


Given an instance G = (V, E) of GRAPH 3-COLORABILITY, construct the following instance of PARTITION INTO FORESTS:

1. **Graph construction:** Build a new graph G' = (V', E') as follows. Start with the original graph G. For each edge {u, v} in E, add a new "edge gadget" vertex w_{uv} and connect it to both u and v, forming a triangle {u, v, w_{uv}}. This ensures that u and v cannot be in the same partition class (since any induced subgraph containing both endpoints of a triangle edge plus the apex vertex would contain a cycle — specifically the triangle itself).

   Formally:
   - V' = V union {w_{uv} : {u,v} in E}. So |V'| = |V| + |E| = n + m.
   - E' = E union {{u, w_{uv}} : {u,v} in E} union {{v, w_{uv}} : {u,v} in E}. So |E'| = |E| + 2|E| = 3m.

2. **Bound:** Set K = 3.

**Correctness:**
- **Forward (3-coloring -> partition into 3 forests):** Given a proper 3-coloring c: V -> {0,1,2} of G, assign each gadget vertex w_{uv} to any color class different from both c(u) and c(v) (possible since c(u) != c(v) and there are 3 classes). Each color class induces an independent set on the original vertices V (since c is a proper coloring). Each gadget vertex w_{uv} is adjacent to at most one vertex in its own class. The induced subgraph on each class is therefore a forest (a collection of stars with gadget vertices as potential leaves).

- **Backward (partition into 3 forests -> 3-coloring):** Given a partition V'_0, V'_1, V'_2 of V' into 3 acyclic induced subgraphs, consider any edge {u,v} in E. The triangle {u, v, w_{uv}} means all three vertices must be in different classes (if two were in the same class, say u and v in V'_i, then the induced subgraph G'[V'_i] would contain the edge {u,v}, and w_{uv} must be in some V'_j. If j = i, we get a triangle = cycle, contradiction. If j != i, we still have u and v in the same class with edge {u,v} between them. This is allowed for a forest only if it doesn't create a cycle. However, consider the broader structure: for any triangle, at most one edge can appear within a single acyclic partition class.) In fact, since each original edge {u,v} is part of a triangle with w_{uv}, and a triangle is a 3-cycle, no two vertices of any triangle can be in the same class (each class must be acyclic, and two triangle vertices in the same class would leave the third forced to create a cycle with the remaining two edges). Thus the restriction of the partition to V gives a proper 3-coloring.

**Alternative (simpler) reduction:**
A proper 3-coloring is trivially a partition into 3 independent sets. Each independent set is trivially a forest (no edges at all). So the identity reduction G' = G, K = 3 works for the direction "3-colorable implies partitionable into 3 forests." The reverse does not hold in general (a forest partition allows edges within classes). The gadget construction above forces the reverse direction.
````


=== Overhead

````


| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | `num_vertices + num_edges` |
| `num_edges` | `3 * num_edges` |
| `num_forests` | `3` |

**Derivation:**
- Vertices: n original + m gadget vertices = n + m
- Edges: m original edges + 2m gadget edges = 3m
- K = 3 (fixed constant)
````


=== Correctness

````

- Closed-loop test: construct a graph G; apply the reduction to get a PartitionIntoForests instance (G', K=3); solve G' with BruteForce; verify the answer matches whether G is 3-colorable.
- Verify vertex count: |V'| = |V| + |E|.
- Verify edge count: |E'| = 3|E|.
- Test with K_4 (not 3-colorable, partition should fail) and a bipartite graph (always 2-colorable hence 3-colorable, partition should succeed).
````


=== Example

````


**Source instance (Graph3Colorability):**
Graph G with 4 vertices {0, 1, 2, 3} and 4 edges:
- Edges: {0,1}, {1,2}, {2,3}, {3,0} (the 4-cycle C_4)
- G is 3-colorable: c(0)=0, c(1)=1, c(2)=0, c(3)=1 (in fact 2-colorable)

**Constructed target instance (PartitionIntoForests):**
- Add 4 gadget vertices: w_{01}=4, w_{12}=5, w_{23}=6, w_{30}=7
- V' = {0,1,2,3,4,5,6,7}, |V'| = 8
- E' = original 4 edges + 8 gadget edges:
  {0,1}, {1,2}, {2,3}, {3,0}, {0,4}, {1,4}, {1,5}, {2,5}, {2,6}, {3,6}, {3,7}, {0,7}
- |E'| = 12 = 3 * 4
- K = 3

**Solution mapping:**
- 3-coloring: c(0)=0, c(1)=1, c(2)=0, c(3)=1
- Gadget assignments: w_{01}=4 -> class 2, w_{12}=5 -> class 2, w_{23}=6 -> class 2, w_{30}=7 -> class 2
- Partition: V'_0 = {0, 2}, V'_1 = {1, 3}, V'_2 = {4, 5, 6, 7}
  - G'[V'_0] = edges between {0,2}? No edge {0,2}. So G'[V'_0] has no edges -> forest.
  - G'[V'_1] = edges between {1,3}? No edge {1,3}. So G'[V'_1] has no edges -> forest.
  - G'[V'_2] = edges among {4,5,6,7}? No original or gadget edges connect gadget vertices to each other -> forest (isolated vertices).
- Answer: YES
````


#pagebreak()


= Graph 3-Colorability


== Graph 3-Colorability $arrow.r$ Sparse Matrix Compression #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#431)]


=== Reference

````
> [SR13] SPARSE MATRIX COMPRESSION
> INSTANCE: An m x n matrix A with entries a_{ij} E {0,1}, 1  QUESTION: Is there a sequence (b_1, b_2, ..., b_{n+K}) of integers b_i, each satisfying 0  {1,2,...,K} such that, for 1  Reference: [Even, Lichtenstein, and Shiloach, 1977]. Transformation from GRAPH 3-COLORABILITY.
> Comment: Remains NP-complete for fixed K = 3.
````


#theorem[
  Graph 3-Colorability polynomial-time reduces to Sparse Matrix Compression.
]


=== Construction

````


**Summary:**
Given a Graph 3-Colorability instance G = (V, E) with |V| = p vertices and |E| = q edges, construct a Sparse Matrix Compression instance as follows. The idea (following Even, Lichtenstein, and Shiloach 1977, as described by Jugé et al. 2026) is to represent each vertex by a "tile" -- a row pattern in the binary matrix -- and to show that the rows can be overlaid with shift offsets from {1,2,3} (K=3) without conflict if and only if G is 3-colorable.

1. **Matrix construction:** Create a binary matrix A of m rows and n columns. Each vertex v_i in V is represented by a row (tile) in the matrix. The tile for vertex v_i has exactly deg(v_i) entries equal to 1 (where deg is the degree of v_i), placed at column positions corresponding to the edges incident to v_i. Specifically, number the edges e_1, ..., e_q. For vertex v_i, set a_{i,j} = 1 if edge e_j is incident to v_i, and a_{i,j} = 0 otherwise. So m = p (one row per vertex) and n = q (one column per edge).

2. **Bound K:** Set K = 3 (the number of available colors/shifts).

3. **Shift function:** The function s: {1,...,m} -> {1,...,3} assigns each row (vertex) a shift value in {1,2,3}, corresponding to a color assignment.

4. **Storage vector:** The vector (b_1, ..., b_{n+K}) of length q+3 stores the compressed representation. The constraint b_{s(i)+j-1} = i for each a_{ij}=1 means that when row i is placed at offset s(i), its non-zero entries must appear at their correct positions without conflict with other rows.

5. **Correctness (forward):** If G has a proper 3-coloring c: V -> {1,2,3}, set s(i) = c(v_i). For any edge e_j = {v_a, v_b}, we have a_{a,j} = 1 and a_{b,j} = 1. The positions s(a)+j-1 and s(b)+j-1 in the storage vector must hold values a and b respectively. Since c(v_a) != c(v_b), we have s(a) != s(b), so s(a)+j-1 != s(b)+j-1, and the two entries do not conflict.

6. **Correctness (reverse):** If a valid compression exists with K=3, define c(v_i) = s(i). Adjacent vertices v_a, v_b sharing edge e_j cannot have the same shift (otherwise b_{s(a)+j-1} would need to equal both a and b), so the coloring is proper.

**Key invariant:** Two vertices sharing an edge produce conflicting entries in the storage vector when assigned the same shift, making a valid compression with K=3 equivalent to a proper 3-coloring.

**Time complexity of reduction:** O(p * q) to construct the incidence matrix.
````


=== Overhead

````


**Symbols:**
- p = `num_vertices` of source Graph 3-Colorability instance (|V|)
- q = `num_edges` of source Graph 3-Colorability instance (|E|)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_rows` | `num_vertices` |
| `num_cols` | `num_edges` |
| `bound_k` | 3 |
| `vector_length` | `num_edges + 3` |

**Derivation:** The matrix has one row per vertex (m = p) and one column per edge (n = q). The bound K = 3 is fixed. The storage vector has length n + K = q + 3.
````


=== Correctness

````


- Closed-loop test: reduce a KColoring(k=3) instance to SparseMatrixCompression, solve target with BruteForce (enumerate all shift assignments s: {1,...,m} -> {1,2,3} and check for valid storage vector), extract solution, verify on source
- Test with known YES instance: a triangle K_3 is 3-colorable; the 3x3 incidence matrix with K=3 should be compressible
- Test with known NO instance: K_4 is not 3-colorable; the 4x6 incidence matrix with K=3 should not be compressible
- Verify that for small graphs (6-8 vertices), 3-colorability agrees with compressibility with K=3
````


=== Example

````


**Source instance (Graph 3-Colorability / KColoring k=3):**
Graph G with 6 vertices {v_1, v_2, v_3, v_4, v_5, v_6} and 7 edges:
- e_1: {v_1,v_2}, e_2: {v_1,v_3}, e_3: {v_2,v_3}, e_4: {v_2,v_4}, e_5: {v_3,v_5}, e_6: {v_4,v_5}, e_7: {v_5,v_6}
- This graph is 3-colorable: c(v_1)=1, c(v_2)=2, c(v_3)=3, c(v_4)=1, c(v_5)=2, c(v_6)=1

**Constructed target instance (SparseMatrixCompression):**
Matrix A (6 x 7, rows=vertices, cols=edges):

|       | e_1 | e_2 | e_3 | e_4 | e_5 | e_6 | e_7 |
|-------|-----|-----|-----|-----|-----|-----|-----|
| v_1   |  1  |  1  |  0  |  0  |  0  |  0  |  0  |
| v_2   |  1  |  0  |  1  |  1  |  0  |  0  |  0  |
| v_3   |  0  |  1  |  1  |  0  |  1  |  0  |  0  |
| v_4   |  0  |  0  |  0  |  1  |  0  |  1  |  0  |
| v_5   |  0  |  0  |  0  |  0  |  1  |  1  |  1  |
| v_6   |  0  |  0  |  0  |  0  |  0  |  0  |  1  |

Bound K = 3. Storage vector length = 7 + 3 = 10.

**Solution mapping:**
Shift function from 3-coloring: s(v_1)=1, s(v_2)=2, s(v_3)=3, s(v_4)=1, s(v_5)=2, s(v_6)=1.

Constructing storage vector b = (b_1, ..., b_10):
- v_1 (shift=1): a_{1,1}=1 -> b_{1+1-1}=b_1=1; a_{1,2}=1 -> b_{1+2-1}=b_2=1
- v_2 (shift=2): a_{2,1}=1 -> b_{2+1-1}=b_2... conflict with v_1 at b_2!

The incidence-matrix construction above is a simplified sketch. The actual Even-Lichtenstein-Shiloach reduction uses more elaborate gadgets to encode vertex adjacency into the row patterns such that overlapping tiles with the same shift always produces a conflict for adjacent vertices. The core idea remains: vertex-to-tile, color-to-shift, edge-conflict-to-overlay-conflict.

**Verification:**
The 3-coloring c(v_1)=1, c(v_2)=2, c(v_3)=3, c(v_4)=1, c(v_5)=2, c(v_6)=1 is proper:
- e_1: c(v_1)=1 != c(v_2)=2
- e_2: c(v_1)=1 != c(v_3)=3
- e_3: c(v_2)=2 != c(v_3)=3
- e_4: c(v_2)=2 != c(v_4)=1
- e_5: c(v_3)=3 != c(v_5)=2
- e_6: c(v_4)=1 != c(v_5)=2
- e_7: c(v_5)=2 != c(v_6)=1

All edges have differently colored endpoints, confirming the correspondence between 3-colorability and 
...(truncated)
````


#pagebreak()


== Graph 3-Colorability $arrow.r$ Conjunctive Query Foldability #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#463)]


=== Reference

````
> [SR30] CONJUNCTIVE QUERY FOLDABILITY
> INSTANCE: Finite domain set D, a collection R = {R_1, R_2, ..., R_m} of relations, where each R_i consists of a set of d_i-tuples with entries from D, a set X of distinguished variables, a set Y of undistinguished variables, and two "queries" Q_1 and Q_2 over X, Y, D, and R, where a query Q has the form
>
> (x_1, x_2, ..., x_k)(∃y_1, y_2, ..., y_l)(A_1 ∧ A_2 ∧ ... ∧ A_r)
>
> for some k, l, and r, with X' = {x_1, x_2, ..., x_k} ⊆ X, Y' = {y_1, y_2, ..., y_l} ⊆ Y, and each A_i of the form R_j(u_1, u_2, ..., u_{d_j}) with each u E D ∪ X' ∪ Y' (see reference for interpretation of such expressions in terms of data bases).
> QUESTION: Is there a function σ: Y → X ∪ Y ∪ D such that, if for each y E Y the symbol σ(y) is substituted for every occurrence of y in Q_1, then the result is query Q_2?
> Reference: [Chandra and Merlin, 1977]. Transformation from GRAPH 3-COLORABILITY.
> Comment: The isomorphism problem for conjunctive queries (with two queries b
...(truncated)
````


#theorem[
  Graph 3-Colorability polynomial-time reduces to Conjunctive Query Foldability.
]


=== Construction

````


**Summary:**
Given a Graph 3-Colorability instance G = (V, E), construct a Conjunctive Query Foldability instance as follows:

1. **Domain construction:** Let D = {1, 2, 3} (the three colors).

2. **Relation construction:** Create a single binary relation R consisting of all pairs (i, j) where i != j and i, j in {1, 2, 3}. That is, R = {(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)} — this is the edge relation of the complete graph K_3.

3. **Query Q_G (from graph G):** For each vertex v in V, introduce a variable y_v (all undistinguished). For each edge (u, v) in E, add a conjunct R(y_u, y_v). The query is:
   Q_G = ()(exists y_{v_1}, ..., y_{v_n})(R(y_u, y_v) for each (u,v) in E)
   This is a Boolean query (no distinguished variables) with |V| existential variables and |E| conjuncts.

4. **Query Q_{K_3} (from complete triangle):** Introduce three undistinguished variables z_1, z_2, z_3. Add conjuncts R(z_1, z_2), R(z_2, z_3), R(z_3, z_1). The query is:
   Q_{K_3} = ()(exists z_1, z_2, z_3)(R(z_1, z_2) ∧ R(z_2, z_3) ∧ R(z_3, z_1))

5. **Foldability condition:** Ask whether Q_G can be "folded" into Q_{K_3}, i.e., whether there exists a substitution sigma mapping variables of Q_G to variables of Q_{K_3} (plus constants from D) such that applying sigma to Q_G yields Q_{K_3}. By the Chandra-Merlin homomorphism theorem, such a substitution exists if and only if there is a homomorphism from G to K_3, which is equivalent to G being 3-colorable.

6. **Solution extraction:** Given a folding sigma, the 3-coloring is: color vertex v with the color corresponding to sigma(y_v), where sigma maps y_v to one of {z_1, z_2, z_3} (corresponding to colors 1, 2, 3). Adjacent vertices must receive different colors because R only contains pairs of distinct values.

**Key invariant:** G is 3-colorable if and only if the query Q_G can be folded into Q_{K_3}. The folding function sigma encodes the color assignment: sigma(y_v) = z_c means vertex v gets color c.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `domain_size` | `3` (constant) |
| `num_relations` | `1` (single binary relation) |
| `relation_tuples` | `6` (constant: edges of K_3) |
| `num_undistinguished_vars_q1` | `num_vertices` |
| `num_conjuncts_q1` | `num_edges` |
| `num_undistinguished_vars_q2` | `3` (constant) |
| `num_conjuncts_q2` | `3` (constant) |

**Derivation:**
- Domain D = {1, 2, 3}: constant size 3
- One relation R with 6 tuples (all non-equal pairs from {1,2,3})
- Q_G has one variable per vertex (n variables) and one conjunct per edge (m conjuncts)
- Q_{K_3} has 3 variables and 3 conjuncts (constant)
- Total encoding size: O(n + m)
````


=== Correctness

````


- Closed-loop test: reduce a KColoring(k=3) instance to ConjunctiveQueryFoldability, solve the foldability problem with BruteForce (enumerate all substitutions sigma: Y -> X ∪ Y ∪ D), extract the coloring, verify it is a valid 3-coloring on the original graph
- Check that a 3-colorable graph (e.g., a bipartite graph) yields a positive foldability instance
- Check that a non-3-colorable graph (e.g., K_4) yields a negative foldability instance
- Verify the folding encodes a valid color assignment: adjacent vertices map to different z_i variables
````


=== Example

````


**Source instance (Graph 3-Colorability):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 9 edges (a wheel graph W_5 minus one spoke):
- Edges: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {5,0}, {0,2}, {0,3}, {1,4}
- This graph is 3-colorable but not 2-colorable (it contains odd cycles)

Valid 3-coloring: 0->1, 1->2, 2->3, 3->1, 4->3, 5->2
- Edge {0,1}: colors 1,2 -- different
- Edge {1,2}: colors 2,3 -- different
- Edge {2,3}: colors 3,1 -- different
- Edge {3,4}: colors 1,3 -- different
- Edge {4,5}: colors 3,2 -- different
- Edge {5,0}: colors 2,1 -- different
- Edge {0,2}: colors 1,3 -- different
- Edge {0,3}: colors 1,1 -- INVALID! Need to fix coloring.

Corrected 3-coloring: 0->1, 1->2, 2->3, 3->2, 4->3, 5->3
- Edge {0,1}: 1,2 -- different
- Edge {1,2}: 2,3 -- different
- Edge {2,3}: 3,2 -- different
- Edge {3,4}: 2,3 -- different
- Edge {4,5}: 3,3 -- INVALID!

Revised graph (simpler, verified): G with 6 vertices {0,1,2,3,4,5} and 7 edges:
- Edges: {0,1}, {0,2}, {1,2}, {1,3}, {2,4}, {3,5}, {4,5}
- Valid 3-coloring: 0->1, 1->2, 2->3, 3->1, 4->1, 5->2
  - {0,1}: 1,2 -- different
  - {0,2}: 1,3 -- different
  - {1,2}: 2,3 -- different
  - {1,3}: 2,1 -- different
  - {2,4}: 3,1 -- different
  - {3,5}: 1,2 -- different
  - {4,5}: 1,2 -- different

**Constructed target instance (ConjunctiveQueryFoldability):**
Domain D = {1, 2, 3}
Relation R = {(1,2), (1,3), (2,1), (2,3), (3,1), (3,2)}

Q_1 (from G): ()(exists y_0, y_1, y_2, y_3, y_4, y_5)(R(y_0, y_1) ∧ R(y_0, y_2) ∧ R(y_1, y_2) ∧ R(y_1, y_3) ∧ R(y_2, y_4) ∧ R(y_3, y_5) ∧ R(y_4, y_5))

Q_2 (K_3): ()(exists z_1, z_2, z_3)(R(z_1, z_2) ∧ R(z_2, z_3) ∧ R(z_3, z_1))

**Solution mapping:**
- Folding sigma: y_0 -> z_1, y_1 -> z_2, y_2 -> z_3, y_3 -> z_1, y_4 -> z_1, y_5 -> z_2
- This encodes the 3-coloring: vertex 0->color 1, 1->color 2, 2->color 3, 3->color 1, 4->color 1, 5->color 2
- Verification: applying sigma to Q_1 yields conjuncts R(z_1, z_2), R(z_1, z_3), R(z_2, z_3), R(z_2, z_1), R(z_3, z_1), R(z_1, z_2), R(z_1, z_2) — 
...(truncated)
````


#pagebreak()


= HAMILTONIAN CIRCUIT


== HAMILTONIAN CIRCUIT $arrow.r$ BOUNDED COMPONENT SPANNING FOREST #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#238)]


=== Reference

````
> [ND10] BOUNDED COMPONENT SPANNING FOREST
> INSTANCE: Graph G=(V,E), positive integers K and B, non-negative integer weight w(v) for each v in V.
> QUESTION: Can the vertices of V be partitioned into at most K disjoint subsets, each inducing a connected subgraph, with the total vertex weight of each subset at most B?
> Reference: [Garey and Johnson, 1979]. Transformation from HAMILTONIAN CIRCUIT.
> Comment: NP-complete even for K=|V|-1 (i.e., spanning trees).
````


#theorem[
  HAMILTONIAN CIRCUIT polynomial-time reduces to BOUNDED COMPONENT SPANNING FOREST.
]


=== Construction

````
**Summary:**
Given a Hamiltonian Circuit instance G = (V, E) with n = |V| vertices, construct a BOUNDED COMPONENT SPANNING FOREST instance as follows:

1. **Pick an edge:** Choose any edge {u, v} in E. If E is empty, output a trivial NO instance.
2. **Add pendant vertices:** Construct G' = (V', E') where:
   - V' = V union {s, t} (two new vertices, so |V'| = n + 2)
   - E' = E union {{s, u}, {t, v}}
   - s is connected only to u; t is connected only to v (both have degree 1 in G').
3. **Set weights:** All vertices receive unit weight 1.
4. **Set parameters:** max_components = 1, max_weight = n + 2.

**Correctness argument:**

- **Forward (HC implies BCSF):** If G has a Hamiltonian circuit C, remove edge {u, v} from C to obtain a Hamiltonian path P in G from u to v. Extend P to the path s-u-...-v-t in G'. This path spans all n + 2 vertices. Placing all vertices in a single component gives weight n + 2 = max_weight and 1 component = max_components. The BCSF instance is satisfied.

- **Backward (BCSF implies HC):** Suppose G' admits a partition into at most 1 connected component of total weight at most n + 2. Since all n + 2 vertices have unit weight and max_weight = n + 2, every vertex must belong to the single component (otherwise some vertices would be unassigned, which is not a valid partition). Now, s has degree 1 in G' (adjacent only to u) and t has degree 1 in G' (adjacent only to v). Within this connected component, consider any spanning tree T of G'. In T, the unique path from s to t must pass through u (since s's only neighbor is u) and through v (since t's only neighbor is v). **Key structural argument:** If G' is connected with the pendant structure, then G must contain a path from u to v that visits all original vertices. Specifically, removing s and t from T yields a spanning tree of G; the path from u to v in T (which exists since T is connected) visits all vertices of G because T spans V'. Since {u, v} is in E(G), appending edge {u, v} closes the path into a Hamiltonian circuit of G.

  **Caveat:** The backward direction relies on the degree-1 pendant structure forcing the spanning path topology. In the general BCSF model (which does not require components to be paths), the single-component partition could use a non-path spanning tree. The backward direction is therefore valid only under the additional assumption that the spanning structure is a path, which holds when the model enforces path components or when the graph structure leaves no alternative.
````


=== Overhead

````
**Symbols:**
- n = `num_vertices` of source HamiltonianCircuit
- m = `num_edges` of source HamiltonianCircuit

| Target metric (getter) | Expression |
|------------------------|------------|
| `num_vertices`         | `num_vertices + 2` |
| `num_edges`            | `num_edges + 2` |
| `max_components`       | `1` |
| `max_weight`           | `num_vertices + 2` |

**Derivation:** Two pendant vertices s and t are added, each contributing one new edge. max_components = 1 forces a single connected component. max_weight = n + 2 because all n + 2 vertices have unit weight and must all belong to the single component.
````


=== Correctness

````
- Closed-loop test: construct a graph G known to have a Hamiltonian circuit; pick any edge {u, v}; add pendant vertices s (adjacent to u) and t (adjacent to v); reduce to BCSF with unit weights, max_components = 1, max_weight = n + 2; solve the target; verify all vertices are in one connected component; confirm removing s, t yields a Hamiltonian path from u to v in G; since {u, v} is in E(G), close to a Hamiltonian circuit.
- Negative test: construct a graph known to have no Hamiltonian circuit (e.g., Petersen graph); verify the constructed BCSF instance is also a NO instance.
- Pendant-degree check: verify s and t each have degree exactly 1 in G'.
- Parameter verification: check max_components = 1 and max_weight = n + 2.
````


=== Example

````
**Source instance (HamiltonianCircuit):**
Graph G with 7 vertices {0, 1, 2, 3, 4, 5, 6} and 10 edges:
- Edges: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {5,6}, {6,0}, {0,3}, {1,4}, {2,5}
- Hamiltonian circuit exists: 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 0
  - Check: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {5,6}, {6,0} -- all edges present.

**Construction:**
- Pick edge {u, v} = {6, 0} in E(G).
- Add pendant vertex s (vertex 7) connected only to vertex 6, and pendant vertex t (vertex 8) connected only to vertex 0.
- G' has 9 vertices {0, ..., 8} and 12 edges (original 10 plus {7, 6} and {8, 0}).
- All weights = 1, max_components = 1, max_weight = 9.

**Solution mapping:**
- Remove edge {6, 0} from the Hamiltonian circuit to get path 0-1-2-3-4-5-6 in G.
- Extend to path 8-0-1-2-3-4-5-6-7 in G'.
- Partition: all 9 vertices in component 0. Weight = 9 = max_weight, components = 1 = max_components.
- Reverse: single connected component spans all vertices. Since s=7 connects only to 6 and t=8 connects only to 0, the spanning structure runs from s through G to t. Removing s, t gives a Hamiltonian path 0-1-2-3-4-5-6 in G. Since {6, 0} is in E(G), close to circuit 0-1-2-3-4-5-6-0.
````


#pagebreak()


= Hamiltonian Path


== Hamiltonian Path $arrow.r$ Consecutive Block Minimization #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#435)]


=== Reference

````
> [SR17] CONSECUTIVE BLOCK MINIMIZATION
> INSTANCE: An m x n matrix A of 0's and 1's and a positive integer K.
> QUESTION: Is there a permutation of the columns of A that results in a matrix B having at most K blocks of consecutive 1's, i.e., having at most K entries b_{ij} such that b_{ij} = 1 and either b_{i,j+1} = 0 or j = n?
> Reference: [Kou, 1977]. Transformation from HAMILTONIAN PATH.
> Comment: Remains NP-complete if "j = n" is replaced by "j = n and b_{i,1} = 0" [Booth, 1975]. If K equals the number of rows of A that are not all 0, then these problems are equivalent to testing A for the consecutive ones property or the circular ones property, respectively, and can be solved in polynomial time.
````


#theorem[
  Hamiltonian Path polynomial-time reduces to Consecutive Block Minimization.
]


=== Construction

````


**Summary:**
Given a HAMILTONIAN PATH instance G = (V, E) with n = |V| vertices, construct a CONSECUTIVE BLOCK MINIMIZATION instance as follows:

1. **Matrix construction:** Construct the n x n adjacency matrix A of G. That is, A[i][j] = 1 if {v_i, v_j} is an edge in E, and A[i][j] = 0 otherwise (with A[i][i] = 0 since there are no self-loops).

2. **Bound:** Set K = n (one block of consecutive 1's per row).

3. **Intuition:** A column permutation of the adjacency matrix corresponds to a reordering of the vertices. If the permutation corresponds to a Hamiltonian path v_{pi(1)}, v_{pi(2)}, ..., v_{pi(n)}, then in the reordered matrix, vertex v_{pi(i)} is adjacent to v_{pi(i-1)} and v_{pi(i+1)} (its neighbors on the path). The 1's in each row of the permuted adjacency matrix will be consecutive if and only if the vertex's neighbors form a contiguous block in the ordering -- which is exactly what happens along a Hamiltonian path (each vertex has at most 2 neighbors on the path, which are adjacent in the ordering).

4. **Correctness (forward):** If G has a Hamiltonian path pi, then permuting columns (and rows) by pi produces a band matrix where each row has exactly one block of consecutive 1's. For interior path vertices, the two neighbors are adjacent in the ordering, giving a single block of 2. For endpoints, a single block of 1. Total blocks = n. So K = n suffices.

5. **Correctness (reverse):** If the columns of A can be permuted to yield at most K = n blocks, then every non-zero row has exactly one block of consecutive 1's. This means the column ordering defines a vertex arrangement where each vertex's neighbors are contiguous. In a graph with maximum degree d, this forces a path-like structure. For general graphs, having exactly n blocks (one per non-zero row) means the ordering has the consecutive ones property, which implies the ordering is a Hamiltonian path.

**Note:** The exact construction in Kou (1977) may involve a modified matrix (e.g., the edge-vertex incidence matrix or a matrix with additional indicator rows). The adjacency matrix approach captures the essential idea, but the precise bound K and correctness argument may differ slightly in the original paper.

**Time complexity of reduction:** O(n^2) to construct the adjacency matrix.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source HamiltonianPath instance (|V|)
- m = `num_edges` of source HamiltonianPath instance (|E|)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_rows` | `num_vertices` |
| `num_cols` | `num_vertices` |
| `bound` | `num_vertices` |

**Derivation:** The adjacency matrix is n x n. The bound K = n means each row gets at most one block of consecutive 1's.
````


=== Correctness

````


- Closed-loop test: reduce a HamiltonianPath instance to ConsecutiveBlockMinimization, solve target with BruteForce (try all column permutations), extract solution, verify on source by checking the column ordering is a Hamiltonian path.
- Test with known YES instance: path graph P_6 has a Hamiltonian path (the identity ordering). The adjacency matrix already has C1P in identity order.
- Test with known NO instance: K_4 union two isolated vertices -- no Hamiltonian path exists, so no column permutation achieves K = 6 blocks.
- Verify the block count matches expectations for small graphs.
````


=== Example

````


**Source instance (HamiltonianPath):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 8 edges:
- Edges: {0,1}, {0,2}, {1,3}, {2,3}, {2,4}, {3,5}, {4,5}, {1,4}
- Hamiltonian path exists: 0 -> 1 -> 3 -> 2 -> 4 -> 5

**Constructed target instance (ConsecutiveBlockMinimization):**
Matrix A (6 x 6 adjacency matrix):
---
       v0 v1 v2 v3 v4 v5
v0:  [  0, 1, 1, 0, 0, 0 ]
v1:  [  1, 0, 0, 1, 1, 0 ]
v2:  [  1, 0, 0, 1, 1, 0 ]
v3:  [  0, 1, 1, 0, 0, 1 ]
v4:  [  0, 1, 1, 0, 0, 1 ]
v5:  [  0, 0, 0, 1, 1, 0 ]
---
Bound K = 6

**Solution mapping:**
Column permutation corresponding to path 0 -> 1 -> 3 -> 2 -> 4 -> 5:
Reorder columns as (v0, v1, v3, v2, v4, v5):
---
       v0 v1 v3 v2 v4 v5
v0:  [  0, 1, 0, 1, 0, 0 ]  -> 1's at cols 1,3: NOT consecutive (gap). 2 blocks.
---

Hmm, let us reconsider. The adjacency matrix approach: row for v0 has neighbors {v1, v2}. In the path ordering (0,1,3,2,4,5), v1 is at position 1 and v2 is at position 3. These are not consecutive. So the simple adjacency matrix approach may not work directly.

Let us use the **edge-vertex incidence matrix** instead (m x n):

Incidence matrix (8 x 6):
---
       v0 v1 v2 v3 v4 v5
e01: [  1, 1, 0, 0, 0, 0 ]
e02: [  1, 0, 1, 0, 0, 0 ]
e13: [  0, 1, 0, 1, 0, 0 ]
e23: [  0, 0, 1, 1, 0, 0 ]
e24: [  0, 0, 1, 0, 1, 0 ]
e35: [  0, 0, 0, 1, 0, 1 ]
e45: [  0, 0, 0, 0, 1, 1 ]
e14: [  0, 1, 0, 0, 1, 0 ]
---
K = 8 (one block per row = one block per edge)

Column permutation (0, 1, 3, 2, 4, 5):
---
       v0 v1 v3 v2 v4 v5
e01: [  1, 1, 0, 0, 0, 0 ]  -> 1 block
e02: [  1, 0, 0, 1, 0, 0 ]  -> 2 blocks (gap at v1,v3)
---

This also has issues. The correct Kou reduction likely uses a different encoding. Let us instead present a simpler verified example:

**Simplified source instance (HamiltonianPath):**
Graph G with 6 vertices, path graph P_6:
- Vertices: {0, 1, 2, 3, 4, 5}
- Edges: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}
- Hamiltonian path: 0 -> 1 -> 2 -> 3 -> 4 -> 5

**Adjacency matrix A (6 x 6):**
---
       v0 v1 v2 v3 v4 v5

...(truncated)
````


#pagebreak()


== Hamiltonian Path $arrow.r$ Consecutive Sets #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#436)]


=== Reference

````
> [SR18] CONSECUTIVE SETS
> INSTANCE: Finite alphabet Sigma, collection C = {Sigma_1, Sigma_2, ..., Sigma_n} of subsets of Sigma, and a positive integer K.
> QUESTION: Is there a string w in Sigma* with |w|  Reference: [Kou, 1977]. Transformation from HAMILTONIAN PATH.
> Comment: The variant in which we ask only that the elements of each Sigma_i occur in a consecutive block of |Sigma_i| symbols of the string ww (i.e., we allow blocks that circulate from the end of w back to its beginning) is also NP-complete [Booth, 1975]. If K is the number of distinct symbols in the Sigma_i, then these problems are equivalent to determining whether a matrix has the consecutive ones property or the circular ones property and are solvable in polynomial time.
````


#theorem[
  Hamiltonian Path polynomial-time reduces to Consecutive Sets.
]


=== Construction

````


**Summary:**
Given a HAMILTONIAN PATH instance G = (V, E) with n = |V| vertices, construct a CONSECUTIVE SETS instance as follows:

1. **Alphabet:** Set Sigma = V (each vertex is a symbol in the alphabet), so |Sigma| = n.

2. **Subsets:** For each vertex v_i in V, define the closed neighborhood:
   Sigma_i = {v_i} union {v_j : {v_i, v_j} in E}
   This is the set containing v_i and all its neighbors. The collection C = {Sigma_1, Sigma_2, ..., Sigma_n}.

3. **Bound:** Set K = n (the string w must be a permutation of all vertices).

4. **Intuition:** A string w of length K = n using all n symbols (a permutation) corresponds to a vertex ordering. Requiring that each Sigma_i (closed neighborhood of v_i) forms a consecutive block of |Sigma_i| symbols means that v_i and all its neighbors must appear contiguously in the ordering. This is precisely the condition for a Hamiltonian path: each vertex and its path-neighbors form a contiguous block.

5. **Correctness (forward):** If G has a Hamiltonian path pi = v_{pi(1)}, v_{pi(2)}, ..., v_{pi(n)}, consider w = v_{pi(1)} v_{pi(2)} ... v_{pi(n)}. For each vertex v_i on the path, its neighbors on the path are exactly the vertices immediately before and after it in the ordering. Its closed neighborhood {v_i} union {path-neighbors} is a contiguous block of consecutive symbols in w. Any non-path edges only add vertices to Sigma_i that are already nearby (but the key is that the path-neighbors are consecutive, and additional edges don't break the consecutiveness of the block if we include v_i itself).

6. **Correctness (reverse):** If there exists w with |w| <= n where each closed neighborhood is consecutive, then w is a permutation of V (since K = n = |Sigma|). The consecutiveness of closed neighborhoods forces the ordering to be a Hamiltonian path.

**Note:** The exact construction in Kou (1977) may use open neighborhoods or a modified definition. The reduction from HAMILTONIAN PATH to CONSECUTIVE SETS is analogous to the reduction to CONSECUTIVE BLOCK MINIMIZATION, translated from a matrix setting to a string/set setting.

**Time complexity of reduction:** O(n + m) where m = |E|, to construct the neighborhoods.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source HamiltonianPath instance (|V|)
- m = `num_edges` of source HamiltonianPath instance (|E|)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `alphabet_size` | `num_vertices` |
| `num_subsets` | `num_vertices` |
| `total_subset_size` | `2 * num_edges + num_vertices` |
| `bound` | `num_vertices` |

**Derivation:** The alphabet has n symbols (one per vertex). There are n subsets (one closed neighborhood per vertex). Each edge contributes to two neighborhoods, and each vertex adds itself, so total subset size is 2m + n. The bound K = n.
````


=== Correctness

````


- Closed-loop test: reduce a HamiltonianPath instance to ConsecutiveSets, solve target with BruteForce (try all permutations of the alphabet as strings), extract solution, verify on source.
- Test with path graph P_6: Hamiltonian path is the identity ordering. Each closed neighborhood is contiguous. String "012345" works with K = 6.
- Test with K_4 + 2 isolated vertices: no Hamiltonian path. Verify no valid string of length 6 exists.
- Verify edge cases: star graph (has HP but with specific ordering constraints), cycle graph (has HP).
````


=== Example

````


**Source instance (HamiltonianPath):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 7 edges:
- Edges: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {1,4}, {2,5}
- Hamiltonian path: 0 -> 1 -> 4 -> 3 -> 2 -> 5 (check: {0,1}Y, {1,4}Y, {4,3}Y, {3,2}Y, {2,5}Y)

**Constructed target instance (ConsecutiveSets):**
Alphabet: Sigma = {0, 1, 2, 3, 4, 5}
Subsets (closed neighborhoods):
- Sigma_0 = {0, 1} (vertex 0: neighbors = {1})
- Sigma_1 = {0, 1, 2, 4} (vertex 1: neighbors = {0, 2, 4})
- Sigma_2 = {1, 2, 3, 5} (vertex 2: neighbors = {1, 3, 5})
- Sigma_3 = {2, 3, 4} (vertex 3: neighbors = {2, 4})
- Sigma_4 = {1, 3, 4, 5} (vertex 4: neighbors = {3, 5, 1})
- Sigma_5 = {2, 4, 5} (vertex 5: neighbors = {4, 2})
Bound K = 6

**Solution mapping:**
String w = "014325" (from Hamiltonian path 0 -> 1 -> 4 -> 3 -> 2 -> 5):
- Sigma_0 = {0, 1}: positions 0,1 -> consecutive. YES.
- Sigma_1 = {0, 1, 2, 4}: positions 0,1,4,2. Need block of 4: positions 0-3 = {0,1,4,3}. But Sigma_1 = {0,1,2,4}. Position of 2 is 4, outside 0-3. NOT consecutive.

Let us recheck the path. Try path 0 -> 1 -> 2 -> 3 -> 4 -> 5 (uses edges {0,1},{1,2},{2,3},{3,4},{4,5}, all present):
String w = "012345":
- Sigma_0 = {0, 1}: positions 0,1 -> block of 2. YES.
- Sigma_1 = {0, 1, 2, 4}: positions 0,1,2,4 -> NOT consecutive (gap at 3).

The issue is that non-path edges (like {1,4}) enlarge the closed neighborhood, breaking consecutiveness. This suggests the reduction uses **open neighborhoods** or **edge-based subsets** rather than closed neighborhoods. Let us use edges as subsets instead:

**Alternative construction using edge subsets:**
Subsets (one per edge, each being the pair of endpoints):
- Sigma_{01} = {0, 1}
- Sigma_{12} = {1, 2}
- Sigma_{23} = {2, 3}
- Sigma_{34} = {3, 4}
- Sigma_{45} = {4, 5}
- Sigma_{14} = {1, 4}
- Sigma_{25} = {2, 5}
K = 6

String w = "014325":
- {0,1}: positions 0,1 -> consecutive. YES.
- {1,2}: positions 1,4 -> NOT consecutive.

This also has issues for non-path edges. The correct Kou constructio
...(truncated)
````


#pagebreak()


= HamiltonianPath


== HamiltonianPath $arrow.r$ IsomorphicSpanningTree #text(size: 8pt, fill: orange)[ \[Blocked\] ] #text(size: 8pt, fill: gray)[(\#912)]


=== Reference

````
> [ND8] ISOMORPHIC SPANNING TREE
> INSTANCE: Graph G=(V,E), tree T=(V_T,E_T).
> QUESTION: Does G contain a spanning tree isomorphic to T?
> Reference: Transformation from HAMILTONIAN PATH.
> Comment: Remains NP-complete even if (a) T is a path, (b) T is a full binary tree [Papadimitriou and Yannakakis, 1978], or if (c) T is a 3-star (that is, V_T={v_0} union {u_i,v_i,w_i: 1<=i<=n}, E_T={{v_0,u_i},{u_i,v_i},{v_i,w_i}: 1<=i<=n}) [Garey and Johnson, ----]. Solvable in polynomial time by graph matching if G is a 2-star.
````


#theorem[
  HamiltonianPath polynomial-time reduces to IsomorphicSpanningTree.
]


=== Construction

````


Given a HAMILTONIAN PATH instance G = (V, E) with n = |V| vertices:

1. **Graph preservation:** Keep G = (V, E) unchanged as the host graph.
2. **Tree construction:** Set T = P_n, the path graph on n vertices. T = ({t_0, ..., t_{n-1}}, {{t_i, t_{i+1}} : 0  V(G) mapping the path tree to a spanning subgraph of G gives the Hamiltonian path as phi(t_0), phi(t_1), ..., phi(t_{n-1}).

**Correctness:**
- (Forward) A Hamiltonian path v_0, v_1, ..., v_{n-1} in G is a spanning tree isomorphic to P_n.
- (Backward) A spanning tree of G isomorphic to P_n has maximum degree 2 and is connected, hence is a Hamiltonian path.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` (host graph) | `num_vertices` |
| `num_edges` (host graph) | `num_edges` |
| `tree_vertices` | `num_vertices` |
| `tree_edges` | `num_vertices - 1` |

**Derivation:** Host graph is unchanged. Target tree P_n has n vertices and n-1 edges.
````


=== Correctness

````

- Closed-loop test: construct graph G, reduce to (G, P_n), solve with BruteForce, extract Hamiltonian path from the isomorphism, verify all vertices visited exactly once using only edges of G.
- Negative test: use a graph with no Hamiltonian path (e.g., Petersen graph), verify no spanning tree isomorphic to P_n exists.
- Identity check: host graph in target instance is identical to source graph.
````


=== Example

````


**Source instance (HamiltonianPath):**
Graph G with 5 vertices {0, 1, 2, 3, 4} and 6 edges:
- Edges: {0,1}, {0,2}, {1,2}, {1,3}, {2,4}, {3,4}
- Hamiltonian path exists: 0 -- 1 -- 3 -- 4 -- 2 (check: {0,1} yes, {1,3} yes, {3,4} yes, {4,2} yes)

**Constructed target instance (IsomorphicSpanningTree):**
- Host graph: G (unchanged)
- Target tree: T = P_5 with vertices {t_0, t_1, t_2, t_3, t_4} and edges {t_0,t_1}, {t_1,t_2}, {t_2,t_3}, {t_3,t_4}

**Solution mapping:**
- Spanning tree of G isomorphic to P_5: edges {0,1}, {1,3}, {3,4}, {4,2}
- Isomorphism: 0->t_0, 1->t_1, 3->t_2, 4->t_3, 2->t_4
- Extracted Hamiltonian path: 0 -- 1 -- 3 -- 4 -- 2
````


#pagebreak()


= KSatisfiability


== KSatisfiability $arrow.r$ MaxCut #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#166)]


#theorem[
  KSatisfiability polynomial-time reduces to MaxCut.
]


=== Construction

````
Given a NAE-3SAT instance with $n$ variables $x_1, \ldots, x_n$ and $m$ clauses $C_1, \ldots, C_m$ (each clause has exactly 3 literals; for each clause, not all literals may be simultaneously true and not all simultaneously false):

**Notation:**
- $n$ = `num_vars`, $m$ = `num_clauses`
- For variable $x_i$, create two vertices: $v_i$ (positive literal) and $v_i'$ (negative literal)
- Forcing weight $M = 2m + 1$

**Variable gadgets:**
1. For each variable $x_i$, create vertices $v_i$ and $v_i'$.
2. Add edge $(v_i, v_i')$ with weight $M$.

Since $M = 2m+1 > 2m$ equals the maximum possible total clause contribution (at most 2 per clause), the optimal cut always cuts every variable-gadget edge. This forces $v_i$ and $v_i'$ to opposite sides. The side containing $v_i$ encodes $x_i = \text{true}$.

**Clause gadgets:**
3. For each clause $C_j = (\ell_a, \ell_b, \ell_c)$:
   - Add a triangle of weight-1 edges: $(\ell_a, \ell_b)$, $(\ell_b, \ell_c)$, $(\ell_a, \ell_c)$.

**Why NAE is essential:**  
For a NAE clause, the induced partition has 1 literal on one side and 2 on the other (or vice versa). A triangle with exactly $1+2$ split has exactly **2** edges crossing the cut. A triangle with all 3 on the same side contributes **0** — but the NAE constraint forbids this. Without NAE (standard 3-SAT), a clause with all literals true places all 3 literal-vertices on the same side, contributing 0 — identical to the unsatisfied case. The triangle gadget cannot distinguish the two, breaking the reduction. NAE exactly avoids this degenerate case.

**Cut threshold:**
4. The instance is NAE-satisfiable if and only if the maximum weighted cut $\geq n \cdot M + 2m$.
   - Satisfiable: every clause contributes exactly 2 → total = $nM + 2m$.
   - Unsatisfiable: every truth assignment has at least one clause with all literals equal (contributing 0) → total clause contribution $\leq 2(m-1)$ → cut $\leq nM + 2m - 2 < nM + 2m$.

**Solution extraction:** For variable $x_i$, if $v_i \in S$, set $x_i = \text{true}$; otherwise $\text{false}$.
````


=== Overhead

````
| Target metric (code name) | Formula |
|----------------------------|---------|
| `num_vertices` | $2n$ = `2 * num_vars` |
| `num_edges` | $n + 3m$ = `num_vars + 3 * num_clauses` |

(Clause triangle edges connect literal-vertices of distinct variables within a clause; they are distinct from variable-gadget edges, which connect $v_i$ to $v_i'$. If a triangle edge happens to connect a complementary pair from the same variable — only possible when a clause contains both $x_i$ and $\neg x_i$ — that edge coincides with a variable-gadget edge and its weight accumulates. The formula `num_vars + 3 * num_clauses` is therefore a worst-case upper bound on distinct edges.)
````


=== Correctness

````
- Construct small NAE-3SAT instances where no clause contains both $x_i$ and $\neg x_i$ (so no edge merging occurs), reduce to MaxCut, solve both with BruteForce.
- Verify: satisfying assignment maps to cut $= nM + 2m$.
- Verify: unsatisfiable instance has maximum cut $< nM + 2m$.
- Test both satisfiable (e.g., a colorable graph encoded as NAE-3SAT) and unsatisfiable instances.
````


=== Example

````
**Source:** NAE-3SAT with $n=3$, $m=2$, $M = 2(2)+1 = 5$
- Variables: $x_1, x_2, x_3$
- $C_1 = (x_1, x_2, x_3)$ (NAE: not all equal)
- $C_2 = (\neg x_1, \neg x_2, \neg x_3)$ (NAE: not all equal)

**Reduction:**
- Vertices: $v_1, v_1', v_2, v_2', v_3, v_3'$ (6 = $2n$ ✓)
- Variable-gadget edges: $(v_1,v_1')$ w=5, $(v_2,v_2')$ w=5, $(v_3,v_3')$ w=5
- $C_1$ triangle: $(v_1,v_2)$ w=1, $(v_2,v_3)$ w=1, $(v_1,v_3)$ w=1
- $C_2$ triangle: $(v_1',v_2')$ w=1, $(v_2',v_3')$ w=1, $(v_1',v_3')$ w=1
- Total edges: 9 = $n + 3m = 3 + 6$ ✓ (no merges — clause edges connect distinct-variable literal pairs)

**Satisfying assignment:** $x_1=T, x_2=F, x_3=F$
- Partition: $S=\{v_1, v_2', v_3'\}$, $\bar S=\{v_1', v_2, v_3\}$
- Variable-gadget cut: all 3 edges cross → $3 \times 5 = 15$
- $C_1$ triangle: $(v_1, v_2)$ crosses ($v_1\in S, v_2\in\bar S$), $(v_1,v_3)$ crosses ($v_1\in S, v_3\in\bar S$), $(v_2,v_3)$ does not ($v_2,v_3\in\bar S$) → 2 edges cut ✓
- $C_2$ triangle: $(v_1',v_2')$ crosses ($v_1'\in\bar S, v_2'\in S$), $(v_1',v_3')$ crosses ($v_1'\in\bar S, v_3'\in S$), $(v_2',v_3')$ does not ($v_2',v_3'\in S$) → 2 edges cut ✓
- **Total cut = 15 + 2 + 2 = 19**
- **Threshold = $nM + 2m = 3(5) + 2(2) = 19$** ✓

**Unsatisfying assignment:** $x_1=T, x_2=T, x_3=T$ (fails $C_1$: all true)
- Partition: $S=\{v_1,v_2,v_3\}$, $\bar S=\{v_1',v_2',v_3'\}$
- Variable-gadget cut: $15$
- $C_1$ triangle: all of $v_1,v_2,v_3\in S$ → 0 edges cut
- $C_2$ triangle: all of $v_1',v_2',v_3'\in\bar S$ → 0 edges cut
- **Total cut = 15 < 19 = threshold** ✓
````


#pagebreak()


= MAX CUT


== MAX CUT $arrow.r$ OPTIMAL LINEAR ARRANGEMENT #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#890)]


=== Reference

````
> GT42 OPTIMAL LINEAR ARRANGEMENT
> INSTANCE: Graph G = (V,E), positive integer K.
> QUESTION: Is there a one-to-one function f: V → {1, 2, ..., |V|} such that Σ_{{u,v}∈E} |f(u) - f(v)| ≤ K?
> Reference: [Garey, Johnson, and Stockmeyer, 1976]. NP-complete even for bipartite graphs. Solvable in polynomial time for trees [Adolphson and Hu, 1973], [Chung, 1984]. Transformation from SIMPLE MAX CUT.
````


#theorem[
  MAX CUT polynomial-time reduces to OPTIMAL LINEAR ARRANGEMENT.
]


=== Construction

````

**Summary:**
Given a MaxCut instance (G = (V, E), K) asking whether there is a partition (S, V\S) with at least K edges crossing the cut, construct an OptimalLinearArrangement instance (G', K') as follows:

1. **Graph construction:** The construction uses a gadget-based approach. The key insight is that in a linear arrangement, edges crossing a "cut" at position i (i.e., one endpoint in positions {1,...,i} and the other in {i+1,...,n}) contribute at least 1 to the total stretch. By designing the graph so that edges in the arrangement correspond to cut edges, we can relate the arrangement cost to the cut size.

2. **Bound transformation:** The bound K' is set as a function of |E|, |V|, and K, specifically K' = |E| · (some function) - K · (some correction), so that achieving arrangement cost ≤ K' requires at least K edges to be "short" (crossing nearby positions), which corresponds to at least K edges crossing a cut in the original graph.



3. **Forward direction:** A cut of size ≥ K in G can be used to construct a linear arrangement of G' with cost ≤ K'.

4. **Reverse direction:** A linear arrangement with cost ≤ K' implies a cut of size ≥ K.
````


=== Overhead

````

| Target metric | Polynomial |
|---|---|
| `num_vertices` | TBD — depends on exact construction |
| `num_edges` | TBD — depends on exact construction |

**Note:** The exact overhead depends on the construction in [Garey, Johnson, Stockmeyer 1976]. If the reduction passes the graph through directly (as in some formulations where the decision threshold is transformed), then `num_vertices = num_vertices` and `num_edges = num_edges`, with only the bound K' changing.
````


=== Correctness

````

- Closed-loop test: construct a small MaxCut instance (e.g., a cycle C₅ with known max cut of 4), reduce to OLA, solve with BruteForce, verify the OLA solution exists iff the max cut meets the threshold.
- Verify that bipartite graph instances (where MaxCut = |E|) produce OLA instances with correspondingly tight bounds.
- Test with a complete graph K₄ (max cut = 4 for partition into two pairs) and verify the OLA bound.
````


=== Example

````


**Source instance (MaxCut):**
Graph G with 4 vertices {0, 1, 2, 3} forming a cycle C₄:
- Edges: {0,1}, {1,2}, {2,3}, {0,3}
- K = 4 (maximum cut: partition {0,2} vs {1,3} cuts all 4 edges)

**Constructed target instance (OptimalLinearArrangement):**

- G' = G (if direct graph transfer), K' derived from the formula in the original reduction.
- The arrangement f: 0→1, 2→2, 1→3, 3→4 gives cost |1-3| + |3-2| + |2-4| + |1-4| = 2+1+2+3 = 8.

**Solution mapping:** The linear arrangement induces a cut at each position; the partition achieving max cut corresponds to the arrangement that minimizes total stretch.
````


#pagebreak()


= MINIMUM MAXIMAL MATCHING


== MINIMUM MAXIMAL MATCHING $arrow.r$ MaximumAchromaticNumber #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#846)]


=== Reference

````
> [GT5] ACHROMATIC NUMBER
> INSTANCE: Graph G = (V,E), positive integer K ≤ |V|.
> QUESTION: Does G have achromatic number K or greater, i.e., is there a partition of V into disjoint sets V_1, V_2, . . . , V_k, k ≥ K, such that each V_i is an independent set for G (no two vertices in V_i are joined by an edge in E) and such that, for each pair of distinct sets V_i, V_j, V_i ∪ V_j is not an independent set for G?
> Reference: [Yannakakis and Gavril, 1978]. Transformation from MINIMUM MAXIMAL MATCHING.
> Comment: Remains NP-complete even if G is the complement of a bipartite graph and hence has no independent set of more than two vertices.
````


#theorem[
  MINIMUM MAXIMAL MATCHING polynomial-time reduces to MaximumAchromaticNumber.
]


=== Construction

````


Given a Minimum Maximal Matching instance (G = (V,E), K):

1. **Construct the complement line graph:** Form the line graph L(G) of G (vertices of L(G) are edges of G; two vertices in L(G) are adjacent iff the corresponding edges share an endpoint). Then take the complement graph H = complement(L(G)).

2. **Set the target parameter:** Set K' = |E| − K as the target achromatic number.

3. **Equivalence:** A maximal matching of size ≤ K in G corresponds to a complete proper coloring of H with ≥ K' colors. The maximal matching condition (every unmatched edge is adjacent to a matched edge) translates to the completeness condition (every pair of color classes has an edge between them in H).

**Key idea:** In the complement of the line graph, edges of G that share an endpoint become non-adjacent. Independent sets in H correspond to sets of edges in G that mutually share endpoints — i.e., stars. The completeness condition on the coloring ensures that the uncolored/merged parts form a dominating structure.
````


=== Overhead

````

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | |E| (vertices of complement line graph) |
| `num_edges` | O(|E|^2) (complement of line graph) |
| `num_colors` | |E| − K |
````


=== Correctness

````

Given a solution (complete proper K'-coloring of H), extract the corresponding edge partition of G. Verify that the matching edges (one color class per matched edge) form a maximal matching of size ≤ K in the original graph G.
````


=== Example

````

**Source:** Path graph P4: v0 — v1 — v2 — v3, with edges e1=(v0,v1), e2=(v1,v2), e3=(v2,v3). K = 1 (is there a maximal matching of size ≤ 1?).

The line graph L(G) has vertices {e1, e2, e3} with edges {(e1,e2), (e2,e3)} (adjacent edges in G). The complement H has vertices {e1, e2, e3} with edges {(e1,e3)} only.

Target: achromatic number of H ≥ K' = 3 − 1 = 2. In H, coloring e1→0, e2→1, e3→0 is proper (e1 and e3 are adjacent in H, but they have different... wait, e1 and e3 are adjacent in H, both colored 0 — invalid). Coloring e1→0, e2→1, e3→1: e2 and e3 both colored 1 but not adjacent in H — valid proper coloring. Colors 0 and 1 appear on edge (e1,e3)? e1 is 0, e3 is 1 — yes, complete. Achromatic number ≥ 2.

This corresponds to matching {e2} = {(v1,v2)} of size 1 in G, which is indeed maximal since e1 shares v1 with e2 and e3 shares v2 with e2.
````


#pagebreak()


== MINIMUM MAXIMAL MATCHING $arrow.r$ MinimumMatrixDomination #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#847)]


=== Reference

````
> [MS12]  MATRIX DOMINATION
> INSTANCE:  An n×n matrix M with entries from {0,1}, and a positive integer K.
> QUESTION:  Is there a set of K or fewer non-zero entries in M that dominate all others, i.e., s subset C ⊆ {1,2,...,n}×{1,2,...,n} with |C| ≤ K such that Mij = 1 for all (i,j) ∈ C and such that, whenever Mij = 1, there exists an (i',j') ∈ C for which either i = i' or j = j'?
> Reference:  [Yannakakis and Gavril, 1978]. Transformation from MINIMUM MAXIMAL MATCHING.
> Comment:  Remains NP-complete even if M is upper triangular.
````


#theorem[
  MINIMUM MAXIMAL MATCHING polynomial-time reduces to MinimumMatrixDomination.
]


=== Construction

````


Given a Minimum Maximal Matching instance (G = (V,E), K):

1. **Construct the matrix:** Let n = |V|. Build the n×n adjacency matrix M of G, where M_ij = 1 if and only if (v_i, v_j) ∈ E, and M_ij = 0 otherwise. (For an undirected graph, M is symmetric.)

2. **Set the target parameter:** Set the bound K' = K (same parameter).

3. **Equivalence:** A maximal matching of size ≤ K in G corresponds to a dominating set of ≤ K non-zero entries in M. Each matched edge (v_i, v_j) maps to selecting entry (i,j) in M. The maximal matching condition — every unmatched edge shares an endpoint with a matched edge — translates directly to the matrix domination condition: every 1-entry (i,j) not in C shares a row (i = i') or column (j = j') with some selected entry (i',j') in C.

**Note:** For the upper-triangular variant (which G&J notes is also NP-complete), one can use only the upper triangle of the adjacency matrix, selecting entry (i,j) with i < j for each edge.
````


=== Overhead

````

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `matrix_size` | |V| × |V| (adjacency matrix) |
| `num_ones` | 2 × |E| (symmetric matrix, two entries per edge) |
| `bound` | K (unchanged) |
````


=== Correctness

````

Given a dominating set C of entries in M, extract the corresponding edges in G. Verify that: (1) no two selected edges share an endpoint (matching condition), (2) every non-selected edge shares an endpoint with a selected edge (maximality condition), and (3) |C| ≤ K. Note that because M is symmetric, selecting entry (i,j) and (j,i) both represent the same edge — the solution extraction should account for this by either using the upper-triangular representation or deduplicating.
````


=== Example

````

**Source:** Path graph P4: v0 — v1 — v2 — v3, with edges {(v0,v1), (v1,v2), (v2,v3)}. K = 1 (is there a maximal matching of size ≤ 1?).

**Target matrix M** (4×4 adjacency matrix):
---
     v0  v1  v2  v3
v0 [  0   1   0   0 ]
v1 [  1   0   1   0 ]
v2 [  0   1   0   1 ]
v3 [  0   0   1   0 ]
---

K' = 1. Select C = {(1,2)} (the entry for edge (v1,v2)). Check domination:
- (0,1): shares row? No. Shares column 1 with (1,2)? Yes (column index 1 matches row index 1 of selected entry) — dominated.
- (1,0): shares row 1 with (1,2) — dominated.
- (2,1): shares row 2? (1,2) is row 1. Shares column 1? (1,2) is column 2. Not dominated by (1,2) alone.

So K' = 1 does not work (as expected — the edge (v1,v2) alone is not a maximal matching since (v0,v1) shares endpoint v1 but we also need to check: actually {(v1,v2)} IS a maximal matching because every other edge shares an endpoint. Let's re-check: (v0,v1) shares v1, (v2,v3) shares v2. So K = 1 works.

For the matrix: C = {(1,2)}. Entry (2,1) shares column 1? No, column is 1 for (2,1) and column is 2 for (1,2). But (2,1) shares ROW 2? (1,2) is in row 1. Hmm — we need both (1,2) and (2,1) selected, or use the upper-triangular encoding. With C = {(1,2), (2,1)} (both entries for edge (v1,v2)), K' = 2:
- (0,1): shares column 1 with (2,1) — dominated.
- (1,0): shares row 1 with (1,2) — dominated.
- (2,3): shares row 2 with (2,1) — dominated.
- (3,2): shares column 2 with (1,2) — dominated.

All dominated with |C| = 2 ≤ K' = 2. The symmetric representation requires K' = 2K to account for both matrix entries per edge.
````


#pagebreak()


= Minimum Cardinality Key


== Minimum Cardinality Key $arrow.r$ Prime Attribute Name #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#461)]


=== Reference

````
> [SR28] PRIME ATTRIBUTE NAME
> INSTANCE: A set A of attribute names, a collection F of functional dependencies on A, and a specified name x E A.
> QUESTION: Is x a "prime attribute name" for , i.e., is there a key K for  such that x E K?
> Reference: [Lucchesi and Osborne, 1977]. Transformation from MINIMUM CARDINALITY KEY.
````


#theorem[
  Minimum Cardinality Key polynomial-time reduces to Prime Attribute Name.
]


=== Construction

````


**Summary:**
Given a Minimum Cardinality Key instance  (asking whether there exists a key of cardinality at most M), construct a Prime Attribute Name instance  as follows:

1. **Extended attribute set:** Create a new attribute x_new not in A. Set A' = A ∪ {x_new}.

2. **Extended functional dependencies:** Keep all functional dependencies from F. Add new functional dependencies that make x_new behave as a "budget counter": x_new is designed so that it participates in a key K' for  if and only if there exists a key K for  with |K|  with |K|  by combining x_new with the attributes of K (and padding with dummy attributes if needed). This key contains x_new, so x_new is a prime attribute.

6. **Correctness (reverse):** If x_new is a prime attribute for , then there exists some key K' containing x_new. By the construction of F', the non-dummy, non-x_new attributes in K' must form a key for the original , and their count is at most M (since x_new and the dummies account for the rest). Hence a key of cardinality at most M exists for .

**Time complexity of reduction:** O(|A| * M + |F|) to construct the extended attribute set and functional dependencies.
````


=== Overhead

````


**Symbols:**
- n = `num_attributes` of source Minimum Cardinality Key instance (|A|)
- f = `num_dependencies` of source instance (|F|)
- M = `budget` of source instance

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_attributes` | `num_attributes` + `budget` + 1 |
| `num_dependencies` | `num_dependencies` + O(`num_attributes` * `budget`) |

**Derivation:**
- Attributes: original n plus M dummy attributes plus 1 query attribute = n + M + 1
- Functional dependencies: original f plus new dependencies linking x_new and dummies to original attributes
- The query attribute x_new is fixed
````


=== Correctness

````


- Closed-loop test: reduce a MinimumCardinalityKey instance to PrimeAttributeName, solve by enumerating all candidate keys of the extended schema, check if x_new appears in any, extract solution, verify key cardinality bound on source
- Test with a schema having a unique small key: the corresponding x_new should be prime
- Test with a schema where the minimum key has size larger than M: x_new should NOT be prime
- Verify that dummy attributes do not create spurious keys
````


=== Example

````


**Source instance (MinimumCardinalityKey):**
Attribute set A = {a, b, c, d, e, f, g} (7 attributes)
Functional dependencies F:
- {a, b} -> {c}
- {c, d} -> {e}
- {a, d} -> {f}
- {b, e} -> {g}
- {f, g} -> {a}

Budget M = 3

Question: Is there a key of cardinality at most 3?

Analysis: Consider K = {a, b, d}:
- {a, b} -> {c} (derive c)
- {c, d} -> {e} (derive e, since c and d are known)
- {a, d} -> {f} (derive f)
- {b, e} -> {g} (derive g, since b and e are known)
- Closure of {a, b, d} = {a, b, c, d, e, f, g} = A
- K = {a, b, d} is a key of cardinality 3 = M. Answer: YES.

**Constructed target instance (PrimeAttributeName):**
Extended attribute set A' = {a, b, c, d, e, f, g, x_new, d_1, d_2, d_3} (11 attributes)

Extended functional dependencies F' = F ∪ {
- {x_new, d_1} -> {a}, {x_new, d_1} -> {b}, ..., {x_new, d_1} -> {g}  (x_new + any dummy determines all originals)
- {x_new, d_2} -> {a}, ..., {x_new, d_2} -> {g}
- {x_new, d_3} -> {a}, ..., {x_new, d_3} -> {g}
- Additional structural dependencies linking original keys to x_new
}

Query attribute: x = x_new

**Solution mapping:**
Since {a, b, d} is a key for  with |{a, b, d}| = 3 = M, we can construct a key for  that includes x_new: K' = {x_new, a, b, d}. Under the extended dependencies, K' determines all of A' (x_new and the original attributes are in K' or derivable; dummy attributes d_1, d_2, d_3 are handled by additional dependencies).

Therefore x_new is prime (it appears in key K').

**Reverse mapping:**
From the prime attribute answer YES and the key K' = {x_new, a, b, d}, extract the original attributes: {a, b, d}. This is a key for  of cardinality 3 <= M = 3.
````


#pagebreak()


= MinimumHittingSet


== MinimumHittingSet $arrow.r$ AdditionalKey #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#460)]


=== Reference

````
> [SR27] ADDITIONAL KEY
> INSTANCE: A set A of attribute names, a collection F of functional dependencies on A, a subset R ⊆ A, and a set K of keys for the relational scheme .
> QUESTION: Does R have a key not already contained in K, i.e., is there an R' ⊆ R such that R' ∉ K, (R',R) ∈ F*, and for no R'' ⊆ R' is (R'',R) ∈ F*?
> Reference: [Beeri and Bernstein, 1978]. Transformation from HITTING SET.
````


#theorem[
  MinimumHittingSet polynomial-time reduces to AdditionalKey.
]


=== Construction

````


**Summary:**
Given a Hitting Set instance (S, C, K) where S = {s_1, ..., s_n} is a universe, C = {c_1, ..., c_m} is a collection of subsets of S, and K is a positive integer, construct an Additional Key instance  as follows:

1. **Attribute set construction:** Create one attribute for each element of the universe: A = {a_{s_1}, ..., a_{s_n}} plus additional auxiliary attributes. Let R = A (the relation scheme is over all attributes).

2. **Functional dependencies:** For each subset c_j = {s_{i_1}, ..., s_{i_t}} in C, create functional dependencies that encode the covering constraint. Specifically, any subset of attributes that "hits" c_j (includes at least one a_{s_i} for s_i in c_j) can determine the auxiliary attributes associated with c_j through the functional dependency system.

3. **Known keys:** The set K_known contains all the keys already discovered. These are constructed to correspond to the subsets of S that are NOT hitting sets for C, or to known hitting sets that we want to exclude.

4. **Encoding of the hitting set condition:** The functional dependencies are designed so that a subset H ⊆ A corresponds to a key for  if and only if the corresponding elements form a hitting set for C (i.e., H intersects every c_j). The key property (H determines all of R via F*) maps to the hitting set property (H hits every subset in C).

5. **Known keys exclusion:** The set K_known is populated with known hitting sets (translated to attribute subsets), so the question "does R have an additional key not in K_known?" becomes "is there a hitting set not already in the known list?"

6. **Correctness (forward):** If there exists a hitting set H for C not corresponding to any key in K_known, then the corresponding attribute subset is a key for  not in K_known.

7. **Correctness (reverse):** If there is an additional key K' not in K_known, the corresponding universe elements form a hitting set for C not already enumerated.

**Time complexity of reduction:** O(poly(n, m, |K_known|)) to construct the attribute set, functional dependencies, and known key set.
````


=== Overhead

````


**Symbols:**
- n = `universe_size` of source Hitting Set instance (|S|)
- m = `num_sets` of source Hitting Set instance (|C|)
- k = |K_known| (number of already-known keys/hitting sets)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_attributes` | O(`universe_size` + `num_sets`) |
| `num_dependencies` | O(`universe_size` * `num_sets`) |
| `num_known_keys` | k (passed through from input) |

**Derivation:**
- Attributes: one per universe element plus auxiliary attributes for encoding subset constraints
- Functional dependencies: encode the membership relationships between universe elements and collection subsets
- Known keys: directly translated from the given set of known hitting sets
````


=== Correctness

````


- Closed-loop test: reduce a HittingSet instance to AdditionalKey, solve by brute-force enumeration of attribute subsets to find keys, check for keys not in K_known, extract solution, verify as hitting set on source
- Test with a case where exactly one hitting set exists and is already in K_known (answer: NO)
- Test with a case where multiple hitting sets exist and only some are in K_known (answer: YES)
- Verify that non-hitting-set subsets do not form keys under the constructed functional dependencies
````


=== Example

````


**Source instance (Hitting Set):**
Universe S = {s_1, s_2, s_3, s_4, s_5, s_6} (n = 6)
Collection C (6 subsets):
- c_1 = {s_1, s_2, s_3}
- c_2 = {s_2, s_4}
- c_3 = {s_3, s_5}
- c_4 = {s_4, s_5, s_6}
- c_5 = {s_1, s_6}
- c_6 = {s_2, s_5, s_6}

Known hitting sets (translated to K_known): {{s_2, s_3, s_6}, {s_2, s_5, s_1}}

Question: Is there a hitting set not in the known set?

**Constructed target instance (AdditionalKey):**
Attribute set A = {a_1, a_2, a_3, a_4, a_5, a_6, b_1, b_2, b_3, b_4, b_5, b_6}
(6 universe attributes + 6 auxiliary attributes for each subset constraint)

Functional dependencies F: for each subset c_j, the attributes corresponding to elements in c_j collectively determine auxiliary attribute b_j:
- {a_1} -> {b_1}, {a_2} -> {b_1}, {a_3} -> {b_1} (from c_1)
- {a_2} -> {b_2}, {a_4} -> {b_2} (from c_2)
- {a_3} -> {b_3}, {a_5} -> {b_3} (from c_3)
- {a_4} -> {b_4}, {a_5} -> {b_4}, {a_6} -> {b_4} (from c_4)
- {a_1} -> {b_5}, {a_6} -> {b_5} (from c_5)
- {a_2} -> {b_6}, {a_5} -> {b_6}, {a_6} -> {b_6} (from c_6)

R = A (full attribute set)
Known keys K_known = {{a_2, a_3, a_6}, {a_2, a_5, a_1}} (corresponding to known hitting sets)

**Solution mapping:**
Consider the candidate hitting set H = {s_2, s_3, s_4, s_6}:
- c_1 = {s_1, s_2, s_3}: s_2 in H
- c_2 = {s_2, s_4}: s_2, s_4 in H
- c_3 = {s_3, s_5}: s_3 in H
- c_4 = {s_4, s_5, s_6}: s_4, s_6 in H
- c_5 = {s_1, s_6}: s_6 in H
- c_6 = {s_2, s_5, s_6}: s_2, s_6 in H
All subsets are hit.

This corresponds to key K' = {a_2, a_3, a_4, a_6}, which:
- Is not in K_known (neither {a_2, a_3, a_6} nor {a_2, a_5, a_1})
- Determines all auxiliary attributes: b_1 via a_2, b_2 via a_2, b_3 via a_3, b_4 via a_4, b_5 via a_6, b_6 via a_2
- Therefore K' is a key for 

Answer: YES, there exists an additional key {a_2, a_3, a_4, a_6} not in K_known.

**Reverse mapping:**
Key {a_2, a_3, a_4, a_6} maps to hitting set {s_2, s_3, s_4, s_6}, verifying that this is a valid hitting set not in the known list.
````


#pagebreak()


== MinimumHittingSet $arrow.r$ BoyceCoddNormalFormViolation #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#462)]


=== Reference

````
> [SR29] BOYCE-CODD NORMAL FORM VIOLATION
> INSTANCE: A set A of attribute names, a collection F of functional dependencies on A, and a subset A' ⊆ A.
> QUESTION: Does A' violate Boyce-Codd normal form for the relational system , i.e., is there a subset X ⊆ A' and two attribute names y,z E A' - X such that (X,{y}) E F* and (X,{z}) ∉ F*, where F* is the closure of F?
> Reference: [Bernstein and Beeri, 1976], [Beeri and Bernstein, 1978]. Transformation from HITTING SET.
> Comment: Remains NP-complete even if A' is required to satisfy "third normal form," i.e., if X ⊆ A' is a key for the system  and if two names y,z E A'-X satisfy (X,{y}) E F* and (X,{z}) ∉ F*, then z is a prime attribute for .
````


#theorem[
  MinimumHittingSet polynomial-time reduces to BoyceCoddNormalFormViolation.
]


=== Construction

````


**Summary:**
Given a Hitting Set instance (S, C, K) where S is the universe, C = {c_1, ..., c_m} is a collection of subsets of S, and K is the budget, construct a BCNF Violation instance as follows:

1. **Attribute set construction:** Create an attribute set A that encodes the universe elements and the subsets in C. For each element s_i in S, create an attribute a_i. Additionally, create auxiliary attributes to encode the structure of C. Let |S| = n and |C| = m. The total attribute set A has O(n + m) attributes.

2. **Functional dependency construction:** Design a collection F of functional dependencies on A such that the closure F* encodes the membership relationships between elements and subsets. Specifically, for each subset c_j in C, introduce functional dependencies that relate the attributes corresponding to elements in c_j so that "hitting" c_j corresponds to a non-trivial FD holding over those attributes.

3. **Target subset construction:** Set A' to be the subset of A corresponding to the universe elements S. The BCNF condition on A' is violated if and only if there exists a subset X of A' and attributes y, z in A' - X such that X functionally determines y (via F*) but not z. This structure mirrors the hitting set condition: a "hit" of a subset c_j means selecting some element from c_j to include in the hitting set.

4. **Budget encoding:** The budget K is encoded by controlling the minimum number of elements needed to create a BCNF violation. The original hitting set has a solution of size <= K if and only if A' violates BCNF.

5. **Solution extraction:** Given a BCNF violation witness (X, y, z), extract the hitting set from the attributes in X (or from the specific violation structure). The correspondence ensures that the violation identifies exactly which elements from S are needed to "hit" all subsets in C.

**Key invariant:** The functional dependencies F are designed so that the closure F* encodes the subset-membership structure of C. A BCNF violation in A' occurs precisely when the underlying hitting set condition is satisfied.
````


=== Overhead

````


**Symbols:**
- n = `universe_size` (number of elements in S)
- m = `num_sets` (number of subsets in C)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_attributes` | `universe_size + num_sets` |
| `num_functional_deps` | `O(num_sets * max_subset_size)` |

**Derivation:**
- Attribute set: one attribute per universe element plus auxiliary attributes for encoding subset structure, giving O(n + m) attributes
- Functional dependencies: at most proportional to the total size of the collection C (sum of subset sizes)
- The target subset A' has at most n attributes (one per universe element)
````


=== Correctness

````


- Closed-loop test: reduce a HittingSet instance to BoyceCoddNormalFormViolation, solve the BCNF violation problem with BruteForce (enumerate all subsets X of A' and check the FD closure condition), extract the hitting set, verify it is a valid hitting set on the original instance
- Check that the BCNF violation exists if and only if the hitting set instance is satisfiable with budget K
- Test with a non-trivial instance where greedy element selection fails
- Verify that the functional dependency closure is correctly computed
````


=== Example

````


**Source instance (HittingSet):**
Universe S = {s_0, s_1, s_2, s_3, s_4, s_5} (6 elements)
Collection C (4 subsets):
- c_0 = {s_0, s_1, s_2}
- c_1 = {s_1, s_3, s_4}
- c_2 = {s_2, s_4, s_5}
- c_3 = {s_0, s_3, s_5}
Budget K = 2

**Constructed target instance (BoyceCoddNormalFormViolation):**
Attribute set A = {a_0, a_1, a_2, a_3, a_4, a_5, b_0, b_1, b_2, b_3} where a_i corresponds to universe element s_i and b_j is an auxiliary attribute for subset c_j.

Functional dependencies F:
- For c_0: {a_0, a_1, a_2} -> {b_0}
- For c_1: {a_1, a_3, a_4} -> {b_1}
- For c_2: {a_2, a_4, a_5} -> {b_2}
- For c_3: {a_0, a_3, a_5} -> {b_3}
- Additional FDs encoding the hitting structure

Target subset A' = {a_0, a_1, a_2, a_3, a_4, a_5}

**Solution mapping:**
- Hitting set solution: S' = {s_1, s_5} (size 2 = K):
  - c_0 = {s_0, s_1, s_2}: s_1 in S' -- hit
  - c_1 = {s_1, s_3, s_4}: s_1 in S' -- hit
  - c_2 = {s_2, s_4, s_5}: s_5 in S' -- hit
  - c_3 = {s_0, s_3, s_5}: s_5 in S' -- hit
- The corresponding BCNF violation in A' identifies a subset X and attributes y, z such that the violation encodes the choice of {s_1, s_5} as the hitting set
- All 4 subsets are hit by S' = {s_1, s_5} with |S'| = 2 <= K
````


#pagebreak()


= MinimumVertexCover


== MinimumVertexCover $arrow.r$ ShortestCommonSupersequence #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#427)]


=== Reference

````
> [SR8] SHORTEST COMMON SUPERSEQUENCE
> INSTANCE: Finite alphabet Σ, finite set R of strings from Σ*, and a positive integer K.
> QUESTION: Is there a string w ∈ Σ* with |w| ≤ K such that each string x ∈ R is a subsequence of w?
> Reference: [Maier, 1978]. Transformation from VERTEX COVER.
> Comment: Remains NP-complete even if |Σ| = 5. Solvable in polynomial time if |R| = 2 (by first computing the longest common subsequence) or if all x ∈ R have |x| ≤ 2.
````


#theorem[
  MinimumVertexCover polynomial-time reduces to ShortestCommonSupersequence.
]


=== Construction

````


**Summary:**
Given a VERTEX COVER instance G = (V, E) with V = {v_1, ..., v_n}, E = {e_1, ..., e_m}, and integer K, construct a SHORTEST COMMON SUPERSEQUENCE instance as follows (based on Maier's 1978 construction):

1. **Alphabet:** Σ = {v_1, v_2, ..., v_n} ∪ {#} where # is a separator symbol not in V. The alphabet has |V| + 1 symbols. (For the fixed-alphabet variant with |Σ| = 5, a further encoding step is applied.)

2. **String construction:** For each edge e_j = {v_a, v_b} (with a < b), create the string:
   s_j = v_a · v_b
   This string of length 2 encodes the constraint that in any supersequence, the symbols v_a and v_b must both appear (at least one needs to be "shared" across edges).

3. **Vertex-ordering string:** Create a "backbone" string:
   T = v_1 · v_2 · ... · v_n
   This ensures the supersequence respects the vertex ordering.

4. **Additional constraint strings:** For each pair of adjacent vertices in an edge, separator-delimited strings enforce that the vertex symbols appear in specific positions. The full construction uses the separator # to create blocks so that the supersequence can be divided into n blocks, where each block corresponds to a vertex. A vertex is "selected" (in the cover) if its block contains the vertex symbol plus extra copies needed by incident edges; a vertex not in the cover has its symbol appear only once.

5. **Bound:** K' = n + m - K, where n = |V|, m = |E|, K = vertex cover size bound. (The exact formula depends on the padding used in the construction.)

6. **Correctness (forward):** If G has a vertex cover S of size ≤ K, the supersequence is constructed by placing all vertex symbols in order, and for each edge e = {v_a, v_b}, the subsequence v_a · v_b is embedded by having both symbols present. Because S covers all edges, at most K vertices carry extra "load," keeping the total length within K'.

7. **Correctness (reverse):** If a supersequence w of length ≤ K' exists, the vertex symbols that appear in positions accommodating multiple edge-strings correspond to a vertex cover of G with size ≤ K.

**Key insight:** Subsequence containment allows encoding the "at least one endpoint must be selected" constraint. The supersequence must "schedule" vertex symbols so that every edge-string is a subsequence, and minimizing the supersequence length corresponds to minimizing the vertex cover.

**Time complexity of reduction:** O(n + m) to construct the instance.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source VertexCover instance (|V|)
- m = `num_edges` of source VertexCover instance (|E|)
- K = vertex cover bound

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `alphabet_size` | `num_vertices + 1` |
| `num_strings` | `num_edges + 1` |
| `max_string_length` | `num_vertices` |
| `bound_K` | `num_vertices + num_edges - cover_bound` |

**Derivation:** One symbol per vertex plus separator; one string per edge plus one backbone string; bound relates linearly to n, m, and K.
````


=== Correctness

````


- Closed-loop test: reduce a MinimumVertexCover instance to ShortestCommonSupersequence, solve target with BruteForce (enumerate candidate supersequences up to length K'), extract solution, verify on source
- Test with known YES instance: triangle graph K_3, vertex cover of size 2
- Test with known NO instance: star graph K_{1,5}, vertex cover must include center vertex
- Verify that every constructed edge-string is indeed a subsequence of the constructed supersequence
- Compare with known results from literature
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 6 vertices V = {v_1, v_2, v_3, v_4, v_5, v_6} and 7 edges:
- Edges: {v_1,v_2}, {v_1,v_3}, {v_2,v_3}, {v_3,v_4}, {v_4,v_5}, {v_4,v_6}, {v_5,v_6}
- (Triangle v_1-v_2-v_3 connected to triangle v_4-v_5-v_6 via edge {v_3,v_4})
- Vertex cover of size K = 3: {v_2, v_3, v_4} covers all edges. Check:
  - {v_1,v_2}: v_2 ✓; {v_1,v_3}: v_3 ✓; {v_2,v_3}: v_2 ✓; {v_3,v_4}: v_3 ✓; {v_4,v_5}: v_4 ✓; {v_4,v_6}: v_4 ✓; {v_5,v_6}: needs v_5 or v_6 -- FAIL.
- Correct cover of size K = 4: {v_1, v_3, v_4, v_6} covers all edges:
  - {v_1,v_2}: v_1 ✓; {v_1,v_3}: v_1 ✓; {v_2,v_3}: v_3 ✓; {v_3,v_4}: v_3 ✓; {v_4,v_5}: v_4 ✓; {v_4,v_6}: v_4 ✓; {v_5,v_6}: v_6 ✓.

**Constructed target instance (ShortestCommonSupersequence):**
- Alphabet: Σ = {v_1, v_2, v_3, v_4, v_5, v_6, #}
- Strings (one per edge): R = {v_1v_2, v_1v_3, v_2v_3, v_3v_4, v_4v_5, v_4v_6, v_5v_6}
- Backbone string: T = v_1v_2v_3v_4v_5v_6
- All strings in R must be subsequences of the supersequence w

**Solution mapping:**
- The supersequence w = v_1v_2v_3v_4v_5v_6 of length 6 already contains every 2-symbol edge-string as a subsequence (since vertex symbols appear in order). The optimal SCS length relates to how many vertex symbols can be "shared" across edges.
- The vertex cover {v_1, v_3, v_4, v_6} identifies which vertices serve as shared anchors in the supersequence.

**Verification:**
- Each edge-string v_av_b (a < b) is a subsequence of v_1v_2v_3v_4v_5v_6 ✓
- The solution length relates to the vertex cover size through the reduction formula
````


#pagebreak()


= OPTIMAL LINEAR ARRANGEMENT


== OPTIMAL LINEAR ARRANGEMENT $arrow.r$ ROOTED TREE ARRANGEMENT #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#888)]


=== Reference

````
> GT45 ROOTED TREE ARRANGEMENT
> INSTANCE: Graph G = (V,E), positive integer K.
> QUESTION: Is there a rooted tree T = (U,F) with |U| = |V| and a one-to-one function f: V → U such that, for every edge {u,v} ∈ E, the unique path in T from the root to some vertex of U contains both f(u) and f(v), and such that Σ_{{u,v}∈E} d_T(f(u), f(v)) ≤ K, where d_T denotes distance in the tree T?
> Reference: [Gavril, 1977a]. Transformation from OPTIMAL LINEAR ARRANGEMENT.
````


=== GJ Source Entry

````
> GT45 ROOTED TREE ARRANGEMENT
> INSTANCE: Graph G = (V,E), positive integer K.
> QUESTION: Is there a rooted tree T = (U,F) with |U| = |V| and a one-to-one function f: V → U such that, for every edge {u,v} ∈ E, the unique path in T from the root to some vertex of U contains both f(u) and f(v), and such that Σ_{{u,v}∈E} d_T(f(u), f(v)) ≤ K, where d_T denotes distance in the tree T?
> Reference: [Gavril, 1977a]. Transformation from OPTIMAL LINEAR ARRANGEMENT.
````


=== Why This Reduction Cannot Be Implemented

````
### The core problem: OLA is a restriction of RTA

A linear arrangement is a special case of a rooted tree arrangement (a path P_n is a degenerate rooted tree). Therefore:

- **OLA ⊆ RTA**: every feasible OLA solution (a permutation on a path) is a feasible RTA solution.
- **opt(RTA) ≤ opt(OLA)**: RTA can search over all rooted trees, not just paths, so it may find strictly better solutions.

### Forward direction works, backward direction fails

As a decision reduction OLA → RTA with identity mapping (G' = G, K' = K):

- **Forward (⟹):** If OLA has a solution with cost ≤ K, then RTA has a solution with cost ≤ K (use the path tree). ✅
- **Backward (⟸):** If RTA has a solution with cost ≤ K using a **non-path tree**, there is no way to extract a valid OLA solution. The RTA-optimal tree may be branching, and no linear arrangement achieves the same cost. ❌

### Witness extraction is broken

The codebase requires `ReduceTo` with witness extraction: given a target solution, produce a valid source solution. For this reduction, the target (RTA) may return a non-path-tree embedding. There is no general procedure to convert an arbitrary rooted-tree embedding back into a linear arrangement while preserving the cost bound.

### What about the Gavril 1977a reference?

The GJ entry states that RTA's NP-completeness is proved "by transformation from OLA." The actual Gavril construction likely uses a non-trivial gadget that modifies the graph to force the optimal tree to be a path, ensuring the backward direction holds. The identity mapping (G' = G, K' = K) proposed in the original version of this issue is insufficient.

### Possible resolution paths

1. **Decision-reduction support**: If the codebase adds support for decision reductions (yes/no without witness extraction), the forward direction alone suffices to prove NP-hardness.
2. **Recover the original Gavril construction**: The actual 1977a paper may contain a gadget-based construction that forces path-tree solutions, enabli
...(truncated)
````


#pagebreak()


= Optimal Linear Arrangement


== Optimal Linear Arrangement $arrow.r$ Consecutive Ones Matrix Augmentation #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#434)]


=== Reference

````
> [SR16] CONSECUTIVE ONES MATRIX AUGMENTATION
> INSTANCE: An m x n matrix A of 0's and 1's and a positive integer K.
> QUESTION: Is there a matrix A', obtained from A by changing K or fewer 0 entries to 1's, such that A' has the consecutive ones property?
> Reference: [Booth, 1975], [Papadimitriou, 1976a]. Transformation from OPTIMAL LINEAR ARRANGEMENT.
> Comment: Variant in which we ask instead that A' have the circular ones property is also NP-complete.
````


#theorem[
  Optimal Linear Arrangement polynomial-time reduces to Consecutive Ones Matrix Augmentation.
]


=== Construction

````


**Summary:**
Given an OPTIMAL LINEAR ARRANGEMENT instance (G = (V, E), K_OLA), construct a CONSECUTIVE ONES MATRIX AUGMENTATION instance as follows:

Let n = |V| and m = |E|. We build the edge-vertex incidence matrix of G.

1. **Matrix construction:** Construct the m x n binary matrix A where rows correspond to edges and columns correspond to vertices. For edge e_i = {u, v}, set A[i][u] = 1 and A[i][v] = 1, and all other entries in row i to 0. Each row has exactly two 1's.

2. **Bound:** Set K_C1P = K_OLA - m, where m = |E|.

3. **Intuition:** In any column permutation (= vertex ordering f), the two 1's in row i (for edge {u,v}) are at positions f(u) and f(v). To make this row have the consecutive ones property, we must fill in all the 0's between positions f(u) and f(v), requiring |f(u) - f(v)| - 1 flips. The total number of flips across all rows is sum_{{u,v} in E} (|f(u) - f(v)| - 1) = (sum |f(u) - f(v)|) - m. Thus, achieving C1P with at most K_C1P = K_OLA - m flips is equivalent to finding an arrangement with total edge length at most K_OLA.

4. **Correctness (forward):** If G has a linear arrangement f with sum_{{u,v} in E} |f(u) - f(v)| <= K_OLA, then using f as the column permutation and filling gaps within each row requires sum |f(u) - f(v)| - m <= K_OLA - m = K_C1P flips. The resulting matrix has the C1P.

5. **Correctness (reverse):** If matrix A can be augmented to have C1P with at most K_C1P flips, then the column permutation achieving C1P defines a vertex ordering f. For each edge row, the flips needed are |f(u) - f(v)| - 1, so the total edge length is (flips + m) <= K_C1P + m = K_OLA.

**Time complexity of reduction:** O(n * m) to construct the incidence matrix.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source OptimalLinearArrangement instance (|V|)
- m = `num_edges` of source OptimalLinearArrangement instance (|E|)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_rows` | `num_edges` |
| `num_cols` | `num_vertices` |
| `bound` | `bound - num_edges` |

**Derivation:** The matrix has one row per edge and one column per vertex. The augmentation bound is the OLA bound minus the number of edges (accounting for the baseline cost of 1 per edge in any arrangement).
````


=== Correctness

````


- Closed-loop test: reduce an OptimalLinearArrangement instance to ConsecutiveOnesMatrixAugmentation, solve target with BruteForce, extract solution (column permutation + flipped entries), verify on source by reconstructing the linear arrangement.
- Test with path graph (polynomial OLA case): path P_6 with identity arrangement has cost 5 (optimal). Incidence matrix has 5 rows and 6 columns. K_C1P = 5 - 5 = 0. The incidence matrix of a path already has C1P (1's are already consecutive).
- Test with complete graph K_4: 4 vertices, 6 edges. Optimal arrangement cost is known. Verify augmentation bound matches.
````


=== Example

````


**Source instance (OptimalLinearArrangement):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 7 edges:
- Edges: e0={0,1}, e1={1,2}, e2={2,3}, e3={3,4}, e4={4,5}, e5={0,3}, e6={2,5}
- Bound K_OLA = 11

**Constructed target instance (ConsecutiveOnesMatrixAugmentation):**
Matrix A (7 x 6), edge-vertex incidence matrix:
---
       v0 v1 v2 v3 v4 v5
e0:  [  1, 1, 0, 0, 0, 0 ]   (edge {0,1})
e1:  [  0, 1, 1, 0, 0, 0 ]   (edge {1,2})
e2:  [  0, 0, 1, 1, 0, 0 ]   (edge {2,3})
e3:  [  0, 0, 0, 1, 1, 0 ]   (edge {3,4})
e4:  [  0, 0, 0, 0, 1, 1 ]   (edge {4,5})
e5:  [  1, 0, 0, 1, 0, 0 ]   (edge {0,3})
e6:  [  0, 0, 1, 0, 0, 1 ]   (edge {2,5})
---
Bound K_C1P = 11 - 7 = 4

**Solution mapping:**
- Column permutation (arrangement): f(0)=1, f(1)=2, f(2)=3, f(3)=4, f(4)=5, f(5)=6
  (identity ordering: v0, v1, v2, v3, v4, v5)
- With identity ordering, rows e0-e4 already have consecutive 1's (adjacent vertices).
- Row e5 (edge {0,3}): 1's at columns 0 and 3. Need to fill positions 1 and 2. Flips: 2.
- Row e6 (edge {2,5}): 1's at columns 2 and 5. Need to fill positions 3 and 4. Flips: 2.
- Total flips: 0+0+0+0+0+2+2 = 4 = K_C1P. YES.

**Verification:**
- Total edge length: |1-2|+|2-3|+|3-4|+|4-5|+|5-6|+|1-4|+|3-6| = 1+1+1+1+1+3+3 = 11 = K_OLA.
- Total flips = 11 - 7 = 4 = K_C1P. Consistent.
````


#pagebreak()


== Optimal Linear Arrangement $arrow.r$ Sequencing to Minimize Weighted Completion Time #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#472)]


=== Reference

````
> [SS4] SEQUENCING TO MINIMIZE WEIGHTED COMPLETION TIME
> INSTANCE: Set T of tasks, partial order  QUESTION: Is there a one-processor schedule sigma for T that obeys the precedence constraints and for which the sum, over all t E T, of (sigma(t) + l(t))*w(t) is K or less?
> Reference: [Lawler, 1978]. Transformation from OPTIMAL LINEAR ARRANGEMENT.
> Comment: NP-complete in the strong sense and remains so even if all task lengths are 1 or all task weights are 1. Can be solved in polynomial time for < a "forest" [Horn, 1972], [Adolphson and Hu, 1973], [Garey, 1973], [Sidney, 1975] or if < is "series-parallel" or "generalized series-parallel" [Knuth, 1973], [Lawler, 1978], [Adolphson, 1977], [Monma and Sidney, 1977]. If the partial order < is replaced by individual task deadlines, the resulting problem is NP-complete in the strong sense [Lenstra, 1977], but can be solved in polynomial time if all task weights are equal [Smith, 1956]. If there are individual task release times instead of de
...(truncated)
````


#theorem[
  Optimal Linear Arrangement polynomial-time reduces to Sequencing to Minimize Weighted Completion Time.
]


=== Construction

````
**Summary:**
Given an OPTIMAL LINEAR ARRANGEMENT instance (G = (V, E), K_OLA), where |V| = n and |E| = m, construct a SEQUENCING TO MINIMIZE WEIGHTED COMPLETION TIME instance via the Lawler/LQSS reduction (Lemma 4.14 with the d_max shift for non-negative weights).

Let d_max = max_{v in V} deg(v) be the maximum vertex degree in G.

1. **Vertex tasks:** For each vertex v in V, create a task t_v with:
   - Length: l(t_v) = 1 (unit processing time)
   - Weight: w(t_v) = d_max - deg(v) (non-negative; zero for maximum-degree vertices)

2. **Edge tasks:** For each edge e = {u, v} in E, create a task t_e with:
   - Length: l(t_e) = 0 (zero processing time)
   - Weight: w(t_e) = 2

3. **Precedence constraints:** For each edge e = {u, v} in E, add:
   - t_u  {1,...,n}, vertex v completes at time C_v = f(v) and zero-length edge job {u,v} completes at time C_{u,v} = max{f(u), f(v)}. The total weighted completion time is:

   W(f) = sum_v (d_max - deg(v)) * f(v) + sum_{(u,v) in E} 2 * max{f(u), f(v)}
        = d_max * sum_v f(v) - sum_v deg(v) * f(v) + sum_{(u,v) in E} 2 * max{f(u), f(v)}
        = d_max * n*(n+1)/2 - sum_{(u,v) in E} (f(u) + f(v)) + sum_{(u,v) in E} 2 * max{f(u), f(v)}
        = d_max * n*(n+1)/2 + sum_{(u,v) in E} (2*max{f(u),f(v)} - f(u) - f(v))
        = d_max * n*(n+1)/2 + sum_{(u,v) in E} |f(u) - f(v)|
        = d_max * n*(n+1)/2 + OLA(f)

   The second step uses sum_v deg(v) * f(v) = sum_{(u,v) in E} (f(u) + f(v)), and the last step uses the identity 2*max(a,b) - a - b = |a - b|.

   Therefore min_f W(f)  {1,...,n}.

**Key invariant:** G has a linear arrangement with cost = 1` validation to allow `l(t) = 0`, which is consistent with the scheduling literature. Alternatively, the LQSS Exercise 4.19 approach can pad edge tasks to unit length with weight 0, but this changes the bound formula and requires a more involved derivation.
````


=== Overhead

````
**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_tasks`               | `num_vertices + num_edges`       |

**Derivation:**
- One task per vertex plus one task per edge gives |T| = n + m.
- The precedence constraints form a bipartite partial order with 2m precedence pairs.
- Construction is O(n + m).
````


=== Correctness

````
- Closed-loop test: construct an OPTIMAL LINEAR ARRANGEMENT instance (G, K_OLA), reduce to SEQUENCING TO MINIMIZE WEIGHTED COMPLETION TIME, solve the target with BruteForce, verify the optimal scheduling cost equals OLA_cost + d_max * n*(n+1)/2.
- Extract the vertex-task ordering from the optimal schedule and verify it yields an optimal linear arrangement.
- Test with a path graph P_4 (4 vertices, 3 edges): d_max = 2. Optimal arrangement cost is 3. Verify scheduling cost = 3 + 2 * 4 * 5 / 2 = 3 + 20 = 23.
- Test with K_3 (triangle, 3 vertices, 3 edges): d_max = 2. Optimal arrangement cost is 4. Verify scheduling cost = 4 + 2 * 3 * 4 / 2 = 4 + 12 = 16.
- Test with a star graph S_4 (center + 3 leaves, 4 vertices, 3 edges): d_max = 3. Optimal arrangement cost is 6 (center at position 2 or 3). Verify scheduling cost = 6 + 3 * 4 * 5 / 2 = 6 + 30 = 36.
````


=== Example

````
**Source instance (OPTIMAL LINEAR ARRANGEMENT):**
Graph G = P_4: vertices {0, 1, 2, 3}, edges {0,1}, {1,2}, {2,3}.
- Degrees: deg(0)=1, deg(1)=2, deg(2)=2, deg(3)=1. d_max = 2.
- Optimal arrangement: f(0)=1, f(1)=2, f(2)=3, f(3)=4
  Cost = |1-2| + |2-3| + |3-4| = 1 + 1 + 1 = 3

**Constructed target instance (SEQUENCING TO MINIMIZE WEIGHTED COMPLETION TIME):**

Tasks (|V| + |E| = 4 + 3 = 7 total):

| Task   | Type   | Length l | Weight w           | Notes                        |
|--------|--------|----------|--------------------|------------------------------|
| t_0    | vertex | 1        | 2 - 1 = 1         | deg(0)=1, d_max - deg = 1   |
| t_1    | vertex | 1        | 2 - 2 = 0         | deg(1)=2, d_max - deg = 0   |
| t_2    | vertex | 1        | 2 - 2 = 0         | deg(2)=2, d_max - deg = 0   |
| t_3    | vertex | 1        | 2 - 1 = 1         | deg(3)=1, d_max - deg = 1   |
| t_01   | edge   | 0        | 2                  | edge {0,1}                  |
| t_12   | edge   | 0        | 2                  | edge {1,2}                  |
| t_23   | edge   | 0        | 2                  | edge {2,3}                  |

Precedence constraints:
- t_0 < t_01, t_1 < t_01
- t_1 < t_12, t_2 < t_12
- t_2 < t_23, t_3 < t_23

**Schedule (from arrangement f(0)=1, f(1)=2, f(2)=3, f(3)=4):**

Vertex tasks are scheduled at positions f(v). Zero-length edge tasks complete instantly at the completion time of their later endpoint:

| Task | Completion time C | Weight w | w * C |
|------|-------------------|----------|-------|
| t_0  | f(0) = 1          | 1        | 1     |
| t_1  | f(1) = 2          | 0        | 0     |
| t_01 | max{1,2} = 2      | 2        | 4     |
| t_2  | f(2) = 3          | 0        | 0     |
| t_12 | max{2,3} = 3      | 2        | 6     |
| t_3  | f(3) = 4          | 1        | 4     |
| t_23 | max{3,4} = 4      | 2        | 8     |

Total weighted completion time = 1 + 0 + 4 + 0 + 6 + 4 + 8 = 23

Verification: d_max * n*(n+1)/2 + OLA = 2 * 10 + 3 = 23. ✓

**
...(truncated)
````


#pagebreak()


= PARTITION


== PARTITION $arrow.r$ INTEGRAL FLOW WITH MULTIPLIERS #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#363)]


=== Reference

````
> [ND33] INTEGRAL FLOW WITH MULTIPLIERS
> INSTANCE: Directed graph G=(V,A), specified vertices s and t, multiplier h(v)∈Z^+ for each v∈V-{s,t}, capacity c(a)∈Z^+ for each a∈A, requirement R∈Z^+.
> QUESTION: Is there a flow function f: A->Z_0^+ such that
> (1) f(a) (2) for each v∈V-{s,t}, Sum_{(u,v)∈A} h(v)*f((u,v)) = Sum_{(v,u)∈A} f((v,u)), and
> (3) the net flow into t is at least R?
> Reference: [Sahni, 1974]. Transformation from PARTITION.
> Comment: Can be solved in polynomial time by standard network flow techniques if h(v)=1 for all v∈V-{s,t}. Corresponding problem with non-integral flows allowed can be solved by linear programming.
````


#theorem[
  PARTITION polynomial-time reduces to INTEGRAL FLOW WITH MULTIPLIERS.
]


=== Construction

````


**Summary:**
Given a PARTITION instance with multiset A = {a_1, a_2, ..., a_n} of positive integers with total sum S, construct an INTEGRAL FLOW WITH MULTIPLIERS instance as follows (based on Sahni, 1974):

1. **Vertices:** Create a directed graph with vertices s, t, and intermediate vertices v_1, v_2, ..., v_n.

2. **Arcs from s:** For each i = 1, ..., n, add an arc (s, v_i) with capacity c(s, v_i) = 1.

3. **Arcs to t:** For each i = 1, ..., n, add an arc (v_i, t) with capacity c(v_i, t) = a_i.

4. **Multipliers:** For each intermediate vertex v_i, set the multiplier h(v_i) = a_i. This means the generalized conservation constraint at v_i is:
   h(v_i) * f(s, v_i) = f(v_i, t), i.e., a_i * f(s, v_i) = f(v_i, t).

5. **Requirement:** Set R = S/2 (the required net flow into t).

6. **Correctness (forward):** If A has a balanced partition A_1 (with sum S/2), for each a_i in A_1 set f(s, v_i) = 1, f(v_i, t) = a_i; for each a_i not in A_1 set f(s, v_i) = 0, f(v_i, t) = 0. The conservation constraint a_i * f(s, v_i) = f(v_i, t) is satisfied at every v_i. The net flow into t is sum of a_i for i in A_1 = S/2 = R.

7. **Correctness (reverse):** If a feasible integral flow exists with net flow >= R = S/2 into t, the conservation constraints force f(v_i, t) = a_i * f(s, v_i). Since c(s, v_i) = 1, f(s, v_i) in {0, 1}. The net flow into t is sum of a_i * f(s, v_i) >= S/2. Since the total of all a_i is S, and each contributes either 0 or a_i, the set {a_i : f(s, v_i) = 1} has sum >= S/2 and the complementary set has sum <= S/2, giving a balanced partition.

**Key invariant:** The multiplier h(v_i) = a_i combined with unit capacity on the source arcs encodes the binary include/exclude decision. The flow requirement R = S/2 encodes the partition balance condition.

**Time complexity of reduction:** O(n) to construct the graph.
````


=== Overhead

````


**Symbols:**
- n = number of elements in the PARTITION instance
- S = sum of all elements

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | `n + 2` |
| `num_arcs` | `2 * n` |
| `requirement` (R) | `S / 2` |

**Derivation:** The graph has n + 2 vertices (s, t, and n intermediate vertices) and 2n arcs (one from s to each v_i and one from each v_i to t). The flow requirement is S/2.
````


=== Correctness

````


- Closed-loop test: reduce a PARTITION instance to IntegralFlowWithMultipliers, solve target with BruteForce (enumerate integer flow assignments), extract solution, verify on source
- Test with known YES instance: A = {1, 2, 3, 4, 5, 5} with S = 20; balanced partition exists ({1,4,5} and {2,3,5})
- Test with known NO instance: A = {1, 2, 3, 7} with S = 13 (odd, no balanced partition)
- Compare with known results from literature
````


=== Example

````


**Source instance (PARTITION):**
A = {2, 3, 4, 5, 6, 4} with S = 24, S/2 = 12.
A valid partition: A_1 = {2, 4, 6} (sum = 12), A_2 = {3, 5, 4} (sum = 12).

**Constructed target instance (IntegralFlowWithMultipliers):**
- Vertices: s, v_1, v_2, v_3, v_4, v_5, v_6, t (8 vertices)
- Arcs and capacities:
  - (s, v_1): c = 1; (s, v_2): c = 1; (s, v_3): c = 1; (s, v_4): c = 1; (s, v_5): c = 1; (s, v_6): c = 1
  - (v_1, t): c = 2; (v_2, t): c = 3; (v_3, t): c = 4; (v_4, t): c = 5; (v_5, t): c = 6; (v_6, t): c = 4
- Multipliers: h(v_1) = 2, h(v_2) = 3, h(v_3) = 4, h(v_4) = 5, h(v_5) = 6, h(v_6) = 4
- Requirement: R = 12

**Solution mapping:**
- Partition A_1 = {a_1, a_3, a_5} = {2, 4, 6}: set f(s, v_1) = 1, f(s, v_3) = 1, f(s, v_5) = 1
- Partition A_2 = {a_2, a_4, a_6} = {3, 5, 4}: set f(s, v_2) = 0, f(s, v_4) = 0, f(s, v_6) = 0
- Flow on arcs to t: f(v_1, t) = 2*1 = 2, f(v_3, t) = 4*1 = 4, f(v_5, t) = 6*1 = 6
- All others: f(v_2, t) = 0, f(v_4, t) = 0, f(v_6, t) = 0
- Net flow into t: 2 + 0 + 4 + 0 + 6 + 0 = 12 = R
- Conservation at each v_i: h(v_i)*f(s,v_i) = f(v_i,t) holds
````


#pagebreak()


== PARTITION $arrow.r$ K-th LARGEST m-TUPLE #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#395)]


=== Reference

````
> [SP21] K^th LARGEST m-TUPLE (*)
> INSTANCE: Sets X_1,X_2,…,X_m⊆Z^+, a size s(x)∈Z^+ for each x∈X_i, 1≤i≤m, and positive integers K and B.
> QUESTION: Are there K or more distinct m-tuples (x_1,x_2,…,x_m) in X_1×X_2×···×X_m for which Σ_{i=1}^{m} s(x_i)≥B?
> Reference: [Johnson and Mizoguchi, 1978]. Transformation from PARTITION.
> Comment: Not known to be in NP. Solvable in polynomial time for fixed m, and in pseudo-polynomial time in general (polynomial in K, Σ|X_i|, and log Σ s(x)). The corresponding enumeration problem is #P-complete.
````


#theorem[
  PARTITION polynomial-time reduces to K-th LARGEST m-TUPLE.
]


=== Construction

````


**Summary:**
Given a PARTITION instance A = {a_1, ..., a_n} with sizes s(a_i) ∈ Z^+ and total sum S = Σ s(a_i), construct a K-th LARGEST m-TUPLE instance as follows:

1. **Number of sets:** Set m = n (one set per element of A).
2. **Sets:** For each i = 1, ..., n, define X_i = {0, s(a_i)} — a two-element set where 0 represents "not including a_i in the partition half" and s(a_i) represents "including a_i."
3. **Bound:** Set B = S/2 (half the total sum). If S is odd, the PARTITION instance has no solution — the reduction can set B = ⌈S/2⌉ to ensure the answer is NO.
4. **Threshold K:** Set K = (number of m-tuples with sum ≥ S/2 when no exact partition exists) + 1. More precisely, let C be the number of m-tuples (x_1, ..., x_m) ∈ X_1 × ... × X_m with Σ x_i > S/2. If PARTITION is feasible, there exist m-tuples with sum = S/2, which are additional m-tuples meeting the threshold. Set K = C + 1 (where C counts tuples with sum strictly greater than S/2).

**Correctness:**
- Each m-tuple (x_1, ..., x_m) ∈ X_1 × ... × X_m corresponds to a subset A' ⊆ A (include a_i iff x_i = s(a_i)). The tuple sum equals Σ_{a_i ∈ A'} s(a_i).
- The m-tuples with sum ≥ S/2 are exactly those corresponding to subsets with sum ≥ S/2.
- PARTITION is feasible iff some subset sums to exactly S/2, which creates additional m-tuples at the boundary (sum = S/2) beyond those with sum > S/2.

**Note:** As with R85, computing K requires counting subsets, making this a Turing reduction. The (*) in GJ indicates the problem is not known to be in NP.
````


=== Overhead

````


**Symbols:**
- n = |A| = number of elements in the PARTITION instance

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_sets` (= m)           | `num_elements` (= n)             |
| `total_set_sizes` (Σ\|X_i\|) | `2 * num_elements` (= 2n)      |

**Derivation:** Each element a_i maps to a 2-element set X_i = {0, s(a_i)}, giving m = n sets with 2 elements each. Total number of m-tuples is 2^n. The bound B and threshold K are scalar parameters. Construction is O(n) for the sets, plus counting time for K.
````


=== Correctness

````


- Closed-loop test: construct a PARTITION instance, reduce to K-th LARGEST m-TUPLE, solve the target with BruteForce (enumerate all 2^n m-tuples, count those with sum ≥ B), verify the count agrees with the source PARTITION answer.
- Compare with known results from literature: verify that the bijection between m-tuples and subsets of A is correct, and that the YES/NO answer matches.
- Edge cases: test with odd total sum (no partition possible), all equal elements (many partitions), and instances with a unique balanced partition.
````


=== Example

````


**Source instance (PARTITION):**
A = {3, 1, 1, 2, 2, 1} (n = 6 elements)
Total sum S = 10; target half-sum = 5.
A balanced partition exists: A' = {3, 2} (sum = 5), A \ A' = {1, 1, 2, 1} (sum = 5).

**Constructed K-th LARGEST m-TUPLE instance:**

Step 1: m = 6 sets.
Step 2: X_1 = {0, 3}, X_2 = {0, 1}, X_3 = {0, 1}, X_4 = {0, 2}, X_5 = {0, 2}, X_6 = {0, 1}
Step 3: B = 5 (= S/2).
Step 4: Count m-tuples with sum > 5 (strictly greater):

Total 2^6 = 64 m-tuples. Each corresponds to a subset of A.
Subsets with sum > 5: these correspond to subsets of {3,1,1,2,2,1} with sum in {6,7,8,9,10}.

Counting by complement: subsets with sum ≤ 4:
- {} : 0, {1}×3 : 1, {2}×2 : 2, {3} : 3 (7 singletons+empty ≤ 4)
- Actually systematically: sum=0: 1, sum=1: 3 ({a_2},{a_3},{a_6}), sum=2: 4 ({a_4},{a_5},{a_2,a_3},{a_2,a_6},{a_3,a_6}... need careful count)

Let me count subsets with sum ≤ 4 using DP:
- DP[0] = 1 (empty set)
- After a_1 (size 3): DP = [1,0,0,1,0,...] → sums 0:1, 3:1
- After a_2 (size 1): sums 0:1, 1:1, 3:1, 4:1
- After a_3 (size 1): sums 0:1, 1:2, 2:1, 3:1, 4:2 (but this counts distinct subsets)

Let me just count: subsets with sum = 5 (balanced partition): these are the boundary.
By symmetry, subsets with sum  5 come in complementary pairs.
Number of subsets with sum = 5: let's enumerate: {3,2_a}(5), {3,2_b}(5), {3,1_a,1_b}(5), {3,1_a,1_c}(5), {3,1_b,1_c}(5), {2_a,2_b,1_a}(5), {2_a,2_b,1_b}(5), {2_a,2_b,1_c}(5), {1_a,1_b,1_c,2_a}(5)... wait, that's sum=6.
Let me be precise with sizes [3,1,1,2,2,1]:
- {a_1,a_4} = {3,2} → 5 ✓
- {a_1,a_5} = {3,2} → 5 ✓
- {a_1,a_2,a_6} = {3,1,1} → 5 ✓
- {a_1,a_3,a_6} = {3,1,1} → 5 ✓
- {a_1,a_2,a_3} = {3,1,1} → 5 ✓
- {a_4,a_5,a_6} = {2,2,1} → 5 ✓
- {a_4,a_5,a_2} = {2,2,1} → 5 ✓
- {a_4,a_5,a_3} = {2,2,1} → 5 ✓
- {a_2,a_3,a_6,a_4} = {1,1,1,2} → 5 ✓
- {a_2,a_3,a_6,a_5} = {1,1,1,2} → 5 ✓

That gives 10 subsets summing to exactly 5.
By symmetry: 64 total, with sum5 count = (64 - 10) / 2 = 27 each.

C = 27 (subsets with sum > 5). K = 27 + 1 = 28.

*
...(truncated)
````


#pagebreak()


= Partition


== Partition $arrow.r$ Sequencing with Deadlines and Set-Up Times #text(size: 8pt, fill: orange)[ \[Blocked\] ] #text(size: 8pt, fill: gray)[(\#474)]


=== Reference

````
> [SS6] SEQUENCING WITH DEADLINES AND SET-UP TIMES
> INSTANCE: Set C of "compilers," set T of tasks, for each t E T a length l(t) E Z+, a deadline d(t) E Z+, and a compiler k(t) E C, and for each c E C a "set-up time" l(c) E Z_0+.
> QUESTION: Is there a one-processor schedule σ for T that meets all the task deadlines and that satisfies the additional constraint that, whenever two tasks t and t' with σ(t) = σ(t) + l(t) + l(k(t'))?
> Reference: [Bruno and Downey, 1978]. Transformation from PARTITION.
> Comment: Remains NP-complete even if all set-up times are equal. The related problem in which set-up times are replaced by "changeover costs," and we want to know if there is a schedule that meets all the deadlines and has total changeover cost at most K, is NP-complete even if all changeover costs are equal. Both problems can be solved in pseudo-polynomial time when the number of distinct deadlines is bounded by a constant. If the number of deadlines is unbounded, it is open whether these
...(truncated)
````


#theorem[
  Partition polynomial-time reduces to Sequencing with Deadlines and Set-Up Times.
]


=== Construction

````


**Summary:**

Given a PARTITION instance: a multiset S = {s_1, ..., s_n} of positive integers with total sum 2B (i.e., Σs_i = 2B), construct a SEQUENCING WITH DEADLINES AND SET-UP TIMES instance as follows.

1. **Compilers:** Create two compilers c_1 and c_2, each with set-up time l(c_1) = l(c_2) = σ (a carefully chosen positive integer, e.g., σ = 1).

2. **Tasks from partition elements:** For each element s_i ∈ S, create a task t_i with:
   - Length l(t_i) = s_i
   - Compiler k(t_i) assigned alternately or strategically to c_1 or c_2
   - Deadline d(t_i) chosen so that meeting all deadlines forces the tasks to be grouped into two balanced batches

3. **Key idea:** The set-up time σ is incurred every time the processor switches between compilers. The deadlines are set so that the total available time accommodates exactly Σs_i plus the minimum number of compiler switches. A feasible schedule exists only if the tasks can be partitioned into two groups (one per compiler) with equal total length B, minimizing the number of switches.

4. **Correctness:** A balanced partition S' ∪ (S \ S') with each half summing to B exists if and only if a feasible schedule σ meeting all deadlines with the set-up time constraints exists. The set-up time penalty forces the tasks to be batched by compiler class, and the tight deadlines force each batch to sum to exactly B.

5. **Solution extraction:** Given a feasible schedule, the tasks assigned to compiler c_1 form one half of the partition (summing to B), and the tasks assigned to compiler c_2 form the other half.
````


=== Overhead

````


**Symbols:**
- n = number of elements in PARTITION instance (`num_elements` of source)
- B = half the total sum (Σs_i / 2)

| Target metric (code name)  | Polynomial (using symbols above) |
|-----------------------------|----------------------------------|
| `num_tasks`                 | n                                |
| `num_compilers`             | 2                                |
| `max_deadline`              | O(n + 2B)                        |
| `setup_time`                | O(1) (constant per compiler)     |

**Derivation:** Each element of S maps directly to one task with the same length. Only two compilers are needed (constant). Deadlines and set-up times are polynomial in the input size. Construction is O(n).
````


=== Correctness

````


- Closed-loop test: construct a PARTITION instance with n = 6 elements, reduce to SEQUENCING WITH DEADLINES AND SET-UP TIMES, enumerate all n! permutations of tasks, verify that a deadline-feasible schedule exists iff the PARTITION instance has a balanced split.
- Check that the constructed instance has exactly n tasks, 2 compilers, and set-up times as specified.
- Edge cases: test with odd total sum (infeasible PARTITION, expect no feasible schedule), n = 2 with equal elements (trivially feasible).
````


=== Example

````


**Source instance (PARTITION):**
S = {3, 4, 5, 6, 7, 5}, n = 6
Total sum = 30, B = 15.
Balanced partition: S' = {4, 5, 6} (sum = 15), S \ S' = {3, 7, 5} (sum = 15).

**Constructed SEQUENCING WITH DEADLINES AND SET-UP TIMES instance:**

Compilers: C = {c_1, c_2}, set-up times l(c_1) = l(c_2) = 1.

| Task | Length | Compiler | Deadline |
|------|--------|----------|----------|
| t_1  | 3      | c_1      | 16       |
| t_2  | 4      | c_1      | 16       |
| t_3  | 5      | c_1      | 16       |
| t_4  | 6      | c_2      | 31       |
| t_5  | 7      | c_2      | 31       |
| t_6  | 5      | c_2      | 31       |

The deadlines are set so that compiler c_1 tasks must complete by time 16 (= B + 1 set-up time), and compiler c_2 tasks must complete by time 31 (= 2B + 1 set-up time). This forces exactly one compiler switch.

**Solution:**
Schedule: t_2 (0–4), t_3 (4–9), t_6 (9–14) ... but we need to respect compiler grouping.

Better grouping: All c_1 tasks first, then switch, then all c_2 tasks.
Schedule: t_1 (0–3), t_2 (3–7), t_3 (7–12), [set-up: 12–13], t_4 (13–19), t_5 (19–26), t_6 (26–31).
Check: c_1 tasks finish by time 12 ≤ 16 ✓, c_2 tasks finish by time 31 ≤ 31 ✓.

**Solution extraction:**
Partition half 1 (c_1 tasks): {3, 4, 5}, sum = 12. Hmm, not 15.

The exact construction from Bruno & Downey is more nuanced — the compiler assignments and deadlines are set to enforce balanced loads rather than simple grouping. The above illustrates the general structure; the precise parameter choices from the original paper ensure that the two compiler batches have equal total length B.
````


#pagebreak()


= Partition / 3-Partition


== Partition / 3-Partition $arrow.r$ Expected Retrieval Cost #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#423)]


=== Reference

````
> [SR4] EXPECTED RETRIEVAL COST
> INSTANCE: Set R of records, rational probability p(r) ∈ [0,1] for each r ∈ R, with ∑_{r ∈ R} p(r) = 1, number m of sectors, and a positive integer K.
> QUESTION: Is there a partition of R into disjoint subsets R_1, R_2, ..., R_m such that, if p(R_i) = ∑_{r ∈ R_i} p(r) and the "latency cost" d(i,j) is defined to be j−i−1 if 1 ≤ i  Reference: [Cody and Coffman, 1976]. Transformation from PARTITION, 3-PARTITION.
> Comment: NP-complete in the strong sense. NP-complete and solvable in pseudo-polynomial time for each fixed m ≥ 2.
````


#theorem[
  Partition / 3-Partition polynomial-time reduces to Expected Retrieval Cost.
]


=== Construction

````


**Summary (PARTITION → EXPECTED RETRIEVAL COST with m = 2):**

Given a PARTITION instance: a finite set A = {a_1, ..., a_n} with sizes s(a_i) ∈ Z⁺ and total sum B = ∑ s(a_i), construct an Expected Retrieval Cost instance as follows:

1. **Records:** For each element a_i ∈ A, create a record r_i with probability p(r_i) = s(a_i) / B. Since ∑ s(a_i) = B, we have ∑ p(r_i) = 1.

2. **Sectors:** Set m = 2 sectors.

3. **Latency cost:** With m = 2, the circular latency function gives d(1,1) = 0, d(2,2) = 0, d(1,2) = 0 (since j − i − 1 = 2 − 1 − 1 = 0), and d(2,1) = m − i + j − 1 = 2 − 2 + 1 − 1 = 0. Wait — with m = 2 the latency is degenerate. The meaningful reduction uses m ≥ 3 or a more careful encoding.

**Summary (3-PARTITION → EXPECTED RETRIEVAL COST, strong sense):**

Given a 3-PARTITION instance: a set A = {a_1, ..., a_{3m}} of 3m positive integers with total sum m·B, where B/4 < a_i < B/2 for all i (so each group must have exactly 3 elements summing to B), construct an Expected Retrieval Cost instance:

1. **Records:** For each element a_i, create a record r_i with probability p(r_i) = a_i / (m·B). The probabilities sum to 1.

2. **Sectors:** Use m sectors (matching the 3-PARTITION parameter m).

3. **Bound K:** Set K to the expected latency cost that would result if the records could be distributed with each sector having total probability exactly 1/m (i.e., a perfectly balanced allocation). This value can be computed from the latency formula: for a perfectly balanced allocation where p(R_i) = 1/m for all i, the total cost equals (1/m²) · ∑_{i,j} d(i,j).

4. **Correctness (forward):** If a valid 3-partition exists (each group of 3 elements sums to B), then assigning the corresponding records to sectors gives p(R_i) = B/(m·B) = 1/m for each sector. The resulting expected retrieval cost equals K (the balanced cost).

5. **Correctness (reverse):** If the expected retrieval cost is at most K, the allocation must be perfectly balanced (each sector has probability 1/m), because any imbalance strictly increases the quadratic latency cost. This means each sector contains records whose original sizes sum to exactly B, yielding a valid 3-partition.

6. **Solution extraction:** Given a valid record allocation achieving cost ≤ K, the partition groups are G_i = {a_j : r_j ∈ R_i} for i = 1, ..., m.

**Key invariant:** The quadratic nature of the latency cost (products p(R_i)·p(R_j)) is minimized when the probability mass is distributed as evenly as possible across sectors. A cost of exactly K is achievable if and only if a perfectly balanced partition exists.

**Time complexity of reduction:** O(n) to compute probabilities and the bound K.
````


=== Overhead

````


**Symbols:**
- n = number of elements in the source PARTITION / 3-PARTITION instance
- m = number of groups in the 3-PARTITION instance (n = 3m)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_records`              | `num_elements` (= n = 3m)       |
| `num_sectors`              | `num_groups` (= m = n/3)        |

**Derivation:** Each element of the source instance maps to exactly one record. The number of sectors equals the number of groups in the 3-PARTITION instance. The bound K is computed from the latency formula in O(m²) time.
````


=== Correctness

````


- Closed-loop test: construct a 3-PARTITION instance, reduce to Expected Retrieval Cost, solve target by brute-force enumeration of all partitions of n records into m sectors, verify the allocation achieving cost ≤ K corresponds to a valid 3-partition.
- Test with known YES instance: A = {5, 6, 7, 5, 6, 7} with m = 2, B = 18; valid groups {5,6,7} and {5,6,7} should give a balanced allocation with cost = K.
- Test with known NO instance: A = {1, 1, 1, 10, 10, 10} with m = 2, B = 16.5 (non-integer, so no valid 3-partition); verify no allocation achieves cost ≤ K.
- Verify that the cost function is indeed minimized at balanced allocations by testing with small m values.
````


=== Example

````


**Source instance (3-PARTITION):**
A = {5, 6, 7, 5, 6, 7} (n = 6 elements, m = 2 groups)
B = (5+6+7+5+6+7)/2 = 18, target group sum = 18.
Valid 3-partition: G_1 = {5, 6, 7} (sum = 18) and G_2 = {5, 6, 7} (sum = 18).

**Constructed target instance (ExpectedRetrievalCost):**
- Records: r_1 through r_6 with probabilities:
  - p(r_1) = 5/36, p(r_2) = 6/36 = 1/6, p(r_3) = 7/36
  - p(r_4) = 5/36, p(r_5) = 6/36 = 1/6, p(r_6) = 7/36
  - Sum = 36/36 = 1 ✓
- Sectors: m = 2
- Latency costs: d(1,2) = 2−1−1 = 0, d(2,1) = 2−2+1−1 = 0. With m = 2, all latency costs are 0 — this is the degenerate case.

**Corrected example with m = 3 sectors (n = 9 elements):**

**Source instance (3-PARTITION):**
A = {3, 3, 4, 2, 4, 4, 3, 5, 2} (n = 9 elements, m = 3 groups)
Total sum = 30, B = 10, each group must sum to 10.
Valid 3-partition: G_1 = {3, 3, 4}, G_2 = {2, 4, 4}, G_3 = {3, 5, 2}.

**Constructed target instance (ExpectedRetrievalCost):**
- Records: r_1, ..., r_9 with p(r_i) = a_i/30
  - p(r_1) = 3/30 = 1/10, p(r_2) = 1/10, p(r_3) = 4/30 = 2/15
  - p(r_4) = 2/30 = 1/15, p(r_5) = 2/15, p(r_6) = 2/15
  - p(r_7) = 1/10, p(r_8) = 5/30 = 1/6, p(r_9) = 1/15
  - Sum = 30/30 = 1 ✓
- Sectors: m = 3
- Latency costs (circular, m = 3):
  - d(1,1) = 0, d(1,2) = 0, d(1,3) = 1
  - d(2,1) = 1, d(2,2) = 0, d(2,3) = 0
  - d(3,1) = 0, d(3,2) = 1, d(3,3) = 0
- Bound K: For balanced allocation with p(R_i) = 1/3 for all i:
  K = ∑_{i,j} p(R_i)·p(R_j)·d(i,j) = (1/3)²·[0+0+1+1+0+0+0+1+0] = (1/9)·3 = 1/3.

**Solution mapping:**
- Assign R_1 = {r_1, r_2, r_3} (elements {3,3,4}): p(R_1) = 10/30 = 1/3 ✓
- Assign R_2 = {r_4, r_5, r_6} (elements {2,4,4}): p(R_2) = 10/30 = 1/3 ✓
- Assign R_3 = {r_7, r_8, r_9} (elements {3,5,2}): p(R_3) = 10/30 = 1/3 ✓
- Cost = (1/3)²·3 = 1/3 ≤ K = 1/3 ✓

**Verification:**
- Each sector has probability mass exactly 1/3 → perfectly balanced → minimum latency cost.
- Extracting element groups: G_1 = {3,3,4} sum 10 ✓, G_2 = {2,4,4} sum 10 ✓, G_3 = {3,5,2} sum 10 ✓.
````


#pagebreak()


= Register Sufficiency


== Register Sufficiency $arrow.r$ Sequencing to Minimize Maximum Cumulative Cost #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#475)]


=== Reference

````
> [SS7] SEQUENCING TO MINIMIZE MAXIMUM CUMULATIVE COST
> INSTANCE: Set T of tasks, partial order  QUESTION: Is there a one-processor schedule σ for T that obeys the precedence constraints and which has the property that, for every task t E T, the sum of the costs for all tasks t' with σ(t')  Reference: [Abdel-Wahab, 1976]. Transformation from REGISTER SUFFICIENCY.
> Comment: Remains NP-complete even if c(t) E {-1,0,1} for all t E T. Can be solved in polynomial time if < is series-parallel [Abdel-Wahab and Kameda, 1978], [Monma and Sidney, 1977].
````


#theorem[
  Register Sufficiency polynomial-time reduces to Sequencing to Minimize Maximum Cumulative Cost.
]


=== Construction

````


**Summary:**

Given a REGISTER SUFFICIENCY instance: a directed acyclic graph G = (V, A) with n = |V| vertices and a positive integer K, construct a SEQUENCING TO MINIMIZE MAXIMUM CUMULATIVE COST instance as follows.

1. **Tasks from vertices:** For each vertex v ∈ V, create a task t_v.

2. **Precedence constraints:** The partial order on tasks mirrors the DAG edges: if (u, v) ∈ A (meaning u depends on v, i.e., v must be computed before u can consume it), then t_v < t_u in the schedule (t_v must be scheduled before t_u).

3. **Cost assignment:** For each task t_v, set the cost c(t_v) = 1 − outdeg(v), where outdeg(v) is the out-degree of v in G. The intuition is:
   - When a vertex v is "evaluated," it occupies one register (cost +1).
   - Each of v's successor vertices u that uses v as an input will eventually "consume" that register (each predecessor that is the last to be needed frees one register slot).
   - A vertex with out-degree d effectively needs 1 register to store its result but frees registers as its successors are evaluated. The net cost c(t_v) = 1 − outdeg(v) captures this: leaves (outdeg = 0) cost +1 (they consume a register until their parent is computed), while high-outdegree nodes may have negative cost (freeing more registers than they use).

4. **Bound:** Set the cumulative cost bound to K (the same register bound from the original instance).

5. **Correctness:** The maximum cumulative cost at any point in the schedule equals the maximum number of simultaneously live registers during the corresponding evaluation order. Thus a K-register computation of G exists if and only if the tasks can be sequenced with maximum cumulative cost ≤ K.

6. **Solution extraction:** A feasible schedule σ with max cumulative cost ≤ K directly gives an evaluation order v_{σ^{-1}(1)}, v_{σ^{-1}(2)}, ..., v_{σ^{-1}(n)} that uses at most K registers.
````


=== Overhead

````


**Symbols:**
- n = |V| = number of vertices in the DAG (`num_vertices` of source)
- e = |A| = number of arcs in the DAG (`num_arcs` of source)

| Target metric (code name)   | Polynomial (using symbols above) |
|------------------------------|----------------------------------|
| `num_tasks`                  | n                                |
| `num_precedence_constraints` | e                                |
| `max_abs_cost`               | max(1, max_outdegree − 1)        |
| `bound_K`                    | K (same as source)               |

**Derivation:** Each vertex maps to one task; each arc maps to one precedence constraint. Costs are integers in range [1 − max_outdeg, 1]. Construction is O(n + e).
````


=== Correctness

````


- Closed-loop test: construct a small DAG (e.g., 6–8 vertices), compute register sufficiency bound K, reduce to SEQUENCING TO MINIMIZE MAXIMUM CUMULATIVE COST, enumerate all topological orderings, verify that the minimum maximum cumulative cost equals K.
- Check that costs satisfy c(t_v) = 1 − outdeg(v) and precedence constraints match DAG edges.
- Edge cases: test with a chain DAG (K = 1 register suffices, max cumulative cost = 1), a tree DAG, and a DAG requiring maximum registers.
````


=== Example

````


**Source instance (REGISTER SUFFICIENCY):**

DAG G = (V, A) with 7 vertices modeling an expression tree:
---
v1 → v3, v1 → v4
v2 → v4, v2 → v5
v3 → v6
v4 → v6
v5 → v7
v6 → v7
---
(Arrows mean "is an input to".) Vertices v1, v2 are inputs (in-degree 0). K = 3.

Out-degrees: v1: 2, v2: 2, v3: 1, v4: 1, v5: 1, v6: 1, v7: 0.

**Constructed SEQUENCING TO MINIMIZE MAXIMUM CUMULATIVE COST instance:**

| Task | Cost c(t) = 1 − outdeg | Predecessors (must be scheduled before) |
|------|------------------------|-----------------------------------------|
| t_1  | 1 − 2 = −1            | (none — input vertex)                   |
| t_2  | 1 − 2 = −1            | (none — input vertex)                   |
| t_3  | 1 − 1 = 0             | t_1                                     |
| t_4  | 1 − 1 = 0             | t_1, t_2                                |
| t_5  | 1 − 1 = 0             | t_2                                     |
| t_6  | 1 − 1 = 0             | t_3, t_4                                |
| t_7  | 1 − 0 = 1             | t_5, t_6                                |

K = 3.

**A feasible schedule (topological order):**
Order: t_1, t_2, t_3, t_4, t_5, t_6, t_7
Cumulative costs: −1, −2, −2, −2, −2, −2, −1

All cumulative costs ≤ K = 3 ✓

Note: In this example the costs are all non-positive except for the final task, so K = 3 is easily satisfied. The NP-hard instances arise from DAGs with many leaves (high positive costs) interleaved with high-outdegree nodes.

**Solution extraction:**
Evaluation order: v1, v2, v3, v4, v5, v6, v7 — uses at most 3 registers ✓
````


#pagebreak()


= SATISFIABILITY


== SATISFIABILITY $arrow.r$ UNDIRECTED FLOW WITH LOWER BOUNDS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#367)]


=== Reference

````
> [ND37] UNDIRECTED FLOW WITH LOWER BOUNDS
> INSTANCE: Graph G=(V,E), specified vertices s and t, capacity c(e)∈Z^+ and lower bound l(e)∈Z_0^+ for each e∈E, requirement R∈Z^+.
> QUESTION: Is there a flow function f: {(u,v),(v,u): {u,v}∈E}→Z_0^+ such that
> (1) for all {u,v}∈E, either f((u,v))=0 or f((v,u))=0,
> (2) for each e={u,v}∈E, l(e)≤max{f((u,v)),f((v,u))}≤c(e),
> (3) for each v∈V−{s,t}, flow is conserved at v, and
> (4) the net flow into t is at least R?
> Reference: [Itai, 1977]. Transformation from SATISFIABILITY.
> Comment: Problem is NP-complete in the strong sense, even if non-integral flows are allowed. Corresponding problem for directed graphs can be solved in polynomial time, even if we ask that the total flow be R or less rather than R or more [Ford and Fulkerson, 1962] (see also [Lawler, 1976a]). The analogous DIRECTED M-COMMODITY FLOW WITH LOWER BOUNDS problem is polynomially equivalent to LINEAR PROGRAMMING for all M≥2 if non-integral flows are allowed [Itai, 1977].
````


#theorem[
  SATISFIABILITY polynomial-time reduces to UNDIRECTED FLOW WITH LOWER BOUNDS.
]


=== Construction

````


**Summary:**
Given a SATISFIABILITY instance with n variables x_1, ..., x_n and m clauses C_1, ..., C_m, construct an UNDIRECTED FLOW WITH LOWER BOUNDS instance as follows:

1. **Variable gadgets:** For each variable x_i, create an undirected "choice" subgraph. Two parallel edges connect node u_i to node v_i: edge e_i^T (representing x_i = TRUE) and edge e_i^F (representing x_i = FALSE). Set lower bound l = 0 and capacity c = 1 on each.

2. **Chain the variable gadgets:** Connect s to u_1, v_1 to u_2, ..., v_n to a junction node. This forces exactly one unit of flow through each variable gadget, choosing either the TRUE or FALSE edge.

3. **Clause gadgets:** For each clause C_j, introduce additional edges that must carry flow (enforced by nonzero lower bounds). The lower bound on a clause edge forces at least one unit of flow, which can only be routed if at least one literal in the clause is satisfied.

4. **Literal connections:** For each literal in a clause, add edges connecting the clause gadget to the appropriate variable gadget edge. If literal x_i appears in clause C_j, connect to the TRUE side; if ¬x_i appears, connect to the FALSE side. The lower bound on the clause edge forces flow through at least one satisfied literal path.

5. **Lower bounds enforce clause satisfaction:** Each clause edge e_{C_j} has lower bound l(e_{C_j}) = 1, meaning at least one unit of flow must traverse it. This flow can only be routed if the corresponding literal's variable assignment allows it.

6. **Requirement:** Set R appropriately (n + m or similar) to ensure both the assignment path and all clause flows are realized.

The SAT formula is satisfiable if and only if there exists a feasible flow meeting all lower bounds and the requirement R. The key insight is that undirected flow with lower bounds is hard because the lower bound constraints interact nontrivially with the undirected flow conservation, unlike in directed graphs where standard max-flow/min-cut techniques handle lower bounds.
````


=== Overhead

````


| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | O(n + m) where n = num_variables, m = num_clauses |
| `num_edges` | O(n + m + L) where L = total literal occurrences |
| `max_capacity` | O(m) |
| `requirement` | O(n + m) |
````


=== Correctness

````


- Closed-loop test: reduce source SAT instance, solve target undirected flow with lower bounds using BruteForce, extract solution, verify on source
- Compare with known results from literature
- Verify that satisfiable SAT instances yield feasible flow and unsatisfiable instances do not
````


=== Example

````


**Source (SAT):**
Variables: x_1, x_2, x_3, x_4
Clauses:
- C_1 = (x_1 ∨ ¬x_2 ∨ x_3)
- C_2 = (¬x_1 ∨ x_2 ∨ x_4)
- C_3 = (¬x_3 ∨ ¬x_4 ∨ x_1)

**Constructed Target (Undirected Flow with Lower Bounds):**

Vertices: s, u_1, v_1, u_2, v_2, u_3, v_3, u_4, v_4, t, clause nodes c_1, c_2, c_3, and auxiliary routing nodes.

Edges:
- Variable chain: {s, u_1}, {u_1, v_1} (TRUE path for x_1), {u_1, v_1} (FALSE path for x_1), {v_1, u_2}, ..., {v_4, t}.
- Clause edges with lower bounds: {c_j_in, c_j_out} with l = 1, c = 1 for each clause.
- Literal connection edges linking clause gadgets to variable gadgets.

Lower bounds: 0 on variable edges, 1 on clause enforcement edges.
Capacities: 1 on all edges.
Requirement R = 4 + 3 = 7.

**Solution mapping:**
Assignment x_1=TRUE, x_2=TRUE, x_3=TRUE, x_4=TRUE satisfies all clauses.
- C_1 satisfied by x_1=TRUE: flow routed through x_1's TRUE edge to clause C_1.
- C_2 satisfied by x_2=TRUE: flow routed through x_2's TRUE edge to clause C_2.
- C_3 satisfied by x_1=TRUE: flow routed through x_1's TRUE edge to clause C_3.
- Total flow: 4 (variable chain) + 3 (clause flows) = 7 = R.
````


#pagebreak()


= SET COVERING


== SET COVERING $arrow.r$ STRING-TO-STRING CORRECTION #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#453)]


=== Reference

````
> [SR20] STRING-TO-STRING CORRECTION
> INSTANCE: Finite alphabet Σ, two strings x,y E Σ*, and a positive integer K.
> QUESTION: Is there a way to derive the string y from the string x by a sequence of K or fewer operations of single symbol deletion or adjacent symbol interchange?
> Reference: [Wagner, 1975]. Transformation from SET COVERING.
> Comment: Solvable in polynomial time if the operation set is expanded to include the operations of changing a single character and of inserting a single character, even if interchanges are not allowed (e.g., see [Wagner and Fischer, 1974]), or if the only operation is adjacent symbol interchange [Wagner, 1975]. See reference for related results for cases in which different operations can have different costs.
````


#theorem[
  SET COVERING polynomial-time reduces to STRING-TO-STRING CORRECTION.
]


=== Construction

````


**Summary:**
Given a SET COVERING instance (S, C, K) where S is a universe of m elements, C = {C_1, ..., C_n} is a collection of n subsets of S, and K is a budget, construct a STRING-TO-STRING CORRECTION instance as follows:

1. **Alphabet construction:** Create a finite alphabet Sigma with one distinct symbol for each element of S plus additional separator/marker symbols. Specifically, use symbols a_1, ..., a_m for the m universe elements, plus additional structural symbols to encode the covering structure. The alphabet size is O(m + n).

2. **Source string x construction:** Construct the source string x that encodes the structure of the set covering instance. For each subset C_j in C, create a "block" in the string containing the symbols corresponding to elements in C_j, arranged so that selecting subset C_j corresponds to performing a bounded number of swap and delete operations on that block. Blocks are separated by marker symbols. The source string has length O(m * n).

3. **Target string y construction:** Construct the target string y that represents the "goal" configuration, where the elements are grouped/ordered in a way that can only be achieved from x by selecting at most K subsets worth of edit operations.

4. **Budget parameter:** Set the edit distance bound K' = f(K, m, n) for some polynomial function f that ensures K or fewer subsets can cover S if and only if K' or fewer swap/delete operations transform x into y.

5. **Solution extraction:** Given a sequence of at most K' edit operations transforming x to y, decode which subsets were effectively "selected" by examining which blocks were modified, recovering a set cover of size at most K.

**Key invariant:** A set cover of S using at most K subsets from C exists if and only if string y can be derived from string x using at most K' swap and delete operations.
````


=== Overhead

````


**Symbols:**
- m = number of universe elements in S
- n = number of subsets in C (i.e., `num_sets`)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `alphabet_size` | O(m + n) |
| `string_length_x` | O(m * n) |
| `string_length_y` | O(m * n) |
| `budget` | polynomial in K, m, n |

**Derivation:** The alphabet must have enough distinct symbols to encode each universe element and structural separators. Each subset contributes a block to the source string proportional to the number of elements it contains, giving total string length polynomial in m and n. The target string has comparable length. The exact polynomial form depends on the specific encoding details in Wagner's 1975 construction.
````


=== Correctness

````


- Closed-loop test: reduce a MinimumSetCovering instance to StringToStringCorrection, solve the target with brute-force enumeration of edit operation sequences, extract the implied set cover, verify it is a valid cover on the original instance
- Check that the minimum edit distance equals the budget threshold exactly when a minimum set cover of the required size exists
- Test with a set covering instance where greedy fails (e.g., elements covered by overlapping subsets requiring non-obvious selection)
- Verify polynomial blow-up: string lengths and alphabet size should be polynomial in the original instance size
````


=== Example

````


**Source instance (MinimumSetCovering):**
Universe S = {1, 2, 3, 4, 5, 6}, Collection C:
- C_1 = {1, 2, 3}
- C_2 = {2, 4, 5}
- C_3 = {3, 5, 6}
- C_4 = {1, 4, 6}
Budget K = 2

Minimum set cover: {C_1, C_3} = {1,2,3} ∪ {3,5,6} = {1,2,3,5,6} -- does not cover 4.
Try: {C_2, C_4} = {2,4,5} ∪ {1,4,6} = {1,2,4,5,6} -- does not cover 3.
Try: {C_1, C_2} = {1,2,3} ∪ {2,4,5} = {1,2,3,4,5} -- does not cover 6.
No cover of size 2 exists. A cover of size 3 is needed, e.g., {C_1, C_2, C_3}.

**Constructed target instance (StringToStringCorrection):**
Using the reduction, construct:
- Alphabet Sigma with symbols {a, b, c, d, e, f, #, $} (one per element plus separators)
- Source string x encodes the subset structure with separator-delimited blocks
- Target string y encodes the desired grouped configuration
- Budget K' computed from K=2 and the instance parameters

**Solution mapping:**
- Since no set cover of size 2 exists, the edit distance from x to y exceeds K', confirming the answer is NO for both instances
- Increasing K to 3 would yield a valid set cover {C_1, C_2, C_3}, and correspondingly the edit distance from x to y would be at most K'(3)

**Note:** The exact string constructions depend on Wagner's specific encoding, which maps subset selection to sequences of adjacent swaps and deletions in a carefully designed string pair.
````


#pagebreak()


= Satisfiability


== Satisfiability $arrow.r$ IntegralFlowHomologousArcs #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#732)]


#theorem[
  Satisfiability polynomial-time reduces to IntegralFlowHomologousArcs.
]


=== Construction

````
Given a CNF formula φ = C₁ ∧ … ∧ Cₘ with n variables x₁, …, xₙ. Let kⱼ = |Cⱼ| (number of literals in clause j) and L = Σⱼ kⱼ (total literal count).

**Step 1: Negate to DNF.** Form P = ¬φ = K₁ ∨ … ∨ Kₘ where Kⱼ = ¬Cⱼ. If Cⱼ = (ℓ₁ ∨ … ∨ ℓ_{kⱼ}), then Kⱼ = (¬ℓ₁ ∧ … ∧ ¬ℓ_{kⱼ}).

**Step 2: Build network vertices.**

- Source s, sink t
- For each variable xᵢ (i = 1…n): one split node splitᵢ
- Pipeline boundary nodes: for each stage boundary j (j = 0…m) and each variable i (i = 1…n), two nodes node[j][i][T] and node[j][i][F] (the "true" and "false" channels for variable i after processing j clauses)
- For each clause stage j (j = 1…m): collector γⱼ and distributor δⱼ

Total vertices: 2nm + 3n + 2m + 2

**Step 3: Build network arcs.**

*Variable stage:* for each variable xᵢ:
- (s, splitᵢ) capacity 1
- Arc T⁰ᵢ = (splitᵢ, node[0][i][T]) capacity 1  — "base true" arc
- Arc F⁰ᵢ = (splitᵢ, node[0][i][F]) capacity 1  — "base false" arc

*Clause stage j* (j = 1…m) for clause Cⱼ:
- Bottleneck arc: (γⱼ, δⱼ) capacity kⱼ − 1

For each variable xᵢ, route based on its role in Cⱼ:

- **Case A — xᵢ appears as positive literal in Cⱼ** (so ¬xᵢ ∈ Kⱼ): the F channel goes through the bottleneck.
  - Entry arc: (node[j−1][i][F], γⱼ) capacity 1
  - Exit arc: (δⱼ, node[j][i][F]) capacity 1
  - T channel bypasses: (node[j−1][i][T], node[j][i][T]) capacity 1

- **Case B — ¬xᵢ appears as literal in Cⱼ** (so xᵢ ∈ Kⱼ): the T channel goes through the bottleneck.
  - Entry arc: (node[j−1][i][T], γⱼ) capacity 1
  - Exit arc: (δⱼ, node[j][i][T]) capacity 1
  - F channel bypasses: (node[j−1][i][F], node[j][i][F]) capacity 1

- **Case C — xᵢ not in Cⱼ**: both channels bypass.
  - (node[j−1][i][T], node[j][i][T]) capacity 1
  - (node[j−1][i][F], node[j][i][F]) capacity 1

*Sink connections:* for each variable xᵢ:
- (node[m][i][T], t) capacity 1
- (node[m][i][F], t) capacity 1

Total arcs: 2nm + 5n + m

**Step 4: Define homologous pairs.**

For each clause stage j, for each literal of Cⱼ involving variable xᵢ:
- If xᵢ ∈ Cⱼ (positive literal): pair entry arc (node[j−1][i][F], γⱼ) with exit arc (δⱼ, node[j][i][F])
- If ¬xᵢ ∈ Cⱼ (negative literal): pair entry arc (node[j−1][i][T], γⱼ) with exit arc (δⱼ, node[j][i][T])

The homologous pairs prevent flow "mixing" at the bottleneck: flow entering the collector from variable i must exit the distributor to variable i, not to some other variable j.

Total homologous pairs: L (one per literal occurrence)

**Step 5: Set flow requirement R = n.**
````


=== Overhead

````
| Target metric | Formula |
|---|---|
| `num_vertices` | `2 * num_vars * num_clauses + 3 * num_vars + 2 * num_clauses + 2` |
| `num_arcs` | `2 * num_vars * num_clauses + 5 * num_vars + num_clauses` |
| `requirement` | `num_vars` |
````


=== Correctness

````
Closed-loop test: enumerate all 2ⁿ truth assignments for a small source SAT instance, verify that each satisfying assignment induces a feasible flow of value n in the target network, and that no feasible flow of value n exists for unsatisfying assignments.
````


=== Correctness

````
**(⇒) Satisfiable → feasible flow.** Given a satisfying assignment σ for φ, route flow as follows: for each variable xᵢ, send 1 unit from s through splitᵢ along the T channel if σ(xᵢ) = true, or the F channel if σ(xᵢ) = false. In each clause stage j, the "literal" channels (those whose Kⱼ-literal would be true under σ) attempt to flow through the bottleneck. Because σ satisfies Cⱼ, at least one literal of Cⱼ is true, meaning at least one literal of Kⱼ is false. Thus at most kⱼ − 1 literal channels carry flow 1, fitting within the bottleneck capacity kⱼ − 1. The homologous arc pairing is satisfied because each variable's channel enters and exits γⱼ/δⱼ as a matched pair. Total flow reaching t equals n = R.

**(⇐) Feasible flow → satisfiable.** If a feasible flow of value ≥ n exists, then since s has exactly n outgoing arcs of capacity 1, each variable contributes exactly 1 unit. Each unit selects exactly one of the T or F channels (by conservation at splitᵢ), defining a truth assignment σ. In each clause stage j, the bottleneck (capacity kⱼ − 1) limits the number of literal flows to at most kⱼ − 1. The homologous pairs prevent mixing: flow from variable i entering γⱼ cannot exit to variable i′ at δⱼ. Therefore at least one literal of Kⱼ has flow 0, meaning that literal is false in Kⱼ, so the corresponding literal of Cⱼ is true. Every clause of φ is thus satisfied by σ.
````


=== Example

````
**Source:** φ = (x₁ ∨ x₂) ∧ (¬x₁ ∨ x₃) ∧ (¬x₂ ∨ ¬x₃) ∧ (x₁ ∨ x₃)

n = 3, m = 4, L = 8. All clauses have 2 literals, so all bottleneck capacities = 1.

Unique satisfying assignment: x₁ = T, x₂ = F, x₃ = T.

**Clause stage routing:**

| Stage | Clause | Literals in Kⱼ | x₁ routing | x₂ routing | x₃ routing |
|-------|--------|-----------------|------------|------------|------------|
| 1 | C₁ = x₁ ∨ x₂ | ¬x₁, ¬x₂ | F thru bottleneck | F thru bottleneck | bypass |
| 2 | C₂ = ¬x₁ ∨ x₃ | x₁, ¬x₃ | T thru bottleneck | bypass | F thru bottleneck |
| 3 | C₃ = ¬x₂ ∨ ¬x₃ | x₂, x₃ | bypass | T thru bottleneck | T thru bottleneck |
| 4 | C₄ = x₁ ∨ x₃ | ¬x₁, ¬x₃ | F thru bottleneck | bypass | F thru bottleneck |

**Constructed network:** 43 vertices, 43 arcs, 8 homologous pairs, R = 3.

**Homologous pairs:**
1. Stage 1: (node[0][1][F]→γ₁, δ₁→node[1][1][F]), (node[0][2][F]→γ₁, δ₁→node[1][2][F])
2. Stage 2: (node[1][1][T]→γ₂, δ₂→node[2][1][T]), (node[1][3][F]→γ₂, δ₂→node[2][3][F])
3. Stage 3: (node[2][2][T]→γ₃, δ₃→node[3][2][T]), (node[2][3][T]→γ₃, δ₃→node[3][3][T])
4. Stage 4: (node[3][1][F]→γ₄, δ₄→node[4][1][F]), (node[3][3][F]→γ₄, δ₄→node[4][3][F])

---

**YES trace (x₁=T, x₂=F, x₃=T):** Variable stage: T₁=1, F₂=1, T₃=1.

| Stage | Bottleneck entries | Load | Cap | Result |
|-------|--------------------|------|-----|--------|
| 1 | F₁=0, F₂=1 | 1 | 1 | ✓ |
| 2 | T₁=1, F₃=0 | 1 | 1 | ✓ |
| 3 | T₂=0, T₃=1 | 1 | 1 | ✓ |
| 4 | F₁=0, F₃=0 | 0 | 1 | ✓ |

Total flow = 3 = R. ✓

**NO trace (x₁=T, x₂=T, x₃=T):** Variable stage: T₁=1, T₂=1, T₃=1.

| Stage | Bottleneck entries | Load | Cap | Result |
|-------|--------------------|------|-----|--------|
| 1 | F₁=0, F₂=0 | 0 | 1 | ✓ |
| 2 | T₁=1, F₃=0 | 1 | 1 | ✓ |
| 3 | T₂=1, T₃=1 | **2** | 1 | **✗** |

Stage 3 bottleneck overloaded (load 2 > cap 1). Conservation violated at γ₃. No feasible flow of value 3 exists. Correctly rejects: C₃ = (¬x₂ ∨ ¬x₃) = (F ∨ F) = F. ✓
````


#pagebreak()


= SchedulingToMinimizeWeightedCompletionTime


== SchedulingToMinimizeWeightedCompletionTime $arrow.r$ ILP #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#783)]


#theorem[
  SchedulingToMinimizeWeightedCompletionTime polynomial-time reduces to ILP.
]


=== Construction

````
Given a SchedulingToMinimizeWeightedCompletionTime instance with n = |T| tasks, m processors, lengths l(t), and weights w(t):

Let M = Σ_{t ∈ T} l(t) (total processing time, used as big-M constant).

1. Create n·m binary **assignment variables** x_{t,p} ∈ {0,1}, where x_{t,p} = 1 means task t is assigned to processor p.
2. Create n integer **completion time variables** C_t, representing the completion time of task t.
3. Create n·(n−1)/2 binary **ordering variables** y_{i,j} ∈ {0,1} (for each pair i < j), where y_{i,j} = 1 means task i is scheduled before task j on their shared processor.
4. Set the objective to **minimize** Σ_{t ∈ T} w(t) · C_t.
5. Add **assignment constraints**: for each task t, Σ_{p=0}^{m-1} x_{t,p} = 1 (each task on exactly one processor). [n constraints]
6. Add **bound constraints**: for each task t, l(t) ≤ C_t ≤ M; for each (t,p), x_{t,p} ≤ 1; for each pair i < j, y_{i,j} ≤ 1. [2n + nm + n(n−1)/2 constraints]
7. Add **ordering constraints**: for each pair (i,j) with i < j and each processor p:
   - C_j − C_i ≥ l(j) − M·(3 − x_{i,p} − x_{j,p} − y_{i,j})
   - C_i − C_j ≥ l(i) − M·(2 − x_{i,p} − x_{j,p} + y_{i,j})

   When x_{i,p} = x_{j,p} = 1 and y_{i,j} = 1: enforces C_j ≥ C_i + l(j) (i before j on processor p).
   When x_{i,p} = x_{j,p} = 1 and y_{i,j} = 0: enforces C_i ≥ C_j + l(i) (j before i on processor p).
   When tasks are on different processors: constraints are slack due to big-M. [2·m·n·(n−1)/2 = m·n·(n−1) constraints]

**Solution extraction:** From the ILP solution, read the assignment variables: config[t] = p where x_{t,p} = 1.
````


=== Overhead

````
| Target metric | Formula |
|---|---|
| `num_vars` | `num_tasks * num_processors + num_tasks + num_tasks * (num_tasks - 1) / 2` |
| `num_constraints` | `3 * num_tasks + num_tasks * num_processors + num_tasks * (num_tasks - 1) / 2 + num_processors * num_tasks * (num_tasks - 1)` |

For the example (n=5, m=2): 25 variables, 75 constraints.
````


=== Correctness

````
Closed-loop test: construct a scheduling instance, reduce to ILP, solve ILP with brute force, extract solution back to scheduling, and verify optimality against direct brute-force solve.
````


=== Example

````
**Source (SchedulingToMinimizeWeightedCompletionTime):**
n = 5 tasks, m = 2 processors.
lengths = [1, 2, 3, 4, 5], weights = [6, 4, 3, 2, 1].

(Same example as #505.)

**Target (ILP):**
- 10 binary assignment variables x_{t,p} (5 tasks × 2 processors)
- 5 integer completion time variables C_0, ..., C_4
- 10 binary ordering variables y_{i,j} for i < j
- Total: 25 variables
- Minimize: 6·C_0 + 4·C_1 + 3·C_2 + 2·C_3 + 1·C_4
- Subject to: 75 constraints (5 assignment + 20 bounds + 10 var bounds + 40 ordering)
- M = 1 + 2 + 3 + 4 + 5 = 15

**Optimal ILP solution:**
- Assignment: x_{0,0}=x_{2,0}=x_{4,0}=1, x_{1,1}=x_{3,1}=1 (P0 = {t_0, t_2, t_4}, P1 = {t_1, t_3})
- Completion times: C_0=1, C_1=2, C_2=4, C_3=6, C_4=9
- Objective: 6·1 + 4·2 + 3·4 + 2·6 + 1·9 = 47

**Extracted scheduling solution:** config = [0, 1, 0, 1, 0] (processor assignments).

This matches the brute-force optimal from #505, confirming the ILP formulation is correct.
````


#pagebreak()


= VERTEX COVER


== VERTEX COVER $arrow.r$ HAMILTONIAN CIRCUIT #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#198)]


#theorem[
  VERTEX COVER polynomial-time reduces to HAMILTONIAN CIRCUIT.
]


=== Construction

````
> Theorem 3.4 HAMILTONIAN CIRCUIT is NP-complete
> Proof: It is easy to see that HC E NP, because a nondeterministic algorithm need only guess an ordering of the vertices and check in polynomial time that all the required edges belong to the edge set of the given graph.
>
> We transform VERTEX COVER to HC. Let an arbitrary instance of VC be given by the graph G = (V,E) and the positive integer K 
> Once more our construction can be viewed in terms of components connected together by communication links. First, the graph G' has K "selector" vertices a1,a2, . . . , aK, which will be used to select K vertices from the vertex set V for G. Second, for each edge in E, G' contains a "cover-testing" component that will be used to ensure that at least one endpoint of that edge is among the selected K vertices. The component for e = {u,v} E E is illustrated in Figure 3.4. It has 12 vertices,
>
> V'_e = {(u,e,i),(v,e,i): 1 
> and 14 edges,
>
> E'_e = {{(u,e,i),(u,e,i+1)},{(v,e,i),(v,e,i+1)}: 1       U {{(u,e,3),(v,e,1)},{(v,e,3),(u,e,1)}}
>      U {{(u,e,6),(v,e,4)},{(v,e,6),(u,e,4)}}
>
> In the completed construction, the only vertices from this cover-testing component that will be involved in any additional edges are (u,e,1), (v,e,1), (u,e,6), and (v,e,6). This will imply, as the reader may readily verify, that any Hamiltonian circuit of G' will have to meet the edges in E'_e in exactly one of the three configurations shown in Figure 3.5. Thus, for example, if the circuit "enters" this component at (u,e,1), it will have to "exit" at (u,e,6) and visit either all 12 vertices in the component or just the 6 vertices (u,e,i), 1 
> Additional edges in our overall construction will serve to join pairs of cover-testing components or to join a cover-testing component to a selector vertex. For each vertex v E V, let the edges incident on v be ordered (arbitrarily) as e_{v[1]}, e_{v[2]}, . . . , e_{v[deg(v)]}, where deg(v) denotes the degree of v in G, that is, the number of edges incident on v. All the cover-testing components corresponding to these edges (having v as endpoint) are joined together by the following connecting edges:
>
> E'_v = {{(v,e_{v[i]},6),(v,e_{v[i+1]},1)}: 1 
> As shown in Figure 3.6, this creates a single path in G' that includes exactly those vertices (x,y,z) having x = v.
>
> The final connecting edges in G' join the first and last vertices from each of these paths to every one of the selector vertices a1,a2, . . . , aK. These edges are specified as follows:
>
> E'' = {{a_i,(v,e_{v[1]},1)},{a_i,(v,e_{v[deg(v)]},6)}: 1 
> The completed graph G' = (V',E') has
>
> V' = {a_i: 1 
> and
>
> E' = (U_{e E E} E'_e) U (U_{v E V} E'_v) U E''
>
> It is not hard to see that G' can be constructed from G and K in polynomial time.
>
> We claim that G' has a Hamiltonian circuit if and only if G has a vertex cover of size K or less. Suppose , where n = |V'|, is a Hamiltonian circuit for G'. Consider any portion of this circuit that begins at a vertex in the set {a1,a2, . . . , aK}, ends at a vertex in {a1,a2, . . . , aK}, and that encounters no such vertex internally. Because of the previously mentioned restrictions on the way in which a Hamiltonian circuit can pass through a cover-testing component, this portion of the circuit must pass through a set of cover-testing components corresponding to exactly those edges from E that are incident on some one particular vertex v E V. Each of the cover-testing components is traversed in one of the modes (a), (b), or (c) of Figure 3.5, and no vertex from any other cover-testing component is encountered. Thus the K vertices from {a1,a2, . . . , aK} divide the Hamiltonian circuit into K paths, each path corresponding to a distinct vertex v E V. Since the Hamiltonian circuit must include all vertices from every one of the cover-testing components, and since vertices from the cover-testing component for edge e E E can be traversed only by a path corresponding to an endpoint of e, every edge in E must h
...(truncated)
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source MinimumVertexCover instance (|V|)
- m = `num_edges` of source MinimumVertexCover instance (|E|)
- k = cover size bound parameter (K)

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_vertices` | `12 * num_edges + k` |
| `num_edges` | `16 * num_edges - num_vertices + 2 * k * num_vertices` |

**Derivation:**
- Vertices: each of the m edge gadgets has 12 vertices, plus k selector vertices → 12m + k
- Edges:
  - 14 per gadget (5+5 chain edges + 4 cross-links) × m gadgets = 14m
  - Vertex path edges: for each vertex v, deg(v)−1 chain edges; total = ∑_v (deg(v)−1) = 2m − n
  - Selector connections: k selectors × n vertices × 2 endpoints = 2kn
  - Total = 14m + (2m − n) + 2kn = 16m − n + 2kn
````


=== Correctness

````

- Closed-loop test: reduce a small MinimumVertexCover instance (G, K) to HamiltonianCircuit G', solve G' with BruteForce, then verify that if a Hamiltonian circuit exists, the corresponding K vertices form a valid vertex cover of G, and vice versa.
- Test with a graph that has a known minimum vertex cover (e.g., a path graph P_n has minimum VC of size n−1) and verify the HC instance has a Hamiltonian circuit iff the cover size K ≥ minimum.
- Test with K < minimum VC size to confirm no Hamiltonian circuit is found.
- Verify vertex and edge counts in G' match the formulas: |V'| = 12m + k, |E'| = 16m − n + 2kn.
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 4 vertices {0, 1, 2, 3} and 6 edges (K_4):
- Edges (indexed): e_0={0,1}, e_1={0,2}, e_2={0,3}, e_3={1,2}, e_4={1,3}, e_5={2,3}
- n = 4, m = 6, K = 3
- Minimum vertex cover of size 3: {0, 1, 2} covers all edges

**Constructed target instance (HamiltonianCircuit):**
- Vertex count: 12 × 6 + 3 = 75 vertices
- Edge count: 16 × 6 − 4 + 2 × 3 × 4 = 96 − 4 + 24 = 116 edges

Gadget for e_0 = {0,1}: vertices (0,e_0,1)...(0,e_0,6) and (1,e_0,1)...(1,e_0,6) with internal edges:
- Chains: {(0,e_0,i),(0,e_0,i+1)} and {(1,e_0,i),(1,e_0,i+1)} for i=1..5 (10 edges)
- Cross-links: {(0,e_0,3),(1,e_0,1)}, {(1,e_0,3),(0,e_0,1)}, {(0,e_0,6),(1,e_0,4)}, {(1,e_0,6),(0,e_0,4)} (4 edges)

Vertex path for vertex 0 (incident edges: e_0, e_1, e_2):
- Chain edges: {(0,e_0,6),(0,e_1,1)}, {(0,e_1,6),(0,e_2,1)} (2 edges)

Selector connections for a_1 and vertex 0:
- {a_1, (0,e_0,1)}, {a_1, (0,e_2,6)} (entry/exit of vertex 0's path)

**Solution mapping (vertex cover {0,1,2} with K=3, assigning a_1↔0, a_2↔1, a_3↔2):**
- For e_0={0,1}: both in cover → mode (b): traverse all 12 vertices of gadget e_0
- For e_3={1,2}: both in cover → mode (b): traverse all 12 vertices of gadget e_3
- For e_1={0,2}: both in cover → mode (b): traverse all 12 vertices of gadget e_1
- For e_2={0,3}: only 0 in cover → mode (a): traverse only the 0-side (6 vertices)
- For e_4={1,3}: only 1 in cover → mode (a): traverse only the 1-side (6 vertices)
- For e_5={2,3}: only 2 in cover → mode (a): traverse only the 2-side (6 vertices)
- Circuit: a_1 → [gadgets for vertex 0] → a_2 → [gadgets for vertex 1] → a_3 → [gadgets for vertex 2] → a_1
- All 75 vertices are visited exactly once ✓
````


#pagebreak()


== VERTEX COVER $arrow.r$ MINIMUM CUT INTO BOUNDED SETS #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#250)]


=== Reference

````
> [ND17] MINIMUM CUT INTO BOUNDED SETS
> INSTANCE: Graph G=(V,E), positive integers K and J.
> QUESTION: Can V be partitioned into J disjoint sets V_1,...,V_J such that each |V_i| Reference: [Garey and Johnson, 1979]. Transformation from VERTEX COVER.
> Comment: NP-complete even for J=2.
````


#theorem[
  VERTEX COVER polynomial-time reduces to MINIMUM CUT INTO BOUNDED SETS.
]


=== Construction

````


**Summary:**
Given a MinimumVertexCover instance (G = (V, E), k) where G is an undirected graph with n = |V| vertices and m = |E| edges, construct a MinimumCutIntoBoundedSets instance (G', s, t, B, K) as follows:

1. **Graph construction:** Start with the original graph G = (V, E). Add two special vertices s and t (the source and sink). Connect s to every vertex in V with an edge, and connect t to every vertex in V with an edge.

2. **Weight assignment:** Assign weight 1 to all edges in E (original graph edges). Assign large weight M = m + 1 to all edges incident to s and t. This ensures that in any optimal cut, no edges between s/t and V are cut (they are too expensive).

   Alternatively, a simpler construction for the unit-weight, J=2 case:
   - Create a new graph G' from G by adding n - 2k isolated vertices (padding vertices) to make the total vertex count N = 2n - 2k (so each side of a balanced partition has exactly n - k vertices).
   - Choose s as any vertex in V and t as any other vertex in V (or as newly added vertices).
   - Set B = n - k (each partition side has at most n - k vertices) and cut bound K' related to k.

3. **Key encoding idea:** A minimum vertex cover of size k in G corresponds to a balanced partition where the k cover vertices are on one side and the n - k non-cover vertices are on the other side. The number of cut edges equals the number of edges with at least one endpoint in the cover, which relates to the vertex cover structure. The balance constraint prevents trivially putting all vertices on one side.

4. **Size bound parameter:** B = ceil(|V'|/2) for the bisection variant.

5. **Cut bound parameter:** The cut weight is set to correspond to the number of edges incident to the vertex cover.

6. **Solution extraction:** Given a balanced partition (V1, V2) with cut weight  SIMPLE MAX CUT -> MINIMUM CUT INTO BOUNDED SETS. The key difficulty is the balance constraint B on partition sizes.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source MinimumVertexCover instance (|V|)
- m = `num_edges` of source MinimumVertexCover instance (|E|)
- k = cover size bound parameter

| Target metric (code name) | Polynomial (using symbols above) |
|---------------------------|----------------------------------|
| `num_vertices` | `num_vertices + 2` |
| `num_edges` | `num_edges + 2 * num_vertices` |

**Derivation (with s,t construction):**
- Vertices: original n vertices plus s and t = n + 2
- Edges: original m edges plus n edges from s to each vertex plus n edges from t to each vertex = m + 2n
````


=== Correctness

````


- Closed-loop test: reduce a MinimumVertexCover instance to MinimumCutIntoBoundedSets, solve target with BruteForce (enumerate all partitions with s in V1 and t in V2, check size bounds, compute cut weight), extract vertex cover from partition, verify it covers all edges
- Test with a graph with known minimum vertex cover (e.g., star graph K_{1,n-1} has minimum VC of size 1)
- Test with both feasible and infeasible VC bounds to verify bidirectional correctness
- Verify vertex and edge counts match the overhead formulas
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 7 edges:
- Edges: {0,1}, {0,2}, {1,2}, {1,3}, {2,4}, {3,4}, {4,5}
- n = 6, m = 7
- Minimum vertex cover: size k = 3, e.g., {1, 2, 4} covers all edges:
  - {0,1}: 1 in cover. {0,2}: 2 in cover. {1,2}: both. {1,3}: 1 in cover.
  - {2,4}: both. {3,4}: 4 in cover. {4,5}: 4 in cover.

**Constructed target instance (MinimumCutIntoBoundedSets):**

Graph G' with 8 vertices {0, 1, 2, 3, 4, 5, s, t} and 7 + 12 = 19 edges:
- Original edges: {0,1}, {0,2}, {1,2}, {1,3}, {2,4}, {3,4}, {4,5} (weight 1 each)
- s-edges: {s,0}, {s,1}, {s,2}, {s,3}, {s,4}, {s,5} (weight M = 8 each)
- t-edges: {t,0}, {t,1}, {t,2}, {t,3}, {t,4}, {t,5} (weight M = 8 each)

Parameters: B = 7 (each side at most 7 vertices), s in V1, t in V2.

**Solution mapping:**
- Any optimal partition avoids cutting the heavy s-edges and t-edges.
- Partition: V1 = {s, 0, 3, 5} (vertices not in cover plus s), V2 = {t, 1, 2, 4} (cover vertices plus t)
- Cut edges (weight 1 each): {0,1}, {0,2}, {1,3}, {3,4}, {4,5} = 5 cut edges
- |V1| = 4 <= B, |V2| = 4 <= B
- Extracted vertex cover: vertices on t's side = {1, 2, 4}
- Verification: all 7 original edges have at least one endpoint in {1, 2, 4}
````


#pagebreak()


== VERTEX COVER $arrow.r$ MINIMIZING DUMMY ACTIVITIES IN PERT NETWORKS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#374)]


=== Reference

````
> [ND44] MINIMIZING DUMMY ACTIVITIES IN PERT NETWORKS
> INSTANCE: Directed acyclic graph G=(V,A) where vertices represent tasks and the arcs represent precedence constraints, and a positive integer K≤|V|.
> QUESTION: Is there a PERT network corresponding to G with K or fewer dummy activities, i.e., a directed acyclic graph G'=(V',A') where V'={v_i^−,v_i^+: v_i∈V} and {(v_i^−,v_i^+): v_i∈V}⊆A', and such that |A'|≤|V|+K and there is a path from v_i^+ to v_j^− in G' if and only if there is a path from v_i to v_j in G?
> Reference: [Krishnamoorthy and Deo, 1977b]. Transformation from VERTEX COVER.
````


#theorem[
  VERTEX COVER polynomial-time reduces to MINIMIZING DUMMY ACTIVITIES IN PERT NETWORKS.
]


=== Construction

````


**Summary:**
Given a MinimumVertexCover instance (undirected graph G = (V, E) with unit weights), construct a MinimumDummyActivitiesPert instance and map solutions back.

**Construction (forward map):**

1. **Orient edges to form a DAG:** For each edge {u, v} in E with u < v, create a directed arc (u, v). Since arcs always go from lower to higher index, the result is a DAG. The DAG has |V| vertices (tasks) and |E| arcs (precedence constraints).

2. **Build the MinimumDummyActivitiesPert instance:** Pass the DAG directly as the `graph` field of `MinimumDummyActivitiesPert::new(dag)`. The target instance has one binary decision variable per arc: for arc (u, v), the variable is 1 (merge u's finish event with v's start event) or 0 (insert a dummy activity from u's finish event to v's start event).

3. **PERT network semantics:** The target model creates two event endpoints per task -- start(i) = 2i, finish(i) = 2i+1 -- connected by a task arc. When merge_bit = 1 for arc (u, v), the union-find merges finish(u) with start(v) into one event node. When merge_bit = 0, a dummy arc is added from finish(u)'s event to start(v)'s event. The configuration is valid when: (a) no task's start and finish collapse to the same event, (b) the event graph is acyclic, and (c) task-to-task reachability in the event network matches the original DAG exactly.

4. **Objective:** The target minimizes the number of dummy arcs (arcs with merge_bit = 0 that are not already implied by task arcs). The minimum vertex cover size of G corresponds to the minimum number of dummy activities in the constructed PERT instance.

**Solution extraction (reverse map):**

Given an optimal PERT configuration (a binary vector over arcs), extract a vertex cover of G:
- For each arc (u, v) with merge_bit = 0 (dummy activity), at least one of {u, v} must be in the cover.
- Collect all vertices that appear as an endpoint of a dummy arc. Since every edge of G is represented as an arc, and each arc is either merged or dummy, the dummy arcs identify uncovered edges. The endpoints of dummy arcs form a vertex cover.
- More precisely: for each dummy arc (u, v), add both u and v to a candidate set, then greedily remove vertices whose removal still leaves a valid cover.

**Correctness sketch:**
The key insight is that merging finish(u) with start(v) is "free" (no dummy needed) but constrains the event topology. Two merges that create a cycle or violate reachability are forbidden. In the DAG derived from an undirected graph by index ordering, the minimum number of arcs that cannot be merged (i.e., must remain as dummy activities) equals the minimum vertex cover of the original graph. Each dummy arc corresponds to an edge "covered" by one of its endpoints needing a separate event node.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source MinimumVertexCover instance
- m = `num_edges` of source MinimumVertexCover instance

| Target metric (code name) | Expression |
|----------------------------|------------|
| `num_vertices` | `num_vertices` |
| `num_arcs` | `num_edges` |

**Derivation:**
- The DAG has n vertices (one per vertex of G, these are the "tasks")
- The DAG has m arcs (one per edge of G, oriented by vertex index)
- The target's `num_vertices()` returns the number of task vertices in the DAG = n
- The target's `num_arcs()` returns the number of precedence arcs in the DAG = m
````


=== Correctness

````


- Closed-loop test: reduce MinimumVertexCover instance to MinimumDummyActivitiesPert, solve target with BruteForce, extract solution, verify vertex cover on source graph
- Verify that optimal MVC value equals optimal MinimumDummyActivitiesPert value on the constructed instance
- Test with small graphs where the answer is known (e.g., paths, triangles, complete bipartite graphs)
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 4 vertices {0, 1, 2, 3} and 4 edges:
- Edges: {0,1}, {0,2}, {1,3}, {2,3}
- Unit weights: [1, 1, 1, 1]
- Optimal vertex cover: {0, 3} with value Min(2)

**Vertex cover verification for {0, 3}:**
- {0,1}: vertex 0 ✓
- {0,2}: vertex 0 ✓
- {1,3}: vertex 3 ✓
- {2,3}: vertex 3 ✓
- Valid cover of size 2 ✓

**Constructed target instance (MinimumDummyActivitiesPert):**

Step 1 -- Orient edges by vertex index to form DAG:
- Edge {0,1} -> arc (0,1)
- Edge {0,2} -> arc (0,2)
- Edge {1,3} -> arc (1,3)
- Edge {2,3} -> arc (2,3)

DAG: 4 vertices, 4 arcs: (0,1), (0,2), (1,3), (2,3)

Step 2 -- Target instance: `MinimumDummyActivitiesPert::new(DirectedGraph::new(4, vec![(0,1), (0,2), (1,3), (2,3)]))`

**PERT event endpoints (before merging):**
- Task 0: start=0, finish=1
- Task 1: start=2, finish=3
- Task 2: start=4, finish=5
- Task 3: start=6, finish=7

**Optimal PERT configuration: [1, 1, 0, 0]**
(arc index order matches arc list: arc 0=(0,1), arc 1=(0,2), arc 2=(1,3), arc 3=(2,3))

- Arc (0,1), bit=1: merge finish(0)=1 with start(1)=2 -> events {1,2}
- Arc (0,2), bit=1: merge finish(0)=1 with start(2)=4 -> events {1,2,4}
- Arc (1,3), bit=0: dummy arc from finish(1)=3's event to start(3)=6's event
- Arc (2,3), bit=0: dummy arc from finish(2)=5's event to start(3)=6's event

**Resulting event graph:**
Event nodes after union-find (dense labeling):
- Event A = {0} (start of task 0)
- Event B = {1,2,4} (finish of task 0 = start of task 1 = start of task 2)
- Event C = {3} (finish of task 1)
- Event D = {5} (finish of task 2)
- Event E = {6} (start of task 3)
- Event F = {7} (finish of task 3)

Task arcs: A->B (task 0), B->C (task 1), B->D (task 2), E->F (task 3)
Dummy arcs: C->E (for precedence 1->3), D->E (for precedence 2->3)

Number of dummy activities = 2 (matches optimal vertex cover size) ✓

**Reachability verification:**
- 0->1: A->B->C (via task 0 then task 1) ✓
- 0->2: A->B->D (via task 0 then task 2) ✓
- 0->3: A->B->C-
...(truncated)
````


#pagebreak()


== VERTEX COVER $arrow.r$ SET BASIS #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#383)]


=== Reference

````
> [SP7] SET BASIS
> INSTANCE: Collection C of subsets of a finite set S, positive integer K≤|C|.
> QUESTION: Is there a collection B of subsets of S with |B|=K such that, for each c∈C, there is a subcollection of B whose union is exactly c?
> Reference: [Stockmeyer, 1975]. Transformation from VERTEX COVER.
> Comment: Remains NP-complete if all c∈C have |c|≤3, but is trivial if all c∈C have |c|≤2.
````


#theorem[
  VERTEX COVER polynomial-time reduces to SET BASIS.
]


=== Construction

````


**Summary:**
Given a MinimumVertexCover instance (G = (V, E), K) where G is a graph with n vertices and m edges, and K is the vertex cover size bound, construct a SetBasis instance as follows:

1. **Define the ground set:** S = E (the edge set of G). Each element of S is an edge of the original graph.
2. **Define the collection C:** For each vertex v ∈ V, define c_v = { e ∈ E : v is an endpoint of e } (the set of edges incident to v). The collection C = { c_v : v ∈ V } contains one subset per vertex.
3. **Define the basis size bound:** Set the basis size to K (same as the vertex cover bound).
4. **Additional target sets:** Include in C the set of all edges E itself (the full ground set), so that the basis must also be able to reconstruct E via union. This enforces that the basis elements collectively cover all edges.

**Alternative construction (Stockmeyer's original):**
The precise construction by Stockmeyer encodes the vertex cover structure into a set basis problem. The key idea is:

1. **Ground set:** S = E ∪ V' where V' contains auxiliary elements encoding vertex identities.
2. **Collection C:** For each edge e = {u, v} ∈ E, create a target set c_e = {u', v', e} containing the two vertex-identity elements and the edge element.
3. **Basis size:** K' = K (the vertex cover bound).
4. **Correctness:** A vertex cover of size K in G corresponds to K basis sets (one per cover vertex), where each basis set for vertex v contains v' and all edges incident to v. Each target set c_e = {u', v'} ∪ {e} can be reconstructed from the basis sets of u and v (at least one of which is in the cover).

**Correctness argument (for the edge-incidence construction):**
- (Forward) If V' ⊆ V is a vertex cover of size K, define basis B = { c_v : v ∈ V' }. For each vertex u ∈ V, the set c_u (edges incident to u) must be expressible as a union of basis sets. Since V' is a vertex cover, every edge e incident to u has at least one endpoint in V'. Thus c_u = ∪{c_v ∩ c_u : v ∈ V'} can be reconstructed if the basis elements partition appropriately.
- The exact construction details depend on Stockmeyer's original paper, which ensures the correspondence is tight.

**Note:** The full technical details of this reduction are from Stockmeyer's IBM Research Report (1975), which is not widely available online. The construction above captures the essential structure.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_items` (ground set size \|S\|) | `num_vertices + num_edges` |
| `num_sets` (collection size \|C\|) | `num_edges` |
| `basis_size` (K) | `K` (same as vertex cover bound) |

**Derivation:** In Stockmeyer's construction, the ground set S contains elements for both vertices and edges (|S| = n + m). The collection C has one target set per edge (|C| = m), each of size 3 (two vertex-identity elements plus the edge element). The basis size K is preserved from the vertex cover instance.
````


=== Correctness

````

- Closed-loop test: reduce source MinimumVertexCover instance to SetBasis, solve target with BruteForce (enumerate all K-subsets of candidate basis sets), extract solution, map basis sets back to vertices, verify the extracted vertices form a valid vertex cover on the original graph
- Compare with known results from literature: a triangle graph K_3 has minimum vertex cover of size 2; the reduction should produce a set basis instance with minimum basis size 2
- Verify the boundary case: all c ∈ C have |c| ≤ 3 (matching GJ's remark that the problem remains NP-complete in this case)
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 5 vertices {0, 1, 2, 3, 4} and 6 edges:
- Edges: e0={0,1}, e1={0,2}, e2={1,2}, e3={1,3}, e4={2,4}, e5={3,4}
- Minimum vertex cover has size K = 3: V' = {1, 2, 3}
  - e0={0,1}: covered by 1 ✓
  - e1={0,2}: covered by 2 ✓
  - e2={1,2}: covered by 1,2 ✓
  - e3={1,3}: covered by 1,3 ✓
  - e4={2,4}: covered by 2 ✓
  - e5={3,4}: covered by 3 ✓

**Constructed target instance (SetBasis) using edge-incidence construction:**
- Ground set: S = E = {e0, e1, e2, e3, e4, e5} (6 elements)
- Collection C (edge-incidence sets, one per vertex):
  - c_0 = {e0, e1} (edges incident to vertex 0)
  - c_1 = {e0, e2, e3} (edges incident to vertex 1)
  - c_2 = {e1, e2, e4} (edges incident to vertex 2)
  - c_3 = {e3, e5} (edges incident to vertex 3)
  - c_4 = {e4, e5} (edges incident to vertex 4)
- Basis size K = 3

**Solution mapping:**
Basis B = {c_1, c_2, c_3} (corresponding to vertex cover {1, 2, 3}):
- c_1 = {e0, e2, e3}, c_2 = {e1, e2, e4}, c_3 = {e3, e5}
- Reconstruct c_0 = {e0, e1}: need e0 from c_1 and e1 from c_2. But c_1 ∪ c_2 = {e0, e1, e2, e3, e4} ⊋ c_0. The union must be *exactly* c_0, not a superset.

This shows the simple edge-incidence construction does not directly work for Set Basis (which requires exact union, not cover). Stockmeyer's construction uses auxiliary elements to enforce exactness.

**Revised construction (with auxiliary elements per Stockmeyer):**
- Ground set: S = {v'_0, v'_1, v'_2, v'_3, v'_4, e0, e1, e2, e3, e4, e5} (|S| = 11)
- Collection C (one per edge, each of size 3):
  - c_{e0} = {v'_0, v'_1, e0} (for edge {0,1})
  - c_{e1} = {v'_0, v'_2, e1} (for edge {0,2})
  - c_{e2} = {v'_1, v'_2, e2} (for edge {1,2})
  - c_{e3} = {v'_1, v'_3, e3} (for edge {1,3})
  - c_{e4} = {v'_2, v'_4, e4} (for edge {2,4})
  - c_{e5} = {v'_3, v'_4, e5} (for edge {3,4})
- Basis size K = 3

Basis B corresponding to vertex cover {1, 2, 3}:
- b_1 = {v'_1, e0, e2, e3} (vertex 1: its identity + incident edges)
- b_2 = {v'_2, e1
...(truncated)
````


#pagebreak()


== VERTEX COVER $arrow.r$ COMPARATIVE CONTAINMENT #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#385)]


=== Reference

````
> [SP10] COMPARATIVE CONTAINMENT
> INSTANCE: Two collections R={R_1,R_2,...,R_k} and S={S_1,S_2,...,S_l} of subsets of a finite set X, weights w(R_i) in Z^+, 1 QUESTION: Is there a subset Y  Sum_{Y = Sum_{Y  Reference: [Plaisted, 1976]. Transformation from VERTEX COVER.
> Comment: Remains NP-complete even if all subsets in R and S have weight 1 [Garey and Johnson, ----].
````


#theorem[
  VERTEX COVER polynomial-time reduces to COMPARATIVE CONTAINMENT.
]


=== Construction

````
**Summary:**

Given a VERTEX COVER instance (graph G = (V, E), bound K), construct a COMPARATIVE CONTAINMENT instance as follows. Let n = |V| and m = |E|.

1. **Universe:** Let X = V (one element per vertex).
2. **Collection R (reward sets):** For each vertex v in V, create a set R_v = V \ {v} with weight w(R_v) = 1. This rewards Y for each vertex it does NOT include: Y subset of R_v iff v not in Y. Thus the total R-weight equals n - |Y|.
3. **Collection S (penalty sets):** Two kinds:
   - For each edge e = {u, v} in E, create S_e = V \ {u, v} with weight w(S_e) = n + 1. Then Y subset of S_e iff neither u nor v is in Y, i.e., edge e is uncovered. Each uncovered edge contributes a large penalty.
   - One budget set S_0 = V with weight w(S_0) = n - K. Since Y subset of V always holds, this contributes a constant penalty of n - K.
4. **Correctness:** The containment inequality becomes:
   (n - |Y|) >= (n + 1) * (number of uncovered edges) + (n - K)
   which simplifies to:
   K - |Y| >= (n + 1) * (number of uncovered edges).
   - If Y is a vertex cover with |Y| = 0. Satisfied.
   - If Y is a vertex cover with |Y| > K: the right side is 0 but K - |Y| = n + 1 > n >= K - |Y|. Not satisfied.
   Hence the inequality holds if and only if Y is a vertex cover of size at most K.
5. **Solution extraction:** The witness Y from the COMPARATIVE CONTAINMENT instance is directly the vertex cover.
````


=== Overhead

````
**Symbols:**
- n = |V| = `num_vertices` of source graph
- m = |E| = `num_edges` of source graph

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `universe_size`            | `num_vertices` (= n)             |
| `num_r_sets`               | `num_vertices` (= n)             |
| `num_s_sets`               | `num_edges + 1` (= m + 1)       |

**Derivation:** The universe X has one element per vertex. Collection R has one set per vertex. Collection S has one set per edge plus one budget set. Total construction is O(n^2 + mn) accounting for set contents.
````


=== Correctness

````
- Closed-loop test: reduce source VERTEX COVER instance, solve target COMPARATIVE CONTAINMENT with BruteForce, extract solution, verify on source
- Compare with known results from literature
- Test with small graphs (triangle, path, cycle) where vertex cover is known
````


=== Example

````
**Source instance (VERTEX COVER):**
Graph G with 6 vertices V = {v_0, v_1, v_2, v_3, v_4, v_5} and 7 edges:
E = { {v_0,v_1}, {v_0,v_2}, {v_1,v_2}, {v_1,v_3}, {v_2,v_4}, {v_3,v_4}, {v_4,v_5} }
Bound K = 3.
(A minimum vertex cover is {v_1, v_2, v_4} of size 3.)

**Constructed COMPARATIVE CONTAINMENT instance:**
Universe X = {v_0, v_1, v_2, v_3, v_4, v_5}, n = 6, m = 7.

Collection R (one set per vertex, weight 1 each):
- R_0 = {1, 2, 3, 4, 5}, w = 1
- R_1 = {0, 2, 3, 4, 5}, w = 1
- R_2 = {0, 1, 3, 4, 5}, w = 1
- R_3 = {0, 1, 2, 4, 5}, w = 1
- R_4 = {0, 1, 2, 3, 5}, w = 1
- R_5 = {0, 1, 2, 3, 4}, w = 1

Collection S (one set per edge with weight n + 1 = 7, plus one budget set):
- S_{0,1} = {2, 3, 4, 5}, w = 7
- S_{0,2} = {1, 3, 4, 5}, w = 7
- S_{1,2} = {0, 3, 4, 5}, w = 7
- S_{1,3} = {0, 2, 4, 5}, w = 7
- S_{2,4} = {0, 1, 3, 5}, w = 7
- S_{3,4} = {0, 1, 2, 5}, w = 7
- S_{4,5} = {0, 1, 2, 3}, w = 7
- S_budget = {0, 1, 2, 3, 4, 5}, w = n - K = 3

**Solution:**
Choose Y = {v_1, v_2, v_4}.

R-containment: Y is a subset of R_v iff v is not in Y. Vertices not in Y: {v_0, v_3, v_5}. So Y is contained in R_0, R_3, and R_5. R-weight = 3 (= n - |Y| = 6 - 3).

S-containment (edges): Y is a subset of S_e = V \ {u,v} iff neither u nor v is in Y. Since Y = {1,2,4} is a vertex cover, every edge has at least one endpoint in Y, so Y is NOT contained in any S_e. Edge S-weight = 0.

S-containment (budget): Y is a subset of V, so S_budget always contributes. Budget S-weight = 3.

Total S-weight = 0 + 3 = 3.

Comparison: R-weight (3) >= S-weight (3)? YES (tight equality).

This confirms the vertex cover {v_1, v_2, v_4} of size 3 maps to a feasible COMPARATIVE CONTAINMENT solution.

**Negative example:** Y = {v_1, v_3} (size 2, but NOT a vertex cover — edges {0,2}, {2,4}, {4,5} are uncovered).
R-weight = 6 - 2 = 4.
S-edge-weight: {0,2}: 0 not in Y, 2 not in Y — uncovered, contributes 7. {2,4}: uncovered, contributes 7. {4,5}: uncovered, contributes 7. Total edge penalty = 21.
S-budget = 3. 
...(truncated)
````


#pagebreak()


== VERTEX COVER $arrow.r$ HAMILTONIAN PATH #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#892)]


=== Reference

````
> GT39 HAMILTONIAN PATH
> INSTANCE: Graph G = (V,E).
> QUESTION: Does G contain a Hamiltonian path, that is, a path that visits each vertex in V exactly once?
> Reference: Chapter 3, [Garey and Johnson, 1979]. Transformation from VERTEX COVER.
````


#theorem[
  VERTEX COVER polynomial-time reduces to HAMILTONIAN PATH.
]


=== Construction

````

**Summary:**
Given a MinimumVertexCover instance (G = (V, E), K), construct a HamiltonianPath instance G'' as follows:

1. **First stage (VC → HC):** Apply the Theorem 3.4 construction to produce a HamiltonianCircuit instance G' = (V', E') with K selector vertices a₁, ..., a_K, cover-testing gadgets (12 vertices per edge), vertex path edges, and selector connection edges. See R279 for details.

2. **Second stage (HC → HP):** Modify G' to produce G'':
   - Add three new vertices: a₀, a_{K+1}, and a_{K+2}.
   - Add two pendant edges: {a₀, a₁} and {a_{K+1}, a_{K+2}}.
   - For each vertex v ∈ V, replace the edge {a₁, (v, e_{v[deg(v)]}, 6)} with {a_{K+1}, (v, e_{v[deg(v)]}, 6)}.

3. **Correctness:** a₀ and a_{K+2} have degree 1, so any Hamiltonian path must start/end at these vertices. The path runs a₀ → a₁ → [circuit body] → a_{K+1} → a_{K+2}. A Hamiltonian path exists in G'' iff a Hamiltonian circuit exists in G' iff G has a vertex cover of size ≤ K.

**Vertex count:** 12m + K + 3
**Edge count:** 16m − n + 2Kn + 2
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source MinimumVertexCover instance (|V|)
- m = `num_edges` of source MinimumVertexCover instance (|E|)
- K = cover size bound

| Target metric | Polynomial |
|---|---|
| `num_vertices` | `12 * num_edges + K + 3` |
| `num_edges` | `16 * num_edges - num_vertices + 2 * K * num_vertices + 2` |

**Derivation:**
- Vertices: 12m (gadgets) + K (selectors) + 3 (new vertices a₀, a_{K+1}, a_{K+2}) = 12m + K + 3
- Edges: from VC→HC we get 16m − n + 2Kn; the HC→HP step replaces n edges and adds 2, net +2: total = 16m − n + 2Kn + 2
````


=== Correctness

````

- Closed-loop test: construct a small MinimumVertexCover instance, reduce to HamiltonianPath, solve with BruteForce, verify a Hamiltonian path exists iff the graph has a vertex cover of size ≤ K.
- Verify that any Hamiltonian path found starts and ends at the degree-1 vertices a₀ and a_{K+2}.
- Test with a triangle (K₃, K=2): should have Hamiltonian path. With K=1: should not.
- Verify vertex and edge counts match formulas.
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 3 vertices {0, 1, 2} forming a path P₃:
- Edges: e₀={0,1}, e₁={1,2}
- n = 3, m = 2, K = 1
- Minimum vertex cover: {1} (covers both edges)

**Constructed target instance (HamiltonianPath):**
- Stage 1 (VC→HC): 12×2 + 1 = 25 vertices, 16×2 − 3 + 2×1×3 = 35 edges
- Stage 2 (HC→HP): +3 vertices, +2 edges → 28 vertices, 37 edges

**Solution mapping:**
- Vertex cover {1} with K=1 → Hamiltonian circuit in G' with selector a₁ routing through vertex 1's gadgets
- Modified to Hamiltonian path in G'': a₀ → a₁ → [traverse gadgets for vertex 1, covering both edge gadgets] → a₂ → a₃
- All 28 vertices visited exactly once ✓
````


#pagebreak()


== VERTEX COVER $arrow.r$ PARTIAL FEEDBACK EDGE SET #text(size: 8pt, fill: green)[ \[Type-incompatible (math verified)\] ] #text(size: 8pt, fill: gray)[(\#894)]


=== Reference

````
> GT9 PARTIAL FEEDBACK EDGE SET
> INSTANCE: Graph G = (V,E), positive integers K = 3.
> QUESTION: Is there a subset E' ⊆ E with |E'|  Reference: [Yannakakis, 1978b]. NP-complete for any fixed L >= 3. Transformation from VERTEX COVER.
````


#theorem[
  VERTEX COVER polynomial-time reduces to PARTIAL FEEDBACK EDGE SET.
]


=== Construction

````
**Status: INCOMPLETE — requires access to Yannakakis 1978b**

The Yannakakis construction reduces Vertex Cover to C_l-free Edge Deletion (equivalently, Partial Feedback Edge Set with cycle length bound L). The general framework for edge-deletion NP-completeness proofs uses vertex gadgets and edge gadgets following the Lewis-Yannakakis methodology.

The naive approach of creating one L-cycle per original edge (using L-2 new internal vertices per edge) creates m disjoint cycles that each require exactly one edge removal, yielding a minimum PFES of size m regardless of the vertex cover size. This does NOT produce a useful reduction because the PFES bound does not relate to the vertex cover bound k.

The actual Yannakakis construction must use a more sophisticated gadget structure where edges are shared between gadget cycles, so that removing edges incident to a single cover vertex simultaneously breaks multiple short cycles. The exact gadget is described in:

- Yannakakis, M. (1978b). "Node- and edge-deletion NP-complete problems." *Proceedings of the 10th Annual ACM Symposium on Theory of Computing (STOC)*, pp. 253-264.
- Yannakakis, M. (1981). "Edge-Deletion Problems." *SIAM Journal on Computing*, 10(2):297-309.

**Known facts about the reduction:**
- For L != 3, the reduction is a linear parameterized reduction (k' = O(k)).
- For L = 3, the reduction gives k' = O(|E(G)| + k), which is NOT a linear parameterized reduction.
- The construction is polynomial-time for any fixed L >= 3.

**What is missing:** The exact gadget structure, the precise bound formula K' as a function of (n, m, k, L), and the overhead expressions for num_vertices and num_edges in the target graph.
````


=== Overhead

````
| Target metric | Polynomial |
|---|---|
| `num_vertices` | Unknown — depends on exact Yannakakis construction |
| `num_edges` | Unknown — depends on exact Yannakakis construction |
````


=== Correctness

````
- Closed-loop test: construct a small MinimumVertexCover instance, reduce to PartialFeedbackEdgeSet, solve with BruteForce, verify correctness.
- Test that a graph with vertex cover of size k produces a PFES instance with the correct bound.
````


=== Example

````
Cannot be constructed without the exact reduction algorithm.
````


#pagebreak()


= Vertex Cover


== Vertex Cover $arrow.r$ Multiple Copy File Allocation #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#425)]


=== Reference

````
> [SR6] MULTIPLE COPY FILE ALLOCATION
> INSTANCE: Graph G = (V, E), for each v ∈ V a usage u(v) ∈ Z⁺ and a storage cost s(v) ∈ Z⁺, and a positive integer K.
> QUESTION: Is there a subset V' ⊆ V such that, if for each v ∈ V we let d(v) denote the number of edges in the shortest path in G from v to a member of V', we have
>
> ∑_{v ∈ V'} s(v) + ∑_{v ∈ V} d(v)·u(v) ≤ K ?
>
> Reference: [Van Sickle and Chandy, 1977]. Transformation from VERTEX COVER.
> Comment: NP-complete in the strong sense, even if all v ∈ V have the same value of u(v) and the same value of s(v).
````


#theorem[
  Vertex Cover polynomial-time reduces to Multiple Copy File Allocation.
]


=== Construction

````


**Summary:**
Given a MinimumVertexCover instance: graph G = (V, E) with |V| = n, |E| = m, and positive integer K_vc (vertex cover size bound), construct a Multiple Copy File Allocation instance as follows:

1. **Graph:** Use the same graph G' = G = (V, E).

2. **Storage costs:** For each vertex v ∈ V, set s(v) = 1 (uniform storage cost).

3. **Usage costs:** For each vertex v ∈ V, set u(v) = n + 1 (a large uniform usage, ensuring that any vertex at distance ≥ 2 from all copies incurs prohibitive cost).

4. **Bound:** Set K = K_vc + (n − K_vc)·(n + 1) = K_vc + (n − K_vc)(n + 1).
   - The K_vc term accounts for storage costs of the cover vertices.
   - The (n − K_vc)(n + 1) term accounts for usage costs: each non-cover vertex must be at distance exactly 1 from some cover vertex (since V' is a vertex cover, every vertex not in V' is adjacent to some vertex in V'), contributing d(v)·u(v) = 1·(n+1) = n+1.

   Wait — more carefully: if V' is a vertex cover of size K_vc, then every edge has at least one endpoint in V'. For v ∈ V', d(v) = 0. For v ∉ V', if v is isolated (no edges), then d(v) could be large; but if every vertex has at least one edge, then v has a neighbor in V', so d(v) ≤ 1.

   **Refined construction using the uniform-cost special case:**

   Since the problem is NP-complete even with uniform u(v) = u and s(v) = s for all v:

1. **Graph:** G' = G.

2. **Costs:** Set s(v) = 1 for all v, and u(v) = M for all v, where M = n·m + 1 (a sufficiently large value to penalize distance ≥ 2).

3. **Bound:** Set K = K_vc · 1 + (n − K_vc) · 1 · M = K_vc + (n − K_vc)·M.

4. **Correctness (forward):** If V' is a vertex cover of size K_vc, then:
   - Storage cost: ∑_{v ∈ V'} s(v) = K_vc.
   - For v ∈ V': d(v) = 0 (v is in V').
   - For v ∉ V': since V' is a vertex cover, every edge incident to v has its other endpoint in V'. Hence v is adjacent to some member of V', so d(v) ≤ 1. If v has at least one edge, d(v) = 1; if v is isolated, d(v) could be large, but we can add v to V' without affecting the cover (isolated vertices don't affect the cover).
   - Assuming G has no isolated vertices: usage cost = ∑_{v ∉ V'} 1 · M = (n − K_vc) · M.
   - Total = K_vc + (n − K_vc)·M = K ✓.

5. **Correctness (reverse):** If there exists V' ⊆ V with total cost ≤ K, then any vertex v ∉ V' with d(v) ≥ 2 would contribute d(v)·M ≥ 2M to the usage cost, making the total exceed K (since 2M > K for suitable M). Therefore, every v ∉ V' has d(v) ≤ 1, meaning every non-cover vertex is adjacent to some cover vertex. This implies V' is a vertex cover (every edge has an endpoint in V') — if some edge {u,w} had neither endpoint in V', both u and w would be non-cover, and we'd need d(u) ≤ 1 and d(w) ≤ 1, which is possible, but actually: the vertex cover property follows because with d(v) ≤ 1 for all non-cover vertices, the total cost is |V'| + (n − |V'|)·M ≤ K = K_vc + (n − K_vc)·M. Since M > n, this forces |V'| ≤ K_vc.

6. **Solution extraction:** Given a valid file allocation V' with cost ≤ K, the set V' is directly the vertex cover.

**Key invariant:** With large uniform usage cost M, placing a file copy at a vertex is equivalent to "covering" it; the budget K is calibrated so that exactly K_vc copies can be placed while keeping all non-cover vertices at distance 1.

**Time complexity of reduction:** O(n + m) to set up the instance.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G (|V|)
- m = `num_edges` of source graph G (|E|)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices`             | `num_vertices` (= n)             |
| `num_edges`                | `num_edges` (= m)                |

**Derivation:** The graph is unchanged. Storage and usage costs are uniform constants or O(n·m). The bound K is a derived parameter from K_vc, n, and M.
````


=== Correctness

````


- Closed-loop test: construct a MinimumVertexCover instance (G, K_vc), reduce to MultipleCopyFileAllocation, solve target by brute-force (enumerate all 2^n subsets V'), compute BFS distances and total cost, verify that V' achieving cost ≤ K is a vertex cover of size ≤ K_vc.
- Test with C_4 (4-cycle): K_vc = 2 (cover = {0, 2} or {1, 3}). With n = 4, m = 4, M = 17, K = 2 + 2·17 = 36. File placement at {0, 2}: storage = 2, usage = 2·1·17 = 34, total = 36 ≤ K ✓.
- Test with star K_{1,5}: K_vc = 1 (center vertex covers all edges). With n = 6, m = 5, M = 31, K = 1 + 5·31 = 156.
- Test unsatisfiable case: K_6 (complete graph on 6 vertices) with K_vc = 3 (too small, minimum VC is 5). Verify no allocation achieves cost ≤ K.
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 7 edges:
- Edges: {0,1}, {0,2}, {1,2}, {2,3}, {3,4}, {4,5}, {3,5}
- Minimum vertex cover size: K_vc = 3, e.g., V' = {0, 2, 3} covers:
  - {0,1} by 0 ✓, {0,2} by 0 or 2 ✓, {1,2} by 2 ✓, {2,3} by 2 or 3 ✓, {3,4} by 3 ✓, {4,5} needs... vertex 4 or 5 must be in cover.
- Corrected: V' = {2, 3, 5} covers: {0,1}... no, 0 and 1 not covered.
- Corrected: V' = {0, 2, 3, 5} (size 4), or V' = {1, 2, 3, 4} (size 4).
- Actually minimum vertex cover of this graph: check all edges.
  - Take V' = {0, 2, 3, 5}: {0,1} by 0 ✓, {0,2} by 0 ✓, {1,2} by 2 ✓, {2,3} by 2 ✓, {3,4} by 3 ✓, {4,5} by 5 ✓, {3,5} by 3 ✓. Size = 4.
  - Take V' = {1, 2, 4, 3}: {0,1} by 1 ✓, {0,2} by 2 ✓, {1,2} by 1 ✓, {2,3} by 2 ✓, {3,4} by 3 ✓, {4,5} by 4 ✓, {3,5} by 3 ✓. Size = 4.
  - Can we do size 3? Try {2, 3, 4}: {0,1} — neither 0 nor 1 in cover. Fail.
  - Minimum is 4. Set K_vc = 4.

**Simpler source instance:**
Graph G with 6 vertices {0, 1, 2, 3, 4, 5} and 6 edges:
- Edges: {0,1}, {1,2}, {2,3}, {3,4}, {4,5}, {5,0} (a 6-cycle C_6)
- Minimum vertex cover: K_vc = 3, e.g., V' = {1, 3, 5}
  - {0,1} by 1 ✓, {1,2} by 1 ✓, {2,3} by 3 ✓, {3,4} by 3 ✓, {4,5} by 5 ✓, {5,0} by 5 ✓

**Constructed target instance (MultipleCopyFileAllocation):**
- Graph G' = G (6 vertices, 6 edges, same C_6)
- s(v) = 1 for all v ∈ V
- u(v) = M = 6·6 + 1 = 37 for all v ∈ V
- K = K_vc + (n − K_vc)·M = 3 + 3·37 = 3 + 111 = 114

**Solution mapping (V' = {1, 3, 5}):**
- Storage cost: ∑_{v ∈ V'} s(v) = 3·1 = 3
- Distances from non-cover vertices to nearest cover vertex:
  - d(0): neighbors are 1 (in V') and 5 (in V'). d(0) = 1.
  - d(2): neighbors are 1 (in V') and 3 (in V'). d(2) = 1.
  - d(4): neighbors are 3 (in V') and 5 (in V'). d(4) = 1.
- Usage cost: ∑_{v ∈ V} d(v)·u(v) = (0 + 1 + 0 + 1 + 0 + 1)·37... wait, vertices in V' have d(v) = 0:
  - d(0) = 1, d(1) = 0, d(2) = 1, d(3) = 0, d(4) = 1, d(5) = 0
  - Usage cost = (1 + 0 + 1 + 0 + 1 + 0)·37 = 3·37
...(truncated)
````


#pagebreak()


== Vertex Cover $arrow.r$ Longest Common Subsequence #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#429)]


=== Reference

````
> [SR10] LONGEST COMMON SUBSEQUENCE
> INSTANCE: Finite alphabet Σ, finite set R of strings from Σ*, and a positive integer K.
> QUESTION: Is there a string w ∈ Σ* with |w| ≥ K such that w is a subsequence of each x ∈ R?
> Reference: [Maier, 1978]. Transformation from VERTEX COVER.
> Comment: Remains NP-complete even if |Σ| = 2. Solvable in polynomial time for any fixed K or for fixed |R| (by dynamic programming).
````


#theorem[
  Vertex Cover polynomial-time reduces to Longest Common Subsequence.
]


=== Construction

````
Given a MinimumVertexCover instance G = (V, E) with V = {0, 1, ..., n−1} and E = {e₁, ..., eₘ}, construct a LongestCommonSubsequence instance as follows:

1. **Alphabet:** Σ = {0, 1, ..., n−1}, one symbol per vertex. So `alphabet_size = n`.

2. **Template string:** S₀ = (0, 1, 2, ..., n−1), listing all vertices in sorted order. Length = n.

3. **Edge strings:** For each edge eⱼ = {u, v}, construct:
   Sⱼ = (0, ..., n−1 with u removed) ++ (0, ..., n−1 with v removed)
   Each half is in sorted order. Length = 2(n−1).

4. **String set:** R = {S₀, S₁, ..., Sₘ}, giving m + 1 strings total.

5. **LCS bound:** K' = n − K, where K is the vertex cover size. The LCS length equals the maximum independent set size.

**Correctness (forward):** Let I ⊆ V be an independent set of size n − K. The sorted sequence of symbols in I is a common subsequence of all strings:
- It is trivially a subsequence of S₀ since S₀ lists all vertices in order.
- For each edge string Sⱼ corresponding to edge {u, v}: since I is independent, at most one of u, v is in I. The symbol not in the edge endpoint set appears in both halves of Sⱼ. The symbol of the one endpoint that might be in I appears in the half where the *other* endpoint was removed. Therefore the sorted symbols of I appear as a subsequence.

**Correctness (backward):** Let w be a common subsequence of length ≥ n − K. Since w is a subsequence of S₀ = (0, 1, ..., n−1) and S₀ has no repeated symbols, w consists of distinct vertex symbols. For any edge {u, v}, the edge string Sⱼ = (V\{u})(V\{v}) contains u only in the second half and v only in the first half. If both u and v appeared in w, then since w must be a subsequence of Sⱼ, v must be matched before u — but w is also a subsequence of S₀ where u < v or v < u in some fixed order. This forces a contradiction for at least one ordering. Therefore at most one endpoint of each edge appears in w, so the symbols of w form an independent set. The complement V \ w is a vertex cover of size ≤ K.

**Solution extraction:** Given the LCS witness (a subsequence of symbols), the symbols present form an independent set. The vertex cover is the complement: config[v] = 1 if v does NOT appear in the LCS, config[v] = 0 if v appears in the LCS.

**Time complexity of reduction:** O(n · m) to construct all strings.
````


=== Overhead

````
**Symbols:**
- n = `num_vertices` of source MinimumVertexCover instance
- m = `num_edges` of source MinimumVertexCover instance

| Target field | Expression | Derivation |
|---|---|---|
| `alphabet_size` | `num_vertices` | One symbol per vertex |
| `num_strings` | `num_edges + 1` | One template + one per edge |
| `max_length` | `num_vertices` | min string length = n (template S₀ has length n ≤ 2(n−1) for n ≥ 2) |
| `total_length` | `num_vertices + num_edges * 2 * (num_vertices - 1)` | S₀ has length n; each edge string has length 2(n−1) |
````


=== Correctness

````
- Closed-loop test: reduce a MinimumVertexCover instance to LongestCommonSubsequence, solve the target with BruteForce, extract solution, verify it is a valid vertex cover on the source
- Test with path P₄ as above (MVC = 2, LCS = 2)
- Test with triangle K₃ (MVC = 2, LCS = 1, independent set = any single vertex)
- Test with empty graph (no edges): MVC = 0, LCS = n (all vertices form the independent set)
- Verify that every constructed string only uses symbols in {0, ..., n−1}
````


=== Example

````
**Source instance (MinimumVertexCover on path P₄):**
- Vertices: V = {0, 1, 2, 3}, n = 4
- Edges: {0,1}, {1,2}, {2,3}, m = 3
- Minimum vertex cover: {1, 2} of size K = 2 (covers all edges)
- Maximum independent set: {0, 3} of size n − K = 2

**Constructed target instance (LongestCommonSubsequence):**
- Alphabet: Σ = {0, 1, 2, 3}, alphabet_size = 4
- Template string: S₀ = (0, 1, 2, 3), length 4
- Edge strings:
  - S₁ for edge {0, 1}: (1, 2, 3) ++ (0, 2, 3) = (1, 2, 3, 0, 2, 3), length 6
  - S₂ for edge {1, 2}: (0, 2, 3) ++ (0, 1, 3) = (0, 2, 3, 0, 1, 3), length 6
  - S₃ for edge {2, 3}: (0, 1, 3) ++ (0, 1, 2) = (0, 1, 3, 0, 1, 2), length 6
- String set: R = {S₀, S₁, S₂, S₃}, num_strings = 4
- max_length = min(4, 6, 6, 6) = 4
- LCS bound: K' = 4 − 2 = 2

**Verification that (0, 3) is a common subsequence of length 2:**
- S₀ = (0, 1, 2, 3): subsequence at positions 0, 3 ✓
- S₁ = (1, 2, 3, 0, 2, 3): match 0 at position 3, then 3 at position 5 ✓
- S₂ = (0, 2, 3, 0, 1, 3): match 0 at position 0, then 3 at position 5 ✓
- S₃ = (0, 1, 3, 0, 1, 2): match 0 at position 0, then 3 at position 2 ✓

**Solution extraction:**
- LCS witness = (0, 3) → independent set = {0, 3}
- Vertex cover = complement = {1, 2}
- Config: config = [0, 1, 1, 0] (v in cover ↔ config[v] = 1)
- Check: edge {0,1} covered by v1 ✓, edge {1,2} covered by v1 and v2 ✓, edge {2,3} covered by v2 ✓
````


#pagebreak()


== Vertex Cover $arrow.r$ Minimum Cardinality Key #text(size: 8pt, fill: purple)[ \[Needs fix\] ] #text(size: 8pt, fill: gray)[(\#459)]


=== Reference

````
> [SR26] MINIMUM CARDINALITY KEY
> INSTANCE: A set A of "attribute names," a collection F of ordered pairs of subsets of A (called "functional dependencies" on A), and a positive integer M.
> QUESTION: Is there a key of cardinality M or less for the relational system , i.e., a minimal subset K ⊆ A with |K|  Reference: [Lucchesi and Osborne, 1977], [Lipsky, 1977a]. Transformation from VERTEX COVER. See [Date, 1975] for general background on relational data bases.
````


#theorem[
  Vertex Cover polynomial-time reduces to Minimum Cardinality Key.
]


=== Construction

````


**Summary:**
Given a Vertex Cover instance (G = (V, E), k) where V = {v_1, ..., v_n} and E = {e_1, ..., e_m}, construct a Minimum Cardinality Key instance  as follows:

1. **Attribute set construction:** Create one attribute for each vertex: A_V = {a_{v_1}, ..., a_{v_n}}. Additionally, create one attribute for each edge: A_E = {a_{e_1}, ..., a_{e_m}}. The full attribute set is A = A_V ∪ A_E, so |A| = n + m.

2. **Functional dependencies:** For each edge e_j = {v_p, v_q} in E, add two functional dependencies:
   - ({a_{v_p}}, {a_{e_j}}): attribute a_{v_p} determines a_{e_j}
   - ({a_{v_q}}, {a_{e_j}}): attribute a_{v_q} determines a_{e_j}

   These express that knowing either endpoint of an edge determines the edge attribute. Also, include the trivial identity dependencies so that each vertex attribute determines itself.

3. **Budget parameter:** Set M = k (same as the vertex cover budget).

4. **Key construction insight:** A subset K ⊆ A is a key for  if and only if the closure of K under F* equals all of A. Since the edge attributes are determined by the vertex attributes (via the functional dependencies), K needs to:
   - Include enough vertex attributes to determine all edge attributes (i.e., for every edge e_j = {v_p, v_q}, at least one of a_{v_p} or a_{v_q} must be in K or derivable from K)
   - Include all vertex attributes not derivable from other attributes in K

5. **Correctness (forward):** If S ⊆ V is a vertex cover of size ≤ k, then K = {a_v : v ∈ S} determines all edge attributes (since every edge has at least one endpoint in S). The remaining vertex attributes not in K can be added to the key if needed, but the functional dependencies are set up so that K already determines all of A. Hence K is a key of size ≤ k = M.

6. **Correctness (reverse):** If K is a key of cardinality ≤ M = k, then the vertex attributes in K form a vertex cover of G: for every edge e_j = {v_p, v_q}, the attribute a_{e_j} must be in the closure of K, which requires that at least one of a_{v_p} or a_{v_q} is in K (since the only way to derive a_{e_j} is from a_{v_p} or a_{v_q}).

**Time complexity of reduction:** O(n + m) to construct the attribute set and functional dependencies.
````


=== Overhead

````


**Symbols:**
- n = `num_vertices` of source graph G
- m = `num_edges` of source graph G

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_attributes` | `num_vertices` + `num_edges` |
| `num_dependencies` | 2 * `num_edges` |
| `budget` | k (same as vertex cover budget) |

**Derivation:**
- Attributes: one per vertex (n) plus one per edge (m) = n + m total
- Functional dependencies: two per edge (one for each endpoint) = 2m total
- Each dependency has a single-attribute left-hand side and a single-attribute right-hand side
- Budget M = k is passed through unchanged
````


=== Correctness

````


- Closed-loop test: reduce a MinimumVertexCover instance to MinimumCardinalityKey, solve the key problem by brute-force enumeration of attribute subsets, extract solution, verify as vertex cover on original graph
- Test with a triangle graph K_3: minimum vertex cover is 2, so minimum key should have cardinality 2
- Test with a star graph K_{1,5}: minimum vertex cover is 1 (center vertex), so minimum key should be 1
- Verify that the closure computation correctly derives all edge attributes from the key attributes
````


=== Example

````


**Source instance (MinimumVertexCover):**
Graph G with 6 vertices V = {v_1, v_2, v_3, v_4, v_5, v_6} and 7 edges:
- e_1 = {v_1, v_2}
- e_2 = {v_1, v_3}
- e_3 = {v_2, v_4}
- e_4 = {v_3, v_4}
- e_5 = {v_3, v_5}
- e_6 = {v_4, v_6}
- e_7 = {v_5, v_6}

Minimum vertex cover: k = 3, e.g., S = {v_1, v_4, v_5} covers all edges:
- e_1 = {v_1, v_2}: v_1 in S
- e_2 = {v_1, v_3}: v_1 in S
- e_3 = {v_2, v_4}: v_4 in S
- e_4 = {v_3, v_4}: v_4 in S
- e_5 = {v_3, v_5}: v_5 in S
- e_6 = {v_4, v_6}: v_4 in S
- e_7 = {v_5, v_6}: v_5 in S

**Constructed target instance (MinimumCardinalityKey):**
Attribute set A = {a_{v1}, a_{v2}, a_{v3}, a_{v4}, a_{v5}, a_{v6}, a_{e1}, a_{e2}, a_{e3}, a_{e4}, a_{e5}, a_{e6}, a_{e7}}
(13 attributes total: 6 vertex + 7 edge)

Functional dependencies F (14 total, 2 per edge):
- From e_1: {a_{v1}} -> {a_{e1}}, {a_{v2}} -> {a_{e1}}
- From e_2: {a_{v1}} -> {a_{e2}}, {a_{v3}} -> {a_{e2}}
- From e_3: {a_{v2}} -> {a_{e3}}, {a_{v4}} -> {a_{e3}}
- From e_4: {a_{v3}} -> {a_{e4}}, {a_{v4}} -> {a_{e4}}
- From e_5: {a_{v3}} -> {a_{e5}}, {a_{v5}} -> {a_{e5}}
- From e_6: {a_{v4}} -> {a_{e6}}, {a_{v6}} -> {a_{e6}}
- From e_7: {a_{v5}} -> {a_{e7}}, {a_{v6}} -> {a_{e7}}

Budget M = 3

**Solution mapping:**
Key K = {a_{v1}, a_{v4}, a_{v5}} (cardinality 3 = M)

Closure computation for K:
- a_{v1} in K: determines a_{e1} (via {a_{v1}} -> {a_{e1}}) and a_{e2} (via {a_{v1}} -> {a_{e2}})
- a_{v4} in K: determines a_{e3} (via {a_{v4}} -> {a_{e3}}), a_{e4} (via {a_{v4}} -> {a_{e4}}), a_{e6} (via {a_{v4}} -> {a_{e6}})
- a_{v5} in K: determines a_{e5} (via {a_{v5}} -> {a_{e5}}), a_{e7} (via {a_{v5}} -> {a_{e7}})
- All 7 edge attributes determined. Vertex attributes a_{v2}, a_{v3}, a_{v6} are NOT determined by K alone.

Note: For K to be a proper key for , K must determine ALL attributes in A. The vertex attributes not in K (a_{v2}, a_{v3}, a_{v6}) are not derivable from K via F alone. To make the reduction work correctly, additional functional dependencies or a modified attribute 
...(truncated)
````


#pagebreak()


== Vertex Cover $arrow.r$ Scheduling with Individual Deadlines #text(size: 8pt, fill: blue)[ \[Not yet verified\] ] #text(size: 8pt, fill: gray)[(\#478)]


=== Reference

````
> [SS11] SCHEDULING WITH INDIVIDUAL DEADLINES
> INSTANCE: Set T of tasks, each having length l(t) = 1, number m E Z+ of processors, partial order  QUESTION: Is there an m-processor schedule σ for T that obeys the precedence constraints and meets all the deadlines, i.e., σ(t) + l(t)  Reference: [Brucker, Garey, and Johnson, 1977]. Transformation from VERTEX COVER.
> Comment: Remains NP-complete even if < is an "out-tree" partial order (no task has more than one immediate predecessor), but can be solved in polynomial time if < is an "in-tree" partial order (no task has more than one immediate successor). Solvable in polynomial time if m = 2 and < is arbitrary [Garey and Johnson, 1976c], even if individual release times are included [Garey and Johnson, 1977b]. For < empty, can be solved in polynomial time by matching for m arbitrary, even with release times and with a single resource having 0-1 valued requirements [Blazewicz, 1977b], [Blazewicz, 1978].
````


#theorem[
  Vertex Cover polynomial-time reduces to Scheduling with Individual Deadlines.
]


=== Construction

````


**Summary:**

Let G = (V, E) be a graph with |V| = n, |E| = q, and K be the vertex-cover bound.

1. **Tasks:** Create one task v_i for each vertex i in V (n vertex tasks), and one task e_j for each edge j in E (q edge tasks). Total tasks: n + q.
2. **Precedence constraints:** For each edge e_j = {u, v}, add precedence constraints v_u < e_j and v_v < e_j (the edge task must be scheduled after both of its endpoint vertex tasks).
3. **Processors:** Set m = n (one processor per vertex, so all vertex tasks can run simultaneously in the first time slot).
4. **Deadlines:** For each vertex task v_i, set d(v_i) = 1 (must complete by time 1). For each edge task e_j, set d(e_j) = 2 (must complete by time 2).
5. **Revised construction (tighter):** Actually, the Brucker-Garey-Johnson construction is more subtle. Set m = K + q. Create n vertex tasks with deadline d(v_i) = 1 and q edge tasks with deadline d(e_j) = 2. The precedence order makes each edge task depend on its two endpoint vertex tasks. With m = K + q processors, at time 0 we can schedule at most K vertex tasks plus up to q edge tasks (but edge tasks have predecessors so they cannot start at time 0). At time 0, we schedule K vertex tasks. At time 1, we schedule the remaining n - K vertex tasks and q edge tasks. The key constraint is that at time 1, we need n - K + q processors (one for each remaining vertex task and each edge task). But we only have m = K + q processors. So we need n - K + q <= K + q, i.e., n <= 2K. Additionally, each edge task requires both its endpoint vertex tasks to be completed by time 1, so at least one endpoint of each edge must be among the K tasks scheduled at time 0, forming a vertex cover.

**Simplified construction (as typically presented):**

Let G = (V, E), |V| = n, |E| = q, bound K.

1. Create n + q unit-length tasks: {v_1, ..., v_n} (vertex tasks) and {e_1, ..., e_q} (edge tasks).
2. For each edge e_j = (u, w): add v_u < e_j and v_w < e_j.
3. Set m = K + q processors.
4. Set d(v_i) = 2 for all vertex tasks, d(e_j) = 2 for all edge tasks.
5. The total work is n + q units in 2 time slots, requiring at most m tasks per slot. At time 0, only vertex tasks can run (edge tasks have unfinished predecessors). At time 1, remaining vertex tasks and edge tasks run. A feasible schedule exists iff we can schedule enough vertex tasks at time 0 so that all edge tasks have both predecessors done, meaning at least one endpoint of each edge was scheduled at time 0 -- i.e., a vertex cover of size at most K.

**Solution extraction:** The vertex cover is V' = {v_i : sigma(v_i) = 0} (vertex tasks scheduled at time 0).
````


=== Overhead

````


**Symbols:**
- n = |V| = number of vertices in the graph
- q = |E| = number of edges
- K = vertex cover bound

| Target metric (code name)   | Polynomial (using symbols above) |
|------------------------------|----------------------------------|
| `num_tasks`                  | `num_vertices + num_edges`       |
| `num_processors`             | `vertex_cover_bound + num_edges` |
| `num_precedence_constraints` | `2 * num_edges`                  |
| `max_deadline`               | 2                                |

**Derivation:** Each vertex and each edge in the source graph becomes a task. Each edge contributes two precedence constraints (one per endpoint). The number of processors and the deadline are derived from K and the graph structure. Construction is O(n + q).
````


=== Correctness

````


- Closed-loop test: construct a VERTEX COVER instance (graph G, bound K), reduce to SCHEDULING WITH INDIVIDUAL DEADLINES, solve by brute-force enumeration of task-to-timeslot assignments respecting precedence and deadlines, verify the schedule corresponds to a vertex cover of size at most K.
- Check that the constructed scheduling instance has n + q tasks, K + q processors, and all deadlines are at most 2.
- Edge cases: test with K = 0 (infeasible unless q = 0), complete graph K_4 (minimum VC = 2 if K_3, etc.), star graph (VC = 1 at center).
````


=== Example

````


**Source instance (VERTEX COVER):**
G = (V, E) with V = {1, 2, 3, 4, 5}, E = {(1,2), (2,3), (3,4), (4,5), (1,5)} (a 5-cycle), K = 3.

Minimum vertex cover of a 5-cycle has size 3: e.g., V' = {1, 3, 4}.

**Constructed SCHEDULING WITH INDIVIDUAL DEADLINES instance:**

Tasks (10 total):
- Vertex tasks: v_1, v_2, v_3, v_4, v_5 (all with deadline 2)
- Edge tasks: e_1, e_2, e_3, e_4, e_5 (all with deadline 2)

Precedence constraints (10 total):
- e_1: v_1 = n - K. If n - K = n/2) this is trivial. The actual Brucker-Garey-Johnson construction is more intricate.

**Working example with simpler graph:**
G = path P_3: V = {1, 2, 3}, E = {(1,2), (2,3)}, K = 1 (vertex 2 covers both edges).

Tasks: v_1, v_2, v_3, e_1, e_2 (5 tasks).
Precedence: v_1 = 0, which is wrong. The construction needs refinement. The real Brucker et al. construction uses a more nuanced encoding. For the purposes of this issue, we note the reduction follows [Brucker, Garey, and Johnson, 1977] and the implementation should follow the original paper.
````


#pagebreak()


= X3C


== X3C $arrow.r$ ACYCLIC PARTITION #text(size: 8pt, fill: red)[ \[Refuted\] ] #text(size: 8pt, fill: gray)[(\#822)]


=== Reference

````
> [ND15] ACYCLIC PARTITION
> INSTANCE: Directed graph G=(V,A), weight w(v)∈Z^+ for each v∈V, cost c(a)∈Z^+ for each a∈A, positive integers B and K.
> QUESTION: Is there a partition of V into disjoint sets V_1,V_2,...,V_m such that the directed graph G'=(V',A'), where V'={V_1,V_2,...,V_m}, and (V_i,V_j)∈A' if and only if (v_i,v_j)∈A for some v_i∈V_i and some v_j∈V_j, is acyclic, such that the sum of the weights of the vertices in each V_i does not exceed B, and such that the sum of the costs of all those arcs having their endpoints in different sets does not exceed K?
> Reference: [Garey and Johnson, ——]. Transformation from X3C.
> Comment: Remains NP-complete even if all v∈V have w(v)=1 and all a∈A have c(a)=1. Can be solved in polynomial time if G contains a Hamiltonian path (a property that can be verified in polynomial time for acyclic digraphs) [Kernighan, 1971]. If G is a tree the general problem is NP-complete in the ordinary sense, but can be solved in pseudo-polynomial time [Lu
...(truncated)
````


#theorem[
  X3C polynomial-time reduces to ACYCLIC PARTITION.
]


=== Construction

````


**Summary:**
Given an X3C instance (X, C) where X = {x_1, ..., x_{3q}} is a universe with |X| = 3q and C = {C_1, ..., C_m} is a collection of 3-element subsets of X, construct an ACYCLIC PARTITION instance as follows. Since G&J note the problem remains NP-complete even with unit weights and unit costs, we use the unit-weight/unit-cost variant.

1. **Create element vertices:** For each element x_j in X, create a vertex v_j with weight w(v_j) = 1.

2. **Create set-indicator vertices:** For each set C_i in C, create a vertex u_i with weight w(u_i) = 0 (or use a construction where the weight budget controls grouping). In the unit-weight variant, all vertices have weight 1.

3. **Add arcs encoding set membership:** For each set C_i = {x_a, x_b, x_c}, add directed arcs from u_i to v_a, from u_i to v_b, and from u_i to v_c. These arcs encode which elements belong to which set. All arcs have cost c = 1.

4. **Add ordering arcs between elements:** Add arcs between element vertices to create a chain: (v_1, v_2), (v_2, v_3), ..., (v_{3q-1}, v_{3q}). These arcs enforce a linear ordering that interacts with the acyclicity constraint.

5. **Set partition parameters:**
   - Weight bound B = 3 (each partition block can hold at most 3 unit-weight element vertices, matching the 3-element sets in C)
   - Arc cost bound K is set so that the only way to achieve cost <= K is to group elements into blocks corresponding to sets in C, with no inter-block arcs from the membership encoding

6. **Acyclicity constraint:** The directed arcs are arranged so that grouping elements into blocks that correspond to an exact cover yields an acyclic quotient graph, while any grouping that does not correspond to a valid cover creates a cycle in the quotient graph (due to overlapping set memberships creating bidirectional dependencies).

7. **Solution extraction:** Given a valid acyclic partition with weight bound B and cost bound K, read off the partition blocks. Each block of 3 element vertices corresponds to a set C_i in the exact cover. The collection of these sets forms the exact cover of X.

**Key invariant:** The weight bound B = 3 forces each partition block to contain at most 3 elements, and the total number of elements 3q means exactly q blocks of size 3 are needed. The acyclicity and cost constraints together ensure these blocks correspond to sets in C that partition X.

**Note:** The exact construction details are from Garey & Johnson's unpublished manuscript referenced as "[Garey and Johnson, ——]". The description above captures the essential structure of such a reduction; the precise gadget construction may vary.
````


=== Overhead

````


**Symbols:**
- n = |X| = 3q (universe size)
- m = |C| (number of 3-element subsets)

| Target metric (code name) | Polynomial (using symbols above) |
|----------------------------|----------------------------------|
| `num_vertices` | `num_elements + num_sets` |
| `num_arcs` | `3 * num_sets + num_elements - 1` |

**Derivation:** One vertex per element (n = 3q) plus one vertex per set (m), giving n + m vertices total. Each set contributes 3 membership arcs, and the element chain contributes n - 1 ordering arcs, giving 3m + n - 1 arcs total.
````


=== Correctness

````

- Closed-loop test: construct an X3C instance, reduce to ACYCLIC PARTITION, solve with BruteForce, extract the partition blocks, and verify they correspond to an exact cover of X
- Check that each partition block contains exactly 3 elements when B = 3
- Verify the quotient graph is acyclic
- Verify the total inter-block arc cost does not exceed K
- Check that a solvable X3C instance yields a valid acyclic partition, and an unsolvable one does not
````


=== Example

````


**Source instance (X3C):**
Universe X = {1, 2, 3, 4, 5, 6} (q = 2)
Collection C:
- C_1 = {1, 2, 3}
- C_2 = {1, 3, 5}
- C_3 = {4, 5, 6}
- C_4 = {2, 4, 6}
- C_5 = {1, 4, 5}

Exact cover exists: C' = {C_1, C_3} = {{1,2,3}, {4,5,6}} covers all 6 elements exactly once.

**Constructed target instance (ACYCLIC PARTITION):**
Vertices:
- Element vertices: v_1, v_2, v_3, v_4, v_5, v_6 (weight 1 each)
- Set vertices: u_1, u_2, u_3, u_4, u_5 (weight 1 each)
- Total: 11 vertices

Arcs (cost 1 each):
- Membership arcs: (u_1,v_1), (u_1,v_2), (u_1,v_3), (u_2,v_1), (u_2,v_3), (u_2,v_5), (u_3,v_4), (u_3,v_5), (u_3,v_6), (u_4,v_2), (u_4,v_4), (u_4,v_6), (u_5,v_1), (u_5,v_4), (u_5,v_5)
- Element chain arcs: (v_1,v_2), (v_2,v_3), (v_3,v_4), (v_4,v_5), (v_5,v_6)
- Total: 15 + 5 = 20 arcs

Parameters: B = 3, K chosen to force exact cover structure.

**Solution mapping:**
- Exact cover {C_1, C_3} -> partition blocks grouping {v_1, v_2, v_3} and {v_4, v_5, v_6} with set vertices assigned to singleton blocks or merged with their corresponding element blocks
- Each block has weight <= 3 (satisfies B = 3)
- The quotient graph on the partition blocks is acyclic (elements are grouped in chain order)
- The exact cover property ensures no element is in two blocks, maintaining consistency
````


#pagebreak()
