"""v3.6 WP5 GitHub-only cold continuation and bounded BuddyRunner tests."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import decompose_v36 as dc
import lifecycle_v36 as lc
import successor_v36 as sv

LABEL=lc.load_label(ROOT/"tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN=dc.load_plan(ROOT/"plans/V36-1-PLAN-01.yaml",LABEL)
REPO="reallakshman19/relay-v36-e2e-lab"
HEAD="61a71a038cca56507040bdb365edf76a9c0d2469"
OLD="e832f6b0c19e3c74ccf55595225b18139dbf23dc"


class Provider:
    repo=REPO
    def __init__(self, *, stale=False, index=True, repo=REPO, wrong_pr=False):
        self.repo=repo
        self.issues=[{"number":i+2,
            "title":dc.child_title(t),
            "body":dc.child_body(t, PLAN),
            "html_url":f"https://github.com/{REPO}/issues/{i+2}"}
            for i,t in enumerate(PLAN["tasks"])]
        links={t["task_id"]:self.issues[i]["html_url"]
               for i,t in enumerate(PLAN["tasks"])}
        self.comments={1:[{
            "body":dc.render_index(PLAN,links),
            "html_url":f"https://github.com/{REPO}/issues/1#issuecomment-1"}] if index else []}
        for i,t in enumerate(PLAN["tasks"]):
            sha=OLD if stale and i==0 else HEAD
            e=lc.render_evidence(outcome=t["outcome"],for_user="Real source fact",
                 proof=f"https://github.com/{REPO}/pull/4/commits/{sha}",
                 task_id=t["task_id"],issue_ref=f"{REPO}#{i+2}",
                 candidate=f"{REPO}@{sha}",tests_passed=2,tests_run=2)
            self.comments[i+2]=[{"body":e,"user":{"login":"reallakshman19"},"html_url":f"https://github.com/{REPO}/issues/{i+2}#issuecomment-{i+2}"}]
        self.pr={"number":5 if wrong_pr else 4,"head":{"sha":HEAD},
                 "title":"[V3.6][O1/O3][DRAFT][E2/2] Evidence probe",
                 "draft":True,"merged":False,"state":"open"}
    def list_issues(self):return self.issues
    def list_comments(self,n):return self.comments.get(n,[])
    def request(self,method,path,body=None):
        assert method=="GET" and path=="/issues/1"
        return {"number":1,"title":"[V3.6][LAB][E2/2] Parent"}
    def get_pr(self,n):
        assert n==4
        return self.pr


class ColdSuccessorTests(unittest.TestCase):
    def test_packet_contains_owner_verbatim_and_real_sources(self):
        d=sv.build_packet(LABEL,PLAN,Provider(),[4])
        self.assertEqual(d["label"]["problem"],LABEL["label"]["problem"])
        self.assertEqual(d["label"]["main_aim"],LABEL["label"]["main_aim"])
        self.assertEqual(d["label"]["owner_constraints"],LABEL["label"]["owner_constraints"])
        self.assertEqual(d["snapshot"]["current_evidence"],2)
        self.assertEqual(d["snapshot"]["accepted_complete"],0)
        self.assertEqual(d["next"],"INDEPENDENT_ACCEPTANCE_REQUIRED")
        self.assertTrue(all(t["evidence"] and t["accepted"] is False for t in d["tasks"]))
        md=sv.render_markdown(d)
        self.assertIn(HEAD,md)
        self.assertIn(LABEL["label"]["main_aim"],md)
        self.assertIn("Next: INDEPENDENT_ACCEPTANCE_REQUIRED",md)

    def test_stale_child_is_next_and_does_not_gain_acceptance(self):
        d=sv.build_packet(LABEL,PLAN,Provider(stale=True),[4])
        self.assertEqual(d["next"],"V36-1-WP1")
        self.assertEqual(d["snapshot"]["stale_evidence"],1)
        self.assertEqual(d["snapshot"]["current_evidence"],1)
        self.assertEqual(d["snapshot"]["accepted_complete"],0)
        self.assertIn("STALE_EVIDENCE",sv.render_markdown(d))

    def test_missing_index_fails_closed(self):
        with self.assertRaisesRegex(lc.ContractError,"managed parent index"):
            sv.build_packet(LABEL,PLAN,Provider(index=False),[4])

    def test_wrong_repo_fails_closed(self):
        with self.assertRaisesRegex(lc.ContractError,"repository mismatch"):
            sv.build_packet(LABEL,PLAN,Provider(repo="wrong/repo"),[4])

    def test_wrong_pr_number_fails_closed(self):
        with self.assertRaisesRegex(lc.ContractError,"malformed"):
            sv.build_packet(LABEL,PLAN,Provider(wrong_pr=True),[4])

    def test_duplicate_pr_selection_fails_closed(self):
        with self.assertRaises(lc.ContractError):
            sv.build_packet(LABEL,PLAN,Provider(),[4,4])

    def test_wrong_label_version_fails_closed(self):
        wrong={**LABEL,"version":"1.1.0"}
        with self.assertRaisesRegex(lc.ContractError,"label/plan mismatch"):
            sv.build_packet(wrong,PLAN,Provider(),[4])

    def test_buddy_1a_execution_holds(self):
        v=sv.buddy_prompt("1a",handover_id="case-1",
                          parent=f"{REPO}#1",assessed_sha=HEAD)
        self.assertIn("EXECUTION=HOLD",v)
        self.assertIn("1b",v)

    def test_buddy_1b_not_product_implementation(self):
        v=sv.buddy_prompt("1b",handover_id="case-1",
                          parent=f"{REPO}#1",assessed_sha=HEAD)
        self.assertIn("PRODUCT_IMPLEMENTATION=HOLD",v)
        self.assertIn("ONE proposal",v)

    def test_buddy_2_requires_provenance_and_ends_loop(self):
        args=dict(handover_id="case-1",parent=f"{REPO}#1",assessed_sha=HEAD)
        with self.assertRaises(lc.ContractError):
            sv.buddy_prompt("2",**args)
        v=sv.buddy_prompt("2",**args,evidence_url=f"https://github.com/{REPO}/issues/1",
                         body_digest="a"*64)
        self.assertIn("HANDOVER=CLOSED",v)
        self.assertIn("no further review loop",v)

    def test_buddy_optional_one_shot_Y(self):
        args=dict(handover_id="case-1",parent=f"{REPO}#1",assessed_sha=HEAD,
                  evidence_url=f"https://github.com/{REPO}/issues/2",
                  body_digest="b"*64)
        v=sv.buddy_prompt("Y",**args)
        self.assertIn("ONE",v)
        self.assertIn("CONTINUE or NO_CHANGE",v)
        with self.assertRaises(lc.ContractError):
            sv.buddy_prompt("Y",**{**args,"body_digest":"invalid"})

    def test_buddy_rejects_nonexact_candidate(self):
        with self.assertRaises(lc.ContractError):
            sv.buddy_prompt("1a",handover_id="a",parent=f"{REPO}#1",assessed_sha="abcdef0")


if __name__=="__main__":
    unittest.main()
