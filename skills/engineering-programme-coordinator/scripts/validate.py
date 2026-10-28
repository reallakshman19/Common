#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from coordlib import load_yaml, validate
from authority_resolver import validate_authority_resolution
from current_state import validate_current_state
from evidence_freshness import validate_evidence_freshness
from execution_kernel import semantic_errors as execution_state_semantic_errors
from l0_task_obligations import (
    validate_manifest as validate_l0_manifest,
    validate_source as validate_l0_source,
)
from l1_baseline_obligations import (
    validate_manifest as validate_l1_manifest,
    validate_source as validate_l1_source,
)
from l2_diff_impact import (
    validate_manifest as validate_l2_manifest,
    validate_source as validate_l2_source,
)
from exact_candidate_evidence import (
    validate_ledger as validate_exact_evidence_ledger,
    validate_source as validate_exact_evidence_source,
)
from repair_replay import (
    validate_result as validate_repair_replay_result,
    validate_source as validate_repair_replay_source,
)
from verdict_policy import (
    validate_projection as validate_verdict_projection,
    validate_source as validate_verdict_source,
)
from phase2_self_review_qualification import (
    validate_result as validate_phase2_qualification_result,
    validate_source as validate_phase2_qualification_source,
)
from phase1_runtime_replay import validate_phase1_replay
from production_readiness import semantic_errors as production_readiness_semantic_errors
from provider_mutation import semantic_errors as provider_mutation_semantic_errors
from review_basis import (
    review_context_semantic_errors,
    self_check_context_semantic_errors,
)


