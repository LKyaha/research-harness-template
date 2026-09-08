#!/usr/bin/env python3
"""Commit and push only Harness communication/protected-state repairs after execution.

Intentional project source/report commits should be created by the Harness itself.
This helper deliberately avoids `git add -A` and pushes the work branch recorded by
`worker.py`, which may be a PR branch rather than the base branch.

`worker.py` restores protected dispatcher files if the Harness changed them. They are
included here so that, even if the Harness committed a protected-file mutation, the
final branch diff contains a committed repair before push/review.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAST_RUN_PATH = ROOT / ".harness" / "last_worker_run.json"
SAFE_PATHS = [
    "HARNESS_OUTBOX.md",
    ".harness/last_worker_run.json",
    ".harness/task.json",
    ".harness/completed.json",
]


def git(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=capture,
    )


def main() -> int:
    if not LAST_RUN_PATH.exists():
        print("No last_worker_run.json; nothing to record")
        return 0

    run = json.loads(LAST_RUN_PATH.read_text(encoding="utf-8"))
    task_id = str(run["task_id"])
    work_branch = str(run["work_branch"])

    git("config", "user.name", "research-harness[bot]")
    git("config", "user.email", "research-harness[bot]@users.noreply.github.com")

    current = git("branch", "--show-current", capture=True).stdout.strip()
    if current != work_branch:
        raise RuntimeError(
            f"Harness changed git branch unexpectedly: current={current!r}, expected={work_branch!r}. "
            "Refusing to guess where results belong."
        )

    existing = [p for p in SAFE_PATHS if (ROOT / p).exists()]
    if existing:
        git("add", "--", *existing)

    diff = git("diff", "--cached", "--quiet", check=False)
    if diff.returncode not in (0, 1):
        return diff.returncode

    if diff.returncode == 1:
        git("commit", "-m", f"harness: record {task_id} result")

    # Push commits created intentionally by the Harness plus the communication/repair commit.
    # Arbitrary uncommitted files remain untracked/unstaged by design.
    git("push", "origin", f"HEAD:{work_branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
