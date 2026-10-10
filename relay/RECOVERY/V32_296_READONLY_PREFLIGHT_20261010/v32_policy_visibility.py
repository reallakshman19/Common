"""Native V3.2 D4/D5 visibility-only witness; never an admission-policy issuer.

Reads a real PR, its submitted review snapshots and the target branch's
ruleset/classic required-check endpoints through the provider. Visibility of
reviews or protections is *not* evidence that an Owner-approved graph,
qualified independent reviewers, or an effective required-check policy exists.

The witness is intentionally HOLD-only and cannot mint accepted E, issue
CHECKPOINT_FACTS_V1, or change the DELP/PR/issue/C6 write surfaces.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from re import fullmatch
from typing import Any, Protocol

_SHA = r"[0-9a-f]{40}"
_REPO = r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+"


class VisibilityProvider(Protocol):
    def get_pull(self, repository: str, number: int) -> Mapping[str, Any]: ...
    def get_pr_reviews(self, repository: str, number: int) -> list[Mapping[str, Any]]: ...
    def get_branch_rulesets(self, repository: str, branch: str) -> list[Mapping[str, Any]]: ...
    def get_branch_required_checks(self, repository: str, branch: str) -> Mapping[str, Any]: ...


@dataclass(frozen=True)
class PolicyVisibility:
    status: str
    reasons: tuple[str, ...]
    observed_candidate: str | None
    submitted_reviews: int
    distinct_latest_approved_reviewers: int
    exact_head_latest_approvals: int
    required_policy_endpoints: Mapping[str, str]
    independent_review_authority: str = "UNKNOWN_NOT_AUTHENTICATED"
    effective_required_check_policy: str = "UNKNOWN_NOT_AUTHENTICATED"
    accepted_evidence_count: None = None
    writer_authorized: bool = False
    delp_invoked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status, "reasons": list(self.reasons),
            "observed_candidate": self.observed_candidate,
            "submitted_reviews": self.submitted_reviews,
            "distinct_latest_approved_reviewers": self.distinct_latest_approved_reviewers,
            "exact_head_latest_approvals": self.exact_head_latest_approvals,
            "required_policy_endpoints": dict(self.required_policy_endpoints),
            "independent_review_authority": self.independent_review_authority,
            "effective_required_check_policy": self.effective_required_check_policy,
            "accepted_evidence_count": None,
            "writer_authorized": False,
            "delp_invoked": False,
        }


def observe_review_and_policy_visibility(
    provider: VisibilityProvider, *, repository: str, pr_number: int, expected_head: str,
) -> PolicyVisibility:
    """Observe only; two PR reads bound the serial GET window, not an atomic snapshot."""
    if (not isinstance(repository, str) or not fullmatch(_REPO, repository)
            or type(pr_number) is not int or pr_number < 1
            or not isinstance(expected_head, str) or not fullmatch(_SHA, expected_head)):
        return PolicyVisibility("FAILED_TARGET", ("TARGET_INVALID",), None, 0, 0, 0, {})
    reasons: list[str] = []
    exposure: dict[str, str] = {
        "rulesets": "NOT_RUN", "classic_required_checks": "NOT_RUN",
    }
    try:
        pr = provider.get_pull(repository, pr_number)
        if not isinstance(pr, Mapping) or pr.get("number") != pr_number:
            raise ValueError("PR_PROVIDER_RESPONSE_INVALID")
        head = (pr.get("head") or {}).get("sha")
        base = (pr.get("base") or {}).get("ref")
        head_repo = (pr.get("head") or {}).get("repo") or {}
        base_repo = (pr.get("base") or {}).get("repo") or {}
        if not isinstance(head, str) or not fullmatch(_SHA, head) or not isinstance(base, str) or not base:
            raise ValueError("PR_SOURCE_IDENTITY_UNKNOWN")
        if str(base_repo.get("full_name") or "").lower() != repository.lower():
            raise ValueError("PR_BASE_REPOSITORY_MISMATCH")
        if head != expected_head:
            return PolicyVisibility("HOLD_STALE_CANDIDATE", ("EXPECTED_HEAD_NOT_LIVE",), head, 0, 0, 0, exposure)
        try:
            reviews = provider.get_pr_reviews(repository, pr_number)
            if not isinstance(reviews, list) or len(reviews) > 2000:
                raise ValueError("REVIEW_PROVIDER_RESPONSE_UNBOUNDED")
            exposure["reviews"] = "OBSERVED"
        except (OSError, ValueError, TypeError) as exc:
            reviews = []
            exposure["reviews"] = "UNKNOWN"
            reasons.append("REVIEW_ENDPOINT_UNKNOWN")
        # A repository ruleset response may be empty or may lack admin access.
        # Even complete provider visibility is *not* proof of an adopted D5
        # evidence-policy snapshot, inherited governance or required CI.
        try:
            rules = provider.get_branch_rulesets(repository, base)
            if not isinstance(rules, list):
                raise ValueError("RULESETS_RESPONSE_INVALID")
            exposure["rulesets"] = "OBSERVED_EMPTY" if not rules else "OBSERVED_UNQUALIFIED"
        except (OSError, ValueError, TypeError):
            exposure["rulesets"] = "UNKNOWN"
            reasons.append("RULESET_ENDPOINT_UNKNOWN")
        try:
            classic = provider.get_branch_required_checks(repository, base)
            if not isinstance(classic, Mapping):
                raise ValueError("CLASSIC_REQUIRED_CHECK_RESPONSE_INVALID")
            exposure["classic_required_checks"] = "OBSERVED_UNQUALIFIED"
        except (OSError, ValueError, TypeError):
            exposure["classic_required_checks"] = "UNKNOWN"
            reasons.append("CLASSIC_REQUIRED_CHECK_ENDPOINT_UNKNOWN")
        latest: dict[str, Mapping[str, Any]] = {}
        author = str((pr.get("user") or {}).get("login") or "").lower()
        submitted = 0
        for row in reviews:
            if not isinstance(row, Mapping):
                raise ValueError("REVIEW_ITEM_INVALID")
            state = str(row.get("state") or "").upper()
            login = str((row.get("user") or {}).get("login") or "").lower()
            if state not in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED", "DISMISSED", "PENDING"}:
                raise ValueError("REVIEW_STATE_INVALID")
            if state == "PENDING":
                continue
            if not login or type(row.get("id")) is not int:
                raise ValueError("REVIEW_ITEM_IDENTITY_INVALID")
            submitted += 1
            # GitHub review listing is chronological; update per reviewer.
            # A COMMENTED later review is not an explicit retraction of a
            # prior APPROVED. For safety, neither can qualify independence.
            latest[login] = row
        approvals = [
            row for login, row in latest.items()
            if login != author and str(row.get("state")).upper() == "APPROVED"
        ]
        current_approvals = [
            row for row in approvals if row.get("commit_id") == head
        ]
        late = provider.get_pull(repository, pr_number)
        if (not isinstance(late, Mapping) or late.get("number") != pr_number or
                (late.get("head") or {}).get("sha") != head or
                (late.get("base") or {}).get("ref") != base or
                str(((late.get("base") or {}).get("repo") or {}).get("full_name") or "").lower() != repository.lower()):
            return PolicyVisibility("HOLD_MOVED_SOURCE", ("PR_MOVED_DURING_POLICY_READ",),
                                    None, 0, 0, 0, exposure)
        reasons.extend(["OWNER_REVIEWER_ELIGIBILITY_NOT_AUTHENTICATED",
                        "EFFECTIVE_REQUIRED_CHECK_POLICY_NOT_AUTHENTICATED"])
        return PolicyVisibility(
            "HOLD_D4_D5_AUTHORITY_UNKNOWN", tuple(dict.fromkeys(reasons)), head,
            submitted, len(approvals), len(current_approvals), exposure,
        )
    except (OSError, ValueError, TypeError, AttributeError):
        return PolicyVisibility(
            "HOLD_PROVIDER_READ", ("REVIEW_POLICY_PROVIDER_READ_UNKNOWN",),
            None, 0, 0, 0, exposure,
        )
