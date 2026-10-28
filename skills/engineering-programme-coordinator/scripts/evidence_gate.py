#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from coordlib import dump_yaml, load_yaml, validate as schema_validate
from principal_independence import validate_truth
from project_outcome_falsification import validate_result as validate_falsification
from review_basis import review_basis_errors
from self_review_expectation_freeze import validate_freeze
from verdict_policy import validate_projection


AUTHORITY_BOUNDARIES = {
    "emits_engineering_pass": False,
    "emits_project_acceptance_pass": False,
    "emits_independent_review_verdict": False,
    "performs_lifecycle_advance": False,
    "grants_merge_authority": False,
    "grants_production_cutover": False,
}

INPUT_KEYS = (
    "verdict_projection",
    "self_check_context",
    "common_review_floor",
    "expectation_challenge",
    "project_falsification",
    "principal_truth",
)

BOUNDARY_REF_PREFIXES = (
    "owner://",
    "authority://",
    "provider://",
    "external://",
    "protected://",
)


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


def source_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    seen_subjects: set[str] = set()
    for row in value["local_resolution"]:
        subject_ref = row["subject_ref"]
        if subject_ref in seen_subjects:
            errors.append(
                "local_resolution subject_ref values must be unique; "
                f"duplicate {subject_ref!r}"
            )
        seen_subjects.add(subject_ref)

        if row["state"] == "LOCAL_RESOLUTION_EXHAUSTED":
            boundary_ref = row["boundary_ref"]
            if not isinstance(boundary_ref, str) or not boundary_ref.startswith(
                BOUNDARY_REF_PREFIXES
            ):
                errors.append(
                    f"{subject_ref}: exhausted local resolution requires an "
                    "owner://, authority://, provider://, external://, or "
                    "protected:// boundary_ref"
                )
    return errors


