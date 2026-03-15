#!/usr/bin/env python3
"""Skill-scoped context bundle CLI skeleton."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

import pipeline_board
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
