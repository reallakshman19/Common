"""B1 lab intake regression: fake provider cases, never real Owner admission."""
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from v32_lab_intake import LabTarget, inspect_lab_read_only

REPO = "owner/v32-lab"
BASE1, BASE2 = "a" * 40, "b" * 40
GRAPH = {
    "schema": "relay-v3.2-delp-execution-graph",
    "programme": {"repository": REPO, "root": "v32-lab#1", "base_ref": "main"},
    "nodes": [
        {"ref": "v32-lab#1", "kind": "ROOT"},
        {"ref": "v32-lab#2", "kind": "LEAF", "parent": "v32-lab#1",
         "weight": 1, "primary_pr": "v32-lab#10",
         "units": [{"id": "U01", "weight": 100}]},
    ],
}

def raw(graph):
    return json.dumps(graph, sort_keys=True).encode()

class Provider:
    def __init__(self):
        self.calls = []
        self.repo = REPO
        self.repo_id = 42
        self.default_branch = "main"
        self.base_sha = BASE1
        self.graph = deepcopy(GRAPH)
        self.mutate = None
        self.title = "Human title"
        self.unavailable = False
        self.pr_number = 10
        self.pr_head_sha = BASE1
        self.pr_head_repo = REPO
        self.pr_head_repo_id = 42
        self.pr_base_repo = REPO
        self.pr_base_repo_id = 42
        self.pr_state = "closed"
        self.pr_merged = True
        self.pr_merged_at = "2026-10-09T10:00:00Z"

    def _call(self, op):
        self.calls.append(op)
        if self.mutate:
            self.mutate(op, len(self.calls), self)
        if self.unavailable:
            raise OSError("private secret 404")

    def get_repository(self, repository):
        self._call("repo")
        return {"full_name": self.repo, "id": self.repo_id,
                "default_branch": self.default_branch}

    def get_commit(self, repository, ref):
        self._call("commit")
        return {"sha": self.base_sha}

    def get_file_bytes(self, repository, path, ref):
        self._call("graph")
        return raw(self.graph)

    def get_issue(self, repository, number):
        self._call("issue")
        return {"number": number, "title": self.title, "body": "Human body"}

    def get_pull(self, repository, number):
        self._call("pull")
        return {
            "number": self.pr_number, "state": self.pr_state,
            "merged": self.pr_merged, "merged_at": self.pr_merged_at,
            "head": {"sha": self.pr_head_sha,
                     "repo": {"full_name": self.pr_head_repo,
                              "id": self.pr_head_repo_id}},
            "base": {"ref": "main",
                     "repo": {"full_name": self.pr_base_repo,
                              "id": self.pr_base_repo_id}},
        }

def target(**kwargs):
    return replace(LabTarget(REPO, 42, "governance/released-graph.json",
                             "v32-lab#1"), **kwargs)

