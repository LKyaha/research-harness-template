import json
import unittest
from pathlib import Path

from harness import validate_repository
from harness import worker


ROOT = Path(__file__).resolve().parents[1]


class HarnessContractTests(unittest.TestCase):
    def template_task(self):
        return json.loads((ROOT / ".harness" / "task.json").read_text(encoding="utf-8"))

    def test_template_task_is_valid(self):
        worker.validate_task(self.template_task())

    def test_safe_branch_component(self):
        self.assertEqual(worker.safe_branch_component("TASK-001"), "TASK-001")
        self.assertEqual(worker.safe_branch_component("stage 1 / probe"), "stage-1-probe")

    def test_base_branch_validation(self):
        self.assertEqual(worker.validate_branch_name("main"), "main")
        self.assertEqual(worker.validate_branch_name("research/exp-1"), "research/exp-1")
        for bad in ["-main", "main..bad", "main//bad", "main lock", "main.lock"]:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    worker.validate_branch_name(bad)

    def test_bad_delivery_mode_is_rejected(self):
        task = self.template_task()
        task["delivery_mode"] = "MAGIC"
        with self.assertRaises(ValueError):
            worker.validate_task(task)

    def test_pr_delivery_requires_base_branch(self):
        task = self.template_task()
        task["delivery_mode"] = "PULL_REQUEST"
        task["base_branch"] = ""
        with self.assertRaises(ValueError):
            worker.validate_task(task)

    def test_inbox_path_cannot_escape_repository(self):
        task = self.template_task()
        task["inbox_path"] = "../HARNESS_INBOX.md"
        with self.assertRaises(ValueError):
            worker.validate_task(task)

    def test_completed_ids(self):
        self.assertEqual(worker.completed_ids({"completed_task_ids": ["A", "B"]}), {"A", "B"})

    def test_markdown_header_parser(self):
        text = (
            "**Task ID:** TASK-007  \n"
            "**Autonomy decision:** AUTO_CONTINUE  \n"
            "**Delivery mode:** `PULL_REQUEST`\n"
        )
        self.assertEqual(validate_repository.markdown_header(text, "Task ID"), "TASK-007")
        self.assertEqual(validate_repository.markdown_header(text, "Autonomy decision"), "AUTO_CONTINUE")
        self.assertEqual(validate_repository.markdown_header(text, "Delivery mode"), "PULL_REQUEST")


if __name__ == "__main__":
    unittest.main()
