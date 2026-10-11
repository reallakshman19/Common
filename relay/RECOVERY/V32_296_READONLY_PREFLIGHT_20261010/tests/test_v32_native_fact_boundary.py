"""Executable RED trust-boundary evidence against the actual native V3.2 DELP.

Important: these tests demonstrate *structural* facts/ledger acceptance and the
need for an independent producer/provider eligibility seam. They are not
evidence that any source or reference was independently admitted, and they
MUST NOT be used to drive production E, a publisher, or C6 acceptance.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

PROBE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROBE_ROOT))

from v32_admission_probe import ObservedCheck, SourceSelection, probe_v32_fact

NATIVE_SOURCE = (
    REPOSITORY_ROOT / "skills" / "engineering-pr-delivery-v3.2" /
    "scripts" / "delp_projection_v32.py"
)
spec = importlib.util.spec_from_file_location("v32_native_delp_for_non_admission_oracle", NATIVE_SOURCE)
if spec is None or spec.loader is None:
    raise RuntimeError("NATIVE_DELP_NOT_PRESENT")
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)

HEAD = "a" * 40
REPOSITORY = "reallakshman19/Common"
LEAF = "Common#733"


def native_shaped_fact():
    # Native schema and material.pr are both optional on the actual V3.2
    # validator. They cannot be made compulsory in a preflight classifier.
    return {
        "responsibility": {"issue": LEAF, "id": "R-PROOF"},
        "material": {"candidate_sha": HEAD},
        "units": [{
            "id": "U01", "state": "COMPLETE", "result": "VERIFIED",
            # This source ref has NOT been fetched/independently verified.
            "evidence_refs": ["Common#733#issuecomment-999"],
        }],
    }


def selected():
    return SourceSelection(
        repository=REPOSITORY, leaf_ref=LEAF, pr_number=740,
        current_head=HEAD, observed_pr_repository=REPOSITORY,
        observed_pr_number=740,
        # Even caller assertions of VERIFIED are NOT authentication.
        original_source_state="VERIFIED", released_graph_state="VERIFIED",
        evidence_policy_state="VERIFIED", required_check_policy_state="VERIFIED",
        independent_review_state="VERIFIED",
    )


def green_selected_check():
    return [ObservedCheck("selected-build", HEAD, "success", True)]


class NativeV32SeamTests(unittest.TestCase):
    def test_01_optional_schema_and_material_pr_are_native_valid(self):
        self.assertEqual(native.validate_facts(native_shaped_fact()), [])

    def test_02_structurally_valid_native_fact_does_not_become_probe_failure(self):
        report = probe_v32_fact(selected(), native_shaped_fact(), green_selected_check())
        self.assertEqual(report.state, "HOLD_NOT_AN_EVIDENCE_ISSUER")
        self.assertIsNone(report.accepted_evidence_count)
        self.assertFalse(report.writer_authorized)
        self.assertFalse(report.delp_invoked)

    def test_03_native_ledger_accepts_structural_claim_without_provider_admission(self):
        f = native_shaped_fact()
        # This is a *synthetic* local fixture, not a released graph or
        # qualified actual GitHub issue/CI/reviewer/source history.
        indexed = {"nodes": {
            LEAF: {"kind": "LEAF", "number": 733, "responsibility_id": "R-PROOF"},
        }}
        accepted, rejected = native.partition_ledger(
            indexed, [{"source": LEAF + "#issuecomment-999", "order": 999, "facts": f}]
        )
        self.assertEqual(rejected, [])
        self.assertEqual(len(accepted[LEAF]), 1)
        # The native ledger structural check is distinct from external
        # evidence eligibility: an author-controlled reference is not proof.
        report = probe_v32_fact(selected(), f, green_selected_check())
        self.assertEqual(report.state, "HOLD_NOT_AN_EVIDENCE_ISSUER")
        self.assertIsNone(report.as_dict()["accepted_evidence_count"])

    def test_04_cross_version_v35_fact_must_not_be_normalized_into_v32(self):
        f = native_shaped_fact()
        f["schema"] = "relay-v3.5-delp-checkpoint-facts"
        self.assertTrue(native.validate_facts(f))
        report = probe_v32_fact(selected(), f, green_selected_check())
        self.assertEqual(report.state, "FAILED")
        self.assertIn("FACT_SCHEMA_NOT_NATIVE_V32", report.reasons)


if __name__ == "__main__":
    unittest.main()
