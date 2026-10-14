"""Typed source-derived rows for the M1 GitHub observation seam.

Pure model/fixture layer. No provider I/O, command dispatch or acceptance inference.
Raw comments, credentials, private chat locations and unredacted prose never enter
the public row representation. Revision history storage belongs to M1-U02.
"""
from __future__ import annotations

import hashlib
import re
from urllib.parse import urlsplit
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Optional

ROW_SCHEMA_VERSION = "1.0.0"
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_SAFE_ID = re.compile(r"^[A-Za-z0-9_.:-]{1,128}$")


class SourceKind(str, Enum):
    ISSUE = "ISSUE"
    ISSUE_COMMENT = "ISSUE_COMMENT"
    PR = "PR"
    CHECK_RUN = "CHECK_RUN"


class SourceState(str, Enum):
    REACHABLE = "REACHABLE"
    PARTIAL = "PARTIAL"
    RATE_LIMITED = "RATE_LIMITED"
    FORBIDDEN = "FORBIDDEN"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"


class EvidenceVerdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"
    NOT_RUN = "NOT_RUN"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class SourceIdentity:
    project_id: str
    repo_id: str
    repo_full_name: str
    kind: SourceKind
    entity_id: str
    revision_id: str
    issue_number: Optional[int] = None
    comment_id: Optional[str] = None
    body_sha256: Optional[str] = None
    created_at_utc: Optional[str] = None
    updated_at_utc: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self) -> None:
        if not _SAFE_ID.fullmatch(self.project_id):
            raise ValueError("Invalid project identity")
        if not self.repo_id.isdecimal() or not _REPO.fullmatch(self.repo_full_name):
            raise ValueError("Invalid repository identity")
        if not isinstance(self.kind, SourceKind):
            raise ValueError("Invalid GitHub source kind")
        if not _SAFE_ID.fullmatch(self.entity_id) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,256}", self.revision_id):
            raise ValueError("Missing or unsafe source revision identity")
        if self.issue_number is not None and (type(self.issue_number) is not int or self.issue_number < 1):
            raise ValueError("Invalid issue number")
        if self.kind == SourceKind.ISSUE_COMMENT and (
            self.issue_number is None or self.comment_id is None or
            self.entity_id != self.comment_id
        ):
            raise ValueError("Comment requires matching issue and comment identity")
        if self.body_sha256 is not None and not _HEX64.fullmatch(self.body_sha256):
            raise ValueError("Invalid exact-body sha256")
        if self.url is not None and not _public_url(self.url, self.repo_full_name):
            raise ValueError("Noncanonical public GitHub source URL")
        _safe_stamp(self.created_at_utc)
        _safe_stamp(self.updated_at_utc)

    @property
    def stable_key(self) -> str:
        return ":".join((self.repo_id, self.kind.value, self.entity_id))

    def public_dict(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "repo_id": self.repo_id,
            "repo_full_name": self.repo_full_name,
            "kind": self.kind.value,
            "entity_id": self.entity_id,
            "revision_id": self.revision_id,
            "issue_number": self.issue_number,
            "comment_id": self.comment_id,
            "body_sha256": self.body_sha256,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
            "url": self.url,
        }


