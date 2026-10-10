"""#296: live-read-only V3.2 source/HEAD consistency preflight.

This is NOT the R3/R12 trusted provider, an evidence issuer, a production
policy evaluator, a DELP wrapper or a writer. It performs two full, bounded,
non-atomic GET passes and refuses to call them one immutable GitHub snapshot.

Reads happen through an injected GET-only provider contract. In a qualifying
runtime, its implementations must use trusted credentials, real provider GETs,
and independently established authority; none is minted or accepted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from json import dumps, loads
from re import fullmatch
from typing import Any, Mapping, Protocol

from v32_admission_probe import ObservedCheck, ProbeReport, SourceSelection, probe_v32_fact
from v32_fact_claims import audit_native_comment_claims

_SHA = r"[0-9a-f]{40}"


class ReadOnlyGetter(Protocol):
    def get_repository(self, repository: str) -> Mapping[str, Any]: ...
    def get_commit(self, repository: str, ref: str) -> Mapping[str, Any]: ...
    def get_file_bytes(self, repository: str, path: str, ref: str) -> bytes: ...
    def get_pull(self, repository: str, number: int) -> Mapping[str, Any]: ...
    def get_issue_comments(self, repository: str, number: int) -> list[Mapping[str, Any]]: ...
    def get_check_runs(self, repository: str, head: str) -> list[Mapping[str, Any]]: ...


@dataclass(frozen=True)
class PreflightTarget:
    repository: str
    repository_id: int
    graph_path: str
    leaf_ref: str
    pr_number: int
    expected_graph_sha256: str | None = None


@dataclass(frozen=True)
class PreflightResult:
    status: str
    reasons: tuple[str, ...]
    source_currentness: str
    graph_digest: str | None
    candidate_sha: str | None
    pass_count: int
    probe: ProbeReport | None
    comment_claims: Mapping[str, Any] | None = None
    accepted_evidence_count: None = None
    writer_authorized: bool = False
    delp_invoked: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
            "source_currentness": self.source_currentness,
            "graph_digest": self.graph_digest,
            "candidate_sha": self.candidate_sha,
            "pass_count": self.pass_count,
            "probe": self.probe.as_dict() if self.probe is not None else None,
            "comment_claims": dict(self.comment_claims) if self.comment_claims is not None else None,
            "accepted_evidence_count": None,
            "writer_authorized": False,
            "delp_invoked": False,
        }


def _sha256(data: bytes) -> str:
    return "sha256:" + sha256(data).hexdigest()


def _canonical(value: Any) -> bytes:
    return dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _ref(value: str, repository: str, number: int) -> bool:
    short = repository.rsplit("/", 1)[-1] + "#" + str(number)
    return value in (short, repository + "#" + str(number))


def _target_errors(target: PreflightTarget) -> list[str]:
    errors: list[str] = []
    if not isinstance(target.repository, str) or not fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", target.repository):
        errors.append("TARGET_REPOSITORY_INVALID")
    if type(target.repository_id) is not int or target.repository_id < 1:
        errors.append("TARGET_REPOSITORY_ID_INVALID")
    if (not isinstance(target.graph_path, str) or len(target.graph_path) > 256 or
            not target.graph_path.endswith(".json") or
            any(x in ("", ".", "..") for x in target.graph_path.split("/")) or
            target.graph_path.startswith("/")):
        errors.append("TARGET_GRAPH_PATH_INVALID")
    if not isinstance(target.leaf_ref, str) or not fullmatch(r"[A-Za-z0-9_.-]+#[1-9][0-9]*", target.leaf_ref):
        errors.append("TARGET_LEAF_INVALID")
    if type(target.pr_number) is not int or target.pr_number < 1:
        errors.append("TARGET_PR_INVALID")
    if target.expected_graph_sha256 is not None and not fullmatch(r"sha256:[0-9a-f]{64}", target.expected_graph_sha256):
        errors.append("TARGET_GRAPH_DIGEST_INVALID")
    return errors


def _round(target: PreflightTarget, getter: ReadOnlyGetter) -> dict[str, Any]:
    # These are serial, individual provider observations, not an atomic read.
    repo = getter.get_repository(target.repository)
    if repo.get("full_name", "").lower() != target.repository.lower() or repo.get("id") != target.repository_id:
        raise ValueError("PROVIDER_REPOSITORY_IDENTITY_MISMATCH")
    branch = repo.get("default_branch")
    if not isinstance(branch, str) or not fullmatch(r"[A-Za-z0-9_./-]{1,200}", branch):
        raise ValueError("PROVIDER_DEFAULT_BRANCH_UNKNOWN")
    base = getter.get_commit(target.repository, branch)
    base_sha = base.get("sha")
    if not isinstance(base_sha, str) or not fullmatch(_SHA, base_sha):
        raise ValueError("PROVIDER_DEFAULT_BRANCH_SHA_UNKNOWN")
    raw = getter.get_file_bytes(target.repository, target.graph_path, base_sha)
    if not isinstance(raw, bytes) or len(raw) > 5_000_000:
        raise ValueError("PROVIDER_GRAPH_FILE_INVALID")
    graph_digest = _sha256(raw)
    try:
        graph = loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("PROVIDER_GRAPH_JSON_INVALID") from exc
    if not isinstance(graph, dict) or not isinstance(graph.get("programme"), dict):
        raise ValueError("PROVIDER_GRAPH_STRUCTURE_INVALID")
    if str(graph["programme"].get("repository") or "").lower() != target.repository.lower():
        raise ValueError("PROVIDER_GRAPH_REPOSITORY_MISMATCH")
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("PROVIDER_GRAPH_NODES_INVALID")
    found = [n for n in nodes if isinstance(n, dict) and n.get("ref") == target.leaf_ref and n.get("kind") == "LEAF"]
    if len(found) != 1:
        raise ValueError("PROVIDER_GRAPH_LEAF_NOT_BOUND")
    pr_ref = found[0].get("primary_pr")
    if not isinstance(pr_ref, str) or not _ref(pr_ref, target.repository, target.pr_number):
        raise ValueError("PROVIDER_GRAPH_PR_NOT_BOUND")
    pull = getter.get_pull(target.repository, target.pr_number)
    if pull.get("number") != target.pr_number:
        raise ValueError("PROVIDER_PR_NUMBER_MISMATCH")
    # The provider's actual base repository is an identity check.  Do NOT
    # fill an "observed" field by copying the target supplied by the caller.
    base_identity = (pull.get("base") or {}).get("repo")
    if (not isinstance(base_identity, Mapping) or
            base_identity.get("id") != target.repository_id or
            str(base_identity.get("full_name") or "").lower() != target.repository.lower()):
        raise ValueError("PROVIDER_PR_BASE_REPOSITORY_MISMATCH")
    candidate_sha = (pull.get("head") or {}).get("sha")
    if not isinstance(candidate_sha, str) or not fullmatch(_SHA, candidate_sha):
        raise ValueError("PROVIDER_PR_HEAD_INVALID")
    actual_base = (pull.get("base") or {}).get("ref")
    expected_base = graph["programme"].get("base_ref")
    if isinstance(expected_base, str) and actual_base != expected_base:
        raise ValueError("PROVIDER_PR_BASE_MISMATCH")
    comments = getter.get_issue_comments(target.repository, int(target.leaf_ref.rsplit("#", 1)[-1]))
    checks = getter.get_check_runs(target.repository, candidate_sha)
    if not isinstance(comments, list) or not isinstance(checks, list):
        raise ValueError("PROVIDER_COMMENTS_OR_CHECKS_INVALID")
    if len(comments) > 2000 or len(checks) > 1000:
        raise ValueError("PROVIDER_OBSERVATION_UNBOUNDED")
    for comment in comments:
        if not isinstance(comment, Mapping) or type(comment.get("id")) is not int or not isinstance(comment.get("body"), str):
            raise ValueError("PROVIDER_COMMENT_INVALID")
    for check in checks:
        if not isinstance(check, Mapping) or not isinstance(check.get("name"), str):
            raise ValueError("PROVIDER_SELECTED_CHECK_INVALID")
    late_pull = getter.get_pull(target.repository, target.pr_number)
    late_base = (late_pull.get("base") or {})
    late_base_identity = late_base.get("repo") or {}
    if (late_pull.get("number") != target.pr_number or
            (late_pull.get("head") or {}).get("sha") != candidate_sha or
            late_base.get("ref") != actual_base or
            late_base_identity.get("id") != target.repository_id or
            str(late_base_identity.get("full_name") or "").lower() != target.repository.lower()):
        raise ValueError("PROVIDER_PR_MOVED_IN_CYCLE")
    late = getter.get_commit(target.repository, branch)
    if late.get("sha") != base_sha:
        raise ValueError("PROVIDER_DEFAULT_BRANCH_MOVED_IN_CYCLE")
    selected_checks = []
    for c in checks:
        selected_checks.append(ObservedCheck(
            name=c["name"], candidate_sha=str(c.get("head_sha") or ""),
            conclusion=str(c.get("conclusion") or "UNKNOWN").lower(),
            executed=c.get("status") == "completed" and c.get("conclusion") != "skipped",
        ))
    # Reuse the genuine native V3.2 parser/validator. Claim observations
    # remain UNATTESTED even when shape, author and candidate are coherent.
    comment_claims = audit_native_comment_claims(
        graph=graph, leaf_ref=target.leaf_ref,
        candidate_sha=candidate_sha, comments=comments,
    )
    source_identity = {
        "repository_id": target.repository_id, "default_branch": branch,
        "default_branch_sha": base_sha, "graph_digest": graph_digest,
        "pr_number": target.pr_number, "candidate_sha": candidate_sha,
        "comments_digest": _sha256(_canonical(comments)),
        "selected_checks_digest": _sha256(_canonical(checks)),
    }
    return {"fingerprint": _sha256(_canonical(source_identity)), "graph_digest": graph_digest,
            "candidate_sha": candidate_sha, "selected_checks": selected_checks,
            "observed_pr_repository": str(base_identity["full_name"]),
            "observed_pr_number": pull["number"],
            "comment_claims": comment_claims}


def inspect_v32_read_only(
    target: PreflightTarget,
    getter: ReadOnlyGetter,
    facts: Mapping[str, Any] | None = None,
) -> PreflightResult:
    """Two in-function GET cycles; no authentic positive admission or write."""
    errors = _target_errors(target)
    if errors:
        return PreflightResult("FAILED_TARGET", tuple(errors), "UNKNOWN", None, None, 0, None)
    try:
        first = _round(target, getter)
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RuntimeError) as exc:
        return PreflightResult("HOLD_PROVIDER_READ", (str(exc) or "PROVIDER_READ_FAILED",), "UNKNOWN", None, None, 0, None)
    try:
        second = _round(target, getter)
    except (ValueError, TypeError, KeyError, AttributeError, OSError, RuntimeError) as exc:
        return PreflightResult("HOLD_PROVIDER_READ", (str(exc) or "PROVIDER_READ_FAILED",), "UNKNOWN", first["graph_digest"], None, 1, None)
    if first["fingerprint"] != second["fingerprint"]:
        return PreflightResult("HOLD_MOVED_SOURCE", ("SOURCE_CHANGED_BETWEEN_NONATOMIC_PASSES",),
                               "DRIFT_DETECTED", None, None, 2, None)
    if target.expected_graph_sha256 is not None and target.expected_graph_sha256 != first["graph_digest"]:
        return PreflightResult("HOLD_GRAPH_DIGEST", ("PINNED_GRAPH_DIGEST_MISMATCH",),
                               "MISMATCH", first["graph_digest"], None, 2, None)
    selection = SourceSelection(
        repository=target.repository, leaf_ref=target.leaf_ref, pr_number=target.pr_number,
        current_head=second["candidate_sha"],
        observed_pr_repository=second["observed_pr_repository"],
        observed_pr_number=second["observed_pr_number"],
    )
    probe = probe_v32_fact(selection, facts, second["selected_checks"])
    return PreflightResult(
        "FAILED_SELECTED_OR_FACT" if probe.state == "FAILED" else "HOLD_NO_APPROVED_POSITIVE_ISSUER",
        tuple(dict.fromkeys([*probe.reasons, "NONATOMIC_READ_ONLY_PROVIDER_WITNESS"])),
        "TWO_CONSISTENT_NONATOMIC_READS_NOT_ATOMIC_PROOF", first["graph_digest"],
        second["candidate_sha"], 2, probe,
        comment_claims=second["comment_claims"],
    )
