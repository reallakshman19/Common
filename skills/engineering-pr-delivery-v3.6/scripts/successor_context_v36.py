#!/usr/bin/env python3
"""Read-only v3.6 C3 successor context. No imports from draft/legacy Relay."""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote, urlsplit

CATEGORIES = (
 "ROOT_OWNER_INTENT","OWNER_AMENDMENTS","ORIGINAL_INPUT","COMPLETE_GOLDEN",
 "MEASURED_BENCHMARK","SOURCE_IMPLEMENTATION_CRUX","AGENT_CONTRIBUTIONS",
 "DECISION_AND_PARKED_IDEAS","KNOWN_FAILURES","SELECTED_NEXT_VERIFICATION",
 "TECHNICAL_HANDOVER")
ROLES = {"ORIGINAL_POSITIVE","ORIGINAL_NEGATIVE","COMPLETE_GOLDEN",
         "PARTIAL_GOLDEN","BENCHMARK_INPUT","DEMONSTRATION_ONLY"}
SHA40 = re.compile(r"^[a-f0-9]{40}$")
SHA64 = re.compile(r"^[a-f0-9]{64}$")
PARENT = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+#[1-9][0-9]*$")


class ContextError(ValueError):
    pass


def guard(yes,code):
    if not yes:
        raise ContextError(code)


def load_input(path):
    file = Path(path)
    guard(file.is_file() and 0 < file.stat().st_size <= 1024*1024,
          "CONTEXT_FILE_MISSING_OR_TOO_LARGE")
    return json.loads(file.read_text(encoding="utf-8"))


def github_link(url,allow):
    guard(isinstance(url,str) and len(url) < 2048,"INVALID_SOURCE_URL")
    u = urlsplit(url)
    p = u.path.strip("/").split("/")
    guard(u.scheme == "https" and u.netloc == "github.com"
          and not u.query and not u.username and not u.password and len(p) >= 4
          and "/".join(p[:2]) in allow and p[2] in
          {"issues","pull","commit","blob","tree","actions"},
          "UNTRUSTED_SOURCE_URL")
    return url


def safe_md(v):
    v=str(v)
    for a,b in (("&","&amp;"),("<","&lt;"),(">","&gt;"),
                ("|","&#124;"),("[","&#91;"),("]","&#93;"),
                (chr(96),"&#96;"),("\n"," "),("\r"," ")):
        v=v.replace(a,b)
    return v[:2500]


