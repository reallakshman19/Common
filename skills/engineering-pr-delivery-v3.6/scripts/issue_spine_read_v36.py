#!/usr/bin/env python3
"""Native v3.6 R2: source-first read-only GitHub issue spine, never approval."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
import re
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCHEMA="v36.live-issue-index/v1"
MARKER="<!-- v36-issue-spine-index/v1 parent:{} -->"
SHA=re.compile(r"^[0-9a-f]{40}$")
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
FIELDS={"id","kind","repository","revision","path","blob_sha1","issue_number","comment_id","claimed_actor","schema"}
ALLOWED={"v36.issue-receipt-stream/v1","v36.issue-continuity-chain/v1","v36.source-custody/v1"}

class SpineError(ValueError):
    pass

def need(ok,msg):
    if not ok: raise SpineError(msg)

def parse(url):
    x=urlsplit(url) if isinstance(url,str) else urlsplit("")
    p=x.path.strip("/").split("/")
    need(x.scheme=="https" and x.netloc=="github.com" and not x.query
         and not x.fragment and not x.username and len(p)==4
         and p[2]=="issues" and REPO.fullmatch("/".join(p[:2]))
         and re.fullmatch(r"[1-9][0-9]*",p[3]),"BAD_ISSUE_URL")
    return "/".join(p[:2]),int(p[3])

def path_valid(p):
    need(isinstance(p,str) and 0<len(p)<500 and not p.startswith("/")
         and "\\" not in p and all(s not in ("",".","..") for s in p.split("/")),
         "UNSAFE_SOURCE_PATH")
    return quote(p,safe="/")

def validate(idx,parent):
    need(isinstance(idx,dict) and set(idx)==
         {"schema","parent","source_cut","index_actor_claim","references"},
         "INDEX_SCHEMA_INVALID")
    need(idx["schema"]==SCHEMA and idx["parent"]==parent,"WRONG_PARENT")
    repo=parent.split("#")[0]
    cut=idx["source_cut"]
    need(isinstance(cut,dict) and set(cut)=={"repository","branch","revision"}
         and cut["repository"]==repo and cut["branch"]=="main"
         and isinstance(cut["revision"],str) and SHA.fullmatch(cut["revision"]),
         "INVALID_SOURCE_CUT")
    need(isinstance(idx["index_actor_claim"],str) and
         re.fullmatch(r"[A-Za-z0-9-]{1,39}",idx["index_actor_claim"]),
         "INVALID_INDEX_ACTOR")
    refs=idx["references"]
    need(isinstance(refs,list) and 1<=len(refs)<=30,"INVALID_REFERENCE_COUNT")
    ids=set()
    for r in refs:
        need(isinstance(r,dict) and set(r)==FIELDS,"INVALID_REF_FIELDS")
        rid=r["id"]
        need(isinstance(rid,str) and re.fullmatch(r"[A-Z][A-Z0-9_]{2,64}",rid)
             and rid not in ids,"DUPLICATE_REF")
        ids.add(rid)
        need(r["repository"]==repo,"FOREIGN_REFERENCE_REPOSITORY")
        if r["kind"]=="ISSUE_COMMENT":
            need(r["revision"] is None and r["path"] is None and
                 r["blob_sha1"] is None and r["schema"] is None and
                 type(r["issue_number"]) is int and
                 r["issue_number"]==int(parent.split("#")[1]) and
                 type(r["comment_id"]) is int and r["comment_id"]>0 and
                 isinstance(r["claimed_actor"],str),"COMMENT_SCOPE_INVALID")
        elif r["kind"]=="PINNED_JSON":
            need(isinstance(r["revision"],str) and SHA.fullmatch(r["revision"])
                 and isinstance(r["blob_sha1"],str) and SHA.fullmatch(r["blob_sha1"])
                 and r["schema"] in ALLOWED and
                 r["issue_number"] is None and r["comment_id"] is None
                 and r["claimed_actor"] is None,"PINNED_JSON_INVALID")
            path_valid(r["path"])
        else: raise SpineError("INVALID_REFERENCE_KIND")
    return idx

def decode_comment(text,parent):
    prefix=MARKER.format(parent)+"\n\x60\x60\x60json\n"
    suffix="\n\x60\x60\x60\n"
    need(isinstance(text,str) and len(text)<18000 and
         text.startswith(prefix) and text.endswith(suffix),
         "INDEX_MUST_BE_EXACT_JSON_FENCE")
    return validate(json.loads(text[len(prefix):-len(suffix)]),parent)

class Reader:
    def __init__(self,token=None): self.token=token
    def get(self,path):
        need(path.startswith("/repos/") and ".." not in path,
             "UNSAFE_PROVIDER_REQUEST")
        headers={"Accept":"application/vnd.github+json","User-Agent":"v36-r2-readonly"}
        if self.token: headers["Authorization"]="Bearer "+self.token
        try:
            with urlopen(Request("https://api.github.com"+path,
                                 headers=headers,method="GET"),timeout=25) as response:
                raw=response.read(2*1024*1024+1)
            need(len(raw)<=2*1024*1024,"PROVIDER_RESPONSE_TOO_LARGE")
            return json.loads(raw)
        except HTTPError as e:
            raise SpineError("PROVIDER_NOT_FOUND_OR_DENIED_"+str(e.code)) from e
        except (URLError,TimeoutError,ValueError) as e:
            raise SpineError("PROVIDER_UNAVAILABLE") from e

def resolve_comment(c,repo,ref):
    item={"id":ref["id"],"kind":"ISSUE_COMMENT","provider_observed":False}
    try:
        obj=c.get("/repos/"+repo+"/issues/comments/"+str(ref["comment_id"]))
        need(obj.get("id")==ref["comment_id"] and
             obj.get("issue_url")=="https://api.github.com/repos/"+repo+
             "/issues/"+str(ref["issue_number"]),"COMMENT_PARENT_OR_ID_CHANGED")
        actor=obj.get("user",{}).get("login")
        need(isinstance(actor,str) and
             actor.casefold()==ref["claimed_actor"].casefold(),
             "COMMENT_ACTOR_CONTRADICTED")
        body=obj.get("body")
        need(isinstance(body,str),"COMMENT_BODY_NOT_FOUND")
        item.update(provider_observed=True,status="ACCOUNT_AND_BODY_OBSERVED_NOT_OWNER_APPROVAL",
                    actor=actor,body_sha256=hashlib.sha256(body.encode()).hexdigest(),
                    url="https://github.com/"+repo+"/issues/"+str(ref["issue_number"])+
                    "#issuecomment-"+str(ref["comment_id"]))
    except (SpineError,KeyError,TypeError) as e: item["status"]=str(e)
    return item

def resolve_json(c,repo,ref,parent,links):
    out={"id":ref["id"],"kind":"PINNED_JSON","provider_observed":False}
    try:
        meta=c.get("/repos/"+repo+"/contents/"+path_valid(ref["path"])+
                   "?ref="+ref["revision"])
        need(meta.get("type")=="file" and meta.get("sha")==ref["blob_sha1"]
             and meta.get("encoding")=="base64","FILE_PIN_CONTRADICTED")
        raw=base64.b64decode(meta["content"],validate=False)
        expected=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
        need(len(raw)<256*1024 and expected==ref["blob_sha1"],
             "FILE_BYTES_CONTRADICTED")
        data=json.loads(raw)
        need(data.get("schema")==ref["schema"],"FILE_SCHEMA_CONTRADICTED")
        out.update(provider_observed=True,sha256=hashlib.sha256(raw).hexdigest(),
                   schema=ref["schema"],status="PINNED_JSON_BYTES_VERIFIED")
        if ref["schema"]=="v36.issue-receipt-stream/v1":
            need(data.get("parent")==parent,"C1B_PARENT_MISMATCH")
            rows=data.get("events",[])
            need(isinstance(rows,list) and rows,"C1B_EMPTY")
            urls={x.get("url") for x in links if x["provider_observed"]}
            matched=sum(x.get("source_ref") in urls for x in rows)
            out.update(events=len(rows),source_refs_matched=matched,
                       status="C1B_REPORTED_SOURCE_LINKED_NOT_OWNER_AUTHENTICATED")
        elif ref["schema"]=="v36.issue-continuity-chain/v1":
            out["reported_parent"]=data.get("parent")
            if data.get("parent")!=parent:
                out["status"]="C1_FOREIGN_PARENT_EXAMPLE_NOT_LIVE_ISSUE_HISTORY"
        else:
            out["artifact_claims"]=len(data.get("artifacts",[]))
            out["source_repository"]=data.get("repository")
            out["status"]="C2_MANIFEST_PINNED_BUT_ARTIFACTS_NOT_REATTESTED"
    except (SpineError,KeyError,ValueError,TypeError) as e:
        out.update(provider_observed=False,status=str(e))
    return out

def audit(issue_url,c):
    repo,num=parse(issue_url)
    parent=repo+"#"+str(num)
    issue=c.get("/repos/"+repo+"/issues/"+str(num))
    need(issue.get("number")==num and "pull_request" not in issue,
         "PARENT_MISSING_OR_PR")
    found=[]
    for page in range(1,11):
        rows=c.get("/repos/"+repo+"/issues/"+str(num)+
                   "/comments?per_page=100&page="+str(page))
        need(isinstance(rows,list),"ISSUE_COMMENTS_UNAVAILABLE")
        for row in rows:
            if (isinstance(row,dict) and isinstance(row.get("body"),str) and
                    MARKER.format(parent) in row["body"]):
                found.append(row)
        if len(rows)<100: break
    need(len(found)==1,"INDEX_MISSING" if not found else "INDEX_AMBIGUOUS")
    index=decode_comment(found[0]["body"],parent)
    actor=found[0].get("user",{}).get("login")
    need(isinstance(actor,str) and
         actor.casefold()==index["index_actor_claim"].casefold(),
         "INDEX_ACTOR_CONTRADICTED")
    live=c.get("/repos/"+repo+"/branches/main")
    sha=live.get("commit",{}).get("sha")
    need(isinstance(sha,str) and SHA.fullmatch(sha),"LIVE_MAIN_UNKNOWN")
    links=[resolve_comment(c,repo,r) for r in index["references"]
           if r["kind"]=="ISSUE_COMMENT"]
    files=[resolve_json(c,repo,r,parent,links) for r in index["references"]
           if r["kind"]=="PINNED_JSON"]
    all_sources=links+files
    failures=[x["id"] for x in all_sources if not x["provider_observed"]]
    current=sha==index["source_cut"]["revision"]
    return {"schema":"v36.live-issue-spine-audit/v1","parent":parent,
            "index_comment_id":found[0]["id"],"index_actor_observed":actor,
            "index_status":"ONE_PROVIDER_OBSERVED_INDEX_NOT_OWNER_AUTHENTICATED",
            "source_cut_current":current,"live_main":sha,
            "references_total":len(all_sources),
            "references_observed":len(all_sources)-len(failures),
            "source_comments":links,"versioned_contracts":files,
            "missing_or_contradicted":failures,
            "status":("LIVE_INDEX_OBSERVED_SOURCE_AUTHORITY_UNVERIFIED" if current
                      and not failures else "LIVE_INDEX_HOLD_STALE_OR_MISSING"),
            "verified_chain_categories":0,"owner_accepted":False,
            "semantic_accepted":False,"complete_golden_accepted":False,
            "twelve_section_recovery_complete":False,
            "may_publish":False,"may_count_for_o2":False,
            "may_change_titles_or_labels":False,"may_merge_or_release":False}

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--issue-url",required=True)
    args=p.parse_args(argv)
    try: out=audit(args.issue_url,Reader(os.environ.get("GITHUB_TOKEN")))
    except (SpineError,TypeError,KeyError) as e:
        print(json.dumps({"status":"R2_READ_BLOCKED","reason":str(e),
                          "may_publish":False,"may_merge_or_release":False}))
        return 2
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
