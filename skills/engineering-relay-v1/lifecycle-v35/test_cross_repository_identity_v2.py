"""WP1/U1 v2 proposal: real U1 validation plus cross-provider ref negatives.

All fixtures reference synthetic GitHub IDs. PASS proves contract-shape only.
No test calls GitHub, accepts TaskEvidence, or grants Owner/writer/reviewer.
"""
from __future__ import annotations
import copy
import unittest

from cross_repository_identity_v2 import (
    CrossRepositoryIdentityError,
    validate_crossrepo_identity_v2,
)

OLD = "reallaksh19/Common"
NEW = "reallakshman19/Common"
MAIN = "d60c36605e988dcc160647421973f170fd87e0eb"
A, B, C = "a" * 40, "b" * 40, "c" * 40
DIGEST = "sha256:" + "d" * 64


def fixture():
    return {
        "schema": "relay-lifecycle-cross-repository-identity-v2",
        "current_identity": {
            "schema": "relay-lifecycle-source-identity-v1",
            "programme": {"id": "RECOVERY-5-SYNTHETIC", "repository": NEW, "root_issue": 5},
            "owner_source_grade": "UNKNOWN",
            "graph_source": {
                "role": "PLAN_GRAPH_REVISION", "state": "REFERENCED",
                "repository": NEW, "revision_sha": A,
                "path": "relay/graph.yaml", "content_sha256": DIGEST,
            },
            "session_source": {
                "role": "SESSION_SOURCE_COMMIT", "state": "REFERENCED",
                "repository": NEW, "commit_sha": B,
            },
            "candidate_source": {
                "role": "CODE_CANDIDATE_HEAD", "state": "REFERENCED",
                "repository": NEW, "pr_number": 9, "head_sha": C, "base_sha": A,
            },
        },
        "historical_origin": {
            "repository_id": 1207996454, "repository": OLD, "kind": "ISSUE",
            "number": 787, "url": "https://github.com/reallaksh19/Common/issues/787",
            "source_grade": "HISTORICAL_SOURCE_REFERENCE",
        },
        "current_target": {
            "repository_id": 1412133785, "repository": NEW, "kind": "ISSUE",
            "number": 5, "url": "https://github.com/reallakshman19/Common/issues/5",
            "source_grade": "CURRENT_EXECUTION_REFERENCE",
        },
        "source_continuity": {
            "historical_commit_sha": MAIN, "current_commit_sha": MAIN,
            "relationship": "CODE_EQUIVALENT",
        },
        "migration_relation": "HISTORICAL_PURPOSE_CONTINUATION_ONLY",
        "owner_original_source": "UNKNOWN",
        "external_review": "NOT_TRANSFERRED",
        "writer_lease": "NOT_GRANTED",
    }


