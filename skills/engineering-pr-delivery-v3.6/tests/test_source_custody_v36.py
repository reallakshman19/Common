"""C2 adversarial tests: byte proof, actor observation, drift, independence."""
from __future__ import annotations
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "source_custody_v36.py"
SPEC = importlib.util.spec_from_file_location("source_custody_v36", SOURCE)
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)

REPO = "example/project"
REV = "a" * 40
BYTES = b"synthetic C2 identity-only fixture, not an Owner original\n"
BLOB = c.git_blob_sha1(BYTES)
DIGEST = hashlib.sha256(BYTES).hexdigest()
REPO_API = "https://api.github.com/repos/" + REPO


def manifest():
    return {
        "schema": c.SCHEMA, "repository": REPO, "revision": REV,
        "artifacts": [
            {"id": "DEMO_001", "role": "DEMONSTRATION_ONLY",
             "path": "tests/test.bin", "expected_blob_sha1": BLOB,
             "expected_sha256": DIGEST, "expected_size_bytes": len(BYTES),
             "oracle_complete": None}],
        "issue_records": [
            {"id": "ISSUE_001", "kind": "ISSUE", "issue_number": 400,
             "comment_id": None, "claimed_actor": "owneruser",
             "expected_body_sha256": hashlib.sha256(b"Human outcome").hexdigest(),
             "expected_updated_at": "2026-10-16T10:00:00Z"},
            {"id": "COMMENT_001", "kind": "ISSUE_COMMENT", "issue_number": 400,
             "comment_id": 987, "claimed_actor": "owneruser",
             "expected_body_sha256": None, "expected_updated_at": None}]
    }


class FakeGitHub:
    def __init__(self):
        self.calls = []
        self.objects = {
            "/repos/" + REPO + "/contents/tests/test.bin?ref=" + REV: {
                "type": "file", "sha": BLOB, "size": len(BYTES)},
            "/repos/" + REPO + "/git/blobs/" + BLOB: {
                "sha": BLOB, "encoding": "base64",
                "content": base64.b64encode(BYTES).decode()},
            "/repos/" + REPO + "/issues/400": {
                "number": 400, "user": {"login": "owneruser"},
                "updated_at": "2026-10-16T10:00:00Z", "body": "Human outcome"},
            "/repos/" + REPO + "/issues/comments/987": {
                "issue_url": REPO_API + "/issues/400",
                "user": {"login": "owneruser"},
                "updated_at": "2026-10-16T10:01:00Z", "body": "Material correction"}
        }

    def get(self, path):
        self.calls.append(path)
        if path not in self.objects:
            raise c.ProviderFailure("NOT_FOUND_UNVERIFIED")
        response = self.objects[path]
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


