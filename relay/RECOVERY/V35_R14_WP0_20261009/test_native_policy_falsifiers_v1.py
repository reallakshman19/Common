"""V3.5 WP0: native, read-only, source-level evidence-policy counterexamples.

These tests use actual Common Python modules, not reimplemented P/E formulas.
Their graph/facts are synthetic, not native GitHub provider attestation.
A passing result proves a policy divergence and strict schema boundary,
NOT an approved programme policy, independent review or DELP bridge.
"""
from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
SHA_A = "a" * 40
SHA_B = "b" * 40
SOURCE = "SYNTHETIC_FIXTURE#TASK_EVIDENCE"
REF = "Common#860#issuecomment-1"


def load_actual(name: str, relative_path: str):
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"MISSING_NATIVE_MODULE:{relative_path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"UNLOADABLE_NATIVE_MODULE:{relative_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


V32 = load_actual("v32_wp0_real", "skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py")
V35 = load_actual("v35_wp0_real", "skills/engineering-pr-delivery-v3.5/scripts/delp_projection_v35.py")
CONT = load_actual("continuity_wp0_real", "skills/engineering-pr-delivery-v3.2/scripts/continuity_projection.py")


def graph():
    return {
        "schema": V32.GRAPH_SCHEMA,
        "programme": {"id": "WP0-SYNTHETIC-POLICY-FALSIFIER", "root": "Common#787"},
        "nodes": [
            {"ref": "Common#787", "kind": "ROOT"},
            {"ref": "Common#860", "kind": "LEAF", "parent": "Common#787",
             "weight": 1, "primary_pr": "Common#861",
             "units": [{"id": "U01", "weight": 1}]},
        ],
    }


def fact(result="FAILED", candidate=SHA_A):
    return {
        "schema": V32.FACTS_SCHEMA,
        "responsibility": {"issue": "Common#860"},
        "material": {"pr": "Common#861", "candidate_sha": candidate},
        "units": [{"id": "U01", "state": "COMPLETE", "result": result,
                   "evidence_refs": [REF], "candidate_sha": candidate}],
    }


def delp_projection(result="FAILED", claimed=SHA_A, observed=SHA_A, *, untrusted=None):
    record = fact(result, claimed)
    errors = V32.validate_facts(record)
    if errors:
        raise AssertionError(f"INVALID_FIXTURE:{errors}")
    entry = {"source": SOURCE, "order": 1, "facts": record}
    if untrusted:
        entry["untrusted_author"] = untrusted
    return V32.project(graph(), [entry],
                       {"Common#860": {"candidate_sha": observed}})


def continuity_projection(result="FAILED", claimed=SHA_A, observed=SHA_A):
    return CONT.progress([{
        "id": "U01", "weight": 1, "complete": True,
        "result": result, "evidence_refs": [REF],
        "evidence_candidate": claimed,
    }], derived=True, material_head=observed)


class NativeEvidencePolicyFalsifiers(unittest.TestCase):
    def test_c1_failed_complete_evidence_drift_is_real(self):
        """Continuity E100 versus DELP E0 for the semantically mapped FAILED unit."""
        legacy = continuity_projection("FAILED")
        leaf = delp_projection("FAILED")["nodes"]["Common#860"]
        self.assertEqual((100, 100),
                         (legacy["progress_percent"], legacy["evidence_percent"]))
        self.assertEqual((100, 0), (leaf["progress"]["P"], leaf["progress"]["E"]))
        self.assertTrue(any("RESULT_NOT_ACCEPTED(FAILED)" in str(gap)
                            for gap in leaf["evidence"]["gaps"])
                        if isinstance(leaf.get("evidence"), dict) and
                        isinstance(leaf["evidence"].get("gaps"), list)
                        else any("RESULT_NOT_ACCEPTED(FAILED)" in str(x)
                                 for x in leaf.values()), leaf)
        print("WP0_C1_CONTINUITY_FAILED_E100_DELP_FAILED_E0")

    def test_c1_positive_verified_is_not_always_zero(self):
        """Positive control on SAME graph and actual DELP projector."""
        leaf = delp_projection("VERIFIED")["nodes"]["Common#860"]
        self.assertEqual((100, 100), (leaf["progress"]["P"], leaf["progress"]["E"]))
        print("WP0_POSITIVE_VERIFIED_CURRENT_E100")

    def test_c1_stale_verified_evidence_is_not_current(self):
        """Negative control on candidate H1→H2 for BOTH calculators."""
        legacy = continuity_projection("VERIFIED", claimed=SHA_A, observed=SHA_B)
        leaf = delp_projection("VERIFIED", claimed=SHA_A, observed=SHA_B)["nodes"]["Common#860"]
        self.assertEqual(0, legacy["evidence_percent"])
        self.assertEqual((100, 0), (leaf["progress"]["P"], leaf["progress"]["E"]))
        print("WP0_STALE_HEAD_H1_TO_H2_E0")

    def test_c2_v35_responsibility_contract_is_not_v32_fact_schema(self):
        """The same fenced marker does not imply identical fact validation semantics."""
        record = {
            "responsibility": {
                "issue": "Common#860", "spec_generation": 2,
                "contract_digest": "sha256:" + "b" * 64,
            },
            "material": {"pr": "Common#861", "candidate_sha": SHA_A},
            "units": [{"id": "U01", "state": "COMPLETE", "result": "VERIFIED",
                       "evidence_refs": [REF], "candidate_sha": SHA_A}],
        }
        errors32 = V32.validate_facts(record)
        errors35 = V35.validate_facts(record)
        self.assertTrue(any("responsibility" in x and "unknown" in x.lower()
                            for x in errors32), errors32)
        self.assertEqual([], errors35)
        self.assertNotEqual(V32.FACTS_SCHEMA, V35.FACTS_SCHEMA)
        explicit35 = {**record, "schema": V35.FACTS_SCHEMA}
        explicit32 = {**record, "schema": V32.FACTS_SCHEMA}
        self.assertEqual([], V35.validate_facts(explicit35))
        self.assertTrue(V32.validate_facts(explicit32))
        self.assertTrue(any("schema" in x for x in V32.validate_facts(explicit35)))
        print("WP0_C2_TYPED_FACT_SCHEMA_INCOMPATIBILITY")

    def test_rejected_untrusted_producer_does_not_mint_evidence(self):
        """Positive structural fact is not enough with untrusted author metadata."""
        result = delp_projection("VERIFIED", untrusted="attacker")
        leaf = result["nodes"]["Common#860"]
        self.assertEqual((0, 0), (leaf["progress"]["P"], leaf["progress"]["E"]))
        self.assertTrue(result["rejected_facts"], result)
        print("WP0_UNTRUSTED_AUTHOR_P0_E0")


if __name__ == "__main__":
    unittest.main(verbosity=2)
