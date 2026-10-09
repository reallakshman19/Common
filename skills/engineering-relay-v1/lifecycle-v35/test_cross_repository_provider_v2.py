"""WP1/U2 positive and adversarial provider-source binding, entirely synthetic."""
from __future__ import annotations

import base64
import copy
import hashlib
import unittest

from cross_repository_provider_v2 import (
    _native_get, observe_crossrepo_provider_v2,
)
from test_cross_repository_identity_v2 import fixture

OLD, NEW = "reallaksh19/Common", "reallakshman19/Common"
GRAPH = b"graph: synthetic source pinned by content digest\n"


def read_fixture():
    envelope = fixture()
    envelope["current_identity"]["graph_source"]["content_sha256"] = (
        "sha256:" + hashlib.sha256(GRAPH).hexdigest()
    )
    origin, target = envelope["historical_origin"], envelope["current_target"]
    identity = envelope["current_identity"]
    g, s, candidate = identity["graph_source"], identity["session_source"], identity["candidate_source"]
    entries = {}
    counts = {}

    for value in (origin, target):
        slug = value["repository"]
        entries[(slug, "")] = {"id": value["repository_id"], "full_name": slug}
        entries[(slug, f"issues/{value['number']}")] = {
            "number": value["number"], "html_url": value["url"], "state": "open"
        }

    for slug, sha in (
        (OLD, envelope["source_continuity"]["historical_commit_sha"]),
        (NEW, envelope["source_continuity"]["current_commit_sha"]),
        (NEW, g["revision_sha"]),
        (NEW, s["commit_sha"]),
    ):
        entries[(slug, "commits/" + sha)] = {"sha": sha}

    entries[(NEW, "contents/" + g["path"] + "?ref=" + g["revision_sha"])] = {
        "type": "file", "encoding": "base64",
        "content": base64.b64encode(GRAPH).decode("ascii"),
    }
    entries[(NEW, f"pulls/{candidate['pr_number']}")] = {
        "number": candidate["pr_number"],
        "head": {
            "sha": candidate["head_sha"], "ref": "feat/v35-current-candidate",
            "repo": {"full_name": NEW},
        },
        "base": {"sha": candidate["base_sha"], "repo": {"full_name": NEW}},
    }
    entries[(NEW, "git/ref/heads/feat/v35-current-candidate")] = {
        "ref": "refs/heads/feat/v35-current-candidate",
        "object": {"sha": candidate["head_sha"]},
    }

    def read(slug, route):
        counts[(slug, route)] = counts.get((slug, route), 0) + 1
        if (slug, route) not in entries:
            raise ValueError("SIMULATED_PROVIDER_NOT_FOUND")
        return copy.deepcopy(entries[(slug, route)])

    return envelope, entries, counts, read


