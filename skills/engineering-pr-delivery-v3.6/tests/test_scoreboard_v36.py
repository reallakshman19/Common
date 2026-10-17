"""V36-ECO-03: read-only scoreboard over the read model (independent E/A/V/acceptance, dry-run)."""
import json
import unittest

import lifecycle_v36 as lc
import readmodel_v36 as rm
import scoreboard_v36 as sb
from test_readmodel_v36 import OLD, PLAN, NOW, SC_ID, Provider, comment, evidence, run, self_check

BLOCK = "Pending: P1 fix · owner OTM · next run checker · unblocks merge · prevents task DONE yes"


def board(comments, **kw):
    return sb.board(run(comments, **kw)[0])


class ScoreboardTests(unittest.TestCase):
    def test_qualified_claim_is_never_acceptance(self):
        b = board([comment(SC_ID, self_check()), comment(9002, evidence())])
        r = b["rows"][0]
        self.assertTrue(r["claim_qualified"])
        for key in ("A", "V", "acceptance"):
            self.assertTrue(b[key].startswith("NOT_EVALUATED"), key)
            self.assertTrue(r[key].startswith("NOT_EVALUATED"), key)
        self.assertEqual(r["next"]["actor"], "coordinator")
        self.assertNotIn("ACCEPTED", json.dumps(b).upper())

    def test_denominator_is_this_plans_tasks(self):
        t = board([comment(SC_ID, self_check()), comment(9002, evidence())])["totals"]
        self.assertEqual((t["tasks"], t["E_current"], t["native_total_matches"]), (len(PLAN["tasks"]), 1, True))

    def test_stale_head_and_its_next_step(self):
        r = board([comment(SC_ID, self_check(sha=OLD)), comment(9002, evidence(sha=OLD))])["rows"][0]
        self.assertEqual(r["E"], "STALE_EVIDENCE")
        self.assertEqual(r["next"]["action"], "publish current evidence")

    def test_blocking_pending_names_its_owner_and_action(self):
        r = board([comment(SC_ID, self_check(pending=BLOCK)), comment(9002, evidence())])["rows"][0]
        self.assertEqual((r["next"]["actor"], r["next"]["action"]), ("OTM", "run checker"))
        self.assertIn("pending item prevents DONE", r["gaps"])

    def test_incomplete_provider_data_is_marked_partial(self):
        b = board([], fail=True)
        self.assertTrue(b["totals"]["partial"])
        self.assertEqual(b["rows"][0]["next"]["action"], "re-read the unavailable source")
        self.assertIn("**INCOMPLETE READ** - unread: 345", sb.render_markdown(b))

        class IssuesDown(Provider):
            def list_issues(self): raise lc.ContractError("down")
        b = sb.board(rm.read_model(PLAN, IssuesDown([]), NOW))
        self.assertEqual((b["rows"], b["totals"]["partial"]), ([], True))

    def test_missing_child_issue(self):
        class NoIssues(Provider):
            def list_issues(self): return []
        r = sb.board(rm.read_model(PLAN, NoIssues([]), NOW))["rows"][0]
        self.assertEqual((r["E"], r["next"]["action"]), ("MISSING_CHILD", "resolve the task's one child issue"))

    def test_unknowns_are_explicit_and_age_is_from_sources(self):
        r = board([comment(SC_ID, self_check()), comment(9002, evidence())])["rows"][0]
        self.assertTrue(r["user_outcome"].startswith("UNKNOWN"))
        self.assertEqual(r["source_age_minutes"], 60)        # sources 07:00Z, observed 08:00Z

    def test_markdown_is_managed_region_only_and_escaped(self):
        b = board([comment(SC_ID, self_check(pending=BLOCK.replace("P1 fix", "P1 a|b"))), comment(9002, evidence())])
        md = sb.render_markdown(b)
        self.assertTrue(md.startswith(sb.MANAGED_BEGIN) and md.endswith(sb.MANAGED_END))
        self.assertIn(sb.TITLE_NOTE, md)
        self.assertEqual(md.count("\n| V36-341-WP1 |"), 1)

    def test_rejects_other_documents(self):
        with self.assertRaises(ValueError):
            sb.board({"schema": "v36.snapshot"})


if __name__ == "__main__":
    unittest.main()
