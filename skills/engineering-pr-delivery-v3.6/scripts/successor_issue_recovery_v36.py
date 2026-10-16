#!/usr/bin/env python3
"""Read-only R3 report assembly for the existing native v3.6 successor.

This is not an independent handover generator or publisher. An existing
successor_v36.py cold invocation owns the CLI and uses this pure renderer.
Source content is untrusted; published reports grant no protected authority.
"""
from __future__ import annotations
import hashlib
import re

from issue_spine_read_v36 import audit, parse, SpineError

SECTIONS=(
 "Original Owner problem and why",
 "Required outcomes and acceptance",
 "Later Owner amendments and corrections",
 "Original input fixtures, goldens and benchmarks",
 "Repository source authority and current cut",
 "Causal input-to-output implementation path",
 "Agent contributions and event chronology",
 "Decisions, improvements and parked ideas",
 "Issue lineage and conversation provenance",
 "Executed tests and observed results",
 "Unresolved defects, drift and permission gates",
 "Next reproducible verification and successor handover",
)
STATUSES={"REPORTED_SOURCE","OBSERVED_SOURCE_SCOPE","UNKNOWN_REQUIRES_EVIDENCE"}

class RecoveryError(ValueError):
    pass

def guard(ok,reason):
    if not ok:
        raise RecoveryError(reason)

def sanitize(value,cap=2400):
    out=str(value)
    for a,b in (("&","&amp;"),("<","&lt;"),(">","&gt;"),
                (chr(96),"&#96;"),("|","&#124;"),("\r"," "),("\n"," ")):
        out=out.replace(a,b)
    return out[:cap]

def subsection(body,title,cap=1000):
    match=re.search(r"(?m)^## "+re.escape(title)+r"[^\n]*\n",body)
    if not match:
        return None
    start=match.end()
    next_head=re.search(r"(?m)^## ",body[start:])
    end=start+next_head.start() if next_head else len(body)
    content=body[start:end].strip()
    return sanitize(content[:cap]) if content else None

def source_comment(reader,repo,observed):
    match=re.fullmatch(r"https://github\.com/"+re.escape(repo)+
        r"/issues/([1-9][0-9]*)#issuecomment-([1-9][0-9]*)",
        observed["url"])
    guard(match is not None,"R3_COMMENT_URL_INVALID")
    item=reader.get("/repos/"+repo+"/issues/comments/"+match[2])
    body=item.get("body") if isinstance(item,dict) else None
    guard(isinstance(body,str) and
          item.get("id")==int(match[2]) and
          item.get("issue_url")=="https://api.github.com/repos/"+repo+
                               "/issues/"+match[1] and
          item.get("user",{}).get("login","").casefold()==
          observed["actor"].casefold() and
          hashlib.sha256(body.encode()).hexdigest()==observed["body_sha256"],
          "R3_SOURCE_DRIFT_AFTER_VERIFIED_READ")
    return body

def verify_sections(doc):
    guard(isinstance(doc,dict) and doc.get("schema")==
          "V36_NATIVE_R3_COLD_HANDOVER_V1","R3_SCHEMA_INVALID")
    all_src=doc.get("sources")
    rows=doc.get("sections")
    guard(isinstance(all_src,dict) and isinstance(rows,list) and len(rows)==12,
          "R3_REQUIRES_EXACTLY_12_SECTIONS")
    for i,row in enumerate(rows):
        guard(isinstance(row,dict) and set(row)==
              {"number","title","evidence","content","source_refs"} and
              row["number"]==i+1 and row["title"]==SECTIONS[i],
              "R3_SECTION_ORDER_INVALID")
        guard(row["evidence"] in STATUSES and isinstance(row["content"],str)
              and len(row["content"].strip())>=40,"R3_SECTION_CONTENT_INVALID")
        refs=row["source_refs"]
        guard(isinstance(refs,list) and 1<=len(refs)<=5 and
              len(set(refs))==len(refs),
              "R3_SECTION_MISSING_SOURCE_REFERENCE")
        for rid in refs:
            value=all_src.get(rid)
            guard(isinstance(value,dict) and set(value)=={"url","basis"} and
                  value["basis"] in {"PROVIDER_COMMENT","PROVIDER_GIT_BLOB",
                                     "PROVIDER_ISSUE","PROVIDER_INDEX"} and
                  isinstance(value["url"],str) and
                  value["url"].startswith("https://github.com/"),
                  "R3_SECTION_SOURCE_UNVERIFIED")
    guard(doc.get("owner_accepted") is False and
          doc.get("semantic_accepted") is False and
          doc.get("may_publish") is False and
          doc.get("may_merge_or_release") is False,
          "R3_AUTHORITY_ELEVATION_FORBIDDEN")
    return doc