def validate_source(
    value: Any,
    label: str = "deterministic-evidence-gate-source",
) -> list[str]:
    errors = schema_validate("deterministic-evidence-gate-source", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: gate source must be an object"]
    return [f"{label}: {error}" for error in source_semantic_errors(value)]


def _actual_bindings(
    verdict_projection: dict[str, Any],
    self_check_context: dict[str, Any],
    governing_basis: dict[str, Any],
    profile: dict[str, Any],
    expectation_freeze: dict[str, Any],
    project_falsification: dict[str, Any],
    principal_truth: dict[str, Any],
) -> dict[str, dict[str, str]]:
    return {
        "verdict_projection": {
            "digest": verdict_projection["projection_digest"],
            "candidate_sha": verdict_projection["candidate"]["sha"],
        },
        "self_check_context": {
            "digest": canonical_digest(
                {
                    "context": self_check_context,
                    "governing_basis": governing_basis,
                }
            ),
            "candidate_sha": self_check_context["candidate_sha"],
        },
        "common_review_floor": {
            "digest": canonical_digest(profile),
            "candidate_sha": profile["review_profile"]["final_candidate"],
        },
        "expectation_challenge": {
            "digest": expectation_freeze["freeze_digest"],
            "candidate_sha": expectation_freeze["identity"]["candidate_sha"],
        },
        "project_falsification": {
            "digest": project_falsification["result_digest"],
            "candidate_sha": project_falsification["identity"]["candidate_sha"],
        },
        "principal_truth": {
            "digest": principal_truth["truth_digest"],
            "candidate_sha": principal_truth["candidate_sha"],
        },
    }


def _source_binding_errors(
    source: dict[str, Any],
    actual: dict[str, dict[str, str]],
) -> tuple[list[str], bool]:
    errors: list[str] = []
    candidate_mismatch = False
    candidate = source["candidate"]["sha"]

    for key in INPUT_KEYS:
        stored = source["inputs"][key]
        current = actual[key]
        if stored["candidate_sha"] != candidate:
            candidate_mismatch = True
            errors.append(f"{key}: source binding candidate_sha does not equal gate candidate")
        if current["candidate_sha"] != candidate:
            candidate_mismatch = True
            errors.append(f"{key}: current artifact candidate_sha does not equal gate candidate")
        if stored["candidate_sha"] != current["candidate_sha"]:
            candidate_mismatch = True
            errors.append(f"{key}: stored/current candidate_sha mismatch")
        if stored["digest"] != current["digest"]:
            errors.append(f"{key}: stored/current digest mismatch")

    for row in source["local_resolution"]:
        if row["candidate_sha"] != candidate:
            candidate_mismatch = True
            errors.append(
                f"{row['subject_ref']}: local-resolution candidate_sha does not equal gate candidate"
            )
    return errors, candidate_mismatch


def _fresh_replay_errors(
    *,
    verdict_projection: Any,
    verdict_source: Any,
    repo_root: Path,
    profile: Any,
    self_check_context: Any,
    governing_basis: Any,
    expectation_freeze: Any,
    l0_manifest: Any,
    l1_manifest: Any,
    l2_manifest: Any,
    project_protocol: Any,
    project_observations: Any,
    project_falsification: Any,
    principal_truth: Any,
) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []

    def extend(component: str, rows: list[str]) -> None:
        errors.extend((component, row) for row in rows)

    extend(
        "verdict_projection",
        validate_projection(
            verdict_projection,
            verdict_source,
            repo_root,
            "verdict-projection",
        ),
    )
    extend(
        "self_check_context",
        review_basis_errors(
            profile,
            self_check_context,
            governing_basis,
            repo_root,
        ),
    )
    extend(
        "expectation_challenge",
        validate_freeze(
            expectation_freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
            "expectation-freeze",
        ),
    )
    extend(
        "project_falsification",
        validate_falsification(
            project_falsification,
            project_falsification["identity"]["responsibility_id"],
            expectation_freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            profile,
            project_protocol,
            project_observations,
            "project-falsification",
        ),
    )
    extend(
        "principal_truth",
        validate_truth(
            principal_truth,
            profile,
            self_check_context,
            "principal-truth",
        ),
    )
    return errors


def _result(
    source: dict[str, Any],
    actual: dict[str, dict[str, str]],
    disposition: str,
    reason_codes: list[str],
    blocking_refs: list[str],
    unresolved_refs: list[str],
) -> dict[str, Any]:
    value = {
        "schema_version": "DETERMINISTIC_EVIDENCE_GATE_RESULT_V1",
        "authority": "EVIDENCE_GATE_DISPOSITION_ONLY",
        "candidate_sha": source["candidate"]["sha"],
        "source": {
            "source_digest": canonical_digest(source),
            "verdict_projection_digest": actual["verdict_projection"]["digest"],
            "self_check_basis_digest": actual["self_check_context"]["digest"],
            "common_review_floor_digest": actual["common_review_floor"]["digest"],
            "expectation_challenge_digest": actual["expectation_challenge"]["digest"],
            "project_falsification_digest": actual["project_falsification"]["digest"],
            "principal_truth_digest": actual["principal_truth"]["digest"],
            "local_resolution_digest": canonical_digest(source["local_resolution"]),
        },
        "disposition": disposition,
        "reason_codes": sorted(set(reason_codes)),
        "blocking_refs": sorted(set(blocking_refs)),
        "unresolved_refs": sorted(set(unresolved_refs)),
        "authority_boundaries": copy.deepcopy(AUTHORITY_BOUNDARIES),
    }
    value["result_digest"] = object_digest(value, "result_digest")
    return value


def _repair_and_unresolved_refs(
    verdict_projection: dict[str, Any],
    profile: dict[str, Any],
    project_falsification: dict[str, Any],
) -> tuple[list[str], list[str], list[str], list[str]]:
    repair_refs: list[str] = []
    unresolved_refs: list[str] = []
    repair_reasons: list[str] = []
    unresolved_reasons: list[str] = []

    critical = verdict_projection["criticality"]
    refuted_ids = critical["unresolved_refuted_ids"]
    unknown_ids = critical["unresolved_unknown_ids"]
    if refuted_ids:
        repair_reasons.append("CRITICAL_REFUTED")
        repair_refs.extend(f"obligation://{item}" for item in refuted_ids)
    if unknown_ids:
        unresolved_reasons.append("CRITICAL_UNKNOWN_LOCAL_WORK_REMAINING")
        unresolved_refs.extend(f"obligation://{item}" for item in unknown_ids)

    review = profile["review_profile"]
    for criterion_id, criterion in review["common_criteria"].items():
        if criterion["applicability"] != "REQUIRED":
            continue
        if criterion["result"] == "FAIL":
            repair_reasons.append("COMMON_CRITERION_FAIL")
            repair_refs.append(f"criterion://{criterion_id}")
        elif criterion["result"] in {"NOT_RUN", "INCONCLUSIVE"}:
            unresolved_reasons.append("REQUIRED_EVIDENCE_INCOMPLETE")
            unresolved_refs.append(f"criterion://{criterion_id}")

    for finding in review.get("findings", []):
        disposition = finding["disposition"]
        if disposition in {"FIXED_AND_REVERIFIED", "ACCEPTED_ADVISORY"}:
            continue
        ref = f"finding://{finding['id']}"
        if finding["class"] in {"BLOCKING_DEFECT", "BOUNDED_PRODUCT_FIX"} and disposition == "OPEN":
            repair_refs.append(ref)
            repair_reasons.append("REQUIRED_FINDING_OPEN")
        else:
            unresolved_refs.append(ref)
            unresolved_reasons.append("REQUIRED_EVIDENCE_INCOMPLETE")

    unresolved_required = review.get("unresolved_required_findings", 0)
    if unresolved_required and not any(ref.startswith("finding://") for ref in repair_refs + unresolved_refs):
        unresolved_refs.append("review://unresolved-required-findings")
        unresolved_reasons.append("REQUIRED_EVIDENCE_INCOMPLETE")

    review_result = review.get("result")
    if review_result != "COMPLETE" and not repair_refs and not unresolved_refs:
        unresolved_refs.append(f"review://result/{review_result or 'MISSING'}")
        unresolved_reasons.append("REQUIRED_EVIDENCE_INCOMPLETE")

    falsification_status = project_falsification["falsification_status"]
    observations = project_falsification["observations"]
    if falsification_status == "FALSIFIED":
        repair_reasons.append("PROJECT_OUTCOME_FALSIFIED")
        failed = [row["method_id"] for row in observations if row["result"] == "FAIL"]
        repair_refs.extend(
            f"project-method://{item}" for item in (failed or ["falsified"])
        )
    elif falsification_status in {"NOT_RUN", "INCONCLUSIVE"}:
        unresolved_reasons.append("REQUIRED_EVIDENCE_INCOMPLETE")
        unresolved = [
            row["method_id"]
            for row in observations
            if row["result"] in {"NOT_RUN", "INCONCLUSIVE"}
        ]
        unresolved_refs.extend(
            f"project-method://{item}" for item in (unresolved or [falsification_status.lower()])
        )

    return (
        sorted(set(repair_refs)),
        sorted(set(unresolved_refs)),
        sorted(set(repair_reasons)),
        sorted(set(unresolved_reasons)),
    )


def _all_unresolved_exhausted(
    source: dict[str, Any],
    unresolved_refs: list[str],
) -> bool:
    if not unresolved_refs:
        return False
    for ref in unresolved_refs:
        matches = [
            row
            for row in source["local_resolution"]
            if row["subject_ref"] == ref
        ]
        if len(matches) != 1:
            return False
        row = matches[0]
        if row["state"] != "LOCAL_RESOLUTION_EXHAUSTED":
            return False
        if not row["evidence_refs"] or not row["boundary_ref"]:
            return False
        if not row["boundary_ref"].startswith(BOUNDARY_REF_PREFIXES):
            return False
    return True


def compile_gate(
    source: Any,
    verdict_projection: Any,
    verdict_source: Any,
    self_check_context: Any,
    governing_basis: Any,
    profile: Any,
    expectation_freeze: Any,
    l0_manifest: Any,
    l1_manifest: Any,
    l2_manifest: Any,
    project_protocol: Any,
    project_observations: Any,
    project_falsification: Any,
    principal_truth: Any,
    repo_root: Path,
) -> dict[str, Any]:
    source_shape_errors = schema_validate(
        "deterministic-evidence-gate-source",
        source,
        "deterministic-evidence-gate-source",
    )

    try:
        actual = _actual_bindings(
            verdict_projection,
            self_check_context,
            governing_basis,
            profile,
            expectation_freeze,
            project_falsification,
            principal_truth,
        )
        candidate_sha = source["candidate"]["sha"]
        source["inputs"]
        source["local_resolution"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "gate source is not structurally readable enough to emit a safe disposition"
        ) from exc

    if source_shape_errors:
        return _checked_result(
            _result(
                source,
                actual,
                "REPLAY",
                ["SOURCE_REPLAY_INVALID"],
                [
                    f"source-shape://{index + 1}"
                    for index in range(len(source_shape_errors))
                ],
                [],
            )
        )

    source_semantic = source_semantic_errors(source)
    if source_semantic:
        return _checked_result(
            _result(
                source,
                actual,
                "REPLAY",
                ["SOURCE_REPLAY_INVALID"],
                [
                    f"source-semantic://{index + 1}"
                    for index in range(len(source_semantic))
                ],
                [],
            )
        )

    _ = candidate_sha
    binding_errors, candidate_mismatch = _source_binding_errors(source, actual)
    if binding_errors:
        reasons = ["SOURCE_REPLAY_INVALID"]
        if candidate_mismatch:
            reasons.append("CANDIDATE_MISMATCH")
        return _checked_result(
            _result(
                source,
                actual,
                "REPLAY",
                reasons,
                [f"source-binding://{index + 1}" for index in range(len(binding_errors))],
                [],
            )
        )

    replay_errors = _fresh_replay_errors(
        verdict_projection=verdict_projection,
        verdict_source=verdict_source,
        repo_root=repo_root,
        profile=profile,
        self_check_context=self_check_context,
        governing_basis=governing_basis,
        expectation_freeze=expectation_freeze,
        l0_manifest=l0_manifest,
        l1_manifest=l1_manifest,
        l2_manifest=l2_manifest,
        project_protocol=project_protocol,
        project_observations=project_observations,
        project_falsification=project_falsification,
        principal_truth=principal_truth,
    )
    if replay_errors:
        refs = [f"source-replay://{component}" for component, _ in replay_errors]
        return _checked_result(
            _result(
                source,
                actual,
                "REPLAY",
                ["SOURCE_REPLAY_INVALID"],
                refs,
                [],
            )
        )

    repair_refs, unresolved_refs, repair_reasons, unresolved_reasons = (
        _repair_and_unresolved_refs(
            verdict_projection,
            profile,
            project_falsification,
        )
    )

    if repair_refs:
        return _checked_result(
            _result(
                source,
                actual,
                "REPAIR",
                repair_reasons,
                repair_refs,
                unresolved_refs,
            )
        )

    if unresolved_refs:
        if _all_unresolved_exhausted(source, unresolved_refs):
            return _checked_result(
                _result(
                    source,
                    actual,
                    "ESCALATE",
                    ["LOCAL_RESOLUTION_EXHAUSTED", "AUTHORITY_OR_EXTERNAL_BOUNDARY"],
                    [],
                    unresolved_refs,
                )
            )
        reasons = unresolved_reasons or ["REQUIRED_EVIDENCE_INCOMPLETE"]
        return _checked_result(
            _result(
                source,
                actual,
                "REPLAY",
                reasons,
                [],
                unresolved_refs,
            )
        )

    return _checked_result(
        _result(
            source,
            actual,
            "ADVANCE_ELIGIBLE",
            ["CLOSED_CURRENT_DENOMINATOR"],
            [],
            [],
        )
    )


def result_semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if value["result_digest"] != object_digest(value, "result_digest"):
        errors.append("result_digest does not match canonical result content")
    if value["authority_boundaries"] != AUTHORITY_BOUNDARIES:
        errors.append("authority boundaries do not match fixed gate contract")

    disposition = value["disposition"]
    if disposition == "ADVANCE_ELIGIBLE":
        if value["blocking_refs"] or value["unresolved_refs"]:
            errors.append("ADVANCE_ELIGIBLE cannot carry blocking or unresolved refs")
        if value["reason_codes"] != ["CLOSED_CURRENT_DENOMINATOR"]:
            errors.append("ADVANCE_ELIGIBLE requires CLOSED_CURRENT_DENOMINATOR only")
    elif disposition == "REPAIR":
        if not value["blocking_refs"]:
            errors.append("REPAIR requires at least one blocking_ref")
    elif disposition == "ESCALATE":
        if not value["unresolved_refs"]:
            errors.append("ESCALATE requires at least one unresolved_ref")
        required = {"LOCAL_RESOLUTION_EXHAUSTED", "AUTHORITY_OR_EXTERNAL_BOUNDARY"}
        if not required.issubset(set(value["reason_codes"])):
            errors.append("ESCALATE requires exhaustion and boundary reason codes")
    return errors


def validate_result_shape(
    value: Any,
    label: str = "deterministic-evidence-gate-result",
) -> list[str]:
    errors = schema_validate("deterministic-evidence-gate-result", value, label)
    if errors:
        return errors
    return [f"{label}: {error}" for error in result_semantic_errors(value)]


def _checked_result(value: dict[str, Any]) -> dict[str, Any]:
    errors = validate_result_shape(value, "compiled-evidence-gate-result")
    if errors:
        raise ValueError("; ".join(errors))
    return value


def validate_result(
    value: Any,
    source: Any | None = None,
    verdict_projection: Any | None = None,
    verdict_source: Any | None = None,
    self_check_context: Any | None = None,
    governing_basis: Any | None = None,
    profile: Any | None = None,
    expectation_freeze: Any | None = None,
    l0_manifest: Any | None = None,
    l1_manifest: Any | None = None,
    l2_manifest: Any | None = None,
    project_protocol: Any | None = None,
    project_observations: Any | None = None,
    project_falsification: Any | None = None,
    principal_truth: Any | None = None,
    repo_root: Path | None = None,
    label: str = "deterministic-evidence-gate-result",
) -> list[str]:
    errors = validate_result_shape(value, label)
    if errors:
        return errors

    inputs = (
        source,
        verdict_projection,
        verdict_source,
        self_check_context,
        governing_basis,
        profile,
        expectation_freeze,
        l0_manifest,
        l1_manifest,
        l2_manifest,
        project_protocol,
        project_observations,
        project_falsification,
        principal_truth,
        repo_root,
    )
    if any(item is None for item in inputs):
        return [f"{label}: source-bound fresh gate replay is required"]

    try:
        fresh = compile_gate(
            source,
            verdict_projection,
            verdict_source,
            self_check_context,
            governing_basis,
            profile,
            expectation_freeze,
            l0_manifest,
            l1_manifest,
            l2_manifest,
            project_protocol,
            project_observations,
            project_falsification,
            principal_truth,
            repo_root,
        )
    except Exception as exc:
        return [f"{label}: fresh gate replay failed: {exc}"]

    if fresh != value:
        errors.append(f"{label}: stored gate result does not equal fresh source replay")
    return errors


def _load_inputs(args: argparse.Namespace) -> tuple[Any, ...]:
    return (
        load_yaml(Path(args.source)),
        load_yaml(Path(args.verdict_projection)),
        load_yaml(Path(args.verdict_source)),
        load_yaml(Path(args.self_check_context)),
        load_yaml(Path(args.governing_basis)),
        load_yaml(Path(args.profile)),
        load_yaml(Path(args.expectation_freeze)),
        load_yaml(Path(args.l0_manifest)),
        load_yaml(Path(args.l1_manifest)),
        load_yaml(Path(args.l2_manifest)),
        load_yaml(Path(args.project_protocol)),
        load_yaml(Path(args.project_observations)),
        load_yaml(Path(args.project_falsification)),
        load_yaml(Path(args.principal_truth)),
        Path(args.repo_root).resolve(),
    )


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("source")
    parser.add_argument("verdict_projection")
    parser.add_argument("verdict_source")
    parser.add_argument("self_check_context")
    parser.add_argument("governing_basis")
    parser.add_argument("profile")
    parser.add_argument("expectation_freeze")
    parser.add_argument("l0_manifest")
    parser.add_argument("l1_manifest")
    parser.add_argument("l2_manifest")
    parser.add_argument("project_protocol")
    parser.add_argument("project_observations")
    parser.add_argument("project_falsification")
    parser.add_argument("principal_truth")
    parser.add_argument("--repo-root", default=".")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compile or validate a deterministic exact-candidate evidence-gate "
            "disposition. The gate emits no engineering PASS or lifecycle authority."
        )
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compile_parser = sub.add_parser("compile")
    _add_common_args(compile_parser)
    compile_parser.add_argument("--output")

    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("result")
    _add_common_args(validate_parser)

    args = parser.parse_args()
    values = _load_inputs(args)

    if args.command == "compile":
        result = compile_gate(*values)
        rendered = dump_yaml(result)
        if args.output:
            Path(args.output).write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return

    result = load_yaml(Path(args.result))
    errors = validate_result(result, *values, label=Path(args.result).name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(
        "OK: deterministic evidence-gate result equals fresh source replay; "
        "eligibility is not lifecycle authority"
    )


if __name__ == "__main__":
    main()
