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


if __name__ == "__main__":
    unittest.main()
