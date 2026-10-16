#!/usr/bin/env python3
"""Native v3.6 C1B: read-only event receipts and lossless issue lineage.

No writes, imports from v3.5/v3.2/v3.1/DELP, provider authentication,
conversation discovery or native task-evidence replacement.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA="v36.issue-receipt-stream/v1"
PARENT=re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#[1-9][0-9]*$")
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
EV=re.compile(r"^EV-[0-9]{4,6}$")
SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA64=re.compile(r"^[0-9a-f]{64}$")
DATE=re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
KINDS={"OWNER_INPUT","OWNER_AMENDMENT","AGENT_CONTRIBUTION",
       "SOURCE_FACT","DECISION","ISSUE_LINEAGE","CONVERSATION_REFERENCE",
       "ADHOC_EVIDENCE"}
DISPOSITIONS={"N_A","PROPOSED","PARKED","ADOPTED_REPORTED",
              "REJECTED_REPORTED","SUPERSEDED_REPORTED"}
CLASSES={"OWNER_DIRECT_REPORTED","AGENT_REPORTED","SOURCE_REPORTED"}
FIELDS={"id","kind","occurred_at","source_ref","source_class",
        "actor_login_claim","actor_authentication","summary","visibility",
        "source_sha256_claim","supersedes","disposition","revisit_trigger",
        "conversation_ref","conversation_access","lineage","previous_digest"}
NODE={"issue","state","availability","reason","disposition_ref"}
EDGE={"from","to","relationship","source_ref"}

class ReceiptError(ValueError):
    pass

def need(ok,reason):
    if not ok:
        raise ReceiptError(reason)

def exact(obj,fields,reason):
    need(isinstance(obj,dict) and set(obj)==fields,reason)

def digest(value):
    b=json.dumps(value,ensure_ascii=False,sort_keys=True,
                 separators=(",",":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

def prose(s,minimum=8,maximum=3500):
    return isinstance(s,str) and minimum<=len(s.strip())<=maximum

def issue_ref(ref,allowed):
    need(isinstance(ref,str) and PARENT.fullmatch(ref),"ISSUE_REF_INVALID")
    need(PARENT.fullmatch(ref).group(1) in allowed,
         "FOREIGN_ISSUE_NOT_IN_SCOPE")
    return ref

def github_url(url,allowed):
    need(isinstance(url,str) and 0<len(url)<=2048,"SOURCE_URL_REQUIRED")
    p=urlsplit(url)
    seg=p.path.strip("/").split("/")
    need(p.scheme=="https" and p.netloc=="github.com" and not p.query
         and not p.username and not p.password and len(seg)>=4
         and "/".join(seg[:2]) in allowed and
         seg[2] in ("issues","pull","commit","blob","tree","actions")
         and all(x not in ("",".","..") for x in seg),
         "SOURCE_URL_UNTRUSTED")
    if seg[2] in ("issues","pull"):
        need(re.fullmatch(r"[1-9][0-9]*",seg[3]) is not None,
             "SOURCE_ISSUE_NUMBER_INVALID")
    need(not p.fragment or re.fullmatch(
         r"issuecomment-[1-9][0-9]*|L[1-9][0-9]*(?:-L[1-9][0-9]*)?",
         p.fragment) is not None,"SOURCE_FRAGMENT_UNSAFE")
    return url

def markdown(value):
    s=str(value)
    for before,after in (("&","&amp;"),("<","&lt;"),(">","&gt;"),
                         ("|","&#124;"),("[","&#91;"),("]","&#93;"),
                         (chr(96),"&#96;"),("\r"," "),("\n"," ")):
        s=s.replace(before,after)
    return s[:3500]

def validate_lineage(value,allowed):
    exact(value,{"nodes","edges"},"LINEAGE_SCHEMA_INVALID")
    nodes,edges=value["nodes"],value["edges"]
    need(isinstance(nodes,list) and 2<=len(nodes)<=120 and
         isinstance(edges,list) and len(edges)<=300,
         "LINEAGE_SIZE_INVALID")
    pos={}
    for i,n in enumerate(nodes):
        exact(n,NODE,"LINEAGE_NODE_SCHEMA_INVALID")
        ref=issue_ref(n["issue"],allowed)
        need(ref not in pos,"LINEAGE_DUPLICATE_ISSUE")
        pos[ref]=i
        state=n["state"]
        need(state in ("ACTIVE","INVALID_REPORTED","SUPERSEDED_REPORTED",
                       "AVAILABILITY_UNVERIFIED"),"LINEAGE_STATE_INVALID")
        need(n["availability"] in ("UNKNOWN","ACCESSIBLE_PROVIDER_OBSERVED",
                                    "NOT_FOUND_UNVERIFIED",
                                    "PERMISSION_DENIED_UNVERIFIED"),
             "LINEAGE_AVAILABILITY_INVALID")
        if state in ("INVALID_REPORTED","SUPERSEDED_REPORTED"):
            need(prose(n["reason"]) and n["disposition_ref"] is not None,
                 "TOMBSTONE_REQUIRES_SOURCE_AND_REASON")
            github_url(n["disposition_ref"],allowed)
        elif state=="AVAILABILITY_UNVERIFIED":
            need(n["availability"] in ("NOT_FOUND_UNVERIFIED",
                                       "PERMISSION_DENIED_UNVERIFIED")
                 and prose(n["reason"]) and n["disposition_ref"] is None,
                 "HTTP_404_NOT_PROOF_OF_DELETION")
        else:
            need(n["reason"] is None and n["disposition_ref"] is None,
                 "ACTIVE_ISSUE_NOT_TOMBSTONED")
    linear=set()
    for e in edges:
        exact(e,EDGE,"LINEAGE_EDGE_SCHEMA_INVALID")
        need(e["from"] in pos and e["to"] in pos and
             pos[e["from"]]<pos[e["to"]],
             "LINEAGE_ORPHAN_OR_CYCLE")
        need(e["relationship"] in ("SUCCESSOR","ALTERNATIVE"),
             "LINEAGE_RELATION_INVALID")
        github_url(e["source_ref"],allowed)
        if e["relationship"]=="SUCCESSOR":
            linear.add((pos[e["from"]],pos[e["to"]]))
    need(all((i,i+1) in linear for i in range(len(nodes)-1)),
         "LINEAGE_MISSING_MIDDLE_HOP")
    return value

def validate_stream(data):
    exact(data,{"schema","parent","allowed_repositories","events"},
          "STREAM_SCHEMA_INVALID")
    need(data["schema"]==SCHEMA,"STREAM_WRONG_VERSION")
    parent=data["parent"]
    need(isinstance(parent,str) and PARENT.fullmatch(parent),
         "STREAM_PARENT_INVALID")
    allowed=data["allowed_repositories"]
    need(isinstance(allowed,list) and 1<=len(allowed)<=20 and
         len(set(allowed))==len(allowed) and
         all(isinstance(x,str) and REPO.fullmatch(x) for x in allowed) and
         PARENT.fullmatch(parent).group(1) in allowed,
         "STREAM_REPOSITORY_SCOPE_INVALID")
    events=data["events"]
    need(isinstance(events,list) and 1<=len(events)<=400,
         "STREAM_EMPTY_OR_TOO_LARGE")
    known=set()
    prev=None
    last_when=""
    for e in events:
        exact(e,FIELDS,"EVENT_SCHEMA_INVALID")
        eid=e["id"]
        need(isinstance(eid,str) and EV.fullmatch(eid) and eid not in known,
             "EVENT_ID_INVALID_OR_DUPLICATE")
        need(e["kind"] in KINDS and e["source_class"] in CLASSES,
             "EVENT_KIND_OR_SOURCE_CLASS_INVALID")
        need(e["actor_authentication"] in (
             "NOT_AUTHENTICATED",
             "PROVIDER_ACCOUNT_OBSERVED_NOT_OWNER_AUTHENTICATED"),
             "EVENT_CANNOT_SELF_AUTHENTICATE_OWNER")
        login=e["actor_login_claim"]
        need(login is None or (isinstance(login,str) and
             re.fullmatch(r"[A-Za-z0-9-]{1,39}",login)),
             "EVENT_LOGIN_CLAIM_INVALID")
        when=e["occurred_at"]
        need(isinstance(when,str) and DATE.fullmatch(when)
             and when>=last_when,"EVENT_TIMESTAMP_INVALID_OR_REORDERED")
        last_when=when
        vis=e["visibility"]
        need(vis in ("PUBLIC_SAFE","CONTENT_NOT_PUBLISHED"),
             "EVENT_VISIBILITY_INVALID")
        if vis=="PUBLIC_SAFE":
            github_url(e["source_ref"],allowed)
            need(prose(e["summary"]),"EVENT_SUMMARY_MISSING")
        else:
            need(e["source_ref"] is None and
                 e["summary"]=="CONTENT_NOT_PUBLISHED" and
                 e["source_sha256_claim"] is None,
                 "PRIVATE_EVENT_CONTENT_MUST_NOT_BE_COPIED")
        claimed=e["source_sha256_claim"]
        need(claimed is None or (isinstance(claimed,str)
             and SHA64.fullmatch(claimed)),"SOURCE_DIGEST_INVALID")
        need(e["previous_digest"]==prev,"EVENT_APPEND_ONLY_HASH_MISMATCH")
        links=e["supersedes"]
        need(isinstance(links,list) and len(links)==len(set(links)) and
             all(x in known for x in links),
             "EVENT_SUPERSESSION_ORPHAN_OR_CYCLE")
        if e["kind"]=="OWNER_AMENDMENT":
            need(bool(links), "OWNER_AMENDMENT_MUST_LINK_CHANGED_PRIOR_EVENT")
        disposition=e["disposition"]
        need(disposition in DISPOSITIONS,"DISPOSITION_INVALID")
        if disposition=="PARKED":
            need(prose(e["revisit_trigger"]),"PARKED_REVISIT_REQUIRED")
        else:
            need(e["revisit_trigger"] is None,"REVISIT_ONLY_FOR_PARKED")
        if disposition in ("ADOPTED_REPORTED","REJECTED_REPORTED",
                           "SUPERSEDED_REPORTED"):
            need(e["source_ref"] is not None,
                 "DECISION_SOURCE_NOT_PUBLISHED")
        access=e["conversation_access"]
        conv=e["conversation_ref"]
        need(access in ("NOT_CAPTURED","RESTRICTED_NOT_PUBLISHED",
                        "AUTHORIZED_PUBLIC"),"CONVERSATION_ACCESS_INVALID")
        if access=="AUTHORIZED_PUBLIC":
            p=urlsplit(conv) if isinstance(conv,str) else None
            need(p is not None and p.scheme=="https" and
                 p.netloc in ("chatgpt.com","chat.openai.com") and
                 p.path.startswith("/share/") and not p.query and
                 not p.fragment and len(conv)<2048,
                 "CONVERSATION_PUBLIC_SHARE_INVALID")
        else:
            need(conv is None,"RESTRICTED_CONVERSATION_LEAK")
        if e["kind"]=="CONVERSATION_REFERENCE":
            need(access!="NOT_CAPTURED","NO_CONVERSATION_REFERENCE_EXISTS")
        if e["kind"]=="ISSUE_LINEAGE":
            validate_lineage(e["lineage"],allowed)
        else:
            need(e["lineage"] is None,"NON_LINEAGE_EVENT_MUTATION")
        if e["kind"] in ("OWNER_INPUT","OWNER_AMENDMENT"):
            need(e["source_class"]=="OWNER_DIRECT_REPORTED",
                 "OWNER_INPUT_MUST_BE_REPORTED_NOT_APPROVED")
        known.add(eid)
        prev=digest(e)
    return {"schema":"v36.issue-receipt-audit/v1","parent":parent,
            "events":len(events),"last_event_digest":prev,
            "stream_sha256":digest(data),"accounted_events":len(events),
            "authenticated_owner_decisions":0,"verified_provider_events":0,
            "semantic_acceptances":0,"may_publish":False,
            "may_count_for_o2":False,
            "may_change_titles_or_labels":False,
            "may_merge_or_release":False,
            "status":"STRUCTURALLY_VALID_PROVIDER_AND_OWNER_AUTHORITY_UNVERIFIED"}

def verify_extension(old,new):
    a,b=validate_stream(old),validate_stream(new)
    need(old["parent"]==new["parent"] and
         old["allowed_repositories"]==new["allowed_repositories"],
         "STREAM_SCOPE_CHANGED")
    rows=old["events"]
    need(len(new["events"])>=len(rows) and
         new["events"][:len(rows)]==rows,
         "HISTORICAL_RECEIPT_EDIT_OR_REMOVAL")
    return {"status":"PREFIX_PRESERVED_PROVIDER_READBACK_STILL_REQUIRED",
            "prior_events":len(rows),"next_events":len(new["events"]),
            "last_event_digest":b["last_event_digest"],
            "may_publish":False}

def issue_url(ref):
    repo,num=ref.split("#")
    return "https://github.com/"+repo+"/issues/"+num

def render(data):
    result=validate_stream(data)
    lines=["# Native v3.6 issue receipt index — source claims only",
           "Owning issue: "+issue_url(data["parent"]),
           "Account observation, hash chain and statement of attribution "
           "do not prove Owner approval, complete golden or native acceptance."]
    for e in data["events"]:
        lines.append("- "+e["id"]+" / "+e["kind"]+": "+markdown(e["summary"])+
                     " | "+e["occurred_at"]+" | "+
                     (e["source_ref"] or "SOURCE_NOT_PUBLISHED")+
                     " | "+e["disposition"])
        if e["supersedes"]:
            lines.append("  - Supersedes: "+", ".join(e["supersedes"]))
        if e["disposition"]=="PARKED":
            lines.append("  - Revisit: "+markdown(e["revisit_trigger"]))
        if e["conversation_access"]=="AUTHORIZED_PUBLIC":
            lines.append("  - Conversation: "+e["conversation_ref"])
        else:
            lines.append("  - Conversation: "+e["conversation_access"])
        if e["kind"]=="ISSUE_LINEAGE":
            nodes=e["lineage"]["nodes"]
            tokens=[("~~"+issue_url(n["issue"])+"~~"
                     if n["state"] in ("INVALID_REPORTED","SUPERSEDED_REPORTED")
                     else issue_url(n["issue"])) for n in nodes]
            lines.append("  - Historical path: "+" → ".join(tokens))
            for n in nodes:
                if n["state"]!="ACTIVE":
                    lines.append("  - "+n["issue"]+" "+n["state"]+
                                 " / "+n["availability"]+
                                 (" / "+markdown(n["reason"]) if n["reason"]
                                  else "")+
                                 (" / "+n["disposition_ref"] if
                                  n["disposition_ref"] else
                                  " / disappearance NOT authenticated"))
    lines.append(result["status"]+"; actual Owner/semantic accepted=0")
    return "\n".join(lines)+"\n"

def render_adhoc(data):
    fields={"protocol_mode","authorized_issue","human_outcome",
            "source_revision","implementation_crux","original_inputs",
            "golden","benchmark","tests","issue_chain","known_gaps",
            "parked_ideas","next_verification","conversation_ref",
            "conversation_access"}
    exact(data,fields,"ADHOC_SCHEMA_INVALID")
    need(data["protocol_mode"]=="AD_HOC_NO_OTHER_PROTOCOL",
         "GOVERNED_OR_ALTERNATE_EVIDENCE_PROTOCOL_PRECEDENCE")
    rev=data["source_revision"]
    need(isinstance(rev,str) and re.fullmatch(
         r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}",rev),
         "ADHOC_EXACT_COMMIT_REQUIRED")
    dest=data["authorized_issue"]
    if dest is not None:
        need(isinstance(dest,str) and PARENT.fullmatch(dest),
             "ADHOC_ISSUE_DESTINATION_INVALID")
    for field in ("human_outcome","implementation_crux","original_inputs",
                  "golden","benchmark","tests","issue_chain","known_gaps",
                  "parked_ideas","next_verification"):
        need(prose(data[field],8,4500),"ADHOC_FIELD_MISSING_"+field)
    access=data["conversation_access"]
    need(access in ("NOT_CAPTURED","RESTRICTED_NOT_PUBLISHED",
                    "AUTHORIZED_PUBLIC"),"ADHOC_CONVERSATION_ACCESS_INVALID")
    if access=="AUTHORIZED_PUBLIC":
        p=urlsplit(data["conversation_ref"]) if isinstance(
            data["conversation_ref"],str) else None
        need(p is not None and p.scheme=="https" and p.netloc=="chatgpt.com"
             and p.path.startswith("/share/") and not p.query and
             not p.fragment,"ADHOC_PUBLIC_CONVERSATION_INVALID")
    else:
        need(data["conversation_ref"] is None,
             "ADHOC_PRIVATE_CONVERSATION_LEAK")
    lines=["# OPTIONAL native v3.6 ad-hoc evidence — COPYABLE, NEVER PUBLISHED",
           "Not governed TASK_EVIDENCE, not an alternative protocol, "
           "not Owner/independent acceptance.",
           "Issue: "+(issue_url(dest) if dest else
                      "UNKNOWN — NO AUTHORIZED PUBLISH DESTINATION"),
           "Exact source: "+rev]
    for field in ("human_outcome","implementation_crux","original_inputs",
                  "golden","benchmark","tests","issue_chain","known_gaps",
                  "parked_ideas","next_verification"):
        lines.append(field.replace("_"," ").title()+": "+
                     markdown(data[field]))
    lines.append("Conversation: "+(data["conversation_ref"] if
                 access=="AUTHORIZED_PUBLIC" else access))
    return "\n".join(lines)+"\n"

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stream",type=Path)
    p.add_argument("--previous",type=Path)
    p.add_argument("--adhoc",type=Path)
    p.add_argument("--render",action="store_true")
    args=p.parse_args(argv)
    try:
        if args.adhoc:
            need(not args.stream and not args.previous,"CHOOSE_ONE_MODE")
            print(render_adhoc(json.loads(args.adhoc.read_text(
                encoding="utf-8"))),end="")
        else:
            need(args.stream is not None,"STREAM_REQUIRED")
            data=json.loads(args.stream.read_text(encoding="utf-8"))
            if args.previous:
                print(json.dumps(verify_extension(json.loads(
                    args.previous.read_text(encoding="utf-8")),data),indent=2))
            elif args.render:
                print(render(data),end="")
            else:
                print(json.dumps(validate_stream(data),indent=2))
        return 0
    except (ReceiptError,OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({"status":"C1B_BLOCKED","reason":str(exc),
                          "may_publish":False,"may_merge_or_release":False}))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
