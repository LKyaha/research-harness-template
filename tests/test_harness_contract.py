import json
import unittest
from pathlib import Path

from harness import worker


ROOT = Path(__file__).resolve().parents[1]


class HarnessContractTests(unittest.TestCase):
    def test_template_task_is_valid(self):
        task = json.loads((ROOT / ".harness" / "task.json").read_text(encoding="utf-8"))
        worker.validate_task(task)

    def test_safe_branch_component(self):
        self.assertEqual(worker.safe_branch_component("TASK-001"), "TASK-001")
        self.assertEqual(worker.safe_branch_component("stage 1 / probe"), "stage-1-probe")

    def test_bad_delivery_mode_is_rejected(self):
        task = json.loads((ROOT / ".harness" / "task.json").read_text(encoding="utf-8"))
        task["delivery_mode"] = "MAGIC"
        with self.assertRaises(ValueError):
            worker.validate_task(task)

    def test_pr_delivery_requires_base_branch(self):
        task = json.loads((ROOT / ".harness" / "task.json").read_text(encoding="utf-8"))
        task["delivery_mode"] = "PULL_REQUEST"
        task["base_branch"] = ""
        with self.assertRaises(ValueError):
            worker.validate_task(task)

    def test_completed_ids(self):
        self.assertEqual(worker.completed_ids({"completed_task_ids": ["A", "B"]}), {"A", "B"})


if __name__ == "__main__":
    unittest.main()
