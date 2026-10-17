"""V36-ECO-02: read model over the native snapshot (A14 SELF-CHECK, provenance, pending)."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import decompose_v36 as dc
import lifecycle_v36 as lc
import readmodel_v36 as rm

LABEL = lc.load_label(ROOT / "tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT / "plans/V36-341-PLAN-02.yaml", LABEL)
HEAD = "11b17586e7a14c4be90cca46cb4a2193804cd59e"
OLD = "46071cbc695226a3ba29f2c53f64a0103102302d"
NOW = "2026-10-17T12:00:00+04:00"
ISSUE = {"number": 345, "title": "V36-341-WP1", "state": "open",
         "body": "**Parent:** #341 · **Task:** V36-341-WP1 · **Size:** S",
         "html_url": "https://github.com/reallakshman19/Common/issues/345"}
SC_ID = 9001
SC_URL = "https://github.com/reallakshman19/Common/issues/345#issuecomment-%d" % SC_ID


def evidence(sha=HEAD, link=True):
    user = "A usable lifecycle plan exists" + (" Self-check: " + SC_URL if link else "")
    return lc.render_evidence(
        outcome="O1", for_user=user,
        proof="https://github.com/reallakshman19/Common/pull/344/commits/" + sha,
        task_id="V36-341-WP1", issue_ref="reallakshman19/Common#345",
        candidate="reallakshman19/Common@" + sha, tests_passed=16, tests_run=16)


def self_check(sha=HEAD, states=("MET", "MET"), pending="", claim="DONE", extra=""):
    lines = ["SELF-CHECK v1 · V36-341-WP1 · reallakshman19/Common#345",
             "Basis: plan V36-341-PLAN-02; candidate reallakshman19/Common@%s; source fixtures" % sha]
    lines += ["Done-when: criterion %d → %s proof" % (i, s) for i, s in enumerate(states)]
    if pending:
        lines.append(pending)
    lines += ["Proposed claim: %s · reason none" % claim, extra]
    return "\n".join(lines)


def comment(cid, body, login="reallakshman19"):
    return {"id": cid, "body": body, "user": {"login": login},
            "html_url": "https://github.com/reallakshman19/Common/issues/345#issuecomment-%d" % cid,
            "updated_at": "2026-10-17T07:00:00Z", "created_at": "2026-10-17T07:%02dZ" % (cid % 60)}


class Provider:
    repo = "reallakshman19/Common"
    def __init__(self, comments, fail=False):
        self.comments, self.fail, self.reads = comments, fail, 0
    def list_issues(self): return [ISSUE]
    def list_comments(self, n):
        self.reads += 1
        if self.fail: raise lc.ContractError("provider down")
        return self.comments if n == 345 else []
    def get_pr(self, n): return {"head": {"sha": HEAD}, "draft": True}


def run(comments, **kw):
    p = Provider(comments, **kw)
    return rm.read_model(PLAN, p, NOW), p


class ReadModelTests(unittest.TestCase):
    def test_qualified_claim_is_not_acceptance(self):
        r, p = run([comment(SC_ID, self_check()), comment(9002, evidence())])
        t = r["tasks"][0]
        self.assertTrue(t["claim_qualified"], t["reasons"])
        self.assertEqual(t["acceptance"], "NOT_EVALUATED")
        self.assertEqual(r["acceptance"], "NOT_EVALUATED")
        self.assertEqual(r["native"]["verified_complete"], 0)
        self.assertEqual(r["claims_qualified"], 1)
        self.assertTrue(t["self_check_matches_candidate"])

    def test_one_read_per_issue(self):
        _, p = run([comment(SC_ID, self_check()), comment(9002, evidence())])
        self.assertEqual(p.reads, 1)

    def test_missing_self_check(self):
        t = run([comment(9002, evidence(link=False))])[0]["tasks"][0]
        self.assertFalse(t["claim_qualified"])
        self.assertIn("no SELF-CHECK v1 companion found", t["reasons"])

    def test_unlinked_or_wrong_link(self):
        t = run([comment(SC_ID, self_check()), comment(9002, evidence(link=False))])[0]["tasks"][0]
        self.assertIn("evidence does not link the self-check on its For the user line", t["reasons"])
        t = run([comment(SC_ID, self_check()), comment(9003, self_check()), comment(9002, evidence())])[0]["tasks"][0]
        self.assertIn("evidence links a different comment than the latest self-check", t["reasons"])

    def test_not_met_and_blocking_pending(self):
        pend = "Pending: P1 fix · owner OTM · next run · unblocks merge · prevents task DONE yes"
        t = run([comment(SC_ID, self_check(states=("MET", "NOT_RUN"), pending=pend)),
                 comment(9002, evidence())])[0]["tasks"][0]
        self.assertIn("done-when not all MET", t["reasons"])
        self.assertIn("pending item prevents DONE", t["reasons"])

    def test_pending_pooled_for_coordinator(self):
        pend = "Pending: P2 reuse decision · owner OTM · next ECO-02 · unblocks ECO-02 · prevents task DONE no"
        r = run([comment(SC_ID, self_check(pending=pend)), comment(9002, evidence())])[0]
        self.assertEqual(r["pending"], [{"task_id": "V36-341-WP1", "source": SC_URL, "what": "P2 reuse decision",
                                         "owner": "OTM", "next": "ECO-02", "unblocks": "ECO-02",
                                         "prevents_done": False}])
        self.assertTrue(r["tasks"][0]["claim_qualified"])

    def test_candidate_mismatch(self):
        t = run([comment(SC_ID, self_check(sha=OLD)), comment(9002, evidence())])[0]["tasks"][0]
        self.assertFalse(t["self_check_matches_candidate"])
        self.assertIn("self-check candidate differs from native evidence candidate", t["reasons"])

    def test_companion_with_canonical_marker_rejected(self):
        t = run([comment(SC_ID, self_check(extra="quoted TASK_EVIDENCE v3.6")), comment(9002, evidence())])[0]["tasks"][0]
        self.assertEqual(t["self_check"]["status"], "REJECTED_CONTAINS_CANONICAL_MARKER")
        self.assertFalse(t["claim_qualified"])

    def test_foreign_author_rejected(self):
        t = run([comment(SC_ID, self_check(), login="someone"), comment(9002, evidence())])[0]["tasks"][0]
        self.assertEqual(t["self_check"]["status"], "REJECTED_FOREIGN_AUTHOR")

    def test_stale_evidence_not_qualified(self):
        t = run([comment(SC_ID, self_check(sha=OLD)), comment(9002, evidence(sha=OLD))])[0]["tasks"][0]
        self.assertEqual(t["status"], "STALE_EVIDENCE")
        self.assertIn("native evidence STALE_EVIDENCE", t["reasons"])

    def test_provider_failure_is_incomplete_not_zero(self):
        r = run([], fail=True)[0]
        self.assertFalse(r["read_complete"])
        self.assertEqual(r["unread_sources"], ["345"])
        self.assertEqual(r["tasks"][0]["status"], "PROVIDER_UNAVAILABLE")

    def test_provenance_digest_and_history(self):
        r = run([comment(SC_ID, self_check()), comment(9002, evidence())])[0]
        t = r["tasks"][0]
        self.assertEqual(len(t["self_check"]["body_sha256"]), 64)
        self.assertEqual(t["self_check_history"], 1)
        self.assertEqual({s["comment_id"] for s in t["sources_read"]}, {SC_ID, 9002})

    def test_link_must_target_this_repo_and_issue(self):
        for url in ("https://github.com/reallakshman19/Common/issues/999#issuecomment-%d" % SC_ID,
                    "https://github.com/other/repo/issues/345#issuecomment-%d" % SC_ID):
            body = evidence(link=False).replace("A usable lifecycle plan exists",
                                                "A usable lifecycle plan exists Self-check: " + url, 1)
            t = run([comment(SC_ID, self_check()), comment(9002, body)])[0]["tasks"][0]
            self.assertIn("evidence does not link the self-check on its For the user line", t["reasons"])

    def test_pr_read_failure_is_incomplete(self):
        class PrDown(Provider):
            def get_pr(self, n): raise lc.ContractError("pr down")
        r = rm.read_model(PLAN, PrDown([comment(SC_ID, self_check()), comment(9002, evidence())]), NOW)
        self.assertFalse(r["read_complete"])
        self.assertIn("pr:344", r["unread_sources"])

    def test_latest_self_check_by_created_at(self):
        older = comment(SC_ID, self_check(claim="PARTIAL")); older["created_at"] = "2026-10-17T06:00Z"
        newer = comment(9010, self_check()); newer["created_at"] = "2026-10-17T08:00Z"
        t = run([newer, older, comment(9002, evidence())])[0]["tasks"][0]
        self.assertEqual(t["self_check"]["comment_id"], 9010)

    def test_now_requires_timezone(self):
        with self.assertRaises(ValueError):
            rm.read_model(PLAN, Provider([]), "2026-10-17T12:00:00")

    def test_native_evidence_still_validates_with_inline_link(self):
        self.assertEqual(lc.validate_evidence(evidence())["task_id"], "V36-341-WP1")


if __name__ == "__main__":
    unittest.main()
