"""v3.6 WP6: two independently invocable purpose-specific prompt generators."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import decompose_v36 as dc
import lifecycle_v36 as lc
import prompt_2pass_v36 as tw
import prompt_3pass_v36 as th

LABEL=lc.load_label(ROOT/"tests/fixtures/relay/AIM/V35-LIFECYCLE.yaml")
PLAN=dc.load_plan(ROOT/"plans/V36-1-PLAN-01.yaml",LABEL)
REPO="reallakshman19/relay-v36-e2e-lab"


def packet():
    return {"parent":PLAN["parent"],"parent_url":f"https://github.com/{REPO}/issues/1",
        "parent_title":"[V3.6][LAB][E2/2] Demo","plan":PLAN["plan_version"],
        "index_url":f"https://github.com/{REPO}/issues/1#issuecomment-1",
        "label":{"work":LABEL["work"],"version":LABEL["version"],
                 "label_sha":LABEL["label_sha"],**LABEL["label"]},
        "snapshot":{"current_evidence":2,"total":2,"stale_evidence":0,"accepted_complete":0},
        "tasks":[dict(task_id=t["task_id"],outcome=t["outcome"],
                      issue=f"https://github.com/{REPO}/issues/{i+2}",
                      evidence=f"https://github.com/{REPO}/issues/{i+2}#issuecomment-{i+2}",
                      status="CURRENT_EVIDENCE",acceptance=t["acceptance"],
                      for_user=t["for_user"],accepted=False)
                 for i,t in enumerate(PLAN["tasks"])],
        "prs":[{"url":f"https://github.com/{REPO}/pull/4",
                "head":"61a71a038cca56507040bdb365edf76a9c0d2469",
                "state":"open","draft":True,"merged":False,"title":"Test PR"}],
        "next":"INDEPENDENT_ACCEPTANCE_REQUIRED",
        "unproven":["No task accepted without independent evidence"]}


class TwoPassTests(unittest.TestCase):
    def test_only_two_distinct_passes(self):
        result=tw.generate_two_pass(packet(),"V36-1-WP1")
        self.assertEqual(result.count("PASS 1 —"),1)
        self.assertEqual(result.count("PASS 2 —"),1)
        self.assertNotIn("PASS 3 —",result)
        self.assertIn("V36_TWO_PASS_EXECUTION_GENERATOR_V1",result)

    def test_preserves_verbatim_owner_aim(self):
        result=tw.generate_two_pass(packet(),"V36-1-WP1")
        for k in ("problem","main_aim","task_aim","done_when"):
            self.assertIn(LABEL["label"][k],result)
        self.assertIn("accepted=0",result)

    def test_selected_child_and_exact_HEAD_in_prompt(self):
        result=tw.generate_two_pass(packet(),"V36-1-WP2")
        self.assertIn("V36-1-WP2",result)
        self.assertIn("/issues/3",result)
        self.assertIn("61a71a038cca56507040bdb365edf76a9c0d2469",result)
        self.assertIn("canonical TASK_EVIDENCE",result)

    def test_missing_selected_task_refused(self):
        with self.assertRaises(lc.ContractError):
            tw.generate_two_pass(packet(),"V36-1-WP9")

    def test_missing_selected_child_refused(self):
        x=packet()
        x["tasks"][0]["issue"]=None
        with self.assertRaises(lc.ContractError):
            tw.generate_two_pass(x,"V36-1-WP1")


class ThreePassTests(unittest.TestCase):
    def test_three_passes_and_distinct_oracle(self):
        result=th.generate_three_pass(packet(),"V36-1-WP1")
        self.assertEqual(result.count("PASS 1 —"),1)
        self.assertEqual(result.count("PASS 2 —"),1)
        self.assertEqual(result.count("PASS 3 —"),1)
        self.assertIn("distinct evaluator",result)
        self.assertIn("negative/falsifying",result)
        self.assertIn("V36_THREE_PASS_INDEPENDENT_VALIDATION_GENERATOR_V1",result)

    def test_preserves_verbatim_owner_and_negative_oracle(self):
        result=th.generate_three_pass(packet(),"V36-1-WP2")
        self.assertIn(LABEL["label"]["main_aim"],result)
        self.assertIn("re-fetches Owner label",result)
        self.assertIn("unrelated PRs",result)
        self.assertIn("NOT_PROVEN/FAILED",result)

    def test_missing_target_or_child_fails_closed(self):
        with self.assertRaises(lc.ContractError):
            th.generate_three_pass(packet(),"V36-1-UNKNOWN")
        x=packet()
        x["tasks"][1]["issue"]=None
        with self.assertRaises(lc.ContractError):
            th.generate_three_pass(x,"V36-1-WP2")

    def test_generators_not_unified_and_not_old_skill_imports(self):
        two=tw.generate_two_pass(packet(),"V36-1-WP1")
        three=th.generate_three_pass(packet(),"V36-1-WP1")
        self.assertNotEqual(two,three)
        self.assertNotIn("THREE_PASS",two)
        self.assertNotIn("TWO_PASS",three)
        for source in (tw,th):
            code=Path(source.__file__).read_text(encoding="utf-8")
            self.assertNotIn("engineering-pr-delivery-v3.5",code)
            self.assertNotIn("buddy-runner-v1-6",code)


if __name__=="__main__":
    unittest.main()