class CrossRepositoryV2Tests(unittest.TestCase):
    def rejects(self, doc, needle):
        with self.assertRaises(CrossRepositoryIdentityError) as cm:
            validate_crossrepo_identity_v2(doc)
        self.assertIn(needle, str(cm.exception))

    def test_positive_unmodified_v1_current_roles_and_v2_old_reference(self):
        result = validate_crossrepo_identity_v2(fixture())
        self.assertEqual("CALLER_REFERENCED_UNATTESTED", result["reference_grade"])
        self.assertEqual("NOT_EXECUTED", result["provider_object_verification"])
        self.assertEqual("NOT_GRANTED", result["writer_lease"])
        self.assertIsNone(result["programme_progress"])
        self.assertEqual("NOT_ADJUDICATED", result["accepted_evidence"])
        self.assertEqual("NOT_AUTHENTICATED", result["owner_authentication"])

    def test_historical_id_and_execution_repo_must_be_different(self):
        doc = fixture()
        doc["historical_origin"]["repository_id"] = 1412133785
        self.rejects(doc, "SEPARATE_REPOSITORY_ID_REQUIRED")
        doc = fixture()
        doc["historical_origin"]["repository"] = NEW
        self.rejects(doc, "SEPARATE_REPOSITORY_ID_REQUIRED")

    def test_historical_issue_url_must_retain_actual_old_repo(self):
        doc = fixture()
        doc["historical_origin"]["url"] = "https://github.com/reallakshman19/Common/issues/787"
        self.rejects(doc, "HISTORICAL_URL_NAMESPACE_MISMATCH")

    def test_current_issue_must_use_actual_new_repo_url(self):
        doc = fixture()
        doc["current_target"]["url"] = "https://github.com/reallaksh19/Common/issues/5"
        self.rejects(doc, "TARGET_URL_NAMESPACE_MISMATCH")

    def test_current_programme_root_and_namespace_are_bound(self):
        doc = fixture()
        doc["current_target"]["number"] = 6
        doc["current_target"]["url"] = "https://github.com/reallakshman19/Common/issues/6"
        self.rejects(doc, "CURRENT_PROGRAMME_ROOT_NOT_BOUND")
        doc = fixture()
        doc["current_identity"]["programme"]["repository"] = OLD
        self.rejects(doc, "CURRENT_V1_IDENTITY_INVALID")

    def test_u1_current_graph_session_candidate_must_not_point_to_historical_repo(self):
        for field in ("graph_source", "session_source", "candidate_source"):
            with self.subTest(field=field):
                doc = fixture()
                doc["current_identity"][field]["repository"] = OLD
                self.rejects(doc, "CROSS_REPOSITORY_REFERENCE")

    def test_historical_code_sha_equality_does_not_transfer_review(self):
        result = validate_crossrepo_identity_v2(fixture())
        self.assertEqual("NOT_TRANSFERRED", result["historical_reviews_and_checks"])
        self.assertEqual("NOT_GRANTED", result["merge_authority"])
        doc = fixture()
        doc["external_review"] = "APPROVED"
        self.rejects(doc, "SCHEMA_INVALID")

    def test_original_owner_grade_remains_unknown_not_legacy_mirror(self):
        doc = fixture()
        doc["current_identity"]["owner_source_grade"] = "GITHUB_VERBATIM_MIRROR"
        self.rejects(doc, "HISTORICAL_OWNER_GRADE_PROMOTED")
        doc = fixture()
        doc["owner_original_source"] = "AUTHENTICATED"
        self.rejects(doc, "SCHEMA_INVALID")

    def test_source_equivalence_is_explicit_and_sha_matched(self):
        doc = fixture()
        doc["source_continuity"]["current_commit_sha"] = "f" * 40
        self.rejects(doc, "FALSE_CODE_EQUIVALENCE")
        doc["source_continuity"]["relationship"] = "CODE_CHANGED"
        out = validate_crossrepo_identity_v2(doc)
        self.assertEqual("NOT_GRANTED", out["writer_lease"])
        doc["source_continuity"]["current_commit_sha"] = MAIN
        self.rejects(doc, "FALSE_CODE_CHANGE")

    def test_swapped_grade_and_extra_authority_escalation_fail(self):
        doc = fixture()
        doc["historical_origin"]["source_grade"] = "CURRENT_EXECUTION_REFERENCE"
        self.rejects(doc, "HISTORICAL_SOURCE_GRADE_MISMATCH")
        doc = fixture()
        doc["current_target"]["source_grade"] = "HISTORICAL_SOURCE_REFERENCE"
        self.rejects(doc, "TARGET_SOURCE_GRADE_MISMATCH")
        doc = fixture()
        doc["provider_verified"] = True
        self.rejects(doc, "SCHEMA_INVALID")
        doc = fixture()
        doc["writer_lease"] = "GRANTED"
        self.rejects(doc, "SCHEMA_INVALID")

    def test_digests_change_on_current_code_role_or_source_history(self):
        a = fixture()
        digest = validate_crossrepo_identity_v2(a)["cross_repository_identity_sha256"]
        for patch in ("head", "origin"):
            with self.subTest(patch=patch):
                b = copy.deepcopy(a)
                if patch == "head":
                    b["current_identity"]["candidate_source"]["head_sha"] = "e"*40
                else:
                    b["historical_origin"]["number"] = 788
                    b["historical_origin"]["url"] = "https://github.com/reallaksh19/Common/issues/788"
                self.assertNotEqual(digest, validate_crossrepo_identity_v2(b)["cross_repository_identity_sha256"])

    def test_v1_rejects_unknown_source_promoted_to_durable_commit(self):
        doc = fixture()
        doc["current_identity"]["session_source"].update(state="UNKNOWN", commit_sha=B)
        self.rejects(doc, "CURRENT_V1_IDENTITY_INVALID")


if __name__ == "__main__":
    unittest.main(verbosity=2)
