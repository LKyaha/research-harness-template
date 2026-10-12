import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from harness import preflight, worker


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / ".harness").mkdir()
        self.inbox = self.root / "HARNESS_INBOX.md"
        self.task = {
            "schema_version": 1,
            "task_id": "TASK-001",
            "status": "READY",
            "autonomy": "AUTO_CONTINUE",
            "delivery_mode": "PULL_REQUEST",
            "base_branch": "main",
            "issued_at": "2026-10-12T00:00:00Z",
            "inbox_path": "HARNESS_INBOX.md",
        }
        self.inbox.write_text(
            "**Task ID:** TASK-001\n"
            "**Autonomy decision:** AUTO_CONTINUE\n"
            "**Delivery mode:** PULL_REQUEST\n",
            encoding="utf-8",
        )
        patches = [
            patch.object(worker, "ROOT", self.root),
            patch.object(worker, "ROOT_RESOLVED", self.root.resolve()),
            patch.object(worker, "TASK_PATH", self.root / ".harness" / "task.json"),
        ]
        for item in patches:
            item.start()
            self.addCleanup(item.stop)

    def test_idle_skips_without_inbox_header_matching(self):
        self.task["status"] = "IDLE"
        self.inbox.write_text("Not an executable inbox\n", encoding="utf-8")
        self.assertEqual(preflight.readiness(self.task), (False, "status=IDLE"))

    def test_human_review_required_skips(self):
        self.task["autonomy"] = "HUMAN_REVIEW_REQUIRED"
        self.assertEqual(preflight.readiness(self.task), (False, "HUMAN_REVIEW_REQUIRED"))

    def test_ready_matching_task_dispatches(self):
        self.assertEqual(preflight.readiness(self.task), (True, "READY task TASK-001"))

    def test_ready_requires_issued_at(self):
        self.task["issued_at"] = None
        with self.assertRaisesRegex(ValueError, "requires issued_at"):
            preflight.readiness(self.task)

    def test_ready_inbox_mismatch_fails_closed(self):
        self.inbox.write_text("**Task ID:** TASK-OTHER\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "header mismatch"):
            preflight.readiness(self.task)

    def test_bad_task_fails_closed(self):
        self.task["delivery_mode"] = "UNRECOGNIZED"
        with self.assertRaises(ValueError):
            preflight.readiness(self.task)

    def test_main_writes_github_output_for_idle_and_ready(self):
        output = self.root / "github_output"
        for status, expected in [("IDLE", "false"), ("READY", "true")]:
            self.task["status"] = status
            (self.root / ".harness" / "task.json").write_text(
                json.dumps(self.task), encoding="utf-8"
            )
            output.write_text("", encoding="utf-8")
            with patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                self.assertEqual(preflight.main(), 0)
            self.assertEqual(output.read_text(encoding="utf-8"), f"ready={expected}\n")


if __name__ == "__main__":
    unittest.main()
