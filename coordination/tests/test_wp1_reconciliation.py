"""Integration/negative acceptance for Issue #353 WP1.
All external GitHub calls are simulated; no Owner/engineering approval inferred.
"""
import json
import socketserver
import tempfile
import threading
import unittest
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from coordination.contracts import (
    Project, Work, ExecutionLane, AgentAssignment, AgentRun,
    TabBinding, ControlTowerRegistry,
)
from coordination.coordination_ui import ApiHandler
from coordination.indexer import (
    EvidenceIndex, CanonicalV36Adapter, ProviderFailure,
    ingest_issue_evidence, ingest_pr_checks, generate_control_tower_snapshot,
)


def canonical(visible="Worker trace remains responsive", issue="353", candidate="a"*40):
    return (
        "Outcome: O1\n"
        f"For the user: {visible}\n"
        "Proof: https://github.com/reallakshman19/Common/issues/353\n"
        "TASK_EVIDENCE v3.6\n"
        "Task: WP1-353-W01\n"
        f"Child issue: reallakshman19/Common#{issue}\n"
        f"Candidate: {candidate}\n"
        "Tests: 3/3\n"
    )


class FakeGitHub:
    def __init__(self):
        self.body = canonical()
        self.fail = None
        self.head = "a"*40
        self.check_head = "a"*40
        self.calls = []

    def get_json(self, path, query=None):
        self.calls.append((path, query))
        if self.fail:
            raise ProviderFailure(self.fail)
        if path == "repos/reallakshman19/Common":
            return {"id": 1412133785, "full_name": "reallakshman19/Common"}
        if path == "repos/reallakshman19/Common/issues/353/comments":
            return [{
                "id": 8899, "body": self.body,
                "created_at": "2026-10-12T10:00:00Z",
                "updated_at": "2026-10-12T10:00:00Z",
                "html_url": "https://github.com/reallakshman19/Common/issues/353#issuecomment-8899",
                "user": {"login": "source-author"},
            }]
        if path == "repos/reallakshman19/Common/pulls/352":
            return {"head": {"sha": self.head}}
        if path.startswith("repos/reallakshman19/Common/commits/") and path.endswith("/check-runs"):
            return {"check_runs": [{
                "id": 1001, "name": "coordination-ci",
                "status": "completed", "conclusion": "success",
                "head_sha": self.check_head,
                "html_url": "https://github.com/reallakshman19/Common/actions/runs/1001",
                "updated_at": "2026-10-12T10:00:00Z",
            }]}
        raise AssertionError("Unexpected provider request: " + path)


