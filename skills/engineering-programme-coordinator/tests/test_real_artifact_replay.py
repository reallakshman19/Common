import copy
import importlib.util
import sys
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from real_artifact_replay import (
    run_real_artifact_replay,
    run_test_double_replay,
    RealArtifactReplayError,
)


MANIFEST_PATH = ROOT / "references" / "p1-i-b-real-artifact-manifest.yaml"


def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


class FakeProvider:
    def __init__(self, data):
        self.data = data

    def get_json(self, path):
        if path not in self.data:
            raise RealArtifactReplayError("fake provider missing path: " + path)
        return copy.deepcopy(self.data[path])


def fake_provider_data(value):
    repo = value["repository"]
    source = value["source"]
    data = {}
    for name, spec in value["comments"].items():
        data[f"/repos/{repo}/issues/comments/{spec['id']}"] = {
            "id": spec["id"],
            "user": {"login": spec["author"]},
            "created_at": spec["created_at"],
            "updated_at": spec["updated_at"],
            "html_url": f"https://github.com/{repo}/issues/{spec['issue']}#issuecomment-{spec['id']}",
            "body": "\n".join(spec["required_tokens"]),
        }
    data[f"/repos/{repo}/pulls/{source['pr']}"] = {
        "number": source["pr"],
        "merged": True,
        "head": {"ref": source["branch"], "sha": "f" * 40},
        "base": {"sha": "e" * 40},
    }
    data[f"/repos/{repo}/commits/{source['exact_head']}"] = {
        "sha": source["exact_head"],
    }
    root_tree = "1" * 40
    skills_tree = "2" * 40
    data[f"/repos/{repo}/commits/{source['target_sha']}"] = {
        "sha": source["target_sha"],
        "commit": {"tree": {"sha": root_tree}},
    }
    data[f"/repos/{repo}/git/trees/{root_tree}"] = {
        "sha": root_tree,
        "tree": [{"path": "skills", "type": "tree", "sha": skills_tree}],
    }
    data[f"/repos/{repo}/git/trees/{skills_tree}"] = {
        "sha": skills_tree,
        "tree": [
            {
                "path": "Local_PR_Deliverty_v1.1",
                "type": "tree",
                "sha": value["protocol_identity"]["local"]["tree_sha1"],
            },
            {
                "path": "engineering-pr-delivery-v3.5",
                "type": "tree",
                "sha": value["protocol_identity"]["v35"]["tree_sha1"],
            },
        ],
    }
    data[f"/repos/{repo}/pulls/{source['pr']}/commits?per_page=100&page=1"] = [
        {"sha": source["exact_head"]},
    ]
    for spec in value["workflow_runs"]:
        data[f"/repos/{repo}/actions/runs/{spec['id']}"] = {
            "id": spec["id"],
            "name": spec["name"],
            "head_sha": spec["head_sha"],
            "head_branch": spec["head_branch"],
            "event": spec["event"],
            "conclusion": spec["conclusion"],
            "status": "completed",
        }
    return data


