#!/usr/bin/env python3
import unittest

from pipeline_checks import (
    detect_scope_from_paths,
    file_whitelist_check,
)


class PipelineChecksTests(unittest.TestCase):
    def test_detect_scope_reports_model_review_for_new_model_file(self) -> None:
        scope = detect_scope_from_paths(
            added_files=["src/models/graph/graph_partitioning.rs"],
            changed_files=[
                "src/models/graph/graph_partitioning.rs",
                "src/unit_tests/models/graph/graph_partitioning.rs",
            ],
        )

        self.assertEqual(scope["review_type"], "model")
        self.assertEqual(scope["models"][0]["category"], "graph")
        self.assertEqual(scope["models"][0]["file_stem"], "graph_partitioning")
        self.assertEqual(scope["models"][0]["problem_name"], "GraphPartitioning")

    def test_detect_scope_reports_rule_review_for_new_rule_file(self) -> None:
        scope = detect_scope_from_paths(
            added_files=["src/rules/binpacking_ilp.rs"],
            changed_files=["src/rules/binpacking_ilp.rs"],
        )

        self.assertEqual(scope["review_type"], "rule")
        self.assertEqual(scope["rules"][0]["rule_stem"], "binpacking_ilp")

    def test_detect_scope_reports_generic_when_no_new_model_or_rule_files(self) -> None:
        scope = detect_scope_from_paths(
            added_files=[],
            changed_files=["src/lib.rs", "docs/paper/reductions.typ"],
        )

        self.assertEqual(scope["review_type"], "generic")
        self.assertEqual(scope["models"], [])
        self.assertEqual(scope["rules"], [])

    def test_file_whitelist_accepts_expected_model_files(self) -> None:
        report = file_whitelist_check(
            "model",
            [
                "src/models/graph/graph_partitioning.rs",
                "src/unit_tests/models/graph/graph_partitioning.rs",
                "src/example_db/model_builders.rs",
                "docs/paper/reductions.typ",
                "docs/src/reductions/problem_schemas.json",
                "tests/suites/trait_consistency.rs",
            ],
        )

        self.assertTrue(report["ok"])
        self.assertEqual(report["violations"], [])

    def test_file_whitelist_flags_unexpected_model_files(self) -> None:
        report = file_whitelist_check(
            "model",
            [
                "src/models/graph/graph_partitioning.rs",
                "Cargo.toml",
            ],
        )

        self.assertFalse(report["ok"])
        self.assertEqual(report["violations"][0]["path"], "Cargo.toml")

    def test_file_whitelist_accepts_expected_rule_files(self) -> None:
        report = file_whitelist_check(
            "rule",
            [
                "src/rules/binpacking_ilp.rs",
                "src/rules/mod.rs",
                "src/unit_tests/rules/binpacking_ilp.rs",
                "src/example_db/rule_builders.rs",
                "src/models/graph/bin_packing.rs",
                "docs/paper/reductions.typ",
                "docs/src/reductions/reduction_graph.json",
            ],
        )

        self.assertTrue(report["ok"])
        self.assertEqual(report["violations"], [])


if __name__ == "__main__":
    unittest.main()
