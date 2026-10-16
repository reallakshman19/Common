"""R2 GitHub-only issue spine: real-shape fake providers and scope negatives."""
import base64
import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import issue_spine_read_v36 as sp

REPO="reallakshman19/Common"
PARENT=REPO+"#400"
MAIN="0a7c4d45d3fa0787d3e80858a27015b09a85eac2"
SOURCE="https://github.com/"+REPO+"/issues/400#issuecomment-12345"
ISSUE_URL="https://github.com/"+REPO+"/issues/400"

def pinned_data(parent=PARENT):
    return {"schema":"v36.issue-receipt-stream/v1","parent":parent,
            "events":[{"id":"EV-0001","source_ref":SOURCE,
                       "visibility":"PUBLIC_SAFE"}]}

def make_index(blob):
    return {"schema":"v36.live-issue-index/v1","parent":PARENT,
            "source_cut":{"repository":REPO,"branch":"main","revision":MAIN},
            "index_actor_claim":"reallakshman19",
            "references":[{"id":"OWNER_SOURCE","kind":"ISSUE_COMMENT",
              "repository":REPO,"revision":None,"path":None,"blob_sha1":None,
              "issue_number":400,"comment_id":12345,
              "claimed_actor":"reallakshman19","schema":None},
              {"id":"C1B_SOURCE","kind":"PINNED_JSON","repository":REPO,
               "revision":"a"*40,
               "path":"fixture.json",
               "blob_sha1":sp.hashlib.sha1(
                    b"blob "+str(len(blob)).encode()+bytes([0])+blob).hexdigest(),
               "issue_number":None,"comment_id":None,"claimed_actor":None,
               "schema":"v36.issue-receipt-stream/v1"}]}

def index_body(idx):
    return (sp.MARKER.format(PARENT)+"\n"+chr(96)*3+"json\n"+
            json.dumps(idx,separators=(",",":"))+"\n"+chr(96)*3+"\n")

class Fake:
    def __init__(self):
        self.data=pinned_data()
        self.blob=json.dumps(self.data).encode()
        self.idx=make_index(self.blob)
        self.index_author="reallakshman19"
        self.owner_actor="reallakshman19"
        self.index_duplicate=False
        self.index_missing=False
        self.main=MAIN
        self.fail_blob=False
    def get(self,path):
        if path=="/repos/"+REPO+"/issues/400":
            return {"number":400,"title":"Source-first issue"}
        if "/issues/400/comments?" in path:
            if self.index_missing:return []
            comment={"id":8080,"user":{"login":self.index_author},
                     "body":index_body(self.idx)}
            return [comment,dict(comment,id=8081)] if self.index_duplicate else [comment]
        if path=="/repos/"+REPO+"/issues/comments/12345":
            return {"id":12345,"issue_url":"https://api.github.com/repos/"+REPO+"/issues/400",
                    "user":{"login":self.owner_actor},"body":"Owner requirements reported"}
        if path=="/repos/"+REPO+"/branches/main":
            return {"commit":{"sha":self.main}}
        if "/contents/fixture.json?" in path:
            return {"type":"file","sha":self.idx["references"][1]["blob_sha1"],
                    "encoding":"base64","content":base64.b64encode(
                        self.blob if not self.fail_blob else b"BAD").decode()}
        raise sp.SpineError("UNEXPECTED_FAKE_PROVIDER_REQUEST:"+path)

