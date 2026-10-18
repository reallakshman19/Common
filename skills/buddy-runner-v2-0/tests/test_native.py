import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml
from support import ROOT, request, reconstruction
from relay_native import preflight
from relay_workflow import PROTOCOL_COMMIT

REPO = ROOT.parents[1]
FIXTURE = REPO / "skills/engineering-pr-delivery-v3.6/tests/fixtures"


class NativeTests(unittest.TestCase):
    def native_inputs(self, directory):
        labels = []
        for path in FIXTURE.rglob("*.yaml"):
            item = yaml.safe_load(path.read_text())
            if isinstance(item, dict) and "guidance" in item and "work" in item:
                labels.append(item)
        self.assertTrue(labels, "real native label fixture required")
        label = labels[0]
        label["mode"] = "standalone"
        label["repository"] = "example/project"
        label["guidance"]["notes"] = [
            n for n in label["guidance"]["notes"] if not n.startswith("Writable lab:")]
        work = label["work"]
        label_path = directory / "relay/AIM" / (work + ".yaml")
        label_path.parent.mkdir(parents=True)
        label_path.write_text(yaml.safe_dump(label, sort_keys=False))
        outcome = next(iter(label["label"]["outcomes"]))
        task = {"task_id": "V36-1-RELAY", "size": "S", "outcome": outcome,
                "title": "Test bounded relay", "acceptance": "Original outputs preserved",
                "for_user": "Continue with complete trace"}
        plan = {"plan_version": "V36-1-PLAN-1", "parent": "example/project#1",
                "label": {k: label[k] for k in ("work", "version", "label_sha")},
                "tasks": [task]}
        plan_path = directory / "plan.yaml"
        plan_path.write_text(yaml.safe_dump(plan, sort_keys=False))
        child = {"number": 2, "body": "<!-- v36-task:V36-1-RELAY parent:example/project#1 -->"}
        return label_path, plan_path, child

    def test_real_pinned_native_validators_accept_binding_without_granting_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            label, plan, child = self.native_inputs(Path(tmp))
            result = preflight(REPO, label, plan, "V36-1-RELAY", child)
        self.assertEqual(result["protocol_commit"], PROTOCOL_COMMIT)
        self.assertTrue(result["binding_valid"])
        self.assertFalse(result["coding_authorized"])
        self.assertIn("tests", result["skill_text"].lower())

    def test_omitted_standalone_mode_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            label, plan, child = self.native_inputs(Path(tmp))
            value = yaml.safe_load(label.read_text())
            del value["mode"]
            label.write_text(yaml.safe_dump(value))
            with self.assertRaises(ValueError):
                preflight(REPO, label, plan, "V36-1-RELAY", child)

    def test_foreign_child_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            label, plan, child = self.native_inputs(Path(tmp))
            child["body"] = "<!-- v36-task:V36-1-OTHER parent:foreign/project#1 -->"
            with self.assertRaises(ValueError):
                preflight(REPO, label, plan, "V36-1-RELAY", child)

    def test_uncommitted_protocol_worktree_is_not_executed(self):
        with tempfile.TemporaryDirectory() as tmp:
            label, plan, child = self.native_inputs(Path(tmp))
            worktree = Path(tmp) / "untrusted-worktree"
            worktree.mkdir()
            (worktree / ".git").write_text("gitdir: " + str(REPO / ".git") + "\n")
            fake = worktree / "skills/engineering-pr-delivery-v3.6/scripts/lifecycle_v36.py"
            fake.parent.mkdir(parents=True)
            fake.write_text("raise RuntimeError('untrusted worktree executed')\n")
            result = preflight(worktree, label, plan, "V36-1-RELAY", child)
        self.assertEqual(result["loaded_from"], "PINNED_GIT_OBJECTS")
        self.assertEqual(result["protocol_commit"], PROTOCOL_COMMIT)


if __name__ == "__main__":
    unittest.main()