def attach(packet,chain,custody):
    guard(isinstance(packet,dict) and
          packet.get("schema")=="V36_COLD_SUCCESSOR_V1" and
          isinstance(packet.get("parent"),str) and
          PARENT.fullmatch(packet["parent"]), "NOT_NATIVE_COLD_SUCCESSOR")
    parent=packet["parent"]
    guard(isinstance(chain,dict) and
          chain.get("schema")=="v36.issue-continuity-chain/v1" and
          chain.get("parent")==parent,"C1_PARENT_OR_SCHEMA_MISMATCH")
    observed=chain.get("observed_main")
    guard(isinstance(observed,dict) and parent.split("#")[0] in observed
          and all(isinstance(x,str) and SHA40.fullmatch(x)
                  for x in observed.values()),"C1_INVALID_SOURCE_CUT")
    intent=chain.get("owner_intent")
    guard(isinstance(intent,dict) and
          intent.get("source_class")=="OWNER_DIRECT_REPORTED" and
          intent.get("actor_authentication")=="NOT_VERIFIED_BY_THIS_TOOL"
          and isinstance(intent.get("excerpt"),str)
          and 12 <= len(intent["excerpt"]) <= 4500,
          "OWNER_INPUT_MUST_REMAIN_REPORTED")
    github_link(intent.get("source_ref"),observed)
    events=chain.get("records")
    guard(isinstance(events,list) and 1<=len(events)<=300,
          "C1_RECORDS_MISSING_OR_EXCESSIVE")
    by_id={}
    for e in events:
        guard(isinstance(e,dict) and
              isinstance(e.get("id"),str) and
              re.fullmatch(r"EV-[0-9]{3,5}",e["id"]) and
              e["id"] not in by_id and e.get("visibility")=="PUBLIC" and
              e.get("repository") in observed and
              isinstance(e.get("summary"),str) and
              12<=len(e["summary"])<=4500,"C1_EVENT_INVALID")
        github_link(e.get("source_ref"), observed)
        by_id[e["id"]]=e
    edges=chain.get("chain")
    guard(isinstance(edges,list) and len(edges)==11 and
          all(isinstance(e,dict) for e in edges) and
          [e.get("category") for e in edges]==list(CATEGORIES),
          "C1_CATEGORY_ORDER_INVALID")
    used=set()
    sections=[]
    for edge in edges:
        state,ids=edge.get("state"),edge.get("record_ids")
        guard(state in {"PRESENT_REPORTED","UNKNOWN","NOT_APPLICABLE"}
              and isinstance(ids,list) and len(set(ids))==len(ids),
              "C1_EDGE_INVALID")
        if state=="PRESENT_REPORTED":
            guard(bool(ids) and all(i in by_id for i in ids)
                  and edge.get("reason") is None,"C1_UNBOUND_EVENT")
            used.update(ids)
        else:
            guard(not ids and isinstance(edge.get("reason"),str)
                  and len(edge["reason"].strip())>=12,
                  "C1_MISSING_GAP_REASON")
        sections.append({"category":edge["category"],"state":state,
                         "reason":edge.get("reason"),
                         "records":[{"id":i,"summary":by_id[i]["summary"],
                                     "source":by_id[i]["source_ref"],
                                     "disposition":by_id[i].get("disposition")}
                                    for i in ids]})
    guard(set(by_id)==used and sections[0]["state"]=="PRESENT_REPORTED",
          "C1_ORPHAN_OR_MISSING_ROOT")

    guard(isinstance(custody,dict) and
          custody.get("schema")=="v36.source-custody/v1" and
          custody.get("repository") in observed and
          isinstance(custody.get("revision"),str) and
          SHA40.fullmatch(custody["revision"]),
          "C2_SOURCE_SCOPE_INVALID")
    arts=custody.get("artifacts")
    guard(isinstance(arts,list) and 1<=len(arts)<=100,"C2_ARTIFACTS_INVALID")
    source=custody["repository"]
    links=[]
    used_ids=set()
    for a in arts:
        guard(isinstance(a,dict) and
              isinstance(a.get("id"),str) and
              re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}",a["id"]) and
              a["id"] not in used_ids and a.get("role") in ROLES and
              isinstance(a.get("expected_blob_sha1"),str) and
              SHA40.fullmatch(a["expected_blob_sha1"]) and
              isinstance(a.get("expected_sha256"),str) and
              SHA64.fullmatch(a["expected_sha256"]) and
              type(a.get("expected_size_bytes")) is int and
              a["expected_size_bytes"]>=0,"C2_ARTIFACT_INVALID")
        used_ids.add(a["id"])
        path=a.get("path")
        guard(isinstance(path,str) and 0<len(path)<=500
              and not path.startswith("/") and chr(92) not in path
              and all(p not in ("",".","..") for p in path.split("/")),
              "C2_ARTIFACT_PATH_UNSAFE")
        if a["role"]=="COMPLETE_GOLDEN":
            guard(a.get("oracle_complete") is True,
                  "C2_GOLDEN_COMPLETENESS_UNPROVED")
        if a["role"]=="PARTIAL_GOLDEN":
            guard(a.get("oracle_complete") is False,
                  "C2_PARTIAL_GOLDEN_MISLABELED")
        links.append({"id":a["id"],"role":a["role"],
                      "bytes":a["expected_size_bytes"],
                      "sha256_claim":a["expected_sha256"],
                      "url":("https://github.com/"+source+"/blob/"+
                             custody["revision"]+"/"+quote(path,safe="/")),
                      "status":"DECLARED_BYTES_REQUIRE_FRESH_PROVIDER_REPLAY"})
    return {"schema":"V36_COLD_CONTINUITY_CONTEXT_V1",
            "parent":parent,"intent":intent["excerpt"],
            "intent_ref":intent["source_ref"],
            "sections":sections,"artifacts":links,
            "reported_revision":observed[source],
            "custody_revision":custody["revision"],
            "source_drift_warning":observed[source]!=custody["revision"],
            "chain_digest":hashlib.sha256(json.dumps(chain,sort_keys=True,
                separators=(",",":")).encode()).hexdigest(),
            "manifest_digest":hashlib.sha256(json.dumps(custody,sort_keys=True,
                separators=(",",":")).encode()).hexdigest(),
            "source_verification":"NOT_ESTABLISHED_BY_JSON_INPUT",
            "owner_acceptance":False,"may_publish":False,
            "may_count_for_o2":False,"may_merge_or_release":False}


def render(context):
    guard(context.get("schema")=="V36_COLD_CONTINUITY_CONTEXT_V1",
          "INVALID_CONTEXT")
    lines=["","## Issue-first engineering continuity — reported only",
           "After-freeze advisory context. Source links, digests and fixture claims are NOT automatic verification or Owner approval.",
           "Owner WHY (reported; actor not independently authenticated): "+
           safe_md(context["intent"]),
           "Owner intent reference: "+context["intent_ref"],
           "Source-cut drift: "+("YES — independently recheck" if
                   context["source_drift_warning"] else "not shown; check freshness"),
           "C1 input digest: "+context["chain_digest"],
           "C2 input digest: "+context["manifest_digest"],
           "### Original intent, amendments, code crux, decisions and gaps"]
    for e in context["sections"]:
        lines.append("- "+e["category"]+" — "+e["state"])
        if e["reason"]:
            lines.append("  - UNKNOWN reason: "+safe_md(e["reason"]))
        for x in e["records"]:
            lines.append("  - "+safe_md(x["id"])+": "+safe_md(x["summary"])+
                         " | "+x["source"]+" | "+safe_md(x["disposition"]))
    lines.append("### Original-source pointers — reverify before use")
    for a in context["artifacts"]:
        lines.append("- "+safe_md(a["id"])+" / "+a["role"]+" / "+
                     str(a["bytes"])+" bytes / SHA256 claimed "+a["sha256_claim"]+
                     " / "+a["url"])
    lines.extend(["### Resumption conditions",
                  "- Re-fetch Owner issue actor, original private source, source code path and real exact-head CI.",
                  "- Re-run C2 Git byte custody; partial golden never implies complete physical output.",
                  "- Preserve unresolved Match-1/Final weights and native CII release HOLD.",
                  "- Complete native 12-section technical handover ONLY after independently verified stage freeze; do not alter Buddy or multipass rounds."])
    return "\n".join(lines)+"\n"
