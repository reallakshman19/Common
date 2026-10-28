#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from review_basis import validate_common_profile
from self_review_expectation_freeze import validate_freeze


SKILLS = Path(__file__).resolve().parents[2]
PROJECT_PROTOCOL_SCHEMA = (
    SKILLS
    / "Local_PR_Deliverty_v1.1"
    / "schemas"
    / "project-protocol.schema.json"
)

AUTHORITY_BOUNDARIES = {
    "consumes_expectation_challenge_freeze": True,
    "consumes_project_protocol": True,
    "consumes_same_principal_method_observations": True,
    "claims_principal_independence": False,
    "emits_engineering_pass": False,
    "emits_project_acceptance_pass": False,
    "emits_evidence_gate_decision": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}

RESULT_STATES = ("PASS", "FAIL", "NOT_RUN", "INCONCLUSIVE")


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


def project_protocol_digest(protocol: dict[str, Any]) -> str:
    payload = copy.deepcopy(protocol)
    payload.pop("digest", None)
    return canonical_digest(payload)


def _schema_errors(
    schema: dict[str, Any],
    value: Any,
    label: str,
) -> list[str]:
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        where = ".".join(str(part) for part in error.path)
        errors.append(f"{label}{'.' + where if where else ''}: {error.message}")
    return errors


