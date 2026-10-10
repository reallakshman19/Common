"""STEP-01 native provider witness: no authored status or guessed authority."""
from __future__ import annotations

import copy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import integration_prototype_witness_v35 as W

REPO = "reallakshman19/Common"
SHA = "a" * 40
OTHER = "b" * 40


class Provider:
    repository = REPO

    def __init__(self):
        self.root = {"number": 5, "html_url": f"https://github.com/{REPO}/issues/5", "state": "open",
                     "body": "<!-- V35_PARENT_OWNER_INTENT_BEGIN --> Original Owner mirror"}
        self.leaf = {"number": 30, "html_url": f"https://github.com/{REPO}/issues/30", "state": "open",
                     "body": "**Parent programme:** #5"}
        self.pr = {"number": 292, "html_url": f"https://github.com/{REPO}/pull/292",
                   "state": "open", "head": {"sha": SHA, "repo": {"full_name": REPO}},
                   "base": {"repo": {"full_name": REPO}},
                   "body": "Implements read-only #30; parent #5"}
        self.comments = []
        self.calls = []
        self.after_pr = None
        self.after_root = None
        self.after_comments = None
        self.fail_comments = False

    def get_issue(self, n):
        self.calls.append(("GET_ISSUE", n))
        if n == 5 and self.after_root is not None and sum(x == ("GET_ISSUE", 5) for x in self.calls) >= 2:
            return copy.deepcopy(self.after_root)
        return copy.deepcopy(self.root if n == 5 else self.leaf)

    def get_pull(self, n):
        self.calls.append(("GET_PR", n))
        if len([x for x in self.calls if x[0] == "GET_PR"]) >= 2 and self.after_pr is not None:
            return copy.deepcopy(self.after_pr)
        return copy.deepcopy(self.pr)

    def get_commit_sha(self, sha):
        self.calls.append(("GET_COMMIT", sha))
        return sha

    def list_comments(self, n):
        self.calls.append(("GET_COMMENTS", n))
        if self.fail_comments:
            raise RuntimeError("provider forbidden")
        if self.after_comments is not None and sum(x[0] == "GET_COMMENTS" for x in self.calls) >= 2:
            return copy.deepcopy(self.after_comments)
        return copy.deepcopy(self.comments)


def call(t):
    return W.observe(t, root_issue=5, leaf_issue=30, pr_number=292,
                     expected_head=SHA)


