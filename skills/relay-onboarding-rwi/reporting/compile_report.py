#!/usr/bin/env python3
"""ONB #391 WP5. Pure, deterministic 12-section technical report compiler.
Source-referenced input is NOT authenticated Owner approval or provider truth.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

NAMES=(
 "Original problem, Owner WHY and user-visible outcomes",
 "Original issue, roadmap, amendments and authority",
 "Repository identity, source cuts and dependency graph",
 "Real user and system flow",
 "Engineering history, investigations and rejected approaches",
 "Changed code and architecture",
 "Input sources and custody",
 "Golden fixtures, benchmarks and observed outcomes",
 "Tests, CI and exact-head evidence",
 "Failures, uncertainties, risks and falsifiers",
 "Step-back reconciliation: KEEP versus IMPROVE",
 "Exact successor starting point and gates",
)
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA40=re.compile(r"^[0-9a-f]{40}$")
SHA64=re.compile(r"^[0-9a-f]{64}$")
CLAIM_ID=re.compile(r"^C[0-9]{2,4}$")
STATUSES={"SOURCE_REPORTED","BYTE_MATCH_REPORTED","UNKNOWN"}
GAPS={"OWNER_APPROVAL_MISSING","CODE_PATH_NOT_ATTESTED","COMPLETE_GOLDEN_MISSING",
      "CURRENT_PROVIDER_RECHECK_REQUIRED","INDEPENDENT_REVIEW_MISSING","OTHER"}

class Invalid(ValueError): pass

def canonical(v):
    return json.dumps(v,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf-8")

def digest(value):
    return hashlib.sha256(value).hexdigest()

def fields(value,keys,label):
    if not isinstance(value,dict) or set(value)!=set(keys):
        raise Invalid(label+" keys are missing/extra")
    return value

def text(value,label,minsize=18,maxsize=3500):
    if not isinstance(value,str) or not minsize<=len(value.strip())<=maxsize:
        raise Invalid(label+" must have substantive bounded text")
    return value

def repository(value):
    if not isinstance(value,str) or not REPO.fullmatch(value):
        raise Invalid("invalid owner/repo identity")
    return value

def sha(value,size=40):
    patt=SHA40 if size==40 else SHA64
    if not isinstance(value,str) or not patt.fullmatch(value):
        raise Invalid("invalid SHA")
    return value

def link(value,repo,pr=False):
    if not isinstance(value,str) or len(value)>2000:
        raise Invalid("invalid citation URL")
    try: parsed=urlsplit(value)
    except ValueError as exc: raise Invalid("invalid citation URL") from exc
    paths=parsed.path.strip("/").split("/")
    if (parsed.scheme!="https" or parsed.netloc!="github.com" or
        parsed.username or parsed.password or parsed.query or
        len(paths)<3 or any(p in ("",".","..") for p in paths) or
        "/".join(paths[:2])!=repo or
        (parsed.fragment and not re.fullmatch(r"issuecomment-[0-9]+|L[1-9][0-9]*(?:-L[1-9][0-9]*)?",parsed.fragment))):
        raise Invalid("cross-repo/unsafe citation URL")
    if pr and (len(paths)!=4 or paths[2]!="pull" or not paths[3].isdigit() or int(paths[3])<1):
        raise Invalid("expected exact PR reference")
    return value

def check(data):
    fields(data,("schema","target","sections","claims","custody","tests",
                 "critical_gaps","first_verification"),"packet")
    if data["schema"]!="onboarding.handover-input/v1":
        raise Invalid("wrong input contract")
    target=fields(data["target"],("repository","issue","observed_at","source_heads",
                                   "candidate_heads","subject"),"target")
    own=repository(target["repository"])
    if type(target["issue"]) is not int or target["issue"]<1: raise Invalid("invalid issue")
    text(target["subject"],"report subject")
    try: when=dt.datetime.fromisoformat(target["observed_at"].replace("Z","+00:00"))
    except (TypeError,ValueError,AttributeError) as exc: raise Invalid("invalid cutoff") from exc
    if when.utcoffset() is None: raise Invalid("cutoff timezone missing")
    heads=target["source_heads"]
    if not isinstance(heads,dict) or own not in heads:
        raise Invalid("target main missing")
    for k,v in heads.items(): repository(k);sha(v)
    candidates=target["candidate_heads"]
    if not isinstance(candidates,dict): raise Invalid("PR head set missing")
    for url,rev in candidates.items():
        p=urlsplit(url)
        repo="/".join(p.path.strip("/").split("/")[:2])
        if repo not in heads: raise Invalid("foreign candidate repo")
        link(url,repo,pr=True);sha(rev)
    claims={}
    if not isinstance(data["claims"],list): raise Invalid("claims missing")
    for c in data["claims"]:
        fields(c,("id","section","statement","status","repository","revision",
                  "source_url","visibility"),"claim")
        ident=c["id"]
        if not isinstance(ident,str) or not CLAIM_ID.fullmatch(ident) or ident in claims:
            raise Invalid("invalid/duplicate claim ID")
        if type(c["section"]) is not int or not 1<=c["section"]<=12:
            raise Invalid("invalid claim section")
        text(c["statement"],"claim")
        if c["visibility"]!="PUBLIC": raise Invalid("nonpublic claims cannot render")
        if c["status"] not in STATUSES: raise Invalid("untrusted source cannot assert verified Owner fact")
        if c["status"]=="UNKNOWN":
            if c["revision"] is not None or c["source_url"] is not None:
                raise Invalid("unknown claim cannot carry implied source")
            if c["repository"] is not None: repository(c["repository"])
        else:
            repo=repository(c["repository"])
            if repo not in heads: raise Invalid("foreign source claim")
            sha(c["revision"]);link(c["source_url"],repo)
        claims[ident]=c
    if not isinstance(data["sections"],list) or len(data["sections"])!=12:
        raise Invalid("exactly 12 sections required")
    included=set()
    for n,s in enumerate(data["sections"],1):
        fields(s,("index","paragraphs","claim_ids"),"section")
        if type(s["index"]) is not int or s["index"]!=n: raise Invalid("wrong 12-section order")
        if not isinstance(s["paragraphs"],list) or len(s["paragraphs"])<2:
            raise Invalid("section lacks substantive explanation")
        for p in s["paragraphs"]: text(p,"paragraph")
        if not isinstance(s["claim_ids"],list) or not s["claim_ids"]:
            raise Invalid("section has no source claims")
        for key in s["claim_ids"]:
            if key not in claims or key in included or claims[key]["section"]!=n:
                raise Invalid("orphaned, repeated or cross-section claim")
            included.add(key)
    if included!=set(claims): raise Invalid("some claims were omitted")
    for name,group,keys in (
        ("custody",data["custody"],("id","path","repository","revision","sha256","status","source_url")),
        ("test",data["tests"],("id","repository","candidate_sha","command","result","oracle","source_url"))):
        if not isinstance(group,list):raise Invalid(name+" must be a list")
        seen=set()
        for row in group:
            fields(row,keys,name)
            if not isinstance(row["id"],str) or not row["id"] or row["id"] in seen:
                raise Invalid("duplicate "+name+" receipt")
            seen.add(row["id"])
            repo=repository(row["repository"])
            if repo not in heads:raise Invalid("foreign "+name+" evidence")
            sha(row["revision"] if name=="custody" else row["candidate_sha"])
            if name=="custody":
                p=row["path"]
                if not isinstance(p,str) or not p or p.startswith("/") or ".." in p.split("/"):
                    raise Invalid("custody path invalid")
                if row["status"] not in ("HASH_MATCH_REPORTED","UNVERIFIED","UNKNOWN"):
                    raise Invalid("invalid custody state")
                if row["sha256"] is not None:sha(row["sha256"],64)
                if row["status"]=="HASH_MATCH_REPORTED" and row["sha256"] is None:
                    raise Invalid("hash match without original digest")
            else:
                text(row["command"],"test command")
                text(row["oracle"],"test oracle")
                if row["result"] not in ("PASS_REPORTED","FAIL_REPORTED","NOT_RUN","UNKNOWN"):
                    raise Invalid("invalid test state")
            if row["source_url"] is not None:link(row["source_url"],repo)
            if ((name=="custody" and row["status"]=="HASH_MATCH_REPORTED") or
                (name=="test" and row["result"] in ("PASS_REPORTED","FAIL_REPORTED"))):
                if row["source_url"] is None:raise Invalid("claim of success without source receipt")
    gaps=data["critical_gaps"]
    if not isinstance(gaps,list) or not gaps or len(gaps)!=len(set(gaps)) or any(g not in GAPS for g in gaps):
        raise Invalid("invalid or concealed critical blockers")
    text(data["first_verification"],"first verification")
    return target,claims

def quote(value):
    """Source prose is data; JSON quotes escape multiline Markdown injection."""
    return json.dumps(value,ensure_ascii=False)

def build(data):
    target,claims=check(data)
    source_hash=digest(canonical(data))
    lines=["# ONBOARDING — source-first technical handover (NOT ACCEPTED)",
           "", "Source packet SHA-256: "+source_hash,
           "Observed cut: "+target["observed_at"],
           "Target: "+target["repository"]+" issue #"+str(target["issue"]),
           "EXECUTION HOLD · OWNER APPROVAL NOT VERIFIED · RWI NOT_EVALUATED",
           "",
           "> All source URLs and claimed results require independent provider verification.",
           "> This report never authorizes a code write, merge, Owner decision or release.",""]
    for s in data["sections"]:
        n=s["index"]
        lines+=["## "+str(n)+". "+NAMES[n-1],""]
        for p in s["paragraphs"]:lines += [quote(p),""]
        for cid in s["claim_ids"]:
            c=claims[cid]
            lines.append("- ["+cid+"] "+quote(c["statement"])+" — "+c["status"])
            if c["source_url"] is not None:
                lines.append("  Source: "+c["source_url"]+" | revision: "+c["revision"])
        if n==7:
            lines+=["","Original input custody; receipt assertions are not benchmark acceptance:"]
            for row in data["custody"]:
                lines.append("- "+quote(row["path"])+" "+row["status"]+
                             " SHA256: "+str(row["sha256"])+" | "+str(row["source_url"]))
        if n==9:
            lines+=["","Exact candidate CI/test receipts (source-reported):"]
            for row in data["tests"]:
                lines.append("- "+row["id"]+" "+row["result"]+" at "+row["candidate_sha"]+
                             " command: "+quote(row["command"])+" | "+str(row["source_url"]))
        if n==10: lines+=["","Critical blockers: "+", ".join(sorted(data["critical_gaps"]))]
        if n==12:
            lines+=["","One first verification: "+quote(data["first_verification"]),
                    "Execution / protected Owner actions / merge: HOLD."]
        lines.append("")
    report="\n".join(lines)
    report_hash=digest(report.encode("utf-8"))
    manifest={"schema":"onboarding.manifest/v1","source_sha256":source_hash,
              "report_sha256":report_hash,"section_names":list(NAMES),
              "source_cut":target["observed_at"],"repository":target["repository"],
              "issue":target["issue"],"source_heads":target["source_heads"],
              "candidate_heads":target["candidate_heads"],
              "claims":data["claims"],"custody":data["custody"],"tests":data["tests"],
              "critical_gaps":data["critical_gaps"],
              "first_verification":data["first_verification"],
              "provider_freshness_verified":False,"owner_approval_verified":False,
              "execution_authorized":False}
    mh=digest(canonical(manifest))
    verdict={"schema":"onboarding.verdict/v1","status":"BLOCKED",
             "reason_codes":sorted(data["critical_gaps"]),
             "source_sha256":source_hash,"report_sha256":report_hash,
             "manifest_sha256":mh,"provider_freshness_verified":False,
             "owner_approval_verified":False,"execution_authorized":False,
             "rwi_disposition":"NOT_EVALUATED",
             "next_verification":data["first_verification"]}
    return report,manifest,verdict

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        data=json.loads(Path(args.input).read_text(encoding="utf-8"))
        report,manifest,verdict=build(data)
        out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
        (out/"ONBOARDING.md").write_text(report,encoding="utf-8")
        (out/"onboarding-manifest.json").write_text(
            json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
        (out/"onboarding-verdict.json").write_text(
            json.dumps(verdict,indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({"status":verdict["status"],"source_sha256":verdict["source_sha256"],
                          "manifest_sha256":verdict["manifest_sha256"],
                          "report_sha256":verdict["report_sha256"],
                          "execution_authorized":False},sort_keys=True))
        return 0
    except (Invalid,OSError,ValueError,TypeError) as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),"execution_authorized":False}))
        return 2

if __name__=="__main__":raise SystemExit(main())
