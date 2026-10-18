#!/usr/bin/env python3
"""Native v3.6 issue-chain spine: validate reported history, NEVER grant authority.

No network, imports of old Relay, GitHub writes, score projection or approval.
A syntactically complete history is not a source-verified technical handover.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA="v36.issue-continuity-chain/v1"
CATEGORIES=(
    "ROOT_OWNER_INTENT","OWNER_AMENDMENTS","ORIGINAL_INPUT",
    "COMPLETE_GOLDEN","MEASURED_BENCHMARK","SOURCE_IMPLEMENTATION_CRUX",
    "AGENT_CONTRIBUTIONS","DECISION_AND_PARKED_IDEAS","KNOWN_FAILURES",
    "SELECTED_NEXT_VERIFICATION","TECHNICAL_HANDOVER"
)
KINDS=frozenset((
    "OWNER_INPUT","AMENDMENT","FIXTURE","GOLDEN","BENCHMARK",
    "SOURCE_FLOW","AGENT_EVIDENCE","IDEA","DECISION","KNOWN_FAILURE",
    "NEXT_VERIFICATION","HANDOVER"
))
CLASSES=frozenset(("OWNER_DIRECT_REPORTED","AGENT_ANALYSIS_REPORTED",
                   "SOURCE_REPORTED","TEST_REPORTED","UNKNOWN"))
DISPOSITIONS=frozenset(("N_A","PROPOSED","PARKED","ADOPTED_REPORTED",
                        "REJECTED_REPORTED","SUPERSEDED_REPORTED"))
STATES=frozenset(("PRESENT_REPORTED","UNKNOWN","NOT_APPLICABLE"))
# Category-to-kind validity checks are structural, never source authentication.
CATEGORY_KINDS={
    "ROOT_OWNER_INTENT":frozenset(("OWNER_INPUT",)),
    "OWNER_AMENDMENTS":frozenset(("AMENDMENT","OWNER_INPUT")),
    "ORIGINAL_INPUT":frozenset(("FIXTURE",)),
    "COMPLETE_GOLDEN":frozenset(("GOLDEN",)),
    "MEASURED_BENCHMARK":frozenset(("BENCHMARK",)),
    "SOURCE_IMPLEMENTATION_CRUX":frozenset(("SOURCE_FLOW","AGENT_EVIDENCE")),
    "AGENT_CONTRIBUTIONS":frozenset(("AGENT_EVIDENCE",)),
    "DECISION_AND_PARKED_IDEAS":frozenset(("IDEA","DECISION")),
    "KNOWN_FAILURES":frozenset(("KNOWN_FAILURE",)),
    "SELECTED_NEXT_VERIFICATION":frozenset(("NEXT_VERIFICATION",)),
    "TECHNICAL_HANDOVER":frozenset(("HANDOVER",)),
}
HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PARENT=re.compile(r"^([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)#([1-9][0-9]*)$")
EVENT=re.compile(r"^EV-[0-9]{3,5}$")

class ChainError(ValueError):
    pass

def require(ok:bool, msg:str)->None:
    if not ok:
        raise ChainError(msg)

def keys(x,fields,which):
    require(isinstance(x,dict) and set(x)==set(fields),which+":MISSING_OR_EXTRA_KEYS")
    return x

def substance(s,label,min_len=12,max_len=4500):
    require(isinstance(s,str) and min_len<=len(s.strip())<=max_len,
            label+":MISSING_OR_INVALID")
    return s

def github_url(value, permitted_repos:set[str]):
    """Classification of a link only; no provider read/authentication."""
    require(isinstance(value,str) and len(value)<2048,"URL_MISSING")
    p=urlsplit(value)
    seg=p.path.strip("/").split("/")
    require(p.scheme=="https" and p.netloc=="github.com" and not p.username
            and not p.password and not p.query and len(seg)>=4
            and all(x not in ("",".","..") for x in seg),
            "URL_UNSAFE_OR_UNSUPPORTED")
    name="/".join(seg[:2])
    require(name in permitted_repos,"FOREIGN_UNDECLARED_REPOSITORY")
    require(seg[2] in ("issues","pull","commit","blob","tree","actions") and
            re.fullmatch(r"[1-9][0-9]*",seg[3]) is not None
            if seg[2] in ("issues","pull") else
            seg[2] in ("commit","blob","tree","actions") and len(seg)>=4,
            "URL_UNSUPPORTED_KIND")
    require(not p.fragment or bool(re.fullmatch(
        r"issuecomment-[1-9][0-9]*|L[1-9][0-9]*(?:-L[1-9][0-9]*)?",p.fragment)),
        "URL_UNSUPPORTED_FRAGMENT")
    return value

def validate(data):
    keys(data,("schema","parent","subject","observed_main","owner_intent",
               "records","chain"),"ROOT")
    require(data["schema"]==SCHEMA,"WRONG_SCHEMA")
    parent=data["parent"]
    require(isinstance(parent,str) and PARENT.fullmatch(parent),"INVALID_PARENT")
    owner_repo=PARENT.fullmatch(parent).group(1)
    substance(data["subject"],"SUBJECT")
    observed=data["observed_main"]
    require(isinstance(observed,dict) and owner_repo in observed,
            "MAIN_SOURCE_FOR_PARENT_MISSING")
    for repo,sha in observed.items():
        require(isinstance(repo,str) and REPO.fullmatch(repo) and
                isinstance(sha,str) and HEX40.fullmatch(sha),
                "MAIN_SOURCE_CUT_INVALID")
    # This allowlist is asserted by the REPORT ITSELF; no trusted repo scope
    # is established without an independent caller/provider comparison.
    permitted=set(observed)
    intent=keys(data["owner_intent"],("excerpt","source_ref","source_class",
                                   "actor_authentication","captured_by"),"OWNER_INTENT")
    substance(intent["excerpt"],"OWNER_INTENT_EXCERPT")
    substance(intent["captured_by"],"CAPTURE_CUSTODY",min_len=3)
    require(intent["source_class"]=="OWNER_DIRECT_REPORTED",
            "OWNER_INTENT_MUST_BE_REPORTED_NOT_AUTHENTICATED")
    require(intent["actor_authentication"]=="NOT_VERIFIED_BY_THIS_TOOL",
            "OWNER_IDENTITY_NOT_AUTHENTICATED")
    github_url(intent["source_ref"],permitted)
    records=data["records"]
    require(isinstance(records,list) and records,"RECORDS_MISSING")
    by_id={}
    for position,event in enumerate(records):
        keys(event,("id","kind","summary","source_ref","source_class","repository",
                    "source_revision","source_sha256","related_ids",
                    "disposition","decision_ref","revisit_trigger","visibility"),"EVENT")
        rid=event["id"]
        require(isinstance(rid,str) and EVENT.fullmatch(rid) and rid not in by_id,
                "EVENT_DUPLICATE_OR_INVALID_ID")
        require(event["kind"] in KINDS,"EVENT_UNKNOWN_KIND")
        substance(event["summary"],"EVENT_SUMMARY")
        require(event["visibility"]=="PUBLIC","PRIVATE_RECORD_MUST_NOT_BE_PUBLISHED")
        require(event["source_class"] in CLASSES and event["source_class"]!="UNKNOWN",
                "UNKNOWN_EVENT_MUST_BE_COVERAGE_GAP")
        repo=event["repository"]
        require(repo in permitted,"EVENT_SOURCE_REPO_OUT_OF_SCOPE")
        github_url(event["source_ref"],permitted)
        require(event["source_ref"].startswith("https://github.com/"+repo+"/"),
                "EVENT_SOURCE_REPO_URL_MISMATCH")
        sha=event["source_revision"]
        require(sha is None or isinstance(sha,str) and HEX40.fullmatch(sha),
                "EVENT_SOURCE_REVISION_INVALID")
        sha256=event["source_sha256"]
        require(sha256 is None or isinstance(sha256,str) and HEX64.fullmatch(sha256),
                "EVENT_SOURCE_DIGEST_INVALID")
        require(event["disposition"] in DISPOSITIONS,"DECISION_DISPOSITION_INVALID")
        if event["kind"] not in ("IDEA","DECISION"):
            require(event["disposition"]=="N_A","NONDECISION_CANNOT_BE_ADOPTED")
        if event["disposition"] in ("ADOPTED_REPORTED","REJECTED_REPORTED"):
            require(isinstance(event["decision_ref"],str),
                    "PROTECTED_DECISION_REFERENCE_REQUIRED")
            github_url(event["decision_ref"],permitted)
        else:
            require(event["decision_ref"] is None,
                    "UNVERIFIED_DECISION_REF_CANNOT_IMPLY_APPROVAL")
        if event["disposition"]=="PARKED":
            substance(event["revisit_trigger"],"PARKED_REVISIT_TRIGGER")
        else:
            require(event["revisit_trigger"] is None,"UNEXPECTED_REVISIT_TRIGGER")
        rel=event["related_ids"]
        require(isinstance(rel,list) and len(set(rel))==len(rel),
                "DUPLICATE_RELATIONS")
        require(all(r in by_id for r in rel),
                "ORPHAN_FORWARD_OR_CYCLIC_EVENT_RELATION")
        by_id[rid]=event
    chain=data["chain"]
    require(isinstance(chain,list) and len(chain)==len(CATEGORIES),
            "CHAIN_REQUIRED_CATEGORIES_MISSING")
    refs=set()
    states=[]
    for i,edge in enumerate(chain):
        keys(edge,("category","state","record_ids","reason"),"CHAIN_EDGE")
        require(edge["category"]==CATEGORIES[i],"CHAIN_ORDER_OR_CATEGORY_DRIFT")
        status=edge["state"]
        require(status in STATES,"CHAIN_STATE_INVALID")
        record_ids=edge["record_ids"]
        require(isinstance(record_ids,list) and len(record_ids)==len(set(record_ids)),
                "CHAIN_DUPLICATE_LINK")
        if status=="PRESENT_REPORTED":
            require(record_ids and set(record_ids).issubset(by_id),"CHAIN_UNBOUND_ORPHAN")
            require(all(by_id[r]["kind"] in CATEGORY_KINDS[edge["category"]]
                        for r in record_ids),"CATEGORY_KIND_MISMATCH")
            require(edge["reason"] is None,"PRESENT_REASON_SHOULD_BE_NULL")
            refs.update(record_ids)
        else:
            require(not record_ids,"UNKNOWN_CANNOT_CLAIM_EVIDENCE")
            substance(edge["reason"],"UNKNOWN_OR_NOT_APPLICABLE_REASON")
        states.append(status)
    if chain[0]["state"]!="PRESENT_REPORTED":
        raise ChainError("ROOT_OWNER_INTENT_MISSING")
    require(set(by_id)==refs,"UNREFERENCED_HISTORY_EVENT")
    # Every required edge has an explicit validated state, including UNKNOWN.
    # This is STRUCTURAL coverage only, not independently verified coverage.
    accounted_count=sum(state in STATES for state in states)
    accounting_percent=100*accounted_count//len(CATEGORIES)
    source_count=sum(x=="PRESENT_REPORTED" for x in states)
    unknown_count=states.count("UNKNOWN")
    not_applicable_count=states.count("NOT_APPLICABLE")
    decision_claims=sum(e["disposition"]=="ADOPTED_REPORTED" for e in records)
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,
           separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    return {
        "schema":"v36.issue-continuity-audit/v1",
        "parent":parent,"input_sha256":digest,
        "required_categories":len(CATEGORIES),
        "accounted_categories":accounted_count,
        "reported_categories":source_count,
        "unknown_categories":unknown_count,
        "not_applicable_categories":not_applicable_count,
        "reported_events":len(records),
        "claimed_adoptions":decision_claims,
        "verified_source_categories":0,
        "authenticated_owner_decisions":0,
        "semantic_acceptances":0,
        "accounting_coverage_percent":accounting_percent,
        "verified_coverage_percent":0,
        "status":"STRUCTURALLY_ACCOUNTED_NOT_SOURCE_VERIFIED",
        "permission_to_write":False,
        "may_change_titles_or_labels":False,
        "may_merge_or_release":False,
        "remaining_gates":[
            "REFETCH_PUBLIC_ISSUES_AND_SOURCE_REFS",
            "ATTEST_ORIGINAL_INPUT_GOLDEN_BENCHMARK_BYTES",
            "VERIFY_OWNER_DIRECT_ACTOR_AND_EFFECTIVE_AMENDMENTS",
            "VERIFY_IMPLEMENTATION_PATH_AND_TRUE_TEST_HEAD",
            "INDEPENDENT_SEMANTIC_AND_OWNER_ACCEPTANCE"
        ]
    }

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input",required=True,type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args(argv)
    try:
        result=validate(json.loads(args.input.read_text(encoding="utf-8")))
        output=json.dumps(result,indent=2,sort_keys=True)+"\n"
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(output,encoding="utf-8")
        else:
            print(output,end="")
    except (ChainError,ValueError,OSError,TypeError) as exc:
        print(json.dumps({"status":"CHAINAGE_BLOCKED","reason":str(exc),
                          "permission_to_write":False,"may_merge_or_release":False}))
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
