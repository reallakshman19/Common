"""V3.6 WP4 publisher tests; dry-run, idempotence, and provider readback."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import publisher_v36 as pu
import decompose_v36 as dc
import lifecycle_v36 as lc

LAB = lc.load_label(ROOT/"tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN = dc.load_plan(ROOT/"plans/V36-1-PLAN-01.yaml", LAB)
PARENT = {"number":1,"title":"[V3.6][LAB][O1–O5][0/2] Independent lifecycle acceptance — planned","body":"","html_url":"https://github.com/reallakshman19/relay-v36-e2e-lab/issues/1"}
CHILDREN = [dict(number=n,title=f"[V3.6][O{outcome}][PLANNED] V36-1-WP{i} — example",body=dc.child_body(PLAN["tasks"][i-1],PLAN),html_url=f"https://github.com/reallakshman19/relay-v36-e2e-lab/issues/{n}") for i,(n,outcome) in enumerate([(2,1),(3,3)],1)]
PR={"number":4,"head":{"sha":"8ec979746b0a7f55532c804fbb959ed1a29eb3a2"},"title":"[V3.6][LAB][O1][DRAFT] Evidence probe — candidate created","draft":True,"state":"open","merged":False}


def report(current=0, statuses=("NO_EVIDENCE","NO_EVIDENCE"), links=(None,None)):
    return {"parent":PLAN["parent"],"label_sha":PLAN["label"]["label_sha"],"current_evidence":current,
            "total":2,"verified_complete":0,"tasks":[dict(task_id=t["task_id"],status=s,pr=link)
                for t,s,link in zip(PLAN["tasks"],statuses,links)]}


class Fake:
    repo="reallakshman19/relay-v36-e2e-lab"
    def __init__(self):
        self.records={"/issues/1":PARENT.copy(),"/issues/2":CHILDREN[0].copy(),
                      "/issues/3":CHILDREN[1].copy(),"/pulls/4":PR.copy()}
        self.writes=[]
    def request(self,method,path,body=None):
        if method=="GET": return self.records[path].copy()
        if method=="PATCH":
            self.records[path]["title"]=body["title"]
            self.writes.append(path)
            return self.records[path].copy()
        raise AssertionError(method)


class PublisherTests(unittest.TestCase):
    def test_zero_state_projects_titles_without_completion(self):
        updates=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report())
        self.assertIn("[E0/2]",updates[0]["after"])
        self.assertIn("[PENDING]",updates[1]["after"])
        self.assertIn("[UNATTRIBUTED][DRAFT][E0/0]",updates[3]["after"])

    def test_one_evidence_updates_parent_child_and_pr(self):
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report(1,("CURRENT_EVIDENCE","NO_EVIDENCE"),("https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4",None)))
        self.assertIn("[E1/2]",u[0]["after"])
        self.assertIn("[EVIDENCED]",u[1]["after"])
        self.assertIn("[PENDING]",u[2]["after"])
        self.assertIn("[O1][DRAFT][E1/1]",u[3]["after"])

    def test_unrelated_pr_does_not_inherit_plan_outcomes(self):
        unrelated=dict(PR,number=5,title="[V3.6][O1/O3][DRAFT] Other feature")
        link="https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],unrelated,
                        report(2,("CURRENT_EVIDENCE","CURRENT_EVIDENCE"),(link,link)))
        self.assertIn("[E2/2]",u[0]["after"])
        self.assertIn("[UNATTRIBUTED][DRAFT][E0/0]",u[-1]["after"])
        self.assertNotIn("[O1/O3]",u[-1]["after"])
        self.assertIn("Other feature",u[-1]["after"])

    def test_one_PR_has_one_outcome_not_whole_plan(self):
        a="https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        other="https://github.com/reallakshman19/relay-v36-e2e-lab/pull/5"
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,
                        report(2,("CURRENT_EVIDENCE","CURRENT_EVIDENCE"),(a,other)))
        self.assertIn("[E2/2]",u[0]["after"])  # parent sees every task
        self.assertIn("[O1][DRAFT][E1/1]",u[-1]["after"])  # PR sees its own task
        self.assertNotIn("[O1/O3]",u[-1]["after"])

    def test_stale_link_retains_PR_outcome_but_not_current_count(self):
        a="https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,
                        report(0,("STALE_EVIDENCE","STALE_EVIDENCE"),(a,a)))
        self.assertIn("[O1/O3][DRAFT][E0/2]",u[-1]["after"])

    def test_wrong_repo_proof_does_not_attribute_outcome(self):
        wrong="https://github.com/other/repo/pull/4"
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,
                        report(1,("CURRENT_EVIDENCE","NO_EVIDENCE"),(wrong,None)))
        self.assertIn("[UNATTRIBUTED][DRAFT][E0/0]",u[-1]["after"])

    def test_closed_PR_status_is_not_draft(self):
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],
                        dict(PR,draft=False,state="closed"),report())
        self.assertIn("[UNATTRIBUTED][CLOSED][E0/0]",u[-1]["after"])

    def test_stale_is_not_evidence(self):
        u=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report(0,("STALE_EVIDENCE","NO_EVIDENCE")))
        self.assertIn("[STALE]",u[1]["after"])
        self.assertIn("[E0/2]",u[0]["after"])

    def test_dry_run_never_writes(self):
        cl=Fake()
        changes=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report())
        result=pu.apply_projection({"parent":PLAN["parent"],"changes":changes},cl,confirm_scope="",allow_write=False)
        self.assertEqual(result["applied"],0)
        self.assertEqual(cl.writes,[])

    def test_apply_verifies_readback(self):
        cl=Fake()
        changes=[u for u in pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report()) if u["before"]!=u["after"]]
        result=pu.apply_projection({"parent":PLAN["parent"],"changes":changes},cl,confirm_scope=PLAN["parent"],allow_write=True)
        self.assertEqual(result["applied"],4)
        self.assertTrue(result["readback_ok"])
        self.assertEqual(len(cl.writes),4)

    def test_wrong_scope_refused(self):
        with self.assertRaises(lc.ContractError):
            pu.apply_projection({"parent":PLAN["parent"],"changes":[]},Fake(),confirm_scope="other/repo#1",allow_write=True)

    def test_missing_parent_refused(self):
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN,CHILDREN,PR,report())

    def test_duplicate_child_refused(self):
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN,[PARENT,*CHILDREN,dict(CHILDREN[0])],PR,report())

    def test_pr_head_drift_refused(self):
        cl=Fake()
        p=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report())[-1]
        cl.records["/pulls/4"]["head"]={"sha":"f"*40}
        with self.assertRaises(lc.ContractError):
            pu.apply_projection({"parent":PLAN["parent"],"changes":[p]},cl,confirm_scope=PLAN["parent"],allow_write=True)

    def test_untouched_second_projection_idempotent(self):
        cl=Fake()
        updates=pu.title_plan(PLAN,[PARENT,*CHILDREN],PR,report())
        pu.apply_projection({"parent":PLAN["parent"],"changes":updates},cl,confirm_scope=PLAN["parent"],allow_write=True)
        after=[cl.records[f"/issues/{n}"] for n in (1,2,3)]
        pr=cl.records["/pulls/4"]
        second=pu.title_plan(PLAN,after,pr,report())
        self.assertEqual([u for u in second if u["before"]!=u["after"]],[])


    def test_eco04_preserves_nonowned_brackets_and_human_child_suffix(self):
        import copy
        pr = dict(PR, title="[SECURITY][V3.6][O1][DRAFT][E0/1] [Human] Fix mechanism")
        issues = [dict(PARENT), *[dict(c) for c in CHILDREN]]
        issues[1]["title"] = "[PERSONAL][V3.6][O1][PENDING] Human child description [keep]"
        changes = pu.title_plan(PLAN, issues, pr, report())
        self.assertIn("[SECURITY][V3.6]", changes[-1]["after"])
        self.assertTrue(changes[-1]["after"].endswith("[Human] Fix mechanism"))
        self.assertIn("[PERSONAL][V3.6]", changes[1]["after"])
        self.assertTrue(changes[1]["after"].endswith("Human child description [keep]"))
        self.assertNotIn("[SECURITY][V3.6][SECURITY]", changes[-1]["after"])

    def test_eco04_repeated_managed_prefix_normalises_without_losing_nonowned(self):
        pr = dict(PR, title="[TEAM][V3.6][O1][OPEN][E1/1][V3.6][O1][DRAFT] Keep this")
        first = pu.title_plan(PLAN, [PARENT, *CHILDREN], pr, report())[-1]["after"]
        self.assertEqual(first.count("[V3.6]"), 1)
        self.assertIn("[TEAM]", first)
        self.assertTrue(first.endswith("Keep this"))
        second = pu.title_plan(PLAN, [PARENT, *CHILDREN], dict(pr, title=first), report())[-1]["after"]
        self.assertEqual(first, second)

    def test_eco04_empty_and_overlong_title_never_truncated(self):
        pr = dict(PR, title="[V3.6][O1][DRAFT]")
        self.assertTrue(pu.title_plan(PLAN, [PARENT, *CHILDREN], pr, report())[-1]["after"].endswith("Lifecycle work"))
        pr["title"] = "[HUMAN] " + "keep" * 70
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN, [PARENT, *CHILDREN], pr, report())

    def test_eco04_parent_profile_from_selected_repo_preserves_lab_and_nonlab(self):
        import copy
        self.assertEqual(pu.parent_display_profile(PLAN), "lab")
        lab = pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, report())[0]["after"]
        self.assertIn("[V3.6][LAB][E0/2]", lab)
        alt = copy.deepcopy(PLAN)
        alt["parent"] = "reallakshman19/Common#1"
        self.assertEqual(pu.parent_display_profile(alt), "non_lab")
        children = [dict(CHILDREN[i], body=dc.child_body(t, alt)) for i, t in enumerate(alt["tasks"])]
        alt_report = dict(report(), parent=alt["parent"])
        title = pu.title_plan(alt, [dict(PARENT), *children], None, alt_report)[0]["after"]
        self.assertIn("[V3.6][E0/2]", title)
        self.assertNotIn("[LAB]", title)

    def test_eco04_signal_stale_from_native_and_preserves_pr_e(self):
        pr_ref = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("STALE_EVIDENCE", "NO_EVIDENCE"), (pr_ref, None))
        u = pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep)[-1]
        self.assertIn("[O1][DRAFT][E0/1][STALE]", u["after"])
        self.assertEqual(u["attention"]["signal"], "STALE")
        self.assertEqual(u["attention"]["source"], "native:STALE_EVIDENCE")
        self.assertEqual(u["attention_grammar"], "v36.attention/v1")

    def test_eco04_attention_precedence_is_stage_specific_and_source_based(self):
        pr_ref = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("STALE_EVIDENCE", "NO_EVIDENCE"), (pr_ref, None))
        b = {"schema": "v36.scoreboard/v1", "plan": PLAN["plan_version"],
             "parent": PLAN["parent"], "label_sha": PLAN["label"]["label_sha"],
             "read_complete": True,
             "rows": [{"task_id": PLAN["tasks"][0]["task_id"], "pr": pr_ref, "E": "STALE_EVIDENCE",
                       "pending": [{"what": "Owner hold", "owner": "Owner", "prevents_done": True}],
                       "original_input": {"input": "MISSING"}, "gaps": ["golden unavailable"]}],
             "by_pr": {pr_ref: {"tasks": 1, "E_current": 0, "task_ids": [PLAN["tasks"][0]["task_id"]]}}}
        u = pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep, scoreboard=b)[-1]
        self.assertIn("[HOLD]", u["after"])
        self.assertEqual(u["attention"]["source"], "board:pending:Owner hold")
        self.assertNotIn("[ORIGINALS_MISSING]", u["after"])
        self.assertNotIn("[STALE]", u["after"])

    def test_eco04_unknown_not_success_and_routine_gate_not_constant_alarm(self):
        pr_ref = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("PROVIDER_UNAVAILABLE", "NO_EVIDENCE"), (pr_ref, None))
        u = pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep)[-1]
        self.assertIn("[UNKNOWN]", u["after"])
        self.assertNotIn("[ACCEPTED]", u["after"])
        rep = report(1, ("CURRENT_EVIDENCE", "NO_EVIDENCE"), (pr_ref, None))
        u = pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep)[-1]
        self.assertIn("[E1/1]", u["after"])
        self.assertIsNone(u["attention"]["signal"])
        for token in ("[OWNER_GATE]", "[ORIGINALS_MISSING]", "[ACCEPTED]"):
            self.assertNotIn(token, u["after"])

    def test_eco04_board_conflicts_cannot_promote_e_or_acceptance(self):
        pr_ref = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("STALE_EVIDENCE", "NO_EVIDENCE"), (pr_ref, None))
        b = {"schema": "v36.scoreboard/v1", "parent": PLAN["parent"], "plan": PLAN["plan_version"],
             "label_sha": PLAN["label"]["label_sha"], "read_complete": True,
             "rows": [{"task_id": PLAN["tasks"][0]["task_id"], "E": "CURRENT_EVIDENCE",
                       "pr": pr_ref, "gaps": [], "pending": []}],
             "by_pr": {pr_ref: {"tasks": 1, "E_current": 1, "task_ids": [PLAN["tasks"][0]["task_id"]]}}}
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep, scoreboard=b)
        b["parent"] = "mallory/other#1"
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN, [PARENT, *CHILDREN], PR, rep, scoreboard=b)


    def test_eco04_calculate_accepts_board_projection_without_writing(self):
        from unittest.mock import patch
        link = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("STALE_EVIDENCE", "NO_EVIDENCE"), (link, None))
        b = {"schema": "v36.scoreboard/v1", "parent": PLAN["parent"],
             "plan": PLAN["plan_version"], "label_sha": PLAN["label"]["label_sha"],
             "read_complete": True,
             "rows": [{"task_id": PLAN["tasks"][0]["task_id"], "E": "STALE_EVIDENCE",
                       "pr": link, "pending": [], "gaps": []}],
             "by_pr": {link: {"tasks": 1, "E_current": 0,
                             "task_ids": [PLAN["tasks"][0]["task_id"]]}}}
        client = Fake()
        client.list_issues = lambda: [PARENT, *CHILDREN]
        with patch.object(pu, "snapshot", return_value=rep):
            projected = pu.calculate(PLAN, client, 4, scoreboard=b)
        pr_projection = projected["all"][-1]
        self.assertIn("[STALE]", pr_projection["after"])
        self.assertEqual(pr_projection["pr_e_denominator"], 1)
        self.assertEqual(client.writes, [])

    def test_eco04_board_cli_cannot_trigger_provider_writes(self):
        from unittest.mock import patch
        with patch.object(pu, "GithubClient") as provider:
            with self.assertRaises(SystemExit):
                pu.main(["--label", "unused", "--plan", "unused",
                         "--scoreboard", "unused", "--apply"])
            provider.assert_not_called()


    def test_eco04_closed_draft_status_precedes_draft_flag(self):
        closed = dict(PR, state="closed", draft=True, merged=False)
        projected = pu.title_plan(PLAN, [PARENT, *CHILDREN], closed, report())[-1]
        self.assertIn("[CLOSED][E0/0]", projected["after"])
        self.assertNotIn("[DRAFT]", projected["after"])
        merged = dict(PR, state="closed", draft=True, merged=True)
        projected = pu.title_plan(PLAN, [PARENT, *CHILDREN], merged, report())[-1]
        self.assertIn("[MERGED][E0/0]", projected["after"])
        with self.assertRaises(lc.ContractError):
            pu.title_plan(PLAN, [PARENT, *CHILDREN], dict(PR, state="invalid",
                                                         draft=False, merged=False), report())


if __name__=="__main__":
    unittest.main()
