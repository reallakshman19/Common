#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from coordlib import validate as schema_validate


SKILLS = Path(__file__).resolve().parents[2]
COMMON_PROFILE_SCHEMA = (
    SKILLS
    / "common-reviewer-protocol-v1.0"
    / "schemas"
    / "common-review-profile.schema.yaml"
)

COMMON_PROTOCOL_MANIFEST = (
    SKILLS
    / "common-reviewer-protocol-v1.0"
    / "protocol-manifest.yaml"
)
COMMON_CRITERIA = tuple(f"CR-{index:02d}" for index in range(1, 11))


SELF_CHECK_BASIS_KEYS = {
    "original_task_ref",
    "base_sha",
    "candidate_sha",
    "manifest_ref",
    "manifest_path",
    "manifest_digest",
    "repository_context_refs",
}


def _canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def load_common_protocol_manifest() -> dict[str, Any]:
    with COMMON_PROTOCOL_MANIFEST.open("r", encoding="utf-8") as fh:
        value = yaml.safe_load(fh)
    if not isinstance(value, dict):
        raise ValueError("Common Reviewer protocol manifest must be an object")
    return value


def active_common_protocol_digest() -> str:
    return _canonical_digest(load_common_protocol_manifest())


def active_common_protocol_ref() -> str:
    manifest = load_common_protocol_manifest()
    protocol = manifest.get("protocol") or {}
    ref = protocol.get("canonical_ref")
    if not isinstance(ref, str) or not ref:
        raise ValueError("Common Reviewer protocol manifest lacks canonical_ref")
    return ref


