"""B05/R2 shadow: REAL V3.2 DELP maths, SYNTHETIC inputs, ZERO evidence admission.

No native GitHub GET, Owner or independent reviewer receipt occurs here. These
executable calculations must never be published as real programme E, source
qualification, approved graph policy, a live issue title, or C6 custody.

This deliberately uses the existing DELP.project() implementation, not a local
calculator or a spoof of source-acquisition evidence.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
NATIVE_DELP = ROOT / "skills/engineering-pr-delivery-v3.2/scripts/delp_projection_v32.py"
H1 = "a" * 40
H2 = "b" * 40
LEAF = "Common#30"
ROOT_REF = "Common#5"
SYNTHETIC_SOURCE = "SYNTHETIC_NO_PROVIDER_RECEIPT"
SYNTHETIC_REF = "Common#30#issuecomment-999999999"

if not NATIVE_DELP.is_file():
    raise RuntimeError("NATIVE_V32_DELP_MISSING")
spec = importlib.util.spec_from_file_location("b05_shadow_actual_v32", NATIVE_DELP)
if spec is None or spec.loader is None:
    raise RuntimeError("NATIVE_V32_DELP_UNLOADABLE")
V32 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V32)


def graph() -> dict:
    """An intentionally unapproved, tiny test-only graph; never a released plan."""
    return {
        "schema": V32.GRAPH_SCHEMA,
        "programme": {
            "id": "B05-SYNTHETIC-SHADOW-NOT-RELEASED",
            "root": ROOT_REF,
        },
        "nodes": [
            {"ref": ROOT_REF, "kind": "ROOT"},
            {
                "ref": LEAF, "kind": "LEAF", "parent": ROOT_REF,
                "primary_pr": "Common#292", "weight": 1,
                "units": [{"id": "SOURCE-CHECK", "weight": 1}],
            },
        ],
    }


def facts(result: str = "VERIFIED", head: str = H1) -> dict:
    return {
        "schema": V32.FACTS_SCHEMA,
        "responsibility": {"issue": LEAF},
        "material": {"pr": "Common#292", "candidate_sha": head},
        "units": [{
            "id": "SOURCE-CHECK", "state": "COMPLETE",
            "result": result,
            "candidate_sha": head,
            # NOT a real GitHub comment; projector does not validate provenance.
            "evidence_refs": [SYNTHETIC_REF],
        }],
    }


def shadow(result="VERIFIED", claimed=H1, observed=H1,
           *, untrusted_author=None, source=SYNTHETIC_SOURCE, record=None):
    ledger_row = {
        "source": source,
        "order": 1,
        "facts": copy.deepcopy(record) if record is not None else facts(result, claimed),
    }
    if untrusted_author is not None:
        ledger_row["untrusted_author"] = untrusted_author
    # Pure, deterministic projection with caller-provided synthetic observation.
    return V32.project(graph(), [ledger_row],
                       {LEAF: {"candidate_sha": observed}})


class B05NativeV32ShadowOracles(unittest.TestCase):
    def setUp(self):
        self.assertEqual([], V32.validate_facts(facts()))
        self.assertEqual(V32.AUTHORITY, "DERIVED_PROJECTION_ONLY")

    def test_synthetic_current_verified_positive_calculation_only(self):
        leaf = shadow()["nodes"][LEAF]
        self.assertEqual((100, 100),
                         (leaf["progress"]["P"], leaf["progress"]["E"]))
        # This arithmetic says nothing about real provider/reviewer/Owner trust.
        self.assertEqual(V32.AUTHORITY, "DERIVED_PROJECTION_ONLY")

    def test_synthetic_failed_complete_preserves_p_and_drops_e(self):
        leaf = shadow(result="FAILED")["nodes"][LEAF]
        self.assertEqual((100, 0),
                         (leaf["progress"]["P"], leaf["progress"]["E"]))

    def test_synthetic_h1_to_h2_head_move_drops_stale_e(self):
        leaf = shadow(claimed=H1, observed=H2)["nodes"][LEAF]
        self.assertEqual((100, 0),
                         (leaf["progress"]["P"], leaf["progress"]["E"]))

    def test_synthetic_h2_refreshed_verification_can_restore_e(self):
        stale = shadow(claimed=H1, observed=H2)["nodes"][LEAF]
        refreshed = shadow(claimed=H2, observed=H2)["nodes"][LEAF]
        self.assertEqual(0, stale["progress"]["E"])
        self.assertEqual((100, 100),
                         (refreshed["progress"]["P"], refreshed["progress"]["E"]))

    def test_untrusted_author_blocks_even_structurally_verified_record(self):
        result = shadow(untrusted_author="UNTRUSTED_FIXTURE_ACTOR")
        leaf = result["nodes"][LEAF]
        self.assertEqual((0, 0),
                         (leaf["progress"]["P"], leaf["progress"]["E"]))
        self.assertTrue(result["rejected_facts"])

    def test_forged_agent_progress_field_is_invalid_fact(self):
        injected = facts()
        injected["progress_percent"] = 100
        self.assertTrue(V32.validate_facts(injected))
        result = shadow(record=injected)
        self.assertEqual((0, 0),
                         (result["nodes"][LEAF]["progress"]["P"],
                          result["nodes"][LEAF]["progress"]["E"]))
        self.assertTrue(result["rejected_facts"])

    def test_v35_fact_schema_is_not_silently_accepted_as_v32(self):
        incompatible = facts()
        incompatible["schema"] = "relay-v3.5-delp-checkpoint-facts"
        self.assertTrue(V32.validate_facts(incompatible))
        self.assertTrue(shadow(record=incompatible)["rejected_facts"])

    def test_synthetic_source_string_is_not_independently_authenticated(self):
        # Deliberate *gap* oracle: the pure projector does not perform a GET.
        # A fake source label is not proof of a current eligible GitHub comment.
        fake_old_repo = "https://github.com/reallaksh19/Common/issues/30#issuecomment-1"
        result = shadow(source=fake_old_repo)
        self.assertEqual(100, result["nodes"][LEAF]["progress"]["E"])
        self.assertEqual(V32.AUTHORITY, result["authority"])
        # Therefore the external trust/admission producer remains mandatory.


if __name__ == "__main__":
    unittest.main(verbosity=2)
