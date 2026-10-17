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

    def test_two_pass_compact_invocation(self):
        self.assert_selected(self.sel(intent="Generate 2pass for this system"),"two_standalone")

    def test_three_pass_compact_invocation(self):
        self.assert_selected(self.sel(intent="Generate 3pass for this system"),"three_standalone")

    def test_compact_two_three_ambiguity(self):
        result=self.sel(intent="Which of 2pass or 3pass is better?")
        self.assertEqual(result["status"],"NEEDS_SELECTION")

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
        self.assertIsNone(x["selection"])
        self.assertEqual(x["canonical_read_paths"],[])

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


# --- Common #408 HM-01/HM-04: v3.6 version-amendment preview (contract v2, #408 comment 6230181135) ---
FIXTURE_REF="https://github.com/reallakshman19/CoordinatorLandingpage/issues/1#issuecomment-6230132308"

class AmendmentRefTests(unittest.TestCase):
    def flags_false(self,x):
        for k in ("may_execute_generator","may_write_or_publish","owner_approval_verified","source_freshness_verified"):
            self.assertIs(x[k],False,k)

    def test_preview_with_valid_ref_is_not_admission(self):
        for phase in ("1a","1b","2","Y"):
            x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",phase=phase,amendment_ref=FIXTURE_REF)
            self.assertEqual(x["status"],"PROVISIONAL_ROUTE")
            self.assertIsNone(x["selection"])
            self.assertEqual(x["canonical_read_paths"],[])
            self.flags_false(x)
            pv=x["preview"]
            self.assertEqual(pv["native_pin"]["buddy_version"],"1.6")
            self.assertEqual(pv["candidate"]["buddy_version"],"1.7")
            self.assertEqual(pv["workflow"],"v3.6")
            self.assertEqual(pv["phase"],phase)
            self.assertTrue(pv["native_pin"]["read_paths"] and pv["candidate"]["read_paths"])
            self.assertIs(x["amendment_ref"]["verified"],False)
            self.assertEqual(x["amendment_ref"]["applied"],"preview_only")
            self.assertTrue(len(x["controller_must_verify"])>=5)

    def test_preview_cli_exit_is_non_success_and_markdown_is_explicit(self):
        args=["--mode","buddy","--workflow","v3.6","--buddy-version","1.7","--phase","1b","--amendment-ref",FIXTURE_REF]
        import contextlib,io
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(m.main(args+["--format","json"]),2)
        self.assertIn("PROVISIONAL_ROUTE",out.getvalue())
        view=m.as_markdown(m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",phase="1b",amendment_ref=FIXTURE_REF))
        self.assertIn("PROVISIONAL",view)
        self.assertIn("NOT ADMITTED",view)
        self.assertIn("controller must verify",view)
        self.assertIn(FIXTURE_REF,view)
        self.assertNotIn("Read these current-main sources",view)
        self.assertNotIn("Execute only",view)

    def test_ref_does_not_replace_phase(self):
        x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",amendment_ref=FIXTURE_REF)
        self.assertEqual(x["status"],"NEEDS_PHASE")
        self.flags_false(x)

    def test_ref_without_upgrade_request_keeps_native_16(self):
        x=m.route(mode="buddy",workflow="v3.6",phase="1a",amendment_ref=FIXTURE_REF)
        self.assertEqual(x["status"],"READ_SOURCE_NOW")
        self.assertEqual(x["selection"]["buddy_version"],"1.6")
        self.assertIs(x["amendment_ref"]["applied"],False)
        self.flags_false(x)

    def test_explicit_16_with_ref_unused(self):
        x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.6",phase="2",amendment_ref=FIXTURE_REF)
        self.assertEqual(x["selection"]["source_key"],"buddy16")
        self.assertIs(x["amendment_ref"]["applied"],False)
        self.assertIn("not applied",m.as_markdown(x))

    def test_ref_unused_outside_v36(self):
        x=m.route(mode="two-pass",amendment_ref=FIXTURE_REF)
        self.assertEqual(x["status"],"READ_SOURCE_NOW")
        self.assertEqual(x["selection"]["source_key"],"two_standalone")
        self.assertIs(x["amendment_ref"]["applied"],False)
        y=m.route(mode="buddy",buddy_version="1.7",phase="1b",amendment_ref=FIXTURE_REF)
        self.assertEqual(y["selection"]["source_key"],"buddy17")
        self.assertIs(y["amendment_ref"]["applied"],False)

    def test_ref_does_not_cure_selection_or_workflow(self):
        self.assertEqual(m.route(intent="Which of 2pass or 3pass is better?",amendment_ref=FIXTURE_REF)["status"],"NEEDS_SELECTION")
        self.assertEqual(m.route(intent="v3.5 and v3.6 buddy",amendment_ref=FIXTURE_REF)["status"],"NEEDS_WORKFLOW")
        self.assertEqual(m.route(mode="buddy",workflow="v3.5",amendment_ref=FIXTURE_REF)["status"],"HOLD")

    def test_malformed_and_lookalike_refs_rejected(self):
        bad=["http://github.com/reallakshman19/Common/issues/408",
             "https://github.com.evil.example/reallakshman19/Common/issues/408",
             "https://github.com@evil.example/reallakshman19/Common/issues/408",
             "https://user:pw@github.com/reallakshman19/Common/issues/408",
             "https://github.com:443/reallakshman19/Common/issues/408",
             "https://github.com/reallakshman19",
             "https://github.com/reallakshman19/Common",
             "https://github.com/reallakshman19/Common/issues/0",
             "https://github.com/reallakshman19/Common/issues/408#issuecomment-abc",
             "https://github.com/reallakshman19/Common/issues/408#top",
             "https://github.com/reallakshman19/Common/issues/408?x=1",
             "https://github.com/reallakshman19/Common/blob/main/README.md",
             "https://github.com/reallakshman19/Common/issues/40%38",
             "https://github.com/reallakshman19/Common/issues/408 ",
             "https://github.com/reallakshman19/Common/issues/4\n08",
             "","x"*301]
        for ref in bad:
            x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",phase="1b",amendment_ref=ref)
            self.assertEqual(x["status"],"INVALID_AMENDMENT_REF",ref)
            self.assertIsNone(x["selection"])
            self.flags_false(x)
            self.assertNotIn("preview",x)

    def test_well_formed_wrong_scope_ref_is_still_only_a_preview(self):
        # Syntax validity is never authority validity: an unrelated issue URL still yields only an unverified preview.
        x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",phase="1a",
                  amendment_ref="https://github.com/reallakshman19/Common/pull/398")
        self.assertEqual(x["status"],"PROVISIONAL_ROUTE")
        self.flags_false(x)
        self.assertIs(x["amendment_ref"]["verified"],False)

    def test_unused_ref_reported_on_every_denial(self):
        cases=[dict(mode="buddy",workflow="v3.6",buddy_version="1.6"),            # NEEDS_PHASE
               dict(intent="Which of 2pass or 3pass is better?"),                  # NEEDS_SELECTION
               dict(intent="v3.5 and v3.6 buddy"),                                 # NEEDS_WORKFLOW
               dict(mode="buddy",workflow="v3.5"),                                 # HOLD
               dict(mode="technical")]                                             # HOLD_FREEZE
        for args in cases:
            x=m.route(amendment_ref=FIXTURE_REF,**args)
            self.assertNotIn(x["status"],("READ_SOURCE_NOW","PROVISIONAL_ROUTE"),args)
            self.assertIs(x["amendment_ref"]["applied"],False,args)
            self.assertIn("not applied",m.as_markdown(x))
            self.flags_false(x)

    def test_dot_and_git_repo_segments_rejected(self):
        for ref in ("https://github.com/a/../issues/1","https://github.com/a/./issues/1",
                    "https://github.com/a/.../issues/1","https://github.com/a/r.git/issues/1",
                    "https://github.com/a-/r/issues/1","HTTPS://github.com/a/r/issues/1",
                    "https://github.com/a/r/issues/1#",
                    "https://github.com/o/r/issues/1?","https://github.com/o/r.git./issues/1",
                    "https://github.com/o/r./issues/1"):
            x=m.route(mode="buddy",workflow="v3.6",buddy_version="1.7",phase="1a",amendment_ref=ref)
            self.assertEqual(x["status"],"INVALID_AMENDMENT_REF",ref)

    def test_positional_api_unchanged(self):
        x=m.route("","buddy","v3.6","1a",None,False)
        self.assertEqual(x["selection"]["source_key"],"buddy16")
        self.assertNotIn("amendment_ref",x)
        y=m.route("","buddy","v3.6","1a","1.7",False)
        self.assertEqual(y["status"],"HOLD_VERSION")

if __name__=="__main__":unittest.main()
