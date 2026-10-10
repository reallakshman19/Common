"""One V3.2 lab→native DELP→issue/PR preview→in-memory publication→C6 cycle.

OFFLINE, GET-only, NO production writes. The native V3.2 module remains the
exclusive reducer, title/status owner and C6 implementation. The existing
source-bound PR view owns managed-section rendering. This adapter owns neither
Owner authorization nor evidence acceptance.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any, Mapping

from pr_source_binding import BindingError, PreviewPins, preview_source_binding


class CycleHold(ValueError):
    """Safe, non-secret-bearing failure code."""


def _hold(condition: bool, code: str) -> None:
    if not condition:
        raise CycleHold(code)


def _native_modules():
    native_path = (Path(__file__).resolve().parents[3] / "skills" /
                   "engineering-pr-delivery-v3.2" / "scripts")
    _hold((native_path / "delp_projection_v32.py").is_file(),
          "NATIVE_V32_SOURCE_NOT_IN_CHECKOUT")
    if str(native_path) not in sys.path:
        sys.path.insert(0, str(native_path))
    import delp_projection_v32 as delp
    import pr_responsibility_view_v32 as views
    return delp, views


def _digest(value: Any) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def _number(ref: str) -> int:
    return int(ref.rsplit("#", 1)[-1])


class SnapshotGET:
    """Fully materialized private GET snapshot; exposes NO write methods.

    Source must be re-captured from actual GitHub. This adapter never pretends
    that importing a snapshot independently authenticates its actor/approval.
    """
    def __init__(self, source: Mapping[str, Any]):
        _hold(source.get("source_kind") == "GITHUB_GET_ONLY_UNATTESTED",
              "SOURCE_CAPTURE_KIND_UNTRUSTED")
        self.source = deepcopy(dict(source))
        self.repository = self.source.get("repository")

    def get_commit_sha(self, ref: str) -> str:
        _hold(ref == self.source.get("base_ref", "main"), "BASE_REF_NOT_CAPTURED")
        return self.source["main_sha"]

    def get_issue(self, number: int) -> dict:
        _hold(str(number) in self.source["issues"], "SOURCE_ISSUE_MISSING")
        return deepcopy(self.source["issues"][str(number)])

    def get_pull(self, number: int) -> dict:
        _hold(str(number) in self.source["pulls"], "SOURCE_PR_MISSING")
        return deepcopy(self.source["pulls"][str(number)])

    def list_comments(self, number: int) -> list:
        _hold(str(number) in self.source["comments"], "SOURCE_COMMENTS_MISSING")
        return deepcopy(self.source["comments"][str(number)])


def _source_fingerprint(transport: SnapshotGET, graph: Mapping[str, Any]) -> str:
    nodes = graph["nodes"]
    base = graph["programme"].get("base_ref", "main")
    selected_issues = {_number(n["ref"]): transport.get_issue(_number(n["ref"]))
                       for n in nodes}
    selected_pulls = {_number(n["primary_pr"]): transport.get_pull(_number(n["primary_pr"]))
                      for n in nodes if n.get("kind") == "LEAF" and n.get("primary_pr")}
    selected_comments = {_number(n["ref"]): transport.list_comments(_number(n["ref"]))
                         for n in nodes if n.get("kind") == "LEAF"}
    return _digest({"base": transport.get_commit_sha(base),
                    "issues": selected_issues, "pulls": selected_pulls,
                    "comments": selected_comments})


def integrated_shadow(
    raw_graph: bytes, pins: PreviewPins, source: Mapping[str, Any],
) -> dict[str, Any]:
    """Complete non-admitting lifecycle on one immutable-shaped GET snapshot.

    Verifies source→PR binding, executes original native facts/DELP, renders
    managed PR text with the existing view module, simulates native issue
    LIVE_STATUS/title publication twice, and snapshots native C6 frontier.
    All mutations are exclusively in native InMemoryStore, never GitHub.
    """
    _hold(source.get("repository") == pins.repository, "SOURCE_REPOSITORY_MISMATCH")
    _hold(source.get("repository_id") == pins.repository_id,
          "SOURCE_NUMERIC_REPOSITORY_MISMATCH")
    _hold(source.get("graph_git_blob") == pins.released_graph_blob_oid,
          "SOURCE_GRAPH_BLOB_MISMATCH")
    transport = SnapshotGET(source)
    graph = json.loads(raw_graph)
    delp, views = _native_modules()
    delp.validate_graph(graph)
    delp.require_repository_match(graph, pins.repository, live=True)
    _hold(transport.get_commit_sha(graph["programme"].get("base_ref", "main")) ==
          source.get("final_main_sha"), "SOURCE_DEFAULT_BRANCH_MOVED")
    leaf = next((node for node in graph["nodes"] if node.get("ref") == pins.leaf_ref), None)
    _hold(isinstance(leaf, dict) and leaf.get("kind") == "LEAF" and
          leaf.get("primary_pr"), "SOURCE_LEAF_PR_UNBOUND")
    pr_number = _number(leaf["primary_pr"])
    observed_pr = transport.get_pull(pr_number)
    repo = {"full_name": pins.repository, "id": source["repository_id"]}
    binding = preview_source_binding(raw_graph, pins, repo, observed_pr)
    _hold(binding["observed_pr_head_sha"] == pins.expected_pr_head_sha,
          "SOURCE_CANDIDATE_MISMATCH")
    first = _source_fingerprint(transport, graph)
    native_plan = delp.plan_github(transport, graph)
    ledger = delp.ledger_from_github(transport, graph)
    observations = delp.observe_github(transport, graph)
    projection = delp.project(graph, ledger, observations)
    _hold(projection["input_digest"] == native_plan["input_digest"],
          "NATIVE_INPUT_DIGEST_MISMATCH")
    _hold(set(native_plan["expected_titles"]) == {n["ref"] for n in graph["nodes"]},
          "NATIVE_ISSUE_COVERAGE_INVALID")
    _hold((observations.get(pins.leaf_ref) or {}).get("candidate_sha") ==
          pins.expected_pr_head_sha, "NATIVE_PROVIDER_HEAD_MISMATCH")
    core = None
    core_hold = None
    try:
        core = delp.source_bound_responsibility_core(graph, projection, pins.leaf_ref)
    except delp.DelpError as exc:
        # Native V3.2 core currently refuses full owner/repo#PR refs even
        # when native graph, projector and C6 accept those original lab refs.
        # Never counterfeit an equivalent core or mutate the approved graph.
        if str(exc) != "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY":
            raise
        core_hold = "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY"
    if core is not None:
        _hold(core["digests"]["input"] == native_plan["input_digest"] and
              core["candidate_sha"] == pins.expected_pr_head_sha,
              "NATIVE_RESPONSIBILITY_CORE_DRIFT")
    c6 = delp.frontier(graph, ledger, observations, pins.leaf_ref)
    _hold(c6["observed"].get("candidate_sha") == pins.expected_pr_head_sha,
          "NATIVE_FRONTIER_CANDIDATE_DRIFT")
    _hold(first == _source_fingerprint(transport, graph),
          "SOURCE_CHANGED_ACROSS_LIFECYCLE")

    # Existing V3.2 managed PR block renderer; deliberately represents Owner
    # provenance as UNVERIFIED, never manufactures a real OwnerIntent/OR record.
    native_view = {
        "responsibility": leaf.get("responsibility_id") or "UNRELEASED",
        "leaf": pins.leaf_ref,
        "owner_trace": {"owner_intents": [{"id": "UNVERIFIED_ORIGINAL_SOURCE"}]},
        "OR_ids": [],
        "claim_ids": list(leaf.get("owns_claims") or []),
        "golden_fixture_ids": [],
        "pr": {"number": pr_number, "head_sha": pins.expected_pr_head_sha,
               "lifecycle": ("MERGED" if observed_pr.get("merged") else
                             observed_pr.get("state", "UNKNOWN").upper()),
               "binding": "BOUND"},
        "qualification": {"state": "UNPROVEN", "basis": "NO_INDEPENDENT_WITNESS"},
        "input_digest": native_plan["input_digest"],
        "actual_next": "AUTHENTICATE_OWNER_AND_EVIDENCE_BEFORE_PUBLICATION",
    }
    block = views.render_pr_block(native_view)
    old_body = observed_pr.get("body")
    _hold(isinstance(old_body, str), "PR_HUMAN_BODY_NOT_OBSERVED")
    new_body = views.reconcile_managed_block(
        old_body, block, observed_digest=views.digest(old_body), pr=True)
    _hold(views.inspect_managed_block(new_body, block, pr=True) == "MATCH",
          "PR_MANAGED_VIEW_READBACK_FAILED")

    # Use the unchanged native issue publisher against its IN-MEMORY store,
    # including all six nodes, per-node versioned status, and idempotent retry.
    base_titles = {ref: transport.get_issue(_number(ref))["title"]
                   for ref in native_plan["expected_titles"]}
    store = delp.InMemoryStore(base_titles)
    def ledger_get():
        return delp.ledger_from_github(transport, graph)
    def observation_get():
        return delp.observe_github(transport, graph)
    first_pass = delp.sync_projection(
        store, graph, ledger_get, observation_get, base_titles,
        expected_input_digest=native_plan["input_digest"])
    second_pass = delp.sync_projection(
        store, graph, ledger_get, observation_get, base_titles,
        expected_input_digest=native_plan["input_digest"])
    _hold(all(row["status"] == "UNCHANGED" for row in second_pass.values()),
          "NATIVE_IN_MEMORY_IDEMPOTENCE_FAILED")
    _hold(store.titles == native_plan["expected_titles"],
          "NATIVE_ISSUE_TITLE_READBACK_FAILED")
    _hold(first == _source_fingerprint(transport, graph),
          "SOURCE_CHANGED_AFTER_SIMULATION")
    fresh_c6 = delp.frontier(graph, ledger_get(), observation_get(), pins.leaf_ref)
    c6_reentry = delp.frontier_drift(c6, fresh_c6)
    _hold(c6_reentry["status"] == "CURRENT" and
          c6_reentry["action"] == "NONE", "NATIVE_C6_REENTRY_DRIFT")

    return {
        "status": "INTEGRATED_SHADOW_ONLY_NOT_RELEASE_READY",
        "repository": pins.repository,
        "source_kind": source["source_kind"],
        "source_snapshot_fingerprint": first,
        "binding": binding,
        "native_input_digest": native_plan["input_digest"],
        "native_rejected_facts": native_plan["rejected_facts"],
        "native_expected_issue_titles": native_plan["expected_titles"],
        "native_issue_drift": native_plan["drift"],
        "native_core": core,
        "native_core_hold": core_hold,
        "pr_managed_block": block,
        "pr_body_preview": new_body,
        "pr_body_changed_in_preview": new_body != old_body,
        "in_memory_issue_first_pass": first_pass,
        "in_memory_issue_second_pass": second_pass,
        "c6_frontier": c6,
        "c6_same_source_reentry": c6_reentry,
        "owner_source_authenticated": False,
        "independent_witness": "NOT_EXECUTED",
        "eligible_evidence_admitted_by_this_cycle": False,
        "issue_or_pr_github_writes": False,
        "production_activation": False,
        "real_cold_successor": "NOT_EXECUTED",
    }


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="V3.2 full-cycle offline shadow. NO GITHUB WRITES.")
    p.add_argument("--graph", type=Path, required=True)
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--repository-id", type=int, required=True)
    p.add_argument("--leaf", required=True)
    p.add_argument("--graph-blob", required=True)
    p.add_argument("--head", required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise SystemExit("OUTPUT_ALREADY_EXISTS_REFUSING_OVERWRITE")
    graph = args.graph.read_bytes()
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    report = integrated_shadow(graph, PreviewPins(
        snapshot["repository"], args.repository_id, args.graph_blob,
        args.leaf, args.head), snapshot)
    # Do not print private issue/comment bodies to stdout or commit them to Git.
    import os
    fd = os.open(args.output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")
    print("OFFLINE_INTEGRATED_SHADOW_OK; OUTPUT_PRIVATE_0600; NO_GITHUB_WRITES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