def _public_url(value: Any, repo: Optional[str] = None) -> bool:
    """Public github.com URL only; prohibit query/credentials/private route leaks."""
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.query:
        return False
    if not re.fullmatch(r"(?:issuecomment-[0-9]+|discussion_r[0-9]+)?", parsed.fragment):
        return False
    if repo is not None:
        return parsed.path.startswith("/" + repo + "/")
    return bool(re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(?:issues|pull|commit|actions|checks)/[A-Za-z0-9_./-]+", parsed.path))


def _safe_stamp(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > 40 or not re.fullmatch(
        r"[0-9TZ:.+\\-]+", value
    ):
        raise ValueError("Unsafe source timestamp")
    return value


def _enum(value: Any, allowed: type[Enum], default: str) -> str:
    if value is None:
        return default
    try:
        return allowed(value).value
    except (ValueError, TypeError):
        raise ValueError("Unknown typed value") from None


def _safe_id(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or not _SAFE_ID.fullmatch(value):
        raise ValueError("Unsafe or ambiguous public identifier")
    return value


def _safe_sha(value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or not _HEX40.fullmatch(value):
        raise ValueError("Invalid candidate SHA")
    return value


def build_row(
    source: SourceIdentity,
    *,
    bindings: Iterable[Mapping[str, Any]] = (),
    report: Optional[Mapping[str, Any]] = None,
    coordinator: Optional[Mapping[str, Any]] = None,
    review: Optional[Mapping[str, Any]] = None,
    source_state: str = "UNKNOWN",
    observed_at_utc: Optional[str] = None,
    freshness: str = "UNKNOWN",
    completed_scan: bool = False,
    present: bool = True,
    current_pr_head_sha: Optional[str] = None,
) -> dict[str, Any]:
    """Produce a whitelist-only seam. It does not evaluate native workflows.

    Binding rows must be explicit and project-consistent; zero or conflicting
    bindings never invent an assignment. A provider report is never a review.
    Partial/unavailable sources never certify disappearance.
    """
    state = _enum(source_state, SourceState, "UNKNOWN")
    _safe_stamp(observed_at_utc)
    if freshness not in ("FRESH", "STALE", "UNKNOWN"):
        raise ValueError("Invalid freshness")
    matches = list(bindings)
    for binding in matches:
        if binding.get("project_id") != source.project_id:
            raise ValueError("Cross-project binding")
        for key in ("work_id", "lane_id", "assignment_id", "run_id"):
            _safe_id(binding.get(key))
    binding_state = "UNASSIGNED" if not matches else "BOUND" if len(matches) == 1 else "CONFLICT"
    bound = matches[0] if len(matches) == 1 else {}
    report = report or {}
    coordinator = coordinator or {}
    review = review or {}
    reported = _enum(report.get("reported_verdict"), EvidenceVerdict, "UNKNOWN")
    if report.get("reported_verdict") == "PARTIAL":
        # PARTIAL is a reviewer verdict, not a provider's test outcome.
        raise ValueError("PARTIAL is not a provider test verdict")
    candidate_sha = _safe_sha(report.get("candidate_sha"))
    current_head = _safe_sha(current_pr_head_sha)
    review_ref = review.get("review_ref")
    if review_ref is not None and not _public_url(review_ref):
        raise ValueError("Invalid independent review provenance")
    if review_ref and review_ref == source.url:
        raise ValueError("Provider report cannot self-certify independent review")
    reviewed = _enum(review.get("review_verdict"), EvidenceVerdict, "UNKNOWN")
    review_sha = _safe_sha(review.get("review_candidate_sha"))
    if reviewed != "UNKNOWN" and not review_ref:
        raise ValueError("Review verdict needs an independently attributable source")
    if review_ref is None and review_sha is not None:
        raise ValueError("Review candidate without reviewer source")
    comparison = "UNKNOWN"
    compare_sha = review_sha if review_sha else candidate_sha
    if compare_sha and current_head:
        comparison = "CURRENT" if compare_sha == current_head else "OLD_HEAD"
    _safe_stamp(coordinator.get("observed_at_utc"))
    liveness = coordinator.get("liveness", "UNKNOWN")
    if liveness not in ("ALIVE", "STALE", "STOPPED", "UNKNOWN"):
        raise ValueError("Invalid coordinator liveness")
    absence = (
        "PRESENT" if present else
        "ABSENT" if completed_scan and state == "REACHABLE" else
        "UNAVAILABLE"
    )
    return {
        "schema_version": ROW_SCHEMA_VERSION,
        "source": source.public_dict(),
        "binding": {
            "state": binding_state,
            "project_id": source.project_id,
            "work_id": bound.get("work_id"),
            "lane_id": bound.get("lane_id"),
            "assignment_id": bound.get("assignment_id"),
            "run_id": bound.get("run_id"),
            "provider_kind": _safe_id(bound.get("provider_kind")) or "UNKNOWN",
            "conflicts": ["MULTIPLE_EXPLICIT_BINDINGS"] if binding_state == "CONFLICT" else [],
        },
        "report": {
            "provenance": "PROVIDER_REPORT",
            "task_id": _safe_id(report.get("task_id")),
            "candidate_sha": candidate_sha,
            "reported_status": _safe_id(report.get("reported_status")),
        },
        "coordinator_observation": {
            "provenance": "COORDINATOR_OBSERVATION",
            "observed_at_utc": coordinator.get("observed_at_utc"),
            "liveness": liveness,
            "probe_status": _safe_id(coordinator.get("probe_status")),
            "source_ref": coordinator.get("source_ref") if
                _public_url(coordinator.get("source_ref")) else None,
        },
        "evidence": {
            "reported_verdict": reported,
            "review_verdict": reviewed,
            "review_ref": review_ref,
            "review_candidate_sha": review_sha,
            "current_pr_head_sha": current_head,
            "candidate_relation": comparison,
            "applicability": review.get("applicability", "UNKNOWN") if
                review.get("applicability", "UNKNOWN") in
                ("APPLICABLE", "NOT_APPLICABLE", "UNKNOWN") else "UNKNOWN",
        },
        "source_health": {
            "state": state,
            "observed_at_utc": observed_at_utc,
            "freshness": freshness,
            "scan_completed": bool(completed_scan),
        },
        "absence": absence,
    }


def version_trace(observations: Iterable[tuple[str, str]]) -> list[dict[str, Any]]:
    """U01 in-memory A→B→A fixture model; persistent cursor is M1-U02.

    (provider_updated_at, exact_utf8_body). Deduplicates exact replay of one
    provider revision, but a return to earlier content at a *new timestamp*
    must be a new version. Conflicting content at one timestamp is rejected.
    """
    revisions: dict[str, str] = {}
    history: list[dict[str, Any]] = []
    for updated_at, body in observations:
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        old = revisions.get(updated_at)
        if old is not None:
            if old != digest:
                raise ValueError("Conflicting body at identical provider revision")
            continue
        if history and updated_at < history[-1]["updated_at_utc"]:
            raise ValueError("Out-of-order unseen provider revision")
        revisions[updated_at] = digest
        history.append({
            "version": len(history) + 1,
            "updated_at_utc": updated_at,
            "body_sha256": digest,
        })
    return history
