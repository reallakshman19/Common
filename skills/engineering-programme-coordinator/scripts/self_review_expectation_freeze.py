#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from l0_task_obligations import manifest_semantic_errors as l0_manifest_semantic_errors
from l1_baseline_obligations import manifest_semantic_errors as l1_manifest_semantic_errors
from l2_diff_impact import validate_manifest_shape as validate_l2_manifest_shape
from review_basis import validate_common_profile


LAYER_ORDER = ("L0", "L1", "L2")
SCHEMA_BY_LAYER = {
    "L0": "l0-task-obligation-manifest",
    "L1": "l1-baseline-obligation-manifest",
}
EXPECTED_SCHEMA_VERSION = {
    "L0": "L0_TASK_OBLIGATION_MANIFEST_V1",
    "L1": "L1_BASELINE_OBLIGATION_MANIFEST_V1",
    "L2": "L2_IMPACT_OBLIGATION_MANIFEST_V1",
}
AUTHORITY_BOUNDARIES = {
    "consumes_candidate_diff_via_l2": True,
    "consumes_exact_candidate_evidence": False,
    "consumes_coder_rationale": False,
    "consumes_coder_confidence": False,
    "consumes_prior_self_review": False,
    "consumes_review_result": False,
    "emits_engineering_pass": False,
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


def review_planning_basis(profile: Any) -> dict[str, Any]:
    errors = validate_common_profile(profile, "self-review-profile")
    if errors:
        raise ValueError("; ".join(errors))
    review = profile["review_profile"]
    if review["role"] != "SELF_REVIEW":
        raise ValueError("expectation/challenge freeze requires SELF_REVIEW profile")

    criteria: dict[str, Any] = {}
    for criterion_id in sorted(review["common_criteria"]):
        criterion = review["common_criteria"][criterion_id]
        projected = {"applicability": criterion["applicability"]}
        if "applicability_basis" in criterion:
            projected["applicability_basis"] = criterion["applicability_basis"]
        criteria[criterion_id] = projected

    basis = {
        "common_protocol": copy.deepcopy(review["common_protocol"]),
        "project_protocol": copy.deepcopy(review["project_protocol"]),
        "role": "SELF_REVIEW",
        "common_criteria": criteria,
        "project_method_ids": sorted(review["project_method_ids"]),
        "specialist_required": sorted(review.get("specialist_required", [])),
        "final_candidate": review["final_candidate"],
    }
    return basis


def review_planning_digest(profile: Any) -> str:
    return canonical_digest(review_planning_basis(profile))


def _manifest_input_errors(
    layer: str,
    manifest: Any,
    label: str,
) -> list[str]:
    if layer in SCHEMA_BY_LAYER:
        errors = schema_validate(SCHEMA_BY_LAYER[layer], manifest, label)
        if errors:
            return errors
        semantic = (
            l0_manifest_semantic_errors(manifest)
            if layer == "L0"
            else l1_manifest_semantic_errors(manifest)
        )
        return [f"{label}: {error}" for error in semantic]
    if layer == "L2":
        return validate_l2_manifest_shape(manifest, label)
    return [f"{label}: unsupported layer {layer}"]


def _manifest_summary(layer: str, manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": manifest["schema_version"],
        "task_id": manifest["identity"]["task_id"],
        "manifest_digest": manifest["manifest_digest"],
    }


def _evidence_requirements(obligation: dict[str, Any]) -> list[dict[str, Any]]:
    value = obligation["evidence_required"]
    if isinstance(value, list):
        return copy.deepcopy(value)
    return [copy.deepcopy(value)]


def _collect_obligations(
    manifests: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    expectations: list[dict[str, Any]] = []
    challenges: list[dict[str, Any]] = []
    seen: set[str] = set()

    for layer in LAYER_ORDER:
        for obligation in manifests[layer]["obligations"]:
            obligation_id = obligation["id"]
            if obligation_id in seen:
                raise ValueError(
                    f"duplicate obligation id across freeze layers: {obligation_id}"
                )
            seen.add(obligation_id)
            expectations.append(
                {
                    "layer": layer,
                    "obligation_id": obligation_id,
                    "severity": obligation["severity"],
                    "claim": copy.deepcopy(obligation["claim"]),
                    "expected_observation": obligation["expected_observation"],
                    "source_refs": copy.deepcopy(obligation["source_refs"]),
                }
            )
            challenges.append(
                {
                    "challenge_id": f"CH-{layer}-{obligation_id}",
                    "layer": layer,
                    "obligation_id": obligation_id,
                    "plausible_green_but_wrong": obligation[
                        "plausible_green_but_wrong"
                    ],
                    "oracle_refs": copy.deepcopy(obligation["oracle_refs"]),
                    "evidence_requirements": _evidence_requirements(obligation),
                }
            )
    return expectations, challenges


def compile_freeze(
    responsibility_id: str,
    l0_manifest: Any,
    l1_manifest: Any,
    l2_manifest: Any,
    profile: Any,
) -> dict[str, Any]:
    manifests = {
        "L0": l0_manifest,
        "L1": l1_manifest,
        "L2": l2_manifest,
    }
    for layer, manifest in manifests.items():
        errors = _manifest_input_errors(
            layer,
            manifest,
            f"{layer.lower()}-manifest",
        )
        if errors:
            raise ValueError("; ".join(errors))
        if manifest["schema_version"] != EXPECTED_SCHEMA_VERSION[layer]:
            raise ValueError(
                f"{layer} manifest schema_version does not match freeze contract"
            )

    planning = review_planning_basis(profile)
    candidate_sha = l2_manifest["candidate"]["head_sha"]
    base_sha = l2_manifest["candidate"]["base_sha"]
    if planning["final_candidate"] != candidate_sha:
        raise ValueError(
            "SELF_REVIEW final_candidate must equal L2 exact candidate head"
        )

    expectations, challenges = _collect_obligations(manifests)

    review_basis = copy.deepcopy(planning)
    review_basis["digest"] = canonical_digest(planning)
    result = {
        "schema_version": "SELF_REVIEW_EXPECTATION_CHALLENGE_FREEZE_V1",
        "authority": "FROZEN_SELF_REVIEW_EXPECTATIONS",
        "identity": {
            "responsibility_id": responsibility_id,
            "base_sha": base_sha,
            "candidate_sha": candidate_sha,
        },
        "source_manifests": {
            "l0": _manifest_summary("L0", l0_manifest),
            "l1": _manifest_summary("L1", l1_manifest),
            "l2": _manifest_summary("L2", l2_manifest),
        },
        "review_basis": review_basis,
        "expectations": expectations,
        "challenges": challenges,
        "freeze": {
            "state": "FROZEN",
            "stage": "SELF_REVIEW_START",
            "candidate_evidence_consumed": False,
            "coder_rationale_consumed": False,
            "coder_confidence_consumed": False,
            "prior_self_review_consumed": False,
            "review_result_consumed": False,
        },
        "authority_boundaries": copy.deepcopy(AUTHORITY_BOUNDARIES),
    }
    result["freeze_digest"] = object_digest(result, "freeze_digest")
    errors = validate_freeze_shape(result, "compiled-freeze")
    if errors:
        raise ValueError("; ".join(errors))
    return result


def freeze_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["freeze_digest"] != object_digest(value, "freeze_digest"):
        errors.append("freeze_digest does not match canonical freeze content")

    planning = copy.deepcopy(value["review_basis"])
    stored_planning_digest = planning.pop("digest")
    if stored_planning_digest != canonical_digest(planning):
        errors.append("review_basis.digest does not match planning fields")

    expectation_ids = [row["obligation_id"] for row in value["expectations"]]
    challenge_ids = [row["obligation_id"] for row in value["challenges"]]
    if len(expectation_ids) != len(set(expectation_ids)):
        errors.append("expectation obligation ids must be globally unique")
    if len(challenge_ids) != len(set(challenge_ids)):
        errors.append("challenge obligation ids must be globally unique")
    if expectation_ids != challenge_ids:
        errors.append("expectations and challenges must cover identical obligations in order")

    unique_challenge_ids = [row["challenge_id"] for row in value["challenges"]]
    if len(unique_challenge_ids) != len(set(unique_challenge_ids)):
        errors.append("challenge ids must be globally unique")

    if value["identity"]["candidate_sha"] != value["review_basis"]["final_candidate"]:
        errors.append("freeze candidate must equal review-basis final_candidate")

    for layer, key in (("L0", "l0"), ("L1", "l1"), ("L2", "l2")):
        if value["source_manifests"][key]["schema_version"] != EXPECTED_SCHEMA_VERSION[layer]:
            errors.append(f"{key} source manifest schema_version is not canonical")

    if value["authority_boundaries"] != AUTHORITY_BOUNDARIES:
        errors.append("freeze authority boundaries do not match fixed contract")
    return errors


def validate_freeze_shape(
    value: Any,
    label: str = "self-review-expectation-freeze",
) -> list[str]:
    errors = schema_validate("self-review-expectation-freeze", value, label)
    if errors:
        return errors
    return [
        f"{label}: {error}"
        for error in freeze_semantic_errors(value)
    ]


def validate_freeze(
    value: Any,
    l0_manifest: Any | None = None,
    l1_manifest: Any | None = None,
    l2_manifest: Any | None = None,
    profile: Any | None = None,
    label: str = "self-review-expectation-freeze",
) -> list[str]:
    errors = validate_freeze_shape(value, label)
    if errors:
        return errors
    if any(item is None for item in (l0_manifest, l1_manifest, l2_manifest, profile)):
        return [f"{label}: source-bound fresh replay is required"]

    try:
        fresh = compile_freeze(
            value["identity"]["responsibility_id"],
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
        )
    except Exception as exc:
        return [f"{label}: fresh replay failed: {exc}"]

    if fresh != value:
        errors.append(f"{label}: stored freeze does not equal fresh source replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compile or validate a source-bound solo self-review expectation/challenge "
            "freeze. The artifact is planning/falsification only and emits no verdict."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("responsibility_id")
    compile_parser.add_argument("l0_manifest")
    compile_parser.add_argument("l1_manifest")
    compile_parser.add_argument("l2_manifest")
    compile_parser.add_argument("profile")
    compile_parser.add_argument("--output")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("freeze")
    validate_parser.add_argument("l0_manifest")
    validate_parser.add_argument("l1_manifest")
    validate_parser.add_argument("l2_manifest")
    validate_parser.add_argument("profile")

    args = parser.parse_args()
    l0_manifest = load_yaml(Path(args.l0_manifest))
    l1_manifest = load_yaml(Path(args.l1_manifest))
    l2_manifest = load_yaml(Path(args.l2_manifest))
    profile = load_yaml(Path(args.profile))

    if args.command == "compile":
        result = compile_freeze(
            args.responsibility_id,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
        )
        rendered = dump_yaml(result)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    value = load_yaml(Path(args.freeze))
    errors = validate_freeze(
        value,
        l0_manifest,
        l1_manifest,
        l2_manifest,
        profile,
        Path(args.freeze).name,
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        "OK: self-review expectation/challenge freeze equals fresh source replay; "
        "no acceptance decision emitted"
    )


if __name__ == "__main__":
    main()
