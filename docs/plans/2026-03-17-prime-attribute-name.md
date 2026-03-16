# Plan: Add PrimeAttributeName Model (Issue #446)

## Summary

Add the `PrimeAttributeName` satisfaction problem — a classical NP-complete problem from relational database theory (Garey & Johnson A4 SR28). Given a set of attributes A, a collection of functional dependencies F, and a query attribute x, determine if x belongs to any candidate key of <A, F>.

## Batch 1: Implementation (Steps 1–5.5)

### Task 1.1: Create model file `src/models/set/prime_attribute_name.rs`

Category: `set/` (operates on attribute sets with functional dependencies).

**Struct:**
```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrimeAttributeName {
    num_attributes: usize,
    dependencies: Vec<(Vec<usize>, Vec<usize>)>,  // (lhs, rhs) pairs
    query_attribute: usize,
}
```

**Constructor:** `new(num_attributes, dependencies, query_attribute)` — validates:
- `query_attribute < num_attributes`
- All attribute indices in dependencies are `< num_attributes`
- LHS of each dependency is non-empty

**Getter methods:**
- `num_attributes() -> usize`
- `num_dependencies() -> usize` (= `dependencies.len()`)
- `query_attribute() -> usize`
- `dependencies() -> &[(Vec<usize>, Vec<usize>)]`

**Helper: `compute_closure(attrs: &[bool], dependencies) -> Vec<bool>`**
Computes the attribute closure under F using a fixpoint algorithm:
1. Start with `closure = attrs.clone()`
2. Repeat: for each FD (X → Y), if X ⊆ closure, add all of Y to closure
3. Stop when no change occurs

**Problem trait impl:**
- `NAME = "PrimeAttributeName"`
- `Metric = bool` (satisfaction problem)
- `dims() = vec![2; num_attributes]` — binary: whether each attribute is in the candidate key K
- `evaluate(config)`:
  1. Check config length and binary values
  2. Let K = {i : config[i] = 1}
  3. If query_attribute ∉ K → false
  4. Compute closure(K) under F — if closure ≠ A → false (K is not a superkey)
  5. Check minimality: for each attribute j in K, compute closure(K \ {j}) — if closure(K \ {j}) = A, then K is not minimal → false
  6. All checks pass → true (K is a candidate key containing x)
- `variant() = crate::variant_params![]` (no type parameters)

**SatisfactionProblem marker trait:** `impl SatisfactionProblem for PrimeAttributeName {}`

**declare_variants!:**
```rust
crate::declare_variants! {
    default sat PrimeAttributeName => "2^num_attributes * num_dependencies * num_attributes",
}
```

**ProblemSchemaEntry:**
```rust
inventory::submit! {
    ProblemSchemaEntry {
        name: "PrimeAttributeName",
        display_name: "Prime Attribute Name",
        aliases: &[],
        dimensions: &[],
        module_path: module_path!(),
        description: "Determine if an attribute belongs to any candidate key under functional dependencies",
        fields: &[
            FieldInfo { name: "num_attributes", type_name: "usize", description: "Number of attributes" },
            FieldInfo { name: "dependencies", type_name: "Vec<(Vec<usize>, Vec<usize>)>", description: "Functional dependencies (lhs, rhs) pairs" },
            FieldInfo { name: "query_attribute", type_name: "usize", description: "The query attribute index" },
        ],
    }
}
```

**Canonical model example spec:**
```rust
#[cfg(feature = "example-db")]
pub(crate) fn canonical_model_example_specs() -> Vec<crate::example_db::specs::ModelExampleSpec> {
    vec![crate::example_db::specs::ModelExampleSpec {
        id: "prime_attribute_name",
        build: || {
            // Issue Example 1: 6 attributes, 3 FDs, query=3 → YES
            let problem = PrimeAttributeName::new(
                6,
                vec![
                    (vec![0, 1], vec![2, 3, 4, 5]),
                    (vec![2, 3], vec![0, 1, 4, 5]),
                    (vec![0, 3], vec![1, 2, 4, 5]),
                ],
                3,
            );
            // {2, 3} is a candidate key containing attribute 3
            crate::example_db::specs::satisfaction_example(problem, vec![vec![0, 0, 1, 1, 0, 0]])
        },
    }]
}
```

**Test link:**
```rust
#[cfg(test)]
#[path = "../../unit_tests/models/set/prime_attribute_name.rs"]
mod tests;
```

### Task 1.2: Register model

1. **`src/models/set/mod.rs`:** Add `pub(crate) mod prime_attribute_name;` and `pub use prime_attribute_name::PrimeAttributeName;`. Add to `canonical_model_example_specs()`.
2. **`src/models/mod.rs`:** Add `PrimeAttributeName` to the set re-export line.

### Task 1.3: Register CLI alias

**`problemreductions-cli/src/problem_name.rs`:**
- Add `"primeattributename" => "PrimeAttributeName".to_string()` in `resolve_alias()`
- No short alias (no well-established abbreviation)

### Task 1.4: Add CLI creation support

**New CLI flags in `problemreductions-cli/src/cli.rs` (`CreateArgs`):**
```rust
/// Functional dependencies (semicolon-separated, each dep is lhs>rhs with comma-separated indices, e.g., "0,1>2,3;2,3>0,1")
#[arg(long)]
pub deps: Option<String>,
/// Query attribute index for PrimeAttributeName
#[arg(long)]
pub query: Option<usize>,
```

**Update `all_data_flags_empty()`** in `create.rs` to include `&& args.deps.is_none() && args.query.is_none()`.

