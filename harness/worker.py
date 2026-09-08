#!/usr/bin/env python3
"""Event-driven local Harness dispatcher.

The worker consumes exactly one machine-readable task from `.harness/task.json`.
It never invents the next research task.

Key guarantees:
- one task ID is claimed on the base branch before local execution;
- a claimed task is never automatically executed again;
- PULL_REQUEST delivery runs on `harness/<task_id>` instead of the base branch;
- the Harness cannot mutate its own trigger or consumption ledger in the final diff;
- retries require a new task ID.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / ".harness" / "task.json"
COMPLETED_PATH = ROOT / ".harness" / "completed.json"
LAST_RUN_PATH = ROOT / ".harness" / "last_worker_run.json"

ALLOWED_AUTONOMY = {"AUTO_CONTINUE", "AUTO_REPAIR", "HUMAN_REVIEW_REQUIRED"}
ALLOWED_DELIVERY = {"DIRECT", "PULL_REQUEST"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    tmp.replace(path)


def git(*args: str, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=capture,
    )


def validate_task(task: dict) -> None:
    required = [
        "schema_version",
        "task_id",
        "status",
        "autonomy",
        "delivery_mode",
        "inbox_path",
    ]
    missing = [k for k in required if k not in task]
    if missing:
        raise ValueError(f"task.json missing fields: {missing}")
    if task["schema_version"] != 1:
        raise ValueError("unsupported task schema_version")
    if not isinstance(task["task_id"], str) or not task["task_id"].strip():
        raise ValueError("task_id must be a non-empty string")
    if task["status"] not in {"IDLE", "READY"}:
        raise ValueError("status must be IDLE or READY")
    if task["autonomy"] not in ALLOWED_AUTONOMY:
        raise ValueError(f"unknown autonomy decision: {task['autonomy']}")
    if task["delivery_mode"] not in ALLOWED_DELIVERY:
        raise ValueError(f"unknown delivery_mode: {task['delivery_mode']}")
    if task["delivery_mode"] == "PULL_REQUEST":
        base = task.get("base_branch")
        if not isinstance(base, str) or not base.strip():
            raise ValueError("PULL_REQUEST delivery requires base_branch")
    inbox = ROOT / task["inbox_path"]
    if not inbox.exists():
        raise ValueError(f"inbox_path does not exist: {task['inbox_path']}")


def completed_ids(data: dict) -> set[str]:
    return set(data.get("completed_task_ids", []))


def safe_branch_component(task_id: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", task_id.strip()).strip(".-")
    if not value:
        raise ValueError("task_id cannot be converted to a safe branch name")
    return value[:120]


def remote_completed(base_branch: str) -> dict:
    proc = git("show", f"origin/{base_branch}:.harness/completed.json", check=False, capture=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        return {"schema_version": 1, "completed_task_ids": []}
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"remote completed.json is invalid: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError("remote completed.json must be a JSON object")
    return data


def prepare_and_claim(task: dict) -> tuple[dict, str, str]:
    """Fast-forward to base, atomically claim task on base, then choose work branch."""
    task_id = task["task_id"]
    base_branch = str(task.get("base_branch") or os.environ.get("GITHUB_REF_NAME") or "main")

    git("config", "user.name", "research-harness[bot]")
    git("config", "user.email", "research-harness[bot]@users.noreply.github.com")
    # Explicit refspec guarantees origin/<base> is refreshed, even when this is a re-run
    # of a workflow whose GITHUB_SHA points to an older dispatch commit.
    git("fetch", "origin", f"+refs/heads/{base_branch}:refs/remotes/origin/{base_branch}")

    completed = remote_completed(base_branch)
    if task_id in completed_ids(completed):
        return completed, base_branch, ""

    # Work from the latest base so an old workflow run cannot replay stale intent.
    git("switch", "-C", base_branch, f"origin/{base_branch}")

    latest_task = load_json(TASK_PATH)
    if latest_task.get("task_id") != task_id or latest_task.get("status") != "READY":
        raise RuntimeError(
            f"stale dispatch: workflow task={task_id}, latest base task={latest_task.get('task_id')} "
            f"status={latest_task.get('status')}"
        )

    ids = list(completed.get("completed_task_ids", []))
    if task_id not in ids:
        ids.append(task_id)
    completed = {"schema_version": 1, "completed_task_ids": ids}
    save_json(COMPLETED_PATH, completed)
    git("add", "--", ".harness/completed.json")
    git("commit", "-m", f"harness: claim {task_id}")
    git("push", "origin", f"HEAD:{base_branch}")

    if task["delivery_mode"] == "PULL_REQUEST":
        work_branch = f"harness/{safe_branch_component(task_id)}"
        exists = git("ls-remote", "--exit-code", "--heads", "origin", work_branch, check=False, capture=True)
        if exists.returncode == 0:
            raise RuntimeError(f"work branch already exists for claimed task: {work_branch}")
        git("switch", "-c", work_branch)
    else:
        work_branch = base_branch

    return completed, base_branch, work_branch


def render_argv(task: dict) -> list[str]:
    raw = os.environ.get("HARNESS_COMMAND_JSON", "").strip()
    if not raw:
        raise RuntimeError(
            "HARNESS_COMMAND_JSON is not configured. Set it to a JSON argv array on the repository/runner."
        )
    argv = json.loads(raw)
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) for x in argv):
        raise ValueError("HARNESS_COMMAND_JSON must be a non-empty JSON array of strings")
    replacements = {
        "{task_id}": task["task_id"],
        "{inbox}": task["inbox_path"],
        "{repo}": str(ROOT),
    }
    out = []
    for arg in argv:
        for old, new in replacements.items():
            arg = arg.replace(old, new)
        out.append(arg)
    return out


def main() -> int:
    dispatch_task = load_json(TASK_PATH)
    validate_task(dispatch_task)

    if dispatch_task["status"] != "READY":
        print(f"No dispatch: status={dispatch_task['status']}")
        return 0

    if dispatch_task["autonomy"] == "HUMAN_REVIEW_REQUIRED":
        print("No dispatch: HUMAN_REVIEW_REQUIRED")
        return 0

    task_id = dispatch_task["task_id"]
    completed, base_branch, work_branch = prepare_and_claim(dispatch_task)
    if not work_branch:
        print(f"No dispatch: task already consumed: {task_id}")
        return 0

    task = load_json(TASK_PATH)
    validate_task(task)
    if task["task_id"] != task_id:
        raise RuntimeError("task changed after claim")

    original_task_text = TASK_PATH.read_text(encoding="utf-8")
    protected_completed_text = COMPLETED_PATH.read_text(encoding="utf-8")

    argv = render_argv(task)
    timeout_s = int(os.environ.get("HARNESS_TIMEOUT_SECONDS", "3600"))
    if timeout_s <= 0:
        raise ValueError("HARNESS_TIMEOUT_SECONDS must be > 0")

    env = os.environ.copy()
    env.update(
        {
            "HARNESS_TASK_ID": task_id,
            "HARNESS_INBOX_PATH": task["inbox_path"],
            "HARNESS_AUTONOMY": task["autonomy"],
            "HARNESS_DELIVERY_MODE": task["delivery_mode"],
            "HARNESS_BASE_BRANCH": base_branch,
            "HARNESS_WORK_BRANCH": work_branch,
        }
    )

    started = datetime.now(timezone.utc).isoformat()
    exit_code: int | None = None
    error: str | None = None
    try:
        print(f"Dispatching task {task_id} on {work_branch}: {argv!r}")
        proc = subprocess.run(argv, cwd=ROOT, env=env, timeout=timeout_s, check=False)
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        error = f"timeout after {timeout_s}s: {exc}"
    except Exception as exc:
        exit_code = 125
        error = f"worker exception: {type(exc).__name__}: {exc}"
    finally:
        # A Harness is not allowed to self-publish the next task or rewrite the one-shot ledger.
        # record_state.py stages these restored files so final branch diff is also repaired if
        # the Harness had committed a protected-file mutation.
        if TASK_PATH.read_text(encoding="utf-8") != original_task_text:
            TASK_PATH.write_text(original_task_text, encoding="utf-8", newline="\n")
            suffix = "task.json mutation by Harness was reverted"
            error = f"{error}; {suffix}" if error else suffix
        if COMPLETED_PATH.read_text(encoding="utf-8") != protected_completed_text:
            COMPLETED_PATH.write_text(protected_completed_text, encoding="utf-8", newline="\n")
            suffix = "completed.json mutation by Harness was reverted"
            error = f"{error}; {suffix}" if error else suffix

        save_json(
            LAST_RUN_PATH,
            {
                "schema_version": 1,
                "task_id": task_id,
                "autonomy": task["autonomy"],
                "delivery_mode": task["delivery_mode"],
                "base_branch": base_branch,
                "work_branch": work_branch,
                "started_at": started,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "worker_exit_code": exit_code,
                "worker_error": error,
                "note": "Task was claimed before execution. Any retry requires a new task_id.",
            },
        )

    if error:
        print(error, file=sys.stderr)
    return int(exit_code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
