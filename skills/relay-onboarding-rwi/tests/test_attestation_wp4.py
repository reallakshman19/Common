"""WP4: synthetic source object and negative custody oracles. No network."""
import base64
import copy
import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("wp4_git",ROOT/"attestation"/"git_bytes.py")
g=importlib.util.module_from_spec(spec);sys.modules[spec.name]=g;spec.loader.exec_module(g)
DATA=b"first\r\nsecond\nthird\n"
BLOB=g.blob_id(DATA)
C="a"*40; T="b"*40; SUB="c"*40
REPO="acme/app"
PATH="fixtures/S1.CII"
EXPECTED=hashlib.sha256(DATA).hexdigest()

class Fake:
    def __init__(self):
        self.calls=[]
        self.objects={
            ("commits",C):{"sha":C,"tree":{"sha":T}},
            ("trees",T):{"sha":T,"truncated":False,"tree":[{"path":"fixtures","type":"tree","sha":SUB,"mode":"040000"}]},
            ("trees",SUB):{"sha":SUB,"truncated":False,"tree":[{"path":"S1.CII","type":"blob","sha":BLOB,"mode":"100644"}]},
            ("blobs",BLOB):{"sha":BLOB,"size":len(DATA),"encoding":"base64","content":base64.b64encode(DATA).decode()}
        }
    def get_object(self,repo,kind,oid):
        self.calls.append((repo,kind,oid))
        if repo!=REPO: raise AssertionError("wrong requested repo")
        return copy.deepcopy(self.objects[(kind,oid)])

class AttestationTests(unittest.TestCase):
    def fake(self):return Fake()
    def run_case(self,p=None,claimed=EXPECTED):
        return g.verify(p or self.fake(),REPO,C,PATH,claimed)
    def test_byte_match_under_pinned_tree(self):
        v=self.run_case()
        self.assertEqual(v["comparison"],"MATCH")
        self.assertEqual(v["blob_oid"],BLOB)
        self.assertFalse(v["execution_authorized"])
        self.assertFalse(v["owner_approval_verified"])
    def test_no_claim_is_not_owner_match(self):
        self.assertEqual(self.run_case(claimed=None)["comparison"],"NO_OWNER_HASH")
    def test_wrong_declared_hash_mismatch(self):
        self.assertEqual(self.run_case(claimed="1"*64)["comparison"],"MISMATCH")
    def test_wrong_blob_bytes_fail(self):
        f=self.fake();f.objects[("blobs",BLOB)]["content"]=base64.b64encode(b"modified").decode()
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_wrong_blob_size_fail(self):
        f=self.fake();f.objects[("blobs",BLOB)]["size"]=len(DATA)+1
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_fake_base64_fail(self):
        f=self.fake();f.objects[("blobs",BLOB)]["content"]="!!!"
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_blob_wrong_id_fail(self):
        f=self.fake();f.objects[("blobs",BLOB)]["sha"]="f"*40
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_commit_wrong_id_fail(self):
        f=self.fake();f.objects[("commits",C)]["sha"]="f"*40
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_tree_wrong_sha_fail(self):
        f=self.fake();f.objects[("trees",T)]["sha"]="f"*40
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_truncated_tree_fail(self):
        f=self.fake();f.objects[("trees",T)]["truncated"]=True
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_missing_tree_member_fail(self):
        f=self.fake();f.objects[("trees",SUB)]["tree"]=[]
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_ambiguous_tree_member_fail(self):
        f=self.fake();item=f.objects[("trees",SUB)]["tree"][0]
        f.objects[("trees",SUB)]["tree"].append(item)
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_symlink_not_trusted(self):
        f=self.fake();f.objects[("trees",SUB)]["tree"][0]["mode"]="120000"
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_submodule_not_trusted(self):
        f=self.fake();f.objects[("trees",SUB)]["tree"][0]["type"]="commit"
        with self.assertRaises(g.AttestationError):self.run_case(f)
    def test_wrong_repo_fail_before_provider(self):
        f=self.fake()
        with self.assertRaises(g.AttestationError):g.verify(f,"acme/app/other",C,PATH)
        self.assertEqual(f.calls,[])
    def test_malformed_sha_fail_before_provider(self):
        f=self.fake()
        with self.assertRaises(g.AttestationError):g.verify(f,REPO,"main",PATH)
        self.assertEqual(f.calls,[])
    def test_traversal_fail_before_provider(self):
        for path in ("../.env","fixtures/../secret","/tmp/secret","fixtures//x","fixtures/%2e%2e/s"):
            f=self.fake()
            with self.subTest(path=path),self.assertRaises(g.AttestationError):
                g.verify(f,REPO,C,path)
            self.assertEqual(f.calls,[])
    def test_line_digest_exact_original_newlines(self):
        result=g.verify(self.fake(),REPO,C,PATH,EXPECTED,2,2)
        self.assertEqual(result["line_sha256"],hashlib.sha256(b"second\n").hexdigest())
    def test_line_range_out_of_bounds(self):
        with self.assertRaises(g.AttestationError):g.verify(self.fake(),REPO,C,PATH,EXPECTED,5,8)
    def test_bool_line_number_rejected(self):
        with self.assertRaises(g.AttestationError):g.verify(self.fake(),REPO,C,PATH,EXPECTED,True,1)
    def test_one_sided_line_selection_rejected(self):
        with self.assertRaises(g.AttestationError):g.verify(self.fake(),REPO,C,PATH,EXPECTED,1,None)
    def test_no_semantic_promotion_on_match(self):
        r=self.run_case()
        for x in ("benchmark_complete","semantic_code_path_verified","owner_approval_verified","execution_authorized"):
            self.assertFalse(r[x])
    def test_api_only_git_object_types(self):
        class NoNetwork:
            def open(self,*a,**kw):raise AssertionError("network should not happen")
        cli=g.GitHubGet();cli.opener=NoNetwork()
        with self.assertRaises(g.AttestationError):cli.get_object(REPO,"pulls",C)
    def test_no_post_or_patch_transport(self):
        self.assertFalse(hasattr(g.GitHubGet(),"post"))
        self.assertFalse(hasattr(g.GitHubGet(),"patch"))
    def test_duplicate_file_basename_cross_repo_not_a_source(self):
        f=self.fake()
        with self.assertRaises(AssertionError):g.get_verified_bytes(f,"other/repo",C,PATH)
    def test_bounded_size_reject(self):
        f=self.fake();f.objects[("blobs",BLOB)]["size"]=g.MAX_SOURCE_BYTES+1
        with self.assertRaises(g.AttestationError):self.run_case(f)

if __name__=="__main__":unittest.main()