SCHEMAS = {
    "issue-contract",
    "work-order",
    "local-coordinator-return",
    "coordination-observation",
    "owner-coordination-report",
    "programme-record",
    "relay-handover",
    "production-readiness",
    "execution-state",
    "provider-mutation",
    "current-state",
    "authority-resolution",
    "evidence-freshness",
    "l0-task-contract-source",
    "l0-task-obligation-manifest",
    "l1-baseline-source",
    "l1-baseline-obligation-manifest",
    "l2-impact-source",
    "l2-impact-obligation-manifest",
    "exact-candidate-evidence-source",
    "exact-candidate-evidence-ledger",
    "repair-replay-source",
    "repair-replay-result",
    "verdict-policy-source",
    "verdict-projection",
    "phase2-self-review-qualification-source",
    "phase2-self-review-qualification-result",
    "deterministic-evidence-gate-source",
    "deterministic-evidence-gate-result",
    "phase1-runtime-replay",
    "review-context",
    "self-check-context",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate engineering programme coordinator objects.")
    parser.add_argument("schema", choices=sorted(SCHEMAS))
    parser.add_argument("path")
    parser.add_argument("--execution-state")
    parser.add_argument("--local-bundle")
    parser.add_argument("--observed-at")
    parser.add_argument("--freshness-request")
    parser.add_argument("--phase1-replay-request")
    parser.add_argument("--l0-source")
    parser.add_argument("--l1-source")
    parser.add_argument("--l2-source")
    parser.add_argument("--evidence-source")
    parser.add_argument("--repair-source")
    parser.add_argument("--verdict-source")
    parser.add_argument("--phase2-qualification-source")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args()

    value = load_yaml(Path(args.path))
    if args.schema == "current-state":
        execution_state = (
            load_yaml(Path(args.execution_state))
            if args.execution_state
            else None
        )
        errors = validate_current_state(
            value,
            execution_state,
            Path(args.path).name,
        )
    elif args.schema == "authority-resolution":
        local_bundle = (
            load_yaml(Path(args.local_bundle))
            if args.local_bundle
            else None
        )
        errors = validate_authority_resolution(
            value,
            local_bundle,
            args.observed_at,
            Path(args.path).name,
        )
    elif args.schema == "evidence-freshness":
        freshness_request = (
            load_yaml(Path(args.freshness_request))
            if args.freshness_request
            else None
        )
        errors = validate_evidence_freshness(
            value,
            freshness_request,
            Path(args.path).name,
        )
    elif args.schema == "phase1-runtime-replay":
        replay_request = (
            load_yaml(Path(args.phase1_replay_request))
            if args.phase1_replay_request
            else None
        )
        errors = validate_phase1_replay(
            value,
            replay_request,
            Path(args.path).name,
        )
    elif args.schema == "l0-task-contract-source":
        errors = validate_l0_source(value, Path(args.path).name)
    elif args.schema == "l0-task-obligation-manifest":
        l0_source = (
            load_yaml(Path(args.l0_source))
            if args.l0_source
            else None
        )
        errors = validate_l0_manifest(
            value,
            l0_source,
            Path(args.path).name,
        )
    elif args.schema == "l1-baseline-source":
        errors = validate_l1_source(value, Path(args.path).name)
    elif args.schema == "l1-baseline-obligation-manifest":
        l1_source = (
            load_yaml(Path(args.l1_source))
            if args.l1_source
            else None
        )
        errors = validate_l1_manifest(
            value,
            l1_source,
            Path(args.repo_root).resolve() if l1_source is not None else None,
            Path(args.path).name,
        )
    elif args.schema == "l2-impact-source":
        errors = validate_l2_source(value, Path(args.path).name)
    elif args.schema == "l2-impact-obligation-manifest":
        l2_source = (
            load_yaml(Path(args.l2_source))
            if args.l2_source
            else None
        )
        errors = validate_l2_manifest(
            value,
            l2_source,
            Path(args.repo_root).resolve() if l2_source is not None else None,
            Path(args.path).name,
        )
    elif args.schema == "exact-candidate-evidence-source":
        errors = validate_exact_evidence_source(value, Path(args.path).name)
    elif args.schema == "exact-candidate-evidence-ledger":
        evidence_source = (
            load_yaml(Path(args.evidence_source))
            if args.evidence_source
            else None
        )
        errors = validate_exact_evidence_ledger(
            value,
            evidence_source,
            Path(args.repo_root).resolve() if evidence_source is not None else None,
            Path(args.path).name,
        )
    elif args.schema == "repair-replay-source":
        errors = validate_repair_replay_source(value, Path(args.path).name)
    elif args.schema == "repair-replay-result":
        repair_source = (
            load_yaml(Path(args.repair_source))
            if args.repair_source
            else None
        )
        errors = validate_repair_replay_result(
            value,
            repair_source,
            Path(args.repo_root).resolve() if repair_source is not None else None,
            Path(args.path).name,
        )
    elif args.schema == "verdict-policy-source":
        errors = validate_verdict_source(value, Path(args.path).name)
    elif args.schema == "verdict-projection":
        verdict_source = (
            load_yaml(Path(args.verdict_source))
            if args.verdict_source
            else None
        )
        errors = validate_verdict_projection(
            value,
            verdict_source,
            Path(args.repo_root).resolve() if verdict_source is not None else None,
            Path(args.path).name,
        )
    elif args.schema == "phase2-self-review-qualification-source":
        errors = validate_phase2_qualification_source(value, Path(args.path).name)
    elif args.schema == "phase2-self-review-qualification-result":
        qualification_source = (
            load_yaml(Path(args.phase2_qualification_source))
            if args.phase2_qualification_source
            else None
        )
        errors = validate_phase2_qualification_result(
            value,
            qualification_source,
            Path(args.repo_root).resolve() if qualification_source is not None else None,
            Path(args.path).name,
        )
    else:
        errors = validate(args.schema, value, Path(args.path).name)
    if not errors and args.schema == "production-readiness":
        errors.extend(
            f"{Path(args.path).name}: {error}"
            for error in production_readiness_semantic_errors(value)
        )
    if not errors and args.schema == "execution-state":
        errors.extend(
            f"{Path(args.path).name}: {error}"
            for error in execution_state_semantic_errors(value)
        )
    if not errors and args.schema == "provider-mutation":
        errors.extend(
            f"{Path(args.path).name}: {error}"
            for error in provider_mutation_semantic_errors(value)
        )
    if not errors and args.schema == "review-context":
        errors.extend(
            f"{Path(args.path).name}: {error}"
            for error in review_context_semantic_errors(value)
        )
    if not errors and args.schema == "self-check-context":
        errors.extend(
            f"{Path(args.path).name}: {error}"
            for error in self_check_context_semantic_errors(value)
        )
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: {args.schema}: {args.path}")


if __name__ == "__main__":
    main()
