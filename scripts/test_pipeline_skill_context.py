#!/usr/bin/env python3
import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import pipeline_skill_context


class PipelineSkillContextTests(unittest.TestCase):
    def test_parse_args_review_pipeline_defaults(self) -> None:
        args = pipeline_skill_context.parse_args(
            [
                "review-pipeline",
                "--repo",
                "CodingThrust/problem-reductions",
            ]
        )

        self.assertEqual(args.command, "review-pipeline")
        self.assertEqual(args.repo, "CodingThrust/problem-reductions")
        self.assertIsNone(args.pr)
        self.assertEqual(
            args.state_file,
            Path("/tmp/problemreductions-review-state.json"),
        )
        self.assertEqual(args.format, "json")

    def test_parse_args_final_review_with_explicit_values(self) -> None:
        args = pipeline_skill_context.parse_args(
            [
                "final-review",
                "--repo",
                "CodingThrust/problem-reductions",
                "--pr",
                "615",
                "--state-file",
                "/tmp/custom-final-review-state.json",
                "--format",
                "text",
            ]
        )

        self.assertEqual(args.command, "final-review")
        self.assertEqual(args.repo, "CodingThrust/problem-reductions")
        self.assertEqual(args.pr, 615)
        self.assertEqual(
            args.state_file,
            Path("/tmp/custom-final-review-state.json"),
        )
        self.assertEqual(args.format, "text")

    def test_emit_result_prints_sorted_json_for_all_formats(self) -> None:
        expected_output = '{\n  "a": 2,\n  "b": 1\n}\n'

        for fmt in ["json", "text"]:
            with self.subTest(fmt=fmt):
                stdout = io.StringIO()
                with redirect_stdout(stdout):
                    pipeline_skill_context.emit_result({"b": 1, "a": 2}, fmt)
                self.assertEqual(stdout.getvalue(), expected_output)

    def test_build_status_result_normalizes_empty_state(self) -> None:
        self.assertEqual(
            pipeline_skill_context.build_status_result(
                "review-pipeline",
                status="empty",
            ),
            {
                "skill": "review-pipeline",
                "status": "empty",
            },
        )

    def test_build_status_result_normalizes_manual_choice_state(self) -> None:
        options = [{"item_id": "PVTI_1", "pr_number": 173}]

        self.assertEqual(
            pipeline_skill_context.build_status_result(
                "review-pipeline",
                status="needs-user-choice",
                options=options,
                recommendation=173,
            ),
            {
                "skill": "review-pipeline",
                "status": "needs-user-choice",
                "options": options,
                "recommendation": 173,
            },
        )

    def test_main_review_pipeline_emits_ready_bundle_shape(self) -> None:
        result = {
            "skill": "review-pipeline",
            "status": "ready",
            "selection": {"item_id": "PVTI_1", "pr_number": 173},
            "prep": {"ready": True},
            "pr": {"number": 173},
        }

        with mock.patch.object(
            pipeline_skill_context,
            "build_review_pipeline_context",
            return_value=result,
        ) as builder:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = pipeline_skill_context.main(
                    [
                        "review-pipeline",
                        "--repo",
                        "CodingThrust/problem-reductions",
                    ]
                )

        builder.assert_called_once_with(
            repo="CodingThrust/problem-reductions",
            pr_number=None,
            state_file=Path("/tmp/problemreductions-review-state.json"),
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), result)

    def test_main_final_review_emits_ready_bundle_shape(self) -> None:
        result = {
            "skill": "final-review",
            "status": "ready",
            "selection": {"item_id": "PVTI_2", "pr_number": 615},
            "prep": {"ready": True},
            "pr": {"number": 615},
            "review_context": {"files": ["src/lib.rs"]},
        }

        with mock.patch.object(
            pipeline_skill_context,
            "build_final_review_context",
            return_value=result,
        ) as builder:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = pipeline_skill_context.main(
                    [
                        "final-review",
                        "--repo",
                        "CodingThrust/problem-reductions",
                        "--pr",
                        "615",
                    ]
                )

        builder.assert_called_once_with(
            repo="CodingThrust/problem-reductions",
            pr_number=615,
            state_file=Path("/tmp/problemreductions-final-review-state.json"),
        )
        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), result)

    def test_build_review_pipeline_context_is_not_implemented_yet(self) -> None:
        with self.assertRaises(NotImplementedError):
            pipeline_skill_context.build_review_pipeline_context(
                repo="CodingThrust/problem-reductions",
                pr_number=None,
                state_file=Path("/tmp/problemreductions-review-state.json"),
            )

    def test_build_final_review_context_is_not_implemented_yet(self) -> None:
        with self.assertRaises(NotImplementedError):
            pipeline_skill_context.build_final_review_context(
                repo="CodingThrust/problem-reductions",
                pr_number=None,
                state_file=Path("/tmp/problemreductions-final-review-state.json"),
            )


if __name__ == "__main__":
    unittest.main()