class NativeSourceBindingTests(unittest.TestCase):
    def test_positive_current_provider_references_are_never_authority(self):
        envelope, _, counts, read = read_fixture()
        result = observe_crossrepo_provider_v2(envelope, read)
        self.assertEqual("CALLER_INJECTED_UNATTESTED", result["source_grade"])
        self.assertEqual("MATCH_AT_OBSERVATION", result["candidate_currentness"])
        self.assertEqual(2, counts[(NEW, "pulls/9")])
        self.assertEqual(2, counts[(NEW, "git/ref/heads/feat/v35-current-candidate")])
        self.assertFalse(result["owner_authenticated"])
        self.assertFalse(result["reviewer_qualified"])
        self.assertFalse(result["evidence_accepted"])
        self.assertFalse(result["writer_authorized"])
        self.assertIsNone(result["programme_progress"])

    def test_wrong_provider_repo_stable_id(self):
        envelope, entries, _, read = read_fixture()
        entries[(NEW, "")]["id"] = 1207996454
        with self.assertRaisesRegex(ValueError, "REPO_ID_OR_NAME_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_old_issue_replaced_with_pr_does_not_transfer(self):
        envelope, entries, _, read = read_fixture()
        entries[(OLD, "issues/787")]["pull_request"] = {"url": "forged"}
        with self.assertRaisesRegex(ValueError, "ISSUE_PROVIDER_BINDING_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_new_issue_wrong_object_number(self):
        envelope, entries, _, read = read_fixture()
        entries[(NEW, "issues/5")]["number"] = 15
        with self.assertRaisesRegex(ValueError, "ISSUE_PROVIDER_BINDING_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_old_commit_not_available_in_origin_repo(self):
        envelope, entries, _, read = read_fixture()
        entries[(OLD, "commits/" + envelope["source_continuity"]["historical_commit_sha"])]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_COMMIT_NOT_VERIFIED"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_graph_sha_reference_without_matching_raw_content_is_not_verified(self):
        envelope, entries, _, read = read_fixture()
        g = envelope["current_identity"]["graph_source"]
        entries[(NEW, "contents/" + g["path"] + "?ref=" + g["revision_sha"])]["content"] = (
            base64.b64encode(b"graph: malicious changed body").decode("ascii")
        )
        with self.assertRaisesRegex(ValueError, "GRAPH_CONTENT_DIGEST_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_wrong_session_role_commit_denied(self):
        envelope, entries, _, read = read_fixture()
        entries[(NEW, "commits/" + envelope["current_identity"]["session_source"]["commit_sha"])]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_ROLE_COMMIT_NOT_VERIFIED"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_current_candidate_head_changed_denied(self):
        envelope, entries, _, read = read_fixture()
        entries[(NEW, "pulls/9")]["head"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "CANDIDATE_PR_HEAD_OR_REPO_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_pr_source_branch_mismatch_denied(self):
        envelope, entries, _, read = read_fixture()
        entries[(NEW, "git/ref/heads/feat/v35-current-candidate")]["object"]["sha"] = "e" * 40
        with self.assertRaisesRegex(ValueError, "PR_BRANCH_REF_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, read)

    def test_candidate_moved_on_second_provider_read_denied(self):
        envelope, entries, counts, original = read_fixture()
        def concurrent(slug, route):
            if (slug, route) == (NEW, "pulls/9") and counts.get((slug, route), 0) == 1:
                entries[(NEW, "pulls/9")]["head"]["sha"] = "e" * 40
                entries[(NEW, "git/ref/heads/feat/v35-current-candidate")]["object"]["sha"] = "e" * 40
            return original(slug, route)
        with self.assertRaisesRegex(ValueError, "CANDIDATE_PR_HEAD_OR_REPO_MISMATCH"):
            observe_crossrepo_provider_v2(envelope, concurrent)

    def test_foreign_owner_and_reviewer_grants_rejected_before_reads(self):
        envelope, _, counts, read = read_fixture()
        envelope["owner_original_source"] = "AUTHENTICATED"
        with self.assertRaisesRegex(ValueError, "SCHEMA_INVALID"):
            observe_crossrepo_provider_v2(envelope, read)
        self.assertEqual({}, counts)

    def test_native_reader_fails_foreign_paths_before_network(self):
        with self.assertRaisesRegex(ValueError, "PROVIDER_PATH_NOT_ALLOWED"):
            _native_get(NEW, "issues/../../etc")
        with self.assertRaisesRegex(ValueError, "PROVIDER_PATH_NOT_ALLOWED"):
            _native_get("attacker/Other", "issues/1/../bad")

    def test_unknown_candidate_is_not_positive_material(self):
        envelope, _, _, read = read_fixture()
        envelope["current_identity"]["candidate_source"].update(
            state="UNKNOWN", pr_number=None, head_sha=None, base_sha=None
        )
        result = observe_crossrepo_provider_v2(envelope, read)
        self.assertIsNone(result["current_candidate_head_sha"])
        self.assertEqual("UNKNOWN", result["candidate_currentness"])
        self.assertFalse(result["evidence_accepted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