class TestWP1ProviderAndSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = str(Path(self.temp.name) / "wp1.db")
        self.idx = EvidenceIndex(self.db)
        self.provider = FakeGitHub()

    def tearDown(self):
        self.idx.close()
        self.temp.cleanup()

    def test_real_canonical_admission_replay_and_edit(self):
        first = ingest_issue_evidence(self.idx, self.provider,
            project_id="project-A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(first["provider_status"], "REACHABLE")
        self.assertEqual(first["canonical"], 1)
        self.assertEqual(len(self.idx.get_active_evidence("project-A")), 1)
        second = ingest_issue_evidence(self.idx, self.provider,
            project_id="project-A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(second["replayed"], 1)
        self.assertEqual(len(self.idx.get_evidence_versions("project-A", "8899")), 1)
        self.provider.body = canonical("Updated user impact")
        third = ingest_issue_evidence(self.idx, self.provider,
            project_id="project-A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(third["canonical"], 1)
        versions = self.idx.get_evidence_versions("project-A", "8899")
        self.assertEqual([x["version"] for x in versions], [1, 2])
        self.assertEqual(sum(x["is_active_version"] for x in versions), 1)
        # Replay of the original version cannot create v3.
        self.provider.body = canonical()
        ingest_issue_evidence(self.idx, self.provider,
            project_id="project-A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(len(self.idx.get_evidence_versions("project-A", "8899")), 2)

    def test_wrong_child_and_malformed_comment_are_not_admitted(self):
        self.provider.body = canonical(issue="999")
        one = ingest_issue_evidence(self.idx, self.provider,
            project_id="A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(one["rejected"], 1)
        self.assertEqual(self.idx.get_active_evidence("A"), [])
        self.provider.body = canonical() + "Extra: forbidden\n"
        two = ingest_issue_evidence(self.idx, self.provider,
            project_id="A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(two["rejected"], 1)
        self.assertEqual(self.idx.get_active_evidence("A"), [])

    def test_provider_429_isolated_without_forging_live_state(self):
        self.provider.fail = 429
        degraded = ingest_issue_evidence(self.idx, self.provider,
            project_id="A", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(degraded["provider_status"], "RATE_LIMITED")
        self.assertEqual(self.idx.get_project_status("A"), "RATE_LIMITED")
        self.provider.fail = None
        success = ingest_issue_evidence(self.idx, self.provider,
            project_id="B", repository="reallakshman19/Common", issue_number=353)
        self.assertEqual(success["provider_status"], "REACHABLE")
        self.assertEqual(self.idx.get_project_status("A"), "RATE_LIMITED")
        self.assertEqual(self.idx.get_project_status("B"), "REACHABLE")
        self.assertEqual(self.idx.get_project_status("NEVER_OBSERVED"), "UNKNOWN")

    def test_ci_uses_fetched_provider_pr_head(self):
        self.provider.head = "b"*40
        self.provider.check_head = "a"*40
        result = ingest_pr_checks(self.idx, self.provider,
            project_id="A", repository="reallakshman19/Common", pr_number=352)
        self.assertEqual(result["observed_head"], "b"*40)
        self.assertEqual(result["counts"]["TESTS_PASSED_ON_OLD_HEAD"], 1)
        self.assertEqual(self.idx.get_checks_for_pr("A", 352)[0]["head_sha"], "a"*40)

    def test_immutable_event_collision_is_rejected(self):
        common = {
            "event_id":"same-id", "project_id":"A", "source_kind":"GITHUB_ISSUE_COMMENT",
            "source_ref":"https://github.com/reallakshman19/Common/issues/353",
            "source_revision":"1", "content_sha":"a"*64, "raw_payload":{},
            "observed_at_utc":"2026-10-12T10:00:00Z",
            "ingested_at_utc":"2026-10-12T10:00:01Z",
            "parse_status":"PARSED", "scope_key":"A/353"
        }
        self.assertTrue(self.idx.record_ingestion_event(common))
        self.assertFalse(self.idx.record_ingestion_event(common))
        changed = dict(common, content_sha="b"*64)
        with self.assertRaises(ValueError):
            self.idx.record_ingestion_event(changed)

    def test_wal_concurrent_ingestions_have_no_lost_events(self):
        def write(i):
            event = {
                "event_id":f"evt-{i}", "project_id":"A" if i%2 else "B",
                "source_kind":"GITHUB_ISSUE_COMMENT",
                "source_ref":"https://github.com/reallakshman19/Common/issues/353",
                "source_revision":str(i), "content_sha":"a"*64,
                "raw_payload":{}, "observed_at_utc":"2026-10-12T10:00:00Z",
                "ingested_at_utc":"2026-10-12T10:00:01Z", "parse_status":"PARSED",
                "scope_key":"A/353"
            }
            return self.idx.record_ingestion_event(event)
        with ThreadPoolExecutor(max_workers=6) as pool:
            self.assertEqual(sum(pool.map(write, range(50))), 50)
        with self.idx._lock:
            count = self.idx._get_connection().execute(
                "SELECT count(*) FROM ingestion_events").fetchone()[0]
        self.assertEqual(count, 50)


class TestWP1Snapshot(unittest.TestCase):
    def test_two_projects_five_assignments_and_private_export_blocked(self):
        fixture = Path(__file__).parent / "fixtures/two_projects_five_agents_fixture.json"
        data = json.loads(fixture.read_text(encoding="utf-8"))
        registry = ControlTowerRegistry()
        for key, cls, method in (
            ("projects", Project, registry.register_project),
            ("works", Work, registry.register_work),
            ("execution_lanes", ExecutionLane, registry.register_lane),
            ("assignments", AgentAssignment, registry.register_assignment),
            ("runs", AgentRun, registry.register_run),
            ("tab_bindings", TabBinding, registry.register_binding)
        ):
            for obj in data[key]:
                method(cls(**obj))
        with tempfile.TemporaryDirectory() as d:
            idx = EvidenceIndex(str(Path(d) / "db.sqlite"))
            try:
                before = {b.binding_id:b.binding_state for b in registry.bindings.values()}
                snap = generate_control_tower_snapshot(registry, idx)
                self.assertEqual(len(snap["projects"]), 2)
                self.assertEqual(len(snap["assignments"]), 5)
                self.assertEqual(before, {b.binding_id:b.binding_state for b in registry.bindings.values()})
                self.assertIn("responsibility_id", snap["assignments"][0])
                with self.assertRaises(PermissionError):
                    generate_control_tower_snapshot(registry, idx, visibility="PUBLIC")
            finally:
                idx.close()

    def test_http_missing_index_never_fabricates_reachable(self):
        with tempfile.TemporaryDirectory() as d:
            db = Path(d) / "nonexistent.db"
            class BoundHandler(ApiHandler):
                pass
            BoundHandler.config = {
                "projects": [{"id":"A", "name":"A", "coordination_dir":d,
                              "repo_url":"https://github.com/reallakshman19/Common"},
                             {"id":"B", "name":"B", "coordination_dir":d,
                              "repo_url":"https://github.com/reallakshman19/Common"}],
                "server": {"evidence_index_path":str(db)}
            }
            BoundHandler.server_host = "127.0.0.1"
            with socketserver.TCPServer(("127.0.0.1", 0), BoundHandler) as httpd:
                thread = threading.Thread(target=httpd.serve_forever, daemon=True)
                thread.start()
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{httpd.server_address[1]}/api/v3/snapshot",
                        timeout=5
                    ) as response:
                        snap = json.load(response)
                    self.assertEqual(snap["visibility"], "INTERNAL")
                    self.assertEqual([p["provider_reachability"] for p in snap["projects"]],
                                     ["UNKNOWN", "UNKNOWN"])
                    self.assertEqual([p["as_of"] for p in snap["projects"]], [None, None])
                    self.assertFalse(db.exists())
                finally:
                    httpd.shutdown()
                    thread.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
