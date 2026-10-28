#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from review_basis import validate_assessment_context, validate_common_profile


AUTHORITY_BOUNDARIES = {
    "emits_independent_review_verdict": False,
    "emits_engineering_pass": False,
    "emits_evidence_gate_decision": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def object_digest(value: dict[str, Any], field: str) -> str:
    payload = copy.deepcopy(value)
    payload.pop(field, None)
    return canonical_digest(payload)


def profile_identity_projection(profile: dict[str, Any]) -> dict[str, Any]:
    review = profile["review_profile"]
    projected = {
        "role": review["role"],
        "author_principal": review["author_principal"],
        "review_principal": review["review_principal"],
        "principal_independence": review["principal_independence"],
        "context_reset": review["context_reset"],
    }
    if "final_candidate" in review:
        projected["final_candidate"] = review["final_candidate"]
    return projected


def context_identity_projection(context: dict[str, Any]) -> dict[str, Any]:
    version = context["schema_version"]
    if version == "SELF_CHECK_CONTEXT_V1":
        principal = context["principal"]
        return {
            "schema_version": version,
            "candidate_sha": context["candidate_sha"],
            "principal": {
                "identity": principal["identity"],
                "principal_independence": principal["principal_independence"],
                "fresh_reconstruction": principal["fresh_reconstruction"],
                "blindness_claim": principal["blindness_claim"],
            },
        }
    if version == "REVIEW_CONTEXT_V1":
        reviewer = context["reviewer"]
        return {
            "schema_version": version,
            "candidate_sha": context["candidate_sha"],
            "reviewer": {
                "kind": reviewer["kind"],
                "identity": reviewer["identity"],
                "principal_independence": reviewer["principal_independence"],
                "fresh_context": reviewer["fresh_context"],
            },
        }
    raise ValueError(f"unsupported assessment context schema_version: {version!r}")


def _source_context_independence(context: dict[str, Any]) -> str:
    if context["schema_version"] == "SELF_CHECK_CONTEXT_V1":
        return context["principal"]["principal_independence"]
    return context["reviewer"]["principal_independence"]


def compile_truth(
    profile: Any,
    context: Any,
) -> dict[str, Any]:
    profile_errors = validate_common_profile(profile, "common-review-profile")
    if profile_errors:
        raise ValueError("; ".join(profile_errors))
    context_errors = validate_assessment_context(context, "assessment-context")
    if context_errors:
        raise ValueError("; ".join(context_errors))

    review = profile["review_profile"]
    role = review["role"]
    author = review["author_principal"]
    reviewer = review["review_principal"]
    relationship = (
        "SAME_PRINCIPAL" if author == reviewer else "DISTINCT_PRINCIPAL"
    )
    candidate_sha = context["candidate_sha"]

    if review.get("final_candidate") and review["final_candidate"] != candidate_sha:
        raise ValueError(
            "assessment context candidate must equal Common Review Profile final_candidate"
        )

    legacy_degraded = False
    if role == "SELF_REVIEW":
        if context["schema_version"] != "SELF_CHECK_CONTEXT_V1":
            raise ValueError("SELF_REVIEW requires SELF_CHECK_CONTEXT_V1")
        principal = context["principal"]
        if author != reviewer:
            raise ValueError(
                "SELF_REVIEW cannot use distinct author and review principals"
            )
        if principal["identity"] != reviewer:
            raise ValueError(
                "SELF_CHECK_CONTEXT principal identity must equal review_principal"
            )
        if review["principal_independence"] != "NONE":
            raise ValueError(
                "SELF_REVIEW source profile must record principal_independence NONE"
            )
        if principal["principal_independence"] != "NONE":
            raise ValueError(
                "SELF_CHECK_CONTEXT must record principal_independence NONE"
            )
        if not principal["fresh_reconstruction"]:
            raise ValueError("SELF_REVIEW requires fresh reconstruction")
        review_mode = "SELF_REVIEW"
        canonical_independence = "NONE"
        context_separation = "SELF_CHECK_FRESH_RECONSTRUCTION"
        methodological = "FRESH_RECONSTRUCTION_ONLY"
    else:
        if context["schema_version"] != "REVIEW_CONTEXT_V1":
            raise ValueError(f"{role} requires REVIEW_CONTEXT_V1")
        ctx = context["reviewer"]
        if ctx["identity"] != reviewer:
            raise ValueError(
                "REVIEW_CONTEXT reviewer identity must equal review_principal"
            )
        if not ctx["fresh_context"]:
            raise ValueError("governed review requires fresh context")
        review_mode = "GOVERNED_REVIEW"
        if relationship == "SAME_PRINCIPAL":
            if review["principal_independence"] != "DEGRADED":
                raise ValueError(
                    "same-principal governed review requires legacy DEGRADED profile input"
                )
            if ctx["kind"] != "SAME_PRINCIPAL_FRESH_CONTEXT":
                raise ValueError(
                    "same-principal governed review requires SAME_PRINCIPAL_FRESH_CONTEXT"
                )
            if ctx["principal_independence"] != "DEGRADED":
                raise ValueError(
                    "same-principal governed review requires legacy DEGRADED context input"
                )
            canonical_independence = "NONE"
            context_separation = "GOVERNED_SAME_PRINCIPAL_FRESH_CONTEXT"
            methodological = "FRESH_RECONSTRUCTION_ONLY"
            legacy_degraded = True
        else:
            if review["principal_independence"] != "DISTINCT_PRINCIPAL":
                raise ValueError(
                    "distinct-principal governed review requires DISTINCT_PRINCIPAL profile input"
                )
            if ctx["kind"] not in {"DISTINCT_PRINCIPAL", "HUMAN_REVIEWER"}:
                raise ValueError(
                    "distinct-principal governed review requires DISTINCT_PRINCIPAL or HUMAN_REVIEWER context kind"
                )
            if ctx["principal_independence"] != "DISTINCT":
                raise ValueError(
                    "distinct-principal governed review requires legacy DISTINCT context input"
                )
            canonical_independence = "DISTINCT_PRINCIPAL"
            context_separation = "GOVERNED_DISTINCT_PRINCIPAL_FRESH_CONTEXT"
            methodological = "DISTINCT_PRINCIPAL_AND_FRESH_RECONSTRUCTION"

    result = {
        "schema_version": "PRINCIPAL_INDEPENDENCE_TRUTH_V1",
        "authority": "DERIVED_PRINCIPAL_IDENTITY_TRUTH",
        "candidate_sha": candidate_sha,
        "source": {
            "profile_identity_digest": canonical_digest(
                profile_identity_projection(profile)
            ),
            "context_identity_digest": canonical_digest(
                context_identity_projection(context)
            ),
            "profile_input_independence": review["principal_independence"],
            "context_input_independence": _source_context_independence(context),
        },
        "review_mode": review_mode,
        "review_role": role,
        "principals": {
            "author": author,
            "reviewer": reviewer,
            "relationship": relationship,
            "principal_independence": canonical_independence,
        },
        "separation": {
            "fresh_context": True,
            "context_separation": context_separation,
            "methodological_separation": methodological,
        },
        "compatibility": {
            "legacy_degraded_input_consumed": legacy_degraded,
            "legacy_labels_are_authority": False,
        },
        "oracle_independence": {
            "derived_from_principal_identity": False,
            "project_oracle_requirement_preserved": True,
        },
        "authority_boundaries": copy.deepcopy(AUTHORITY_BOUNDARIES),
    }
    result["truth_digest"] = object_digest(result, "truth_digest")
    errors = validate_truth_shape(result, "compiled-principal-independence-truth")
    if errors:
        raise ValueError("; ".join(errors))
    return result


def truth_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["truth_digest"] != object_digest(value, "truth_digest"):
        errors.append("truth_digest does not match canonical truth content")

    principals = value["principals"]
    same = principals["author"] == principals["reviewer"]
    expected_relationship = (
        "SAME_PRINCIPAL" if same else "DISTINCT_PRINCIPAL"
    )
    if principals["relationship"] != expected_relationship:
        errors.append("principal relationship does not match principal identities")

    expected_independence = "NONE" if same else "DISTINCT_PRINCIPAL"
    if principals["principal_independence"] != expected_independence:
        errors.append(
            "canonical principal_independence does not match principal identity truth"
        )
    if principals["principal_independence"] == "NONE" and value["separation"][
        "methodological_separation"
    ] != "FRESH_RECONSTRUCTION_ONLY":
        errors.append(
            "same-principal truth may record only fresh-reconstruction methodological separation"
        )
    if (
        principals["principal_independence"] == "DISTINCT_PRINCIPAL"
        and value["separation"]["methodological_separation"]
        != "DISTINCT_PRINCIPAL_AND_FRESH_RECONSTRUCTION"
    ):
        errors.append(
            "distinct-principal truth must preserve both principal and reconstruction separation"
        )

    if value["review_mode"] == "SELF_REVIEW":
        if value["review_role"] != "SELF_REVIEW":
            errors.append("SELF_REVIEW mode requires SELF_REVIEW role")
        if not same:
            errors.append("SELF_REVIEW mode must be same principal")
        if value["separation"]["context_separation"] != "SELF_CHECK_FRESH_RECONSTRUCTION":
            errors.append("SELF_REVIEW must record self-check fresh reconstruction context")
        if value["compatibility"]["legacy_degraded_input_consumed"]:
            errors.append("SELF_REVIEW cannot consume legacy DEGRADED label")
    else:
        if value["review_role"] not in {"REVIEWER", "SUPER_REVIEWER"}:
            errors.append("GOVERNED_REVIEW requires REVIEWER or SUPER_REVIEWER role")
        expected_context = (
            "GOVERNED_SAME_PRINCIPAL_FRESH_CONTEXT"
            if same
            else "GOVERNED_DISTINCT_PRINCIPAL_FRESH_CONTEXT"
        )
        if value["separation"]["context_separation"] != expected_context:
            errors.append("governed-review context separation does not match identity truth")
        if same and not value["compatibility"]["legacy_degraded_input_consumed"]:
            errors.append(
                "same-principal governed review must expose consumed DEGRADED compatibility input"
            )
        if not same and value["compatibility"]["legacy_degraded_input_consumed"]:
            errors.append(
                "distinct-principal governed review cannot consume DEGRADED compatibility input"
            )

    if value["authority_boundaries"] != AUTHORITY_BOUNDARIES:
        errors.append("authority boundaries do not match fixed contract")
    if value["oracle_independence"]["derived_from_principal_identity"]:
        errors.append("oracle independence must not be derived from principal identity")
    return errors


def validate_truth_shape(
    value: Any,
    label: str = "principal-independence-truth",
) -> list[str]:
    errors = schema_validate("principal-independence-truth", value, label)
    if errors:
        return errors
    return [
        f"{label}: {error}"
        for error in truth_semantic_errors(value)
    ]


def validate_truth(
    value: Any,
    profile: Any | None = None,
    context: Any | None = None,
    label: str = "principal-independence-truth",
) -> list[str]:
    errors = validate_truth_shape(value, label)
    if errors:
        return errors
    if profile is None or context is None:
        return [f"{label}: source-bound fresh replay is required"]
    try:
        fresh = compile_truth(profile, context)
    except Exception as exc:
        return [f"{label}: fresh replay failed: {exc}"]
    if fresh != value:
        errors.append(f"{label}: stored truth does not equal fresh source replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Derive canonical principal-independence truth from an existing Common "
            "Review Profile and assessment context without rewriting source records."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("profile")
    compile_parser.add_argument("context")
    compile_parser.add_argument("--output")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("truth")
    validate_parser.add_argument("profile")
    validate_parser.add_argument("context")

    args = parser.parse_args()
    profile = load_yaml(Path(args.profile))
    context = load_yaml(Path(args.context))

    if args.command == "compile":
        result = compile_truth(profile, context)
        rendered = dump_yaml(result)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    value = load_yaml(Path(args.truth))
    errors = validate_truth(
        value,
        profile,
        context,
        Path(args.truth).name,
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        "OK: principal identity truth equals fresh source replay; "
        "fresh context does not manufacture principal independence"
    )


if __name__ == "__main__":
    main()
