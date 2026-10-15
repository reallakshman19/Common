"""Synthetic offline WP1b custody/decision tests; no source provider calls."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("custody_contract", root / "scripts" / "validate_custody.py")
m = importlib.util.module_from_spec(s)
sys.modules[s.name] = m
s.loader.exec_module(m)

C = {"schema":"onboarding.custody/v1","id":"S1","repository":"acme/app",
     "source_url":"https://github.com/acme/app/blob/" + "a"*40 + "/Benchmark/S1.CII",
     "source_revision":"a"*40,"path":"Benchmark/S1.CII","role":"ORIGINAL_INPUT",
     "claimed_sha256":None,"verification":"CLAIMED_ONLY","authority":"ISSUE_DECLARATION","visibility":"PUBLIC"}
E = {"schema":"onboarding.experiment/v1","id":"run-1","repository":"acme/app","candidate_sha":"a"*40,
     "input_ids":["S1"],"command":"pytest tests/test_example.py","expected":"zero false matches",
     "observed":None,"status":"NOT_RUN","oracle_class":"SYNTHETIC","proof_url":None}
D = {"schema":"onboarding.decision/v1","id":"D-1","repository":"acme/app",
     "statement":"Keep original source custody unchanged","actor_role":"OWNER",
     "disposition":"REPORTED_APPROVED","source_url":"https://github.com/acme/app/issues/2#issuecomment-10",
     "supersedes":[],"visibility":"PUBLIC"}
B = {"schema":"onboarding.custody-bundle/v1","custody":[C],"experiments":[E],"decisions":[D]}


class CustodyTests(unittest.TestCase):
    def fresh(self):
        return copy.deepcopy(B)

    def test_bundle_valid_but_not_authorized(self):
        v = m.validate_bundle(self.fresh())
        self.assertEqual(v["status"], "LOCAL_VALIDATION_ONLY")
        self.assertFalse(v["execution_authorized"])
        self.assertFalse(v["owner_approval_verified"])

    def test_canonical_digest_order_independent(self):
        self.assertEqual(m.digest({"a":1,"b":2}),m.digest({"b":2,"a":1}))

    def test_n05_issue_declared_original_not_verified(self):
        self.assertEqual(m.validate_custody(self.fresh()["custody"][0])["verification"], "CLAIMED_ONLY")

    def test_bytes_digest_is_strict_and_not_owner_acceptance(self):
        b=self.fresh();c=b["custody"][0]
        import hashlib
        c["claimed_sha256"]=hashlib.sha256(b"original").hexdigest()
        self.assertEqual(m.verify_bytes(c,b"original")["comparison"],"SUPPLIED_BYTES_MATCH")
        self.assertFalse(m.verify_bytes(c,b"original")["semantic_owner_acceptance"])
        self.assertEqual(m.verify_bytes(c,b"changed")["comparison"],"SUPPLIED_BYTES_MISMATCH")

    def test_self_asserted_verified_rejected(self):
        b=self.fresh();b["custody"][0]["verification"]="BYTES_VERIFIED"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_unclaimed_original_bytes_never_count_as_matching(self):
        observation=m.verify_bytes(self.fresh()["custody"][0],b"original")
        self.assertEqual(observation["comparison"],"UNCLAIMED_BYTES")
        self.assertFalse(observation["source_git_blob_verified"])
        self.assertFalse(observation["provider_authenticated"])

    def test_caller_claimed_mismatch_not_admitted_as_observed_status(self):
        b=self.fresh();b["custody"][0]["verification"]="MISMATCH"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_hash_match_is_not_provider_source_attestation(self):
        b=self.fresh();c=b["custody"][0]
        import hashlib
        c["claimed_sha256"]=hashlib.sha256(b"original").hexdigest()
        observed=m.verify_bytes(c,b"original")
        self.assertEqual(observed["schema"],"onboarding.supplied-byte-comparison/v1")
        self.assertEqual(observed["comparison"],"SUPPLIED_BYTES_MATCH")
        self.assertFalse(observed["source_git_blob_verified"])
        self.assertFalse(observed["provider_authenticated"])
        self.assertFalse(observed["semantic_owner_acceptance"])
        self.assertFalse(observed["execution_authorized"])

    def test_observation_schema_fields_are_exact(self):
        b=self.fresh()
        observed=m.verify_bytes(b["custody"][0],b"untrusted")
        import json
        schema=json.loads((root/"schemas"/"supplied-byte-comparison.v1.schema.json").read_text())
        self.assertEqual(set(schema["required"]),set(observed))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["schema"]["const"],observed["schema"])
        claimed=json.loads((root/"schemas"/"custody.v1.schema.json").read_text())
        self.assertNotIn("BYTES_VERIFIED",claimed["properties"]["verification"]["enum"])
        self.assertNotIn("MISMATCH",claimed["properties"]["verification"]["enum"])

    def test_source_traversal_link_not_authoritative(self):
        b=self.fresh();b["custody"][0]["source_url"]="https://github.com/acme/app/blob/../secrets"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_path_traversal_rejected(self):
        b=self.fresh();b["custody"][0]["path"]="../secret"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_source_wrong_host_rejected(self):
        b=self.fresh();b["custody"][0]["source_url"]="https://github.com@evil.test/acme/app/blob/file"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_cross_repo_source_rejected(self):
        b=self.fresh();b["custody"][0]["source_url"]="https://github.com/other/app/blob/main/file"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_cross_repo_fixture_not_accepted(self):
        b=self.fresh();b["experiments"][0]["repository"]="acme/other"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_n08_notrun_cannot_have_observation(self):
        b=self.fresh();b["experiments"][0]["observed"]="all pass"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_n08_notrun_cannot_claim_ci_proof(self):
        b=self.fresh();b["experiments"][0]["proof_url"]="https://github.com/acme/app/actions/runs/100"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_no_false_pass_without_proof(self):
        b=self.fresh();b["experiments"][0]["status"]="PASS";b["experiments"][0]["observed"]="pass"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_issue_owner_claim_is_not_independent_verification(self):
        v=m.validate_bundle(self.fresh())
        self.assertFalse(v["owner_approval_verified"])

    def test_unknown_decision_has_no_source(self):
        b=self.fresh();d=b["decisions"][0];d.update({"disposition":"UNKNOWN","source_url":None,"actor_role":"UNKNOWN"})
        self.assertEqual(m.validate_bundle(b)["decision_count"],1)

    def test_unknown_decision_ref_rejected(self):
        b=self.fresh();d=b["decisions"][0];d.update({"disposition":"UNKNOWN","actor_role":"UNKNOWN"})
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_non_owner_cannot_claim_approved(self):
        b=self.fresh();b["decisions"][0]["actor_role"]="ENGINEER"
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_duplicate_decision_refused(self):
        b=self.fresh();b["decisions"].append(copy.deepcopy(D))
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_self_supersession_refused(self):
        b=self.fresh();b["decisions"][0]["supersedes"]=["D-1"]
        with self.assertRaises(m.InvalidReceipt):m.validate_bundle(b)

    def test_same_id_different_repository_is_distinct(self):
        b=self.fresh();d=copy.deepcopy(D);d["repository"]="acme/other";d["source_url"]="https://github.com/acme/other/issues/2"
        b["decisions"].append(d)
        self.assertEqual(m.validate_bundle(b)["decision_count"],2)


if __name__=="__main__":
    unittest.main()
