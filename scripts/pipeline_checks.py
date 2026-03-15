#!/usr/bin/env python3
"""Deterministic review checks for scope detection and file whitelists."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


MODEL_WHITELIST = [
    "src/models/",
    "src/unit_tests/models/",
    "src/example_db/model_builders.rs",
    "src/example_db/rule_builders.rs",
    "docs/paper/reductions.typ",
    "docs/src/reductions/problem_schemas.json",
    "docs/src/reductions/reduction_graph.json",
    "tests/suites/trait_consistency.rs",
]

RULE_WHITELIST = [
    "src/rules/",
    "src/unit_tests/rules/",
    "src/example_db/rule_builders.rs",
    "src/models/",
    "docs/paper/reductions.typ",
    "docs/src/reductions/reduction_graph.json",
    "docs/src/reductions/problem_schemas.json",
]

IGNORED_RULE_FILES = {
    "src/rules/mod.rs",
    "src/rules/traits.rs",
    "src/rules/cost.rs",
    "src/rules/graph.rs",
    "src/rules/registry.rs",
}


def snake_to_camel(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_") if part)


def is_new_model_file(path: str) -> bool:
    return (
        path.startswith("src/models/")
        and path.endswith(".rs")
        and not path.endswith("/mod.rs")
    )


def is_new_rule_file(path: str) -> bool:
    return (
        path.startswith("src/rules/")
        and path.endswith(".rs")
        and path not in IGNORED_RULE_FILES
        and not path.endswith("/mod.rs")
    )


def detect_scope_from_paths(*, added_files: list[str], changed_files: list[str]) -> dict:
    models = []
    rules = []

    for path in added_files:
        if is_new_model_file(path):
            parts = path.split("/")
            category = parts[2]
            file_stem = Path(path).stem
            models.append(
                {
                    "path": path,
                    "category": category,
                    "file_stem": file_stem,
                    "problem_name": snake_to_camel(file_stem),
                }
            )
        elif is_new_rule_file(path):
            rules.append(
                {
                    "path": path,
                    "rule_stem": Path(path).stem,
                }
            )

    if models and rules:
        review_type = "model+rule"
    elif models:
        review_type = "model"
    elif rules:
        review_type = "rule"
    else:
        review_type = "generic"

    return {
        "review_type": review_type,
        "models": models,
        "rules": rules,
        "added_files": list(added_files),
        "changed_files": list(changed_files),
    }


def path_allowed(kind: str, path: str) -> tuple[bool, str | None]:
    if kind == "model":
        allowed = any(
            path == prefix or path.startswith(prefix)
            for prefix in MODEL_WHITELIST
        )
        if not allowed:
            return False, "not in whitelist for model PR"
        return True, None

    if kind == "rule":
        allowed = any(
            path == prefix or path.startswith(prefix)
            for prefix in RULE_WHITELIST
        )
        if not allowed:
            return False, "not in whitelist for rule PR"
        return True, None

    raise ValueError(f"Unsupported whitelist kind: {kind}")


def file_whitelist_check(kind: str, files: list[str]) -> dict:
    violations = []
    for path in files:
        ok, reason = path_allowed(kind, path)
        if not ok:
            violations.append({"path": path, "reason": reason})

    return {
        "kind": kind,
        "ok": not violations,
        "files": list(files),
        "violations": violations,
    }


def git_output(*args: str) -> list[str]:
    output = subprocess.check_output(["git", *args], text=True)
    return [line for line in output.splitlines() if line]


def load_file_list(path: str | Path) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [line.strip() for line in lines if line.strip()]


def emit_result(result: dict, fmt: str) -> None:
    print(json.dumps(result, indent=2, sort_keys=True))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline review checks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect = subparsers.add_parser("detect-scope")
    detect.add_argument("--base", required=True)
    detect.add_argument("--head", required=True)
    detect.add_argument("--format", choices=["json", "text"], default="json")

    whitelist = subparsers.add_parser("file-whitelist")
    whitelist.add_argument("--kind", choices=["model", "rule"], required=True)
    whitelist.add_argument("--files-file", required=True)
    whitelist.add_argument("--format", choices=["json", "text"], default="json")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.command == "detect-scope":
        changed_files = git_output("diff", "--name-only", f"{args.base}..{args.head}")
        added_files = git_output(
            "diff",
            "--name-only",
            "--diff-filter=A",
            f"{args.base}..{args.head}",
        )
        emit_result(
            detect_scope_from_paths(
                added_files=added_files,
                changed_files=changed_files,
            ),
            args.format,
        )
        return 0

    if args.command == "file-whitelist":
        emit_result(
            file_whitelist_check(args.kind, load_file_list(args.files_file)),
            args.format,
        )
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
