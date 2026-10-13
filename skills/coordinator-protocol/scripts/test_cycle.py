"""Offline behavioral regression tests. No live state, browser or network."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
SPEC = importlib.util.spec_from_file_location("cycle", Path(__file__).with_name("cycle.py"))
C = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(C)
URL = "https://chatgpt.com/c/12345678-aaaa-bbbb-cccc-000000000001"
URL2 = "https://chatgpt.com/c/12345678-aaaa-bbbb-cccc-000000000002"
START = "2026-10-11T10:00:00+00:00"
LEDGERS = {}
REAL_STORE = C.AimStore


class FakeStore:
    """Explicit ledger assertions, independent of agent footer contents."""
    def __init__(self, path, read_only=False):
        if read_only is not True:
            raise AssertionError("cycle must open the aim store read-only")
    def projection(self, namespace, workpack_id, recipient):
        return copy.deepcopy(LEDGERS[namespace])
    def close(self):
        pass


C.AimStore = FakeStore


def ledger_config(namespace=None, tasks=None):
    namespace = namespace or "work:cycle-" + str(len(LEDGERS))
    ids = tasks or [f"T{i}" for i in range(1, 9)]
    LEDGERS[namespace] = {"sequence": 1, "main": {"id": "MA1", "label": "A usable product"},
        "task": {"id": "TA1", "label": "Usable corrections"}, "validated_ids": [],
        "registered_ids": ids, "eligible_ids": list(ids), "alignment": "ALIGNED",
        "latest_assessment": None, "due": [], "reviewed_thresholds": [],
        "pending_proposal_ids": [], "reviewed_message_ids": [], "unreviewed_message_ids": []}
    return {"path": str(Path(__file__).with_name("aim_store.py").resolve()),
            "namespace": namespace, "workpack_id": "WP1"}


def fixture(s, label="Tab1"):
    return LEDGERS[s["streams"][label]["ledger"]["namespace"]]


def validate(s, ids):
    data = fixture(s)
    data.update(validated_ids=list(ids), eligible_ids=[i for i in data["registered_ids"] if i not in ids], sequence=data["sequence"] + 1)


def temporary_directory():
    root = Path.cwd() / "work"
    root.mkdir(exist_ok=True)
    return tempfile.TemporaryDirectory(prefix="coord-test-", dir=root)


def setup(interval=15, **config):
    s = {}
    cfg = {"url": URL, "ledger": ledger_config(), "plan": {"rev": "r1", "tasks": [{"id": f"T{i}", "outcome": f"outcome {i}", "status": "open"} for i in range(1, 9)]}, **config}
    C.operate(s, "init", {"interval": interval, "streams": {"Tab1": cfg}, "now": START})
    C.operate(s, "control", {"status": "RUNNING", "now": START})
    return s


def probe(mid="a1", done=None, nxt=None, kind="NONE", **fields):
    return {"url": URL, "state": "IDLE", "at_bottom": True, "user_ids": ["u1"],
            "latest_user": {"id": "u1", "hash": C.content_hash("Owner task")},
            "latest_assistant": {"id": mid, "hash": C.content_hash(mid)},
            "completed_messages": [{"id": mid, "minutes": 1, "pages": None}], "draft": "", "live_error": "",
            "status": {"plan_rev": "r1", "done": done or [], "next": nxt if nxt is not None else ["T2", "T3"], "ac": 0, "blocker": {"kind": kind, "text": "decision"}}, **fields}


def observe(s, p, now=START, reviewed=True):
    if reviewed:
        for item in p if isinstance(p, list) else [p]:
            for r in s["streams"].values():
                if item["url"] == r["url"] and r.get("ledger"):
                    data = LEDGERS[r["ledger"]["namespace"]]
                    for message in item.get("completed_messages", []):
                        if message["id"] not in data["reviewed_message_ids"]:
                            data["reviewed_message_ids"].append(message["id"])
    return C.operate(s, "observe", {"probes": p if isinstance(p, list) else [p], "now": now})


class CycleTests(unittest.TestCase):
    def test_allowed_intervals_and_default_hold(self):
        for interval in (10, 15, 30):
            s = {}
            self.assertEqual(C.operate(s, "init", {"interval": interval})["status"], "HOLD")
        for interval in (20, 60):
            with self.assertRaises(ValueError):
                setup(interval)

    def test_four_identical_durations_are_four_messages(self):
        s = setup(handover_hold=True)
        for n in range(4):
            p = probe(f"a{n}")
            p["completed_messages"][0]["minutes"] = 5
            observe(s, p)
        self.assertEqual(C.metric(s["streams"]["Tab1"])["turns"], 4)
        self.assertEqual(C.metric(s["streams"]["Tab1"])["minutes"], 20)

    def test_reprobe_does_not_recount_and_missing_metric_does_not_erase(self):
        s, p = setup(), probe(done=["T1"])
        observe(s, p)
        p["completed_messages"][0]["minutes"] = None
        observe(s, p)
        r = s["streams"]["Tab1"]
        self.assertEqual(C.metric(r), {"turns": 1, "minutes": 1, "pages": 0})
        self.assertEqual(r["evidence"], 0)
        self.assertEqual(len(r["claim_history"]), 1)
        self.assertIn("T1", r["claims"])
        self.assertNotIn("T1", r["closed"])

    def test_repeated_done_does_not_reset_stall(self):
        s = setup(handover_hold=True)
        for n in range(4):
            result = observe(s, probe(f"a{n}", done=["T1"]))
        r = s["streams"]["Tab1"]
        self.assertEqual(r["evidence"], 0)
        self.assertEqual(r["stall"], 4)
        self.assertEqual(result["actions"][0]["kind"], "RECONCILE")

    def test_off_plan_and_wrong_revision_do_not_count(self):
        for p in (probe(done=["DIAGNOSTIC-X"]), probe(status={"plan_rev": "old", "done": ["T1"], "next": ["T2"]})):
            s = setup()
            observe(s, p)
            self.assertEqual(s["streams"]["Tab1"]["evidence"], 0)

    def test_plan_history_survives_revision(self):
        s = setup()
        observe(s, probe(done=["T1"]))
        C.operate(s, "update", {"stream": "Tab1", "patch": {"plan": {"rev": "r2", "tasks": [{"id": "T1", "outcome": "same", "status": "open"}, {"id": "T2", "outcome": "next"}]}}})
        observe(s, probe("a2", status={"plan_rev": "r2", "done": ["T1"], "next": ["T2"]}))
        self.assertEqual(s["streams"]["Tab1"]["evidence"], 0)
        self.assertEqual(s["streams"]["Tab1"]["plan"]["tasks"]["T1"]["status"], "claimed")
        self.assertEqual(s["streams"]["Tab1"]["plan_history"][0]["rev"], "r1")

    def test_plan_revision_cannot_change_ledger_denominator(self):
        s = setup()
        observe(s, probe(done=["T1"]))
        C.operate(s, "update", {"stream": "Tab1", "patch": {"plan": {"rev": "r2", "tasks": [{"id": "T2", "outcome": "next"}]}}})
        observe(s, probe("a2", status={"plan_rev": "r2", "done": [], "next": ["T2"]}))
        self.assertEqual(s["streams"]["Tab1"]["summary"]["progress"], {"done": 0, "validated": 0, "claimed": 1, "total": 8})
        self.assertIn("T1", s["streams"]["Tab1"]["claims"])

    def test_finished_reply_without_duration_or_footer_changes(self):
        s = setup(speed="economy")
        p = probe(state="GENERATING", completed_messages=[], status={})
        observe(s, p)
        p = probe(state="IDLE", status={})
        p["completed_messages"][0]["minutes"] = None
        result = observe(s, p, "2026-10-11T10:15:00Z")
        self.assertIn("Tab1", result["full_check"])
        self.assertEqual(C.metric(s["streams"]["Tab1"])["turns"], 1)

    def ticket(self, s=None, p=None):
        s, p = s or setup(), p or probe()
        a = observe(s, p)["actions"][0]
        payload = {"action": a, "probe": p, "now": START}
        if a["kind"] == "SEND_DRAFT":
            token = a["aim_token"]
            payload["draft_scope_review"] = {"within_scope": True, "sequence": token["sequence"],
                "main_id": token["main_id"], "task_id": token["task_id"], "draft_hash": C.digest(p["draft"])}
        reserved = C.operate(s, "reserve", payload)
        self.assertEqual(reserved["result"], "RESERVED")
        return s, p, reserved["ticket"], a

    def test_old_message_cannot_prove_delivery(self):
        s, p, t, a = self.ticket()
        p["latest_user"]["hash"] = C.content_hash(a["text"])
        self.assertEqual(C.operate(s, "verify", {"ticket": t, "probe": p})["result"], "UNCERTAIN")
        self.assertIsNotNone(s["streams"]["Tab1"]["pending"])

    def test_new_message_and_exact_hash_prove_delivery_once(self):
        s, p, t, a = self.ticket()
        p["user_ids"].append("u2")
        p["latest_user"] = {"id": "u2", "hash": C.content_hash(a["text"])}
        for _ in range(2):
            self.assertEqual(C.operate(s, "verify", {"ticket": t, "probe": p})["result"], "DELIVERED")
        self.assertIsNone(s["streams"]["Tab1"]["pending"])

    def test_same_prefix_different_body_cannot_prove_delivery(self):
        s, p, t, a = self.ticket()
        p["user_ids"].append("u2")
        p["latest_user"] = {"id": "u2", "hash": C.content_hash(a["text"][:60] + "different ending")}
        self.assertEqual(C.operate(s, "verify", {"ticket": t, "probe": p})["result"], "UNCERTAIN")

    def test_full_url_not_short_id_controls_identity(self):
        s, p, t, a = self.ticket()
        p["url"] = URL2
        p["user_ids"].append("u2")
        p["latest_user"] = {"id": "u2", "hash": C.content_hash(a["text"])}
        self.assertEqual(C.operate(s, "verify", {"ticket": t, "probe": p})["result"], "UNCERTAIN")

    def test_pending_send_prevents_second_send(self):
        s, p, t, a = self.ticket()
        self.assertEqual(C.operate(s, "reserve", {"action": a, "probe": p})["result"], "STOP")

    def test_delivery_waits_for_new_finished_reply(self):
        s, p, t, a = self.ticket()
        p["user_ids"].append("u2")
        p["latest_user"] = {"id": "u2", "hash": C.content_hash(a["text"])}
        C.operate(s, "verify", {"ticket": t, "probe": p})
        self.assertEqual(observe(s, p)["actions"], [])
        self.assertTrue(observe(s, probe("a2"))["actions"])

    def test_draft_is_exact_and_has_priority(self):
        p = probe(draft="Owner text\nsecond line ")
        s, _, _, a = self.ticket(p=p)
        self.assertEqual(a["kind"], "SEND_DRAFT")
        self.assertEqual(a["text"], p["draft"])

    def test_changed_composer_rejects_reserved_action(self):
        s, p = setup(), probe(draft="Owner text")
        a = observe(s, p)["actions"][0]
        p["draft"] += " continued typing"
        self.assertEqual(C.operate(s, "reserve", {"action": a, "probe": p})["result"], "STOP")

    def test_hold_or_policy_change_rejects_action(self):
        s, p = setup(), probe()
        a = observe(s, p)["actions"][0]
        C.operate(s, "control", {"status": "HOLD"})
        self.assertEqual(C.operate(s, "reserve", {"action": a, "probe": p})["result"], "STOP")
        self.assertEqual(observe(s, probe(draft="Draft"))["actions"], [])

    def test_generating_held_and_missing_ids_do_not_send(self):
        for p in (probe(state="GENERATING"), probe(latest_user={"id": "", "hash": "x"}), probe(at_bottom=False)):
            result = observe(setup(), p)
            self.assertFalse(any(a.get("text") for a in result["actions"]))
        self.assertEqual(observe(setup(hold=True), probe(draft="x"))["actions"], [])

    def test_ping_uses_each_selected_interval(self):
        for interval in (10, 15, 30):
            s, p = setup(interval), probe(kind="OWNER", nxt=[])
            self.assertEqual(observe(s, p)["actions"], [])
            before = C.iso(C.stamp(START) + C.timedelta(minutes=interval - 1))
            after = C.iso(C.stamp(START) + C.timedelta(minutes=interval))
            self.assertEqual(observe(s, p, before)["actions"], [])
            self.assertEqual(observe(s, p, after)["actions"][0]["kind"], "PING")

    def test_ci_fallback_only_trusted_private_infrastructure(self):
        for private, verified, ci_kind, expected in ((True, True, "queue", "CI_FALLBACK"), (False, True, "queue", "CI_BLOCKED"), (True, False, "queue", "CI_BLOCKED"), (True, True, "test", "CI_BLOCKED"), (True, True, "unknown", "CI_BLOCKED")):
            s = setup(repo={"name": "r/c", "private": private, "verified": verified, "source": "github-api"})
            p = probe(kind="CI")
            p["status"]["ci_kind"] = ci_kind
            self.assertEqual(observe(s, p)["actions"][0]["kind"], expected)

    def test_private_ci_flag_persists_for_held_missing_chat(self):
        s = setup(hold=True, repo={"name": "r/c", "private": True, "verified": True, "source": "github-api"})
        observe(s, [])
        report = C.operate(s, "report", {})
        self.assertEqual(report["streams"][0]["ci"]["mode"], "limited")
        self.assertIn("CI limited (private)", report["table"])
        self.assertIn("held", report["table"])

    def test_public_and_unknown_visibility_not_flagged_private(self):
        for repo, expected in (({"private": False, "verified": True, "source": "github-api"}, "Normal CI"), ({"private": True}, "Visibility unverified")):
            report = C.operate(setup(repo=repo), "report", {})
            self.assertIn(expected, report["table"])
            self.assertNotIn("CI limited (private)", report["table"])

    def test_private_nudge_carries_ci_limit(self):
        s = setup(repo={"private": True, "verified": True, "source": "github-api"})
        result = observe(s, probe())
        self.assertIn("Private-repo CI is limited", result["actions"][0]["text"])

    def test_fallback_due_after_45_minutes(self):
        s, p = setup(speed="economy"), probe()
        observe(s, p)
        self.assertEqual(observe(s, p, "2026-10-11T10:30:00Z")["full_check"], [])
        self.assertEqual(observe(s, p, "2026-10-11T10:45:00Z")["full_check"], ["Tab1"])

    def test_pin_is_required_and_preserved(self):
        s = setup()
        p = probe(completed_messages=[{"id": f"a{i}", "minutes": 1} for i in range(6)])
        self.assertEqual(observe(s, p)["actions"][0]["kind"], "NEEDS_PIN")
        with self.assertRaises(ValueError):
            C.operate(s, "update", {"stream": "Tab1", "patch": {"buddy": {"repo": "r/c", "commit": "main"}}})
        s = setup(buddy={"repo": "r/c", "commit": "a" * 40, "stage": "work"})
        a = observe(s, p)["actions"][0]
        self.assertEqual(a["kind"], "HANDOVER")
        self.assertIn("a" * 40, a["text"])

    def test_duplicate_urls_rejected(self):
        with self.assertRaises(ValueError):
            C.operate({}, "init", {"interval": 15, "streams": {"one": {"url": URL}, "two": {"url": URL}}})

    def test_active_pin_cannot_change(self):
        s = setup(buddy={"repo": "r/c", "commit": "a" * 40, "stage": "1a_requested"})
        with self.assertRaises(ValueError):
            C.operate(s, "update", {"stream": "Tab1", "patch": {"buddy": {"repo": "r/c", "commit": "b" * 40, "stage": "1a_requested"}}})

    def test_new_chat_resets_meter_preserves_task_history(self):
        s = setup()
        observe(s, probe(done=["T1"], pages=25))
        validate(s, ["T1"])
        observe(s, probe(done=["T1"], pages=25))
        C.operate(s, "update", {"stream": "Tab1", "patch": {"url": URL2}})
        r = s["streams"]["Tab1"]
        self.assertEqual(C.metric(r), {"turns": 0, "minutes": 0, "pages": 0})
        self.assertIn("T1", r["closed"])
        self.assertEqual(r["evidence"], 1)
        self.assertIn("T1", r["claims"])
        self.assertEqual(r["message_history"][0]["url"], URL)

    def test_pending_send_serializes_all_streams(self):
        s = setup()
        C.operate(s, "update", {"stream": "Tab2", "patch": {"url": URL2, "ledger": ledger_config(tasks=["T2"]), "plan": {"rev": "r1", "tasks": [{"id": "T2", "outcome": "second"}]}}})
        p1, p2 = probe(), probe(url=URL2)
        result = observe(s, [p1, p2])
        a1, a2 = result["actions"]
        self.assertEqual(C.operate(s, "reserve", {"action": a1, "probe": p1})["result"], "RESERVED")
        self.assertEqual(C.operate(s, "reserve", {"action": a2, "probe": p2})["result"], "STOP")

    def test_unknown_state_not_overwritten(self):
        with self.assertRaises(ValueError):
            C.operate({"claude_code_log_anchor": 0}, "observe", {"probes": []})

    def test_lease_excludes_competing_cycle(self):
        s = setup()
        self.assertEqual(C.operate(s, "lease", {"owner": "one", "seconds": 180, "now": START})["result"], "LEASED")
        self.assertEqual(C.operate(s, "lease", {"owner": "two", "now": START})["result"], "BUSY")
        self.assertEqual(C.operate(s, "observe", {"owner": "two", "probes": [probe()], "now": START})["result"], "BUSY")

    def test_failed_atomic_replace_preserves_state(self):
        with temporary_directory() as d:
            path = Path(d) / "state.json"
            path.write_text('{"old":1}', encoding="utf-8")
            with patch.object(C.os, "replace", side_effect=OSError("interrupted")):
                with self.assertRaises(OSError):
                    C.atomic_save(path, {"new": 2})
            self.assertEqual(json.loads(path.read_text()), {"old": 1})
            self.assertEqual(list(Path(d).glob("*.tmp")), [])

    def test_parallel_writers_preserve_updates(self):
        with temporary_directory() as d:
            state = Path(d) / "state.json"
            C.transaction(state, "init", {"interval": 15})
            jobs = []
            for n in range(12):
                source = Path(d) / f"input{n}.json"
                source.write_text(json.dumps({"stream": f"Tab{n}", "patch": {"url": f"https://chatgpt.com/c/conversation-{n}"}}), encoding="utf-8")
                jobs.append(subprocess.Popen([sys.executable, str(Path(C.__file__)), "--state", str(state), "update", "--input", str(source)], stdout=subprocess.PIPE, stderr=subprocess.PIPE))
            for job in jobs:
                out, error = job.communicate(timeout=30)
                self.assertEqual(job.returncode, 0, (out, error))
            result = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(len(result["streams"]), 12)
            self.assertEqual(result["revision"], 13)

    def test_plan_done_is_only_a_claim(self):
        s = setup(plan={"rev": "r1", "tasks": [{"id": "T1", "status": "done"}]})
        r = s["streams"]["Tab1"]
        observe(s, probe(done=["T1"]))
        self.assertEqual(r["plan"]["tasks"]["T1"]["status"], "claimed")
        self.assertEqual(r["evidence"], 0)
        self.assertEqual(r["closed"], {})
        self.assertEqual(C.operate(s, "report", {})["streams"][0]["progress"]["claimed"], 1)

    def test_no_ledger_blocks_product_nudges_and_drafts(self):
        for p in (probe(done=["T1"]), probe(draft="exact Owner text")):
            s = setup(ledger=None)
            result = observe(s, p)
            self.assertEqual(result["actions"][0]["kind"], "NEEDS_AIMS")
            self.assertFalse(any(a.get("text") for a in result["actions"]))
            self.assertEqual(s["streams"]["Tab1"]["evidence"], 0)

    def test_missing_ledger_is_not_created_by_reader(self):
        with temporary_directory() as directory:
            path = Path(directory) / "missing.sqlite"
            s = setup(ledger={"path": str(path.resolve()), "namespace": "work:missing", "workpack_id": "WP1"})
            self.assertEqual(observe(s, probe(), reviewed=False)["actions"][0]["kind"], "NEEDS_AIMS")
            self.assertFalse(path.exists())

    def test_ledger_config_rejects_relative_paths_and_demo_namespaces(self):
        for config in ({"path": "relative.sqlite", "namespace": "work:one", "workpack_id": "WP1"},
                       {"path": str(Path(__file__).resolve()), "namespace": "demo", "workpack_id": "WP1"}):
            with self.assertRaises(ValueError):
                setup(ledger=config)

    def test_every_finished_report_needs_current_review_even_without_footer(self):
        s = setup(handover_hold=True)
        for n in range(3):
            p = probe(f"support-{n}", status={})
            result = observe(s, p, reviewed=False)
            self.assertEqual(result["actions"][0]["kind"], "REVIEW_TASK_REPORT")
            self.assertEqual(result["actions"][0]["message_id"], f"support-{n}")
            self.assertFalse(result["actions"][0].get("text"))
        self.assertEqual(len(result["task_review_due"]), 3)
        self.assertEqual(s["streams"]["Tab1"]["evidence"], 0)

    def test_all_new_completed_message_ids_are_reviewed_once(self):
        s = setup()
        p = probe("a3", completed_messages=[{"id": f"a{i}"} for i in range(1, 4)])
        first = observe(s, p, reviewed=False)
        second = observe(s, p, reviewed=False)
        self.assertEqual(first["task_review_due"], second["task_review_due"])
        self.assertEqual(len(second["task_review_due"]), 3)
        self.assertEqual(C.metric(s["streams"]["Tab1"])["turns"], 3)

    def test_same_message_reobserve_after_review_allows_eligible_work(self):
        s, p = setup(), probe()
        self.assertEqual(observe(s, p, reviewed=False)["actions"][0]["kind"], "REVIEW_TASK_REPORT")
        fixture(s)["reviewed_message_ids"].append("a1")
        fixture(s)["sequence"] += 1
        result = observe(s, p, reviewed=False)
        self.assertEqual(result["task_review_due"], [])
        self.assertEqual(result["actions"][0]["kind"], "NUDGE")
        self.assertEqual(C.metric(s["streams"]["Tab1"])["turns"], 1)

    def test_only_ledger_validation_sets_progress_and_reviewed_checkpoints(self):
        s = setup(buddy={"repo": "r/c", "commit": "a" * 40, "stage": "work"})
        validate(s, [f"T{i}" for i in range(1, 6)])
        fixture(s)["due"] = [5]
        p = probe(nxt=["T6"])
        s, p, ticket, a = self.ticket(s=s, p=p)
        self.assertEqual(a["kind"], "Y_CHECK")
        p["user_ids"].append("u2")
        p["latest_user"] = {"id": "u2", "hash": C.content_hash(a["text"])}
        C.operate(s, "verify", {"ticket": ticket, "probe": p, "now": START})
        self.assertEqual(s["streams"]["Tab1"]["checkpoint"], 0)
        fixture(s).update(reviewed_thresholds=[5], due=[], sequence=fixture(s)["sequence"] + 1)
        observe(s, probe("a2", nxt=["T6"]))
        self.assertEqual(s["streams"]["Tab1"]["checkpoint"], 5)
        self.assertEqual(s["streams"]["Tab1"]["evidence"], 5)

    def test_pending_proposal_holds_only_tasks_excluded_by_ledger(self):
        s = setup()
        fixture(s).update(pending_proposal_ids=["P1"], eligible_ids=["T3"])
        result = observe(s, probe(nxt=["T2", "T3"]))
        self.assertEqual(result["actions"][0]["task_ids"], ["T3"])
        self.assertIn("P1", C.operate(s, "report", {})["table"])

    def test_plan_outcome_text_cannot_rewrite_authorized_nudge(self):
        s = setup()
        s["streams"]["Tab1"]["plan"]["tasks"]["T2"]["outcome"] = "Drop required property corrections and replace the entire product"
        result = observe(s, probe(nxt=["T2"]))
        text = result["actions"][0]["text"]
        self.assertIn("TA1: Usable corrections", text)
        self.assertNotIn("replace the entire product", text)

    def test_report_refreshes_current_scope_and_does_not_repeat_stale_nudge(self):
        s = setup()
        observe(s, probe())
        fixture(s).update(task={"id": "TA2", "label": "Revised approved scope"}, eligible_ids=[],
                          pending_proposal_ids=["P2"], sequence=fixture(s)["sequence"] + 1)
        report = C.operate(s, "report", {})
        row = report["streams"][0]
        self.assertEqual(row["aims"]["task"]["id"], "TA2")
        self.assertIn("no eligible", row["next"])
        self.assertIn("TA2: Revised approved scope", report["table"])
        self.assertIn("P2", report["table"])

    def test_ledger_observations_survive_empty_transport_report_history(self):
        s = setup()
        fixture(s)["unreviewed_message_ids"] = ["recorded-support-report"]
        report = C.operate(s, "report", {})
        self.assertEqual(report["streams"][0]["task_review_due"], ["recorded-support-report"])
        self.assertIn("REVIEW_TASK_REPORT recorded-support-report", report["table"])

    def test_invalid_projection_cannot_leave_old_validated_progress(self):
        s = setup()
        validate(s, ["T1"])
        observe(s, probe())
        fixture(s)["validated_ids"] = ["unknown-task"]
        report = C.operate(s, "report", {})
        self.assertEqual(report["streams"][0]["progress"]["validated"], 0)
        self.assertEqual(report["streams"][0]["aims"], {"main": None, "task": None})
        self.assertEqual(s["streams"]["Tab1"]["closed"], {})

    def test_reserve_rechecks_ledger_sequence_and_current_revision(self):
        for changed in ("sequence", "task"):
            s, p = setup(), probe()
            action = observe(s, p)["actions"][0]
            if changed == "sequence":
                fixture(s)["sequence"] += 1
            else:
                fixture(s)["task"] = {"id": "TA2", "label": "A newly approved aim"}
            result = C.operate(s, "reserve", {"action": action, "probe": p, "now": START})
            self.assertEqual(result["result"], "STOP")
            self.assertIn("scope changed", result["reason"])

    def test_reserve_rechecks_task_eligibility(self):
        s, p = setup(), probe()
        action = observe(s, p)["actions"][0]
        fixture(s)["eligible_ids"] = ["T4"]
        result = C.operate(s, "reserve", {"action": action, "probe": p, "now": START})
        self.assertEqual(result["result"], "STOP")
        self.assertIn("no longer eligible", result["reason"])

    def test_exact_draft_requires_matching_runner_scope_review(self):
        s, p = setup(), probe(draft="Owner exact text\nkeep spacing ")
        action = observe(s, p)["actions"][0]
        base = {"action": action, "probe": p, "now": START}
        self.assertEqual(C.operate(s, "reserve", base)["result"], "STOP")
        token = action["aim_token"]
        review = {"within_scope": True, "sequence": token["sequence"], "main_id": token["main_id"],
                  "task_id": token["task_id"], "draft_hash": C.digest(p["draft"])}
        for key, bad in (("draft_hash", C.digest(p["draft"].strip())), ("sequence", 0), ("task_id", "TA0"), ("within_scope", False)):
            supplied = {**review, key: bad}
            self.assertEqual(C.operate(s, "reserve", {**base, "draft_scope_review": supplied})["result"], "STOP")
        self.assertEqual(C.operate(s, "reserve", {**base, "draft_scope_review": review})["result"], "RESERVED")

    def test_live_error_visible_without_bottom_identity_and_no_send(self):
        s = setup(ledger=None)
        result = observe(s, probe(state="ERROR", at_bottom=False, live_error="Hmm... something seems to have gone wrong"))
        self.assertEqual(result["actions"][0]["kind"], "ERROR")
        self.assertFalse(result["actions"][0].get("text"))
        self.assertIn("something seems to have gone wrong", C.operate(s, "report", {})["table"])

    def test_recovery_without_ledger_reports_error_and_does_not_send(self):
        s, p = setup(ledger=None), probe(state="ERROR", live_error="Hmm... something seems to have gone wrong")
        action = observe(s, p)["actions"][0]
        self.assertEqual(action["kind"], "ERROR")
        self.assertFalse(action.get("text"))

    def test_recovery_requires_current_eligible_registered_work(self):
        s, p = setup(), probe(state="ERROR", live_error="Hmm... something seems to have gone wrong")
        fixture(s)["eligible_ids"] = ["T2"]
        action = observe(s, p)["actions"][0]
        self.assertEqual(action["kind"], "RECOVER")
        self.assertEqual(action["task_ids"], ["T2"])
        self.assertEqual(C.operate(s, "reserve", {"action": action, "probe": p, "now": START})["result"], "RESERVED")

    def test_recovery_and_ci_fallback_cannot_bypass_adoption_gap(self):
        s = setup(repo={"private": True, "verified": True, "source": "github-api"})
        fixture(s)["eligible_ids"] = []
        error = observe(s, probe(state="ERROR", live_error="Hmm... something seems to have gone wrong"))
        self.assertEqual(error["actions"][0]["kind"], "ERROR")
        p = probe(kind="CI")
        p["status"]["ci_kind"] = "queue"
        fallback = observe(s, p)
        self.assertEqual(fallback["actions"][0]["kind"], "CI_BLOCKED")
        self.assertFalse(any(a.get("text") for a in fallback["actions"]))

    def legacy(self):
        s = setup(ledger=None, hold=True)
        s.update(schema=1, version="3.27", status="RUNNING", epoch=7, heartbeat="saved-heartbeat")
        r = s["streams"]["Tab1"]
        r.update(closed={"T1": {"rev": "r1", "message": "old-a1"}}, evidence=1, checkpoint=5,
                 pending={"ticket": "uncertain-legacy", "kind": "NUDGE", "before": ["old-u1"],
                          "assistant": "old-a1", "hash": "saved-hash", "reserved": START})
        r["plan"]["tasks"]["T1"]["status"] = "done"
        r["messages"] = {"old-a1": {"minutes": 2, "pages": None}}
        return s

    def test_upgrade_holds_preserves_mapping_pending_claims_history(self):
        s = self.legacy()
        pending = copy.deepcopy(s["streams"]["Tab1"]["pending"])
        s["lease"] = {"owner": "old-cycle", "until": "2026-10-11T09:59:00Z"}
        result = C.operate(s, "upgrade", {"now": START})
        r = s["streams"]["Tab1"]
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual((s["schema"], s["version"], s["epoch"]), (2, "3.28", 8))
        self.assertEqual(r["pending"], pending)
        self.assertEqual(s["heartbeat"], "saved-heartbeat")
        self.assertEqual(s["lease"]["owner"], "old-cycle")
        self.assertTrue(r["hold"])
        self.assertEqual(r["url"], URL)
        self.assertIn("old-a1", r["messages"])
        self.assertIn("T1", r["claims"])
        self.assertEqual((r["closed"], r["evidence"], r["checkpoint"]), ({}, 0, 0))
        self.assertEqual(r["plan"]["tasks"]["T1"]["status"], "claimed")
        self.assertEqual(r["plan_history"][0]["tasks"]["T1"]["status"], "done")

    def test_upgrade_rejects_active_lease_without_partial_mutation(self):
        s = self.legacy()
        s["lease"] = {"owner": "old-cycle", "until": "2026-10-11T10:01:00Z"}
        original = copy.deepcopy(s)
        with self.assertRaises(ValueError):
            C.operate(s, "upgrade", {"now": START})
        self.assertEqual(s, original)

    def test_upgrade_rejects_unknown_or_already_upgraded_state(self):
        for s in ({"claude_code_log_anchor": 0}, setup()):
            with self.assertRaises(ValueError):
                C.operate(s, "upgrade", {"now": START})

    def test_real_read_only_ledger_review_validation_and_reserve(self):
        with temporary_directory() as directory:
            path = Path(directory) / "aims.sqlite"
            namespace = "work:offline-integration"
            with REAL_STORE(path) as store:
                for identifier, kind in (("MA1", "main"), ("TA1", "task")):
                    store.register_aim({"id": identifier, "aim_type": kind, "label": "Offline fixture goal",
                        "criteria": [{"id": "C1", "text": "Fixture acceptance"}],
                        "excluded_scope": ["Any live action"], "authority_ref": "Offline test supplied instruction", "active": True}, namespace)
                for tid in ("T1", "T2"):
                    store.register_task({"id": tid, "aim_id": "TA1", "recipient": URL, "workpack_id": "WP1",
                        "criterion_ids": ["C1"], "expected_proof": ["C1"]}, namespace)
                s = setup(ledger={"path": str(path.resolve()), "namespace": namespace, "workpack_id": "WP1"})
                p = probe(done=["T1"])
                with patch.object(C, "AimStore", REAL_STORE):
                    before = C.digest(path.read_bytes().hex())
                    result = observe(s, p, reviewed=False)
                    self.assertEqual(result["actions"][0]["kind"], "REVIEW_TASK_REPORT")
                    self.assertEqual(s["streams"]["Tab1"]["evidence"], 0)
                    self.assertEqual(C.digest(path.read_bytes().hex()), before)
                    store.append("report", {"id": "R1", "message_id": "a1", "recipient": URL, "workpack_id": "WP1"}, namespace)
                    store.append("control", {"id": "review-a1", "control_type": "TASK_REPORT_REVIEW",
                        "message_id": "a1", "recipient": URL, "workpack_id": "WP1", "report_id": "R1",
                        "reason": "Offline review; claimed task still needs proof", "source_ref": "offline a1",
                        "alignment": "ALIGNED", "assessment_ids": []}, namespace)
                    result = observe(s, p, reviewed=False)
                    self.assertEqual(result["actions"][0]["kind"], "NUDGE")
                    store.record_evidence({"id": "E1", "task_id": "T1", "aim_id": "TA1",
                        "artifact": "simulated-artifact", "criterion_ids": ["C1"], "result": "PASS", "verified": True,
                        "summary": "Synthetic test result", "proof_source": "offline fixture",
                        "test_input": "synthetic input", "limitation": "No live engineering acceptance"}, namespace)
                    store.assess_task({"id": "A1", "task_id": "T1", "aim_id": "TA1", "artifact": "simulated-artifact",
                        "verdict": "VALIDATED", "evidence_ids": ["E1"], "reason": "Offline checked fixture"}, namespace)
                    action = observe(s, p, reviewed=False)["actions"][0]
                    self.assertEqual(s["streams"]["Tab1"]["evidence"], 1)
                    self.assertEqual(action["task_ids"], ["T2"])
                    store.append("roi", {"id": "ROI-new", "claim": "Unmeasured offline suggestion"}, namespace)
                    result = C.operate(s, "reserve", {"action": action, "probe": p, "now": START})
                    self.assertEqual(result["result"], "STOP")
                    self.assertIn("scope changed", result["reason"])


if __name__ == "__main__":
    unittest.main()
