#!/usr/bin/env python3
"""Skill-scoped context bundle CLI skeleton."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEFAULT_STATE_FILES = {
    "review-pipeline": Path("/tmp/problemreductions-review-state.json"),
    "final-review": Path("/tmp/problemreductions-final-review-state.json"),
}


def build_status_result(skill: str, *, status: str, **fields: object) -> dict:
    result = {
        "skill": skill,
        "status": status,
    }
    for key, value in fields.items():
        if value is not None:
            result[key] = value
    return result


def emit_result(result: dict, fmt: str) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def build_review_pipeline_context(
    *,
    repo: str,
    pr_number: int | None,
    state_file: Path,
) -> dict:
    raise NotImplementedError("review-pipeline bundle is implemented in a later chunk")


def build_final_review_context(
    *,
    repo: str,
    pr_number: int | None,
    state_file: Path,
) -> dict:
    raise NotImplementedError("final-review bundle is implemented in a later chunk")


def add_bundle_parser(
    subparsers,
    command: str,
) -> None:
    parser = subparsers.add_parser(command)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", type=int)
    parser.add_argument(
        "--state-file",
        type=Path,
        default=DEFAULT_STATE_FILES[command],
    )
    parser.add_argument("--format", choices=["json", "text"], default="json")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Skill-scoped pipeline context bundles.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_bundle_parser(subparsers, "review-pipeline")
    add_bundle_parser(subparsers, "final-review")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.command == "review-pipeline":
        emit_result(
            build_review_pipeline_context(
                repo=args.repo,
                pr_number=args.pr,
                state_file=args.state_file,
            ),
            args.format,
        )
        return 0

    if args.command == "final-review":
        emit_result(
            build_final_review_context(
                repo=args.repo,
                pr_number=args.pr,
                state_file=args.state_file,
            ),
            args.format,
        )
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
