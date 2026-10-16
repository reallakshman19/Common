"""C1/C1A integration: one spine authority, bounded read-only lineage and protocol view."""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import continuity_bridge_v36 as bridge

SAMPLE = ROOT / "tests" / "fixtures" / "issue-chain-274-reported.json"


class ContinuityBridgeTests(unittest.TestCase):
    def document(self):
        return json.loads(SAMPLE.read_text(encoding="utf-8"))

    def lineage(self):
        # One-node lineage anchored to the actual owning-issue identity.
        # This is a synthetic presentation fixture, not issue readback.
        return {
            "repository": "reallakshman19/3D_Converters",
            "nodes": [
                {"issue": 274, "parent": None, "state": "ACTIVE",
                 "reason": None, "decision_ref": None}
            ]
        }

    def test_reported_spine_remains_only_coverage_authority(self):
        result = bridge.project(self.document(), lineage=self.lineage())
        self.assertEqual(result["required_categories"], 11)
        self.assertEqual(result["reported_categories"], 7)
        self.assertEqual(result["verified_source_categories"], 0)
        self.assertEqual(result["lineage_status"], "REPORTED_NOT_PROVIDER_VERIFIED")
        self.assertFalse(result["may_publish"])
        self.assertFalse(result["may_count_for_native_o2"])
        self.assertFalse(result["may_grant_owner_acceptance"])
        self.assertFalse(result["permission_to_write"])

    def test_wrong_repo_blocks_advisory_lineage(self):
        lineage = self.lineage()
        lineage["repository"] = "other/repository"
        with self.assertRaisesRegex(bridge.BridgeError, "LINEAGE_REPOSITORY_MISMATCH"):
            bridge.project(self.document(), lineage=lineage)

    def test_wrong_root_issue_blocks_advisory_lineage(self):
        lineage = self.lineage()
        lineage["nodes"][0]["issue"] = 275
        with self.assertRaisesRegex(bridge.BridgeError, "LINEAGE_ROOT_ISSUE_MISMATCH"):
            bridge.project(self.document(), lineage=lineage)

    def test_404_cannot_become_proven_deletion(self):
        lineage = self.lineage()
        lineage["nodes"].append({
            "issue": 275, "parent": 274, "state": "NOT_FOUND_UNVERIFIED",
            "reason": "Not found is ambiguous between access restrictions and deletion",
            "decision_ref": None})
        result = bridge.project(self.document(), lineage=lineage)
        self.assertIn("NOT_FOUND_UNVERIFIED", result["reported_issue_lineage"])
        self.assertNotIn("~~[#275]", result["reported_issue_lineage"])
        self.assertEqual(result["verified_source_categories"], 0)

    def test_provenance_source_unchanged_by_bridge(self):
        document = self.document()
        preserved = copy.deepcopy(document)
        bridge.project(document, lineage=self.lineage())
        self.assertEqual(document, preserved)

    def test_governed_evidence_route_has_no_new_o2(self):
        result = bridge.project(self.document(), inspect_protocol=True,
                                governed_v36=True, has_issue=True)
        self.assertEqual(result["evidence_routing"]["mode"], "NATIVE_V36_REQUIRED")
        self.assertTrue(result["evidence_routing"]["required"])
        self.assertTrue(result["evidence_routing"]["does_not_create_evidence"])
        self.assertFalse(result["may_count_for_native_o2"])

    def test_ad_hoc_is_voluntary_not_posted(self):
        result = bridge.project(self.document(), inspect_protocol=True)
        self.assertEqual(result["evidence_routing"]["mode"], "OPTIONAL_ADHOC_ADVISORY")
        self.assertFalse(result["evidence_routing"]["may_publish"])
        self.assertFalse(result["may_publish"])

    def test_dual_native_and_foreign_project_protocol_is_hold(self):
        result = bridge.project(self.document(), inspect_protocol=True,
                                project_protocol="TASK EVIDENCE v2",
                                governed_v36=True)
        self.assertEqual(result["evidence_routing"]["mode"], "PROTOCOL_CONFLICT_HOLD")
        self.assertFalse(result["may_grant_owner_acceptance"])

    def test_external_project_protocol_without_native_binding_is_preserved(self):
        result = bridge.project(self.document(), inspect_protocol=True,
                                project_protocol="TASK EVIDENCE v2")
        self.assertEqual(result["evidence_routing"]["mode"], "PROJECT_PROTOCOL_REQUIRED")
        self.assertEqual(result["evidence_routing"]["protocol"], "TASK EVIDENCE v2")

    def test_an_invalid_11_category_claim_fails_before_view(self):
        document = self.document()
        document["chain"].pop()
        with self.assertRaisesRegex(bridge.spine.ChainError, "CHAIN_REQUIRED_CATEGORIES_MISSING"):
            bridge.project(document, lineage=self.lineage())


if __name__ == "__main__":
    unittest.main()
