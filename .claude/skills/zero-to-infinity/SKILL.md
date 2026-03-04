---
name: zero-to-infinity
description: Use when you want to discover and prioritize new problems and reduction rules to add to the codebase, based on user-ranked impact dimensions
---

# Zero to Infinity

Discover high-impact problems and reduction rules, rank them by user priorities, and file them as GitHub issues — feeding the existing `issue-to-pr` / `meta-power` pipeline.

## Overview

This skill bridges "what should we add next?" with the implementation pipeline. It does NOT write code — it creates well-formed `[Model]` and `[Rule]` issues that downstream skills can implement.

## Step 1: Survey — Rank Impact Dimensions

Present all impact dimensions in a single `AskUserQuestion` prompt. The user ranks them by importance.

**Default dimensions:**

| # | Dimension | Description |
|---|-----------|-------------|
| 0 | Academic Publications | Papers in JACM, SICOMP, and top CS venues studying this problem/reduction |
| 1 | Industrial Application | Real-world use cases (search engines, navigation, scheduling, compilers) |
| 2 | Cross-Field Application | Relevance to physics, chemistry, biology, or other scientific domains |
| 3 | Top-Scientists Interest | Featured in Karp's 21, Garey & Johnson, or by researchers like Aaronson |
| 4 | Graph Connectivity | Bridges disconnected components in the existing reduction graph |
| 5 | Pedagogical Value | Clean, illustrative reductions good for teaching |

Ask:
```
Rank these impact dimensions from most to least important (1 = most important).
You may also add custom dimensions.
```

**Scoring weights:** For N dimensions, rank k gets weight N - k + 1.

## Step 2: Discover — Web Search + Graph Gap Analysis

Run two discovery channels **in parallel** (use `dispatching-parallel-agents` or concurrent subagents):

### Channel A: Web Search

Run multiple search queries targeting the user's top-ranked dimensions:
- `"classical NP-complete problems Karp's 21 reductions"`
- `"NP-hard problems {top_dimension_keyword}"` (e.g., `"NP-hard problems industrial applications"`)
- `"polynomial reductions from {existing_problem}"` for each problem with few outgoing edges
- `"important reductions computational complexity textbook"`

For each candidate, collect:
- Formal problem name
- Brief definition
- Known reductions to/from other problems
- Complexity class and best known algorithms
- Reference URLs

### Channel B: Reduction Graph Gap Analysis

```bash
cat docs/data/reduction_graph.json
```

Identify:
- **Dead-end problems**: nodes with no outgoing reductions
- **Missing natural reductions**: pairs of related problems without a direct edge (e.g., SAT variants, graph complement problems)
- **Disconnected components**: subgraphs that could be bridged by a single reduction
- **Well-known textbook reductions** not yet implemented (cross-reference with Garey & Johnson, CLRS, Arora & Barak)

### Deduplication

Before proceeding, filter out candidates that already exist:

```bash
# Check implemented models
ls src/models/*/

# Check implemented rules
ls src/rules/

# Check open issues
gh issue list --state open --limit 100 --json title,number

# Check recently closed issues
gh issue list --state closed --limit 100 --json title,number
```

Remove any candidate that matches an existing model, rule, or issue.

## Step 3: Rank — Score and Sort

For each candidate, assign a score (0-5) per dimension:

| Score | Meaning |
|-------|---------|
| 0 | No relevance |
| 1 | Marginal |
| 2 | Some relevance |
| 3 | Moderate |
| 4 | Strong |
| 5 | Exceptional |

**Total score** = sum of (dimension_score × dimension_weight) for all dimensions.

Sort candidates by total score descending. Present the top 10 as a table:

```
| # | Type  | Name              | Score | Top Dimensions Hit         |
|---|-------|-------------------|-------|----------------------------|
| 1 | Model | SubsetSum         | 23    | Academic(5), Industry(4)   |
| 2 | Rule  | 3SAT → MaxCut     | 21    | Academic(5), TopSci(4)     |
| 3 | Model | HamiltonianPath   | 18    | Pedagogical(3), GraphConn(5)|
...
```

Include a 1-line justification for each candidate's top scores.

## Step 4: Select — User Picks Candidates

Use `AskUserQuestion` with `multiSelect: true` to let the user choose which candidates to file as issues.

Present each candidate as an option with its score and type (Model/Rule) in the label.

## Step 5: File — Create GitHub Issues

For each selected candidate, draft a GitHub issue following the existing conventions:

### For `[Model]` candidates

Fill in all 11 items from the [add-model](../add-model/SKILL.md) Step 0 checklist:

1. Problem name (with optimization prefix)
2. Mathematical definition
3. Problem type (optimization/satisfaction)
4. Type parameters
5. Struct fields
6. Configuration space (`dims()`)
7. Feasibility check
8. Objective function
9. Best known exact algorithm (with citation)
10. Solving strategy
11. Category (`graph/`, `formula/`, `set/`, `algebraic/`, `misc/`)

### For `[Rule]` candidates

Fill in all 9 items from the [add-rule](../add-rule/SKILL.md) Step 0 checklist:

1. Source problem
2. Target problem
3. Reduction algorithm
4. Solution extraction
5. Correctness argument
6. Size overhead
7. Concrete example
8. Solving strategy
9. Reference (URL or citation)

### Filing Process

1. Show the draft issue to the user for confirmation
2. Create via:
   ```bash
   gh issue create --title "[Model] ProblemName" --body "$(cat <<'EOF'
   <issue body>
   EOF
   )"
   ```
3. Report the created issue number and URL

**All web search results must be cited with URLs in the issue body.**

## Step 6: Implement (Optional)

After all issues are filed, ask:

```
Would you like to invoke meta-power to automatically implement these issues?
```

If yes, invoke the `meta-power` skill. If no, stop — the user can run `/meta-power` later.

## Key Constraints

- **No code writing**: This skill only creates issues. Implementation is delegated to downstream skills.
- **No duplicates**: Deduplication check (Step 2) is mandatory before presenting candidates.
- **Template compliance**: Every issue must fully satisfy the `add-model` or `add-rule` checklist. Incomplete issues get rejected by `issue-to-pr`.
- **Citations required**: Every claim about a problem's complexity, applications, or significance must include a reference URL.
- **User approval gates**: The user approves at two points — candidate selection (Step 4) and issue draft confirmation (Step 5).

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Filing issues without dedup check | Always run deduplication (Step 2) first |
| Incomplete issue templates | Fill ALL checklist items — `issue-to-pr` will reject incomplete ones |
| Missing citations | Every complexity claim and reference needs a URL |
| Inventing problem definitions | Use web search results, not hallucinated definitions |
| Filing without user confirmation | Show draft, get approval, then file |
| Scoring without web evidence | Dimension scores must be justified by search results |
