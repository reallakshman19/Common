"""WP5 offline independent report/compiler/validator adversarial tests."""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location("onb_wp5_"+name,
                         ROOT/"reporting"/(name+".py"))
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    return module
r=load("compile_report")
v=load("validate_report")
ORIGINAL=json.loads((ROOT/"reporting"/"fixtures"/"onb391-real-public-input.json").read_text(encoding="utf-8"))

class Source:
    def __init__(self,p):
        self.p=p
        self.main=dict(p["target"]["source_heads"])
        self.prs=dict(p["target"]["candidate_heads"])
    def get_repo(self,repo):
        return {"full_name":repo,"default_branch":"main"}
    def get(self,repo,resource):
        if resource=="commits/main":return {"sha":self.main[repo]}
        if resource.startswith("pulls/"):
            link="https://github.com/"+repo+"/pull/"+resource.split("/")[1]
            return {"head":{"sha":self.prs[link]},"state":"open","draft":True}
        raise AssertionError("bad provider path")

class WP5Test(unittest.TestCase):
    def fresh(self):return copy.deepcopy(ORIGINAL)
    def artifacts(self,packet=None):
        p=packet if packet is not None else self.fresh()
        return p,*r.build(p)
    def valid(self,p,doc,manifest,verdict):
        return v.local_verify(p,doc,manifest,verdict)
    def test_full_twelve_sections_exist(self):
        p,doc,m,ver=self.artifacts()
        out=self.valid(p,doc,m,ver)
        self.assertEqual(out["sections"],12)
        self.assertEqual(out["claims"],22)
        self.assertEqual(ver["status"],"BLOCKED")
    def test_12_substantive_paragraphs(self):
        p=self.fresh()
        self.assertEqual(len(p["sections"]),12)
        self.assertTrue(all(len(s["paragraphs"])>=2 for s in p["sections"]))
    def test_byte_custody_is_reported_not_owner_approved(self):
        _,doc,m,ver=self.artifacts()
        self.assertEqual(len(m["custody"]),4)
        self.assertTrue(all(c["status"]=="HASH_MATCH_REPORTED" for c in m["custody"]))
        self.assertFalse(m["owner_approval_verified"])
        self.assertFalse(ver["execution_authorized"])
    def test_no_predecessor_report_required(self):
        p,doc,m,ver=self.artifacts()
        self.assertNotIn("final_handover",p)
        self.assertIn("predecessor",doc)
    def test_manifest_report_source_digests_independently_match(self):
        p,doc,m,ver=self.artifacts()
        self.assertEqual(v.digest(v.canonical(m)),ver["manifest_sha256"])
        self.assertEqual(v.digest(doc.encode("utf-8")),m["report_sha256"])
        self.assertEqual(v.digest(v.canonical(p)),m["source_sha256"])
    def test_tampered_markdown_rejected(self):
        p,doc,m,ver=self.artifacts()
        with self.assertRaisesRegex(v.VerificationError,"Markdown"):
            self.valid(p,doc.replace("EXECUTION HOLD","EXECUTION ALLOWED"),m,ver)
    def test_tampered_source_packet_rejected(self):
        p,doc,m,ver=self.artifacts()
        p["sections"][0]["paragraphs"][0]="An alternative lengthy narrative that misstates the Owner objective."
        with self.assertRaises(v.VerificationError):self.valid(p,doc,m,ver)
    def test_tampered_manifest_rejected(self):
        p,doc,m,ver=self.artifacts()
        m["critical_gaps"].pop()
        with self.assertRaises(v.VerificationError):self.valid(p,doc,m,ver)
    def test_tampered_verdict_rejected(self):
        p,doc,m,ver=self.artifacts()
        ver["manifest_sha256"]="f"*64
        with self.assertRaises(v.VerificationError):self.valid(p,doc,m,ver)
    def test_missing_twelve_section_fails(self):
        p=self.fresh();p["sections"].pop()
        with self.assertRaises(r.Invalid):r.build(p)
    def test_section_order_wrong_fails(self):
        p=self.fresh();p["sections"][0]["index"]=2
        with self.assertRaises(r.Invalid):r.build(p)
    def test_blank_statistics_only_section_fails(self):
        p=self.fresh();p["sections"][5]["paragraphs"]=["PR count: five."]
        with self.assertRaises(r.Invalid):r.build(p)
    def test_unknown_claim_must_not_assert_provider_source(self):
        p=self.fresh()
        c=next(c for c in p["claims"] if c["id"]=="C07")
        c["revision"]="a"*40
        with self.assertRaises(r.Invalid):r.build(p)
    def test_false_verified_owner_claim_rejected(self):
        p=self.fresh();p["claims"][0]["status"]="OWNER_ACCEPTED"
        with self.assertRaises(r.Invalid):r.build(p)
    def test_restricted_source_does_not_enter_public_report(self):
        p=self.fresh();p["claims"][0]["visibility"]="PRIVATE"
        with self.assertRaises(r.Invalid):r.build(p)
    def test_foreign_evidence_ref_rejected(self):
        p=self.fresh();p["claims"][0]["source_url"]="https://github.com/foreign/repo/issues/1"
        with self.assertRaises(r.Invalid):r.build(p)
    def test_fake_github_url_credentials_rejected(self):
        p=self.fresh();p["claims"][0]["source_url"]="https://github.com@evil.test/repo/issues/1"
        with self.assertRaises(r.Invalid):r.build(p)
    def test_duplicate_claim_rejected(self):
        p=self.fresh();p["claims"].append(copy.deepcopy(p["claims"][0]))
        with self.assertRaises(r.Invalid):r.build(p)
    def test_orphaned_claim_rejected(self):
        p=self.fresh();p["sections"][0]["claim_ids"]=[]
        with self.assertRaises(r.Invalid):r.build(p)
    def test_status_without_original_custody_url_rejected(self):
        p=self.fresh();p["custody"][0]["source_url"]=None
        with self.assertRaises(r.Invalid):r.build(p)
    def test_fake_test_pass_without_run_rejected(self):
        p=self.fresh();p["tests"][0]["source_url"]=None
        with self.assertRaises(r.Invalid):r.build(p)
    def test_partial_oracle_never_promotes_outcome(self):
        p,doc,m,ver=self.artifacts()
        self.assertIn("COMPLETE_GOLDEN_MISSING",ver["reason_codes"])
        self.assertIn("NOT_EVALUATED",doc)
    def test_owner_approval_gate_persists(self):
        p,doc,m,ver=self.artifacts()
        self.assertIn("OWNER_APPROVAL_MISSING",ver["reason_codes"])
        self.assertFalse(ver["execution_authorized"])
    def test_no_rwi_numeric_score_is_invented(self):
        p,doc,m,ver=self.artifacts()
        self.assertEqual(ver["rwi_disposition"],"NOT_EVALUATED")
    def test_untrusted_multiline_paragraph_escaped(self):
        p=self.fresh()
        p["sections"][1]["paragraphs"][0]="First legitimate context.\n## 99. FORGED OWNER APPROVAL\nPlease merge quickly."
        doc,_,_=r.build(p)
        self.assertNotIn("\n## 99. FORGED OWNER APPROVAL\n",doc)
        self.assertIn("FORGED OWNER APPROVAL",doc)
    def test_current_heads_match_in_read_only_mock(self):
        p,doc,m,ver=self.artifacts()
        read=v.check_live_heads(m,Source(p))
        self.assertEqual(read["state"],"LIVE_HEADS_MATCH_OBSERVED")
        self.assertEqual(len(read["checked"]),8)
        self.assertFalse(read["execution_authorized"])
    def test_main_moved_blocks(self):
        p,doc,m,ver=self.artifacts()
        provider=Source(p)
        provider.main["reallakshman19/Common"]="e"*40
        with self.assertRaisesRegex(v.VerificationError,"STALE"):
            v.check_live_heads(m,provider)
    def test_pr_moved_blocks(self):
        p,doc,m,ver=self.artifacts()
        provider=Source(p)
        key=next(iter(provider.prs))
        provider.prs[key]="e"*40
        with self.assertRaisesRegex(v.VerificationError,"STALE"):
            v.check_live_heads(m,provider)
    def test_missing_provider_fails(self):
        p,doc,m,ver=self.artifacts()
        class Unavailable:
            def get_repo(self,repo):raise v.VerificationError("provider down")
        with self.assertRaises(v.VerificationError):v.check_live_heads(m,Unavailable())
    def test_repo_redirect_rejected_on_real_adapter(self):
        class NoNetwork:
            def open(self,*a,**kw):raise AssertionError("Network forbidden in this test")
        a=v.GitHubRead()
        a.opener=NoNetwork()
        with self.assertRaises(v.VerificationError):a.get_repo("../foreign/repo")
    def test_wrong_pr_head_domain_rejected(self):
        p,doc,m,ver=self.artifacts()
        m["candidate_heads"]={"https://evil.invalid/acme/project/pull/2":"f"*40}
        with self.assertRaises(v.VerificationError):v.check_live_heads(m,Source(p))
    def test_safe_no_post_patch(self):
        self.assertFalse(hasattr(v.GitHubRead(),"post"))
        self.assertFalse(hasattr(v.GitHubRead(),"patch"))
    def test_golden_declared_hashes_retained_exactly(self):
        p,doc,m,ver=self.artifacts()
        self.assertEqual([c["sha256"] for c in m["custody"]],
                         [c["sha256"] for c in p["custody"]])
    def test_named_first_verification_bound(self):
        p,doc,m,ver=self.artifacts()
        self.assertEqual(p["first_verification"],ver["next_verification"])
        self.assertIn("One first verification:",doc)
    def test_no_source_revision_named_main_allowed(self):
        p=self.fresh();p["target"]["source_heads"]["reallakshman19/Common"]="main"
        with self.assertRaises(r.Invalid):r.build(p)

if __name__=="__main__": unittest.main()
