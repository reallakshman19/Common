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


    def test_eco04_human_attention_word_after_bare_version_marker_is_not_stripped(self):
        for supplied in ("[V3.6] [UNKNOWN] x", "[V3.6][HOLD] fix login"):
            with self.subTest(supplied=supplied):
                projected = pu.title_plan(
                    PLAN, [PARENT, *CHILDREN], dict(PR, title=supplied), report()
                )[-1]["after"]
                human = supplied.split("[V3.6]", 1)[1].strip()
                self.assertTrue(projected.endswith(human), projected)
                self.assertIn(human, projected)
                self.assertEqual(projected.count(human), 1)

    def test_eco04_human_attention_word_after_complete_legacy_pr_prefix_is_preserved(self):
        pr = dict(PR, title="[V3.6][O1][DRAFT][E0/0][HOLD] fix login")
        projected = pu.title_plan(PLAN, [PARENT, *CHILDREN], pr, report())[-1]
        self.assertIsNone(projected["attention"]["signal"])
        self.assertTrue(projected["after"].endswith("[HOLD] fix login"))
        self.assertEqual(projected["after"].count("[HOLD]"), 1)

    def test_eco04_emitted_attention_marker_allows_idempotent_reprojection(self):
        link = "https://github.com/reallakshman19/relay-v36-e2e-lab/pull/4"
        rep = report(0, ("STALE_EVIDENCE", "NO_EVIDENCE"), (link, None))
        original = dict(PR, title="[TEAM] [HOLD] fix login")
        first = pu.title_plan(PLAN, [PARENT, *CHILDREN], original, rep)[-1]["after"]
        self.assertIn("[O1][DRAFT][E0/1][STALE]", first)
        self.assertIn("[v36.attention/v1]", first)
        self.assertTrue(first.endswith("[HOLD] fix login"))
        second = pu.title_plan(PLAN, [PARENT, *CHILDREN],
                               dict(original, title=first), rep)[-1]["after"]
        self.assertEqual(first, second)

    def test_eco04_title_tail_intentionally_retains_foreign_prefix_and_human_word(self):
        self.assertEqual(
            pu.title_tail("[TEAM][V3.6] [UNKNOWN] x", "fallback"),
            "[TEAM] [UNKNOWN] x",
        )
        self.assertEqual(
            pu.title_tail("[V3.6][HOLD] fix login", "fallback"),
            "[HOLD] fix login",
        )


