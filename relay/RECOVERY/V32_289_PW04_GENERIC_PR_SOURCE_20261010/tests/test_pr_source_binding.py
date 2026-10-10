"""PW04 isolated, deterministic read-only source/PR binding falsifiers."""
from __future__ import annotations
import copy
from dataclasses import replace
from hashlib import sha1
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pr_source_binding import BindingError, PreviewPins, preview_source_binding

REPO = "author/example-lab"
SHA = "a" * 40
GRAPH = {"schema": "relay-v3.2-delp-execution-graph",
         "programme": {"repository": REPO, "root": "example-lab#1", "base_ref": "main"},
         "nodes": [
             {"ref": "example-lab#1", "kind": "ROOT"},
             {"ref": "example-lab#2", "kind": "LEAF", "parent": "example-lab#1",
              "weight": 1, "primary_pr": "example-lab#10",
              "units": [{"id": "U01", "weight": 100}]},
         ]}


def raw(graph):
    return json.dumps(graph, sort_keys=True).encode()


def oid(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class PW04BindingTests(unittest.TestCase):
    def setUp(self):
        self.graph = copy.deepcopy(GRAPH)
        self.repo = {"id": 42, "full_name": REPO}
        self.pr = {"number": 10, "state": "closed", "merged": True,
                   "merged_at": "2026-10-09T10:00:00Z",
                   "head": {"sha": SHA, "repo": copy.deepcopy(self.repo)},
                   "base": {"ref": "main", "repo": copy.deepcopy(self.repo)}}
        self.calls = []

    def check(self, *, native=None, pins=None, data=None):
        data = raw(self.graph) if data is None else data
        pins = pins or PreviewPins(REPO, 42, oid(data), "example-lab#2", SHA)
        def stub(graph, repository):
            self.calls.append(repository)
        return preview_source_binding(data, pins, self.repo, self.pr,
                                      native_validate=native or stub)

    def reject(self, reason, **kwargs):
        with self.assertRaisesRegex(BindingError, "^" + reason + "$"):
            self.check(**kwargs)

    def test_01_coherent_graph_provider_never_authorizes(self):
        result = self.check()
        self.assertEqual(result["status"], "SOURCE_BOUND_PREVIEW_NON_ADMITTING")
        self.assertFalse(result["publication_authorized"])
        self.assertFalse(result["owner_source_authenticated"])
        self.assertFalse(result["evidence_admitted"])
        self.assertFalse(result["native_projector_executed"])
        self.assertEqual(result["primary_pr_number"], 10)
        self.assertEqual(len(self.calls), 1)

    def test_02_true_blob_oid_pin_matters(self):
        self.reject("GRAPH_BLOB_PIN_MISMATCH", pins=PreviewPins(REPO,42,"f"*40,"example-lab#2",SHA))
        self.assertEqual(self.calls, [])

    def test_03_wrong_provider_repo_numeric_identity(self):
        self.repo["id"] = 43
        self.reject("PROVIDER_REPOSITORY_IDENTITY_MISMATCH")

    def test_04_wrong_provider_repo_name(self):
        self.repo["full_name"] = "attacker/example-lab"
        self.reject("PROVIDER_REPOSITORY_IDENTITY_MISMATCH")

    def test_05_wrong_pr_number(self):
        self.pr["number"] = 11
        self.reject("PROVIDER_PR_IDENTITY_MISMATCH")

    def test_06_wrong_pr_base_branch(self):
        self.pr["base"]["ref"] = "release/evil"
        self.reject("PROVIDER_PR_WRONG_BASE")

    def test_07_wrong_head_repo(self):
        self.pr["head"]["repo"]["full_name"] = "attacker/example-lab"
        self.reject("PROVIDER_REPOSITORY_IDENTITY_MISMATCH")

    def test_08_wrong_base_repo(self):
        self.pr["base"]["repo"]["id"] = 99
        self.reject("PROVIDER_REPOSITORY_IDENTITY_MISMATCH")

    def test_09_moved_head_rejected(self):
        self.pr["head"]["sha"] = "b" * 40
        self.reject("PROVIDER_PR_HEAD_MOVED")

    def test_10_non_sha_head_rejected(self):
        self.pr["head"]["sha"] = "main"
        self.reject("PROVIDER_PR_HEAD_INVALID")

    def test_11_inconsistent_merged_state_rejected(self):
        self.pr["state"] = "open"
        self.reject("PROVIDER_PR_STATE_INVALID")

    def test_12_string_true_is_not_boolean(self):
        self.pr["merged"] = "true"
        self.reject("PROVIDER_PR_STATE_INVALID")

    def test_13_graph_foreign_repository_rejected(self):
        self.graph["programme"]["repository"] = "attacker/example-lab"
        self.reject("GRAPH_REPOSITORY_MISMATCH")
        self.assertEqual(self.calls, [])

    def test_14_foreign_pr_ref_rejected(self):
        self.graph["nodes"][1]["primary_pr"] = "attacker/example-lab#10"
        self.reject("GRAPH_FOREIGN_REFERENCE")

    def test_15_graph_leaf_must_exist(self):
        self.reject("GRAPH_LEAF_UNBOUND", pins=PreviewPins(REPO,42,oid(raw(self.graph)),"example-lab#99",SHA))

    def test_16_sane_nondefault_base_allowed_only_as_preview(self):
        self.graph["programme"]["base_ref"] = "release/2026"
        self.pr["base"]["ref"] = "release/2026"
        res = self.check()
        self.assertEqual(res["base_ref"], "release/2026")
        self.assertFalse(res["publication_authorized"])

    def test_17_traversal_base_rejected(self):
        self.graph["programme"]["base_ref"] = "../main"
        self.reject("GRAPH_BASE_REF_INVALID")

    def test_18_duplicate_json_field_rejected(self):
        duplicate = b'{"programme":{},"programme":{},"nodes":[]}'
        self.reject("GRAPH_DUPLICATE_JSON_KEY", data=duplicate)

    def test_19_native_graph_validator_failure_keeps_hold(self):
        def deny(_graph,_repo):
            raise BindingError("NATIVE_GRAPH_INVALID")
        self.reject("NATIVE_GRAPH_INVALID", native=deny)

    def test_20_native_falsy_source_not_called_on_unpinned_blob(self):
        self.reject("GRAPH_BLOB_PIN_MISMATCH", pins=PreviewPins(REPO,42,"0"*40,"example-lab#2",SHA))
        self.assertEqual(self.calls, [])

    def test_21_fingerprint_changed_on_candidate(self):
        a = self.check()
        self.pr["head"]["sha"] = "b"*40
        b = self.check(pins=PreviewPins(REPO,42,oid(raw(self.graph)),"example-lab#2","b"*40))
        self.assertNotEqual(a["binding_fingerprint"], b["binding_fingerprint"])

    def test_22_no_title_or_percentage_or_body_writes_in_result(self):
        result = self.check()
        for prohibited in ("progress", "E", "P", "title", "body", "writer", "plan_github"):
            self.assertNotIn(prohibited, result)

    def test_23_pin_not_an_authority_even_if_self_consistent(self):
        self.graph["nodes"][1]["units"][0]["weight"] = 99
        result = self.check()
        self.assertFalse(result["owner_source_authenticated"])
        self.assertFalse(result["publication_authorized"])

    def test_24_immutable_bytes_upper_bound(self):
        self.reject("GRAPH_BYTES_UNAVAILABLE", data=b" "*(5_000_001))

    @unittest.skipUnless((Path(__file__).resolve().parents[4] / "skills" /
                          "engineering-pr-delivery-v3.2" / "scripts" /
                          "delp_projection_v32.py").exists(), "native Common source not mounted")
    def test_25_real_frozen_native_validator_on_synthetic_graph(self):
        # Unlike other mock/negative tests, this actually loads the current
        # unchanged Common native V3.2 validator from the checkout.
        result = preview_source_binding(raw(self.graph),
            PreviewPins(REPO,42,oid(raw(self.graph)),"example-lab#2",SHA),
            self.repo,self.pr)
        self.assertEqual(result["status"], "SOURCE_BOUND_PREVIEW_NON_ADMITTING")


if __name__ == "__main__":
    unittest.main()
