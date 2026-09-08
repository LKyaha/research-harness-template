#!/usr/bin/env python3
"""Event-driven local Harness dispatcher.

The worker consumes exactly one machine-readable task from `.harness/task.json`.
It never invents the next research task.

Key guarantees:
- one task ID is claimed on the base branch before local execution;
- a claimed task is never automatically executed again;
- task.json + HARNESS_INBOX content are bound to the dispatch commit;
- task-controlled file paths stay inside the repository;
- PULL_REQUEST delivery runs on `harness/<task_id>` instead of the base branch;
- protected trigger/consumption files cannot survive Harness mutation in the final diff;
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
ROOT_RESOLVED = ROOT.resolve()
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


def resolve_repo_path(value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("repository path must be a non-empty string")
    rel = Path(value)
    if rel.is_absolute():
        raise ValueError(f"repository path must be relative: {value!r}")
    resolved = (ROOT / rel).resolve()
    try:
        resolved.relative_to(ROOT_RESOLVED)
    except ValueError as exc:
        raise ValueError(f"repository path escapes project root: {value!r}") from exc
    return resolved


def validate_branch_name(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("base_branch must be a non-empty string")
    name = value.strip()
    # Deliberately narrower than all Git-valid refs: predictable ASCII branch names are safer
    # in an automation template and avoid option/ref ambiguity across platforms.
    if len(name) > 200 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", name):
        raise ValueError(f"unsafe/unsupported base_branch: {value!r}")
    if ".." in name or "@{" in name or "//" in name:
        raise ValueError(f"unsafe/unsupported base_branch: {value!r}")
    if name.endswith(("/", ".", ".lock")) or any(part in {"", ".", ".."} for part in name.split("/")):
        raise ValueError(f"unsafe/unsupported base_branch: {value!r}")
    return name


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
    inbox = resolve_repo_path(task["inbox_path"])
    if not inbox.is_file():
        raise ValueError(f"inbox_path does not exist or is not a file: {task['inbox_path']}")
    if task["delivery_mode"] == "PULL_REQUEST":
        validate_branch_name(task.get("base_branch"))
    elif task.get("base_branch") is not None:
        validate_branch_name(task["base_branch"])


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


def prepare_and_claim(task: dict, dispatch_inbox_text: str) -> tuple[dict, str, str]:
    """Fast-forward to base, verify intent is unchanged, claim task, choose work branch."""
    task_id = task["task_id"]
    base_branch = validate_branch_name(str(task.get("base_branch") or os.environ.get("GITHUB_REF_NAME") or "main"))
    work_branch = (
        f"harness/{safe_branch_component(task_id)}"
        if task["delivery_mode"] == "PULL_REQUEST"
        else base_branch
    )

    git("config", "user.name", "research-harness[bot]")
    git("config", "user.email", "research-harness[bot]@users.noreply.github.com")
    git("fetch", "origin", f"+refs/heads/{base_branch}:refs/remotes/origin/{base_branch}")

    completed = remote_completed(base_branch)
    if task_id in completed_ids(completed):
        return completed, base_branch, ""

    if task["delivery_mode"] == "PULL_REQUEST":
        exists = git("ls-remote", "--exit-code", "--heads", "origin", work_branch, check=False, capture=True)
        if exists.returncode == 0:
            raise RuntimeError(
                f"work branch already exists for unconsumed task: {work_branch}; "
                "resolve the collision or publish a new task ID before claiming execution"
            )

    # Move to latest base. A workflow re-run may have an old GITHUB_SHA, but it must
    # never replay stale intent against newer repository state.
    git("switch", "-C", base_branch, f"origin/{base_branch}")

    latest_task = load_json(TASK_PATH)
    latest_inbox_path = resolve_repo_path(latest_task.get("inbox_path", "HARNESS_INBOX.md"))
    latest_inbox_text = latest_inbox_path.read_text(encoding="utf-8")
    if latest_task != task or latest_inbox_text != dispatch_inbox_text:
        raise RuntimeError(
            "stale dispatch: task.json or inbox content changed after the triggering commit; "
            "publish a new task ID intentionally instead of reusing old workflow intent"
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
        git("switch", "-c", work_branch)

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

    # Infrastructure/config preflight happens before the one-shot claim. A missing local
    # command or invalid timeout is not a scientific execution attempt and should be fixable
    # without burning the task ID.
    argv = render_argv(dispatch_task)
    timeout_s = int(os.environ.get("HARNESS_TIMEOUT_SECONDS", "3600"))
    if timeout_s <= 0:
        raise ValueError("HARNESS_TIMEOUT_SECONDS must be > 0")

    dispatch_inbox_path = resolve_repo_path(dispatch_task["inbox_path"])
    dispatch_inbox_text = dispatch_inbox_path.read_text(encoding="utf-8")
    task_id = dispatch_task["task_id"]
    completed, base_branch, work_branch = prepare_and_claim(dispatch_task, dispatch_inbox_text)
    if not work_branch:
        print(f"No dispatch: task already consumed: {task_id}")
        return 0

    task = load_json(TASK_PATH)
    validate_task(task)
    original_task_text = TASK_PATH.read_text(encoding="utf-8")
    protected_completed_text = COMPLETED_PATH.read_text(encoding="utf-8")

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
                "note": "Task was claimed before execution. Any execution retry requires a new task_id.",
            },
        )

    if error:
        print(error, file=sys.stderr)
    return int(exit_code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