def current_head():
    import subprocess
    proc = subprocess.run(
        ["git", "-C", str(ROOT.parents[1]), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    )
    return proc.stdout.strip()


class RealArtifactReplayTests(unittest.TestCase):
    def replay(self, value=None, data=None):
        value = value or manifest()
        data = data or fake_provider_data(value)
        return run_test_double_replay(
            value,
            FakeProvider(data),
            repo_root=ROOT.parents[1],
            candidate_sha=current_head(),
        )

    def test_test_double_cannot_qualify_horizontal_integration(self):
        result = self.replay()
        self.assertEqual(result["artifact_class"], "TEST_DOUBLE_UNATTESTED")
        self.assertFalse(result["provider_attestation"]["live_verified"])
        self.assertEqual(
            result["production_readiness"]["components"]["real_artifact_horizontal_integration"]["state"],
            "CONDITIONALLY_QUALIFIED",
        )
        self.assertIn(
            "P1I-REAL-ARTIFACT-MISSING",
            {row["id"] for row in result["production_readiness"]["cutover_blockers"]},
        )

    def test_qualifying_entrypoint_rejects_test_double(self):
        value = manifest()
        with self.assertRaisesRegex(
            RealArtifactReplayError,
            "requires concrete live GitHubProvider",
        ):
            run_real_artifact_replay(
                value,
                FakeProvider(fake_provider_data(value)),
                repo_root=ROOT.parents[1],
                candidate_sha=current_head(),
            )

    def test_current_local_projection_consumes_retained_control_truth(self):
        result = self.replay()
        self.assertEqual(result["local_observation"]["task_id"], "PRD-506-P0-R1")
        self.assertEqual(result["local_observation"]["release_state"], "READY")
        self.assertFalse(result["local_observation"]["local_responsibility_complete"])

    def test_current_v35_contract_preserves_nested_boundary(self):
        result = self.replay()
        self.assertEqual(
            result["v35"]["engineering_responsibility"],
            "ENG-PRD-506-P0-R1-CODER",
        )
        self.assertFalse(result["v35"]["engineering_responsibility_complete"])
        self.assertFalse(result["v35"]["local_responsibility_complete"])

    def test_historical_hosted_failures_must_remain_failures(self):
        value = manifest()
        data = fake_provider_data(value)
        run = next(row for row in value["workflow_runs"] if row["name"] == "Local PR Delivery v1.1 integration")
        data[f"/repos/{value['repository']}/actions/runs/{run['id']}"]["conclusion"] = "success"
        with self.assertRaisesRegex(RealArtifactReplayError, "conclusion drift"):
            self.replay(value, data)

    def test_comment_edit_invalidates_retained_artifact(self):
        value = manifest()
        data = fake_provider_data(value)
        spec = value["comments"]["super_review"]
        data[f"/repos/{value['repository']}/issues/comments/{spec['id']}"]["updated_at"] = "2026-10-06T02:00:00Z"
        with self.assertRaisesRegex(RealArtifactReplayError, "edited after pin"):
            self.replay(value, data)

    def test_comment_must_belong_to_pinned_issue(self):
        value = manifest()
        data = fake_provider_data(value)
        spec = value["comments"]["release_basis"]
        path = f"/repos/{value['repository']}/issues/comments/{spec['id']}"
        data[path]["html_url"] = (
            f"https://github.com/{value['repository']}/issues/999"
            f"#issuecomment-{spec['id']}"
        )
        with self.assertRaisesRegex(RealArtifactReplayError, "comment issue/ref mismatch"):
            self.replay(value, data)

    def test_qualifying_manifest_is_hard_bound_to_p1_i_b_source(self):
        value = manifest()
        value["source"]["exact_head"] = "f" * 40
        with self.assertRaisesRegex(
            RealArtifactReplayError,
            "Unexpected retained artifact source field: exact_head",
        ):
            self.replay(value, fake_provider_data(value))

    def test_missing_semantic_token_invalidates_provider_attestation(self):
        value = manifest()
        data = fake_provider_data(value)
        spec = value["comments"]["certification"]
        path = f"/repos/{value['repository']}/issues/comments/{spec['id']}"
        data[path]["body"] = data[path]["body"].replace(
            "nested_engineering_responsibility_complete: false",
            "",
        )
        with self.assertRaisesRegex(RealArtifactReplayError, "required provider token missing"):
            self.replay(value, data)

    def test_exact_historical_commit_must_still_resolve(self):
        value = manifest()
        data = fake_provider_data(value)
        source = value["source"]
        data[f"/repos/{value['repository']}/commits/{source['exact_head']}"] = {
            "sha": "f" * 40,
        }
        with self.assertRaisesRegex(RealArtifactReplayError, "candidate commit missing"):
            self.replay(value, data)

    def test_retained_pr_branch_identity_must_match(self):
        value = manifest()
        data = fake_provider_data(value)
        source = value["source"]
        data[f"/repos/{value['repository']}/pulls/{source['pr']}"]["head"]["ref"] = "other-branch"
        with self.assertRaisesRegex(RealArtifactReplayError, "PR branch mismatch"):
            self.replay(value, data)

    def test_workflow_event_and_branch_are_historical_binding_evidence(self):
        value = manifest()
        data = fake_provider_data(value)
        run = value["workflow_runs"][0]
        path = f"/repos/{value['repository']}/actions/runs/{run['id']}"
        data[path]["event"] = "push"
        with self.assertRaisesRegex(RealArtifactReplayError, "event mismatch"):
            self.replay(value, data)

    def test_noncanonical_local_release_state_is_rejected_by_current_local_runtime(self):
        value = manifest()
        value["source"]["release_state"] = "COMPLETE"
        data = fake_provider_data(value)
        with self.assertRaisesRegex(Exception, "non-canonical"):
            self.replay(value, data)

    def test_historical_protocol_tree_must_match_live_target_commit(self):
        value = manifest()
        data = fake_provider_data(value)
        root = data[
            f"/repos/{value['repository']}/commits/{value['source']['target_sha']}"
        ]["commit"]["tree"]["sha"]
        skills = data[f"/repos/{value['repository']}/git/trees/{root}"]["tree"][0]["sha"]
        rows = data[f"/repos/{value['repository']}/git/trees/{skills}"]["tree"]
        next(
            row for row in rows
            if row["path"] == "engineering-pr-delivery-v3.5"
        )["sha"] = "f" * 40
        with self.assertRaisesRegex(RealArtifactReplayError, "protocol tree SHA mismatch"):
            self.replay(value, data)

    def test_digest_namespaces_are_preserved_not_collapsed(self):
        result = self.replay()
        self.assertTrue(result["assertions"]["digest_namespaces_preserved"])

    def test_no_replay_output_grants_authority(self):
        result = self.replay()
        self.assertFalse(any(result["authority_boundaries"].values()))
        self.assertEqual(result["production_readiness"]["production_mode"], "OFF")

    def test_readiness_uses_actual_phase1_pull_request_refs(self):
        result = self.replay()
        components = result["production_readiness"]["components"]
        self.assertIn(
            "https://github.com/reallaksh19/Common/pull/551",
            components["active_authority_resolution"]["evidence_refs"],
        )
        self.assertIn(
            "https://github.com/reallaksh19/Common/pull/544",
            components["execution_kernel"]["evidence_refs"],
        )
        self.assertIn(
            "https://github.com/reallaksh19/Common/pull/547",
            components["provider_idempotency"]["evidence_refs"],
        )

    def test_source_residuals_are_retained(self):
        result = self.replay()
        self.assertIn("F3_AUTHENTICITY", result["historical_residuals"])
        self.assertIn("ASD-506-01", result["historical_residuals"])
        self.assertIn("HOSTED_PROTOCOL_JOB_CANCELLED", result["historical_residuals"])


if __name__ == "__main__":
    unittest.main()
