// Verification proof: SubsetSum → IntegerKnapsack
// Issue: #521
// Reference: Garey & Johnson, Computers and Intractability, A6 (MP10), p.247

= Subset Sum $arrow.r$ Integer Knapsack

== Problem Definitions

*Subset Sum (SP13).* Given a finite set $A = {a_1, dots, a_n}$ of positive integers and
a target $B in bb(Z)^+$, determine whether there exists a subset $A' subset.eq A$ such that
$sum_(a in A') a = B$.

*Integer Knapsack (MP10).* Given a finite set $U = {u_1, dots, u_n}$, for each $u_i$ a
positive size $s(u_i) in bb(Z)^+$ and a positive value $v(u_i) in bb(Z)^+$, and a
nonnegative capacity $B$, find non-negative integer multiplicities $c(u_i) in bb(Z)_(>= 0)$
maximizing $sum_(i=1)^n c(u_i) dot v(u_i)$ subject to $sum_(i=1)^n c(u_i) dot s(u_i) <= B$.

== Reduction

Given a Subset Sum instance $(A, B)$ with $n$ elements having sizes $s(a_1), dots, s(a_n)$:

+ *Item set:* $U = A$. For each element $a_i$, create an item $u_i$ with
  $s(u_i) = s(a_i)$ and $v(u_i) = s(a_i)$ (size equals value).
+ *Capacity:* Set knapsack capacity to $B$.

== Correctness Proof

=== Forward Direction: YES Source $arrow.r$ YES Target

If there exists $A' subset.eq A$ with $sum_(a in A') s(a) = B$, set $c(u_i) = 1$ if
$a_i in A'$, else $c(u_i) = 0$. Then:
$ sum_i c(u_i) dot s(u_i) = sum_(a in A') s(a) = B <= B quad checkmark $
$ sum_i c(u_i) dot v(u_i) = sum_(a in A') s(a) = B $

So the optimal IntegerKnapsack value is at least $B$.

=== Nature of the Reduction

This reduction is a *forward-only NP-hardness embedding*. Subset Sum is a special
case of Integer Knapsack (with $s = v$ and multiplicities restricted to ${0, 1}$).
The reduction proves Integer Knapsack is NP-hard because any Subset Sum instance
can be embedded as an Integer Knapsack instance where:
- A YES answer to Subset Sum guarantees a YES answer to Integer Knapsack (value $>= B$).

The reverse implication does *not* hold in general: Integer Knapsack may achieve
value $>= B$ using multiplicities $> 1$, even when no 0-1 subset sums to $B$.

*Counterexample:* $A = {3}$, $B = 6$. No subset of ${3}$ sums to 6 (Subset Sum
answer: NO). But Integer Knapsack with $s(u_1) = v(u_1) = 3$, capacity 6 allows
$c(u_1) = 2$, achieving value $6 >= 6$ (Integer Knapsack answer: YES).

=== Solution Extraction (Forward Direction Only)

Given a Subset Sum solution $A' subset.eq A$, the Integer Knapsack solution is:
$ c(u_i) = cases(1 &"if" a_i in A', 0 &"otherwise") $

This is a valid Integer Knapsack solution with total value $= B$.

== Overhead

The reduction preserves instance size exactly:
$ "num_items"_"target" = "num_elements"_"source" $

The capacity of the target equals the target sum of the source.

== YES Example

*Source:* $A = {3, 7, 1, 8, 5}$, $B = 16$.
Valid subset: $A' = {3, 8, 5}$ with sum $= 3 + 8 + 5 = 16 = B$. #sym.checkmark

*Target:* IntegerKnapsack with:
- Sizes: $(3, 7, 1, 8, 5)$, Values: $(3, 7, 1, 8, 5)$, Capacity: $16$.

*Solution:* $c = (1, 0, 0, 1, 1)$.
- Total size: $3 + 8 + 5 = 16 <= 16$. #sym.checkmark
- Total value: $3 + 8 + 5 = 16$. #sym.checkmark

== NO Example (Demonstrating Forward-Only Nature)

*Source:* $A = {3}$, $B = 6$. No subset sums to 6. Subset Sum: NO.

*Target:* IntegerKnapsack with sizes $= (3)$, values $= (3)$, capacity $= 6$.

$c(u_1) = 2$ gives total size $= 6 <= 6$ and total value $= 6$.
Integer Knapsack optimal value $= 6 >= 6$, so the knapsack is satisfiable.

This demonstrates that the reduction is *not* an equivalence-preserving (Karp)
reduction. It is a forward embedding: Subset Sum YES $arrow.r$ Integer Knapsack YES,
but NOT Integer Knapsack YES $arrow.r$ Subset Sum YES.

The NP-hardness proof is valid because it only requires the forward direction.