class ECO05GuardTests(unittest.TestCase):
    """Strict fake-provider-only authorisation; no live GitHub operations."""

    PIN = "a" * 64

    def setup_guard(self, *, pr=True):
        client = Fake()
        client.records["/pulls/4"]["body"] = "Human PR body"
        client.records["/pulls/4"]["labels"] = [{"name": "human-label"}]
        issues = [client.records[f"/issues/{n}"] for n in (1, 2, 3)]
        projection = pu.title_plan(PLAN, issues, client.records["/pulls/4"] if pr else None,
                                   report())
        changes = [r for r in projection if r["before"] != r["after"]]
        calculated = {"parent": PLAN["parent"], "label_sha": PLAN["label"]["label_sha"],
                      "source_pin": self.PIN, "changes": changes}
        targets = frozenset((r["kind"], r["number"]) for r in changes)
        options = {"confirm_scope": PLAN["parent"], "allow_write": True,
                   "authorized_surfaces": frozenset({"title"}),
                   "authorized_targets": targets, "lab_scope": client.repo,
                   "source_probe": lambda: self.PIN}
        return client, calculated, options

    def test_eco05_dry_run_default_never_patches(self):
        client, plan, options = self.setup_guard()
        options["allow_write"] = False
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "NOT_RUN")
        self.assertEqual(result["applied"], 0)
        self.assertFalse(result["complete"])
        self.assertEqual(client.writes, [])

    def test_eco05_separate_surface_consent_and_exact_target_scope(self):
        client, plan, options = self.setup_guard()
        options["authorized_surfaces"] = frozenset({"scoreboard"})
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(plan, client, **options)
        self.assertEqual(client.writes, [])
        options["authorized_surfaces"] = frozenset({"title"})
        options["authorized_targets"] = frozenset({("issue", 1)})
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(plan, client, **options)
        options["authorized_targets"] = frozenset((r["kind"], r["number"]) for r in plan["changes"])
        options["confirm_scope"] = "another/repository#1"
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(plan, client, **options)
        self.assertEqual(client.writes, [])

    def test_eco05_fresh_source_pin_required_before_any_write(self):
        client, plan, options = self.setup_guard()
        options["source_probe"] = lambda: "b" * 64
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("source", result["next_reconciliation"])
        self.assertEqual(result["applied"], 0)
        self.assertEqual(client.writes, [])

    def test_eco05_concurrent_body_edit_refused_without_restoring_owner_text(self):
        client, plan, options = self.setup_guard()
        client.records["/issues/1"]["body"] += "\nOWNER NEW PARAGRAPH"
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["applied"], 0)
        self.assertIn("OWNER NEW PARAGRAPH", client.records["/issues/1"]["body"])
        self.assertEqual(client.writes, [])

    def test_eco05_head_change_refused_without_patch(self):
        client, plan, options = self.setup_guard()
        plan["changes"] = [r for r in plan["changes"] if r["kind"] == "pr"]
        options["authorized_targets"] = frozenset({("pr", 4)})
        client.records["/pulls/4"]["head"] = {"sha": "b" * 40}
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("head", result["next_reconciliation"].lower())
        self.assertEqual(client.writes, [])

    def test_eco05_partial_provider_error_records_completed_and_pending(self):
        client, plan, options = self.setup_guard()
        original = client.request
        def fail_on_second(method, path, body=None):
            if method == "PATCH" and path == "/issues/2":
                raise lc.ContractError("simulated provider 503")
            return original(method, path, body)
        client.request = fail_on_second
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["applied"], 1)
        self.assertFalse(result["complete"])
        self.assertTrue(result["pending_surfaces"])
        self.assertIn("reconcile", result["next_reconciliation"])
        self.assertEqual(client.writes, ["/issues/1"])

    def test_eco05_readback_mismatch_marks_uncertain_and_stops(self):
        client, plan, options = self.setup_guard()
        original = client.request
        def bad_readback(method, path, body=None):
            if method == "PATCH" and path == "/issues/1":
                result = original(method, path, body)
                client.records[path]["title"] = "CONCURRENT CHANGED"
                return result
            return original(method, path, body)
        client.request = bad_readback
        result = pu.apply_projection(plan, client, **options)
        self.assertEqual(result["status"], "UNCERTAIN")
        self.assertFalse(result["complete"])
        self.assertTrue(result["pending_surfaces"])
        self.assertIn("readback", result["next_reconciliation"])
        self.assertEqual(client.writes, ["/issues/1"])

    def test_eco05_success_get_verified_then_safe_zero_change_replay(self):
        client, plan, options = self.setup_guard()
        first = pu.apply_projection(plan, client, **options)
        self.assertEqual(first["status"], "VERIFIED")
        self.assertTrue(first["complete"])
        self.assertEqual(first["applied"], 4)
        original_writes = list(client.writes)
        second = pu.apply_projection(plan, client, **options)
        self.assertEqual(second["status"], "VERIFIED")
        self.assertEqual(second["applied"], 0)
        self.assertEqual(client.writes, original_writes)

    def test_eco05_scoreboard_body_scope_preserves_owner_and_never_writes_labels(self):
        client, plan, options = self.setup_guard(pr=False)
        client.records["/issues/1"]["body"] = "OWNER AMENDMENT\nDo not overwrite.\n"
        change = pu.scoreboard_body_change(
            client.records["/issues/1"], "Managed score", parent_number=1)
        plan["changes"] = [change]
        options["authorized_surfaces"] = frozenset({"scoreboard"})
        options["authorized_targets"] = frozenset({("issue", 1)})
        first = pu.apply_projection(plan, client, **options)
        self.assertEqual(first["status"], "VERIFIED")
        self.assertEqual(first["applied"], 1)
        self.assertTrue(client.records["/issues/1"]["body"].startswith("OWNER AMENDMENT\n"))
        self.assertEqual(client.records["/issues/1"].get("labels"), None)
        again = pu.apply_projection(plan, client, **options)
        self.assertEqual(again["applied"], 0)
        self.assertEqual(len(client.writes), 1)

    def test_eco05_namespace_and_live_cli_writes_remain_denied(self):
        from unittest.mock import patch
        client, plan, options = self.setup_guard()
        options["authorized_surfaces"] = frozenset({"title", "namespace"})
        with self.assertRaises(lc.ContractError):
            pu.apply_projection(plan, client, **options)
        with patch.object(pu, "GithubClient") as provider:
            with self.assertRaises(SystemExit):
                pu.main(["--label", "unused", "--plan", "unused", "--apply"])
            provider.assert_not_called()
        self.assertEqual(client.writes, [])


if __name__=="__main__":
    unittest.main()
