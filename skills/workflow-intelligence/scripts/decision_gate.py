#!/usr/bin/env python3
"""Review-gated MCDA adapter. A JSON claim is never independent evidence proof.

Provides deterministic, *advisory* comparisons for explicitly bound, provenance-
declared inputs. It cannot certify a reviewer, GitHub ref or test result; until
a trusted verifier is connected, all evaluations remain ineligible for alerts.
"""
import argparse
import importlib.util
import json
import re
from pathlib import Path

from observe import fingerprint

REQUEST_SCHEMA = "workflow-intelligence.decision-request/v1"
RESULT_SCHEMA = "workflow-intelligence.assessment/v1"
HEX_SHA = re.compile(r"^[a-f0-9]{40}$")
HEX_DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def load_mcda():
    path = Path(__file__).resolve().parents[2] / "software-mcda" / "scripts" / "mcda.py"
    spec = importlib.util.spec_from_file_location("software_mcda_engine", path)
    if spec is None or spec.loader is None:
        raise ValueError("Standalone Software MCDA skill unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scope_of(request):
    scope = request.get("scope")
    if not isinstance(scope, dict):
        raise ValueError("Decision scope required")
    repository = scope.get("repository")
    if (not isinstance(repository, str) or not REPOSITORY.fullmatch(repository) or
            any(not component.strip(".") for component in repository.split("/"))):
        raise ValueError("Invalid repository scope")
    if not isinstance(scope.get("workflow_id"), str) or not scope["workflow_id"]:
        raise ValueError("Workflow ID required")
    if not isinstance(scope.get("decision_id"), str) or not scope["decision_id"]:
        raise ValueError("Decision ID required")
    if type(scope.get("issue")) is not int or scope["issue"] < 1:
        raise ValueError("Issue number required")
    sha = scope.get("assessed_sha")
    if not isinstance(sha, str) or not HEX_SHA.fullmatch(sha):
        raise ValueError("Exact assessed commit SHA required")
    return {k: scope[k] for k in ("repository", "workflow_id", "decision_id",
                                  "issue", "assessed_sha")}


def assessment(request, github_check_request=None, check_reader=None):
    if not isinstance(request, dict) or request.get("schema") != REQUEST_SCHEMA:
        raise ValueError("Unsupported decision request schema")
    scope = scope_of(request)
    enabled = request.get("enabled")
    if type(enabled) is not bool:
        raise ValueError("Enabled must be explicit boolean")
    base = {"schema": RESULT_SCHEMA, "scope": scope,
            "notification_eligible": False,
            "authority": "SELF_DECLARED_INPUTS_NOT_INDEPENDENTLY_VERIFIED"}
    if not enabled:
        return {**base, "status": "NOT_EVALUATED", "reason": "Decision is disabled"}
    decision = request.get("decision")
    if not isinstance(decision, dict):
        return {**base, "status": "NOT_EVALUATED", "reason": "Missing decision configuration"}
    engine = load_mcda()
    try:
        weights = engine.validate(decision)
    except (ValueError, TypeError, KeyError) as error:
        return {**base, "status": "NOT_EVALUATED", "reason": f"Invalid MCDA input: {error}"}
    authority = request.get("authority")
    if not isinstance(authority, dict):
        return {**base, "status": "NOT_EVALUATED", "reason": "Approval reference absent"}
    ref, bound_digest = authority.get("approval_ref"), authority.get("decision_digest")
    if not isinstance(ref, str) or not ref.startswith(
            "https://github.com/" + scope["repository"] + "/issues/"):
        return {**base, "status": "NOT_EVALUATED", "reason": "Invalid provenance approval reference"}
    if not isinstance(bound_digest, str) or not HEX_DIGEST.fullmatch(bound_digest):
        return {**base, "status": "NOT_EVALUATED", "reason": "Missing approved-config digest"}
    if bound_digest != "sha256:" + fingerprint(decision):
        return {**base, "status": "NOT_EVALUATED", "reason": "Decision configuration digest mismatch"}
    evidence = request.get("rating_evidence")
    if not isinstance(evidence, dict):
        return {**base, "status": "NOT_EVALUATED", "reason": "Rating evidence not supplied"}
    options = {item["name"] for item in decision["options"]}
    if set(evidence) != options:
        return {**base, "status": "NOT_EVALUATED", "reason": "Evidence option set mismatch"}
    for option, ratings in evidence.items():
        if not isinstance(ratings, dict) or set(ratings) != set(weights):
            return {**base, "status": "NOT_EVALUATED", "reason": f"Evidence criterion mismatch: {option}"}
        for criterion, claim in ratings.items():
            if not isinstance(claim, dict) or set(claim) != {"ref", "assessed_sha", "status"}:
                return {**base, "status": "NOT_EVALUATED", "reason": "Malformed evidence binding"}
            if (claim["status"] != "OBSERVED"
                    or claim["assessed_sha"] != scope["assessed_sha"]
                    or not isinstance(claim["ref"], str)
                    or not claim["ref"].startswith("https://github.com/" + scope["repository"] + "/")):
                return {**base, "status": "NOT_EVALUATED",
                        "reason": "Unqualified, stale or cross-repository rating evidence"}
    if any(option.get("evidence_level") != "OBSERVED" for option in decision["options"]):
        return {**base, "status": "NOT_EVALUATED",
                "reason": "Enabled decision requires OBSERVED evidence level for every option"}
    verified_check_facts = None
    if github_check_request is not None:
        from github_check_facts import validate as validate_github_checks
        from github_check_facts import verify as verify_github_checks
        ci_repo, ci_sha, _ = validate_github_checks(github_check_request)
        if ci_repo != scope["repository"] or ci_sha != scope["assessed_sha"]:
            return {**base, "status": "NOT_EVALUATED",
                    "reason": "GitHub CI fact scope does not match decision candidate"}
        verified_check_facts = verify_github_checks(github_check_request, check_reader)
        if github_check_request["enabled"] and verified_check_facts["status"] != "CHECKS_VERIFIED":
            return {**base, "status": "NOT_EVALUATED",
                    "reason": "Required exact-commit CI checks not verified",
                    "ci_check_facts": verified_check_facts}
    calculated = engine.report(decision)
    return {**base, "status": "ADVISORY_REVIEW_REQUIRED",
            "reason": "Evidence/approval references are self-declared; no independent provider verification",
            "configuration_digest": bound_digest, "mcda": calculated,
            **({"ci_check_facts": verified_check_facts}
               if verified_check_facts is not None else {})}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--request", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--github-check-request", type=Path)
    args = p.parse_args()
    try:
        request = json.loads(args.request.read_text(encoding="utf-8"))
        ci_request = (json.loads(args.github_check_request.read_text(encoding="utf-8"))
                      if args.github_check_request else None)
        result = assessment(request, ci_request)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                               encoding="utf-8")
        print(result["status"] + ": alerts disabled")
    except (OSError, ValueError, TypeError) as exc:
        p.exit(2, f"ASSESSMENT_FAILED: {exc}\n")


if __name__ == "__main__":
    main()
