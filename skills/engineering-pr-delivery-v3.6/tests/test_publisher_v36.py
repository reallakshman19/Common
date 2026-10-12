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


if __name__=="__main__":
    unittest.main()