def common_manifest_semantic_errors(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    protocol = manifest.get("protocol")
    capabilities = manifest.get("capabilities")
    floor = manifest.get("self_review_floor")
    if not isinstance(protocol, dict):
        return ["Common Reviewer protocol manifest lacks protocol object"]
    if protocol.get("version") != "1.0":
        errors.append("Common Reviewer protocol version must be 1.0")
    if protocol.get("status") != "ACTIVE":
        errors.append("Common Reviewer protocol must be ACTIVE")
    if protocol.get("canonical_ref") != "skills/common-reviewer-protocol-v1.0":
        errors.append("Common Reviewer canonical_ref must identify the active v1.0 package")
    if not isinstance(capabilities, dict) or capabilities.get("common_review_catalog") != "CR-01..CR-10":
        errors.append("Common Reviewer manifest must declare CR-01..CR-10 catalog")
    if not isinstance(floor, dict):
        return errors + ["Common Reviewer manifest lacks self_review_floor"]

    criteria = floor.get("criteria")
    na_policy = floor.get("not_applicable")
    waiver = floor.get("waiver")
    overlay = floor.get("project_overlay")
    if floor.get("role") != "SELF_REVIEW":
        errors.append("self_review_floor.role must be SELF_REVIEW")
    if not isinstance(criteria, dict):
        errors.append("self_review_floor.criteria must be an object")
        return errors

    always = criteria.get("always_required")
    conditional = criteria.get("conditionally_applicable")
    if not isinstance(always, list) or not isinstance(conditional, list):
        errors.append("self_review_floor criteria sets must be lists")
        return errors
    if len(always) != len(set(always)) or len(conditional) != len(set(conditional)):
        errors.append("self_review_floor criteria sets must not contain duplicates")
    if set(always) & set(conditional):
        errors.append("self_review_floor criteria sets must be disjoint")
    if set(always) | set(conditional) != set(COMMON_CRITERIA):
        errors.append("self_review_floor must cover CR-01..CR-10 exactly")
    if set(always) != {"CR-01", "CR-02", "CR-03", "CR-04", "CR-05", "CR-10"}:
        errors.append("self_review_floor always-required set does not match Common v1.0")
    if set(conditional) != {"CR-06", "CR-07", "CR-08", "CR-09"}:
        errors.append("self_review_floor conditional set does not match Common v1.0")

    if not isinstance(na_policy, dict):
        errors.append("self_review_floor.not_applicable must be an object")
    else:
        if na_policy.get("permitted_only_for_conditionally_applicable") is not True:
            errors.append("N/A must be limited to conditionally applicable Common criteria")
        if na_policy.get("explicit_basis_required") is not True:
            errors.append("N/A must require explicit applicability basis")

    if not isinstance(waiver, dict):
        errors.append("self_review_floor.waiver must be an object")
    else:
        if waiver.get("self_review_may_grant") is not False:
            errors.append("SELF_REVIEW must not grant its own Common-criterion waiver")
        if waiver.get("authoritative_external_waiver_validation") != "LOCAL_ACCEPTANCE_AUTHORITY":
            errors.append("external waiver validation must remain Local acceptance authority")

    if not isinstance(overlay, dict):
        errors.append("self_review_floor.project_overlay must be an object")
    else:
        if overlay.get("required") is not True:
            errors.append("project overlay must remain required")
        if overlay.get("may_strengthen_common_floor") is not True:
            errors.append("project overlay must be allowed to strengthen Common floor")
        if overlay.get("may_silently_weaken_common_floor") is not False:
            errors.append("project overlay must not silently weaken Common floor")
    return errors


def self_review_floor_errors(value: dict[str, Any]) -> list[str]:
    review = value["review_profile"]
    if review["role"] != "SELF_REVIEW":
        return []

    try:
        manifest = load_common_protocol_manifest()
    except Exception as exc:
        return [f"cannot load active Common Reviewer manifest: {exc}"]
    errors = common_manifest_semantic_errors(manifest)
    if errors:
        return errors

    protocol = manifest["protocol"]
    common_protocol = review["common_protocol"]
    if common_protocol["ref"] != protocol["canonical_ref"]:
        errors.append("SELF_REVIEW common_protocol.ref must equal active Common Reviewer canonical_ref")
    if common_protocol["version"] != protocol["version"]:
        errors.append("SELF_REVIEW common_protocol.version must equal active Common Reviewer version")
    if common_protocol["digest"] != _canonical_digest(manifest):
        errors.append("SELF_REVIEW common_protocol.digest must equal active Common Reviewer manifest digest")

    floor = manifest["self_review_floor"]["criteria"]
    always = set(floor["always_required"])
    conditional = set(floor["conditionally_applicable"])
    criteria = review["common_criteria"]

    for criterion_id in sorted(always):
        if criteria[criterion_id]["applicability"] != "REQUIRED":
            errors.append(
                f"{criterion_id}: SELF_REVIEW Common floor requires applicability REQUIRED"
            )

    for criterion_id in sorted(conditional):
        applicability = criteria[criterion_id]["applicability"]
        if applicability not in {"REQUIRED", "NOT_APPLICABLE"}:
            errors.append(
                f"{criterion_id}: SELF_REVIEW Common floor permits only REQUIRED or NOT_APPLICABLE"
            )

    for criterion_id, criterion in criteria.items():
        if criterion["applicability"] == "WAIVED_BY_AUTHORITY":
            errors.append(
                f"{criterion_id}: SELF_REVIEW cannot grant or consume a Common-floor waiver in profile validation"
            )
    return errors


def _safe_repo_path(repo_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or chr(92) in value or ".." in path.parts:
        raise ValueError(f"unsafe repository path: {value}")
    root = repo_root.resolve()
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"repository path escapes root: {value}") from exc
    return resolved


def validate_self_check_basis(
    value: Any,
    repo_root: Path,
    label: str = "self-check-governing-basis",
) -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: governing basis must be an object"]
    errors: list[str] = []
    unknown = sorted(set(value) - SELF_CHECK_BASIS_KEYS)
    missing = sorted(SELF_CHECK_BASIS_KEYS - set(value))
    if unknown:
        errors.append(f"{label}: unknown fields: {', '.join(unknown)}")
    if missing:
        errors.append(f"{label}: missing fields: {', '.join(missing)}")
    if errors:
        return errors

    for key in ("original_task_ref", "manifest_ref", "manifest_path"):
        if not isinstance(value[key], str) or not value[key]:
            errors.append(f"{label}.{key}: must be a non-empty string")
    for key in ("base_sha", "candidate_sha"):
        item = value[key]
        if not isinstance(item, str) or len(item) != 40 or any(c not in "0123456789abcdef" for c in item):
            errors.append(f"{label}.{key}: must be a lowercase 40-hex SHA")
    digest = value["manifest_digest"]
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
        errors.append(f"{label}.manifest_digest: must be a lowercase 64-hex digest")
    refs = value["repository_context_refs"]
    if (
        not isinstance(refs, list)
        or not refs
        or len(refs) != len(set(refs))
        or any(not isinstance(item, str) or not item for item in refs)
    ):
        errors.append(
            f"{label}.repository_context_refs: must be a non-empty unique string list"
        )
    if errors:
        return errors

    try:
        manifest_path = _safe_repo_path(repo_root, value["manifest_path"])
    except ValueError as exc:
        return [f"{label}: {exc}"]
    if not manifest_path.is_file():
        return [f"{label}: frozen manifest path does not exist: {value['manifest_path']}"]
    try:
        with manifest_path.open("r", encoding="utf-8") as fh:
            manifest = yaml.safe_load(fh)
    except Exception as exc:
        return [f"{label}: cannot read frozen manifest: {exc}"]
    if not isinstance(manifest, dict):
        return [f"{label}: frozen manifest must be an object"]

    actual_digest = manifest.get("manifest_digest")
    if actual_digest != value["manifest_digest"]:
        errors.append(
            f"{label}: frozen manifest declared digest does not match governing basis"
        )
    if actual_digest is not None:
        payload = dict(manifest)
        payload.pop("manifest_digest", None)
        if actual_digest != _canonical_digest(payload):
            errors.append(
                f"{label}: frozen manifest self-digest does not match its content"
            )
    return errors


def self_check_binding_errors(
    context: dict[str, Any],
    basis: dict[str, Any],
) -> list[str]:
    policy = context["reconstruction_policy"]
    errors: list[str] = []
    exact_pairs = (
        ("candidate_sha", context["candidate_sha"], basis["candidate_sha"]),
        ("reconstruction_policy.candidate_sha", policy["candidate_sha"], basis["candidate_sha"]),
        ("reconstruction_policy.base_sha", policy["base_sha"], basis["base_sha"]),
        ("reconstruction_policy.original_task_ref", policy["original_task_ref"], basis["original_task_ref"]),
        ("manifest_ref", context["manifest_ref"], basis["manifest_ref"]),
        ("manifest_digest", context["manifest_digest"], basis["manifest_digest"]),
    )
    for label, actual, expected in exact_pairs:
        if actual != expected:
            errors.append(f"{label} must equal the frozen governing basis")

    missing_refs = sorted(
        set(basis["repository_context_refs"])
        - set(policy["repository_context_refs"])
    )
    if missing_refs:
        errors.append(
            "reconstruction_policy.repository_context_refs missing governing refs: "
            + ", ".join(missing_refs)
        )
    return errors


def _schema_errors(schema: dict[str, Any], value: Any, label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        where = ".".join(str(part) for part in error.path)
        errors.append(f"{label}{'.' + where if where else ''}: {error.message}")
    return errors


def validate_common_profile(value: Any, label: str = "common-review-profile") -> list[str]:
    with COMMON_PROFILE_SCHEMA.open("r", encoding="utf-8") as fh:
        schema = yaml.safe_load(fh)
    errors = _schema_errors(schema, value, label)
    if errors:
        return errors
    semantic = common_profile_semantic_errors(value)
    semantic.extend(self_review_floor_errors(value))
    return [f"{label}: {error}" for error in semantic]


def review_context_semantic_errors(context: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    reviewer = context["reviewer"]
    policy = context["context_policy"]
    if policy["candidate_sha"] != context["candidate_sha"]:
        errors.append("context_policy.candidate_sha must equal review candidate_sha")
    kind = reviewer["kind"]
    independence = reviewer["principal_independence"]
    if kind == "SAME_PRINCIPAL_FRESH_CONTEXT" and independence != "DEGRADED":
        errors.append("same-principal fresh-context review must record DEGRADED independence")
    if kind in {"DISTINCT_PRINCIPAL", "HUMAN_REVIEWER"} and independence != "DISTINCT":
        errors.append(f"{kind} must record DISTINCT principal independence")
    return errors


def self_check_context_semantic_errors(context: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    principal = context["principal"]
    policy = context["reconstruction_policy"]
    if policy["candidate_sha"] != context["candidate_sha"]:
        errors.append("reconstruction_policy.candidate_sha must equal self-check candidate_sha")
    if principal["principal_independence"] != "NONE":
        errors.append("solo self-check must record principal_independence NONE")
    if principal["blindness_claim"] != "NONE":
        errors.append("solo self-check cannot claim blinded or independent review")
    if not principal["fresh_reconstruction"]:
        errors.append("solo self-check requires fresh reconstruction")
    if policy["author_reasoning_used_as_evidence"]:
        errors.append("author reasoning cannot be used as self-check acceptance evidence")
    if policy["coder_confidence_used_as_evidence"]:
        errors.append("coder confidence cannot be used as self-check acceptance evidence")
    if policy["prior_self_check_used_as_evidence"]:
        errors.append("prior self-check cannot be used as current self-check acceptance evidence")
    return errors


def validate_assessment_context(value: Any, label: str = "assessment-context") -> list[str]:
    if not isinstance(value, dict):
        return [f"{label}: assessment context must be an object"]
    version = value.get("schema_version")
    if version == "SELF_CHECK_CONTEXT_V1":
        errors = schema_validate("self-check-context", value, label)
        if not errors:
            errors.extend(
                f"{label}: {error}"
                for error in self_check_context_semantic_errors(value)
            )
        return errors
    if version == "REVIEW_CONTEXT_V1":
        errors = schema_validate("review-context", value, label)
        if not errors:
            errors.extend(
                f"{label}: {error}"
                for error in review_context_semantic_errors(value)
            )
        return errors
    return [f"{label}: unsupported schema_version: {version!r}"]


def common_profile_semantic_errors(value: dict[str, Any]) -> list[str]:
    review = value["review_profile"]
    errors: list[str] = []
    role = review["role"]
    independence = review["principal_independence"]
    author = review["author_principal"]
    reviewer = review["review_principal"]

    if role == "SELF_REVIEW":
        if independence != "NONE":
            errors.append("SELF_REVIEW must record principal_independence NONE")
        if author != reviewer:
            errors.append("SELF_REVIEW author_principal and review_principal must match")
        if not review.get("final_candidate"):
            errors.append("SELF_REVIEW requires exact final_candidate binding")
    else:
        if independence == "NONE":
            errors.append(f"{role} cannot record principal_independence NONE")
        if independence == "DEGRADED" and author != reviewer:
            errors.append("DEGRADED review must use the same principal identity")
        if independence == "DISTINCT_PRINCIPAL" and author == reviewer:
            errors.append("DISTINCT_PRINCIPAL review requires distinct principal identities")

    for criterion_id, criterion in review["common_criteria"].items():
        applicability = criterion["applicability"]
        result = criterion["result"]
        if applicability == "REQUIRED" and result in {"NOT_APPLICABLE", "WAIVED"}:
            errors.append(f"{criterion_id}: REQUIRED criterion cannot be {result}")
        if result == "PASS" and not criterion.get("evidence_refs"):
            errors.append(f"{criterion_id}: PASS requires at least one evidence_ref")

    if review.get("result") == "COMPLETE":
        if review.get("unresolved_required_findings", 0) != 0:
            errors.append("COMPLETE review cannot have unresolved required findings")
        if not review.get("final_candidate"):
            errors.append("COMPLETE review requires final_candidate")
        for criterion_id, criterion in review["common_criteria"].items():
            if criterion["applicability"] == "REQUIRED" and criterion["result"] != "PASS":
                errors.append(
                    f"{criterion_id}: COMPLETE review requires PASS for REQUIRED criterion"
                )

    return errors


def review_basis_errors(
    profile: Any,
    assessment_context: Any,
    governing_basis: Any | None = None,
    repo_root: Path | None = None,
) -> list[str]:
    errors = validate_common_profile(profile)
    errors.extend(validate_assessment_context(assessment_context))
    if errors:
        return errors

    review = profile["review_profile"]
    role = review["role"]
    version = assessment_context["schema_version"]

    if role == "SELF_REVIEW":
        if version != "SELF_CHECK_CONTEXT_V1":
            errors.append("SELF_REVIEW requires SELF_CHECK_CONTEXT_V1")
        else:
            principal = assessment_context["principal"]
            if principal["identity"] != review["review_principal"]:
                errors.append("self-check principal identity must match review_principal")
            if governing_basis is None or repo_root is None:
                errors.append(
                    "SELF_REVIEW requires source-bound governing basis and repository root"
                )
            else:
                basis_errors = validate_self_check_basis(
                    governing_basis,
                    repo_root,
                )
                errors.extend(basis_errors)
                if not basis_errors:
                    errors.extend(
                        self_check_binding_errors(
                            assessment_context,
                            governing_basis,
                        )
                    )
    else:
        if version != "REVIEW_CONTEXT_V1":
            errors.append(f"{role} requires REVIEW_CONTEXT_V1")
        else:
            reviewer = assessment_context["reviewer"]
            if reviewer["identity"] != review["review_principal"]:
                errors.append("review-context reviewer identity must match review_principal")
            expected = (
                "DEGRADED"
                if review["principal_independence"] == "DEGRADED"
                else "DISTINCT"
            )
            if reviewer["principal_independence"] != expected:
                errors.append(
                    "review-context independence must match Common Review Profile"
                )

    final_candidate = review.get("final_candidate")
    if final_candidate and assessment_context["candidate_sha"] != final_candidate:
        errors.append("assessment context candidate must equal profile final_candidate")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a Common Review Profile and selected assessment context. "
            "This validates review basis only and never emits engineering PASS "
            "or lifecycle advancement."
        )
    )
    parser.add_argument("profile")
    parser.add_argument("assessment_context")
    parser.add_argument(
        "--governing-basis",
        help="YAML frozen basis required for SELF_REVIEW source-bound validation",
    )
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    with Path(args.profile).open("r", encoding="utf-8") as fh:
        profile = yaml.safe_load(fh)
    with Path(args.assessment_context).open("r", encoding="utf-8") as fh:
        context = yaml.safe_load(fh)

    basis = None
    if args.governing_basis:
        with Path(args.governing_basis).open("r", encoding="utf-8") as fh:
            basis = yaml.safe_load(fh)

    errors = review_basis_errors(
        profile,
        context,
        basis,
        Path(args.repo_root).resolve(),
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print("OK: review basis/context is coherent; no acceptance decision emitted")


if __name__ == "__main__":
    main()
