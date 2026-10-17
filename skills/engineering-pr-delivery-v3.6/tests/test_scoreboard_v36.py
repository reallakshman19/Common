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


    def test_audit_unadmitted_chain_reports_eleven_categories_without_a100(self):
        b = board([comment(SC_ID, self_check()), comment(9002, evidence())])
        self.assertEqual(b["A_detail"]["status"], "NOT_EVALUATED")
        self.assertEqual(len(b["A_detail"]["required_categories"]), 11)
        self.assertIsNone(b["A_detail"]["accounted"])
        self.assertIsNone(b["A_detail"]["attested"])
        self.assertIn("#401", b["A_detail"]["reason"])
        self.assertNotIn("A100%", sb.render_markdown(b))

    def test_originals_scope_source_revision_and_heads_are_disclosed(self):
        r = board([comment(SC_ID, self_check()), comment(9002, evidence())])["rows"][0]
        self.assertEqual(r["observed_head"], rm.HEAD if hasattr(rm, "HEAD") else __import__("test_readmodel_v36").HEAD)
        self.assertEqual(r["candidate_sha"], r["observed_head"])
        self.assertEqual(r["original_input"]["input"], "UNKNOWN")
        self.assertEqual(r["original_input"]["attribution"], "REPORTED_BY_AUTHOR")
        self.assertIn("UNKNOWN", r["user_outcome"])
        self.assertIn("UNKNOWN", r["implementation_crux"])
        self.assertEqual(r["verification_scope"]["run_verified"], "NOT_EVALUATED")
        self.assertEqual(len(r["source_revisions"]), 2)
        self.assertTrue(all(s["body_sha256"] for s in r["source_revisions"]))

    def test_child_and_pr_denominators_not_borrowed_from_parent(self):
        b = board([comment(SC_ID, self_check()), comment(9002, evidence())])
        pr = "https://github.com/reallakshman19/Common/pull/344"
        issue = "https://github.com/reallakshman19/Common/issues/345"
        self.assertEqual(b["by_pr"][pr]["tasks"], 1)
        self.assertEqual(b["by_pr"][pr]["E_current"], 1)
        self.assertEqual(b["by_child"][issue]["tasks"], 1)
        self.assertEqual(b["by_child"][issue]["E_current"], 1)
        self.assertEqual(b["rows"][0]["pr_denominator"], 1)
        self.assertEqual(b["rows"][0]["child_denominator"], 1)

    def test_foreign_issue_cannot_be_counted_as_trusted_linkage(self):
        import copy
        m = run([comment(SC_ID, self_check()), comment(9002, evidence())])[0]
        m = copy.deepcopy(m)
        m["tasks"][0]["issue"] = "https://github.com/mallory/foreign/issues/345"
        b = sb.board(m)
        self.assertEqual(b["rows"][0]["E"], "SOURCE_MISMATCH")
        self.assertEqual(b["totals"]["E_current"], 0)
        self.assertFalse(b["by_child"])
        self.assertFalse(b["by_pr"])
        self.assertIn("foreign child", " ".join(b["rows"][0]["gaps"]))

    def test_stale_observed_head_downgrades_inconsistent_current_status(self):
        import copy
        m = copy.deepcopy(run([comment(SC_ID, self_check()), comment(9002, evidence())])[0])
        m["tasks"][0]["head_matches_candidate"] = False
        m["tasks"][0]["observed_head"] = OLD
        b = sb.board(m)
        self.assertEqual(b["rows"][0]["E"], "STALE_EVIDENCE")
        self.assertEqual(b["totals"]["E_current"], 0)
        self.assertIn("current evidence", b["rows"][0]["next"]["action"])

    def test_unread_issue_list_does_not_masquerade_as_zero_work(self):
        class IssuesDown(Provider):
            def list_issues(self): raise lc.ContractError("down")
        b = sb.board(rm.read_model(PLAN, IssuesDown([]), NOW))
        self.assertIsNone(b["totals"]["tasks"])
        self.assertTrue(b["totals"]["partial"])
        self.assertIn("not a zero", sb.render_markdown(b).lower())

    def test_managed_region_preserves_every_character_outside_its_markers(self):
        b = board([comment(SC_ID, self_check()), comment(9002, evidence())])
        md = sb.render_markdown(b)
        original = "# Owner aim\nDo not erase my words.\n\n# Agent notes\nOther author.\n"
        combined = sb.merge_managed_region(original, md)
        self.assertTrue(combined.startswith(original))
        self.assertEqual(sb.merge_managed_region(combined, md), combined)
        self.assertEqual(sb.merge_managed_region(combined, "replacement\n"), original + sb.MANAGED_BEGIN + "\nreplacement\n" + sb.MANAGED_END)
        with self.assertRaises(ValueError):
            sb.merge_managed_region(combined + md, md)
        with self.assertRaises(ValueError):
            sb.merge_managed_region(original + sb.MANAGED_BEGIN, md)

    def test_markdown_has_original_source_verification_and_per_pr_scope(self):
        md = sb.render_markdown(board([comment(SC_ID, self_check()), comment(9002, evidence())]))
        for required in ("Original input", "Verification scope", "Observed head", "PR-specific", "Next actor"):
            self.assertIn(required, md)
        self.assertIn("not engineering truth", md)

    def test_no_title_or_native_constant_zero_can_grant_acceptance(self):
        import copy
        m = copy.deepcopy(run([comment(SC_ID, self_check()), comment(9002, evidence())])[0])
        m["tasks"][0]["title"] = "[ACCEPTED][E99/99] Done!"
        m["native"]["verified_complete"] = 0
        b = sb.board(m)
        self.assertTrue(b["acceptance"].startswith("NOT_EVALUATED"))
        self.assertTrue(b["V"].startswith("NOT_EVALUATED"))
        self.assertTrue(b["rows"][0]["acceptance"].startswith("NOT_EVALUATED"))
        self.assertEqual(b["by_pr"]["https://github.com/reallakshman19/Common/pull/344"]["tasks"], 1)


    def test_two_prs_do_not_borrow_each_others_e_denominator(self):
        import copy
        m = copy.deepcopy(run([comment(SC_ID, self_check()), comment(9002, evidence())])[0])
        # WP2 is already present in the selected plan; modify its model row.
        # Appending a second WP2 makes the duplicate-ID fail-closed guard
        # deliberately exclude it from PR attribution (not a PR grouping bug).
        second = next(t for t in m["tasks"] if t["task_id"] == "V36-341-WP2")
        second["issue"] = "https://github.com/reallakshman19/Common/issues/346"
        second["pr"] = "https://github.com/reallakshman19/Common/pull/355"
        second["status"] = "NO_EVIDENCE"
        second["claim_qualified"] = False
        self.assertEqual(len(m["tasks"]), len(PLAN["tasks"]))
        b = sb.board(m)
        self.assertEqual(b["by_pr"]["https://github.com/reallakshman19/Common/pull/344"]["E_current"], 1)
        self.assertEqual(b["by_pr"]["https://github.com/reallakshman19/Common/pull/344"]["tasks"], 1)
        self.assertEqual(b["by_pr"]["https://github.com/reallakshman19/Common/pull/355"]["E_current"], 0)
        self.assertEqual(b["by_pr"]["https://github.com/reallakshman19/Common/pull/355"]["tasks"], 1)
        self.assertEqual(b["totals"]["tasks"], len(PLAN["tasks"]))
        self.assertNotIn("tests_passed", b["totals"])

    def test_repeated_task_id_never_inflates_e_or_pr_numerator(self):
        import copy
        m = copy.deepcopy(run([comment(SC_ID, self_check()), comment(9002, evidence())])[0])
        m["tasks"].append(copy.deepcopy(m["tasks"][0]))
        # Keep native total consistent so this test isolates duplicate identity,
        # not a separate native-total mismatch.
        m["native"]["total"] = len(m["tasks"])
        b = sb.board(m)
        self.assertTrue(b["totals"]["partial"])
        self.assertEqual(b["totals"]["E_current"], 0)
        self.assertEqual(b["by_pr"], {})
        self.assertIn("task_ids:duplicate", b["unread_sources"])
        duplicated = [r for r in b["rows"] if r["task_id"] == "V36-341-WP1"]
        self.assertEqual(len(duplicated), 2)
        for row in duplicated:
            self.assertEqual(row["E"], "SOURCE_MISMATCH")
            self.assertTrue(any("duplicated task id" in gap for gap in row["gaps"]))
            self.assertEqual(row["next"]["source"], "task_ids:duplicate")
            self.assertIsNone(row["pr_denominator"])


if __name__ == "__main__":
    unittest.main()
