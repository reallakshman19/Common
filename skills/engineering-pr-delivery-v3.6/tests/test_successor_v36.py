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


class ECO06ContextProvider(Provider):
    """Source records only; no mutation methods and no external service."""
    def __init__(self, *, private=False, fail_comments=False, source_reader=True):
        super().__init__()
        self.private, self.fail_comments = private, fail_comments
        self.source_reader = source_reader
        self.owner = ("Original Owner intent: keep user input intact.\n"
                      "Decision: ADOPTED preserve source identity; REJECTED inferred matching; "
                      "PARKED deployment.\n"
                      "Superseded by: https://github.com/" + REPO + "/issues/9\n"
                      "Original input: https://github.com/" + REPO + "/blob/" + HEAD
                      + "/fixtures/input.xml\n"
                      "Golden: https://github.com/" + REPO + "/blob/" + HEAD
                      + "/fixtures/full-golden.json\n"
                      "Benchmark: https://github.com/" + REPO + "/blob/" + HEAD
                      + "/benchmarks/expected.json\n")
        self.issues[0]["body"] += "\nDecision: REJECTED fabricated accuracy claims\n"
        self.comments[1].append({
            "body": "Owner amendment: preserve physical identity; Next verification: independent Chromium run.",
            "html_url": f"https://github.com/{REPO}/issues/1#issuecomment-99",
            "id": 99, "user": {"login": "reallakshman19"},
            "updated_at": "2026-10-17T05:00:00Z"})
        self.linked = {"number": 9, "title": "Superseded context",
                       "body": "Decision: PARKED experimental path",
                       "html_url": f"https://github.com/{REPO}/issues/9"}

    def request(self, method, path, body=None):
        assert method == "GET" and path == "/issues/1"
        return {"number": 1, "title": "[V3.6][E2/2] Reported success",
                "body": self.owner,
                "html_url": f"https://github.com/{REPO}/issues/1"}

    def get_issue(self, number):
        if number != 9:
            raise lc.ContractError("unrelated issue")
        return self.linked

    def fetch_source(self, url):
        if not self.source_reader:
            raise NotImplementedError("blob retrieval capability unavailable")
        if self.private:
            raise PermissionError("403 private source")
        return {"url": url, "content": "<original occurrence id='7'/>",
                "sha": HEAD}

    def list_comments(self, n):
        if self.fail_comments and n == 1:
            raise lc.ContractError("provider 503")
        return super().list_comments(n)


