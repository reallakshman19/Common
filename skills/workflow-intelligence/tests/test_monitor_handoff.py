"""PR #364 snapshot -> bounded portable state handoff; no new scheduler."""
import copy
import importlib.util
import json
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("uwi_handoff",
                                               ROOT / "scripts" / "monitor_handoff.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
FIXTURE = ROOT / "examples" / "monitor-snapshot.json"
SNAPSHOT = json.loads(FIXTURE.read_text(encoding="utf-8"))
ONE = "1" * 64


class MonitorHandoff(unittest.TestCase):
    def test_explicit_bootstrap_silent(self):
        b = mod.reconcile(SNAPSHOT, bootstrap=True)
        self.assertEqual(b["events"], [])
        self.assertEqual(b["mode"], "DIAGNOSTIC_ONLY")
        self.assertIsNone(b["previous_state_digest"])

    def test_no_implicit_reset(self):
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT)

    def test_prior_and_bootstrap_conflict(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT, previous_bundle=prior, bootstrap=True)

    def test_repeat_poll_changed_timestamp_silent(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        now = copy.deepcopy(SNAPSHOT)
        now["observed_at"] = "2030-01-01T00:00:00Z"
        nxt = mod.reconcile(now, previous_bundle=prior)
        self.assertEqual(nxt["events"], [])
        self.assertEqual(nxt["source_digest"], prior["source_digest"])
        self.assertEqual(nxt["state_digest"], prior["state_digest"])

    def test_comment_evidence_change_diagnostic_only(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        now = copy.deepcopy(SNAPSHOT)
        now["workflows"][0]["stages"][0]["evidence"].append(
            {"comment_id": 29, "sha256": ONE})
        next_bundle = mod.reconcile(now, previous_bundle=prior)
        self.assertEqual(len(next_bundle["events"]), 1)
        event = next_bundle["events"][0]
        self.assertFalse(event["alert_eligible"])
        self.assertFalse(event["mcda_eligible"])
        self.assertEqual(event["observation"]["verification"], "UNVERIFIED")
        self.assertEqual(mod.reconcile(now, previous_bundle=prior)["events"],
                         next_bundle["events"])
        self.assertEqual(mod.reconcile(now, previous_bundle=next_bundle)["events"], [])

    def test_corrupted_state_digest_fail_closed(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        prior["state_digest"] = "sha256:" + ONE
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT, previous_bundle=prior)

    def test_corrupt_internal_state_fail_closed(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        prior["state"]["entries"] = {"bad": "bad"}
        prior["state_digest"] = "sha256:" + mod.fingerprint(prior["state"])
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT, previous_bundle=prior)

    def test_prior_cannot_contain_actionable_event(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        prior["events"].append({"event_id": "fake", "alert_eligible": True,
                                "mcda_eligible": False})
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT, previous_bundle=prior)

    def test_unknown_version_not_migrated(self):
        prior = mod.reconcile(SNAPSHOT, bootstrap=True)
        prior["schema"] = "workflow-intelligence.handoff/v2"
        with self.assertRaises(ValueError):
            mod.reconcile(SNAPSHOT, previous_bundle=prior)

    def test_forged_monitor_verified_fails(self):
        current = copy.deepcopy(SNAPSHOT)
        current["workflows"][0]["stages"][0]["verification"] = "VERIFIED"
        with self.assertRaises(ValueError):
            mod.reconcile(current, bootstrap=True)

    def test_missing_snapshot_schema_fails(self):
        now = copy.deepcopy(SNAPSHOT)
        now.pop("schema")
        with self.assertRaises(ValueError):
            mod.reconcile(now, bootstrap=True)

    def test_empty_workflows_allowed_baseline(self):
        now = {"schema": mod.MONITOR_SCHEMA, "workflows": []}
        prior = mod.reconcile(now, bootstrap=True)
        self.assertEqual(prior["events"], [])
        self.assertEqual(prior["state"]["entries"], {})

    def test_preserve_advisory_decision_without_alert(self):
        assessed = {"schema": "workflow-intelligence.assessment/v1",
                    "scope": {"repository": "owner/repo", "workflow_id": "sample-buddy",
                              "issue": 17, "decision_id": "arch",
                              "assessed_sha": "a" * 40},
                    "notification_eligible": False,
                    "authority": "SELF_DECLARED_INPUTS_NOT_INDEPENDENTLY_VERIFIED",
                    "status": "NOT_EVALUATED", "reason": "sample disabled"}
        prior = mod.reconcile(SNAPSHOT, bootstrap=True, assessment=assessed)
        self.assertEqual(len(prior["state"]["decisions"]), 1)
        self.assertEqual(prior["events"], [])
        repeat = mod.reconcile(SNAPSHOT, previous_bundle=prior, assessment=assessed)
        self.assertEqual(repeat["events"], [])

    def test_cli_explicit_bootstrap_then_repeat(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first, second = root / "first.json", root / "second.json"
            cli = ROOT / "scripts" / "monitor_handoff.py"
            cmd = [sys.executable, str(cli), "--monitor-current", str(FIXTURE)]
            first_run = subprocess.run(cmd + ["--bootstrap", "--output-artifact", str(first)],
                                       capture_output=True, text=True)
            self.assertEqual(first_run.returncode, 0, first_run.stderr)
            second_run = subprocess.run(cmd + ["--previous-artifact", str(first),
                                                "--output-artifact", str(second)],
                                        capture_output=True, text=True)
            self.assertEqual(second_run.returncode, 0, second_run.stderr)
            a, b = json.loads(first.read_text()), json.loads(second.read_text())
            self.assertEqual(a["events"], [])
            self.assertEqual(b["events"], [])
            self.assertEqual(a["state_digest"], b["state_digest"])

    def test_cli_missing_prior_fails_without_rebaselining(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            output = root / "output.json"
            cmd = [sys.executable, str(ROOT / "scripts" / "monitor_handoff.py"),
                   "--monitor-current", str(FIXTURE),
                   "--previous-artifact", str(root / "nonexistent.json"),
                   "--output-artifact", str(output)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("HANDOFF_FAILED", r.stderr)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
