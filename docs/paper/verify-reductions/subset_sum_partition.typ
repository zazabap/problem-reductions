// Verification proof: SubsetSum → Partition
// Issue: #973
// Reference: Garey & Johnson, Computers and Intractability, SP12–SP13

= Subset Sum $arrow.r$ Partition

== Problem Definitions

*Subset Sum (SP13).* Given a finite set $S = {s_1, dots, s_n}$ of positive integers and
a target $T in bb(Z)^+$, determine whether there exists a subset $A' subset.eq S$ such that
$sum_(a in A') a = T$.

*Partition (SP12).* Given a finite set $A = {a_1, dots, a_m}$ of positive integers,
determine whether there exists a subset $A' subset.eq A$ such that
$sum_(a in A') a = sum_(a in A without A') a$.

== Reduction

Given a Subset Sum instance $(S, T)$ with $Sigma = sum_(i=1)^n s_i$:

+ Compute padding $d = |Sigma - 2T|$.
+ If $d = 0$: output $"Partition"(S)$.
+ If $d > 0$: output $"Partition"(S union {d})$.

== Correctness Proof

Let $Sigma' = sum "of Partition instance"$ and $H = Sigma' slash 2$ (the half-sum target).

=== Case 1: $Sigma = 2T$ ($d = 0$)

The Partition instance is $S$ with $Sigma' = 2T$ and $H = T$.

*Forward.* If $A' subset.eq S$ satisfies $sum_(a in A') a = T$, then
$sum_(a in A') a = T = H$ and $sum_(a in S without A') a = Sigma - T = T = H$.
So $A'$ is a valid partition.

*Backward.* If partition $A'$ satisfies $sum_(a in A') a = H = T$,
then $A'$ is a valid Subset Sum solution.

=== Case 2: $Sigma > 2T$ ($d = Sigma - 2T > 0$)

$Sigma' = Sigma + d = 2(Sigma - T)$, so $H = Sigma - T$.

*Forward.* Given $A' subset.eq S$ with $sum_(a in A') a = T$, place $A' union {d}$ on one side:
$ sum_(a in A' union {d}) a = T + (Sigma - 2T) = Sigma - T = H. $
The complement $S without A'$ sums to $Sigma - T = H$. #sym.checkmark

*Backward.* Given a balanced partition, $d$ is on one side. The $S$-elements
on that side sum to $H - d = (Sigma - T) - (Sigma - 2T) = T$. #sym.checkmark

=== Case 3: $Sigma < 2T$ ($d = 2T - Sigma > 0$)

$Sigma' = Sigma + d = 2T$, so $H = T$.

*Forward.* Given $A' subset.eq S$ with $sum_(a in A') a = T = H$, place $A'$ on one side.
The other side is $(S without A') union {d}$ with sum $(Sigma - T) + (2T - Sigma) = T = H$. #sym.checkmark

*Backward.* Given a balanced partition, $d$ is on one side. The $S$-elements
on the *opposite* side sum to $H = T$. #sym.checkmark

=== Infeasible Instances

If $T > Sigma$, no subset of $S$ can sum to $T$. Here $d = 2T - Sigma > Sigma$,
so $d > Sigma' slash 2 = T$, meaning a single element exceeds the half-sum. The
Partition instance is therefore infeasible. #sym.checkmark

== Solution Extraction

Given a Partition solution $c in {0,1}^m$:
- If $d = 0$: return $c[0..n]$ directly.
- If $Sigma > 2T$: the $S$-elements on the *same side* as $d$ (the padding element at index $n$)
  form the subset summing to $T$. Return indicator $c'_i = c_i$ if $c_n = 1$, else $c'_i = 1 - c_i$.
- If $Sigma < 2T$: the $S$-elements on the *opposite side* from $d$ form the subset summing to $T$.
  Return indicator $c'_i = 1 - c_i$ if $c_n = 1$, else $c'_i = c_i$.

== Overhead

$ "num_elements"_"target" = "num_elements"_"source" + 1 quad "(worst case)" $

== YES Example

*Source:* $S = {1, 5, 6, 8}$, $T = 11$, $Sigma = 20 < 22 = 2T$.

Padding: $d = 2T - Sigma = 2$.

*Target:* $"Partition"({1, 5, 6, 8, 2})$, $Sigma' = 22$, $H = 11$.

*Solution:* Partition side 0 $= {5, 6} = 11$, side 1 $= {1, 8, 2} = 11$. #sym.checkmark

Extract: padding at index 4 is on side 1. Since $Sigma < 2T$, take opposite side (side 0):
elements $\{5, 6\}$ sum to $11 = T$. #sym.checkmark

== NO Example

*Source:* $S = {3, 7, 11}$, $T = 5$, $Sigma = 21$.

No subset of ${3, 7, 11}$ sums to 5.

Padding: $d = |21 - 10| = 11$. *Target:* $"Partition"({3, 7, 11, 11})$, $Sigma' = 32$, $H = 16$.

No partition of ${3, 7, 11, 11}$ into two equal-sum subsets exists. #sym.checkmark