class ECO06SuccessorRecoveryTests(unittest.TestCase):
    OWNER_URL = f"https://github.com/{REPO}/issues/1"
    TEN = (
        "original_intent_amendments", "originals_golden_benchmark",
        "causal_code_path", "decision_rationale", "issue_lineage",
        "permitted_provenance", "proof_vs_acceptance",
        "handover_next_verification", "stale_source_brief", "safety_boundaries",
    )

    def test_eco06_packet_reports_all_ten_from_fresh_owned_sources(self):
        provider = ECO06ContextProvider()
        packet = sv.build_packet(LABEL, PLAN, provider, [4])
        recovery = packet["recovery"]
        self.assertEqual(recovery["schema"], "v36.successor.recovery/v1")
        self.assertEqual(recovery["owning_issue_url"], self.OWNER_URL)
        self.assertEqual(tuple(recovery["outcomes"]), self.TEN)
        self.assertEqual(recovery["investigation"]["mode"], "OPEN_SOURCE_INSPECTION")
        self.assertEqual(recovery["investigation"]["blind_review"], "NOT_RUN")
        self.assertEqual(recovery["acceptance_demonstration"], "NOT_RUN")
        self.assertEqual(recovery["outcomes"]["original_intent_amendments"]["status"], "REPORTED")
        self.assertTrue(recovery["outcomes"]["original_intent_amendments"]["source_refs"])
        self.assertEqual(recovery["outcomes"]["proof_vs_acceptance"]["acceptance"], "NOT_EVALUATED")
        self.assertEqual(recovery["outcomes"]["causal_code_path"]["status"], "NOT_RUN")
        self.assertIn("issues/9", str(recovery["linked_history"]))
        self.assertIn("Owner intent", sv.render_markdown(packet))
        for item in recovery["outcomes"].values():
            self.assertTrue(item["source_refs"] or
                            (item["status"] in ("MISSING", "UNKNOWN", "NOT_RUN")
                             and item["reason"]), item)
        self.assertNotIn("ACCEPTED", str(recovery["outcomes"]).upper())

    def test_eco06_one_exact_authorized_owner_issue_only(self):
        provider = ECO06ContextProvider()
        for url in (f"https://github.com/{REPO}/issues/2",
                    f"https://github.com/other/repo/issues/1",
                    self.OWNER_URL + "?draft=1",
                    self.OWNER_URL + "#issuecomment-99"):
            with self.subTest(url=url), self.assertRaises(lc.ContractError):
                sv.recover_context(LABEL, PLAN, provider, owning_issue_url=url)
        with self.assertRaises(lc.ContractError):
            sv.recover_context(LABEL, PLAN,
                               Provider(repo="foreign/repo"),
                               owning_issue_url=self.OWNER_URL)

    def test_eco06_private_original_not_certified(self):
        result = sv.recover_context(LABEL, PLAN, ECO06ContextProvider(private=True),
                                    owning_issue_url=self.OWNER_URL)
        entry = result["outcomes"]["originals_golden_benchmark"]
        self.assertIn(entry["status"], ("UNKNOWN", "MISSING"))
        self.assertIn("private", entry["reason"].lower())
        self.assertNotIn("accepted", str(entry).lower())

    def test_eco06_provider_unavailable_is_explicit_unknown(self):
        result = sv.recover_context(LABEL, PLAN, ECO06ContextProvider(fail_comments=True),
                                    owning_issue_url=self.OWNER_URL)
        self.assertFalse(result["read_complete"])
        self.assertIn("comments", str(result["unavailable_sources"]))
        self.assertIn(result["outcomes"]["handover_next_verification"]["status"],
                      ("UNKNOWN", "NOT_RUN"))

    def test_eco06_stale_source_and_owner_brief_downgrade(self):
        provider = ECO06ContextProvider()
        first = sv.recover_context(LABEL, PLAN, provider, owning_issue_url=self.OWNER_URL)
        stale = sv.recover_context(
            LABEL, PLAN, provider, owning_issue_url=self.OWNER_URL,
            prior={"source_hashes": {self.OWNER_URL: "f" * 64},
                   "brief_sha256": "e" * 64})
        self.assertEqual(stale["outcomes"]["stale_source_brief"]["status"], "UNKNOWN")
        self.assertTrue(stale["source_changes"])
        self.assertIn("STALE", stale["source_state"])
        self.assertNotEqual(first["brief_sha256"], "e" * 64)

    def test_eco06_capability_gap_and_no_earlier_chat_are_honest(self):
        provider = ECO06ContextProvider(source_reader=False)
        result = sv.recover_context(LABEL, PLAN, provider, owning_issue_url=self.OWNER_URL)
        self.assertEqual(result["prior_chats"]["status"], "NOT_RUN")
        self.assertEqual(result["outcomes"]["causal_code_path"]["status"], "NOT_RUN")
        originals = result["outcomes"]["originals_golden_benchmark"]
        self.assertIn(originals["status"], ("UNKNOWN", "NOT_RUN"))
        self.assertTrue(originals["reason"])
        self.assertEqual(result["acceptance_demonstration"], "NOT_RUN")

    def test_eco06_no_scoreboard_title_or_fabricated_claim_grants_acceptance(self):
        provider = ECO06ContextProvider()
        provider.owner += "\n# BOARD ACCEPTED 100% SUCCESS -- unsupported claim\n"
        packet = sv.build_packet(LABEL, PLAN, provider, [4])
        self.assertEqual(packet["snapshot"]["accepted_complete"], 0)
        self.assertEqual(packet["recovery"]["outcomes"]["proof_vs_acceptance"]["acceptance"],
                         "NOT_EVALUATED")
        self.assertEqual(packet["recovery"]["acceptance_demonstration"], "NOT_RUN")

    def test_eco06_blind_stages_and_legacy_buddy_prompt_unchanged(self):
        provider = ECO06ContextProvider()
        report = sv.recover_context(LABEL, PLAN, provider, owning_issue_url=self.OWNER_URL)
        self.assertEqual(report["investigation"]["blind_review"], "NOT_RUN")
        prompt = sv.buddy_prompt("1b", handover_id="case", parent=f"{REPO}#1",
                                 assessed_sha=HEAD)
        self.assertIn("PRODUCT_IMPLEMENTATION=HOLD", prompt)
        self.assertEqual(sv.PHASES, frozenset(("1a", "1b", "2", "Y")))


    def test_eco06_wrong_owning_issue_preflight_before_any_provider_reads(self):
        class Spy(ECO06ContextProvider):
            def __init__(self):
                super().__init__()
                self.reads = []
            def list_issues(self):
                self.reads.append("issues")
                return super().list_issues()
            def request(self, method, path, body=None):
                self.reads.append(method + " " + path)
                return super().request(method, path, body)
        provider = Spy()
        with self.assertRaises(lc.ContractError):
            sv.build_packet(LABEL, PLAN, provider, [4],
                            owning_issue_url=f"https://github.com/{REPO}/issues/2")
        self.assertEqual(provider.reads, [])


if __name__=="__main__":
    unittest.main()
