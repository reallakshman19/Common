"""M1-U03 fixture-profile tests for the read-only loopback seam.

Run: python -m unittest coordination.tests.test_master_panel_read_api -v
No real private command source or installed browser is exercised here.
"""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from pathlib import Path

from coordination.master_panel.models import SourceIdentity, SourceKind
from coordination.master_panel.read_api import MasterPanelHandler, MasterReadService
from coordination.master_panel.storage import SourceStore


STAMP = "2026-10-14T01:00:00Z"
REPO = "reallakshman19/Common"
REPO_ID = "1412133785"


def source(identifier: str, body: str) -> SourceIdentity:
    import hashlib
    return SourceIdentity(
        project_id="common", repo_id=REPO_ID, repo_full_name=REPO,
        kind=SourceKind.ISSUE_COMMENT, entity_id=identifier,
        revision_id=STAMP, issue_number=373, comment_id=identifier,
        body_sha256=hashlib.sha256(body.encode()).hexdigest(),
        created_at_utc=STAMP, updated_at_utc=STAMP,
        url=f"https://github.com/{REPO}/issues/373#issuecomment-{identifier}",
    )


class TestMasterPanelReadAPI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = str(Path(self.tmp.name) / "ledger.sqlite")
        self.writer = SourceStore(self.file)
        self.writer.observe(source("1001", "PRIVATE BODY NOT FOR PUBLIC API"), "scan-a")
        self.writer.observe(source("1002", "PRIVATE BODY B"), "scan-a")
        self.writer.save_scan(
            project_id="common", repo_id=REPO_ID, scan_id="scan-a",
            issue_page=1, issue_index=1, comment_page=1,
            status="REACHABLE", completed=True,
        )
        self.service = MasterReadService(self.file)

    def tearDown(self):
        self.writer.close()
        self.tmp.cleanup()

    def test_projects_sources_unknown_not_zero(self):
        projects = self.service.projects()
        by_id = {p["project_id"]: p for p in projects["projects"]}
        self.assertEqual(set(by_id), {"common", "aa3"})
        self.assertEqual(by_id["aa3"]["source_state"], "UNKNOWN")
        self.assertEqual(by_id["common"]["source_state"], "REACHABLE")
        sources = self.service.sources()
        self.assertEqual(len(sources["sources"]), 2)
        aa3 = next(s for s in sources["sources"] if s["project_id"] == "aa3")
        self.assertEqual(aa3["state"], "UNKNOWN")
        self.assertIsNone(aa3["completed_at_utc"])
        self.assertEqual(aa3["freshness"], "UNKNOWN")

    def test_rows_private_body_suppressed_and_reviews_not_inferred(self):
        response = self.service.rows("common")
        self.assertEqual(response["schema_version"], "1.0.0")
        self.assertEqual(len(response["items"]), 2)
        row = response["items"][0]
        self.assertEqual(row["binding"]["state"], "UNASSIGNED")
        self.assertEqual(row["coordinator_observation"]["liveness"], "UNKNOWN")
        self.assertEqual(row["evidence"]["reported_verdict"], "UNKNOWN")
        self.assertEqual(row["evidence"]["review_verdict"], "UNKNOWN")
        self.assertEqual(row["absence"], "PRESENT")
        serialized = json.dumps(response)
        self.assertNotIn("PRIVATE BODY", serialized)
        self.assertNotIn("token", serialized.lower())
        self.assertNotIn("chat_url", serialized)

    def test_cursor_is_scope_and_generation_bound(self):
        one = self.service.rows("common", limit=1)
        self.assertTrue(one["has_more"])
        cursor = one["next_cursor"]
        second = self.service.rows("common", limit=1, cursor=cursor)
        self.assertNotEqual(
            one["items"][0]["source"]["entity_id"],
            second["items"][0]["source"]["entity_id"],
        )
        with self.assertRaisesRegex(ValueError, "Invalid cursor"):
            self.service.rows("common", limit=1, cursor="%invalid")
        with self.assertRaisesRegex(ValueError, "Unregistered"):
            self.service.rows("unknown", limit=1)
        self.writer.observe(
            source("1003", "PRIVATE BODY C"), "scan-a"
        )
        with self.assertRaisesRegex(LookupError, "Expired"):
            self.service.rows("common", limit=1, cursor=cursor)

    def test_injected_independent_review_requires_source(self):
        key = source("1001", "PRIVATE").stable_key
        bad = MasterReadService(self.file, reviews={key: {
            "review_verdict": "PASS",
        }})
        with self.assertRaisesRegex(ValueError, "independently"):
            bad.rows("common")
        good = MasterReadService(self.file, reviews={key: {
            "review_verdict": "PASS",
            "review_ref": f"https://github.com/{REPO}/issues/375#issuecomment-222",
            "review_candidate_sha": "1"*40,
        }}, current_heads={key: "2"*40})
        row = next(x for x in good.rows("common")["items"]
                   if x["source"]["entity_id"] == "1001")
        self.assertEqual(row["evidence"]["review_verdict"], "PASS")
        self.assertEqual(row["evidence"]["candidate_relation"], "OLD_HEAD")
        self.assertNotEqual(row["evidence"]["candidate_relation"], "CURRENT")

    def test_missing_ledger_refuses_instead_of_empty_success(self):
        with self.assertRaises(FileNotFoundError):
            MasterReadService(str(Path(self.tmp.name)/"absent.sqlite")).projects()

    def test_loopback_http_host_origin_and_no_cors(self):
        service = self.service

        class Handler(MasterPanelHandler):
            pass

        Handler.service = service
        server = HTTPServer(("127.0.0.1", 0), Handler)
        thr = threading.Thread(target=server.serve_forever, daemon=True)
        thr.start()
        base = f"http://127.0.0.1:{server.server_port}"
        def request(path: str, headers=None):
            req = urllib.request.Request(base + path, headers=headers or {})
            try:
                with urllib.request.urlopen(req, timeout=3) as response:
                    return response.status, dict(response.headers), response.read()
            except urllib.error.HTTPError as error:
                return error.code, dict(error.headers), error.read()
        try:
            status, headers, body = request("/api/master/v1/projects")
            self.assertEqual(status, 200)
            self.assertNotIn("Access-Control-Allow-Origin", headers)
            self.assertEqual(json.loads(body)["schema_version"], "1.0.0")
            self.assertEqual(request(
                "/api/master/v1/projects", {"Host": "evil.example"}
            )[0], 400)
            self.assertEqual(request(
                "/api/master/v1/projects", {"Origin": "https://evil.example"}
            )[0], 403)
            self.assertEqual(request("/api/master/v1/rows?project_id=aa3")[0], 200)
            self.assertEqual(request("/api/master/v1/rows?project_id=forbidden")[0], 400)
        finally:
            server.shutdown()
            server.server_close()
            thr.join(timeout=3)


if __name__ == "__main__":
    unittest.main()
