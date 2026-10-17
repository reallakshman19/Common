"""V36-ECO-02b: observed head, history cursor, Owner-input attribution, issue hops, P3 hardening."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_readmodel_v36 import (HEAD, ISSUE, NOW, OLD, PLAN, SC_ID, Provider, comment, evidence,
                                self_check)
import lifecycle_v36 as lc
import readmodel_v36 as rm

LATER = "2026-10-17T13:00:00+04:00"


def good():
    return [comment(SC_ID, self_check()), comment(9002, evidence())]


class HttpError(lc.ContractError):
    def __init__(self, code):
        super().__init__("HTTP %d" % code)
        self.code = code


class HopProvider(Provider):
    def __init__(self, comments, issues, extra):
        super().__init__(comments)
        self.issues, self.extra = issues, extra
    def list_issues(self): return self.issues
    def get_issue(self, n):
        v = self.extra.get(n)
        if isinstance(v, Exception):
            raise v
        if v is None:
            raise HttpError(404)
        return v


class ObservedHeadTests(unittest.TestCase):
    def test_head_emitted_next_to_candidate(self):
        t = rm.read_model(PLAN, Provider(good()), NOW)["tasks"][0]
        self.assertEqual((t["observed_head"], t["candidate_sha"], t["head_matches_candidate"]), (HEAD, HEAD, True))

    def test_head_mismatch_flagged(self):
        class Moved(Provider):
            def get_pr(self, n): return {"head": {"sha": OLD}}
        t = rm.read_model(PLAN, Moved(good()), NOW)["tasks"][0]
        self.assertEqual((t["observed_head"], t["head_matches_candidate"]), (OLD, False))
        self.assertFalse(t["claim_qualified"])
        self.assertIn("observed PR head %s differs from candidate %s" % (OLD, HEAD), t["reasons"])

    def test_head_unknown_when_pr_unread(self):
        class PrDown(Provider):
            def get_pr(self, n): raise lc.ContractError("down")
        t = rm.read_model(PLAN, PrDown(good()), NOW)["tasks"][0]
        self.assertEqual((t["observed_head"], t["head_matches_candidate"]), (None, None))


class CursorTests(unittest.TestCase):
    def test_cursor_records_digest_updated_and_read_time(self):
        r = rm.read_model(PLAN, Provider(good()), NOW)
        c = r["source_cursor"]["comment:%d" % SC_ID]
        self.assertEqual((len(c["body_sha256"]), c["updated_at"], c["read_at"], c["status"]),
                         (64, "2026-10-17T07:00:00Z", NOW, "READ"))
        self.assertEqual(r["cursor"]["last_complete_read_at"], NOW)
        self.assertEqual(len(r["source_history"]["comment:%d" % SC_ID]), 1)

    def test_edit_appends_history_and_fails_closed(self):
        first = rm.read_model(PLAN, Provider(good()), NOW)
        edited = good()
        edited[0]["body"] = self_check() + "\nTests: edited later"
        edited[0]["updated_at"] = "2026-10-17T08:30:00Z"
        r = rm.read_model(PLAN, Provider(edited), LATER, prior=first)
        key = "comment:%d" % SC_ID
        hist = r["source_history"][key]
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[0], first["source_history"][key][0])        # earlier read not rewritten
        self.assertEqual(hist[1]["first_read_at"], LATER)
        self.assertIn(key, r["edited_sources"])
        t = r["tasks"][0]
        self.assertFalse(t["claim_qualified"])
        self.assertIn("source edited since prior read: " + key, t["reasons"])
        self.assertEqual(first["source_history"][key][0]["first_read_at"], NOW)   # prior object untouched

    def test_unchanged_source_keeps_one_revision(self):
        first = rm.read_model(PLAN, Provider(good()), NOW)
        r = rm.read_model(PLAN, Provider(good()), LATER, prior=first)
        self.assertEqual(r["edited_sources"], [])
        self.assertEqual(len(r["source_history"]["comment:%d" % SC_ID]), 1)
        self.assertTrue(r["tasks"][0]["claim_qualified"])

    def test_partial_failure_keeps_prior_cursor_truthful(self):
        first = rm.read_model(PLAN, Provider(good()), NOW)
        r = rm.read_model(PLAN, Provider(good(), fail=True), LATER, prior=first)
        c = r["source_cursor"]["comment:%d" % SC_ID]
        self.assertEqual((c["read_at"], c["status"]), (NOW, "UNREAD_KEEPING_PRIOR"))
        self.assertEqual(r["cursor"]["last_complete_read_at"], NOW)
        self.assertFalse(r["read_complete"])

    def test_missing_since_prior_is_not_deletion(self):
        first = rm.read_model(PLAN, Provider(good()), NOW)
        r = rm.read_model(PLAN, Provider(good()[1:]), LATER, prior=first)
        self.assertEqual(r["source_cursor"]["comment:%d" % SC_ID]["status"], "MISSING_SINCE_PRIOR")

    def test_no_prior_complete_read_is_unknown(self):
        r = rm.read_model(PLAN, Provider([], fail=True), NOW)
        self.assertIsNone(r["cursor"]["last_complete_read_at"])


class AttributionTests(unittest.TestCase):
    def test_input_golden_benchmark_reported_or_unknown(self):
        t = rm.read_model(PLAN, Provider(good()), NOW)["tasks"][0]
        self.assertEqual(t["inputs"], {"input": "UNKNOWN", "golden": "UNKNOWN", "benchmark": "UNKNOWN",
                                       "attribution": "REPORTED_BY_AUTHOR"})
        sc = self_check().replace("source fixtures", "source fixtures input COMPLETE golden MISSING benchmark NOT_APPLICABLE")
        t = rm.read_model(PLAN, Provider([comment(SC_ID, sc), comment(9002, evidence())]), NOW)["tasks"][0]
        self.assertEqual((t["inputs"]["input"], t["inputs"]["golden"], t["inputs"]["benchmark"]),
                         ("COMPLETE", "MISSING", "NOT_APPLICABLE"))

    def test_owner_account_quote_and_hash_are_reported_not_authenticated(self):
        extra = [comment(9020, "Approved, go ahead"),
                 comment(9021, "> Owner: approved\nnoted", login="helper"),
                 comment(9022, "caller_sha256: " + "a" * 64, login="bot")]
        for c in extra:
            c["created_at"] = "2026-10-17T06:00Z"
        t = rm.read_model(PLAN, Provider(extra + good()), NOW)["tasks"][0]
        kinds = {o["comment_id"]: o["kind"] for o in t["owner_inputs"]}
        self.assertEqual(kinds, {9020: "GITHUB_ACCOUNT", 9021: "QUOTED_TEXT", 9022: "CALLER_HASH"})
        for o in t["owner_inputs"]:
            self.assertEqual((o["attribution"], o["authenticated_human_approval"]), ("REPORTED", False))


class HopTests(unittest.TestCase):
    def old(self, n, body):
        return {"number": n, "title": "old", "state": "closed", "body": body,
                "html_url": "https://github.com/reallakshman19/Common/issues/%d" % n}

    def test_hops_kept_with_reason_and_source(self):
        issue = {**ISSUE, "body": ISSUE["body"] + "\nSuperseded by #350: scope split"}
        nxt = self.old(350, "Superseded by #351 — renamed")
        p = HopProvider(good(), [issue, nxt], {351: self.old(351, "final")})
        hops = rm.read_model(PLAN, p, NOW)["tasks"][0]["issue_hops"]
        self.assertEqual([(h["from"], h["to"], h["reason"], h["status"]) for h in hops],
                         [(345, 350, "scope split", "FOUND"), (350, 351, "renamed", "FOUND")])
        self.assertEqual(hops[0]["source"], ISSUE["html_url"])

    def test_404_is_inaccessible_and_410_is_verified_deleted(self):
        for target, status in ((None, "NOT_FOUND_OR_INACCESSIBLE"), (HttpError(403), "NOT_FOUND_OR_INACCESSIBLE"),
                               (HttpError(410), "VERIFIED_DELETED"), (OSError("x"), "UNREAD")):
            issue = {**ISSUE, "body": ISSUE["body"] + "\nSuperseded by #360: moved"}
            p = HopProvider(good(), [issue], {360: target})
            hops = rm.read_model(PLAN, p, NOW)["tasks"][0]["issue_hops"]
            self.assertEqual(hops[-1]["status"], status, target)

    def test_hop_cycle_stops(self):
        issue = {**ISSUE, "body": ISSUE["body"] + "\nSuperseded by #350: a"}
        p = HopProvider(good(), [issue, self.old(350, "Superseded by #345: b")], {})
        hops = rm.read_model(PLAN, p, NOW)["tasks"][0]["issue_hops"]
        self.assertEqual(hops[-1]["status"], "CYCLE")

    def test_failed_hop_fetch_does_not_advance_cursor(self):
        first = rm.read_model(PLAN, Provider(good()), NOW)
        issue = {**ISSUE, "body": ISSUE["body"] + "\nSuperseded by #360: moved"}
        r = rm.read_model(PLAN, HopProvider(good(), [issue], {360: OSError("x")}), LATER, prior=first)
        self.assertEqual((r["read_complete"], r["unread_sources"]), (False, ["issue:360"]))
        self.assertEqual(r["cursor"]["last_complete_read_at"], NOW)

    def test_fetched_hop_with_other_number_is_mismatched(self):
        issue = {**ISSUE, "body": ISSUE["body"] + "\nSuperseded by #360: moved"}
        r = rm.read_model(PLAN, HopProvider(good(), [issue], {360: self.old(361, "x")}), NOW)
        self.assertEqual(r["tasks"][0]["issue_hops"][-1]["status"], "MISMATCHED")
        self.assertIn("issue:360", r["unread_sources"])


class HardeningTests(unittest.TestCase):
    def test_huge_int_ids_are_unread_not_crash(self):
        sc = comment(SC_ID, self_check()); sc["id"] = 10 ** 5000
        r = rm.read_model(PLAN, Provider([sc, comment(9002, evidence())]), NOW)
        self.assertEqual((r["read_complete"], r["unread_sources"]), (False, ["345"]))
        class HugeIssue(Provider):
            def list_issues(self): return [{**ISSUE, "number": 10 ** 5000}]
        r = rm.read_model(PLAN, HugeIssue([]), NOW)
        self.assertEqual((r["read_complete"], r["unread_sources"]), (False, ["issues"]))

    def test_link_form_reason_is_specific(self):
        url = "https://github.com/reallakshman19/Common/pull/345#issuecomment-%d" % SC_ID
        body = evidence().replace("Self-check: https://github.com/reallakshman19/Common/issues/345#issuecomment-%d" % SC_ID,
                                  "Self-check: " + url)
        t = rm.read_model(PLAN, Provider([comment(SC_ID, self_check()), comment(9002, body)]), NOW)["tasks"][0]
        self.assertIn("evidence Self-check link form not recognised (expected "
                      "https://github.com/<owner>/<repo>/issues/<n>#issuecomment-<id>)", t["reasons"])
        other = evidence().replace("/issues/345#", "/issues/999#")
        t = rm.read_model(PLAN, Provider([comment(SC_ID, self_check()), comment(9002, other)]), NOW)["tasks"][0]
        self.assertIn("evidence Self-check link targets reallakshman19/Common#999, not this child issue", t["reasons"])


if __name__ == "__main__":
    unittest.main()
