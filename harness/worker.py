#!/usr/bin/env python3
"""Event-driven local Harness dispatcher.

The worker intentionally does not decide research tasks. It consumes exactly one
machine-readable task published in .harness/task.json and invokes a local Harness
command supplied by the operator through HARNESS_COMMAND_JSON.

HARNESS_COMMAND_JSON example:
  ["opencode", "run", "Read AGENTS.md and HARNESS_INBOX.md and execute task {task_id}."]

The same task_id is never executed twice. Repairs require a new task_id.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_PATH = ROOT / ".harness" / "task.json"
COMPLETED_PATH = ROOT / ".harness" / "completed.json"
LAST_RUN_PATH = ROOT / ".harness" / "last_worker_run.json"

ALLOWED_AUTONOMY = {"AUTO_CONTINUE", "AUTO_REPAIR", "HUMAN_REVIEW_REQUIRED"}


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


def validate_task(task: dict) -> None:
    required = ["schema_version", "task_id", "status", "autonomy", "inbox_path"]
    missing = [k for k in required if k not in task]
    if missing:
        raise ValueError(f"task.json missing fields: {missing}")
    if not isinstance(task["task_id"], str) or not task["task_id"].strip():
        raise ValueError("task_id must be a non-empty string")
    if task["status"] not in {"IDLE", "READY"}:
        raise ValueError("status must be IDLE or READY")
    if task["autonomy"] not in ALLOWED_AUTONOMY:
        raise ValueError(f"unknown autonomy decision: {task['autonomy']}")
    inbox = ROOT / task["inbox_path"]
    if not inbox.exists():
        raise ValueError(f"inbox_path does not exist: {task['inbox_path']}")


def completed_ids(data: dict) -> set[str]:
    return set(data.get("completed_task_ids", []))


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
    original_task_text = TASK_PATH.read_text(encoding="utf-8")
    task = json.loads(original_task_text)
    validate_task(task)

    if task["status"] != "READY":
        print(f"No dispatch: status={task['status']}")
        return 0

    if task["autonomy"] == "HUMAN_REVIEW_REQUIRED":
        print("No dispatch: HUMAN_REVIEW_REQUIRED")
        return 0

    completed = load_json(COMPLETED_PATH) if COMPLETED_PATH.exists() else {"schema_version": 1, "completed_task_ids": []}
    done = completed_ids(completed)
    task_id = task["task_id"]
    if task_id in done:
        print(f"No dispatch: task already consumed: {task_id}")
        return 0

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
        }
    )

    started = datetime.now(timezone.utc).isoformat()
    exit_code = None
    error = None
    try:
        print(f"Dispatching task {task_id}: {argv!r}")
        proc = subprocess.run(argv, cwd=ROOT, env=env, timeout=timeout_s, check=False)
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        exit_code = 124
        error = f"timeout after {timeout_s}s: {exc}"
    except Exception as exc:  # preserve attempt as consumed; repair requires new ID
        exit_code = 125
        error = f"worker exception: {type(exc).__name__}: {exc}"
    finally:
        # A Harness is not allowed to self-publish the next task or mutate its trigger.
        if TASK_PATH.read_text(encoding="utf-8") != original_task_text:
            TASK_PATH.write_text(original_task_text, encoding="utf-8", newline="\n")
            suffix = "task.json mutation by Harness was reverted"
            error = f"{error}; {suffix}" if error else suffix

        ids = list(completed.get("completed_task_ids", []))
        if task_id not in ids:
            ids.append(task_id)
        completed["schema_version"] = 1
        completed["completed_task_ids"] = ids
        save_json(COMPLETED_PATH, completed)

        save_json(
            LAST_RUN_PATH,
            {
                "schema_version": 1,
                "task_id": task_id,
                "autonomy": task["autonomy"],
                "started_at": started,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "worker_exit_code": exit_code,
                "worker_error": error,
                "note": "Execution attempt is consumed. Any retry requires a new task_id.",
            },
        )

    if error:
        print(error, file=sys.stderr)
    return int(exit_code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
