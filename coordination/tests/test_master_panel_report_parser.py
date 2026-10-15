"""M1-U03 synthetic CASP metadata/identity privacy tests.

This validates source parsing, NOT message authentication, product acceptance,
AgentRun registration, authenticated coordinator delivery or real SEND.
"""
import json
import tempfile
import unittest
from pathlib import Path

from coordination.master_panel.models import SourceIdentity, SourceKind
from coordination.master_panel.report_parser import extract_report
from coordination.master_panel.read_api import MasterReadService
from coordination.master_panel.storage import SourceStore


REPO = "reallakshman19/Common"
ISSUE = 373
STAMP = "2026-10-14T01:00:00Z"


def source(body: str, stamp: str = STAMP):
    import hashlib
    return SourceIdentity(
        project_id="common", repo_id="1412133785",
        repo_full_name=REPO, kind=SourceKind.ISSUE_COMMENT,
        entity_id="999", revision_id=stamp,
        issue_number=ISSUE, comment_id="999",
        body_sha256=hashlib.sha256(body.encode()).hexdigest(),
        created_at_utc=STAMP, updated_at_utc=stamp,
        url=f"https://github.com/{REPO}/issues/{ISSUE}#issuecomment-999",
    )


def envelope(**overrides):
    base = {
        "protocol_version": "1.0.0",
        "message_id": "synthetic-message-01",
        "request_id": "synthetic-request-01",
        "kind": "RESULT",
        "sender_id": "synthetic-agent",
        "status": "REPORTED",
        "target": {
            "project_id": "common",
            "work_id": "common-360-dash-master", "lane_id": "m1",
            "assignment_id": "dash-master-m1", "run_id": "dash-r2",
        },
        "repository": {"id": "1412133785", "name": REPO},
        "mailbox": {
            "repository": {"id": "1412133785", "name": REPO},
            "issue_number": ISSUE, "visibility": "PUBLIC",
        },
        "basis": {"candidate": "a"*40},
        "payload": {
            "text": "SYNTHETIC PRIVATE HUMAN PROSE NOT PUBLIC",
            "refs": ["https://chatgpt.com/c/private"],
            "decision": None,
        },
    }
    base.update(overrides)
    return "public note\n```casp\n" + json.dumps(base) + "\n```\n"


class TestCASPSourceClaims(unittest.TestCase):
    def test_exact_scoped_identity_and_no_free_text(self):
        body = envelope()
        claim = extract_report(body, source(body))
        self.assertEqual(claim["work_id"], "common-360-dash-master")
        self.assertEqual(claim["reported_status"], "REPORTED")
        self.assertEqual(claim["kind"], "RESULT")
        self.assertEqual(claim["assignment_id"], "dash-master-m1")
        exported = json.dumps(claim)
        self.assertNotIn("PRIVATE HUMAN PROSE", exported)
        self.assertNotIn("chatgpt.com", exported)
        self.assertNotIn("Owner", exported)

    def test_wrong_repo_issue_project_and_ambiguous_fences_rejected(self):
        good = envelope()
        cases = [
            good+good,
            envelope(repository={"id": "1363905693", "name": "reallakshman19/AA3"}),
            envelope(mailbox={"repository": {"id": "1412133785", "name": REPO},
                              "issue_number": 374, "visibility": "PUBLIC"}),
            envelope(target={"project_id": "aa3", "work_id": "common-360-dash-master",
                             "lane_id": "m1", "assignment_id": "dash-master-m1",
                             "run_id": "dash-r2"}),
            envelope(message_id="hostile?message"),
            envelope(protocol_version="99.0.0"),
            "```casp\n{this is not JSON}\n```",
        ]
        for body in cases:
            with self.subTest(body=body[-64:]):
                self.assertIsNone(extract_report(body, source(body)))

    def test_source_claim_is_not_registered_agent(self):
        tmp = tempfile.TemporaryDirectory()
        path = str(Path(tmp.name) / "ledger.sqlite")
        store = SourceStore(path)
        try:
            body = envelope()
            candidate = source(body)
            claim = extract_report(body, candidate)
            self.assertEqual(store.observe(candidate, "scan-a", claim), "NEW")
            store.save_scan(
                project_id="common", repo_id="1412133785",
                scan_id="scan-a", issue_page=1, issue_index=1, comment_page=1,
                status="REACHABLE", completed=True,
            )
            service = MasterReadService(path)
            row = service.rows("common")["items"][0]
            self.assertEqual(row["report"]["reported_work_id"],
                             "common-360-dash-master")
            self.assertEqual(row["report"]["reported_assignment_id"], "dash-master-m1")
            self.assertEqual(row["binding"]["state"], "UNASSIGNED")
            self.assertEqual(row["evidence"]["review_verdict"], "UNKNOWN")
            self.assertNotIn("PRIVATE HUMAN PROSE", json.dumps(row))
            self.assertNotIn("chatgpt.com", json.dumps(row))
            # Same object gets a new reported kind only on the next edit.
            newer = "2026-10-14T01:01:00Z"
            body2 = envelope(kind="ACK", status="RECEIVED")
            self.assertEqual(store.observe(source(body2, newer), "scan-b",
                                           extract_report(body2, source(body2, newer))),
                             "EDITED")
            current = service.rows("common")["items"][0]
            self.assertEqual(current["report"]["kind"], "ACK")
            self.assertEqual(len(store.revisions(
                "common", "1412133785", "ISSUE_COMMENT", "999"
            )), 2)
        finally:
            store.close()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
