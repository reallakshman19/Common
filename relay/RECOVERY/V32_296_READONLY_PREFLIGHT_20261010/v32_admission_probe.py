"""V3.2 #296 STEP-02/03 read-only pre-admission probe (NOT a trusted issuer).

This deliberately does not modify DELP, accept a CHECKPOINT_FACTS_V1, issue a
SourceReceiptV2, or make GitHub writes.  It identifies the first missing
producer -> trusted policy -> DELP edge without manufacturing eligibility.

Integrate only after the existing V3.2 owner adopts a source-pinned evidence
policy, source authorization and separately qualified issuer.  No claims in
this module can be converted into production E by this module itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from re import fullmatch
from typing import Any, Mapping, Sequence

V32_FACTS_SCHEMA = "relay-v3.2-delp-checkpoint-facts"
_SHA = r"[0-9a-f]{40}"


@dataclass(frozen=True)
class SourceSelection:
    """Observed identities; NOT an Owner/reviewer authorization token."""
    repository: str
    leaf_ref: str
    pr_number: int
    current_head: str | None
    observed_pr_repository: str | None
    observed_pr_number: int | None
    original_source_state: str = "UNKNOWN"
    released_graph_state: str = "UNKNOWN"
    evidence_policy_state: str = "UNKNOWN"
    required_check_policy_state: str = "UNKNOWN"
    independent_review_state: str = "UNKNOWN"


@dataclass(frozen=True)
class ObservedCheck:
    """A *selected* check observation; not proof that all required checks exist."""
    name: str
    candidate_sha: str
    conclusion: str
    executed: bool


@dataclass(frozen=True)
class ProbeReport:
    state: str
    reasons: tuple[str, ...]
    candidate_sha: str | None
    accepted_evidence_count: None = None
    writer_authorized: bool = False
    delp_invoked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "state": self.state,
            "reasons": list(self.reasons),
            "candidate_sha": self.candidate_sha,
            "accepted_evidence_count": self.accepted_evidence_count,
            "writer_authorized": self.writer_authorized,
            "delp_invoked": self.delp_invoked,
        }


def probe_v32_fact(
    selection: SourceSelection,
    facts: Mapping[str, Any] | None,
    checks: Sequence[ObservedCheck] = (),
) -> ProbeReport:
    """Classify *read-only material*, never deliver eligibility or E.

    UNKNOWN, FAILED and NOT_RUN are explicit distinct states.  The caller
    supplies provider observations; this function cannot establish that they
    came from the original R3/R12 acquisition cycle.  Even a coherent result
    remains a HOLD until a separate approved evidence issuer exists.
    """
    failures: list[str] = []
    unknowns: list[str] = []
    not_run: list[str] = []
    if (not isinstance(selection.repository, str) or
            not fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", selection.repository) or
            any(segment in (".", "..") for segment in selection.repository.split("/"))):
        failures.append("INVALID_TARGET_REPOSITORY")
    if not isinstance(selection.leaf_ref, str) or not fullmatch(r"[A-Za-z0-9_.-]+#[1-9][0-9]*", selection.leaf_ref):
        failures.append("INVALID_LEAF_REF")
    if type(selection.pr_number) is not int or selection.pr_number < 1:
        failures.append("INVALID_PR_NUMBER")
    if selection.observed_pr_repository is None or selection.observed_pr_number is None:
        unknowns.append("PR_PROVIDER_IDENTITY_UNKNOWN")
    elif selection.observed_pr_repository.lower() != selection.repository.lower() or selection.observed_pr_number != selection.pr_number:
        failures.append("PR_PROVIDER_IDENTITY_MISMATCH")
    if selection.current_head is None:
        unknowns.append("LIVE_HEAD_UNKNOWN")
    elif not fullmatch(_SHA, selection.current_head):
        failures.append("LIVE_HEAD_INVALID")

    fact_head = None
    if not isinstance(facts, Mapping):
        unknowns.append("FACTS_ABSENT")
    else:
        # Native DELP permits an omitted "schema" (CHECKPOINT_FACTS_V1
        # wrapper supplies it).  This classifier must not mislabel a valid
        # native fact as structurally invalid.
        if facts.get("schema") not in (None, V32_FACTS_SCHEMA):
            failures.append("FACT_SCHEMA_NOT_NATIVE_V32")
        responsibility = facts.get("responsibility")
        if not isinstance(responsibility, Mapping) or responsibility.get("issue") != selection.leaf_ref:
            failures.append("FACT_LEAF_MISMATCH")
        material = facts.get("material")
        if not isinstance(material, Mapping) or not isinstance(material.get("candidate_sha"), str) or not fullmatch(_SHA, material["candidate_sha"]):
            failures.append("FACT_CANDIDATE_INVALID")
        else:
            fact_head = material["candidate_sha"]
            candidate_pr = material.get("pr")
            expected_pr = selection.repository.rsplit("/", 1)[-1] + "#" + str(selection.pr_number)
            # material.pr is optional in native V3.2.  The separate released
            # graph and observed provider PR must still be checked; this
            # optional field cannot mint positive evidence either way.
            if candidate_pr is not None and candidate_pr not in (
                expected_pr, selection.repository + "#" + str(selection.pr_number)
            ):
                failures.append("FACT_PR_NOT_BOUND")
            if selection.current_head is not None and fact_head != selection.current_head:
                failures.append("FACT_CANDIDATE_STALE")
        units = facts.get("units", ())
        if not isinstance(units, (tuple, list)):
            failures.append("FACT_UNITS_INVALID")
            units = ()
        for unit in units:
            if not isinstance(unit, Mapping) or unit.get("state") != "COMPLETE":
                continue
            if unit.get("result") != "VERIFIED" or not unit.get("evidence_refs"):
                failures.append("COMPLETE_UNIT_HAS_NO_CURRENT_VERIFICATION_CLAIM")
            candidate = unit.get("candidate_sha")
            if candidate is not None and candidate != fact_head:
                failures.append("UNIT_CANDIDATE_MISMATCH")

    # Selected checks are never proof of the effective CI policy.
    if not checks:
        not_run.append("SELECTED_CHECKS_NOT_RUN_OR_NOT_OBSERVED")
    for check in checks:
        if not check.executed:
            not_run.append("CHECK_NOT_EXECUTED:" + check.name)
        elif check.conclusion == "failure":
            failures.append("SELECTED_CHECK_FAILED:" + check.name)
        elif check.conclusion != "success":
            unknowns.append("SELECTED_CHECK_NOT_SUCCESS:" + check.name)
        if selection.current_head and check.candidate_sha != selection.current_head:
            failures.append("SELECTED_CHECK_WRONG_HEAD:" + check.name)

    for name, value in (
        ("ORIGINAL_OWNER_SOURCE", selection.original_source_state),
        ("RELEASED_GRAPH", selection.released_graph_state),
        ("EVIDENCE_POLICY", selection.evidence_policy_state),
        ("EFFECTIVE_REQUIRED_CHECK_POLICY", selection.required_check_policy_state),
        ("INDEPENDENT_REVIEWS", selection.independent_review_state),
    ):
        if value != "VERIFIED":
            unknowns.append(name + "_NOT_AUTHENTICATED")

    if failures:
        state = "FAILED"
    elif unknowns:
        state = "HOLD_UNKNOWN_AUTHORITY_OR_SOURCE"
    elif not_run:
        state = "HOLD_NOT_RUN"
    else:
        state = "HOLD_NOT_AN_EVIDENCE_ISSUER"
    reasons = tuple(dict.fromkeys(failures + unknowns + not_run + ["NATIVE_POSITIVE_ADMISSION_NOT_IMPLEMENTED"]))
    return ProbeReport(state, reasons, fact_head)
