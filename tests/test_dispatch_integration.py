import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from harness import worker


def git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=check,
    )


@contextmanager
def worker_root(repo: Path):
    old = (
        worker.ROOT,
        worker.ROOT_RESOLVED,
        worker.TASK_PATH,
        worker.COMPLETED_PATH,
        worker.LAST_RUN_PATH,
    )
    worker.ROOT = repo
    worker.ROOT_RESOLVED = repo.resolve()
    worker.TASK_PATH = repo / ".harness" / "task.json"
    worker.COMPLETED_PATH = repo / ".harness" / "completed.json"
    worker.LAST_RUN_PATH = repo / ".harness" / "last_worker_run.json"
    try:
        yield
    finally:
        (
            worker.ROOT,
            worker.ROOT_RESOLVED,
            worker.TASK_PATH,
            worker.COMPLETED_PATH,
            worker.LAST_RUN_PATH,
        ) = old


class DispatchIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.remote = root / "remote.git"
        self.repo = root / "repo"

        git(root, "init", "--bare", str(self.remote))
        self.repo.mkdir()
        git(self.repo, "init")
        git(self.repo, "config", "user.name", "test")
        git(self.repo, "config", "user.email", "test@example.invalid")

        (self.repo / ".harness").mkdir()
        self.task = {
            "schema_version": 1,
            "task_id": "TASK-001",
            "status": "READY",
            "autonomy": "AUTO_CONTINUE",
            "delivery_mode": "PULL_REQUEST",
            "base_branch": "main",
            "depends_on": None,
            "issued_at": "2026-01-01T00:00:00Z",
            "failure_budget": 0,
            "inbox_path": "HARNESS_INBOX.md",
            "notes": "integration test",
        }
        self.inbox_text = (
            "**Task ID:** TASK-001\n"
            "**Autonomy decision:** AUTO_CONTINUE\n"
            "**Delivery mode:** PULL_REQUEST\n"
        )
        (self.repo / ".harness" / "task.json").write_text(
            json.dumps(self.task, indent=2) + "\n", encoding="utf-8"
        )
        (self.repo / ".harness" / "completed.json").write_text(
            json.dumps({"schema_version": 1, "completed_task_ids": []}, indent=2) + "\n",
            encoding="utf-8",
        )
        (self.repo / "HARNESS_INBOX.md").write_text(self.inbox_text, encoding="utf-8")

        git(self.repo, "add", ".")
        git(self.repo, "commit", "-m", "publish task")
        git(self.repo, "branch", "-M", "main")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        git(self.repo, "push", "-u", "origin", "main")
        self.dispatch_sha = git(self.repo, "rev-parse", "HEAD").stdout.strip()

    def tearDown(self):
        self.tmp.cleanup()

    def remote_completed_ids(self):
        raw = git(self.remote, "show", "main:.harness/completed.json").stdout
        return set(json.loads(raw)["completed_task_ids"])

    def test_claim_is_persisted_before_pr_branch_and_rerun_is_noop(self):
        old_sha = os.environ.get("GITHUB_SHA")
        os.environ["GITHUB_SHA"] = self.dispatch_sha
        try:
            with worker_root(self.repo):
                worker.validate_task(self.task)
                _, base, work_branch, base_sha = worker.prepare_and_claim(self.task, self.inbox_text)
                self.assertEqual(base, "main")
                self.assertEqual(base_sha, self.dispatch_sha)
                self.assertEqual(work_branch, "harness/TASK-001")
                self.assertEqual(git(self.repo, "branch", "--show-current").stdout.strip(), work_branch)
                self.assertIn("TASK-001", self.remote_completed_ids())

                # Simulate manually re-running the original workflow SHA after the claim commit.
                git(self.repo, "switch", "--detach", self.dispatch_sha)
                _, base2, work_branch2, base_sha2 = worker.prepare_and_claim(self.task, self.inbox_text)
                self.assertEqual(base2, "main")
                self.assertEqual(work_branch2, "")
                self.assertEqual(base_sha2, "")
        finally:
            if old_sha is None:
                os.environ.pop("GITHUB_SHA", None)
            else:
                os.environ["GITHUB_SHA"] = old_sha

    def test_base_move_makes_old_dispatch_stale(self):
        # Advance main without consuming TASK-001.
        (self.repo / "unrelated.txt").write_text("new state\n", encoding="utf-8")
        git(self.repo, "add", "unrelated.txt")
        git(self.repo, "commit", "-m", "advance base")
        git(self.repo, "push", "origin", "main")
        git(self.repo, "switch", "--detach", self.dispatch_sha)

        old_sha = os.environ.get("GITHUB_SHA")
        os.environ["GITHUB_SHA"] = self.dispatch_sha
        try:
            with worker_root(self.repo):
                with self.assertRaisesRegex(RuntimeError, "base branch moved"):
                    worker.prepare_and_claim(self.task, self.inbox_text)
                self.assertNotIn("TASK-001", self.remote_completed_ids())
        finally:
            if old_sha is None:
                os.environ.pop("GITHUB_SHA", None)
            else:
                os.environ["GITHUB_SHA"] = old_sha


if __name__ == "__main__":
    unittest.main()