class SourceCustodyTests(unittest.TestCase):
    def fixture(self):
        return manifest(), FakeGitHub()

    def test_positive_byte_and_provider_actor_only(self):
        doc, client = self.fixture()
        result = c.audit(doc, client)
        self.assertEqual(result["byte_verified"], 1)
        self.assertEqual(result["provider_actors_observed"], 2)
        self.assertEqual(result["artifacts"][0]["status"],
                         "BYTE_VERIFIED_ON_PINNED_GIT_REVISION")
        self.assertEqual(result["issue_records"][0]["status"],
                         "PROVIDER_RECORD_OBSERVED_NOT_OWNER_AUTHENTICATED")
        self.assertTrue(result["issue_records"][0]["claimed_actor_matches"])
        self.assertEqual(result["semantic_verified"], 0)
        self.assertEqual(result["owner_decisions_authenticated"], 0)
        for flag in ("may_publish", "may_count_for_o2",
                     "may_change_titles_or_labels", "may_merge_or_release"):
            self.assertFalse(result[flag])
        self.assertFalse(result["v3_5_v3_2_runtime_dependency"])

    def test_wrong_declared_sha256_cannot_be_verified(self):
        doc, client = self.fixture()
        doc["artifacts"][0]["expected_sha256"] = "f" * 64
        result = c.audit(doc, client)
        self.assertEqual(result["byte_verified"], 0)
        self.assertEqual(result["artifacts"][0]["status"], "CONTRADICTED_ACTUAL_BYTES")

    def test_provider_blob_does_not_match_pinned_git_sha(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/git/blobs/" + BLOB]["content"] = (
            base64.b64encode(b"wrong bytes").decode())
        self.assertEqual(c.audit(doc, client)["artifacts"][0]["status"],
                         "CONTRADICTED_ACTUAL_BYTES")

    def test_pinned_path_wrong_blob_blocks(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/contents/tests/test.bin?ref=" + REV]["sha"] = "b" * 40
        result = c.audit(doc, client)
        self.assertEqual(result["byte_verified"], 0)
        self.assertEqual(result["artifacts"][0]["status"],
                         "CONTRADICTED_PINNED_PATH_OR_BLOB")

    def test_wrong_size_rejected_before_blob_fetch(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/contents/tests/test.bin?ref=" + REV]["size"] += 1
        result = c.audit(doc, client)
        self.assertEqual(result["artifacts"][0]["status"],
                         "CONTRADICTED_DECLARED_SIZE")
        self.assertEqual(len([p for p in client.calls if "/git/blobs/" in p]), 0)

    def test_missing_blob_does_not_infer_deletion(self):
        doc, client = self.fixture()
        client.objects.pop("/repos/" + REPO + "/git/blobs/" + BLOB)
        result = c.audit(doc, client)
        self.assertEqual(result["artifacts"][0]["status"], "NOT_FOUND_UNVERIFIED")

    def test_limit_is_explicit_and_prevents_download(self):
        doc, client = self.fixture()
        doc["artifacts"][0]["expected_size_bytes"] = c.MAX_BLOB_BYTES + 1
        result = c.audit(doc, client)
        self.assertEqual(result["artifacts"][0]["status"],
                         "SIZE_OUT_OF_C2_PILOT_RANGE_UNVERIFIED")
        self.assertFalse(any('/contents/' in p or '/git/blobs/' in p for p in client.calls))

    def test_original_role_is_not_automatic_proof(self):
        doc, client = self.fixture()
        doc["artifacts"][0]["role"] = "ORIGINAL_POSITIVE"
        result = c.audit(doc, client)
        self.assertTrue(result["artifacts"][0]["byte_identity_verified"])
        self.assertEqual(result["semantic_verified"], 0)
        self.assertEqual(result["artifacts"][0]["semantic_acceptance"], "NOT_ESTABLISHED")

    def test_partial_golden_cannot_claim_complete(self):
        doc, client = self.fixture()
        doc["artifacts"][0].update(role="PARTIAL_GOLDEN", oracle_complete=True)
        with self.assertRaisesRegex(c.InvalidManifest,
                                    "PARTIAL_GOLDEN_REQUIRES_PARTIAL_ORACLE"):
            c.audit(doc, client)

    def test_full_golden_requires_completeness_claim(self):
        doc, client = self.fixture()
        doc["artifacts"][0].update(role="COMPLETE_GOLDEN", oracle_complete=None)
        with self.assertRaisesRegex(c.InvalidManifest,
                                    "FULL_GOLDEN_REQUIRES_COMPLETE_ORACLE_CLAIM"):
            c.audit(doc, client)

    def test_changed_issue_body_is_contradicted_not_owner_adopted(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/issues/400"]["body"] = "Changed instruction"
        result = c.audit(doc, client)
        self.assertEqual(result["issue_records"][0]["status"], "CONTRADICTED_ISSUE_BODY")
        self.assertEqual(result["owner_decisions_authenticated"], 0)

    def test_stale_issue_timestamp_detected_first(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/issues/400"]["updated_at"] = "2026-10-16T12:00:00Z"
        self.assertEqual(c.audit(doc, client)["issue_records"][0]["status"], "STALE_ISSUE_EDIT")

    def test_wrong_actor_does_not_create_owner_authority(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/issues/400"]["user"]["login"] = "someoneelse"
        result = c.audit(doc, client)
        self.assertEqual(result["issue_records"][0]["status"], "CONTRADICTED_CLAIMED_ACTOR")
        self.assertEqual(result["owner_decisions_authenticated"], 0)

    def test_comment_wrong_parent_rejected(self):
        doc, client = self.fixture()
        client.objects["/repos/" + REPO + "/issues/comments/987"]["issue_url"] = (
            REPO_API + "/issues/401")
        self.assertEqual(c.audit(doc, client)["issue_records"][1]["status"],
                         "CONTRADICTED_COMMENT_PARENT")

    def test_not_found_comment_keeps_access_uncertainty(self):
        doc, client = self.fixture()
        client.objects.pop("/repos/" + REPO + "/issues/comments/987")
        self.assertEqual(c.audit(doc, client)["issue_records"][1]["status"],
                         "NOT_FOUND_UNVERIFIED")

    def test_no_mutation_of_manifest(self):
        doc, client = self.fixture()
        original = copy.deepcopy(doc)
        c.audit(doc, client)
        self.assertEqual(doc, original)

    def test_no_unpinned_revision(self):
        doc, client = self.fixture()
        doc["revision"] = "main"
        with self.assertRaisesRegex(c.InvalidManifest, "REVISION_MUST_BE_PINNED_SHA40"):
            c.audit(doc, client)

    def test_path_traversal_and_host_switch_blocked(self):
        doc, client = self.fixture()
        for invalid_path in ("../../secrets", "/etc/passwd", "a\\b", "a//b"):
            with self.subTest(path=invalid_path):
                copy_doc = copy.deepcopy(doc)
                copy_doc["artifacts"][0]["path"] = invalid_path
                with self.assertRaisesRegex(c.InvalidManifest, "UNSAFE_ARTIFACT_PATH"):
                    c.audit(copy_doc, client)

    def test_duplicate_id_rejected(self):
        doc, client = self.fixture()
        doc["issue_records"][0]["id"] = "DEMO_001"
        with self.assertRaisesRegex(c.InvalidManifest, "INVALID_OR_DUPLICATE_RECORD_ID"):
            c.audit(doc, client)

    def test_real_repository_fixture_is_pinned_but_cannot_grant_acceptance(self):
        source = SOURCE.parents[1] / "tests" / "fixtures" / "c2-3d-firstpass-nc-pinned.json"
        entry = json.loads(source.read_text(encoding="utf-8"))
        c.validate_manifest(entry)
        self.assertEqual(entry["repository"], "reallakshman19/3D_Converters")
        self.assertEqual(entry["revision"],
                         "6e7f4b98e286d19598fc6cb27f007c12811fbc4d")
        self.assertEqual(len(entry["artifacts"]), 5)
        self.assertEqual(sum(x["role"] == "ORIGINAL_POSITIVE" for x in entry["artifacts"]), 2)
        self.assertEqual(sum(x["role"] == "ORIGINAL_NEGATIVE" for x in entry["artifacts"]), 2)
        self.assertEqual(sum(x["role"] == "PARTIAL_GOLDEN" for x in entry["artifacts"]), 1)
        self.assertFalse(any(x["role"] == "COMPLETE_GOLDEN" for x in entry["artifacts"]))
        self.assertEqual(entry["issue_records"][0]["claimed_actor"], None)

    def test_python_imports_are_stdlib_only_and_no_legacy_relay(self):
        source = SOURCE.read_text(encoding="utf-8")
        for token in ("import lifecycle_v32", "import lifecycle_v35",
                      "from engineering_pr_delivery_v3_2", "from delp",
                      "from issue_chain_v36", "from continuity_bridge_v36"):
            self.assertNotIn(token, source)
        self.assertNotIn("def apply(", source)
        self.assertNotIn("method=\"POST\"", source)


if __name__ == "__main__":
    unittest.main()
