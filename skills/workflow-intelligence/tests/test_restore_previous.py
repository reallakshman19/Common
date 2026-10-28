"""Selection of a trusted predecessor from bounded GitHub artifact metadata."""
import copy
import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("restore", SCRIPTS / "restore_previous.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
CURRENT = {"id": 101, "workflow_id": 23, "repository": {"full_name": "owner/repo"},
           "created_at": "2026-10-14T17:00:00Z", "event": "schedule",
           "head_branch": "main", "head_sha": "a"*40}
PRIOR = {"id": 100, "workflow_id": 23, "repository": {"full_name": "owner/repo"},
         "created_at": "2026-10-14T16:45:00Z", "event": "schedule",
         "status": "completed", "conclusion": "success",
         "head_branch": "main", "head_sha": "b"*40}
ART = {"name": mod.ARTIFACT_NAME, "expired": False, "size_in_bytes": 1200,
       "created_at": "2026-10-14T16:50:00Z",
       "workflow_run": {"id": 100, "head_sha": "b"*40}}


def reader(current=None, prior=None, artifacts=None):
    current = copy.deepcopy(current if current is not None else CURRENT)
    prior = copy.deepcopy(prior if prior is not None else PRIOR)
    artifacts = copy.deepcopy(artifacts if artifacts is not None else [ART])
    def get(endpoint):
        if endpoint == "/actions/runs/101":
            return current
        if endpoint == "/actions/runs/100":
            return prior
        if endpoint.startswith("/actions/artifacts?"):
            if endpoint.endswith("page=1"):
                return {"artifacts": artifacts}
            return {"artifacts": []}
        raise AssertionError(endpoint)
    return get


class RestorationTests(unittest.TestCase):
    def test_valid_successful_same_workflow_run(self):
        self.assertEqual(mod.pick_run("owner/repo", 101, reader=reader()), 100)

    def test_no_prior_artifact_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(artifacts=[]))

    def test_failed_prior_run_fails(self):
        value = dict(PRIOR, conclusion="failure")
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=value))

    def test_skipped_prior_run_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=dict(PRIOR, conclusion="skipped")))

    def test_other_workflow_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=dict(PRIOR, workflow_id=999)))

    def test_wrong_branch_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=dict(PRIOR, head_branch="feature")))

    def test_wrong_repository_fails(self):
        value = dict(PRIOR, repository={"full_name": "other/repo"})
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=value))

    def test_wrong_event_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(prior=dict(PRIOR, event="pull_request")))

    def test_foreign_sha_fails(self):
        other = dict(ART, workflow_run={"id": 100, "head_sha": "f"*40})
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(artifacts=[other]))

    def test_expired_or_empty_artifact_fails(self):
        for artifact in (dict(ART, expired=True), dict(ART, size_in_bytes=0)):
            with self.subTest(artifact=artifact):
                with self.assertRaises(ValueError):
                    mod.pick_run("owner/repo", 101, reader=reader(artifacts=[artifact]))

    def test_bad_repository_rejected_before_request(self):
        for name in ("../repo", "owner/..", "owner/repo/path", "", "http://evil/repo"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                mod.pick_run(name, 101, reader=lambda _: self.fail("unexpected read"))

    def test_stale_artifact_rejected(self):
        art = dict(ART, created_at="2026-10-01T00:00:00Z")
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(artifacts=[art]))

    def test_created_after_current_rejected(self):
        art = dict(ART, created_at="2026-10-14T18:00:00Z")
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(artifacts=[art]))

    def test_current_run_identity_mismatch_fails(self):
        cur = dict(CURRENT, workflow_id="23")
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=reader(current=cur))

    def test_manual_dispatch_allowed(self):
        current = dict(CURRENT, event="workflow_dispatch")
        prior = dict(PRIOR, event="workflow_dispatch")
        self.assertEqual(mod.pick_run("owner/repo", 101,
                                      reader=reader(current=current, prior=prior)), 100)

    def test_invalid_artifacts_page_fails(self):
        def bad(endpoint):
            if "/actions/artifacts?" in endpoint:
                return {"artifacts": {"not": "list"}}
            return copy.deepcopy(CURRENT)
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101, reader=bad)

    def test_prior_not_completed_fails(self):
        with self.assertRaises(ValueError):
            mod.pick_run("owner/repo", 101,
                         reader=reader(prior=dict(PRIOR, status="in_progress", conclusion=None)))


if __name__ == "__main__":
    unittest.main()
