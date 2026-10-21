"""Offline falsifiers: source routing must never claim workflow execution."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "route_invocation.py"
spec = importlib.util.spec_from_file_location("uwp_route", SCRIPT)
route_module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(route_module)


class InvocationRoutingTests(unittest.TestCase):
    def test_explicit_start_routes_to_buddy_runner_not_observer(self):
        out = route_module.route("start", "buddy-runner-v1-7")
        self.assertEqual(out["route"], "GOVERNING_BUDDY_RUNNER_V17")
        self.assertEqual(out["state"], "PREPARATION_REQUIRED")
        self.assertIn("--status-json", out["command"])
        self.assertFalse(out["agent_invoked"])
        self.assertFalse(out["workflow_executed"])

    def test_one_time_live_progress_requires_config_check(self):
        out = route_module.route("progress", "buddy-runner-v1-7", "ON")
        self.assertEqual(out["route"], "UNIVERSAL_WORKFLOW_PROGRESS")
        self.assertEqual(out["state"], "READ_ONLY_OBSERVATION_REQUESTED")
        self.assertEqual(out["next_action"], "VERIFY_MAPPING_THEN_READ_ONCE")
        self.assertFalse(out["source_checked"])

    def test_progress_defaults_to_not_live(self):
        out = route_module.route("progress", "buddy-runner-v1-7")
        self.assertEqual(out["state"], "NOT_LIVE")
        self.assertEqual(out["monitor"], "OFF")

    def test_ambiguous_request_never_activates(self):
        out = route_module.route("unclear", "buddy-runner-v1-7")
        self.assertEqual(out["route"], "CLARIFY_INTENT")

    def test_missing_target_not_guessed(self):
        for intent in ("start", "progress"):
            with self.subTest(intent=intent):
                out = route_module.route(intent, "")
                self.assertEqual(out["route"], "REQUIRE_TARGET")

    def test_arbitrary_workflow_start_requires_governing_executor(self):
        out = route_module.route("start", "unknown-workflow", "ON")
        self.assertEqual(out["route"], "GOVERNING_EXECUTOR_REQUIRED")
        self.assertFalse(out["approval_granted"])

    def test_bad_monitor_or_intent_refused(self):
        for args in (("start", "buddy-runner-v1-7", "BYPASS"),
                     ("run", "buddy-runner-v1-7", "OFF")):
            with self.subTest(args=args), self.assertRaises(ValueError):
                route_module.route(*args)

    def test_cli_emits_exactly_one_machine_readable_decision(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--intent", "start",
             "--workflow", "buddy-runner-v1-7"], capture_output=True, text=True,
            check=True,
        )
        out = json.loads(proc.stdout)
        self.assertEqual(proc.stderr, "")
        self.assertEqual(out["schema"], "workflow-invocation-route/v1")
        for key in ("workflow_executed", "repository_mutated", "agent_invoked"):
            self.assertIs(out[key], False)

    def test_oracle_mcda_default_without_workflow_is_independent(self):
        out = route_module.route("mcda", "", consumer="oracle")
        self.assertEqual(out["route"], "ORACLE_MCDA_ADVISORY")
        self.assertEqual(out["render_order"], ["MCDA"])
        self.assertEqual(out["monitor"], "OFF")
        self.assertFalse(out["source_checked"])
        self.assertFalse(out["approval_granted"])

    def test_oracle_combined_off_progress_first_but_not_live(self):
        out = route_module.route("combined", "ciifr", consumer="oracle")
        self.assertEqual(out["route"], "ORACLE_MCDA_PROGRESS")
        self.assertEqual(out["render_order"], ["WORKFLOW_PROGRESS", "MCDA"])
        self.assertEqual(out["state"], "NOT_LIVE")
        self.assertFalse(out["repository_mutated"])

    def test_oracle_combined_on_requests_not_fabricates_read(self):
        out = route_module.route("combined", "ciifr", monitor="ON", consumer="oracle")
        self.assertEqual(out["state"], "READ_ONLY_OBSERVATION_REQUESTED")
        self.assertEqual(out["next_action"], "VERIFY_MAPPING_THEN_READ_ONCE_AND_KEEP_MCDA_ADVISORY")
        self.assertFalse(out["source_checked"])
        self.assertFalse(out["workflow_executed"])

    def test_missing_mapping_does_not_block_mcda(self):
        out = route_module.route("mcda", "", monitor="ON", consumer="oracle")
        self.assertEqual(out["route"], "MCDA_PROGRESS_TARGET_REQUIRED")
        self.assertTrue(out["mcda_allowed"])
        self.assertFalse(out["source_checked"])

    def test_oracle_start_does_not_become_observation(self):
        out = route_module.route("start", "ciifr", monitor="ON", consumer="oracle")
        self.assertEqual(out["route"], "GOVERNING_EXECUTOR_REQUIRED")
        self.assertFalse(out["agent_invoked"])
        self.assertFalse(out["approval_granted"])

    def test_invalid_consumer_is_refused(self):
        with self.assertRaises(ValueError):
            route_module.route("combined", "ciifr", consumer="ownerbot")

    def test_cli_oracle_combined_off_prints_no_execution_receipt(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--intent", "combined", "--workflow", "ciifr",
             "--consumer", "oracle"], capture_output=True, text=True, check=True)
        result = json.loads(proc.stdout)
        self.assertEqual(result["render_order"][0], "WORKFLOW_PROGRESS")
        self.assertEqual(result["route"], "ORACLE_MCDA_PROGRESS")
        self.assertFalse(result["workflow_executed"])


if __name__ == "__main__":
    unittest.main()