def project_protocol_semantic_errors(protocol: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if protocol["digest"] != project_protocol_digest(protocol):
        errors.append("project protocol digest does not match canonical visible content")

    protected = protocol["protected_surface"]
    expected_manifest_digest = canonical_digest(protected["manifest"])
    if protected["manifest_digest"] != expected_manifest_digest:
        errors.append(
            "protected-surface manifest_digest does not match canonical manifest content"
        )

    for label, rows in (
        ("verification method", protocol["verification_methods"]),
        ("harness", protocol["harnesses"]),
        ("external gate", protocol["external_gates"]),
    ):
        ids = [row["id"] for row in rows]
        duplicates = sorted({item for item in ids if ids.count(item) > 1})
        if duplicates:
            errors.append(f"{label} ids must be unique: " + ", ".join(duplicates))

    manifest_ids = [row["id"] for row in protected["manifest"]]
    duplicates = sorted({item for item in manifest_ids if manifest_ids.count(item) > 1})
    if duplicates:
        errors.append(
            "protected-surface manifest ids must be unique: " + ", ".join(duplicates)
        )
    return errors


def validate_project_protocol(
    protocol: Any,
    label: str = "project-protocol",
) -> list[str]:
    schema = json.loads(PROJECT_PROTOCOL_SCHEMA.read_text(encoding="utf-8"))
    errors = _schema_errors(schema, protocol, label)
    if errors:
        return errors
    return [
        f"{label}: {error}"
        for error in project_protocol_semantic_errors(protocol)
    ]


def _criteria_for_method(
    protocol: dict[str, Any],
    method_id: str,
) -> list[str]:
    ids: set[str] = set()
    for acceptance_set in protocol["acceptance_sets"]:
        for criterion in acceptance_set["criteria"]:
            if method_id in criterion["verification_method_ids"]:
                ids.add(criterion["id"])
    return sorted(ids)


def _resolve_unique(
    rows: list[dict[str, Any]],
    row_id: str,
    label: str,
) -> dict[str, Any]:
    matches = [row for row in rows if row["id"] == row_id]
    if len(matches) != 1:
        raise ValueError(
            f"{label} {row_id!r} must resolve exactly once; found {len(matches)}"
        )
    return matches[0]


def resolve_method_plan(
    profile: dict[str, Any],
    protocol: dict[str, Any],
) -> list[dict[str, Any]]:
    review = profile["review_profile"]
    method_ids = list(review["project_method_ids"])
    if not method_ids:
        raise ValueError(
            "project-outcome falsification requires at least one project_method_id"
        )
    if len(method_ids) != len(set(method_ids)):
        raise ValueError("project_method_ids must be unique")

    plan: list[dict[str, Any]] = []
    for method_id in sorted(method_ids):
        method = _resolve_unique(
            protocol["verification_methods"],
            method_id,
            "project verification method",
        )
        criterion_ids = _criteria_for_method(protocol, method_id)

        harness_refs: list[str] = []
        if method["harness_id"] is not None:
            harness = _resolve_unique(
                protocol["harnesses"],
                method["harness_id"],
                "project harness",
            )
            if method_id not in harness["verification_method_ids"]:
                raise ValueError(
                    f"{method_id}: bound harness does not declare the verification method"
                )
            harness_refs = sorted(harness["manifest_refs"])

        if method["external_gate_id"] is not None:
            _resolve_unique(
                protocol["external_gates"],
                method["external_gate_id"],
                "project external gate",
            )

        if not criterion_ids and method["external_gate_id"] is None:
            raise ValueError(
                f"{method_id}: selected project method is not connected to a criterion or external gate"
            )

        plan.append(
            {
                "method_id": method_id,
                "verification_class": method["verification_class"],
                "criterion_ids": criterion_ids,
                "harness_id": method["harness_id"],
                "external_gate_id": method["external_gate_id"],
                "harness_manifest_refs": harness_refs,
                "required_evidence_classes": sorted(
                    method["required_evidence_classes"]
                ),
                "material_inputs": sorted(method["material_inputs"]),
                "rerun_policy": method["rerun_policy"],
                "applies_to_roles": sorted(method["applies_to_roles"]),
            }
        )
    return plan


def observation_errors(
    observations: Any,
    selected_method_ids: list[str],
    candidate_sha: str,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(observations, list):
        return ["observations must be an array"]

    ids: list[str] = []
    for index, observation in enumerate(observations):
        if not isinstance(observation, dict):
            errors.append(f"observation[{index}] must be an object")
            continue
        method_id = observation.get("method_id")
        if isinstance(method_id, str):
            ids.append(method_id)
        if observation.get("candidate_sha") != candidate_sha:
            errors.append(
                f"observation[{index}]: candidate_sha must equal exact freeze candidate"
            )
        result = observation.get("result")
        evidence_refs = observation.get("evidence_refs")
        limitation = observation.get("limitation")
        if result in {"PASS", "FAIL", "INCONCLUSIVE"}:
            if not isinstance(evidence_refs, list) or len(evidence_refs) < 1:
                errors.append(
                    f"observation[{index}]: {result} requires at least one evidence_ref"
                )
        if result == "NOT_RUN":
            if not isinstance(limitation, str) or not limitation.strip():
                errors.append(
                    f"observation[{index}]: NOT_RUN requires a concrete limitation"
                )

    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("method observations must be unique: " + ", ".join(duplicates))

    expected = sorted(selected_method_ids)
    actual = sorted(ids)
    if actual != expected:
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        if missing:
            errors.append("missing selected method observations: " + ", ".join(missing))
        if extra:
            errors.append("unexpected method observations: " + ", ".join(extra))
    return errors


def _status(counts: dict[str, int]) -> str:
    if counts["FAIL"]:
        return "FALSIFIED"
    if counts["INCONCLUSIVE"]:
        return "INCONCLUSIVE"
    if counts["NOT_RUN"]:
        return "NOT_RUN"
    return "NOT_FALSIFIED"


def compile_result(
    responsibility_id: str,
    freeze: Any,
    l0_manifest: Any,
    l1_manifest: Any,
    l2_manifest: Any,
    profile: Any,
    project_protocol: Any,
    observations: Any,
) -> dict[str, Any]:
    freeze_errors = validate_freeze(
        freeze,
        l0_manifest,
        l1_manifest,
        l2_manifest,
        profile,
        "expectation-freeze",
    )
    if freeze_errors:
        raise ValueError("; ".join(freeze_errors))

    profile_errors = validate_common_profile(profile, "self-review-profile")
    if profile_errors:
        raise ValueError("; ".join(profile_errors))
    review = profile["review_profile"]
    if review["role"] != "SELF_REVIEW":
        raise ValueError("project-outcome falsification requires SELF_REVIEW profile")

    protocol_errors = validate_project_protocol(project_protocol)
    if protocol_errors:
        raise ValueError("; ".join(protocol_errors))
    if review["project_protocol"]["ref"] != project_protocol["source_ref"]:
        raise ValueError(
            "SELF_REVIEW project_protocol.ref must equal supplied Local project protocol source_ref"
        )
    if review["project_protocol"]["digest"] != project_protocol["digest"]:
        raise ValueError(
            "SELF_REVIEW project_protocol.digest must equal supplied Local project protocol digest"
        )

    if freeze["identity"]["candidate_sha"] != review["final_candidate"]:
        raise ValueError(
            "expectation freeze candidate must equal SELF_REVIEW final_candidate"
        )
    if freeze["review_basis"]["digest"] != canonical_digest(
        {
            key: copy.deepcopy(value)
            for key, value in freeze["review_basis"].items()
            if key != "digest"
        }
    ):
        raise ValueError("expectation freeze review-basis digest is invalid")

    method_plan = resolve_method_plan(profile, project_protocol)
    method_ids = [row["method_id"] for row in method_plan]
    candidate_sha = freeze["identity"]["candidate_sha"]

    obs_errors = observation_errors(observations, method_ids, candidate_sha)
    if obs_errors:
        raise ValueError("; ".join(obs_errors))

    ordered_observations = sorted(
        copy.deepcopy(observations),
        key=lambda row: row["method_id"],
    )
    counts = {
        state: sum(row["result"] == state for row in ordered_observations)
        for state in RESULT_STATES
    }
    result = {
        "schema_version": "PROJECT_OUTCOME_FALSIFICATION_RESULT_V1",
        "authority": "SAME_PRINCIPAL_PROJECT_OUTCOME_FALSIFICATION_EVIDENCE",
        "identity": {
            "responsibility_id": responsibility_id,
            "candidate_sha": candidate_sha,
        },
        "source": {
            "freeze_digest": freeze["freeze_digest"],
            "review_basis_digest": freeze["review_basis"]["digest"],
            "project_protocol_ref": project_protocol["source_ref"],
            "project_protocol_digest": project_protocol["digest"],
            "protected_surface_manifest_digest": project_protocol[
                "protected_surface"
            ]["manifest_digest"],
            "observations_digest": canonical_digest(ordered_observations),
        },
        "review_mode": "SELF_REVIEW",
        "principal_independence": "NONE",
        "method_plan": method_plan,
        "observations": ordered_observations,
        "accounting": {
            "selected_methods": len(method_plan),
            "observed_methods": len(ordered_observations),
            "result_counts": counts,
        },
        "falsification_status": _status(counts),
        "interpretation": "NON_AUTHORITATIVE_PROJECT_OUTCOME_FALSIFICATION_ONLY",
        "authority_boundaries": copy.deepcopy(AUTHORITY_BOUNDARIES),
    }
    result["result_digest"] = object_digest(result, "result_digest")
    shape_errors = validate_result_shape(result, "compiled-project-outcome-falsification")
    if shape_errors:
        raise ValueError("; ".join(shape_errors))
    return result


def result_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["result_digest"] != object_digest(value, "result_digest"):
        errors.append("result_digest does not match canonical result content")

    method_ids = [row["method_id"] for row in value["method_plan"]]
    observation_ids = [row["method_id"] for row in value["observations"]]
    if len(method_ids) != len(set(method_ids)):
        errors.append("method_plan ids must be globally unique")
    if len(observation_ids) != len(set(observation_ids)):
        errors.append("observation method ids must be globally unique")
    if method_ids != observation_ids:
        errors.append("method_plan and observations must cover identical methods in order")

    counts = value["accounting"]["result_counts"]
    observed = len(value["observations"])
    if value["accounting"]["selected_methods"] != len(value["method_plan"]):
        errors.append("selected_methods does not equal method_plan count")
    if value["accounting"]["observed_methods"] != observed:
        errors.append("observed_methods does not equal observation count")
    if sum(counts.values()) != observed:
        errors.append("result_counts do not close the observation denominator")
    for state in RESULT_STATES:
        actual = sum(row["result"] == state for row in value["observations"])
        if counts[state] != actual:
            errors.append(f"result_counts.{state} does not match observations")

    expected_status = _status(counts)
    if value["falsification_status"] != expected_status:
        errors.append("falsification_status does not match method observations")

    if value["authority_boundaries"] != AUTHORITY_BOUNDARIES:
        errors.append("authority boundaries do not match fixed contract")
    return errors


def validate_result_shape(
    value: Any,
    label: str = "project-outcome-falsification-result",
) -> list[str]:
    errors = schema_validate("project-outcome-falsification", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in result_semantic_errors(value)]


def validate_result(
    value: Any,
    responsibility_id: str | None = None,
    freeze: Any | None = None,
    l0_manifest: Any | None = None,
    l1_manifest: Any | None = None,
    l2_manifest: Any | None = None,
    profile: Any | None = None,
    project_protocol: Any | None = None,
    observations: Any | None = None,
    label: str = "project-outcome-falsification-result",
) -> list[str]:
    errors = validate_result_shape(value, label)
    if errors:
        return errors
    if any(
        item is None
        for item in (
            responsibility_id,
            freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
            project_protocol,
            observations,
        )
    ):
        return [f"{label}: source-bound fresh replay is required"]

    try:
        fresh = compile_result(
            responsibility_id,
            freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
            project_protocol,
            observations,
        )
    except Exception as exc:
        return [f"{label}: fresh replay failed: {exc}"]
    if fresh != value:
        errors.append(f"{label}: stored result does not equal fresh source replay")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compile or validate a same-principal project-outcome falsification result. "
            "NOT_FALSIFIED is not engineering PASS or lifecycle authority."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    compile_parser = subparsers.add_parser("compile")
    compile_parser.add_argument("responsibility_id")
    compile_parser.add_argument("freeze")
    compile_parser.add_argument("l0_manifest")
    compile_parser.add_argument("l1_manifest")
    compile_parser.add_argument("l2_manifest")
    compile_parser.add_argument("profile")
    compile_parser.add_argument("project_protocol")
    compile_parser.add_argument("observations")
    compile_parser.add_argument("--output")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("responsibility_id")
    validate_parser.add_argument("result")
    validate_parser.add_argument("freeze")
    validate_parser.add_argument("l0_manifest")
    validate_parser.add_argument("l1_manifest")
    validate_parser.add_argument("l2_manifest")
    validate_parser.add_argument("profile")
    validate_parser.add_argument("project_protocol")
    validate_parser.add_argument("observations")

    args = parser.parse_args()
    freeze = load_yaml(Path(args.freeze))
    l0_manifest = load_yaml(Path(args.l0_manifest))
    l1_manifest = load_yaml(Path(args.l1_manifest))
    l2_manifest = load_yaml(Path(args.l2_manifest))
    profile = load_yaml(Path(args.profile))
    project_protocol = load_yaml(Path(args.project_protocol))
    observations = load_yaml(Path(args.observations))

    if args.command == "compile":
        result = compile_result(
            args.responsibility_id,
            freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
            project_protocol,
            observations,
        )
        rendered = dump_yaml(result)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    value = load_yaml(Path(args.result))
    errors = validate_result(
        value,
        args.responsibility_id,
        freeze,
        l0_manifest,
        l1_manifest,
        l2_manifest,
        profile,
        project_protocol,
        observations,
        Path(args.result).name,
    )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        "OK: same-principal project-outcome falsification result equals fresh source replay; "
        "NOT_FALSIFIED is non-authoritative"
    )


if __name__ == "__main__":
    main()
