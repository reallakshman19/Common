"""Native v3.6 addendum regression: evidence precedence and lossless tombstones."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"scripts"/"continuity_addendum_v36.py"
SPEC=importlib.util.spec_from_file_location("continuity_addendum_v36",SOURCE)
c=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)
SYNTH=ROOT/"tests"/"fixtures"/"chainage-tombstone-synthetic.json"

class CodingAddendumTests(unittest.TestCase):
    def chain(self):
        return json.loads(SYNTH.read_text(encoding="utf-8"))
    def refusal(self,x,code):
        with self.assertRaisesRegex(c.AddendumError,code):
            c.render_chain(x)

    def test_v36_governed_still_mandatory(self):
        got=c.evidence_choice(governed_v36=True,has_issue=True)
        self.assertEqual(got["mode"],"NATIVE_V36_REQUIRED")
        self.assertTrue(got["required"])
        self.assertEqual(got["protocol"],"TASK_EVIDENCE v3.6")
    def test_teamowner_v2_takes_precedence(self):
        got=c.evidence_choice(project_protocol="TASK EVIDENCE v2",has_issue=True)
        self.assertEqual(got["mode"],"PROJECT_PROTOCOL_REQUIRED")
        self.assertEqual(got["protocol"],"TASK EVIDENCE v2")
    def test_explicit_alternative_takes_precedence(self):
        got=c.evidence_choice(explicit_protocol="Custom Reviewer Evidence v5")
        self.assertEqual(got["mode"],"EXPLICIT_PROTOCOL_PRESERVED")
    def test_conflict_project_vs_explicit_is_hold(self):
        got=c.evidence_choice(project_protocol="TASK EVIDENCE v2",
                              explicit_protocol="TASK_EVIDENCE v3.6")
        self.assertEqual(got["mode"],"PROTOCOL_CONFLICT_HOLD")
    def test_bound_v36_vs_other_explicit_is_hold(self):
        got=c.evidence_choice(governed_v36=True,explicit_protocol="Ad hoc evidence")
        self.assertEqual(got["mode"],"PROTOCOL_CONFLICT_HOLD")
    def test_unbound_v36_must_not_forge_child(self):
        got=c.evidence_choice(explicit_protocol="v3.6",has_issue=True)
        self.assertEqual(got["mode"],"V36_BINDING_MISSING_HOLD")
    def test_adhoc_optional_even_if_issue_link_present(self):
        got=c.evidence_choice(has_issue=True)
        self.assertEqual(got["mode"],"OPTIONAL_ADHOC_ADVISORY")
        self.assertFalse(got["required"])
        self.assertFalse(got["may_publish"])
        self.assertFalse(got["may_count_for_v36_o2"])
    def test_no_issue_is_chat_only(self):
        got=c.evidence_choice()
        self.assertEqual(got["target"],"CHAT_ONLY")
    def test_empty_explicit_protocol_rejected(self):
        with self.assertRaisesRegex(c.AddendumError,"INVALID_PROTOCOL_SELECTOR"):
            c.evidence_choice(explicit_protocol="")

    def test_tombstone_kept_in_middle(self):
        rendered=c.render_chain(self.chain())
        self.assertIn("[#123](https://github.com/example/tracker/issues/123)",rendered)
        self.assertIn("~~[#125](https://github.com/example/tracker/issues/125)~~",rendered)
        self.assertIn("[#126](https://github.com/example/tracker/issues/126)",rendered)
        self.assertIn("INVALID_REPORTED",rendered)
        self.assertIn("issuecomment-12345",rendered)
        self.assertEqual(rendered.count(" → "),2)
        self.assertLess(rendered.index("#123"),rendered.index("#125"))
        self.assertLess(rendered.index("#125"),rendered.index("#126"))
    def test_not_found_does_not_claim_deleted(self):
        x=self.chain()
        x["nodes"][1].update(state="NOT_FOUND_UNVERIFIED",
                             reason="GitHub returned not found, visibility and deletion unknown",
                             decision_ref=None)
        rendered=c.render_chain(x)
        self.assertIn("NOT_FOUND_UNVERIFIED",rendered)
        self.assertNotIn("~~[#125]",rendered)
    def test_inaccessible_does_not_strike(self):
        x=self.chain()
        x["nodes"][1].update(state="INACCESSIBLE_UNVERIFIED",
                             reason="Current token cannot read the issue, privacy is unknown",
                             decision_ref=None)
        self.assertNotIn("~~[#125]",c.render_chain(x))
    def test_reported_deletion_requires_source(self):
        x=self.chain()
        x["nodes"][1].update(state="DELETED_REPORTED",
                             reason="The archive owner reported deletion of this issue",
                             decision_ref=None)
        self.refusal(x,"DECISION_REF_MISSING")
    def test_unknown_reason_required(self):
        x=self.chain()
        x["nodes"][1].update(state="UNKNOWN",reason="",decision_ref=None)
        self.refusal(x,"REASON_MISSING_OR_UNSAFE")
    def test_deleted_without_proof_not_inferred(self):
        x=self.chain()
        x["nodes"][1]["state"]="DELETED_VERIFIED"
        self.refusal(x,"UNSUPPORTED_STATE")
    def test_reordered_edge_rejected(self):
        x=self.chain()
        x["nodes"][2]["parent"]=123
        self.refusal(x,"MISSING_OR_REORDERED_CHAIN_EDGE")
    def test_duplicate_issue_rejected(self):
        x=self.chain()
        x["nodes"][2]["issue"]=125
        self.refusal(x,"DUPLICATE_OR_INVALID_ISSUE")
    def test_wrong_repo_decision_rejected(self):
        x=self.chain()
        x["nodes"][1]["decision_ref"]="https://github.com/other/repo/issues/5"
        self.refusal(x,"DECISION_REF_FOREIGN_OR_INVALID")
    def test_untrusted_hostname_rejected(self):
        x=self.chain()
        x["nodes"][1]["decision_ref"]="https://github.com.evil.com/example/tracker/issues/5"
        self.refusal(x,"DECISION_REF_FOREIGN_OR_INVALID")
    def test_query_redirect_rejected(self):
        x=self.chain()
        x["nodes"][1]["decision_ref"]+="?token=abc"
        self.refusal(x,"DECISION_REF_FOREIGN_OR_INVALID")
    def test_active_issue_cannot_have_invalid_reason(self):
        x=self.chain()
        x["nodes"][1]["state"]="ACTIVE"
        self.refusal(x,"ACTIVE_CANNOT_CLAIM_TOMBSTONE")
    def test_markdown_reason_escaped(self):
        x=self.chain()
        x["nodes"][1]["reason"]="Superseded because original [claim](untrusted) is wrong"
        rendered=c.render_chain(x)
        self.assertIn(r"\[claim\]",rendered)
        self.assertIn(r"\(untrusted\)",rendered)
    def test_advisory_receipt_has_no_canonical_native_marker(self):
        result=c.advisory_evidence(chain=self.chain(),outcome="Current HTML verification remains held",
            source_sha="a"*40,
            implementation_crux="Source Reader to Worker session to Output consumer",
            originals="Original complete golden UNKNOWN, synthetic input not acceptable",
            tests="Hosted exact SHA tests not run; no real Owner workload measured",
            next_check="Fetch served JavaScript blob and compare canonical readiness",
            result="423 original weights unresolved, no native CII release")
        self.assertIn("TASK_EVIDENCE — ADHOC",result)
        self.assertIn("~~[#125]",result)
        self.assertIn("NOT_GRANTED",result)
        self.assertNotIn("TASK_EVIDENCE v3.6",result)
        self.assertNotIn("Outcome:",result)
    def test_advisory_receipt_requires_real_sha(self):
        opts=dict(chain=self.chain(),outcome="Source evidence remains subject to review",
            source_sha="abc",implementation_crux="The source reader feeds the worker result",
            originals="Full authentic output golden is not yet available",
            tests="No original user workload browser evidence was run",
            next_check="Refetch exact current source and test normal propagation",
            result="Reported completion is not original-mass acceptance")
        with self.assertRaisesRegex(c.AddendumError,"SOURCE_SHA_INVALID"):
            c.advisory_evidence(**opts)

if __name__=="__main__":unittest.main()
