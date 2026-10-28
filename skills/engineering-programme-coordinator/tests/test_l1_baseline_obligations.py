#!/usr/bin/env python3
from __future__ import annotations
import copy, subprocess, sys, tempfile, unittest
from pathlib import Path
import yaml
SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from l1_baseline_obligations import compile_source, extract_precommitted_source, manifest_digest, resolve_pointer, validate_manifest, validate_source, validate_stored

class L1BaselineObligationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.repo=Path(self.tmp.name); (self.repo/"contracts").mkdir()
        (self.repo/"contracts/source.yaml").write_text("additionalProperties: false\nproperties:\n  authority:\n    const: CHILD_CONTRACT_PROJECTION\n",encoding="utf-8")
        (self.repo/"contracts/manifest.yaml").write_text("properties:\n  authority:\n    const: FROZEN_PREIMPLEMENTATION_EXPECTATIONS\n  authority_boundaries:\n    properties:\n      consumes_candidate_state:\n        const: false\n",encoding="utf-8")
        subprocess.run(["git","init"],cwd=self.repo,check=True,capture_output=True)
        subprocess.run(["git","config","user.email","test@example.com"],cwd=self.repo,check=True)
        subprocess.run(["git","config","user.name","Test"],cwd=self.repo,check=True)
        subprocess.run(["git","add","."],cwd=self.repo,check=True)
        subprocess.run(["git","commit","-m","baseline"],cwd=self.repo,check=True,capture_output=True)
        self.base=subprocess.check_output(["git","rev-parse","HEAD"],cwd=self.repo,text=True).strip()
        self.source={"schema_version":"L1_BASELINE_SOURCE_V1","authority":"BASELINE_SELECTION_CONTRACT","identity":{"programme_or_parent_id":"TEST","parent_ref":"issue://1","task_id":"PRD-TEST-L1","child_ref":"issue://2","contract_version":"v1"},"base":{"ref":"main","sha":self.base},"selectors":[{"id":"L1-A","severity":"CRITICAL","preservation_kind":"PRESERVATION","path":"contracts/source.yaml","pointer":"/additionalProperties","evidence_requirement":{"id":"REQ-A","method":"SCHEMA_CHECK"}},{"id":"L1-B","severity":"CRITICAL","preservation_kind":"AUTHORITY","path":"contracts/manifest.yaml","pointer":"/properties/authority/const","evidence_requirement":{"id":"REQ-B","method":"SCHEMA_CHECK"}}],"forbidden_outcomes":["candidate input"],"non_goals":["L2"]}
    def tearDown(self): self.tmp.cleanup()
    def test_deterministic_exact_base_replay(self):
        a=compile_source(self.source,self.repo); b=compile_source(self.source,self.repo)
        self.assertEqual(a,b); self.assertEqual(False,a["obligations"][0]["baseline_observation"]["value"]); self.assertEqual([],validate_stored(self.source,a,self.repo))
    def test_working_tree_change_cannot_change_declared_base(self):
        a=compile_source(self.source,self.repo); (self.repo/"contracts/source.yaml").write_text("additionalProperties: true\n",encoding="utf-8"); self.assertEqual(a,compile_source(self.source,self.repo))
    def test_new_base_value_changes_obligation(self):
        a=compile_source(self.source,self.repo); (self.repo/"contracts/source.yaml").write_text("additionalProperties: true\nproperties:\n  authority:\n    const: CHILD_CONTRACT_PROJECTION\n",encoding="utf-8")
        subprocess.run(["git","add","."],cwd=self.repo,check=True); subprocess.run(["git","commit","-m","new"],cwd=self.repo,check=True,capture_output=True)
        s=copy.deepcopy(self.source); s["base"]["sha"]=subprocess.check_output(["git","rev-parse","HEAD"],cwd=self.repo,text=True).strip(); b=compile_source(s,self.repo)
        self.assertNotEqual(a["obligations"][0]["baseline_observation"]["value_digest"],b["obligations"][0]["baseline_observation"]["value_digest"])
    def test_missing_pointer_fails_closed(self):
        s=copy.deepcopy(self.source); s["selectors"][0]["pointer"]="/not/here"
        with self.assertRaises(ValueError): compile_source(s,self.repo)
    def test_missing_base_fails_closed(self):
        s=copy.deepcopy(self.source); s["base"]["sha"]="0"*40
        with self.assertRaises(ValueError): compile_source(s,self.repo)
    def test_path_traversal_rejected(self):
        s=copy.deepcopy(self.source); s["selectors"][0]["path"]="../secret.yaml"; self.assertTrue(validate_source(s))
    def test_candidate_field_rejected(self):
        s=copy.deepcopy(self.source); s["candidate_sha"]="1"*40; self.assertTrue(validate_source(s))
    def test_diff_field_rejected(self):
        s=copy.deepcopy(self.source); s["diff"]={"files":[]}; self.assertTrue(validate_source(s))
    def test_duplicate_selector_ids_rejected(self):
        s=copy.deepcopy(self.source); s["selectors"][1]["id"]=s["selectors"][0]["id"]; self.assertTrue(validate_source(s))
    def test_duplicate_evidence_ids_rejected(self):
        s=copy.deepcopy(self.source); s["selectors"][1]["evidence_requirement"]["id"]="REQ-A"; self.assertTrue(validate_source(s))
    def test_impact_kind_rejected(self):
        s=copy.deepcopy(self.source); s["selectors"][0]["preservation_kind"]="IMPACT"; self.assertTrue(validate_source(s))
    def test_recomputed_tamper_digest_does_not_bypass_replay(self):
        m=compile_source(self.source,self.repo); m["obligations"][0]["claim"]["statement"]="forged"; m["manifest_digest"]=manifest_digest(m)
        self.assertTrue(any("fresh exact-base replay" in e for e in validate_stored(self.source,m,self.repo)))
    def test_authority_boundaries_and_evidence_independence(self):
        m=compile_source(self.source,self.repo); self.assertTrue(all(v is False for v in m["authority_boundaries"].values())); self.assertTrue(all(x["evidence_required"]["independence"]=="BASELINE_DERIVED" for x in m["obligations"]))
    def test_json_pointer_escaping(self): self.assertEqual(20,resolve_pointer({"a/b":{"~key":[10,20]}},"/a~1b/~0key/1"))
    def test_invalid_pointer_escape_rejected(self):
        with self.assertRaises(ValueError): resolve_pointer({"x":1},"/~2")
    def test_unbound_manifest_validation_fails_closed(self):
        manifest=compile_source(self.source,self.repo)
        errors=validate_manifest(manifest)
        self.assertTrue(any("source-bound exact-base replay is required" in e for e in errors))
    def test_generic_validator_requires_source_and_exact_repo(self):
        manifest=compile_source(self.source,self.repo)
        source_path=self.repo/"l1-source.yaml"
        manifest_path=self.repo/"l1-manifest.yaml"
        source_path.write_text(yaml.safe_dump(self.source,sort_keys=False),encoding="utf-8")
        manifest_path.write_text(yaml.safe_dump(manifest,sort_keys=False),encoding="utf-8")
        unbound=subprocess.run(
            [sys.executable,str(SCRIPTS/"validate.py"),"l1-baseline-obligation-manifest",str(manifest_path)],
            cwd=self.repo,capture_output=True,text=True,
        )
        self.assertNotEqual(0,unbound.returncode)
        self.assertIn("source-bound exact-base replay is required",unbound.stdout)
        bound=subprocess.run(
            [sys.executable,str(SCRIPTS/"validate.py"),"l1-baseline-obligation-manifest",str(manifest_path),"--l1-source",str(source_path),"--repo-root",str(self.repo)],
            cwd=self.repo,capture_output=True,text=True,
        )
        self.assertEqual(0,bound.returncode,bound.stdout+bound.stderr)
    def test_extracts_precommitted_issue_source(self):
        md = (
            "# Child\n\n"
            "## Precommitted L1 selector source\n\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        self.assertEqual(self.source, extract_precommitted_source(md))
    def test_duplicate_precommitted_heading_rejected(self):
        block = (
            "## Precommitted L1 selector source\n"
            "```yaml\n"
            + yaml.safe_dump(self.source, sort_keys=False)
            + "```\n"
        )
        with self.assertRaises(ValueError):
            extract_precommitted_source(block + block)
if __name__=="__main__": unittest.main()
