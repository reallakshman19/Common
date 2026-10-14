"""Contract: one existing scheduler, opt-in sidecar, no live workflow enabled."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "universal-workflow-progress.yml"
CONFIG = ROOT / "skills" / "universal-workflow-progress" / "config" / "workflows.json"


class BridgeContract(unittest.TestCase):
    def test_one_cron_no_second_monitor(self):
        value = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(value.count("cron:"), 1)
        self.assertIn("7,22,37,52 * * * *", value)
        self.assertEqual(value.count("  observe:\n"), 1)
        self.assertIn("  uwi-handoff:\n", value)
        self.assertIn("    needs: observe\n", value)

    def test_opt_in_only(self):
        value = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("vars.UWI_DIAGNOSTIC_HANDOFF_ENABLED == 'true'", value)
        self.assertIn("if: github.event_name != 'pull_request'", value)
        self.assertIn("uwi_bootstrap:", value)
        self.assertIn("default: false", value)

    def test_artifact_paths_are_separate(self):
        value = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("name: universal-workflow-progress-state", value)
        self.assertIn("name: uwi-diagnostic-handoff-state", value)
        self.assertIn("path: .state/uwi-handoff.json", value)

    def test_prior_artifact_is_required_after_baseline(self):
        value = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("--bootstrap", value)
        self.assertIn("--previous-artifact", value)
        self.assertIn("test -s .state/previous-uwi-handoff.json", value)

    def test_monitor_config_remains_disabled(self):
        source = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertTrue(source["workflows"])
        self.assertTrue(all(wf["enabled"] is False for wf in source["workflows"]))


if __name__ == "__main__":
    unittest.main()
