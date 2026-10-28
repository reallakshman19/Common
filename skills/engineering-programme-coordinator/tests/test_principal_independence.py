import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from principal_independence import (
    AUTHORITY_BOUNDARIES,
    canonical_digest,
    compile_truth,
    object_digest,
    profile_identity_projection,
    validate_truth,
    validate_truth_shape,
)
from review_basis import active_common_protocol_digest, active_common_protocol_ref


CANDIDATE = "c" * 40
BASE = "b" * 40
MANIFEST_DIGEST = "d" * 64
PROJECT_DIGEST = "e" * 64


def criterion(result="NOT_RUN"):
    value = {"applicability": "REQUIRED", "result": result}
    if result == "PASS":
        value["evidence_refs"] = ["evidence://criterion"]
    return value


def profile(
    *,
    role="SELF_REVIEW",
    author="agent://solo",
    reviewer="agent://solo",
    independence="NONE",
):
    return {
        "review_profile": {
            "common_protocol": {
                "ref": active_common_protocol_ref(),
                "version": "1.0",
                "digest": active_common_protocol_digest(),
            },
            "project_protocol": {
                "ref": "issue://582/project-review",
                "digest": PROJECT_DIGEST,
            },
            "role": role,
            "author_principal": author,
            "review_principal": reviewer,
            "principal_independence": independence,
            "context_reset": "FRESH_REVIEW_ATTEMPT",
            "common_criteria": {
                f"CR-{index:02d}": criterion()
                for index in range(1, 11)
            },
            "project_method_ids": ["PROJECT-METHOD-1"],
            "specialist_required": [],
            "final_candidate": CANDIDATE,
        }
    }


def self_context(identity="agent://solo"):
    return {
        "schema_version": "SELF_CHECK_CONTEXT_V1",
        "authority": "SOLO_SELF_CHECK_CONTEXT",
        "candidate_sha": CANDIDATE,
        "manifest_ref": "manifest://frozen",
        "manifest_digest": MANIFEST_DIGEST,
        "principal": {
            "kind": "SOLO_PRINCIPAL",
            "identity": identity,
            "principal_independence": "NONE",
            "fresh_reconstruction": True,
            "blindness_claim": "NONE",
        },
        "reconstruction_policy": {
            "original_task_ref": "issue://582",
            "base_sha": BASE,
            "candidate_sha": CANDIDATE,
            "repository_context_refs": ["repo://main"],
            "expectation_manifest_frozen": True,
            "author_reasoning_used_as_evidence": False,
            "coder_confidence_used_as_evidence": False,
            "prior_self_check_used_as_evidence": False,
            "outcome_falsification_required": True,
        },
        "tool_access": ["repository", "tests"],
    }


def review_context(
    *,
    identity,
    kind="SAME_PRINCIPAL_FRESH_CONTEXT",
    independence="DEGRADED",
):
    return {
        "schema_version": "REVIEW_CONTEXT_V1",
        "authority": "FRESH_REVIEW_CONTEXT",
        "candidate_sha": CANDIDATE,
        "manifest_ref": "manifest://frozen",
        "manifest_digest": MANIFEST_DIGEST,
        "reviewer": {
            "kind": kind,
            "identity": identity,
            "principal_independence": independence,
            "fresh_context": True,
        },
        "context_policy": {
            "original_task_ref": "issue://582",
            "base_sha": BASE,
            "candidate_sha": CANDIDATE,
            "repository_context_refs": ["repo://main"],
            "candidate_visible_in_phase_a": False,
            "generated_tests_visible_in_phase_a": False,
            "coder_reasoning_included": False,
            "coder_confidence_included": False,
            "prior_self_review_included": False,
            "implementation_rationale_included": False,
            "candidate_visible_in_phase_b": True,
        },
        "tool_access": ["repository", "tests"],
    }


def refresh_truth_digest(value):
    value["truth_digest"] = object_digest(value, "truth_digest")


