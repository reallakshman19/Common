"""Execute original local source, preserve its native receipt and prepare review."""
import copy
import importlib.util
import unittest

from adapter_support import ROOT, native_return
from nd_io import load_json
from nd_profiles import load_profiles
from nd_team import task_binding
from nd_returns import receive
from nd_adapters import adapt


class RuntimeCycleTests(unittest.TestCase):
    def test_original_source_execution_return_review_and_successor_cycle(self):
        folder = ROOT / "examples/team-cycle"
        intent, plan = load_json(folder / "intent.json"), load_json(folder / "plan.json")
        profiles = load_profiles()
        spec = importlib.util.spec_from_file_location("nd_original_fixture", folder / "source.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        late_old = {"current_revision": 10, "result": "NEW"}
        module.receive(late_old, 9, "OLD")
        control = {"current_revision": 10, "result": "OLD"}
        module.receive(control, 10, "NEW")
        self.assertEqual(late_old["result"], "OLD")
        self.assertEqual(control["result"], "NEW")
        report = native_return(task_binding(intent, plan, "N-PROBE"))
        report["native_report"]["content"] = "Actual original-function results: late old=" + late_old["result"] + "; current=" + control["result"]
        report["attempts"][0]["observed"] = report["native_report"]["content"]
        before = copy.deepcopy([intent, plan, report])
        worksheet = receive(intent, plan, report, profiles)
        review = adapt(intent, plan, "N-PROBE", profiles, "reviewer", "github", "R", report)
        successor = adapt(intent, plan, "N-PROBE", profiles, "successor", "buddy-checkpoint", report=report)
        self.assertIn("late old=OLD", review["content"])
        self.assertIn("N-EXPORT", successor["content"])
        self.assertIn("N-EXPORT", worksheet["independent_candidates"])
        self.assertNotIn("N-REVIEW", worksheet["independent_candidates"])
        self.assertEqual(worksheet["accepted_outcomes"], [])
        self.assertFalse(review["independence_verified"])
        self.assertEqual(before, [intent, plan, report])


if __name__ == "__main__":
    unittest.main()
