import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from review_basis import (
    active_common_protocol_digest,
    active_common_protocol_ref,
    common_manifest_semantic_errors,
    load_common_protocol_manifest,
    review_basis_errors,
    validate_assessment_context,
    validate_self_check_basis,
)


CANDIDATE = "c" * 40
BASE = "a" * 40
PROFILE_DIGEST = active_common_protocol_digest()
COMMON_PROTOCOL_REF = active_common_protocol_ref()


def canonical_digest(value):
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def criterion(
    result="PASS",
    applicability="REQUIRED",
    applicability_basis=None,
    waiver_ref=None,
):
    item = {"applicability": applicability, "result": result}
    if result == "PASS":
        item["evidence_refs"] = ["evidence://review"]
    if applicability_basis is not None:
        item["applicability_basis"] = applicability_basis
    if waiver_ref is not None:
        item["waiver_ref"] = waiver_ref
    return item


def profile(
    role="SELF_REVIEW",
    independence="NONE",
    author="agent://1",
    reviewer="agent://1",
    final_candidate=CANDIDATE,
):
    review = {
        "common_protocol": {
            "ref": COMMON_PROTOCOL_REF,
            "version": "1.0",
            "digest": PROFILE_DIGEST,
        },
        "project_protocol": {
            "ref": "issue://project-review",
            "digest": PROFILE_DIGEST,
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
        "unresolved_required_findings": 0,
        "result": "COMPLETE",
    }
    if final_candidate is not None:
        review["final_candidate"] = final_candidate
    return {"review_profile": review}


def self_context(manifest_digest, manifest_ref="manifest://1"):
    return {
        "schema_version": "SELF_CHECK_CONTEXT_V1",
        "authority": "SOLO_SELF_CHECK_CONTEXT",
        "candidate_sha": CANDIDATE,
        "manifest_ref": manifest_ref,
        "manifest_digest": manifest_digest,
        "principal": {
            "kind": "SOLO_PRINCIPAL",
            "identity": "agent://1",
            "principal_independence": "NONE",
            "fresh_reconstruction": True,
            "blindness_claim": "NONE",
        },
        "reconstruction_policy": {
            "original_task_ref": "issue://574",
            "base_sha": BASE,
            "candidate_sha": CANDIDATE,
            "repository_context_refs": [
                "repo://base",
                "repo://candidate",
                "repo://common-reviewer",
            ],
            "expectation_manifest_frozen": True,
            "author_reasoning_used_as_evidence": False,
            "coder_confidence_used_as_evidence": False,
            "prior_self_check_used_as_evidence": False,
            "outcome_falsification_required": True,
        },
        "tool_access": ["repository", "tests"],
    }


def review_context(
    manifest_digest,
    kind="SAME_PRINCIPAL_FRESH_CONTEXT",
    independence="DEGRADED",
    identity="agent://1",
):
    return {
        "schema_version": "REVIEW_CONTEXT_V1",
        "authority": "FRESH_REVIEW_CONTEXT",
        "candidate_sha": CANDIDATE,
        "manifest_ref": "manifest://1",
        "manifest_digest": manifest_digest,
        "reviewer": {
            "kind": kind,
            "identity": identity,
            "principal_independence": independence,
            "fresh_context": True,
        },
        "context_policy": {
            "original_task_ref": "issue://574",
            "base_sha": BASE,
            "candidate_sha": CANDIDATE,
            "repository_context_refs": ["repo://base", "repo://candidate"],
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


class ReviewBasisTests(unittest.TestCase):
    def test_crf01_active_common_manifest_floor_is_coherent(self):
        manifest = load_common_protocol_manifest()
        self.assertEqual([], common_manifest_semantic_errors(manifest))
        self.assertEqual(
            "skills/common-reviewer-protocol-v1.0",
            active_common_protocol_ref(),
        )
        self.assertEqual(64, len(active_common_protocol_digest()))

    def test_crf02_cr01_cannot_be_not_applicable(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-01"] = criterion(
            result="NOT_APPLICABLE",
            applicability="NOT_APPLICABLE",
            applicability_basis="seed://not-applicable",
        )
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "CR-01: SELF_REVIEW Common floor requires applicability REQUIRED"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf03_cr05_cannot_be_not_applicable(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-05"] = criterion(
            result="NOT_APPLICABLE",
            applicability="NOT_APPLICABLE",
            applicability_basis="seed://not-applicable",
        )
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "CR-05: SELF_REVIEW Common floor requires applicability REQUIRED"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf04_cr10_cannot_be_not_applicable(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-10"] = criterion(
            result="NOT_APPLICABLE",
            applicability="NOT_APPLICABLE",
            applicability_basis="seed://not-applicable",
        )
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "CR-10: SELF_REVIEW Common floor requires applicability REQUIRED"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf05_conditional_cr06_can_be_not_applicable_with_basis(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-06"] = criterion(
            result="NOT_APPLICABLE",
            applicability="NOT_APPLICABLE",
            applicability_basis="project://no-interface-change",
        )
        self.assertEqual([], self.self_errors(prof=value))

    def test_crf06_conditional_na_without_basis_is_rejected(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-06"] = criterion(
            result="NOT_APPLICABLE",
            applicability="NOT_APPLICABLE",
        )
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any("applicability_basis" in error for error in errors),
            errors,
        )

    def test_crf07_project_overlay_can_strengthen_conditional_cr06(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-06"] = criterion()
        value["review_profile"]["project_method_ids"] = [
            "PROJECT-METHOD-1",
            "PROJECT-METHOD-INTERFACE",
        ]
        self.assertEqual([], self.self_errors(prof=value))

    def test_crf08_self_review_common_floor_waiver_is_rejected(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-06"] = criterion(
            result="WAIVED",
            applicability="WAIVED_BY_AUTHORITY",
            waiver_ref="waiver://caller-supplied",
        )
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "SELF_REVIEW cannot grant or consume a Common-floor waiver"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf09_fake_common_protocol_digest_is_rejected(self):
        value = profile()
        value["review_profile"]["common_protocol"]["digest"] = "f" * 64
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "common_protocol.digest must equal active Common Reviewer manifest digest"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf09_wrong_common_protocol_ref_is_rejected(self):
        value = profile()
        value["review_profile"]["common_protocol"]["ref"] = "repo://wrong-common-reviewer"
        errors = self.self_errors(prof=value)
        self.assertTrue(
            any(
                "common_protocol.ref must equal active Common Reviewer canonical_ref"
                in error
                for error in errors
            ),
            errors,
        )

    def test_crf10_project_methods_remain_additive_without_authority(self):
        value = profile()
        methods = ["PROJECT-METHOD-1", "PROJECT-METHOD-NEGATIVE-CASE"]
        value["review_profile"]["project_method_ids"] = methods
        self.assertEqual([], self.self_errors(prof=value))
        self.assertEqual(methods, value["review_profile"]["project_method_ids"])

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.tmp.name)
        manifest_dir = cls.repo / "manifests"
        manifest_dir.mkdir(parents=True)
        payload = {
            "schema_version": "TEST_EXPECTATION_MANIFEST_V1",
            "authority": "FROZEN_TEST_EXPECTATIONS",
            "claims": ["fresh reconstruction", "exact candidate"],
        }
        cls.manifest_digest = canonical_digest(payload)
        manifest = dict(payload)
        manifest["manifest_digest"] = cls.manifest_digest
        (manifest_dir / "frozen.yaml").write_text(
            yaml.safe_dump(manifest, sort_keys=False),
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def basis(self):
        return {
            "original_task_ref": "issue://574",
            "base_sha": BASE,
            "candidate_sha": CANDIDATE,
            "manifest_ref": "manifest://1",
            "manifest_path": "manifests/frozen.yaml",
            "manifest_digest": self.manifest_digest,
            "repository_context_refs": [
                "repo://base",
                "repo://candidate",
                "repo://common-reviewer",
            ],
        }

    def self_errors(self, ctx=None, prof=None, basis=None):
        return review_basis_errors(
            prof or profile(),
            ctx or self_context(self.manifest_digest),
            self.basis() if basis is None else basis,
            self.repo,
        )

    def test_scx10_clean_solo_self_review_context_is_valid_basis_only(self):
        errors = self.self_errors()
        self.assertEqual([], errors)
        self.assertIsInstance(errors, list)

    def test_self_review_requires_source_bound_governing_basis(self):
        errors = review_basis_errors(
            profile(),
            self_context(self.manifest_digest),
        )
        self.assertTrue(
            any("source-bound governing basis" in error for error in errors),
            errors,
        )

    def test_self_review_requires_exact_final_candidate_binding(self):
        errors = review_basis_errors(
            profile(final_candidate=None),
            self_context(self.manifest_digest),
            self.basis(),
            self.repo,
        )
        self.assertTrue(
            any("exact final_candidate binding" in error for error in errors),
            errors,
        )

    def test_self_review_requires_self_check_context(self):
        errors = review_basis_errors(
            profile(),
            review_context(self.manifest_digest),
        )
        self.assertTrue(
            any("SELF_CHECK_CONTEXT_V1" in error for error in errors),
            errors,
        )

    def test_scx01_independence_inflation_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["principal"]["principal_independence"] = "DEGRADED"
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any(
                "principal_independence" in error
                or "NONE" in error
                for error in errors
            ),
            errors,
        )

    def test_scx02_fake_blindness_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["principal"]["blindness_claim"] = "BLINDED_REVIEW"
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any("blindness_claim" in error or "blinded" in error for error in errors),
            errors,
        )

    def test_scx03_candidate_mismatch_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["candidate_sha"] = "e" * 40
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any("candidate_sha" in error for error in errors),
            errors,
        )

    def test_scx04_author_reasoning_as_evidence_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["author_reasoning_used_as_evidence"] = True
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any(
                "author_reasoning_used_as_evidence" in error
                or "author reasoning" in error
                for error in errors
            ),
            errors,
        )

    def test_scx05_coder_confidence_as_evidence_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["coder_confidence_used_as_evidence"] = True
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any(
                "coder_confidence_used_as_evidence" in error
                or "coder confidence" in error
                for error in errors
            ),
            errors,
        )

    def test_scx06_prior_self_check_as_evidence_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["prior_self_check_used_as_evidence"] = True
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any(
                "prior_self_check_used_as_evidence" in error
                or "prior self-check" in error
                for error in errors
            ),
            errors,
        )

    def test_scx07_no_fresh_reconstruction_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["principal"]["fresh_reconstruction"] = False
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any(
                "fresh_reconstruction" in error
                or "fresh reconstruction" in error
                for error in errors
            ),
            errors,
        )

    def test_scx08_schema_valid_stale_manifest_binding_is_rejected_source_bound(self):
        ctx = self_context("f" * 64)
        self.assertEqual([], validate_assessment_context(ctx))
        errors = review_basis_errors(
            profile(),
            ctx,
            self.basis(),
            self.repo,
        )
        self.assertTrue(
            any("manifest_digest" in error for error in errors),
            errors,
        )

    def test_scx08_basis_digest_must_match_actual_frozen_manifest(self):
        basis = self.basis()
        basis["manifest_digest"] = "f" * 64
        errors = validate_self_check_basis(basis, self.repo)
        self.assertTrue(
            any("declared digest" in error for error in errors),
            errors,
        )

    def test_scx09_wrong_candidate_effective_profile_is_rejected(self):
        errors = self.self_errors(
            prof=profile(final_candidate="e" * 40),
        )
        self.assertTrue(
            any("profile final_candidate" in error for error in errors),
            errors,
        )

    def test_wrong_task_binding_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["original_task_ref"] = "issue://wrong"
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any("original_task_ref" in error for error in errors),
            errors,
        )

    def test_wrong_base_binding_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["base_sha"] = "b" * 40
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any("base_sha" in error for error in errors),
            errors,
        )

    def test_missing_required_repository_context_is_rejected(self):
        ctx = self_context(self.manifest_digest)
        ctx["reconstruction_policy"]["repository_context_refs"].remove(
            "repo://common-reviewer"
        )
        errors = self.self_errors(ctx=ctx)
        self.assertTrue(
            any("missing governing refs" in error for error in errors),
            errors,
        )

    def test_basis_rejects_unknown_field(self):
        basis = self.basis()
        basis["engineering_pass"] = True
        errors = validate_self_check_basis(basis, self.repo)
        self.assertTrue(any("unknown fields" in error for error in errors), errors)

    def test_same_principal_reviewer_must_be_degraded(self):
        value = profile(role="REVIEWER", independence="DEGRADED")
        self.assertEqual(
            review_basis_errors(
                value,
                review_context(self.manifest_digest),
            ),
            [],
        )

    def test_distinct_reviewer_requires_distinct_identity(self):
        value = profile(
            role="REVIEWER",
            independence="DISTINCT_PRINCIPAL",
            reviewer="agent://2",
        )
        ctx = review_context(
            self.manifest_digest,
            kind="DISTINCT_PRINCIPAL",
            independence="DISTINCT",
            identity="agent://2",
        )
        self.assertEqual(review_basis_errors(value, ctx), [])

    def test_distinct_claim_with_same_identity_is_rejected(self):
        value = profile(role="REVIEWER", independence="DISTINCT_PRINCIPAL")
        errors = review_basis_errors(
            value,
            review_context(
                self.manifest_digest,
                kind="DISTINCT_PRINCIPAL",
                independence="DISTINCT",
            ),
        )
        self.assertTrue(
            any("distinct principal identities" in error for error in errors),
            errors,
        )

    def test_required_pass_needs_evidence(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-05"].pop("evidence_refs")
        errors = review_basis_errors(
            value,
            self_context(self.manifest_digest),
            self.basis(),
            self.repo,
        )
        self.assertTrue(
            any("CR-05: PASS requires" in error for error in errors),
            errors,
        )

    def test_not_applicable_needs_basis(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-07"] = {
            "applicability": "NOT_APPLICABLE",
            "result": "NOT_APPLICABLE",
        }
        errors = review_basis_errors(
            value,
            self_context(self.manifest_digest),
            self.basis(),
            self.repo,
        )
        self.assertTrue(
            any("applicability_basis" in error for error in errors),
            errors,
        )

    def test_complete_cannot_hide_not_run_required_criterion(self):
        value = profile()
        value["review_profile"]["common_criteria"]["CR-08"] = criterion("NOT_RUN")
        errors = review_basis_errors(
            value,
            self_context(self.manifest_digest),
            self.basis(),
            self.repo,
        )
        self.assertTrue(
            any("COMPLETE review requires PASS" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
