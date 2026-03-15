---
name: fix-pr
description: Use when a PR has review comments to address, CI failures to fix, or codecov coverage gaps to resolve
---

# Fix PR

Resolve PR review comments, fix CI failures, and address codecov coverage gaps for the current branch's PR.

## Step 1: Gather PR State

Use the shared scripted helpers for deterministic PR metadata, comment, CI, and Codecov collection. Do not rebuild this logic inline with `gh api | python3 -c` unless you are debugging the helper itself.

```bash
# Get current branch PR context
CURRENT=$(python3 scripts/pipeline_pr.py current --format json)
REPO=$(printf '%s\n' "$CURRENT" | python3 -c "import sys,json; print(json.load(sys.stdin)['repo'])")
PR=$(printf '%s\n' "$CURRENT" | python3 -c "import sys,json; print(json.load(sys.stdin)['pr_number'])")

# Get structured PR state
SNAPSHOT=$(python3 scripts/pipeline_pr.py snapshot --repo "$REPO" --pr "$PR" --format json)
COMMENTS=$(python3 scripts/pipeline_pr.py comments --repo "$REPO" --pr "$PR" --format json)
CI=$(python3 scripts/pipeline_pr.py ci --repo "$REPO" --pr "$PR" --format json)
CODECOV=$(python3 scripts/pipeline_pr.py codecov --repo "$REPO" --pr "$PR" --format json)

# Extract the current head SHA when needed
HEAD_SHA=$(printf '%s\n' "$SNAPSHOT" | python3 -c "import sys,json; print(json.load(sys.stdin)['head_sha'])")
```

### 1a. Fetch Review Comments

**Check ALL four sources.** User inline comments are the most commonly missed — do not skip any.

Read the `COMMENTS` JSON and inspect these arrays:
- `inline_comments` — all inline review comments
- `reviews` — top-level review bodies
- `human_issue_comments` — PR conversation comments excluding bots and Codecov
- `human_linked_issue_comments` — linked issue comments excluding bots
- `codecov_comments` — PR conversation comments from Codecov only

Use `COMMENTS["counts"]` to verify whether any source is genuinely empty before assuming there is no feedback.

### 1b. Check CI Status

Read the `CI` JSON. It includes:
- `state` — `pending`, `failure`, or `success`
- `runs` — normalized check-run details
- `pending` / `failing` / `succeeding` counts

### 1c. Check Codecov Report

Read the `CODECOV` JSON. It includes:
- `found` — whether a Codecov comment is present
- `patch_coverage`
- `project_coverage`
- `filepaths` — deduplicated paths referenced by Codecov links
- `body` — the raw latest Codecov comment body

## Step 2: Triage and Prioritize

Categorize all findings:

| Priority | Type | Action |
|----------|------|--------|
| 1 | CI failures (clippy/test/coverage) | Fix immediately — blocks merge |
| 2 | User inline/review comments | Address each one — highest review priority |
| 3 | Copilot inline suggestions | Evaluate validity, fix if correct |
| 4 | Codecov coverage gaps | Add tests for uncovered lines |

**User comments always take priority over bot comments.** A user inline comment requesting file deletion is just as important as a user review requesting a code change.

## Step 3: Fix CI Failures

For each failing check:

1. **Clippy**: Run `make clippy` locally, fix warnings
2. **Test**: Run `make test` locally, fix failures (build errors surface here too)
3. **Code Coverage**: See Step 5 (codecov-specific flow)

## Step 4: Address Review Comments

For each review comment:

1. Read the comment and the code it references
2. Evaluate if the suggestion is correct
3. If valid: make the fix, commit
4. If debatable: fix it anyway unless technically wrong
5. If wrong: prepare a response explaining why

**Do NOT respond on the PR** -- just fix and commit. The user will push and respond.

### Handling Copilot Suggestions

Copilot suggestions with `suggestion` blocks contain exact code. Evaluate each:
- **Correct**: Apply the suggestion
- **Partially correct**: Apply the spirit, adjust details
- **Wrong**: Skip, note why in commit message

## Step 5: Fix Codecov Coverage Gaps

**IMPORTANT: Do NOT run `cargo-llvm-cov` locally.** Use the `gh api` to read the codecov report instead.

### 5a. Identify Uncovered Lines

From the `CODECOV` JSON (fetched in Step 1c), extract:
- Files with missing coverage
- Patch coverage percentage
- Specific uncovered files referenced in `filepaths`

Then read the source files and identify which new/changed lines lack test coverage.

### 5b. Add Tests for Uncovered Lines

1. Read the uncovered file and identify the untested code paths
2. Write tests targeting those specific paths (error branches, edge cases, etc.)
3. Run `make test` to verify tests pass
4. Commit the new tests

### 5c. Verify Coverage Improvement

After pushing, CI will re-run coverage. Check the updated codecov comment on the PR.

## Step 6: Commit and Report

After all fixes:

```bash
# Verify everything passes locally
make check  # fmt + clippy + test
```

Commit with a descriptive message referencing the PR:

```bash
git commit -m "fix: address PR #$PR review comments

- [summary of fixes applied]
"
```

Report to user:
- List of review comments addressed (with what was done)
- CI fixes applied
- Coverage gaps filled
- Any comments left unresolved (with reasoning)

## Integration

### With review-implementation

Run `/review-implementation` first to catch issues before push. Then `/fix-pr` after push to address CI and reviewer feedback.

### With executing-plans / finishing-a-development-branch

After creating a PR and running `make copilot-review`, use `/fix-pr` to address the resulting feedback.
