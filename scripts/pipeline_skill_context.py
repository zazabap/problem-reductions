#!/usr/bin/env python3
"""Skill-scoped context bundle CLI skeleton."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pipeline_board
import pipeline_checks
import pipeline_pr
import pipeline_worktree


DEFAULT_STATE_FILES = {
    "review-pipeline": Path("/tmp/problemreductions-review-state.json"),
    "final-review": Path("/tmp/problemreductions-final-review-state.json"),
}
PROJECT_BOARD_NUMBER = 8
PROJECT_BOARD_LIMIT = 500


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


def fetch_review_candidates(repo: str) -> list[dict]:
    owner = repo.split("/", 1)[0]
    board_data = pipeline_board.fetch_board_items(
        owner,
        PROJECT_BOARD_NUMBER,
        PROJECT_BOARD_LIMIT,
    )
    return pipeline_board.review_candidates(
        board_data,
        repo,
        pipeline_board.fetch_pr_reviews,
        pipeline_board.resolve_issue_pr,
        pipeline_board.fetch_pr_info,
    )


def claim_review_entry(
    *,
    repo: str,
    state_file: Path,
    pr_number: int | None,
) -> dict | None:
    owner = repo.split("/", 1)[0]
    board_data = pipeline_board.fetch_board_items(
        owner,
        PROJECT_BOARD_NUMBER,
        PROJECT_BOARD_LIMIT,
    )
    return pipeline_board.claim_next_entry(
        "review",
        board_data,
        state_file,
        repo=repo,
        review_fetcher=pipeline_board.fetch_pr_reviews,
        pr_resolver=pipeline_board.resolve_issue_pr,
        pr_state_fetcher=pipeline_board.fetch_pr_state,
        target_number=pr_number,
    )


def build_ready_result(*, skill: str, selection: dict, pr: dict, prep: dict) -> dict:
    return build_status_result(
        skill,
        status="ready",
        selection=selection,
        pr=pr,
        prep=prep,
    )


def build_ambiguous_selection(candidate: dict, *, pr_number: int) -> dict:
    return {
        "item_id": candidate["item_id"],
        "number": pr_number,
        "issue_number": candidate.get("issue_number"),
        "pr_number": pr_number,
        "status": candidate.get("status"),
        "title": candidate.get("title"),
        "claimed": True,
        "claimed_status": pipeline_board.STATUS_UNDER_REVIEW,
    }


def select_final_review_entry(
    *,
    repo: str,
    state_file: Path,
    pr_number: int | None,
) -> dict | None:
    owner = repo.split("/", 1)[0]
    board_data = pipeline_board.fetch_board_items(
        owner,
        PROJECT_BOARD_NUMBER,
        PROJECT_BOARD_LIMIT,
    )
    return pipeline_board.select_next_entry(
        "final-review",
        board_data,
        state_file,
        repo=repo,
        pr_resolver=pipeline_board.resolve_issue_pr,
        pr_state_fetcher=pipeline_board.fetch_pr_state,
        target_number=pr_number,
    )


def git_output_in(repo_root: str | Path, *args: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", str(repo_root), *args],
        text=True,
    )
    return [line for line in output.splitlines() if line]


def git_text_in(repo_root: str | Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(repo_root), *args],
        text=True,
    )


def infer_final_review_subject(scope: dict, pr_context: dict) -> dict:
    subject = pipeline_checks.infer_review_subject(scope)
    linked_issue = pr_context.get("linked_issue") or {}
    linked_title = (linked_issue.get("title") or "").strip()

    rule_match = pipeline_checks.RULE_TITLE_RE.match(linked_title)
    if rule_match:
        subject["kind"] = "rule"
        subject["source"] = rule_match.group("source")
        subject["target"] = rule_match.group("target")
        return subject

    model_match = pipeline_checks.MODEL_TITLE_RE.match(linked_title)
    if model_match:
        subject["kind"] = "model"
        subject["name"] = subject.get("name") or model_match.group("name")
        subject["source"] = None
        subject["target"] = None

    return subject


def build_final_review_checks(*, prep: dict, pr_context: dict) -> dict:
    checkout = prep.get("checkout") or {}
    worktree_dir = checkout.get("worktree_dir")
    base_sha = checkout.get("base_sha")
    head_sha = checkout.get("head_sha")
    if not worktree_dir or not base_sha or not head_sha:
        raise ValueError("prepare-review output missing checkout diff range")

    diff_range = f"{base_sha}..{head_sha}"
    changed_files = git_output_in(worktree_dir, "diff", "--name-only", diff_range)
    added_files = git_output_in(
        worktree_dir,
        "diff",
        "--name-only",
        "--diff-filter=A",
        diff_range,
    )
    scope = pipeline_checks.detect_scope_from_paths(
        added_files=added_files,
        changed_files=changed_files,
    )
    subject = infer_final_review_subject(scope, pr_context)
    return pipeline_checks.build_review_context(
        worktree_dir,
        diff_stat=git_text_in(worktree_dir, "diff", "--stat", diff_range),
        scope=scope,
        subject=subject,
    )


def build_review_pipeline_context(
    *,
    repo: str,
    pr_number: int | None,
    state_file: Path,
    review_candidate_fetcher: Callable[[str], list[dict]] | None = None,
    claim_entry: Callable[..., dict | None] | None = None,
    pr_context_builder: Callable[[str, int], dict] | None = None,
    review_preparer: Callable[[str, int], dict] | None = None,
    mover: Callable[[str, str], None] | None = None,
) -> dict:
    review_candidate_fetcher = review_candidate_fetcher or fetch_review_candidates
    claim_entry = claim_entry or claim_review_entry
    pr_context_builder = pr_context_builder or pipeline_pr.build_pr_context
    review_preparer = review_preparer or (
        lambda repo, pr_number: pipeline_worktree.prepare_review(
            repo=repo,
            pr_number=pr_number,
        )
    )
    mover = mover or pipeline_board.move_item

    candidates = review_candidate_fetcher(repo)
    if not candidates:
        return build_status_result("review-pipeline", status="empty")

    if pr_number is None:
        ambiguous = next(
            (
                candidate
                for candidate in candidates
                if candidate.get("eligibility") == "ambiguous-linked-prs"
            ),
            None,
        )
        if ambiguous is not None:
            return build_status_result(
                "review-pipeline",
                status="needs-user-choice",
                options=ambiguous.get("linked_repo_prs", []),
                recommendation=ambiguous.get("recommendation"),
            )

        selection = claim_entry(
            repo=repo,
            state_file=state_file,
            pr_number=None,
        )
        if selection is None:
            return build_status_result("review-pipeline", status="empty")

        selected_pr_number = int(selection["pr_number"])
        return build_ready_result(
            skill="review-pipeline",
            selection=selection,
            pr=pr_context_builder(repo, selected_pr_number),
            prep=review_preparer(repo, selected_pr_number),
        )

    matching_ambiguous = next(
        (
            candidate
            for candidate in candidates
            if candidate.get("eligibility") == "ambiguous-linked-prs"
            and any(
                int(option["number"]) == pr_number
                for option in candidate.get("linked_repo_prs", [])
            )
        ),
        None,
    )
    if matching_ambiguous is not None:
        mover(str(matching_ambiguous["item_id"]), pipeline_board.STATUS_UNDER_REVIEW)
        selection = build_ambiguous_selection(
            matching_ambiguous,
            pr_number=pr_number,
        )
        return build_ready_result(
            skill="review-pipeline",
            selection=selection,
            pr=pr_context_builder(repo, pr_number),
            prep=review_preparer(repo, pr_number),
        )

    matching_candidate = next(
        (
            candidate
            for candidate in candidates
            if int(candidate.get("pr_number") or candidate.get("number") or -1) == pr_number
        ),
        None,
    )
    if matching_candidate is None:
        return build_status_result("review-pipeline", status="empty")

    if matching_candidate.get("eligibility") != "eligible":
        return build_status_result("review-pipeline", status="empty")

    selection = claim_entry(
        repo=repo,
        state_file=state_file,
        pr_number=pr_number,
    )
    if selection is None:
        return build_status_result("review-pipeline", status="empty")

    return build_ready_result(
        skill="review-pipeline",
        selection=selection,
        pr=pr_context_builder(repo, pr_number),
        prep=review_preparer(repo, pr_number),
    )


def build_final_review_context(
    *,
    repo: str,
    pr_number: int | None,
    state_file: Path,
    selection_fetcher: Callable[..., dict | None] | None = None,
    pr_context_builder: Callable[[str, int], dict] | None = None,
    review_preparer: Callable[[str, int], dict] | None = None,
    review_context_builder: Callable[..., dict] | None = None,
) -> dict:
    selection_fetcher = selection_fetcher or select_final_review_entry
    pr_context_builder = pr_context_builder or pipeline_pr.build_pr_context
    review_preparer = review_preparer or (
        lambda repo, pr_number: pipeline_worktree.prepare_review(
            repo=repo,
            pr_number=pr_number,
        )
    )
    review_context_builder = review_context_builder or build_final_review_checks

    selection = selection_fetcher(
        repo=repo,
        state_file=state_file,
        pr_number=pr_number,
    )
    if selection is None:
        return build_status_result("final-review", status="empty")

    selected_pr_number = int(selection.get("pr_number") or selection["number"])
    pr_context = pr_context_builder(repo, selected_pr_number)

    prep: dict
    try:
        prep = review_preparer(repo, selected_pr_number)
    except Exception as exc:
        return {
            "skill": "final-review",
            "status": "ready-with-warnings",
            "selection": selection,
            "pr": pr_context,
            "prep": {
                "ready": False,
                "error": str(exc),
            },
            "review_context": None,
            "warnings": [
                f"failed to prepare final-review worktree: {exc}",
            ],
        }

    try:
        review_context = review_context_builder(
            prep=prep,
            pr_context=pr_context,
        )
    except Exception as exc:
        return {
            "skill": "final-review",
            "status": "ready-with-warnings",
            "selection": selection,
            "pr": pr_context,
            "prep": prep,
            "review_context": None,
            "warnings": [
                f"failed to derive final-review review context: {exc}",
            ],
        }

    return build_status_result(
        "final-review",
        status="ready",
        selection=selection,
        pr=pr_context,
        prep=prep,
        review_context=review_context,
    )


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
