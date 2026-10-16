#!/usr/bin/env python3
"""Native v3.6 additive: advisory evidence selection and lossless issue chain."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
ISSUE=re.compile(r"^[1-9][0-9]*$")
SHA=re.compile(r"^[0-9a-f]{40}$")
STRIKE={"SUPERSEDED_REPORTED","INVALID_REPORTED","DELETED_REPORTED"}
UNCERTAIN={"INACCESSIBLE_UNVERIFIED","NOT_FOUND_UNVERIFIED","UNKNOWN"}
STATES={"ACTIVE"}|STRIKE|UNCERTAIN

class AddendumError(ValueError): pass

def demand(ok,code):
    if not ok: raise AddendumError(code)

def evidence_choice(*, explicit_protocol=None, project_protocol=None,
                    governed_v36=False, has_issue=False):
    """Never replace a governing or explicit protocol with an ad-hoc receipt."""
    for value in (explicit_protocol,project_protocol):
        demand(value is None or isinstance(value,str) and 0<len(value.strip())<=120,
               "INVALID_PROTOCOL_SELECTOR")
    explicit=explicit_protocol.strip() if explicit_protocol else None
    project=project_protocol.strip() if project_protocol else None
    if project and explicit and project.casefold()!=explicit.casefold():
        return {"mode":"PROTOCOL_CONFLICT_HOLD","required":False}
    if project:
        return {"mode":"PROJECT_PROTOCOL_REQUIRED","protocol":project,"required":True}
    if governed_v36:
        if explicit and explicit.casefold() not in ("v3.6","native v3.6","task_evidence v3.6"):
            return {"mode":"PROTOCOL_CONFLICT_HOLD","required":False}
        return {"mode":"NATIVE_V36_REQUIRED","protocol":"TASK_EVIDENCE v3.6","required":True}
    if explicit:
        if explicit.casefold() in ("v3.6","native v3.6","task_evidence v3.6"):
            return {"mode":"V36_BINDING_MISSING_HOLD","required":False}
        return {"mode":"EXPLICIT_PROTOCOL_PRESERVED","protocol":explicit,"required":True}
    return {"mode":"OPTIONAL_ADHOC_ADVISORY","protocol":"TASK_EVIDENCE — ADHOC",
            "required":False,"may_count_for_v36_o2":False,"may_publish":False,
            "target":"AUTHORIZED_ISSUE_IF_EXPLICIT" if has_issue else "CHAT_ONLY"}

def source_url(ref,repo):
    demand(isinstance(ref,str) and len(ref)<=2048,"DECISION_REF_MISSING")
    u=urlsplit(ref)
    p=u.path.strip("/").split("/")
    demand(u.scheme=="https" and u.netloc=="github.com" and not u.query
           and not u.username and not u.password and len(p)>=4
           and "/".join(p[:2])==repo and p[2]=="issues"
           and ISSUE.fullmatch(p[3]),"DECISION_REF_FOREIGN_OR_INVALID")
    demand(not u.fragment or re.fullmatch(r"issuecomment-[1-9][0-9]*",u.fragment),
           "DECISION_REF_FRAGMENT_INVALID")
    return ref

def reason(s):
    demand(isinstance(s,str) and 10<=len(s.strip())<=320 and
           all(ord(c)>=32 for c in s),"REASON_MISSING_OR_UNSAFE")
    # Disallow a forged table or injected Markdown link in source text.
    return re.sub(r"([\\*_{}\[\]()<>!|])",r"\\\1",s.strip()).replace(
        chr(96),chr(92)+chr(96))

def check_chain(chain):
    demand(isinstance(chain,dict) and set(chain)=={"repository","nodes"},
           "CHAIN_SCHEMA_INVALID")
    repo=chain["repository"]
    demand(isinstance(repo,str) and REPO.fullmatch(repo),"CHAIN_REPO_INVALID")
    nodes=chain["nodes"]
    demand(isinstance(nodes,list) and 1<=len(nodes)<=60,"CHAIN_NODES_INVALID")
    seen=set()
    prev=None
    for row in nodes:
        demand(isinstance(row,dict) and set(row)=={
            "issue","parent","state","reason","decision_ref"},"NODE_SCHEMA_INVALID")
        n=row["issue"]
        demand(type(n) is int and n>0 and n not in seen,"DUPLICATE_OR_INVALID_ISSUE")
        demand(row["parent"]==prev,"MISSING_OR_REORDERED_CHAIN_EDGE")
        state=row["state"]
        demand(state in STATES,"UNSUPPORTED_STATE")
        if state in STRIKE:
            reason(row["reason"])
            source_url(row["decision_ref"],repo)
        elif state in UNCERTAIN:
            reason(row["reason"])
            demand(row["decision_ref"] is None,"UNVERIFIED_CANNOT_CLAIM_DECISION")
        else:
            demand(row["reason"] is None and row["decision_ref"] is None,
                   "ACTIVE_CANNOT_CLAIM_TOMBSTONE")
        seen.add(n)
        prev=n
    return nodes

def render_chain(chain):
    out=[]
    for row in check_chain(chain):
        repo=chain["repository"]
        anchor=f"[#{row['issue']}](https://github.com/{repo}/issues/{row['issue']})"
        s=row["state"]
        if s in STRIKE:
            anchor=f"~~{anchor}~~ ({s}: {reason(row['reason'])}; [decision]({row['decision_ref']}))"
        elif s in UNCERTAIN:
            anchor=f"{anchor} ({s}: {reason(row['reason'])})"
        out.append(anchor)
    return " → ".join(out)

def advisory_evidence(*,chain,outcome,source_sha,implementation_crux,
                      originals,tests,next_check,result):
    link=render_chain(chain)
    for value in (outcome,implementation_crux,originals,tests,next_check,result):
        reason(value)
    demand(isinstance(source_sha,str) and SHA.fullmatch(source_sha),
           "SOURCE_SHA_INVALID")
    return (
       "TASK_EVIDENCE — ADHOC / ADVISORY (NOT v3.6 O2)\n"
       f"Issue chain: {link}\n"
       f"User outcome: {outcome}\n"
       f"Exact source/candidate SHA: {source_sha}\n"
       f"Implementation crux: {implementation_crux}\n"
       f"Original fixture, golden, benchmark: {originals}\n"
       f"Tests on exact SHA: {tests}\n"
       f"Observed result and negative knowledge: {result}\n"
       f"Next source-first verification: {next_check}\n"
       "Owner/academic/merge acceptance: NOT_GRANTED\n"
       "Do not count this as canonical v3.6 TASK_EVIDENCE or modify titles.\n"
    )

def main(argv=None):
    p=argparse.ArgumentParser(description="Read-only issue-chain display")
    p.add_argument("--chain",required=True,type=Path)
    args=p.parse_args(argv)
    try: print(render_chain(json.loads(args.chain.read_text(encoding="utf-8"))))
    except (AddendumError,OSError,ValueError,TypeError) as exc:
        print(json.dumps({"status":"CHAIN_RENDER_BLOCKED","reason":str(exc),
                          "permission_to_write":False}))
        return 2
    return 0

if __name__=="__main__":
    raise SystemExit(main())