class PrincipalIndependenceTruthTests(unittest.TestCase):
    def test_pis01_self_review_same_principal_is_none(self):
        value = compile_truth(profile(), self_context())
        self.assertEqual("SELF_REVIEW", value["review_mode"])
        self.assertEqual("SAME_PRINCIPAL", value["principals"]["relationship"])
        self.assertEqual("NONE", value["principals"]["principal_independence"])
        self.assertFalse(value["compatibility"]["legacy_degraded_input_consumed"])
        self.assertEqual([], validate_truth_shape(value))
        self.assertEqual([], validate_truth(value, profile(), self_context()))

    def test_source_bound_fresh_replay_is_required(self):
        value = compile_truth(profile(), self_context())
        errors = validate_truth(value)
        self.assertTrue(
            any("source-bound fresh replay is required" in error for error in errors),
            errors,
        )

    def test_pis02_self_review_distinct_author_and_reviewer_is_rejected(self):
        value = profile(author="agent://author", reviewer="agent://reviewer")
        with self.assertRaisesRegex(
            ValueError,
            "SELF_REVIEW author_principal and review_principal must match",
        ):
            compile_truth(value, self_context(identity="agent://reviewer"))

    def test_pis03_governed_same_principal_degraded_input_canonicalizes_to_none(self):
        p = profile(
            role="REVIEWER",
            author="agent://same",
            reviewer="agent://same",
            independence="DEGRADED",
        )
        c = review_context(identity="agent://same")
        value = compile_truth(p, c)
        self.assertEqual("GOVERNED_REVIEW", value["review_mode"])
        self.assertEqual("SAME_PRINCIPAL", value["principals"]["relationship"])
        self.assertEqual("NONE", value["principals"]["principal_independence"])
        self.assertEqual(
            "GOVERNED_SAME_PRINCIPAL_FRESH_CONTEXT",
            value["separation"]["context_separation"],
        )
        self.assertEqual(
            "FRESH_RECONSTRUCTION_ONLY",
            value["separation"]["methodological_separation"],
        )
        self.assertTrue(value["compatibility"]["legacy_degraded_input_consumed"])

    def test_pis04_governed_distinct_principal_is_distinct_principal(self):
        p = profile(
            role="SUPER_REVIEWER",
            author="agent://author",
            reviewer="agent://reviewer",
            independence="DISTINCT_PRINCIPAL",
        )
        c = review_context(
            identity="agent://reviewer",
            kind="DISTINCT_PRINCIPAL",
            independence="DISTINCT",
        )
        value = compile_truth(p, c)
        self.assertEqual("DISTINCT_PRINCIPAL", value["principals"]["relationship"])
        self.assertEqual(
            "DISTINCT_PRINCIPAL",
            value["principals"]["principal_independence"],
        )
        self.assertEqual(
            "DISTINCT_PRINCIPAL_AND_FRESH_RECONSTRUCTION",
            value["separation"]["methodological_separation"],
        )
        self.assertFalse(value["compatibility"]["legacy_degraded_input_consumed"])

    def test_human_reviewer_is_distinct_only_when_identity_is_distinct(self):
        p = profile(
            role="REVIEWER",
            author="agent://author",
            reviewer="human://reviewer",
            independence="DISTINCT_PRINCIPAL",
        )
        c = review_context(
            identity="human://reviewer",
            kind="HUMAN_REVIEWER",
            independence="DISTINCT",
        )
        value = compile_truth(p, c)
        self.assertEqual(
            "DISTINCT_PRINCIPAL",
            value["principals"]["principal_independence"],
        )

    def test_pis05_same_principal_claiming_distinct_is_rejected(self):
        p = profile(
            role="REVIEWER",
            author="agent://same",
            reviewer="agent://same",
            independence="DISTINCT_PRINCIPAL",
        )
        c = review_context(
            identity="agent://same",
            kind="DISTINCT_PRINCIPAL",
            independence="DISTINCT",
        )
        with self.assertRaisesRegex(
            ValueError,
            "DISTINCT_PRINCIPAL review requires distinct principal identities",
        ):
            compile_truth(p, c)

    def test_pis06_distinct_principals_claiming_degraded_is_rejected(self):
        p = profile(
            role="REVIEWER",
            author="agent://author",
            reviewer="agent://reviewer",
            independence="DEGRADED",
        )
        c = review_context(identity="agent://reviewer")
        with self.assertRaisesRegex(
            ValueError,
            "DEGRADED review must use the same principal identity",
        ):
            compile_truth(p, c)

    def test_pis07_context_identity_must_equal_review_principal(self):
        p = profile(
            role="REVIEWER",
            author="agent://same",
            reviewer="agent://same",
            independence="DEGRADED",
        )
        c = review_context(identity="agent://other")
        with self.assertRaisesRegex(
            ValueError,
            "REVIEW_CONTEXT reviewer identity must equal review_principal",
        ):
            compile_truth(p, c)

    def test_pis08_fresh_context_does_not_upgrade_same_principal(self):
        p = profile(
            role="SUPER_REVIEWER",
            author="agent://same",
            reviewer="agent://same",
            independence="DEGRADED",
        )
        c = review_context(identity="agent://same")
        value = compile_truth(p, c)
        self.assertTrue(value["separation"]["fresh_context"])
        self.assertEqual("NONE", value["principals"]["principal_independence"])

    def test_pis09_evidence_result_and_findings_do_not_change_identity_digest(self):
        p = profile()
        before_projection = profile_identity_projection(p)
        before_digest = canonical_digest(before_projection)
        before = compile_truth(p, self_context())

        changed = copy.deepcopy(p)
        changed["review_profile"]["common_criteria"]["CR-03"] = criterion("PASS")
        changed["review_profile"]["findings"] = [
            {
                "id": "ADV-1",
                "class": "ADVISORY",
                "summary": "Later evidence-only finding.",
                "disposition": "ACCEPTED_ADVISORY",
            }
        ]
        after_projection = profile_identity_projection(changed)
        after_digest = canonical_digest(after_projection)
        after = compile_truth(changed, self_context())

        self.assertEqual(before_projection, after_projection)
        self.assertEqual(before_digest, after_digest)
        self.assertEqual(before, after)

    def test_pis10_identity_movement_stales_stored_truth(self):
        original = compile_truth(profile(), self_context())
        moved_profile = profile(
            author="agent://replacement",
            reviewer="agent://replacement",
        )
        moved_context = self_context(identity="agent://replacement")
        errors = validate_truth(original, moved_profile, moved_context)
        self.assertTrue(
            any("stored truth does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_pis11_recomputed_truth_tamper_is_rejected_by_fresh_replay(self):
        p = profile()
        c = self_context()
        value = compile_truth(p, c)
        value["source"]["profile_identity_digest"] = "f" * 64
        refresh_truth_digest(value)
        self.assertEqual([], validate_truth_shape(value))
        errors = validate_truth(value, p, c)
        self.assertTrue(
            any("stored truth does not equal fresh source replay" in error for error in errors),
            errors,
        )

    def test_pis12_canonical_principal_independence_never_contains_degraded(self):
        p = profile(
            role="REVIEWER",
            author="agent://same",
            reviewer="agent://same",
            independence="DEGRADED",
        )
        c = review_context(identity="agent://same")
        value = compile_truth(p, c)
        self.assertNotEqual(
            "DEGRADED",
            value["principals"]["principal_independence"],
        )
        self.assertEqual("DEGRADED", value["source"]["profile_input_independence"])
        self.assertEqual("DEGRADED", value["source"]["context_input_independence"])

    def test_pis13_oracle_independence_is_not_derived_from_identity(self):
        same = compile_truth(profile(), self_context())
        p = profile(
            role="REVIEWER",
            author="agent://author",
            reviewer="agent://reviewer",
            independence="DISTINCT_PRINCIPAL",
        )
        c = review_context(
            identity="agent://reviewer",
            kind="DISTINCT_PRINCIPAL",
            independence="DISTINCT",
        )
        distinct = compile_truth(p, c)
        for value in (same, distinct):
            self.assertFalse(
                value["oracle_independence"]["derived_from_principal_identity"]
            )
            self.assertTrue(
                value["oracle_independence"]["project_oracle_requirement_preserved"]
            )

    def test_pis14_truth_has_no_review_or_lifecycle_authority(self):
        value = compile_truth(profile(), self_context())
        self.assertEqual(AUTHORITY_BOUNDARIES, value["authority_boundaries"])
        self.assertTrue(all(item is False for item in value["authority_boundaries"].values()))


if __name__ == "__main__":
    unittest.main()