class WitnessTests(unittest.TestCase):
    def test_native_negative_no_graph_is_not_a_fictional_positive(self):
        t = Provider()
        r = call(t)
        self.assertEqual("HOLD_NO_PROVIDER_APPROVED_GRAPH", r["status"])
        self.assertEqual("SOURCE_HEAD_DOUBLE_READ_MATCH", r["provider_material"])
        self.assertEqual("CONSISTENT_UNTRUSTED_PROSE", r["route_hints"])
        self.assertEqual(SHA, r["observed_head"])
        self.assertEqual("UNKNOWN", r["effective_required_checks"])
        self.assertEqual("NOT_DERIVED", r["positive_evidence_admission"])
        self.assertEqual("NOT_CALCULATED", r["delp_progress"])
        self.assertFalse(r["prototype_qualified"])
        self.assertEqual("NONE", r["github_writes"])
        self.assertEqual(2, sum(x[0] == "GET_PR" for x in t.calls))
        self.assertEqual(2, sum(x[0] == "GET_COMMENTS" for x in t.calls))

    def test_route_hints_reject_unrelated_or_conflicting_same_repo_sources(self):
        cases = (
            ("wrong_parent", lambda t: t.leaf.update(body="**Parent programme:** #9")),
            ("ambiguous_parent", lambda t: t.leaf.update(
                body="**Parent programme:** #5\nParent programme: #9")),
            ("unrelated_pr", lambda t: t.pr.update(body="Implements #31 not this leaf")),
            ("missing_child_route", lambda t: t.leaf.update(body="No explicit parent")),
            ("missing_pr_route", lambda t: t.pr.update(body="No explicit leaf")),
            ("wrong_number_prefix", lambda t: t.pr.update(body="Mentions #300 only")),
        )
        for name, mutate in cases:
            with self.subTest(case=name):
                t = Provider()
                mutate(t)
                result = call(t)
                self.assertEqual("HOLD_SOURCE_LINKAGE_UNVERIFIED", result["status"])
                self.assertEqual("UNVERIFIED", result["route_hints"])
                self.assertFalse(result["prototype_qualified"])
                self.assertFalse(any(x[0] == "GET_COMMENTS" for x in t.calls))

    def test_consistent_route_prose_does_not_establish_ownership_or_evidence(self):
        t = Provider()
        result = call(t)
        self.assertEqual("CONSISTENT_UNTRUSTED_PROSE", result["route_hints"])
        self.assertEqual("HOLD_NO_PROVIDER_APPROVED_GRAPH", result["status"])
        self.assertEqual("NOT_DERIVED", result["positive_evidence_admission"])
        self.assertEqual("NOT_GRANTED_BY_WITNESS", result["local_writer"])
        self.assertEqual("NOT_CALCULATED", result["delp_progress"])

    def test_missing_governed_root_marker_fails_before_graph_claim(self):
        t = Provider()
        t.root["body"] = "manually maintained owner text"
        r = call(t)
        self.assertEqual("HOLD_ROOT_NOT_GOVERNED", r["status"])
        self.assertEqual("ROOT_CONTRACT_MISSING", r["graph"])
        self.assertEqual(SHA, r["observed_head"])
        self.assertEqual("SOURCE_HEAD_DOUBLE_READ_MATCH", r["provider_material"])
        self.assertEqual(2, sum(x[0] == "GET_PR" for x in t.calls))
        self.assertFalse(any(x[0] == "GET_COMMENTS" for x in t.calls))

    def test_root_changed_during_readback_is_not_stable(self):
        t = Provider()
        t.after_root = copy.deepcopy(t.root)
        t.after_root["body"] += "\nRevised while reading"
        self.assertEqual("HOLD_ISSUE_MOVED_DURING_OBSERVATION", call(t)["status"])

    def test_graph_approval_added_or_revoked_mid_observation(self):
        t = Provider()
        t.after_comments = [{"id": 13, "body": W.GRAPH_MARKER}]
        self.assertEqual("HOLD_COMMENTS_MOVED_DURING_OBSERVATION", call(t)["status"])
        t = Provider()
        t.comments = [{"id": 13, "body": W.GRAPH_MARKER}]
        t.after_comments = []
        module = types.ModuleType("integration_cold_entry_v35")
        module.reconstruct = lambda *_: {
            "status": "GOVERNED_GRAPH_PROVIDER_OBSERVED_READ_ONLY",
            "selected_leaf": "Common#30", "approved_pr": 292, "exact_head": SHA,
        }
        with patch.dict(sys.modules, {"integration_cold_entry_v35": module}):
            self.assertEqual("HOLD_COMMENTS_MOVED_DURING_OBSERVATION", call(t)["status"])

    def test_pr_body_changed_during_readback_refused(self):
        t = Provider()
        t.after_pr = copy.deepcopy(t.pr)
        t.after_pr["body"] = "New semantic claims"
        self.assertEqual("HOLD_PR_MOVED_DURING_OBSERVATION", call(t)["status"])

    def test_cli_uses_graph_capable_transport_without_writing(self):
        fake = Provider()
        seen = []
        module = types.ModuleType("integration_scoreboard_publish_v35")
        module.ScoreboardTransport = lambda repo: (seen.append(repo) or fake)
        argv = [
            "witness", "--repository", REPO, "--root", "5", "--leaf", "30",
            "--pr", "292", "--expected-head", SHA,
        ]
        with patch.dict(sys.modules, {"integration_scoreboard_publish_v35": module}), patch.object(sys, "argv", argv):
            self.assertEqual(3, W.main())
        self.assertEqual([REPO], seen)
        self.assertTrue(all(x[0].startswith("GET_") for x in fake.calls))

    def test_stale_expected_head_exits_before_approval(self):
        t = Provider()
        result = W.observe(t, root_issue=5, leaf_issue=30, pr_number=292,
                           expected_head=OTHER)
        self.assertEqual("HOLD_EXPECTED_HEAD_MOVED", result["status"])
        self.assertFalse(any(x[0] == "GET_COMMENTS" for x in t.calls))

    def test_pr_moves_between_reads_even_if_first_material_valid(self):
        t = Provider()
        t.after_pr = copy.deepcopy(t.pr)
        t.after_pr["head"]["sha"] = OTHER
        self.assertEqual("HOLD_PR_MOVED_DURING_OBSERVATION", call(t)["status"])

    def test_foreign_or_malformed_provider_identity_refused(self):
        t = Provider()
        t.pr["base"]["repo"]["full_name"] = "reallaksh19/Common"
        self.assertEqual("HOLD_PR_IDENTITY_UNVERIFIED", call(t)["status"])
        t = Provider()
        t.root["html_url"] = "https://github.com/reallaksh19/Common/issues/5"
        self.assertEqual("HOLD_ISSUE_IDENTITY_UNVERIFIED", call(t)["status"])

    def test_missing_or_closed_source_never_admitted(self):
        t = Provider()
        t.pr["state"] = "closed"
        self.assertEqual("HOLD_SOURCE_LIFECYCLE_CHANGED", call(t)["status"])
        t = Provider()
        t.get_commit_sha = lambda _: OTHER
        self.assertEqual("HOLD_COMMIT_NOT_RESOLVED", call(t)["status"])

    def test_transport_unknown_is_not_no_approval(self):
        t = Provider()
        t.fail_comments = True
        r = call(t)
        self.assertEqual("HOLD_PROVIDER_READ_UNKNOWN", r["status"])
        self.assertEqual("UNKNOWN", r["graph"])

    def test_duplicate_typed_approval_denied(self):
        t = Provider()
        t.comments = [{"body": W.GRAPH_MARKER}] * 2
        self.assertEqual("HOLD_AMBIGUOUS_GRAPH_SELECTION", call(t)["status"])

    def test_existing_cold_entry_is_only_graph_authority(self):
        t = Provider()
        t.comments = [{"body": W.GRAPH_MARKER}]
        module = types.ModuleType("integration_cold_entry_v35")
        module.reconstruct = lambda *_: {
            "status": "GOVERNED_GRAPH_PROVIDER_OBSERVED_READ_ONLY",
            "selected_leaf": "Common#30", "approved_pr": 292, "exact_head": SHA,
        }
        with patch.dict(sys.modules, {"integration_cold_entry_v35": module}):
            result = call(t)
        self.assertEqual("HOLD_LOCAL_AND_ACCEPTANCE_NOT_PROVEN", result["status"])
        self.assertEqual("SOURCE_VALIDATED_READ_ONLY", result["graph"])
        self.assertFalse(result["prototype_qualified"])
        self.assertEqual("NOT_GRANTED_BY_WITNESS", result["local_writer"])

    def test_approved_graph_mismatched_binding_and_exception_refuse(self):
        t = Provider()
        t.comments = [{"body": W.GRAPH_MARKER}]
        module = types.ModuleType("integration_cold_entry_v35")
        module.reconstruct = lambda *_: {
            "status": "GOVERNED_GRAPH_PROVIDER_OBSERVED_READ_ONLY",
            "selected_leaf": "Common#31", "approved_pr": 292, "exact_head": SHA,
        }
        with patch.dict(sys.modules, {"integration_cold_entry_v35": module}):
            self.assertEqual("HOLD_SELECTED_GRAPH_SCOPE_MISMATCH", call(t)["status"])
        module.reconstruct = lambda *_: (_ for _ in ()).throw(ValueError("bad graph"))
        with patch.dict(sys.modules, {"integration_cold_entry_v35": module}):
            self.assertEqual("HOLD_GRAPH_VALIDATION_UNVERIFIED", call(t)["status"])

    def test_provider_faults_expose_only_bounded_failure_stage(self):
        for step, method, fail_on_call in (
            ("ROOT_GET", "get_issue", 1),
            ("LEAF_GET", "get_issue", 2),
            ("PR_INITIAL_GET", "get_pull", 1),
            ("COMMIT_RESOLVE", "get_commit_sha", 1),
            ("APPROVAL_COMMENTS_GET", "list_comments", 1),
            ("ROOT_READBACK", "get_issue", 3),
            ("LEAF_READBACK", "get_issue", 4),
            ("APPROVAL_COMMENTS_READBACK", "list_comments", 2),
            ("PR_READBACK", "get_pull", 2),
        ):
            with self.subTest(stage=step):
                t = Provider()
                orig = getattr(t, method)
                calls = [0]
                def failing(*args):
                    calls[0] += 1
                    if calls[0] == fail_on_call:
                        raise RuntimeError("SECRET_DO_NOT_EXPOSE_TO_CONSUMER")
                    return orig(*args)
                setattr(t, method, failing)
                observed = call(t)
                self.assertEqual("HOLD_PROVIDER_READ_UNKNOWN", observed["status"])
                self.assertEqual(step, observed["failure_stage"])
                self.assertEqual("UNKNOWN", observed["graph"])
                self.assertEqual("UNKNOWN", observed["provider_material"])
                self.assertNotIn("SECRET_DO_NOT_EXPOSE_TO_CONSUMER", str(observed))
                self.assertFalse(observed["prototype_qualified"])

    def test_graph_validation_exception_has_specific_stage_not_source_success(self):
        t = Provider()
        t.comments = [{"id": 123, "body": W.GRAPH_MARKER}]
        module = types.ModuleType("integration_cold_entry_v35")
        module.reconstruct = lambda *_: (_ for _ in ()).throw(RuntimeError("SECRET"))
        with patch.dict(sys.modules, {"integration_cold_entry_v35": module}):
            observed = call(t)
        self.assertEqual("HOLD_GRAPH_VALIDATION_UNVERIFIED", observed["status"])
        self.assertEqual("GRAPH_VALIDATION", observed["failure_stage"])
        self.assertEqual("SOURCE_HEAD_DOUBLE_READ_MATCH", observed["provider_material"])
        self.assertNotIn("SECRET", str(observed))

    def test_invalid_inputs_produce_zero_provider_reads(self):
        t = Provider()
        for kwargs in ({"root_issue": 30, "leaf_issue": 30, "pr_number": 292, "expected_head": SHA},
                       {"root_issue": 5, "leaf_issue": 30, "pr_number": 292, "expected_head": "bad"},
                       {"root_issue": True, "leaf_issue": 30, "pr_number": 292, "expected_head": SHA}):
            with self.assertRaises(W.WitnessInputError):
                W.observe(t, **kwargs)
        self.assertEqual([], t.calls)


if __name__ == "__main__":
    unittest.main()
