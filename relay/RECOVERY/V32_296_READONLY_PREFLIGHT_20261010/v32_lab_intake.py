"""Read-only, non-admitting V3.2 lab source-intake witness for Common #296.

B1 starts before a product PR exists. Reads an explicitly selected GitHub
lab, native-shaped graph and real issue objects twice. It cannot prove human
Owner approval, CI, facts, writer lease, or cutover.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
from typing import Any, Callable, Mapping, Protocol

_REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
_REF_RE = re.compile(r"[A-Za-z0-9_.-]+#[1-9][0-9]*\Z")
_SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
_GRAPH_DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
_MAX_NODES = 25

class ReadOnlyLabProvider(Protocol):
    def get_repository(self, repository: str) -> Mapping[str, Any]: ...
    def get_commit(self, repository: str, ref: str) -> Mapping[str, Any]: ...
    def get_file_bytes(self, repository: str, path: str, ref: str) -> bytes: ...
    def get_issue(self, repository: str, number: int) -> Mapping[str, Any]: ...

@dataclass(frozen=True)
class LabTarget:
    repository: str
    repository_id: int
    graph_path: str
    root_ref: str
    expected_graph_digest: str | None = None

@dataclass(frozen=True)
class LabIntake:
    status: str
    reasons: tuple[str, ...]
    observations: Mapping[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reasons": list(self.reasons),
            "observations": dict(self.observations) if self.observations else None,
            "owner_release_authenticated": False,
            "positive_fact_issuer": False,
            "accepted_evidence_count": None,
            "writer_authorized": False,
            "delp_invoked": False,
        }

def _bad_target(target: LabTarget) -> list[str]:
    result = []
    repo = target.repository
    if (not isinstance(repo, str) or not _REPO_RE.fullmatch(repo) or
            any(s in (".", "..") for s in repo.split("/"))):
        result.append("INVALID_LAB_REPOSITORY")
    if type(target.repository_id) is not int or target.repository_id < 1:
        result.append("INVALID_LAB_REPOSITORY_ID")
    path = target.graph_path
    if (not isinstance(path, str) or len(path) > 256 or not path.endswith(".json") or
            any(s in ("", ".", "..") for s in path.split("/")) or path.startswith("/")):
        result.append("INVALID_LAB_GRAPH_PATH")
    root = target.root_ref
    if (not isinstance(root, str) or not _REF_RE.fullmatch(root) or
            (isinstance(repo, str) and "/" in repo and
             root.split("#", 1)[0].lower() != repo.rsplit("/", 1)[1].lower())):
        result.append("INVALID_LAB_ROOT_REF")
    if target.expected_graph_digest is not None and (
            not isinstance(target.expected_graph_digest, str) or
            not _GRAPH_DIGEST_RE.fullmatch(target.expected_graph_digest)):
        result.append("INVALID_EXPECTED_GRAPH_DIGEST")
    return result

def _native_structure(graph: Mapping[str, Any], repository: str) -> None:
    """Invoke the unchanged native V3.2 graph validator; do not fork schema."""
    path = (Path(__file__).resolve().parents[3] / "skills" /
            "engineering-pr-delivery-v3.2" / "scripts" / "delp_projection_v32.py")
    spec = spec_from_file_location("_v32_b1_native", path)
    if spec is None or spec.loader is None:
        raise ValueError("NATIVE_V32_GRAPH_UNAVAILABLE")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        module.validate_graph(graph)
        module.require_repository_match(graph, repository, live=True)
    except (ValueError, TypeError, AttributeError, RuntimeError) as exc:
        raise ValueError("NATIVE_V32_GRAPH_INVALID") from exc

def _digest(value: bytes) -> str:
    return "sha256:" + sha256(value).hexdigest()

def _round(target: LabTarget, getter: ReadOnlyLabProvider,
           validate: Callable[[Mapping[str, Any], str], None]) -> dict[str, Any]:
    repo = getter.get_repository(target.repository)
    if (not isinstance(repo, Mapping) or
        str(repo.get("full_name") or "").lower() != target.repository.lower() or
        type(repo.get("id")) is not int or repo["id"] != target.repository_id):
        raise ValueError("LAB_REPOSITORY_IDENTITY_MISMATCH")
    branch = repo.get("default_branch")
    if (not isinstance(branch, str) or
            not re.fullmatch(r"[A-Za-z0-9_./-]{1,200}", branch) or
            any(s in ("", ".", "..") for s in branch.split("/"))):
        raise ValueError("LAB_DEFAULT_BRANCH_UNRESOLVED")
    base = getter.get_commit(target.repository, branch)
    sha = base.get("sha") if isinstance(base, Mapping) else None
    if not isinstance(sha, str) or not _SHA_RE.fullmatch(sha):
        raise ValueError("LAB_DEFAULT_BRANCH_SHA_UNRESOLVED")
    raw = getter.get_file_bytes(target.repository, target.graph_path, sha)
    if not isinstance(raw, bytes) or len(raw) > 5_000_000:
        raise ValueError("LAB_GRAPH_BYTES_INVALID")
    graph_hash = _digest(raw)
    if target.expected_graph_digest is not None and graph_hash != target.expected_graph_digest:
        raise ValueError("LAB_GRAPH_DIGEST_MISMATCH")
    try:
        graph = json.loads(raw.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise ValueError("LAB_GRAPH_JSON_INVALID") from exc
    if not isinstance(graph, Mapping) or not isinstance(graph.get("programme"), Mapping):
        raise ValueError("LAB_GRAPH_SHAPE_INVALID")
    programme = graph["programme"]
    if str(programme.get("repository") or "").lower() != target.repository.lower():
        raise ValueError("LAB_GRAPH_FOREIGN_REPOSITORY")
    if programme.get("root") != target.root_ref:
        raise ValueError("LAB_GRAPH_ROOT_MISMATCH")
    validate(graph, target.repository)
    nodes = graph.get("nodes")
    if not isinstance(nodes, list) or len(nodes) < 2 or len(nodes) > _MAX_NODES:
        raise ValueError("LAB_GRAPH_NODES_UNMATERIALIZED_OR_UNBOUNDED")
    refs = [node.get("ref") if isinstance(node, Mapping) else None for node in nodes]
    if len(set(refs)) != len(refs) or target.root_ref not in refs or not all(
            isinstance(ref, str) and _REF_RE.fullmatch(ref) and
            ref.split("#", 1)[0].lower() == target.repository.rsplit("/", 1)[1].lower()
            for ref in refs):
        raise ValueError("LAB_GRAPH_ISSUE_REF_INVALID")
    issue_facts = []
    for ref in refs:
        number = int(ref.split("#")[-1])
        issue = getter.get_issue(target.repository, number)
        if (not isinstance(issue, Mapping) or
                type(issue.get("number")) is not int or issue.get("number") != number or
                not isinstance(issue.get("title"), str) or not issue["title"].strip() or
                not isinstance(issue.get("body"), str) or
                issue.get("pull_request") is not None):
            raise ValueError("LAB_GRAPH_ISSUE_NOT_MATERIALIZED")
        # Human text is hashed into the source fingerprint but never emitted.
        issue_facts.append({"number": number, "title": issue["title"], "body": issue["body"]})
    late_commit = getter.get_commit(target.repository, branch)
    if not isinstance(late_commit, Mapping) or late_commit.get("sha") != sha:
        raise ValueError("LAB_DEFAULT_BRANCH_MOVED_DURING_READ")
    fingerprint = _digest(json.dumps({
        "repo_id": repo["id"], "repository": target.repository.lower(),
        "base": sha, "graph_digest": graph_hash, "issues": issue_facts,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return {"fingerprint": fingerprint, "repository": target.repository,
            "repository_id": target.repository_id, "base_ref": branch,
            "base_sha": sha, "graph_digest": graph_hash,
            "root_ref": target.root_ref, "issues_observed": len(refs)}

def inspect_lab_read_only(target: LabTarget, getter: ReadOnlyLabProvider,
                          *, native_validate: Callable[[Mapping[str, Any], str], None] = _native_structure) -> LabIntake:
    """Never yields APPROVED/PASS/facts/writer rights, including coherent GETs."""
    invalid = _bad_target(target)
    if invalid:
        return LabIntake("FAILED_TARGET", tuple(invalid))
    try:
        first = _round(target, getter, native_validate)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        code = (str(exc) if isinstance(exc, ValueError) and
                (str(exc).startswith("LAB_") or
                 str(exc) in ("NATIVE_V32_GRAPH_INVALID", "NATIVE_V32_GRAPH_UNAVAILABLE"))
                else "LAB_SOURCE_GET_UNAVAILABLE")
        return LabIntake("HOLD_LAB_SOURCE", (code,))
    try:
        second = _round(target, getter, native_validate)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError, AttributeError):
        return LabIntake("HOLD_LAB_SOURCE", ("LAB_SECOND_READ_UNAVAILABLE",))
    if first["fingerprint"] != second["fingerprint"]:
        return LabIntake("HOLD_LAB_DRIFT", ("LAB_NONATOMIC_SOURCE_MOVED",))
    observed = {key: first[key] for key in (
        "repository", "repository_id", "base_ref", "base_sha",
        "graph_digest", "root_ref", "issues_observed")}
    return LabIntake("HOLD_OWNER_RELEASE_UNVERIFIED", (
        "LAB_STRUCTURE_ONLY_NOT_HUMAN_OWNER_APPROVAL",
        "LAB_NONATOMIC_GETS_NOT_ORIGINAL_SOURCE_ATTESTATION"), observed)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--repository-id", type=int, required=True)
    parser.add_argument("--graph-path", required=True)
    parser.add_argument("--root-ref", required=True)
    parser.add_argument("--expected-graph-digest")
    args = parser.parse_args()
    from v32_github_get import GitHubGetOnly
    target = LabTarget(args.repository, args.repository_id,
                       args.graph_path, args.root_ref, args.expected_graph_digest)
    report = inspect_lab_read_only(target, GitHubGetOnly())
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    return 1 if report.status == "FAILED_TARGET" else 2

if __name__ == "__main__":
    raise SystemExit(main())
