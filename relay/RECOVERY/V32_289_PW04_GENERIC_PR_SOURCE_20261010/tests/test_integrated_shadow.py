"""Full V3.2 lifecycle verification using the UNCHANGED native projector.

Synthetic provider material only; never accepts or publishes a production fact.
"""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha1
import os
import stat
import json
from pathlib import Path
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pr_source_binding import BindingError, PreviewPins
import v32_integrated_shadow as shadow_module
from v32_integrated_shadow import CycleHold, SnapshotGET, integrated_shadow, _native_modules, main as shadow_main

REPO = "author/example-lab"
HEAD = "a" * 40
BASE = "b" * 40
GRAPH = {
    "schema": "relay-v3.2-delp-execution-graph",
    "programme": {
        "repository": REPO, "root": "example-lab#1", "base_ref": "main"
    },
    "nodes": [
        {"ref": "example-lab#1", "kind": "ROOT"},
        {"ref": "example-lab#2", "kind": "LEAF", "parent": "example-lab#1",
         "weight": 1, "primary_pr": "example-lab#10",
         "units": [{"id": "U01", "weight": 100}]},
    ],
}


def raw(graph):
    return json.dumps(graph, sort_keys=True).encode()


def oid(data):
    return sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def make():
    graph = deepcopy(GRAPH)
    binary = raw(graph)
    node_repo = {"full_name": REPO, "id": 42}
    pull = {
        "number": 10, "title": "Original human PR title",
        "body": "Original human PR body.\n\nHuman acceptance is not granted.",
        "head": {"sha": HEAD, "repo": deepcopy(node_repo)},
        "base": {"sha": BASE, "ref": "main", "repo": deepcopy(node_repo)},
        "state": "closed", "merged": True,
        "merged_at": "2026-10-09T11:00:00Z",
    }
    source = {
        "source_kind": "GITHUB_GET_ONLY_UNATTESTED",
        "repository": REPO, "repository_id": 42,
        "graph_git_blob": oid(binary),
        "base_ref": "main", "main_sha": BASE, "final_main_sha": BASE,
        "issues": {"1": {"title": "Original root human title"},
                   "2": {"title": "Original leaf human title"}},
        "pulls": {"10": pull},
        "comments": {"2": []},
    }
    pin = PreviewPins(REPO, 42, oid(binary), "example-lab#2", HEAD)
    return binary, pin, source


@unittest.skipUnless((Path(__file__).resolve().parents[4] / "skills" /
                      "engineering-pr-delivery-v3.2" / "scripts" /
                      "delp_projection_v32.py").is_file(), "requires real Common native V3.2 checkout")
class IntegratedFullLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.binary, self.pin, self.source = make()

    def cycle(self):
        return integrated_shadow(self.binary, self.pin, self.source)

    def test_01_one_complete_native_delp_to_issue_pr_c6_cycle(self):
        r = self.cycle()
        self.assertEqual(r["status"], "INTEGRATED_SHADOW_ONLY_NOT_RELEASE_READY")
        self.assertTrue(r["native_input_digest"].startswith("sha256:"))
        self.assertEqual(r["binding"]["primary_pr_number"], 10)
        self.assertEqual(r["native_core"]["digests"]["input"], r["native_input_digest"])
        self.assertEqual(r["c6_frontier"]["observed"]["candidate_sha"], HEAD)
        self.assertEqual(r["c6_same_source_reentry"]["status"], "CURRENT")
        self.assertEqual(len(r["native_expected_issue_titles"]), 2)
        self.assertIn("Original human PR body.", r["pr_body_preview"])
        self.assertIn("relay-v32:pr-read-view:start", r["pr_body_preview"])
        self.assertTrue(r["pr_body_changed_in_preview"])
        self.assertEqual(len(r["in_memory_issue_first_pass"]), 2)
        self.assertTrue(all(x["status"] == "WRITTEN" for x in r["in_memory_issue_first_pass"].values()))
        self.assertTrue(all(x["status"] == "UNCHANGED" for x in r["in_memory_issue_second_pass"].values()))
        self.assertFalse(r["issue_or_pr_github_writes"])
        self.assertFalse(r["production_activation"])
        self.assertFalse(r["owner_source_authenticated"])
        self.assertFalse(r["eligible_evidence_admitted_by_this_cycle"])
        self.assertEqual(r["real_cold_successor"], "NOT_EXECUTED")

    def test_02_real_native_material_without_facts_not_credited(self):
        r = self.cycle()
        self.assertEqual(r["native_rejected_facts"], [])
        self.assertEqual(r["native_core"]["progress"]["leaf"]["E"], 0)
        self.assertIn(r["native_core"]["leaf_state"], ("UNMATERIALIZED", "EVIDENCE_GAP"))

    def test_03_pr_head_move_refuses(self):
        self.source["pulls"]["10"]["head"]["sha"] = "c" * 40
        with self.assertRaisesRegex(BindingError, "PROVIDER_PR_HEAD_MOVED"):
            self.cycle()

    def test_04_wrong_pr_base_ref_refuses(self):
        self.source["pulls"]["10"]["base"]["ref"] = "other"
        with self.assertRaisesRegex(BindingError, "PROVIDER_PR_WRONG_BASE"):
            self.cycle()

    def test_05_forged_graph_pin_refuses(self):
        self.source["graph_git_blob"] = "f" * 40
        with self.assertRaisesRegex(CycleHold, "SOURCE_GRAPH_BLOB_MISMATCH"):
            self.cycle()

    def test_06_fake_repo_identity_refuses(self):
        self.source["repository_id"] = 999
        with self.assertRaisesRegex(CycleHold, "SOURCE_NUMERIC_REPOSITORY_MISMATCH"):
            self.cycle()

    def test_07_default_branch_move_refuses(self):
        self.source["final_main_sha"] = "f" * 40
        with self.assertRaisesRegex(CycleHold, "SOURCE_DEFAULT_BRANCH_MOVED"):
            self.cycle()

    def test_08_missing_private_issue_refuses(self):
        del self.source["issues"]["2"]
        with self.assertRaisesRegex(CycleHold, "SOURCE_ISSUE_MISSING"):
            self.cycle()

    def test_09_missing_private_comment_feed_refuses(self):
        del self.source["comments"]["2"]
        with self.assertRaisesRegex(CycleHold, "SOURCE_COMMENTS_MISSING"):
            self.cycle()

    def test_10_duplicate_managed_pr_markers_refuse(self):
        self.source["pulls"]["10"]["body"] = (
            "<!-- relay-v32:pr-read-view:start -->" * 2 + "Human text")
        with self.assertRaisesRegex(Exception, "DUPLICATE_MANAGED_MARKER"):
            self.cycle()

    def test_11_snapshot_has_no_mutating_transport_methods(self):
        t = SnapshotGET(self.source)
        for name in ("post_comment", "patch_comment", "patch_title",
                     "patch_issue_body", "patch_pull_title_body", "write", "apply"):
            self.assertFalse(hasattr(t, name), name)

    def test_12_original_graph_has_not_been_reduced_by_shadow(self):
        before = deepcopy(self.source)
        a = self.cycle()
        b = self.cycle()
        self.assertEqual(self.source, before)
        self.assertEqual(a["native_input_digest"], b["native_input_digest"])
        self.assertEqual(a["c6_frontier"]["frontier_digest"], b["c6_frontier"]["frontier_digest"])
        self.assertEqual(a["pr_body_preview"], b["pr_body_preview"])

    def test_13_bad_source_capture_kind_rejected(self):
        self.source["source_kind"] = "SIGNED_AND_APPROVED"
        with self.assertRaisesRegex(CycleHold, "SOURCE_CAPTURE_KIND_UNTRUSTED"):
            self.cycle()

    def test_14_malformed_original_pr_body_rejected(self):
        self.source["pulls"]["10"]["body"] = None
        with self.assertRaisesRegex(CycleHold, "PR_HUMAN_BODY_NOT_OBSERVED"):
            self.cycle()

    def test_16_native_c6_detects_changed_candidate_after_handover(self):
        r = self.cycle()
        native, _ = _native_modules()
        moved = deepcopy(r["c6_frontier"])
        moved["observed"]["candidate_sha"] = "f" * 40
        verdict = native.frontier_drift(r["c6_frontier"], moved)
        self.assertEqual(verdict["status"], "MOVED")
        self.assertEqual(verdict["action"], "RECONCILE")
        self.assertFalse(r["issue_or_pr_github_writes"])

    def test_15_unchanged_native_frontier_depends_on_live_head(self):
        r = self.cycle()
        native, _ = _native_modules()
        graph = json.loads(self.binary)
        self.assertEqual(r["c6_frontier"]["schema"], native.frontier(
            graph, native.ledger_from_github(SnapshotGET(self.source), graph),
            native.observe_github(SnapshotGET(self.source), graph), self.pin.leaf_ref)["schema"])


    def test_17_full_repository_pr_reference_is_explicit_core_hold(self):
        # Original lab graph uses owner/repo#PR throughout, not short repo#PR.
        # Real native graph and DELP accept this, but native responsibility core
        # currently holds. Never report a successful complete core or CLI OK.
        graph = json.loads(self.binary)
        graph["programme"]["root"] = f"{REPO}#1"
        for node in graph["nodes"]:
            node["ref"] = f"{REPO}#{node['ref'].rsplit('#', 1)[-1]}"
            if node.get("parent"):
                node["parent"] = f"{REPO}#{node['parent'].rsplit('#', 1)[-1]}"
            if node.get("primary_pr"):
                node["primary_pr"] = f"{REPO}#{node['primary_pr'].rsplit('#', 1)[-1]}"
        self.binary = raw(graph)
        self.source["graph_git_blob"] = oid(self.binary)
        self.pin = PreviewPins(REPO, 42, oid(self.binary), f"{REPO}#2", HEAD)
        report = self.cycle()
        self.assertIsNone(report["native_core"])
        self.assertEqual(report["native_core_hold"], "RESPONSIBILITY_CORE_MATERIAL_BOUNDARY")
        self.assertEqual(report["status"], "INTEGRATED_SHADOW_NATIVE_CORE_HOLD_NOT_RELEASE_READY")
        self.assertFalse(report["issue_or_pr_github_writes"])
        self.assertFalse(report["production_activation"])
        self.assertFalse(report["eligible_evidence_admitted_by_this_cycle"])
        self.assertEqual(report["real_cold_successor"], "NOT_EXECUTED")
        self.assertEqual(report["c6_same_source_reentry"]["status"], "CURRENT")

        # The private diagnostic is still written, but the CLI exits nonzero
        # and never prints a success marker while the native core is on HOLD.
        with TemporaryDirectory() as directory:
            graph_file = Path(directory) / "released-graph.json"
            snapshot_file = Path(directory) / "source-snapshot.json"
            output_file = Path(directory) / "report.json"
            graph_file.write_bytes(self.binary)
            snapshot_file.write_text(json.dumps(self.source), encoding="utf-8")
            argv = [
                "v32_integrated_shadow.py",
                "--graph", str(graph_file), "--snapshot", str(snapshot_file),
                "--repository-id", "42", "--leaf", self.pin.leaf_ref,
                "--graph-blob", self.pin.released_graph_blob_oid,
                "--head", HEAD, "--output", str(output_file),
            ]
            output = StringIO()
            with patch.object(sys, "argv", argv), redirect_stdout(output):
                return_code = shadow_main()
            self.assertEqual(return_code, 2)
            self.assertIn("NATIVE_CORE_HOLD", output.getvalue())
            self.assertNotIn("SHADOW_OK", output.getvalue())
            saved = json.loads(output_file.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], report["status"])
            self.assertEqual(saved["native_core_hold"], report["native_core_hold"])


    def test_18_duplicate_graph_keys_are_a_safe_hold(self):
        self.binary = self.binary.replace(
            b'"programme":', b'"programme":{"repository":"different/repo"},"programme":', 1)
        self.source["graph_git_blob"] = oid(self.binary)
        self.pin = PreviewPins(REPO, 42, oid(self.binary), "example-lab#2", HEAD)
        with self.assertRaisesRegex(CycleHold, "^GRAPH_DUPLICATE_JSON_KEY$"):
            self.cycle()

    def test_19_invalid_utf8_graph_is_a_safe_hold(self):
        self.binary += bytes([255])
        self.source["graph_git_blob"] = oid(self.binary)
        self.pin = PreviewPins(REPO, 42, oid(self.binary), "example-lab#2", HEAD)
        with self.assertRaisesRegex(CycleHold, "^GRAPH_JSON_INVALID$"):
            self.cycle()

    def test_20_absent_snapshot_collections_are_safe_holds(self):
        for name in ("issues", "pulls", "comments"):
            with self.subTest(collection=name):
                data = deepcopy(self.source)
                del data[name]
                with self.assertRaisesRegex(CycleHold, "^SOURCE_SNAPSHOT_SHAPE_INVALID$"):
                    integrated_shadow(self.binary, self.pin, data)

    def test_21_nonmapping_issues_are_safe_holds(self):
        self.source["issues"] = []
        with self.assertRaisesRegex(CycleHold, "^SOURCE_SNAPSHOT_SHAPE_INVALID$"):
            self.cycle()

    def test_22_missing_main_sha_is_a_safe_hold(self):
        del self.source["main_sha"]
        with self.assertRaisesRegex(CycleHold, "^SOURCE_SNAPSHOT_MAIN_SHA_INVALID$"):
            self.cycle()


    def test_23_managed_pr_second_replay_is_byte_identical(self):
        report = self.cycle()
        _, views = _native_modules()
        preview = report["pr_body_preview"]
        second = views.reconcile_managed_block(
            preview, report["pr_managed_block"],
            observed_digest=views.digest(preview), pr=True)
        self.assertEqual(preview, second)
        self.assertTrue(report["pr_view_second_pass_unchanged"])
        self.assertTrue(preview.startswith("Original human PR body."))
        self.assertIn("Human acceptance is not granted.", preview)

    @unittest.skipUnless(os.name == "posix", "POSIX file mode")
    def test_24_shadow_cli_private_output_0600(self):
        with TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            snapshot = Path(directory) / "snapshot.json"
            report = Path(directory) / "report.json"
            graph.write_bytes(self.binary)
            snapshot.write_text(json.dumps(self.source), encoding="utf-8")
            argv = ["v32_integrated_shadow.py", "--graph", str(graph),
                    "--snapshot", str(snapshot), "--repository-id", "42",
                    "--leaf", self.pin.leaf_ref, "--graph-blob",
                    self.pin.released_graph_blob_oid, "--head", HEAD,
                    "--output", str(report)]
            with patch.object(sys, "argv", argv), redirect_stdout(StringIO()):
                self.assertEqual(shadow_main(), 0)
            self.assertEqual(stat.S_IMODE(report.stat().st_mode), 0o600)

    def test_25_shadow_write_failure_removes_partial_file(self):
        with TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            snapshot = Path(directory) / "snapshot.json"
            report = Path(directory) / "report.json"
            graph.write_bytes(self.binary)
            snapshot.write_text(json.dumps(self.source), encoding="utf-8")
            argv = ["v32_integrated_shadow.py", "--graph", str(graph),
                    "--snapshot", str(snapshot), "--repository-id", "42",
                    "--leaf", self.pin.leaf_ref, "--graph-blob",
                    self.pin.released_graph_blob_oid, "--head", HEAD,
                    "--output", str(report)]
            def fail_dump(value, stream, **kwargs):
                stream.write("INCOMPLETE_RECORD")
                raise OSError("write failed")
            with patch.object(sys, "argv", argv), patch.object(
                    shadow_module.json, "dump", side_effect=fail_dump):
                with self.assertRaises(OSError):
                    shadow_main()
            self.assertFalse(report.exists())


    def test_26_raw_graph_bytes_differ_from_pins_before_native_execution(self):
        self.binary += b" "
        with patch.object(shadow_module, "_native_modules",
                          side_effect=AssertionError("native used before graph source check")):
            with self.assertRaisesRegex(CycleHold, "^GRAPH_BLOB_PIN_MISMATCH$"):
                self.cycle()

    def test_27_snapshot_json_duplicate_repository_key_refuses(self):
        encoded = json.dumps(self.source).encode()
        encoded = encoded.replace(
            b'"repository":', b'"repository":"different/repo","repository":', 1)
        with self.assertRaisesRegex(CycleHold, "^SNAPSHOT_DUPLICATE_JSON_KEY$"):
            shadow_module._decode_snapshot(encoded)

    def test_28_snapshot_json_nonfinite_and_invalid_utf8_refuse(self):
        encoded = json.dumps(self.source).encode()
        for mutated in (encoded[:-1] + b',"extra":NaN}',
                        encoded + bytes([255])):
            with self.subTest(mutated=mutated[-20:]):
                with self.assertRaisesRegex(CycleHold, "^SNAPSHOT_JSON_INVALID$"):
                    shadow_module._decode_snapshot(mutated)

    def test_29_snapshot_bytes_over_budget_refuse(self):
        raw_snapshot = json.dumps(self.source).encode()
        with patch.object(shadow_module, "_MAX_SNAPSHOT_BYTES", 128):
            with self.assertRaisesRegex(CycleHold, "^SNAPSHOT_BYTES_UNBOUNDED$"):
                shadow_module._decode_snapshot(raw_snapshot)

    def test_30_malformed_nested_snapshot_records_refuse_before_native(self):
        for collection, key, value in (
            ("issues", "1", "not a record"),
            ("pulls", "10", 1),
            ("comments", "2", {"invalid": "not a comment list"}),
        ):
            with self.subTest(collection=collection):
                source = deepcopy(self.source)
                source[collection][key] = value
                with patch.object(shadow_module, "_native_modules",
                                  side_effect=AssertionError("native reached with malformed source")):
                    with self.assertRaisesRegex(CycleHold,
                                                "^SOURCE_SNAPSHOT_RECORD_INVALID$"):
                        integrated_shadow(self.binary, self.pin, source)


    def test_31_shadow_cli_rejects_ambiguous_and_oversize_snapshots_without_output(self):
        with TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            snapshot = Path(directory) / "snapshot.json"
            output = Path(directory) / "report.json"
            graph.write_bytes(self.binary)
            argv = ["v32_integrated_shadow.py", "--graph", str(graph),
                    "--snapshot", str(snapshot), "--repository-id", "42",
                    "--leaf", self.pin.leaf_ref, "--graph-blob",
                    self.pin.released_graph_blob_oid, "--head", HEAD,
                    "--output", str(output)]
            original = json.dumps(self.source).encode()
            duplicate = original.replace(
                b'"repository":', b'"repository":"different/repo","repository":', 1)
            snapshot.write_bytes(duplicate)
            with patch.object(sys, "argv", argv):
                with self.assertRaisesRegex(CycleHold, "^SNAPSHOT_DUPLICATE_JSON_KEY$"):
                    shadow_main()
            self.assertFalse(output.exists())
            snapshot.write_bytes(original)
            with patch.object(sys, "argv", argv), patch.object(
                    shadow_module, "_MAX_SNAPSHOT_BYTES", 128):
                with self.assertRaisesRegex(CycleHold, "^SNAPSHOT_BYTES_UNBOUNDED$"):
                    shadow_main()
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