class R2Tests(unittest.TestCase):
    def test_one_issue_cold_read_resolves_both_provider_objects(self):
        a=sp.audit(ISSUE_URL,Fake())
        self.assertEqual(a["references_total"],2)
        self.assertEqual(a["references_observed"],2)
        self.assertEqual(a["versioned_contracts"][0]["source_refs_matched"],1)
        self.assertFalse(a["owner_accepted"])
        self.assertFalse(a["semantic_accepted"])
        self.assertFalse(a["may_publish"])
        self.assertFalse(a["may_count_for_o2"])
        self.assertFalse(a["may_change_titles_or_labels"])
        self.assertFalse(a["may_merge_or_release"])
        self.assertFalse(a["twelve_section_recovery_complete"])

    def test_missing_index_holds(self):
        f=Fake();f.index_missing=True
        with self.assertRaisesRegex(sp.SpineError,"INDEX_MISSING"):
            sp.audit(ISSUE_URL,f)

    def test_duplicate_managed_index_holds(self):
        f=Fake();f.index_duplicate=True
        with self.assertRaisesRegex(sp.SpineError,"INDEX_AMBIGUOUS"):
            sp.audit(ISSUE_URL,f)

    def test_fake_index_comment_actor_rejected(self):
        f=Fake();f.index_author="attacker"
        with self.assertRaisesRegex(sp.SpineError,"INDEX_ACTOR_CONTRADICTED"):
            sp.audit(ISSUE_URL,f)

    def test_owner_comment_actor_contradiction_is_not_counted(self):
        f=Fake();f.owner_actor="attacker"
        a=sp.audit(ISSUE_URL,f)
        self.assertEqual(a["references_observed"],1)
        self.assertIn("OWNER_SOURCE",a["missing_or_contradicted"])
        self.assertIn("HOLD",a["status"])

    def test_source_cut_move_is_not_current(self):
        f=Fake();f.main="d"*40
        a=sp.audit(ISSUE_URL,f)
        self.assertFalse(a["source_cut_current"])
        self.assertIn("HOLD",a["status"])

    def test_tampered_git_blob_is_not_provider_verified(self):
        f=Fake();f.fail_blob=True
        a=sp.audit(ISSUE_URL,f)
        self.assertEqual(a["references_observed"],1)
        self.assertIn("C1B_SOURCE",a["missing_or_contradicted"])

    def test_c1b_foreign_parent_does_not_enter_issue_history(self):
        f=Fake()
        f.data=pinned_data("reallakshman19/3D_Converters#274")
        f.blob=json.dumps(f.data).encode()
        f.idx=make_index(f.blob)
        a=sp.audit(ISSUE_URL,f)
        self.assertIn("C1B_SOURCE",a["missing_or_contradicted"])

    def test_unsafe_path_refusal(self):
        f=Fake();f.idx["references"][1]["path"]="../../wrong.json"
        with self.assertRaisesRegex(sp.SpineError,"UNSAFE_SOURCE_PATH"):
            sp.audit(ISSUE_URL,f)

    def test_foreign_reference_repo_refusal(self):
        f=Fake();f.idx["references"][1]["repository"]="attacker/repository"
        with self.assertRaisesRegex(sp.SpineError,"FOREIGN_REFERENCE"):
            sp.audit(ISSUE_URL,f)

    def test_no_non_github_issue_url(self):
        for url in ("https://github.com.evil.test/"+REPO+"/issues/400",
                    "http://github.com/"+REPO+"/issues/400",
                    ISSUE_URL+"?admin=true",ISSUE_URL+"#token"):
            with self.assertRaisesRegex(sp.SpineError,"BAD_ISSUE_URL"):
                sp.parse(url)

    def test_wrong_json_schema_is_rejected(self):
        f=Fake();f.idx["schema"]="v36.fake/v1"
        with self.assertRaisesRegex(sp.SpineError,"WRONG_PARENT"):
            sp.audit(ISSUE_URL,f)

    def test_c1_cross_parent_not_treated_as_same_issue(self):
        f=Fake()
        f.data={"schema":"v36.issue-continuity-chain/v1",
                "parent":"reallakshman19/3D_Converters#274","records":[]}
        f.blob=json.dumps(f.data).encode()
        f.idx=make_index(f.blob)
        f.idx["references"][1]["schema"]="v36.issue-continuity-chain/v1"
        a=sp.audit(ISSUE_URL,f)
        self.assertIn("C1_FOREIGN_PARENT_EXAMPLE",
                      a["versioned_contracts"][0]["status"])
        self.assertEqual(a["verified_chain_categories"],0)

    def test_c2_manifest_is_reference_not_reverified_artifacts(self):
        f=Fake()
        f.data={"schema":"v36.source-custody/v1",
                "repository":"reallakshman19/3D_Converters",
                "artifacts":[{"id":"partial"},{"id":"negative"}]}
        f.blob=json.dumps(f.data).encode()
        f.idx=make_index(f.blob)
        f.idx["references"][1]["schema"]="v36.source-custody/v1"
        a=sp.audit(ISSUE_URL,f)
        self.assertEqual(a["versioned_contracts"][0]["artifact_claims"],2)
        self.assertIn("NOT_REATTESTED",a["versioned_contracts"][0]["status"])
        self.assertFalse(a["complete_golden_accepted"])

    def test_read_only_stdlib_imports(self):
        import ast
        p=(ROOT/"scripts/issue_spine_read_v36.py").read_text(encoding="utf-8")
        names=set()
        for n in ast.walk(ast.parse(p)):
            if isinstance(n,ast.Import):
                names.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n,ast.ImportFrom):
                names.add((n.module or "").split(".")[0])
        self.assertTrue(names<={"__future__","argparse","base64","hashlib",
                               "json","os","re","urllib"})

if __name__=="__main__":
    unittest.main()