**Add match arm in `create.rs`:**
```rust
"PrimeAttributeName" => {
    let universe = args.universe.ok_or_else(|| {
        anyhow::anyhow!(
            "PrimeAttributeName requires --universe, --deps, and --query\n\n\
             Usage: pred create PrimeAttributeName --universe 6 --deps \"0,1>2,3,4,5;2,3>0,1,4,5\" --query 3"
        )
    })?;
    let deps_str = args.deps.as_deref().ok_or_else(|| {
        anyhow::anyhow!(
            "PrimeAttributeName requires --deps\n\n\
             Usage: pred create PrimeAttributeName --universe 6 --deps \"0,1>2,3,4,5;2,3>0,1,4,5\" --query 3"
        )
    })?;
    let query = args.query.ok_or_else(|| {
        anyhow::anyhow!(
            "PrimeAttributeName requires --query\n\n\
             Usage: pred create PrimeAttributeName --universe 6 --deps \"0,1>2,3,4,5;2,3>0,1,4,5\" --query 3"
        )
    })?;
    // Parse deps: "0,1>2,3;2,3>0,1" => vec![(vec![0,1], vec![2,3]), (vec![2,3], vec![0,1])]
    let dependencies = parse_deps(deps_str)?;
    // Validate
    for (i, (lhs, rhs)) in dependencies.iter().enumerate() {
        for &attr in lhs.iter().chain(rhs.iter()) {
            if attr >= universe {
                bail!("Dependency {} references attribute {} outside universe of size {}", i, attr, universe);
            }
        }
    }
    if query >= universe {
        bail!("Query attribute {} is outside universe of size {}", query, universe);
    }
    (ser(PrimeAttributeName::new(universe, dependencies, query))?, resolved_variant.clone())
}
```

**Add helper `parse_deps()`** in `create.rs`:
```rust
fn parse_deps(s: &str) -> Result<Vec<(Vec<usize>, Vec<usize>)>> {
    s.split(';')
        .map(|dep| {
            let parts: Vec<&str> = dep.split('>').collect();
            if parts.len() != 2 {
                bail!("Invalid dependency format '{}': expected 'lhs>rhs'", dep);
            }
            let lhs = parse_index_list(parts[0])?;
            let rhs = parse_index_list(parts[1])?;
            Ok((lhs, rhs))
        })
        .collect()
}
fn parse_index_list(s: &str) -> Result<Vec<usize>> {
    s.split(',')
        .map(|x| x.trim().parse::<usize>().map_err(|e| anyhow::anyhow!("Invalid index '{}': {}", x, e)))
        .collect()
}
```

**Update help text** in `cli.rs` `after_help`:
```
  PrimeAttributeName              --universe, --deps, --query
```

**Update examples** in `after_help`:
```
  pred create PrimeAttributeName --universe 6 --deps "0,1>2,3,4,5;2,3>0,1,4,5" --query 3
```

### Task 1.5: Write unit tests

Create `src/unit_tests/models/set/prime_attribute_name.rs`:

**Required tests (≥3):**

1. `test_prime_attribute_name_creation` — construct, verify getters, dims, num_variables
2. `test_prime_attribute_name_evaluate_yes` — Issue Example 1: config [0,0,1,1,0,0] ({2,3} is candidate key containing 3) → true
3. `test_prime_attribute_name_evaluate_no` — Issue Example 2: only key is {0,1}, query=3, no key contains 3
4. `test_prime_attribute_name_evaluate_superkey_not_minimal` — config [0,1,1,1,0,0] for Example 1: {1,2,3} has closure=A but not minimal → false
5. `test_prime_attribute_name_evaluate_not_superkey` — config [1,0,0,1,0,0] for Example 1: {0,3} closure check
6. `test_prime_attribute_name_solver` — BruteForce on Example 1 finds satisfying solutions
7. `test_prime_attribute_name_no_solution` — BruteForce on Example 2 finds no satisfying solutions
8. `test_prime_attribute_name_serialization` — round-trip serde
9. `test_prime_attribute_name_paper_example` — verify the paper example (same as canonical example)
10. `test_prime_attribute_name_multiple_keys` — Issue Example 3 (8 attributes, more complex)

**Link test file** in model file with `#[path]` attribute.
**Register test module** in `src/unit_tests/models/set/mod.rs`.

### Task 1.6: Verify build and tests

```bash
make check  # fmt + clippy + test
```

Fix any issues found.

## Batch 2: Paper Entry (Step 6)

### Task 2.1: Write paper entry in `docs/paper/reductions.typ`

**6a. Register display name:**
```typst
"PrimeAttributeName": [Prime Attribute Name],
```

**6b. Write problem-def:**
```typst
#problem-def("PrimeAttributeName")[
  Given a set $A$ of attribute names, a collection $F$ of functional dependencies on $A$,
  and a specified attribute $x in A$, determine whether $x$ is a _prime attribute_ — i.e.,
  whether there exists a candidate key $K$ for $angle.l A, F angle.r$ such that $x in K$.
  A _candidate key_ is a minimal set $K subset.eq A$ whose closure under $F$ equals $A$.
][
  // Background, algorithm, example with CeTZ diagram
]
```

**6c. Write body:** Background on database normalization (2NF/3NF), cite Lucchesi & Osborne (1978), brute-force complexity, and a worked example with a visualization showing attributes and functional dependencies.

**6d. Build paper:**
```bash
make paper
```

### Task 2.2: Verify everything

```bash
make check
make paper
```

## Dependencies

- Batch 2 depends on Batch 1 (paper entry needs exports from implemented model).
- No external model dependencies (this is a standalone model).
