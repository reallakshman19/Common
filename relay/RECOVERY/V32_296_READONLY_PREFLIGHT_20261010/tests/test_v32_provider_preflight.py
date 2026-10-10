"""In-process fake GET provider. No live provider or real Owner authority claimed."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from json import dumps
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from v32_provider_preflight import PreflightTarget, inspect_v32_read_only

REPO = "lab/v32-proto"
H1 = "1" * 40
H2 = "2" * 40
MAIN = "a" * 40
GRAPH = {
    "programme": {"repository": REPO, "root": "v32-proto#1", "base_ref": "main"},
    "nodes": [
        {"ref": "v32-proto#1", "kind": "ROOT"},
        {"ref": "v32-proto#4", "kind": "LEAF", "primary_pr": "v32-proto#10"},
    ],
}

def raw_graph(graph=GRAPH):
    return dumps(graph, sort_keys=True).encode("utf-8")


class FakeProvider:
    def __init__(self):
        self.calls = []
        self.graph = deepcopy(GRAPH)
        self.sha = H1
        self.base = MAIN
        self.repo_id = 112233
        self.pr_base_repository = REPO
        self.pr_base_repo_id = 112233
        self.pr_base_ref = "main"
        self.checks = [{"name": "build", "head_sha": H1, "status": "completed", "conclusion": "success"}]
        self.comments = [{"id": 1, "body": "historical comment"}]
        self.call_mutator = None
        self.fail_on = None

    def _before(self, kind):
        self.calls.append(kind)
        if self.call_mutator:
            self.call_mutator(kind, len(self.calls), self)
        if kind == self.fail_on:
            raise OSError("PROVIDER_GET_FORBIDDEN")

    def get_repository(self, repository):
        self._before("repo")
        return {"full_name": REPO, "id": self.repo_id, "default_branch": "main"}

    def get_commit(self, repository, ref):
        self._before("commit")
        return {"sha": self.base}

    def get_file_bytes(self, repository, path, ref):
        self._before("graph")
        return raw_graph(self.graph)

    def get_pull(self, repository, number):
        self._before("pull")
        return {
            "number": 10, "head": {"sha": self.sha},
            "base": {
                "ref": self.pr_base_ref,
                "repo": {"id": self.pr_base_repo_id, "full_name": self.pr_base_repository},
            },
        }

    def get_issue_comments(self, repository, number):
        self._before("comments")
        return deepcopy(self.comments)

    def get_check_runs(self, repository, head):
        self._before("checks")
        return deepcopy(self.checks)


def target(**overrides):
    return replace(PreflightTarget(repository=REPO, repository_id=112233,
                                   graph_path="governance/released-graph.json",
                                   leaf_ref="v32-proto#4", pr_number=10), **overrides)


def fact(head=H1):
    return {"schema": "relay-v3.2-delp-checkpoint-facts",
            "responsibility": {"issue": "v32-proto#4"},
            "material": {"candidate_sha": head, "pr": "v32-proto#10"},
            "units": [{"id": "R01", "state": "COMPLETE", "result": "VERIFIED",
                       "candidate_sha": head, "evidence_refs": ["synthetic:assertion"]}]}


class V32ProviderPreflightTests(unittest.TestCase):
    def test_01_two_coherent_native_shaped_get_cycles_are_still_hold(self):
        p = FakeProvider()
        v = inspect_v32_read_only(target(), p, fact())
        self.assertEqual(v.status, "HOLD_NO_APPROVED_POSITIVE_ISSUER")
        self.assertEqual(v.source_currentness, "TWO_CONSISTENT_NONATOMIC_READS_NOT_ATOMIC_PROOF")
        self.assertEqual(v.pass_count, 2)
        self.assertEqual(len(p.calls), 16)
        self.assertIsNone(v.accepted_evidence_count)
        self.assertFalse(v.writer_authorized)
        self.assertFalse(v.delp_invoked)
        self.assertEqual(v.candidate_sha, H1)
        self.assertEqual(v.probe.state, "HOLD_UNKNOWN_AUTHORITY_OR_SOURCE")

    def test_02_wrong_repository_id_is_source_failure(self):
        p = FakeProvider(); p.repo_id = 4321
        v = inspect_v32_read_only(target(), p)
        self.assertEqual(v.status, "HOLD_PROVIDER_READ")
        self.assertIn("PROVIDER_REPOSITORY_IDENTITY_MISMATCH", v.reasons)

    def test_03_old_repo_graph_cannot_bind_new_repo_target(self):
        p = FakeProvider(); p.graph["programme"]["repository"] = "historic/v32-proto"
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_GRAPH_REPOSITORY_MISMATCH", v.reasons)

    def test_04_undeclared_leaf_rejected(self):
        p = FakeProvider()
        v = inspect_v32_read_only(target(leaf_ref="v32-proto#5"), p)
        self.assertIn("PROVIDER_GRAPH_LEAF_NOT_BOUND", v.reasons)

    def test_05_unbound_product_pr_rejected(self):
        p = FakeProvider(); p.graph["nodes"][1]["primary_pr"] = "v32-proto#11"
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_GRAPH_PR_NOT_BOUND", v.reasons)

    def test_06_moved_candidate_across_passes_holds(self):
        p = FakeProvider()
        def move(kind, count, this):
            if kind == "repo" and count == 9:
                this.sha = H2
                this.checks[0]["head_sha"] = H2
        p.call_mutator = move
        v = inspect_v32_read_only(target(), p, fact())
        self.assertEqual(v.status, "HOLD_MOVED_SOURCE")
        self.assertEqual(v.source_currentness, "DRIFT_DETECTED")
        self.assertIsNone(v.candidate_sha)
        self.assertIsNone(v.probe)

    def test_07_changed_comment_across_passes_holds(self):
        p = FakeProvider()
        def move(kind, count, this):
            if kind == "repo" and count == 9:
                this.comments[0]["body"] = "changed evidence comment"
        p.call_mutator = move
        self.assertEqual(inspect_v32_read_only(target(), p).status, "HOLD_MOVED_SOURCE")

    def test_08_changed_check_across_passes_holds(self):
        p = FakeProvider()
        def change(kind, count, this):
            if kind == "repo" and count == 9:
                this.checks[0]["conclusion"] = "failure"
        p.call_mutator = change
        self.assertEqual(inspect_v32_read_only(target(), p).status, "HOLD_MOVED_SOURCE")

    def test_09_changed_graph_across_passes_holds(self):
        p = FakeProvider()
        def move(kind, count, this):
            if kind == "repo" and count == 9:
                this.graph["programme"]["revision"] = "unexpected"
        p.call_mutator = move
        self.assertEqual(inspect_v32_read_only(target(), p).status, "HOLD_MOVED_SOURCE")

    def test_10_mid_cycle_default_branch_move_blocks(self):
        p = FakeProvider()
        def mutate(kind, count, this):
            if kind == "commit" and count == 8:
                this.base = H2
        p.call_mutator = mutate
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_DEFAULT_BRANCH_MOVED_IN_CYCLE", v.reasons)
        self.assertEqual(v.pass_count, 0)

    def test_11_pinned_graph_digest_mismatch_holds(self):
        p = FakeProvider()
        v = inspect_v32_read_only(target(expected_graph_sha256="sha256:" + "0" * 64), p)
        self.assertEqual(v.status, "HOLD_GRAPH_DIGEST")
        self.assertIn("PINNED_GRAPH_DIGEST_MISMATCH", v.reasons)

    def test_12_correct_digest_is_not_owner_release_authorization(self):
        p = FakeProvider()
        dg = "sha256:" + sha256(raw_graph()).hexdigest()
        v = inspect_v32_read_only(target(expected_graph_sha256=dg), p, fact())
        self.assertEqual(v.graph_digest, dg)
        self.assertEqual(v.status, "HOLD_NO_APPROVED_POSITIVE_ISSUER")

    def test_13_selected_skipped_check_not_execution(self):
        p = FakeProvider()
        p.checks[0]["conclusion"] = "skipped"
        v = inspect_v32_read_only(target(), p, fact())
        self.assertIn("CHECK_NOT_EXECUTED:build", v.probe.reasons)

    def test_14_failed_selected_check_not_success(self):
        p = FakeProvider()
        p.checks[0]["conclusion"] = "failure"
        v = inspect_v32_read_only(target(), p, fact())
        self.assertIn("SELECTED_CHECK_FAILED:build", v.probe.reasons)
        self.assertEqual(v.probe.state, "FAILED")
        self.assertEqual(v.status, "FAILED_SELECTED_OR_FACT")

    def test_15_missing_checks_remains_not_run(self):
        p = FakeProvider(); p.checks = []
        v = inspect_v32_read_only(target(), p, fact())
        self.assertIn("SELECTED_CHECKS_NOT_RUN_OR_NOT_OBSERVED", v.probe.reasons)

    def test_16_second_cycle_provider_error_holds(self):
        p = FakeProvider()
        def change(kind, count, this):
            if kind == "repo" and count == 9:
                this.fail_on = "checks"
        p.call_mutator = change
        v = inspect_v32_read_only(target(), p, fact())
        self.assertEqual(v.status, "HOLD_PROVIDER_READ")
        self.assertEqual(v.pass_count, 1)
        self.assertIsNone(v.candidate_sha)

    def test_17_missing_observed_pr_head_blocks(self):
        p = FakeProvider(); p.sha = None
        self.assertIn("PROVIDER_PR_HEAD_INVALID", inspect_v32_read_only(target(), p).reasons)

    def test_18_wrong_product_base_blocks(self):
        p = FakeProvider(); p.graph["programme"]["base_ref"] = "release"
        self.assertIn("PROVIDER_PR_BASE_MISMATCH", inspect_v32_read_only(target(), p).reasons)

    def test_19_invalid_path_blocks_before_get(self):
        p = FakeProvider()
        v = inspect_v32_read_only(target(graph_path="../secret.json"), p)
        self.assertEqual(v.status, "FAILED_TARGET")
        self.assertEqual(p.calls, [])

    def test_20_no_original_provenance_claimed_from_two_reads(self):
        p = FakeProvider()
        v = inspect_v32_read_only(target(), p, fact()).as_dict()
        self.assertIn("ORIGINAL_OWNER_SOURCE_NOT_AUTHENTICATED", v["probe"]["reasons"])
        self.assertIn("EVIDENCE_POLICY_NOT_AUTHENTICATED", v["probe"]["reasons"])
        self.assertIsNone(v["accepted_evidence_count"])
        self.assertFalse(v["writer_authorized"])
        self.assertFalse(v["delp_invoked"])

    def test_21_foreign_provider_pr_base_repository_rejected(self):
        p = FakeProvider()
        p.pr_base_repository = "historic/v32-proto"
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_PR_BASE_REPOSITORY_MISMATCH", v.reasons)
        self.assertEqual(v.status, "HOLD_PROVIDER_READ")

    def test_22_provider_pr_base_id_changed_rejected(self):
        p = FakeProvider()
        p.pr_base_repo_id = 998877
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_PR_BASE_REPOSITORY_MISMATCH", v.reasons)

    def test_23_provider_pr_retarget_midcycle_rejected(self):
        p = FakeProvider()
        def retarget(kind, count, this):
            if kind == "pull" and count == 7:
                this.pr_base_ref = "release"
        p.call_mutator = retarget
        v = inspect_v32_read_only(target(), p)
        self.assertIn("PROVIDER_PR_MOVED_IN_CYCLE", v.reasons)
        self.assertEqual(v.pass_count, 0)

    def test_24_missing_provider_pr_base_identity_rejected(self):
        p = FakeProvider()
        p.pr_base_repository = None
        v = inspect_v32_read_only(target(), p)
        self.assertEqual(v.status, "HOLD_PROVIDER_READ")
        self.assertIn("PROVIDER_PR_BASE_REPOSITORY_MISMATCH", v.reasons)

    def test_25_provider_comment_claims_are_exposed_as_unattested(self):
        p = FakeProvider()
        p.comments = [{
            "id": 11, "user": {"login": "owner"}, "author_association": "OWNER",
            "body": (
                "```yaml\nCHECKPOINT_FACTS_V1:\n"
                "  responsibility: {issue: v32-proto#4}\n"
                "  material: {candidate_sha: '" + H1 + "'}\n"
                "  units:\n"
                "    - id: U01\n"
                "      state: COMPLETE\n"
                "      result: VERIFIED\n"
                "      evidence_refs: [v32-proto#4#issuecomment-11]\n"
                "```"
            ),
        }]
        row = inspect_v32_read_only(target(), p).as_dict()
        self.assertEqual(row["status"], "HOLD_NO_APPROVED_POSITIVE_ISSUER")
        self.assertEqual(row["comment_claims"]["native_structural_claims"], 1)
        self.assertEqual(row["comment_claims"]["complete_verified_unit_claims"], 1)
        self.assertEqual(row["comment_claims"]["status"], "HOLD_UNATTESTED_COMMENT_CLAIMS")
        self.assertIsNone(row["accepted_evidence_count"])
        self.assertFalse(row["delp_invoked"])

    def test_26_missing_provider_checkpoint_comments_are_not_evidence(self):
        p = FakeProvider()
        row = inspect_v32_read_only(target(), p).as_dict()
        self.assertEqual(row["comment_claims"]["status"], "HOLD_NO_COMMENT_CLAIMS")
        self.assertEqual(row["comment_claims"]["blocks_seen"], 0)
        self.assertIsNone(row["accepted_evidence_count"])

    def test_27_bad_provider_comment_yaml_never_returns_empty_success(self):
        p = FakeProvider()
        p.comments[0]["body"] = "```yaml\nCHECKPOINT_FACTS_V1:\n  broken: [\n```"
        row = inspect_v32_read_only(target(), p).as_dict()
        self.assertEqual(row["status"], "HOLD_PROVIDER_READ")
        self.assertIn("CLAIM_AUDIT_NATIVE_BLOCK_PARSE_FAILED", row["reasons"])
        self.assertIsNone(row["comment_claims"])

if __name__ == "__main__":
    unittest.main()
