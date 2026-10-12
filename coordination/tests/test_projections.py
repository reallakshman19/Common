"""WP3 ADV-09..16: producer, private API, provider-independent assertions."""
import json
import socketserver
import sqlite3
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from coordination.contracts import (
    Project, Work, ExecutionLane, AgentAssignment, AgentRun, TabBinding, ControlTowerRegistry,
)
from coordination.indexer import EvidenceIndex
from coordination.projections import ProjectionEngine, ProjectionQueryService
from coordination.coordination_ui import ApiHandler


ASOF = "2026-10-12T12:00:00Z"
CHILD = "reallakshman19/Common#353"


def setup_registry():
    reg = ControlTowerRegistry()
    for pid in ("common", "grade9"):
        reg.register_project(Project(pid,pid,"https://github.com/example/"+pid,
            "coordination", "ACTIVE" if pid=="common" else "DEGRADED",ASOF,
            "REACHABLE" if pid=="common" else "RATE_LIMITED"))
    snapshots = {}
    for i in range(5):
        pid = "common" if i<3 else "grade9"
        wid, lid, aid, rid = (f"{pid}-work-{i}",f"{pid}-lane-{i}",
                               f"{pid}-assignment-{i}",f"{pid}-run-{i}")
        reg.register_work(Work(wid,pid,f"AIM-{i}","5f9065d",
            f"https://github.com/example/{pid}/issues/{i+1}","IN_PROGRESS"))
        reg.register_lane(ExecutionLane(lid,wid,"DEVELOPMENT"))
        reg.register_assignment(AgentAssignment(aid,lid,f"RESP-{i}",
            "PRIMARY_IMPLEMENTER","ACTIVE"))
        tab = "Tab3" if i in (0,3) else "Tab5" if i == 2 else f"Tab{i+1}"
        chat = "same-chat" if i in (0,3) else f"chat-{i}"
        reg.register_run(AgentRun(rid,aid,1,chat,ASOF,0,"IN_PROGRESS"))
        reg.register_binding(TabBinding(f"binding-{i}",rid,pid,tab,1,"ACTIVE",
                                        session_alias="Session_One"))
        snap=snapshots.setdefault(pid,{"schema_version":"v1.0.0",
            "project_id":pid,"coordinator_id":"coord-1",
            "session_id":"Session_One","generated_at_utc":ASOF,
            "source_digest":"a"*64,"source_watermark":"cycle-1",
            "cycle_seconds":900,"observations":[]})
        snap["observations"].append({
            "tab":tab, "status":f"status-{i}", "aim":"-","plan":"-","ac":"-",
            "ci":"CI_UNKNOWN","meter":"-","due":"-","checked":"-",
            "next":f"original coordinator next {i}",
            "tab_position":tab.replace("Tab",""),"chat_id":chat,
            "binding_generation":1,"probe_status":"SUCCESS",
            "last_probe_at_utc":"2026-10-12T11:59:00Z",
            "observed_at_utc":ASOF
        })
    return reg,list(snapshots.values())


def canonical():
    return ("Outcome: O1\nFor the user: Evidence projection is read only\n"
            "Proof: https://github.com/reallakshman19/Common/issues/353\n"
            "TASK_EVIDENCE v3.6\nTask: WP3-353-W01\n"
            "Child issue: reallakshman19/Common#353\n"
            "Candidate: "+"a"*40+"\nTests: 1/1\n")


