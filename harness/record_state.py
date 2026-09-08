#!/usr/bin/env python3
"""Commit/push only communication state after a Harness execution.

Intentional project source/report commits should be created by the Harness itself.
This helper deliberately avoids `git add -A`.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAFE_PATHS = [
    "HARNESS_OUTBOX.md",
    ".harness/completed.json",
    ".harness/last_worker_run.json",
]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
    )


def main() -> int:
    git("config", "user.name", "research-harness[bot]")
    git("config", "user.email", "research-harness[bot]@users.noreply.github.com")

    existing = [p for p in SAFE_PATHS if (ROOT / p).exists()]
    if existing:
        git("add", "--", *existing)

    diff = git("diff", "--cached", "--quiet", check=False)
    if diff.returncode not in (0, 1):
        return diff.returncode

    if diff.returncode == 1:
        task = json.loads((ROOT / ".harness" / "task.json").read_text(encoding="utf-8"))
        git("commit", "-m", f"harness: record {task['task_id']} result")

    branch = os.environ.get("GITHUB_REF_NAME", "").strip()
    if not branch:
        branch = git("branch", "--show-current", check=True).stdout.strip() if False else ""
    if not branch:
        # workflow sets GITHUB_REF_NAME; manual invocation may pass branch explicitly instead
        raise RuntimeError("GITHUB_REF_NAME is empty; refusing to guess push target")

    git("push", "origin", f"HEAD:{branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
