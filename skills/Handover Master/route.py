#!/usr/bin/env python3
"""Single read-only decision entry for Common handover workflows.

Returns a route and canonical reading/validation requirements. It NEVER executes
a generator, writes GitHub, publishes an Owner decision or advances a phase.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO_ROOT=HERE.parents[1]
ALLOWED_MODES={"auto","technical","two-pass","three-pass","buddy","zero-exit","status"}
WORKFLOWS={"auto","standalone","v3.6","v3.5"}
VERSIONS={"1.6","1.7"}
PHASES={"1a","1b","2","Y"}
ROUTES={"technical":"technical","zero-exit":"onb","status":"observer"}
GUARDED=(
 "Never execute, post, merge, deploy, change task ownership or send an Owner response merely from routing.",
 "Re-fetch current canonical SKILL and schema and verify source/blob SHA before prompt generation.",
 "Treat historical source claims, PRs, check runs and original input bytes as different authority classes.",
 "A generated report or a PASS is not a protected Owner approval or proof of a complete functional oracle.",
 "Never expose Stage-1 quarantined or private information to an independent/blind recipient.",
 "CoordinatorLandingpage is only a later read-only consumer; do not modify its existing site or protocol."
)

def match_mode(intent):
    raw=(intent or "").casefold()
    tokens={
      "status":r"\b(show|check|view|monitor|track)\b.{0,40}\b(progress|status|stage)\b|\bprogress dashboard\b",
      "buddy":r"\bbuddyrunner\b|\b1a\s*(?:→|->)\s*1b\b|\bxb\s*(?:→|->)\s*y\b",
      "zero-exit":r"\bzero.exit\b|\babrupt (?:exit|handover)\b|\bno predecessor\b|\bno outgoing\b|\bwithout (?:a )?(?:handover|log)\b|\bcold successor\b",
      "technical":r"\btechnical handover\b|\b12.section (?:report|handover)\b|\btechnical report\b",
      "two-pass":r"\btwo.pass\b|\b2.pass\b|\bindependent baseline\b|\bblind baseline\b",
      "three-pass":r"\bthree.pass\b|\b3.pass\b|\bprompt 2\.5\b|\bprogramme imagination\b|\bq1.q5\b"
    }
    hits=[name for name,pattern in tokens.items() if re.search(pattern,raw)]
    if not hits:return None,hits
    if len(hits)>1:return None,hits
    return hits[0],hits

def route(intent="",mode="auto",workflow="auto",phase=None,buddy_version=None,
          stage1_freeze_verified=False):
    if mode not in ALLOWED_MODES or workflow not in WORKFLOWS:
        raise ValueError("invalid mode/workflow")
    if phase is not None and phase not in PHASES:
        raise ValueError("invalid Buddy phase")
    if buddy_version is not None and buddy_version not in VERSIONS:
        raise ValueError("invalid Buddy version")
    index=json.loads((HERE/"sources.json").read_text(encoding="utf-8"))
    auto_hits=[]
    if mode=="auto":
        mode,auto_hits=match_mode(intent)
        if mode is None:
            return decision("NEEDS_SELECTION",None,
                            "Ambiguous or absent request: explicitly select handover, 2pass, 3pass, Buddy, zero-exit, or status.",
                            choices=auto_hits or sorted(ALLOWED_MODES-{"auto"}))
    if workflow=="v3.5" and mode not in ("status","technical"):
        return decision("HOLD",None,
                        "Historical v3.5 has distinct live-source and ownership rules; do not route new generators through it.",
                        choices=["technical","status"])
    if mode=="buddy":
        if not buddy_version:
            return decision("NEEDS_VERSION",None,
                            "Select the exact project-governing BuddyRunner version (1.6 or 1.7).")
        if phase is None:
            return decision("NEEDS_PHASE",None,
                            "Supply 1a, 1b, 2 or Y from live owning issue; do not repeat a completed phase.")
        source_key="buddy16" if buddy_version=="1.6" else "buddy17"
        reason="Execute only this explicitly selected BuddyRunner phase; 1a is preparation/HOLD, not automatic 1b execution."
        checks=[
         "Read actual owning issue and completed phase receipts; reject duplicates or stale G2 evidence.",
         "For 2 require authentic previous 1b body and source digest; for Y require exact Task Evidence Xb.",
         "Respect the 1a→1b→2 (or one Xb→Y) boundary: no acknowledgement loop.",
         "Check existing workflow permissions; phase publication requires separate scope authority."
        ]
    elif mode=="technical":
        if not stage1_freeze_verified:
            return decision("HOLD_FREEZE",None,
                 "Native HANDOVER_TECHNICAL_V2 is Stage2-after-authenticated-Stage1-freeze only. No verified isolation: do not expose predecessor implementation.")
        source_key="technical"
        reason="Use native twelve-section technical report after verified isolation, without replacing PLAN_HANDOVER/HANDOVER_CONTEXT."
        checks=[
         "Prove the Stage-1 blind snapshot was independently frozen and its recipient isolation verified.",
         "Bind the report to native PLAN_HANDOVER and HANDOVER_CONTEXT, not chat memory.",
         "Trace exact source→entrypoint→owning function→consumer and separate historical/main/PR/test SHAs.",
         "Represent absent data as NOT_PUBLISHED, UNKNOWN, NOT_VERIFIED or NOT_RUN."
        ]
    elif mode in ("two-pass","three-pass"):
        if workflow=="v3.6":
            source_key="v36"
            selected_script="two_script" if mode=="two-pass" else "three_script"
            reason="v3.6-governed work uses its own "+mode+" prompt generator and label/plan authority."
            checks=[
              "Re-fetch exact Owner-approved relay/AIM/<WORK>.yaml label and selected plan; verify work/version/label_sha and parent.",
              "Read current v3.6 SKILL and selected generator script; do not substitute the standalone generator.",
              "Explicit --lab from the label is needed for lab routes; dry-run and no write without --apply and --confirm-scope.",
              "Preserve current v3.6 O1–O5 lifecycle and its native 2-/3-pass scope, test exact source and never invent authorization."
            ]
        else:
            source_key="two_standalone" if mode=="two-pass" else "three_standalone"
            selected_script=None
            reason=("Exactly two schema-defined prompts with a genuinely task-blind independent Pass 1."
                    if mode=="two-pass" else
                    "Schema-defined Prompt 0.5/1/2/2.5/3; independently imagine, inspect reality and reconcile.")
            checks=[
              "Fetch the canonical schema at current main THIS RUN, establish protocol revision and actual schema SHA.",
              "Emit the canonical SCHEMA EXECUTION HANDSHAKE first; if fetch fails, emit only the schema-defined FAIL.",
              ("Keep Pass 1 unaware of issue/task/PR, suggested fix, confidential answers and work orders." if mode=="two-pass"
               else "Quarantine current answers from early prompts; keep Prompt 0.5/1 independent of current solution."),
              "Generate exactly the canonical prompt count; run the native validate.py without inserting extra stages.",
              "Owner approval and source-provider readback are separate from generator success."
            ]
    else:
        source_key=ROUTES[mode]
        selected_script=None
        if mode=="zero-exit":
            reason="Compile source-referenced 12-section ONB report even without a predecessor LOG; current public WP5 is BLOCKED by default."
            checks=[
              "Read current ONB WP5 compiler and validator and its known fixture/source HEAD limitations.",
              "Do not pretend draft WP1a–WP4 modules are available on Common main; inspect their PRs separately.",
              "Regenerate from fresh authenticated provider observations; an old --live fixture cutoff should fail STALE.",
              "Use SHA manifest/verdict, retain UNKNOWN and Owner approval BLOCKED; RWI NOT_EVALUATED."
            ]
        else:
            reason="Observe workflow progress read-only. Do not start or advance BuddyRunner or any other handover stage."
            checks=[
              "Read current workflow and status source, not old chat progress claims.",
              "No GitHub write, controller assignment, timer creation or Owner-approval claim."
            ]
    source=index["sources"][source_key]
    read=[source["path"]]
    if mode in ("two-pass","three-pass") and workflow=="v3.6":
        read.append(source[selected_script])
    elif source_key in ("two_standalone","three_standalone"):
        read.extend([source["schema"],source["validator"]])
    elif source_key=="onb":
        read.extend([source["compiler"],source["validator"]])
    elif source_key in ("buddy16","buddy17"):
        read.append(source["script"])
    action="READ_SOURCE_NOW"
    return {
      "schema":"handover-master.route/v1","status":action,
      "selection":{"mode":mode,"workflow":workflow,
                   "phase":phase if mode=="buddy" else None,
                   "buddy_version":buddy_version if mode=="buddy" else None,
                   "source_key":source_key},
      "canonical_read_paths":read,
      "repo":"reallakshman19/Common",
      "reason":reason,"preflight":checks,"global_guards":list(GUARDED),
      "may_execute_generator":False,"may_write_or_publish":False,
      "owner_approval_verified":False,
      "source_freshness_verified":False
    }

def decision(status,mode,reason,choices=None):
    return {
      "schema":"handover-master.route/v1","status":status,
      "selection":None,"canonical_read_paths":[],
      "reason":reason,"choices":choices or [],
      "may_execute_generator":False,"may_write_or_publish":False,
      "owner_approval_verified":False,"source_freshness_verified":False
    }

def as_markdown(item):
    lines=["# Handover Master decision: "+item["status"],"",
           "**Reason:** "+item["reason"],""]
    if item.get("selection"):
        s=item["selection"]
        lines += ["**Selected:** "+s["mode"]+" / "+s["source_key"],
                  "**Workflow:** "+s["workflow"],""]
        lines += ["## Read these current-main sources, in this order"]
        lines += ["- ["+p+"](https://github.com/reallakshman19/Common/blob/main/"+p.replace(" ","%20")+")"
                  for p in item["canonical_read_paths"]]
        lines += ["","## Preflight (not a write grant)"]
        lines += ["- "+p for p in item["preflight"]]
    elif item.get("choices"):
        lines += ["**Choices:** "+", ".join(item["choices"])]
    lines += ["","**Safety:** Router made no provider read, file edits, generator invocation or Owner decision."]
    return "\n".join(lines)+"\n"

def main(argv=None):
    p=argparse.ArgumentParser(description="One read-only entry: choose canonical handover/2pass/3pass/Buddy/ONB/status")
    p.add_argument("--intent",default="",help="natural language intent (auto mode)")
    p.add_argument("--mode",choices=sorted(ALLOWED_MODES),default="auto")
    p.add_argument("--workflow",choices=sorted(WORKFLOWS),default="auto")
    p.add_argument("--phase",choices=sorted(PHASES))
    p.add_argument("--buddy-version",choices=sorted(VERSIONS))
    p.add_argument("--stage1-freeze-verified",action="store_true")
    p.add_argument("--format",choices=["json","markdown"],default="markdown")
    args=p.parse_args(argv)
    result=route(args.intent,args.mode,args.workflow,args.phase,args.buddy_version,args.stage1_freeze_verified)
    print(as_markdown(result) if args.format=="markdown" else json.dumps(result,indent=2))
    return 0 if result["status"]=="READ_SOURCE_NOW" else 2

if __name__=="__main__":
    raise SystemExit(main())
