"""Handover Master read-only routing, version and blind-isolation contract tests."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("handover_master",ROOT/"route.py")
m=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=m
spec.loader.exec_module(m)

class RouterTests(unittest.TestCase):
    def sel(self,**args):
        return m.route(**args)

    def assert_selected(self,result,key):
        self.assertEqual(result["status"],"READ_SOURCE_NOW")
        self.assertEqual(result["selection"]["source_key"],key)
        self.assertFalse(result["may_execute_generator"])
        self.assertFalse(result["may_write_or_publish"])
        self.assertFalse(result["owner_approval_verified"])
        self.assertFalse(result["source_freshness_verified"])
        self.assertTrue(result["canonical_read_paths"])

    def test_two_standalone(self):
        x=self.sel(mode="two-pass")
        self.assert_selected(x,"two_standalone")
        self.assertTrue(any("schema.md" in p for p in x["canonical_read_paths"]))

    def test_three_standalone(self):
        x=self.sel(mode="three-pass")
        self.assert_selected(x,"three_standalone")
        self.assertTrue(any("three-pass" in p for p in x["canonical_read_paths"]))

    def test_two_v36(self):
        x=self.sel(mode="two-pass",workflow="v3.6")
        self.assert_selected(x,"v36")
        self.assertIn("skills/engineering-pr-delivery-v3.6/scripts/prompt_2pass_v36.py",x["canonical_read_paths"])

    def test_three_v36(self):
        x=self.sel(mode="three-pass",workflow="v3.6")
        self.assert_selected(x,"v36")
        self.assertIn("skills/engineering-pr-delivery-v3.6/scripts/prompt_3pass_v36.py",x["canonical_read_paths"])

    def test_standalone_never_uses_v36(self):
        x=self.sel(mode="three-pass",workflow="standalone")
        self.assertNotIn("v36",x["selection"]["source_key"])

    def test_v36_intent_detected_without_flag(self):
        x=self.sel(intent="Please generate three-pass prompts for v3.6.")
        self.assert_selected(x,"v36")
        self.assertEqual(x["selection"]["mode"],"three-pass")

    def test_v35_governance_from_intent_is_not_v36(self):
        x=self.sel(intent="Technical handover for legacy v3.5",stage1_freeze_verified=True)
        self.assert_selected(x,"v35_legacy")

    def test_v35_no_new_two_pass(self):
        x=self.sel(mode="two-pass",workflow="v3.5")
        self.assertEqual(x["status"],"HOLD")

    def test_v35_v36_conflict(self):
        x=self.sel(mode="three-pass",intent="v3.5 to v3.6")
        self.assertEqual(x["status"],"NEEDS_WORKFLOW")

    def test_no_mode_selected(self):
        x=self.sel(intent="Please help with the repository")
        self.assertEqual(x["status"],"NEEDS_SELECTION")
        self.assertEqual(x["canonical_read_paths"],[])

    def test_multiple_modes_ambiguity(self):
        x=self.sel(intent="Should I do two-pass or three-pass?")
        self.assertEqual(x["status"],"NEEDS_SELECTION")
        self.assertEqual(set(x["choices"]),{"two-pass","three-pass"})

    def test_explicit_mode_beats_intent(self):
        x=self.sel(mode="two-pass",intent="three pass?")
        self.assert_selected(x,"two_standalone")

    def test_invalid_mode_fails(self):
        with self.assertRaises(ValueError):
            self.sel(mode="run_everything")

    def test_invalid_workflow_fails(self):
        with self.assertRaises(ValueError):
            self.sel(workflow="v4.0")

    def test_buddy_missing_version_outside_v36(self):
        x=self.sel(mode="buddy",phase="1a")
        self.assertEqual(x["status"],"NEEDS_VERSION")

    def test_buddy_missing_phase(self):
        x=self.sel(mode="buddy",buddy_version="1.7")
        self.assertEqual(x["status"],"NEEDS_PHASE")

    def test_v36_pinned_buddy16(self):
        x=self.sel(mode="buddy",workflow="v3.6",phase="1a")
        self.assert_selected(x,"buddy16")
        self.assertEqual(x["selection"]["buddy_version"],"1.6")

    def test_explicit_buddy17_standalone(self):
        x=self.sel(mode="buddy",buddy_version="1.7",phase="1b")
        self.assert_selected(x,"buddy17")

    def test_no_silent_upgrade_v36_to_buddy17(self):
        x=self.sel(mode="buddy",workflow="v3.6",buddy_version="1.7",phase="2")
        self.assertEqual(x["status"],"HOLD_VERSION")

    def test_buddy_final_is_not_fourth_stage(self):
        x=self.sel(mode="buddy",buddy_version="1.6",phase="2")
        self.assert_selected(x,"buddy16")
        self.assertEqual(x["selection"]["phase"],"2")
        self.assertTrue(any("no acknowledgement loop" in s for s in x["preflight"]))

    def test_buddy_y_is_one_evidence_intervention(self):
        x=self.sel(mode="buddy",buddy_version="1.7",phase="Y")
        self.assert_selected(x,"buddy17")
        self.assertTrue(any("Task Evidence Xb" in s for s in x["preflight"]))

    def test_buddy_bad_phase(self):
        with self.assertRaises(ValueError):
            self.sel(mode="buddy",buddy_version="1.7",phase="3")

    def test_technical_requires_stage1_freeze(self):
        x=self.sel(mode="technical")
        self.assertEqual(x["status"],"HOLD_FREEZE")

    def test_technical_after_freeze_still_no_permissions(self):
        x=self.sel(mode="technical",stage1_freeze_verified=True)
        self.assert_selected(x,"technical")
        self.assertIn("relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md",x["canonical_read_paths"])

    def test_v35_technical_still_requires_freeze(self):
        x=self.sel(mode="technical",workflow="v3.5")
        self.assertEqual(x["status"],"HOLD_FREEZE")

    def test_v35_technical_routes_native_not_template(self):
        x=self.sel(mode="technical",workflow="v3.5",stage1_freeze_verified=True)
        self.assert_selected(x,"v35_legacy")

    def test_zero_exit_routes_wp5(self):
        x=self.sel(mode="zero-exit")
        self.assert_selected(x,"onb")
        self.assertTrue(any("compile_report.py" in p for p in x["canonical_read_paths"]))

    def test_zero_exit_intent(self):
        self.assert_selected(self.sel(intent="Need cold successor without handover"),"onb")

    def test_progress_status_is_observer(self):
        self.assert_selected(self.sel(intent="check progress status"),"observer")

    def test_status_never_advances_buddy(self):
        x=self.sel(mode="status")
        self.assert_selected(x,"observer")
        self.assertNotIn("buddy",x["selection"]["source_key"])

    def test_auto_detect_buddy(self):
        x=self.sel(intent="Run BuddyRunner 1a please")
        self.assertEqual(x["status"],"NEEDS_VERSION")

    def test_source_registry_has_native_skills(self):
        source=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
        self.assertEqual(source["schema"],"handover-master.sources/v1")
        self.assertTrue({"technical","two_standalone","three_standalone","v36","buddy16",
                         "buddy17","onb","v35_legacy","observer","mcda"}.issubset(source["sources"]))
        for ref in source["sources"].values():
            self.assertFalse(ref["path"].startswith("/"))
            self.assertTrue(ref["path"].startswith(("skills/","relay/")))

    def test_all_referenced_main_sources_exist(self):
        source=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
        for key,info in source["sources"].items():
            for p in info:
                if p in ("path","schema","validator","two_script","three_script","cold_script",
                         "script","compiler"):
                    target=m.REPO_ROOT / info[p]
                    self.assertTrue(target.is_file(),f"{key}: missing canonical {target}")

    def test_local_status_is_not_external_authority(self):
        for x in (self.sel(mode="two-pass"),self.sel(mode="status"),
                  self.sel(mode="technical",stage1_freeze_verified=True)):
            self.assertFalse(x.get("may_write_or_publish"))
            self.assertFalse(x.get("owner_approval_verified"))

    def test_output_includes_live_source_requirement(self):
        x=self.sel(mode="three-pass")
        self.assertTrue(any("THIS RUN" in t for t in x["preflight"]))

    def test_output_has_no_arbitrary_cli_execution(self):
        x=self.sel(mode="two-pass")
        self.assertFalse(x["may_execute_generator"])
        self.assertFalse(hasattr(m,"run_shell"))
        self.assertFalse(hasattr(m,"apply"))

    def test_route_markdown_lists_source_links(self):
        x=self.sel(mode="two-pass")
        view=m.as_markdown(x)
        self.assertIn("https://github.com/reallakshman19/Common/blob/main/",view)
        self.assertIn("Safety:",view)

    def test_route_markdown_failure_no_link_to_wrong_protocol(self):
        x=self.sel(mode="technical")
        view=m.as_markdown(x)
        self.assertIn("HOLD_FREEZE",view)
        self.assertNotIn("github.com/reallakshman19/Common/blob/main/",view)

if __name__=="__main__":unittest.main()
