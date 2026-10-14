import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("observe", ROOT / "scripts" / "observe.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
ZERO = "0" * 64
ONE = "1" * 64
BASE = {"schema": "workflow-progress-monitor/v1", "observed_at": "2026-10-14T00:00:00Z",
        "workflows": [{"id": "test", "repository": "owner/repo", "issue": 7, "stages": [
            {"id": "1a", "state": "SUBMITTED", "verification": "UNVERIFIED",
             "evidence": [{"comment_id": 2, "sha256": ZERO}]},
            {"id": "1b", "state": "UNKNOWN", "verification": "UNKNOWN", "evidence": []}]}]}


class TestReadOnlyAdapter(unittest.TestCase):
    def test_first_observation_is_baseline(self):
        self.assertEqual(mod.changed_events(BASE), [])

    def test_identical_snapshot_and_new_time_silent(self):
        latest = copy.deepcopy(BASE)
        latest["observed_at"] = "2026-10-15T00:00:00Z"
        self.assertEqual(mod.changed_events(latest, BASE), [])

    def test_comment_change_observation_not_verification(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"][0]["stages"][0]["evidence"].append({"comment_id": 3, "sha256": ONE})
        events = mod.changed_events(latest, BASE)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["authority"], "UNVERIFIED_COMMENT_OBSERVATION")
        self.assertFalse(events[0]["alert_eligible"])
        self.assertFalse(events[0]["mcda_eligible"])
        self.assertEqual(events, mod.changed_events(latest, BASE))

    def test_cross_scope_identity(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"][0]["repository"] = "elsewhere/project"
        evt = mod.changed_events(latest, BASE)[0]
        self.assertEqual(evt["source"]["repository"], "elsewhere/project")

    def test_refuse_forged_verified(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"][0]["stages"][0]["verification"] = "VERIFIED"
        with self.assertRaises(ValueError):
            mod.normalize(latest)

    def test_refuse_malformed_evidence(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"][0]["stages"][0]["evidence"][0]["sha256"] = "fake"
        with self.assertRaises(ValueError):
            mod.normalize(latest)

    def test_refuse_unknown_with_evidence(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"][0]["stages"][1]["evidence"] = [{"comment_id": 3, "sha256": ONE}]
        with self.assertRaises(ValueError):
            mod.normalize(latest)

    def test_refuse_duplicate_scope(self):
        latest = copy.deepcopy(BASE)
        latest["workflows"].append(copy.deepcopy(latest["workflows"][0]))
        with self.assertRaises(ValueError):
            mod.normalize(latest)

    def test_refuse_unsupported_schema(self):
        latest = copy.deepcopy(BASE)
        latest["schema"] = "workflow-progress-monitor/v2"
        with self.assertRaises(ValueError):
            mod.normalize(latest)


if __name__ == "__main__":
    unittest.main()