class TestWP3MaterializedProjections(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        self.reg,self.snaps=setup_registry()
        self.idx=EvidenceIndex(str(self.root/"source.sqlite"))
        self.idx.update_project_status("common","GITHUB_ISSUE_COMMENT","REACHABLE")
        self.idx.update_project_status("grade9","GITHUB_ISSUE_COMMENT","RATE_LIMITED")
        self.path=str(self.root/"materialized.sqlite")
        self.engine=ProjectionEngine(self.path)
        self.asof=ASOF
        self.wm={"common":"source-v1","grade9":"source-v2"}

    def tearDown(self):
        self.idx.close()
        self.tmp.cleanup()

    def build(self,**kw):
        return self.engine.materialize(self.reg,self.idx,self.snaps,
                   kw.pop("as_of_utc",self.asof),
                   kw.pop("source_watermarks",self.wm),**kw)

    def rows(self,view,project=None,limit=200,cursor=None):
        return ProjectionQueryService(self.path).page(view,project,limit,cursor)

    def test_adv09_five_agents_duplicate_tab3_and_chat_are_isolated(self):
        built=self.build()
        self.assertEqual(built["counts"]["assignments"],5)
        rows=self.rows("assignments")["items"]
        self.assertEqual(len(rows),5)
        self.assertEqual(len({(x["project_id"],x["assignment_id"]) for x in rows}),5)
        common=next(x for x in rows if x["project_id"]=="common" and x["tab"]=="Tab3")
        grade=next(x for x in rows if x["project_id"]=="grade9" and x["tab"]=="Tab3")
        self.assertNotEqual(common["assignment_id"],grade["assignment_id"])
        self.assertEqual(common["status"],"status-0")
        self.snaps[0]["observations"].append({
            **self.snaps[0]["observations"][0],
            "tab":"Tab8","tab_position":"8","chat_id":"unbound-chat",
            "status":"original unbound status"})
        self.build(source_watermarks={"common":"source-v2","grade9":"source-v2"})
        self.assertEqual(len(self.rows("assignments")["items"]),5)
        orphan=self.rows("unassigned_observations")["items"]
        self.assertEqual(len(orphan),1)
        self.assertEqual(orphan[0]["status"],"original unbound status")
        self.assertIsNone(orphan[0]["assignment_id"])

    def test_adv10_digest_is_deterministic_and_source_sensitive(self):
        a=self.build()["projection_digest"]
        self.assertEqual(a,self.build()["projection_digest"])
        other=ProjectionEngine(str(self.root/"second.sqlite"))
        self.assertEqual(a,other.materialize(self.reg,self.idx,self.snaps,self.asof,self.wm)["projection_digest"])
        self.snaps[0]["observations"][0]["status"]="provider-observed change"
        self.assertNotEqual(a,self.build()["projection_digest"])

    def test_adv11_staleness_provider_isolation(self):
        self.snaps[0]["observations"][0]["last_probe_at_utc"]="2026-10-12T10:00:00Z"
        self.build()
        cells={x["tab"]:x for x in self.rows("assignments","common")["items"]}
        self.assertEqual(cells["Tab3"]["agent_probe_freshness"],"STALE")
        self.assertEqual(cells["Tab2"]["agent_probe_freshness"],"ALIVE")
        p={x["project_id"]:x for x in self.rows("portfolio")["items"]}
        self.assertEqual(p["common"]["provider_reachability"],"REACHABLE")
        self.assertEqual(p["grade9"]["provider_reachability"],"RATE_LIMITED")

    def test_adv12_unattributed_evidence_not_inherited_by_run(self):
        self.idx.store_evidence("common",{
            "provider_comment_id":"9001","evidence_id":"comment-9001",
            "task_id":"WP3-353-W01","owner_issue":CHILD,
            "candidate_sha":"a"*40,"author":"source",
            "created_at":"2026-10-12T11:00:00Z",
            "raw_text":canonical(),"is_canonical_8line":True,
            "proof_url":"https://github.com/reallakshman19/Common/issues/353"})
        self.build()
        evidence=self.rows("evidence")["items"]
        self.assertEqual(evidence[0]["attribution"],"UNATTRIBUTED")
        self.assertIsNone(evidence[0]["run_id"])
        self.assertIsNone(self.rows("works","common")["items"][0]["evidenced_tasks"])
        mapping={
            "project_id":"common","task_id":"WP3-353-W01","child_issue":CHILD,
            "work_id":"common-work-0","assignment_id":"common-assignment-0",
            "run_id":"common-run-0",
            "source_ref":"https://github.com/reallakshman19/Common/issues/353",
            "source_revision":"plan-r3",
        }
        self.build(task_attributions=[mapping])
        e=self.rows("evidence")["items"][0]
        self.assertEqual(e["attribution"],"ATTRIBUTED")
        self.assertEqual(e["run_id"],"common-run-0")
        self.assertEqual(next(x for x in self.rows("works")["items"]
                              if x["work_id"]=="common-work-0")["evidenced_tasks"],1)
        self.assertEqual(e["validator_verdict"],None)

    def test_adv13_green_check_does_not_infer_owner_acceptance(self):
        self.build()
        for w in self.rows("works")["items"]:
            self.assertEqual(w["acceptance_status"],"IN_PROGRESS")
            self.assertEqual(w["ci_status"],"UNKNOWN")
            self.assertIsNone(w["tasks_total"])
            self.assertIsNone(w["accepted_ac"])

    def test_adv13_source_pinned_exact_head_ci_and_skipped_never_accept_work(self):
        binding={"project_id":"common","work_id":"common-work-0",
                 "repo_id":"987","pr_number":500,
                 "current_head_sha":"b"*40,"observed_at_utc":ASOF,
                 "source_ref":"https://github.com/reallakshman19/Common/pull/500",
                 "required_jobs":["build"]}
        def check(check_id,sha,result,observed):
            self.idx.store_check_observation({
                "check_id":check_id,"project_id":"common","repo_id":"987",
                "pr_number":500,"head_sha":sha,"workflow_name":"build",
                "job_name":"build","applicability":"PATH_SCOPED",
                "conclusion":result,"run_url":"https://github.com/reallakshman19/Common/actions",
                "observed_at":observed})
        check("old-head","a"*40,"EXACT_HEAD_PASSED","2026-10-12T11:55:00Z")
        self.build(pr_bindings=[binding])
        row=next(x for x in self.rows("works")["items"] if x["work_id"]=="common-work-0")
        self.assertEqual(row["ci_status"],"OLD_HEAD")
        check("skipped-head","b"*40,"GREEN_NOT_APPLICABLE","2026-10-12T11:56:00Z")
        self.build(pr_bindings=[binding])
        row=next(x for x in self.rows("works")["items"] if x["work_id"]=="common-work-0")
        self.assertEqual(row["ci_status"],"NOT_APPLICABLE")
        check("current-success","b"*40,"EXACT_HEAD_PASSED","2026-10-12T11:59:00Z")
        self.build(pr_bindings=[binding])
        row=next(x for x in self.rows("works")["items"] if x["work_id"]=="common-work-0")
        self.assertEqual(row["ci_status"],"EXACT_HEAD_PASSED")
        self.assertEqual(row["acceptance_status"],"IN_PROGRESS")
        stale={**binding,"observed_at_utc":"2026-10-12T09:00:00Z"}
        self.build(pr_bindings=[stale])
        row=next(x for x in self.rows("works")["items"] if x["work_id"]=="common-work-0")
        self.assertEqual(row["ci_status"],"UNKNOWN")

    def test_adv14_only_factual_recovery_with_original_next(self):
        self.snaps[0]["observations"][0]["probe_status"]="LOADFAIL"
        self.build()
        r=self.rows("recovery")["items"]
        bad=next(x for x in r if x["anomaly_type"]=="PROBE_FAILURE")
        self.assertEqual(bad["coordinator_next"],"original coordinator next 0")
        self.assertNotIn("recommended_action",bad)
        self.assertEqual(bad["status_verbatim"],"status-0")

    def test_adv15_keyset_generation_cursor_and_bounded_pages(self):
        self.build()
        first=self.rows("assignments",limit=2)
        second=self.rows("assignments",limit=2,cursor=first["next_cursor"])
        self.assertEqual(len(first["items"]),2)
        self.assertEqual(len(second["items"]),2)
        ids=[x["assignment_id"] for x in first["items"]+second["items"]]
        self.assertEqual(len(set(ids)),4)
        with self.assertRaises(ValueError):
            self.rows("assignments",limit=201)
        with self.assertRaises(ValueError):
            self.rows("assignments",limit=2,cursor="wrong%%%")
        self.snaps[0]["observations"][0]["status"]="new generation"
        self.build(source_watermarks={"common":"cycle2","grade9":"cycle1"})
        with self.assertRaises(LookupError):
            self.rows("assignments",limit=2,cursor=first["next_cursor"])

    def test_adv15_ten_thousand_evidence_rows_are_paged_without_bulk_load(self):
        # Ingest is deliberately out-of-scope here: populate source SQLite in
        # one transaction to stress the WP3 materializer's 200-row fetchmany.
        raw=canonical()
        rows=[(f"bulk-{i}", "common", str(100000+i),
               "WP3-353-W01", CHILD, "a"*40, None, "source",
               "2026-10-12T11:00:00Z", None, "a"*64,
               "https://github.com/reallakshman19/Common/issues/353",
               1, raw, 1, 1) for i in range(10000)]
        with self.idx._lock, self.idx._get_connection() as conn:
            conn.executemany(
                """INSERT INTO task_evidence(
                   evidence_id,project_id,provider_comment_id,task_id,owner_issue,
                   candidate_sha,pr_number,author,created_at,updated_at,
                   content_sha,proof_url,is_canonical_8line,raw_text,version,is_active_version)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
        import tracemalloc
        tracemalloc.start()
        try:
            built=self.build()
            peak=tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
        self.assertEqual(built["counts"]["evidence"],10000)
        self.assertLess(peak,50*1024*1024)
        seen=0
        cur=None
        while True:
            page=self.rows("evidence",limit=200,cursor=cur)
            self.assertLessEqual(len(page["items"]),200)
            seen+=len(page["items"])
            cur=page["next_cursor"]
            if not cur:
                break
        self.assertEqual(seen,10000)

    def test_private_cli_materializer_reads_explicit_pinned_sources_only(self):
        from dataclasses import asdict
        from coordination.projections import materialize_manifest
        source={
            "schema_version":"WP3_PRIVATE_MANIFEST_V1",
            "registry_source_ref":"https://github.com/reallakshman19/Common/issues/353",
            "source_watermarks":self.wm,
            "projects":[asdict(x) for x in self.reg.projects.values()],
            "works":[asdict(x) for x in self.reg.works.values()],
            "execution_lanes":[asdict(x) for x in self.reg.lanes.values()],
            "assignments":[asdict(x) for x in self.reg.assignments.values()],
            "runs":[asdict(x) for x in self.reg.runs.values()],
            "tab_bindings":[asdict(x) for x in self.reg.bindings.values()],
            "observation_files":["coordinator-a.json","coordinator-b.json"],
        }
        for name,snap in zip(source["observation_files"],self.snaps):
            (self.root/name).write_text(json.dumps(snap),encoding="utf-8")
        manifest=self.root/"wp3-manifest.json"
        manifest.write_text(json.dumps(source),encoding="utf-8")
        result=materialize_manifest(str(manifest),self.idx.db_path,self.path,ASOF)
        self.assertEqual(result["counts"]["assignments"],5)
        self.assertEqual(len(self.rows("assignments")["items"]),5)
        source["observation_files"]=["../private.json"]
        manifest.write_text(json.dumps(source),encoding="utf-8")
        with self.assertRaises(ValueError):
            materialize_manifest(str(manifest),self.idx.db_path,self.path,ASOF)
        self.assertEqual(len(self.rows("assignments")["items"]),5)

    def test_adv16_private_api_get_never_creates_or_writes_db(self):
        self.build()
        before=Path(self.path).stat().st_mtime_ns
        class Handler(ApiHandler):
            pass
        Handler.config={"projects":[{"id":"common","name":"Common"},{"id":"grade9","name":"Grade9"}],
                        "server":{"projection_db_path":self.path}}
        Handler.server_host="127.0.0.1"
        with socketserver.TCPServer(("127.0.0.1",0),Handler) as server:
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                addr=f"http://127.0.0.1:{server.server_address[1]}"
                with urllib.request.urlopen(addr+"/api/v3/projections?view=assignments&limit=2") as response:
                    body=json.load(response)
                self.assertEqual(len(body["items"]),2)
                self.assertEqual(body["schema_version"],"control_tower_projections_v1")
                for suffix,code in (("?view=invalid",400),
                                    ("?view=portfolio&project=not-a-project",404),
                                    ("?view=portfolio&cursor=broken%%%",400)):
                    with self.subTest(suffix=suffix):
                        with self.assertRaises(urllib.error.HTTPError) as ctx:
                            urllib.request.urlopen(addr+"/api/v3/projections"+suffix)
                        self.assertEqual(ctx.exception.code,code)
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    req=urllib.request.Request(addr+"/api/v3/projections")
                    req.add_header("Host","evil.example")
                    urllib.request.urlopen(req)
                self.assertEqual(ctx.exception.code,400)
            finally:
                server.shutdown();thread.join(timeout=4)
        self.assertEqual(before,Path(self.path).stat().st_mtime_ns)


if __name__=="__main__":
    unittest.main()
