"""WP1 contract tests; offline, no GitHub credentials or old skill imports."""
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("lifecycle_v36", ROOT / "scripts" / "lifecycle_v36.py")
v36 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v36)

LABEL = {
    "work": "V35-LIFECYCLE",
    "repository": "reallakshman19/Common",
    "engineering_critical": "standard",
    "version": "1.1.0",
    "label_sha": "775f2bc",
    "label": {
        "problem": "You cannot see from GitHub what agents did or how far a work has got; each successor starts half-blind.",
        "main_aim": "From one parent issue, GitHub alone shows the plan, evidence and live progress; any successor continues without chats.",
        "outcomes": {f"O{i}": f"Outcome {i}" for i in range(1, 6)},
        "owner_constraints": ["A new, independent v3.6 lifecycle skill", "BuddyRunner v1.6 and revamped 2-pass / 3-pass prompts inside v3.6"],
        "task_outcome": "O1-O5",
        "task_aim": "Build v3.6; one real parent issue on the lab runs end to end, titles updating themselves as evidence lands.",
        "done_when": "With v3.6 only, on relay-v35-e2e-lab: parent and child issues with evidence, automatic titles, and a handover a successor continues from.",
    },
    "guidance": {"not_now": [], "watch": ["Reports about the lifecycle instead of running it"], "notes": []},
    "bindings": ["Session_Oct07:2 coordination/Session_Oct07/Tab2_Lifecycle_Evidence_Reconciliation"],
    "history": ["v1.1.0 · 2026-10-12 · approved by the Owner"],
}
EVIDENCE = dict(
    outcome="O1", for_user="A usable child task now exists",
    proof="https://github.com/reallakshman19/Common/pull/1",
    task_id="V36-341-WP1", issue_ref="reallakshman19/Common#342",
    candidate="reallakshman19/Common@abcdef0123456789",
    tests_passed=8, tests_run=8,
)


class LabelTests(unittest.TestCase):
    def test_label_reads_approved_master_shape(self):
        item = v36.validate_label(LABEL, "V35-LIFECYCLE")
        self.assertEqual(item["version"], "1.1.0")

    def test_bad_aim_id(self):
        with self.assertRaises(v36.ContractError):
            v36.validate_label(LABEL, "OTHER-LABEL")

    def test_missing_outcome(self):
        changed = {**LABEL, "label": {**LABEL["label"], "outcomes": {"O1": "Only one"}}}
        with self.assertRaises(v36.ContractError):
            v36.validate_label(changed)

    def test_unknown_extra_field_is_rejected(self):
        with self.assertRaises(v36.ContractError):
            v36.validate_label({**LABEL, "writer": "ON"})

    def test_bad_repository_ref(self):
        with self.assertRaises(v36.ContractError):
            v36.validate_label({**LABEL, "repository": "random URL"})

    def test_master_key_mismatch_fails(self):
        with self.assertRaises(v36.ContractError):
            v36.validate_label({**LABEL, "label_sha": "unknown"})

    def test_owner_master_example_is_accepted(self):
        master = ROOT / "tests" / "fixtures" / "V35-LIFECYCLE.yaml"
        self.assertEqual(v36.load_label(master)["label_sha"], "775f2bc")

    def test_no_ambiguous_yaml_duplicate_keys(self):
        source = "label_id: A\nlabel_id: B\n"
        with self.assertRaises(v36.ContractError):
            import yaml
            yaml.load(source, Loader=v36.UniqueKeyLoader)

    def test_label_path_must_be_relay_aim(self):
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "wrong" / "V35-LIFECYCLE.yaml"
            path.parent.mkdir()
            path.write_text("label_id: V35-LIFECYCLE")
            with self.assertRaises(v36.ContractError):
                v36.load_label(path)

    def test_valid_yaml_file(self):
        import yaml
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "relay" / "AIM" / "V35-LIFECYCLE.yaml"
            path.parent.mkdir(parents=True)
            path.write_text(yaml.safe_dump(LABEL, sort_keys=False))
            self.assertEqual(v36.load_label(path)["label_sha"], LABEL["label_sha"])


class EvidenceTests(unittest.TestCase):
    def test_first_three_lines_and_round_trip(self):
        content = v36.render_evidence(**EVIDENCE)
        self.assertEqual(content.splitlines()[:3], [
            "Outcome: O1",
            "For the user: A usable child task now exists",
            "Proof: https://github.com/reallakshman19/Common/pull/1",
        ])
        self.assertEqual(v36.validate_evidence(content)["task_id"], "V36-341-WP1")

    def test_reject_placeholder_proof(self):
        with self.assertRaises(v36.ContractError):
            v36.render_evidence(**{**EVIDENCE, "proof": "https://example.com/TODO"})

    def test_reject_incorrect_outcome(self):
        with self.assertRaises(v36.ContractError):
            v36.render_evidence(**{**EVIDENCE, "outcome": "O6"})

    def test_reject_unverified_task(self):
        with self.assertRaises(v36.ContractError):
            v36.render_evidence(**{**EVIDENCE, "tests_passed": 0, "tests_run": 0})

    def test_reject_extra_comment_claim(self):
        content = v36.render_evidence(**EVIDENCE) + "Status: PRODUCTION\n"
        with self.assertRaises(v36.ContractError):
            v36.validate_evidence(content)

    def test_cli_rejects_missing_label(self):
        run = subprocess.run([sys.executable, str(ROOT / "scripts" / "lifecycle_v36.py"),
                              "validate-label", "/tmp/relay/AIM/ABSENT.yaml"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("contract error", run.stderr)


if __name__ == "__main__":
    unittest.main()
