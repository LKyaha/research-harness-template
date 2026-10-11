#!/usr/bin/env python3
"""Cheap GitHub-hosted gate before scheduling a self-hosted Harness job.

This is an optimization, not the one-shot claim or stale-dispatch authority.
worker.py must still validate and claim on the remote base before execution.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from harness import validate_repository, worker


def readiness(task: dict) -> tuple[bool, str]:
    """Fail closed on malformed tasks; skip intentionally non-executable ones."""
    worker.validate_task(task)
    if task["status"] != "READY":
        return False, f"status={task['status']}"
    if task["autonomy"] == "HUMAN_REVIEW_REQUIRED":
        return False, "HUMAN_REVIEW_REQUIRED"
    if not task.get("issued_at"):
        raise ValueError("READY task requires issued_at")

    inbox = worker.resolve_repo_path(task["inbox_path"]).read_text(encoding="utf-8")
    for label, expected in (
        ("Task ID", task["task_id"]),
        ("Autonomy decision", task["autonomy"]),
        ("Delivery mode", task["delivery_mode"]),
    ):
        observed = validate_repository.markdown_header(inbox, label)
        if observed != expected:
            raise ValueError(
                f"READY inbox header mismatch for {label}: "
                f"expected {expected!r}, observed {observed!r}"
            )
    return True, f"READY task {task['task_id']}"


def main() -> int:
    task = json.loads(worker.TASK_PATH.read_text(encoding="utf-8"))
    ready, reason = readiness(task)
    print(f"Harness preflight: {'dispatch' if ready else 'skip'} ({reason})")
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as output:
            output.write(f"ready={'true' if ready else 'false'}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