class LabIntakeTests(unittest.TestCase):
    def test_coherent_real_shaped_reads_never_grant_authority(self):
        p = Provider()
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_OWNER_RELEASE_UNVERIFIED")
        self.assertEqual(r.observations["issues_observed"], 2)
        self.assertEqual(len(p.calls), 14)
        self.assertEqual(r.observations["prs_observed"], 1)
        self.assertEqual(r.observations["merged_prs_observed"], 1)
        self.assertRegex(r.observations["pr_sources_digest"], r"^sha256:[0-9a-f]{64}$")
        d = r.as_dict()
        self.assertFalse(d["owner_release_authenticated"])
        self.assertFalse(d["positive_fact_issuer"])
        self.assertIsNone(d["accepted_evidence_count"])
        self.assertFalse(d["writer_authorized"])
        self.assertFalse(d["delp_invoked"])

    def test_wrong_repo_identity_holds(self):
        p = Provider(); p.repo_id = 43
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_REPOSITORY_IDENTITY_MISMATCH", r.reasons)
        self.assertIsNone(r.observations)

    def test_old_released_graph_is_not_current_repo_graph(self):
        p = Provider(); p.graph["programme"]["repository"] = "historical/v32-lab"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_GRAPH_FOREIGN_REPOSITORY", r.reasons)

    def test_wrong_root_ref_holds(self):
        p = Provider(); p.graph["programme"]["root"] = "v32-lab#99"
        self.assertIn("LAB_GRAPH_ROOT_MISMATCH", inspect_lab_read_only(
            target(), p, native_validate=lambda g, repo: None).reasons)

    def test_pinned_graph_digest_mismatch_holds(self):
        p = Provider()
        r = inspect_lab_read_only(target(expected_graph_digest="sha256:" + "0" * 64),
                                  p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_GRAPH_DIGEST_MISMATCH", r.reasons)

    def test_correct_hash_never_mints_owner_approval(self):
        p = Provider()
        pin = "sha256:" + sha256(raw(GRAPH)).hexdigest()
        r = inspect_lab_read_only(target(expected_graph_digest=pin),p,
                                  native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_OWNER_RELEASE_UNVERIFIED")

    def test_provider_404_sanitized_and_no_green(self):
        p = Provider(); p.unavailable = True
        r = inspect_lab_read_only(target(),p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_LAB_SOURCE")
        self.assertEqual(r.reasons, ("LAB_SOURCE_GET_UNAVAILABLE",))
        self.assertNotIn("private", str(r.as_dict()))

    def test_no_provider_call_on_malformed_selector(self):
        for bad in (target(repository="../v32-lab"),
                    target(graph_path="../private.json"),
                    target(root_ref="another-repo#1"),
                    target(repository_id=0),
                    target(expected_graph_digest="sha256:evil")):
            p = Provider()
            r = inspect_lab_read_only(bad,p)
            self.assertEqual(r.status, "FAILED_TARGET")
            self.assertEqual(p.calls, [])

    def test_midcycle_default_branch_move_blocks(self):
        p = Provider()
        def move(op, count, x):
            if op == "issue" and count == 5:
                x.base_sha = BASE2
        p.mutate = move
        r = inspect_lab_read_only(target(),p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_DEFAULT_BRANCH_MOVED_DURING_READ", r.reasons)

    def test_source_move_between_rounds_holds(self):
        p = Provider()
        def move(op, count, x):
            if op == "repo" and count == 8:
                x.base_sha = BASE2
        p.mutate = move
        r = inspect_lab_read_only(target(),p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_LAB_DRIFT")
        self.assertIsNone(r.observations)

    def test_issue_title_move_between_rounds_holds(self):
        p = Provider()
        def move(op, count, x):
            if op == "repo" and count == 8:
                x.title = "New human title"
        p.mutate = move
        r = inspect_lab_read_only(target(),p,native_validate=lambda g, repo: None)
        self.assertEqual(r.status,"HOLD_LAB_DRIFT")

    def test_malformed_node_binding_holds(self):
        p = Provider(); p.graph["nodes"][1]["ref"] = "foreign#2"
        r = inspect_lab_read_only(target(),p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_GRAPH_ISSUE_REF_INVALID",r.reasons)

    def test_native_validator_invoked_and_errors_halt(self):
        p = Provider()
        witnessed = []
        def reject(graph, repo):
            witnessed.append(repo)
            raise ValueError("NATIVE_V32_GRAPH_INVALID")
        r = inspect_lab_read_only(target(),p, native_validate=reject)
        self.assertEqual(witnessed,[REPO])
        self.assertEqual(r.status,"HOLD_LAB_SOURCE")
        self.assertEqual(r.reasons,("NATIVE_V32_GRAPH_INVALID",))

    @unittest.skipUnless((Path(__file__).resolve().parents[4] / "skills" /
                          "engineering-pr-delivery-v3.2" / "scripts" /
                          "delp_projection_v32.py").exists(), "native checkout unavailable")
    def test_actual_native_graph_validator_runs_in_checkout(self):
        p = Provider()
        r = inspect_lab_read_only(target(),p)
        self.assertEqual(r.status,"HOLD_OWNER_RELEASE_UNVERIFIED")

    def test_linked_pr_wrong_number_holds(self):
        p = Provider(); p.pr_number = 11
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_IDENTITY_MISMATCH", r.reasons)

    def test_linked_pr_wrong_head_repo_holds(self):
        p = Provider(); p.pr_head_repo = "foreign/v32-lab"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_REPOSITORY_MISMATCH", r.reasons)

    def test_linked_pr_wrong_head_repo_id_holds(self):
        p = Provider(); p.pr_head_repo_id = 99
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_REPOSITORY_MISMATCH", r.reasons)

    def test_linked_pr_wrong_base_repo_holds(self):
        p = Provider(); p.pr_base_repo = "foreign/v32-lab"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_REPOSITORY_MISMATCH", r.reasons)

    def test_linked_pr_bad_head_sha_holds(self):
        p = Provider(); p.pr_head_sha = "current-branch"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_HEAD_UNPINNED", r.reasons)

    def test_linked_pr_merged_claim_type_must_be_boolean(self):
        p = Provider(); p.pr_merged = "true"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_STATE_INVALID", r.reasons)

    def test_linked_pr_head_move_between_reads_holds(self):
        p = Provider()
        def change(op, count, x):
            if op == "repo" and count == 8:
                x.pr_head_sha = BASE2
        p.mutate = change
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_LAB_DRIFT")
        self.assertIsNone(r.observations)

    def test_linked_pr_state_move_between_reads_holds(self):
        p = Provider()
        def change(op, count, x):
            if op == "repo" and count == 8:
                x.pr_merged = False
                x.pr_merged_at = None
                x.pr_state = "open"
        p.mutate = change
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_LAB_DRIFT")

    def test_graph_primary_pr_foreign_ref_fails_before_pr_get(self):
        p = Provider(); p.graph["nodes"][1]["primary_pr"] = "foreign/lab#10"
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_PRIMARY_PR_BINDING_INVALID", r.reasons)
        self.assertNotIn("pull", p.calls)

    def test_linked_pr_closed_without_merge_still_not_admitted(self):
        p = Provider(); p.pr_merged = False; p.pr_merged_at = None
        r = inspect_lab_read_only(target(), p, native_validate=lambda g, repo: None)
        self.assertEqual(r.status, "HOLD_OWNER_RELEASE_UNVERIFIED")
        self.assertEqual(r.observations["merged_prs_observed"], 0)
        self.assertFalse(r.as_dict()["positive_fact_issuer"])

    def test_unbounded_issue_graph_rejected(self):
        p=Provider()
        for number in range(3,28):
            p.graph["nodes"].append({"ref":f"v32-lab#{number}", "kind":"LEAF"})
        r=inspect_lab_read_only(target(),p, native_validate=lambda g, repo: None)
        self.assertIn("LAB_GRAPH_NODES_UNMATERIALIZED_OR_UNBOUNDED",r.reasons)

if __name__ == "__main__":
    unittest.main()
