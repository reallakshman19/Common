"""Invocation scope ON/OFF; no network on OFF, no scheduler mutations."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "invoke.py"
spec = importlib.util.spec_from_file_location("invoke", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
EXAMPLE = json.loads((ROOT.parent / "software-mcda" / "assets" / "example-decision.json").read_text())
MONITOR = {"schema": "workflow-progress-monitor/v1",
           "workflows": [{"id": "project-42", "enabled": True, "repository": "owner/project",
                          "issue": 42, "stages": [
                              {"id": "design", "title": "Design review",
                               "evidence_markers": ["REVIEW_SUBMITTED"],
                               "trusted_authors": ["reviewer"]}]}]}
COMMENT = {"id": 123, "user": {"login": "reviewer"}, "body": "REVIEW_SUBMITTED",
           "html_url": "https://github.com/owner/project/issues/42#issuecomment-123"}


class InvocationToggleTests(unittest.TestCase):
    def test_off_default_no_network(self):
        def forbidden(*_):
            raise AssertionError("Network access attempted while OFF")
        result = mod.run_invocation(read_comments=forbidden)
        self.assertEqual(result["monitoring"]["mode"], "off")
        self.assertEqual(result["monitoring"]["status"], "SKIPPED")

    def test_off_ignores_untrusted_workflow_config_without_read(self):
        r = mod.run_invocation("off", workflow_config={"malformed": True},
                               workflow_id="project-42",
                               read_comments=lambda *_: self.fail("Network access"))
        self.assertEqual(r["monitoring"]["status"], "SKIPPED")

    def test_off_preserves_standalone_mcda(self):
        r = mod.run_invocation("off", decision=EXAMPLE,
                               read_comments=lambda *_: self.fail("Network access"))
        self.assertEqual(r["mcda"]["result"]["original"]["winner"], "Rewrite From Scratch")
        self.assertEqual(r["mcda"]["authority"], "ADVISORY_ONLY")
        self.assertFalse(r["mcda"]["notification_eligible"])

    def test_on_reads_single_selected_workflow(self):
        calls = []
        def reader(repo, issue, _token):
            calls.append((repo, issue))
            return [COMMENT]
        r = mod.run_invocation("on", workflow_config=MONITOR, workflow_id="project-42",
                               read_comments=reader, stamp="2026-10-14T14:00:00Z")
        self.assertEqual(calls, [("owner/project", 42)])
        obs = r["monitoring"]["snapshot"]["workflows"][0]["stages"][0]
        self.assertEqual(obs["state"], "SUBMITTED")
        self.assertEqual(obs["verification"], "UNVERIFIED")
        self.assertFalse(r["monitoring"]["scheduled_monitoring_changed"])

    def test_on_with_no_matching_evidence_unknown(self):
        result = mod.run_invocation("on", workflow_config=MONITOR,
                                    workflow_id="project-42", read_comments=lambda *_: [],
                                    stamp="2026-10-14T14:00:00Z")
        self.assertEqual(result["monitoring"]["snapshot"]["workflows"][0]["stages"][0]["state"],
                         "UNKNOWN")

    def test_on_with_decision_does_not_use_monitor_to_rescore(self):
        result = mod.run_invocation("on", workflow_config=MONITOR,
                                    workflow_id="project-42", read_comments=lambda *_: [COMMENT],
                                    decision=EXAMPLE)
        self.assertEqual(result["mcda"]["result"]["original"]["winner"], "Rewrite From Scratch")
        self.assertEqual(result["monitoring"]["authority"], "COMMENT_OBSERVATION_ONLY_NOT_VERIFIED")
        self.assertFalse(result["mcda"]["notification_eligible"])

    def test_on_without_mapping_rejected(self):
        for opts in ({"workflow_config": MONITOR},
                     {"workflow_id": "project-42"},
                     {}):
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                mod.run_invocation("on", **opts, read_comments=lambda *_: self.fail("should not read"))

    def test_on_disabled_mapping_rejected(self):
        config = copy.deepcopy(MONITOR)
        config["workflows"][0]["enabled"] = False
        with self.assertRaises(ValueError):
            mod.run_invocation("on", workflow_config=config, workflow_id="project-42",
                               read_comments=lambda *_: self.fail("should not read"))

    def test_on_placeholder_repository_rejected(self):
        config = copy.deepcopy(MONITOR)
        config["workflows"][0]["repository"] = "owner/repo"
        with self.assertRaises(ValueError):
            mod.run_invocation("on", workflow_config=config, workflow_id="project-42",
                               read_comments=lambda *_: self.fail("should not read"))

    def test_on_missing_allowlist_rejected(self):
        config = copy.deepcopy(MONITOR)
        config["workflows"][0]["stages"][0]["trusted_authors"] = []
        with self.assertRaises(ValueError):
            mod.run_invocation("on", workflow_config=config, workflow_id="project-42",
                               read_comments=lambda *_: self.fail("should not read"))

    def test_unrecognized_switch_fails(self):
        with self.assertRaises(ValueError):
            mod.run_invocation("scheduled")

    def test_malformed_enabled_config_fails_before_fetch(self):
        config = copy.deepcopy(MONITOR)
        config["workflows"][0]["stages"][0]["evidence_markers"] = []
        with self.assertRaises(ValueError):
            mod.run_invocation("on", workflow_config=config, workflow_id="project-42",
                               read_comments=lambda *_: self.fail("should not read"))

    def test_cli_default_off(self):
        proc = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["monitoring"]["status"], "SKIPPED")

    def test_cli_off_ignores_missing_workflow_file(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--monitor", "off",
                               "--workflow-config", "/some/file/that/does/not/exist"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_cli_on_no_config_fails_closed(self):
        proc = subprocess.run([sys.executable, str(SCRIPT), "--monitor", "on"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("INVOCATION_FAILED", proc.stderr)

    def test_cli_off_decision_scored(self):
        path = ROOT.parent / "software-mcda" / "assets" / "example-decision.json"
        proc = subprocess.run([sys.executable, str(SCRIPT), "--monitor", "off",
                               "--decision", str(path)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["mcda"]["result"]["original"]["winner"],
                         "Rewrite From Scratch")

    def test_on_no_issuer_side_effect(self):
        result = mod.run_invocation("on", workflow_config=MONITOR, workflow_id="project-42",
                                    read_comments=lambda *_: [COMMENT])
        self.assertEqual(result["schema"], "workflow-intelligence.invocation/v1")
        self.assertEqual(result["monitoring"]["scope"], "this_invocation_only")
        self.assertFalse(result["monitoring"]["scheduled_monitoring_changed"])


if __name__ == "__main__":
    unittest.main()
