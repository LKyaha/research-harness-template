#!/usr/bin/env python3
"""Validate the durable research-state contract using only the Python stdlib."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "CONTEXT_LEDGER.md",
    "RESEARCH_TASK.md",
    "HYPOTHESES.md",
    "DECISIONS.md",
    "UNRESOLVED.md",
    "FAILURES.md",
    "HARNESS_INBOX.md",
    "HARNESS_OUTBOX.md",
    "AUTONOMY_POLICY.md",
    ".harness/task.json",
    "provenance/sources.json",
    "provenance/artifacts.json",
]

ALLOWED_TASK_STATUS = {"IDLE", "READY"}
ALLOWED_AUTONOMY = {"AUTO_CONTINUE", "AUTO_REPAIR", "HUMAN_REVIEW_REQUIRED"}
ALLOWED_DELIVERY = {"DIRECT", "PULL_REQUEST"}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def load_json(path: str, v: Validation) -> dict:
    p = ROOT / path
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        v.error(f"{path}: invalid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        v.error(f"{path}: top level must be an object")
        return {}
    return data


def validate_required_files(v: Validation) -> None:
    for rel in REQUIRED_FILES:
        if not (ROOT / rel).exists():
            v.error(f"missing required file: {rel}")


def validate_task(v: Validation) -> None:
    task = load_json(".harness/task.json", v)
    if not task:
        return

    required = [
        "schema_version",
        "task_id",
        "status",
        "autonomy",
        "delivery_mode",
        "inbox_path",
    ]
    for key in required:
        if key not in task:
            v.error(f".harness/task.json: missing {key}")

    if task.get("schema_version") != 1:
        v.error(".harness/task.json: schema_version must be 1")
    if task.get("status") not in ALLOWED_TASK_STATUS:
        v.error(f".harness/task.json: invalid status {task.get('status')!r}")
    if task.get("autonomy") not in ALLOWED_AUTONOMY:
        v.error(f".harness/task.json: invalid autonomy {task.get('autonomy')!r}")
    if task.get("delivery_mode") not in ALLOWED_DELIVERY:
        v.error(f".harness/task.json: invalid delivery_mode {task.get('delivery_mode')!r}")

    task_id = task.get("task_id")
    if not isinstance(task_id, str) or not task_id.strip():
        v.error(".harness/task.json: task_id must be a non-empty string")

    inbox_path = task.get("inbox_path")
    if not isinstance(inbox_path, str) or not (ROOT / inbox_path).exists():
        v.error(f".harness/task.json: inbox_path does not exist: {inbox_path!r}")

    if task.get("delivery_mode") == "PULL_REQUEST":
        base = task.get("base_branch")
        if not isinstance(base, str) or not base.strip():
            v.error(".harness/task.json: PULL_REQUEST delivery requires base_branch")

    if task.get("status") == "READY":
        if not task.get("issued_at"):
            v.error(".harness/task.json: READY task requires issued_at")
        if task.get("autonomy") == "HUMAN_REVIEW_REQUIRED":
            v.warn("READY + HUMAN_REVIEW_REQUIRED will intentionally not dispatch")
        try:
            inbox = (ROOT / str(inbox_path)).read_text(encoding="utf-8")
            if str(task_id) not in inbox:
                v.error("READY task_id is not present in HARNESS_INBOX/inbox_path")
        except Exception:
            pass


def validate_registry(path: str, collection: str, id_key: str, required_keys: list[str], v: Validation) -> None:
    data = load_json(path, v)
    if not data:
        return
    if data.get("schema_version") != 1:
        v.error(f"{path}: schema_version must be 1")
    items = data.get(collection)
    if not isinstance(items, list):
        v.error(f"{path}: {collection} must be an array")
        return

    seen: set[str] = set()
    for i, item in enumerate(items):
        loc = f"{path}:{collection}[{i}]"
        if not isinstance(item, dict):
            v.error(f"{loc}: entry must be an object")
            continue
        for key in required_keys:
            if key not in item:
                v.error(f"{loc}: missing {key}")
        ident = item.get(id_key)
        if not isinstance(ident, str) or not ident.strip():
            v.error(f"{loc}: {id_key} must be a non-empty string")
        elif ident in seen:
            v.error(f"{loc}: duplicate {id_key} {ident!r}")
        else:
            seen.add(ident)


def validate_outbox_contract(v: Validation) -> None:
    text = (ROOT / "HARNESS_OUTBOX.md").read_text(encoding="utf-8")
    required_sections = [
        "## Gate result",
        "## Environment",
        "## Commands",
        "## Evidence / artifacts",
        "## Interpretation confidence",
    ]
    for section in required_sections:
        if section not in text:
            v.warn(f"HARNESS_OUTBOX.md missing recommended section: {section}")


def main() -> int:
    v = Validation()
    validate_required_files(v)
    validate_task(v)
    validate_registry(
        "provenance/sources.json",
        "sources",
        "source_id",
        ["source_id", "kind", "name", "uri", "revision"],
        v,
    )
    validate_registry(
        "provenance/artifacts.json",
        "artifacts",
        "artifact_id",
        ["artifact_id", "task_id", "kind", "description", "location"],
        v,
    )
    if (ROOT / "HARNESS_OUTBOX.md").exists():
        validate_outbox_contract(v)

    for msg in v.warnings:
        print(f"WARNING: {msg}")
    for msg in v.errors:
        print(f"ERROR: {msg}", file=sys.stderr)

    if v.errors:
        print(f"Research-state validation FAILED: {len(v.errors)} error(s), {len(v.warnings)} warning(s)")
        return 1

    print(f"Research-state validation PASS: {len(v.warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