def build(issue_url,reader):
    repo,number=parse(issue_url)
    parent=repo+"#"+str(number)
    audited=audit(issue_url,reader)
    chronology=audited.get("event_chronology",{})
    guard(audited.get("parent")==parent and
          audited.get("status")=="LIVE_INDEX_OBSERVED_CHRONOLOGY_PROVIDER_ONLY" and
          audited.get("source_cut_current") is True and
          audited.get("references_observed")==audited.get("references_total") and
          chronology.get("status")==
          "PROVIDER_OBSERVED_UNEDITED_CONTIGUOUS_NOT_OWNER_APPROVED" and
          chronology.get("provider_observed_contiguous") is True and
          chronology.get("provider_events"),
          "R3_REQUIRES_LIVE_VERIFIED_R2_CHRONOLOGY")
    sources={
       "PARENT_ISSUE":{"url":issue_url,"basis":"PROVIDER_ISSUE"},
       "ISSUE_INDEX":{"url":audited["index_url"],"basis":"PROVIDER_INDEX"},
    }
    bodies={}
    for r in audited["source_comments"]:
        if r.get("provider_observed"):
            sources[r["id"]]={"url":r["url"],"basis":"PROVIDER_COMMENT"}
            if not r["id"].startswith("EVENT_"):
                bodies[r["id"]]=source_comment(reader,repo,r)
    for r in audited["versioned_contracts"]:
        if r.get("provider_observed") and r.get("url"):
            sources[r["id"]]={"url":r["url"],"basis":"PROVIDER_GIT_BLOB"}
    for needed in ("OWNER_STATEMENT","REVISED_PLAN","C1B_RECEIPT",
                   "C2_ORIGINAL_REFERENCES","EVENT_0001","EVENT_0002",
                   "R2_VERIFICATION"):
        guard(needed in sources,"R3_REQUIRED_VERIFIED_SOURCE_MISSING_"+needed)
    owner=bodies["OWNER_STATEMENT"]
    plan=bodies["REVISED_PLAN"]
    why=subsection(owner,"1. Problem statement",1400)
    accept=subsection(owner,"10. Owner-required acceptance demonstration",1400)
    original_example=subsection(owner,"9.1 3D_Converters:",800)
    lineage_example=subsection(owner,"4. Lossless issue lineage",700)
    owner_practices=subsection(owner,"6. v3.5 coding practices",650)
    guard(why is not None and accept is not None,
          "R3_OWNER_SOURCE_SECTIONS_MISSING")
    events=chronology["provider_events"]
    lines=[]
    for r in events:
        guard(r["event_url"] in [s["url"] for s in sources.values()],
              "R3_EVENT_NOT_IN_VERIFIED_ISSUE_INDEX")
        lines.append(r["id"]+" "+r["kind"]+" ["+r["source_class"]+"] "+
                     sanitize(r["summary"],420)+" / "+r["occurred_at"])
    event_text="; ".join(lines)
    unknown_amendment=("Only two source-linked provider events are indexed. The first "
        "reports original Owner intent and the second an AGENT implementation plan. "
        "No independent Owner authorization or complete historical amendment "
        "sequence is authenticated. Uncaptured changes remain UNKNOWN. "+
        event_text)
    sources_unknown=("C2's pinned manifest document is byte-observed, but the six "
        "referenced external blobs are NOT reattested by this R3 read. The "
        "Owner's full original ~877.2 KB source and complete physical golden "
        "are not source-established here; public GLRD and partial golden must "
        "not replace them. Historical example (reported, not qualified): "+
        (original_example or "Original workload not verified."))
    code_route=("Verified continuity source-reading path: GitHub owning issue URL "
        "→ unique managed index → exact issue-comment GET and pinned-Git "
        "JSON bytes → R2 contiguous event checks → existing native v3.6 "
        "cold successor. This is the continuity implementation, not the "
        "production XML→worker→physical Preview→Match-1→Final→CII route. "
        "The product source-to-output flow and accepted application run "
        "remain UNKNOWN from the current #400 evidence scope.")
    main_scope=("The R2 live-read cut of Common/main is "+
        audited["live_main"]+". It matches the source cut in the managed "
        "issue index. C1 #274 is deliberately classified CROSS-PARENT EXAMPLE; "
        "C1B belongs to Common #400; C2's document is verified as a pinned "
        "manifest only, without new product-output authority.")
    decisions=("The revised R0–R7 plan is a reported AGENT proposal, not "
        "a protected Owner adoption. The Owner demands KEEP, IMPROVE, ADOPT, "
        "REJECT and PARK with causal reasons and revisit triggers. These "
        "two events do not establish all historical adopted/parked decisions. "
        "Status UNKNOWN. Native coding practices requested: "+
        (owner_practices or "source-first reconciliation and no patchwork."))
    lineage=("Two provider-observed chronological event records are not ten "
        "independent agent handovers. The Owner's issue #123 → struck-through "
        "#125 → #126 illustration must not be described as an actual invalid "
        "issue. Other predecessor/child relationships are UNKNOWN. "
        "Agent ChatGPT conversation link is NOT_CAPTURED, not guessed. "+
        (lineage_example or "Retain any invalid middle issue with its source."))
    tests=("The verified R2 report comment records 119/119 native checks "
        "at its then pinned head, including rejection of missing/reordered "
        "events. That is a source-observed TEST REPORT, not a new execution "
        "of physical XML/CII or independent Physics correctness. R3 must "
        "be separately tested at its exact head.")
    risks=("HOLD/UNKNOWN: complete Owner fixture/golden, accepted XML→CII "
        "semantics, full real code input-to-output pathway, earlier agent "
        "intent/decision chain, session provenance and independent Owner "
        "approval. Provider-account observation, 8/8 index refs and a "
        "green structural test do not grant O2, merge or release.")
    next_action=("Repeat the exact issue-URL cold recovery, verify all twelve "
        "sections and provenance. Next independent substantive falsifier: "
        "re-fetch 3D_Converters #274 original files, current source and actual "
        "423 unresolved weight records; verify independent reviewer/Owner "
        "gates before any real product continuation. If originals are missing "
        "report HOLD with the source reference, not a guessed result.")
    content=[
      (why,"REPORTED_SOURCE",["OWNER_STATEMENT","EVENT_0001"]),
      ("The Owner demands a successor recover ten specified engineering "
       "truth checks, NOT merely an expanded PR/CI report. "+accept,
       "REPORTED_SOURCE",["OWNER_STATEMENT"]),
      (unknown_amendment,"UNKNOWN_REQUIRES_EVIDENCE",
       ["EVENT_0001","EVENT_0002","OWNER_STATEMENT"]),
      (sources_unknown,"UNKNOWN_REQUIRES_EVIDENCE",
       ["OWNER_STATEMENT","C2_ORIGINAL_REFERENCES"]),
      (main_scope,"OBSERVED_SOURCE_SCOPE",
       ["ISSUE_INDEX","C1B_RECEIPT"]),
      (code_route,"UNKNOWN_REQUIRES_EVIDENCE",
       ["ISSUE_INDEX","REVISED_PLAN"]),
      ("Chronology is a bounded provider observation: "+event_text+
       ". Contributions of any earlier agents not indexed remain UNKNOWN.",
       "UNKNOWN_REQUIRES_EVIDENCE",["EVENT_0001","EVENT_0002"]),
      (decisions,"UNKNOWN_REQUIRES_EVIDENCE",
       ["OWNER_STATEMENT","REVISED_PLAN"]),
      (lineage,"UNKNOWN_REQUIRES_EVIDENCE",
       ["OWNER_STATEMENT","ISSUE_INDEX"]),
      (tests,"REPORTED_SOURCE",["R2_VERIFICATION"]),
      (risks,"UNKNOWN_REQUIRES_EVIDENCE",
       ["OWNER_STATEMENT","C2_ORIGINAL_REFERENCES","REVISED_PLAN"]),
      (next_action,"UNKNOWN_REQUIRES_EVIDENCE",
       ["REVISED_PLAN","ISSUE_INDEX"]),
    ]
    doc={"schema":"V36_NATIVE_R3_COLD_HANDOVER_V1","parent":parent,
         "parent_url":issue_url,"source_cut":audited["live_main"],
         "events_provider_observed":chronology["event_count"],
         "chronology":chronology["status"],"sources":sources,
         "sections":[{"number":n+1,"title":SECTIONS[n],"content":row[0],
                      "evidence":row[1],"source_refs":row[2]}
                     for n,row in enumerate(content)],
         "owner_accepted":False,"semantic_accepted":False,
         "may_publish":False,"may_merge_or_release":False}
    return verify_sections(doc)

def render(doc):
    verify_sections(doc)
    lines=["<!-- v36-native-r3-cold-recovery -->",
           "# Native v3.6 twelve-section technical handover",
           "Owning issue: "+doc["parent_url"],
           "Observed Common source cut: "+doc["source_cut"],
           "Provider-verified contiguous events: "+str(doc["events_provider_observed"]),
           "Authority: NOT Owner authenticated; not semantic/product accepted."]
    for section in doc["sections"]:
        lines.extend(["","## "+str(section["number"])+". "+section["title"],
                     "Status: "+section["evidence"],
                     section["content"],"Source references:"])
        for key in section["source_refs"]:
            src=doc["sources"][key]
            lines.append("- "+key+": "+src["url"]+" ("+src["basis"]+")")
    lines.extend(["","STOP: No approval or release inferred; independent "
                  "engineering verification and original evidence still required."])
    return "\n".join(lines)+"\n"
