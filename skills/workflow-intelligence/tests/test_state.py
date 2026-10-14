"""Durable observation-state regression and negative tests."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("uwi_state", ROOT / "scripts" / "state.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
H0 = "0" * 64
H1 = "1" * 64
BASE = {"schema": "workflow-progress-monitor/v1", "observed_at": "2026-10-14T01:00:00Z",
        "workflows": [{"id": "w", "repository": "owner/repo", "issue": 2,
                       "stages": [{"id": "1b", "state": "SUBMITTED", "verification": "UNVERIFIED",
                                   "evidence": [{"comment_id": 5, "sha256": H0}]}]}]}


class StateTest(unittest.TestCase):
    def test_baseline_silent(self):
        state, events = mod.advance(BASE)
        self.assertEqual(state["schema"], mod.STATE_SCHEMA)
        self.assertEqual(events, [])

    def test_same_semantics_new_poll_time_silent(self):
        old, _ = mod.advance(BASE)
        now = copy.deepcopy(BASE)
        now["observed_at"] = "2026-10-15T01:00:00Z"
        self.assertEqual(mod.advance(now, old)[1], [])

    def test_changed_observation_never_actionable(self):
        old, _ = mod.advance(BASE)
        now = copy.deepcopy(BASE)
        now["workflows"][0]["stages"][0]["evidence"].append({"comment_id": 6, "sha256": H1})
        new, events = mod.advance(now, old)
        self.assertEqual(len(events), 1)
        self.assertFalse(events[0]["alert_eligible"])
        self.assertFalse(events[0]["mcda_eligible"])
        self.assertEqual(events[0]["authority"], "UNVERIFIED_COMMENT_OBSERVATION")
        self.assertEqual(mod.advance(now, old)[1], events)
        self.assertEqual(mod.advance(now, new)[1], [])

    def test_removed_workflow_notified_only_as_diagnostic(self):
        old, _ = mod.advance(BASE)
        now = {"schema": "workflow-progress-monitor/v1", "workflows": []}
        self.assertEqual(mod.advance(now, old)[1][0]["kind"], "OBSERVATION_REMOVED")

    def test_repository_namespace_isolation(self):
        old, _ = mod.advance(BASE)
        now = copy.deepcopy(BASE)
        now["workflows"][0]["repository"] = "other/repo"
        events = mod.advance(now, old)[1]
        self.assertEqual(len(events), 2)
        self.assertEqual(len(set(e["event_id"] for e in events)), 2)

    def test_issue_namespace_isolation(self):
        old, _ = mod.advance(BASE)
        now = copy.deepcopy(BASE)
        now["workflows"][0]["issue"] = 3
        self.assertEqual(len(mod.advance(now, old)[1]), 2)

    def test_bad_prior_hash_fails_closed(self):
        old, _ = mod.advance(BASE)
        key = next(iter(old["entries"]))
        old["entries"][key]["semantic_sha256"] = H0
        with self.assertRaises(ValueError):
            mod.advance(BASE, old)

    def test_bad_prior_schema_fails(self):
        with self.assertRaises(ValueError):
            mod.advance(BASE, {"schema": "wrong", "entries": {}})

    def test_forged_verification_rejected(self):
        now = copy.deepcopy(BASE)
        now["workflows"][0]["stages"][0]["verification"] = "VERIFIED"
        with self.assertRaises(ValueError):
            mod.advance(now)

    def test_bad_prior_key_fails(self):
        old, _ = mod.advance(BASE)
        value = next(iter(old["entries"].values()))
        old["entries"] = {json.dumps(["owner/repo", "w", 2, "wrong"]): value}
        with self.assertRaises(ValueError):
            mod.advance(BASE, old)

    def test_schema_upgrade_not_assumed(self):
        now = copy.deepcopy(BASE)
        now["schema"] = "workflow-progress-monitor/v2"
        with self.assertRaises(ValueError):
            mod.advance(now)

    def test_missing_prior_observation_is_not_verified(self):
        old, _ = mod.advance(BASE)
        now = copy.deepcopy(BASE)
        now["workflows"][0]["stages"][0]["evidence"].append({"comment_id": 7, "sha256": H1})
        events = mod.advance(now, old)[1]
        self.assertEqual(events[0]["observation"]["verification"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
