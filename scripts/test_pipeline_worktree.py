#!/usr/bin/env python3
import unittest

from pipeline_worktree import (
    plan_issue_worktree,
    plan_pr_worktree,
    summarize_merge,
)


class PipelineWorktreeTests(unittest.TestCase):
    def test_plan_issue_worktree_sanitizes_slug_and_uses_worktrees_dir(self) -> None:
        plan = plan_issue_worktree(
            "/tmp/problemreductions",
            issue_number=117,
            slug="Graph Partitioning / Exact",
            base_ref="origin/main",
        )

        self.assertEqual(plan["branch"], "issue-117-graph-partitioning-exact")
        self.assertEqual(
            plan["worktree_dir"],
            "/tmp/problemreductions/.worktrees/issue-117-graph-partitioning-exact",
        )
        self.assertEqual(plan["base_ref"], "origin/main")

    def test_plan_pr_worktree_uses_pull_ref_and_sanitized_local_branch(self) -> None:
        plan = plan_pr_worktree(
            "/tmp/problemreductions",
            pr_number=570,
            head_ref_name="feature/lcs cleanup",
            base_sha="base123",
            head_sha="head456",
        )

        self.assertEqual(plan["local_branch"], "review-pr-570-feature-lcs-cleanup")
        self.assertEqual(
            plan["worktree_dir"],
            "/tmp/problemreductions/.worktrees/review-pr-570-feature-lcs-cleanup",
        )
        self.assertEqual(
            plan["fetch_ref"],
            "pull/570/head:review-pr-570-feature-lcs-cleanup",
        )
        self.assertEqual(plan["base_sha"], "base123")
        self.assertEqual(plan["head_sha"], "head456")

    def test_summarize_merge_clean_result(self) -> None:
        summary = summarize_merge(
            worktree="/tmp/problemreductions/.worktrees/review-pr-570",
            exit_code=0,
            conflicts=[],
        )

        self.assertEqual(summary["status"], "clean")
        self.assertFalse(summary["likely_complex"])
        self.assertEqual(summary["conflicts"], [])

    def test_summarize_merge_conflicted_result_marks_complex_skill_conflicts(self) -> None:
        summary = summarize_merge(
            worktree="/tmp/problemreductions/.worktrees/review-pr-570",
            exit_code=1,
            conflicts=[
                ".claude/skills/add-model/SKILL.md",
                "src/models/graph/graph_partitioning.rs",
            ],
        )

        self.assertEqual(summary["status"], "conflicted")
        self.assertTrue(summary["likely_complex"])
        self.assertEqual(
            summary["conflicts"],
            [
                ".claude/skills/add-model/SKILL.md",
                "src/models/graph/graph_partitioning.rs",
            ],
        )

    def test_summarize_merge_without_conflicts_is_aborted(self) -> None:
        summary = summarize_merge(
            worktree="/tmp/problemreductions/.worktrees/review-pr-570",
            exit_code=128,
            conflicts=[],
        )

        self.assertEqual(summary["status"], "aborted")
        self.assertFalse(summary["likely_complex"])


if __name__ == "__main__":
    unittest.main()
