#!/usr/bin/env python3
"""Independent WP5 artifact and source-freshness checker; no compiler import.

Recomputes all digests, section ordering, claim IDs, safety flags and exact source
heads; even a VALID packet NEVER grants engineering or Owner decision authority.
"""
import argparse
import hashlib
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HEADERS=("Original problem, Owner WHY and user-visible outcomes",
 "Original issue, roadmap, amendments and authority",
 "Repository identity, source cuts and dependency graph",
 "Real user and system flow",
 "Engineering history, investigations and rejected approaches",
 "Changed code and architecture","Input sources and custody",
 "Golden fixtures, benchmarks and observed outcomes",
 "Tests, CI and exact-head evidence","Failures, uncertainties, risks and falsifiers",
 "Step-back reconciliation: KEEP versus IMPROVE",
 "Exact successor starting point and gates")
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
OID=re.compile(r"^[0-9a-f]{40}$")

class VerificationError(ValueError):pass

def canonical(d):
    return json.dumps(d,sort_keys=True,ensure_ascii=False,
                      separators=(",",":"),allow_nan=False).encode("utf-8")

def digest(b):return hashlib.sha256(b).hexdigest()

def assert_value(condition,message):
    if not condition: raise VerificationError(message)

def local_verify(packet,report,manifest,verdict):
    assert_value(isinstance(packet,dict) and isinstance(manifest,dict) and
                 isinstance(verdict,dict) and isinstance(report,str),"invalid artifact types")
    source_sha=digest(canonical(packet))
    report_sha=digest(report.encode("utf-8"))
    manifest_sha=digest(canonical(manifest))
    assert_value(packet.get("schema")=="onboarding.handover-input/v1" and
                 manifest.get("schema")=="onboarding.manifest/v1" and
                 verdict.get("schema")=="onboarding.verdict/v1","invalid artifact version")
    assert_value(source_sha==manifest.get("source_sha256")==verdict.get("source_sha256"),
                 "source input or manifest digest mismatch")
    assert_value(report_sha==manifest.get("report_sha256")==verdict.get("report_sha256"),
                 "Markdown report changed after compilation")
    assert_value(manifest_sha==verdict.get("manifest_sha256"),
                 "manifest tampered or verdict out of sync")
    assert_value(manifest.get("section_names")==list(HEADERS),"section contract differs")
    headings=re.findall(r"^## ([0-9]+)\. (.+)$",report,re.MULTILINE)
    assert_value(headings==[(str(i),name) for i,name in enumerate(HEADERS,1)],
                 "12-section heading count/order tampered")
    sections=packet.get("sections")
    assert_value(isinstance(sections,list) and len(sections)==12,
                 "source lost a required section")
    claims=packet.get("claims")
    assert_value(isinstance(claims,list) and len(claims)>=12,
                 "missing source-grounded claims")
    seen=set()
    for c in claims:
        assert_value(isinstance(c,dict),"malformed claim")
        key=c.get("id")
        assert_value(isinstance(key,str) and re.fullmatch(r"C[0-9]{2,4}",key)
                     and key not in seen,"claim ID collision")
        seen.add(key)
        assert_value(report.count("["+key+"]")==1,"claim missing/duplicated in Markdown")
        assert_value(c.get("visibility")=="PUBLIC","private fact in public artifacts")
        assert_value(c.get("status") in ("SOURCE_REPORTED","BYTE_MATCH_REPORTED","UNKNOWN"),
                     "untrusted source status promoted to provider VERIFIED")
        if c.get("status")=="UNKNOWN":
            assert_value(c.get("source_url") is None and c.get("revision") is None,
                         "unknown source promoted to cited fact")
        else:
            assert_value(isinstance(c.get("source_url"),str) and c["source_url"] in report,
                         "reported source missing hyperlink in handover")
        assert_value(c in manifest.get("claims",[]),"report claim absent from manifest")
    assert_value(packet.get("critical_gaps")==manifest.get("critical_gaps") and
                 sorted(packet["critical_gaps"])==verdict.get("reason_codes"),
                 "critical evidence gap list rewritten")
    assert_value(packet.get("first_verification")==
                 manifest.get("first_verification")==verdict.get("next_verification"),
                 "first verification changed or omitted")
    assert_value(packet.get("target",{}).get("source_heads")==manifest.get("source_heads") and
                 packet.get("target",{}).get("candidate_heads")==manifest.get("candidate_heads"),
                 "source identity not synchronized")
    assert_value(packet.get("custody")==manifest.get("custody") and
                 packet.get("tests")==manifest.get("tests"),
                 "original fixture or CI evidence changed")
    for k in ("execution_authorized","owner_approval_verified","provider_freshness_verified"):
        assert_value(manifest.get(k) is False and verdict.get(k) is False,
                     "authority/freshness flag illegally promoted")
    assert_value(verdict.get("rwi_disposition")=="NOT_EVALUATED" and
                 verdict.get("status")=="BLOCKED","missing Owner authority did not block")
    assert_value("EXECUTION HOLD" in report and "NOT_EVALUATED" in report,
                 "unsafe actionable handover")
    assert_value("Source packet SHA-256: "+source_sha in report,
                 "readable source digest not bound to Markdown")
    return {"status":"INTEGRITY_VALID_BUT_BLOCKED",
            "sections":len(headings),"claims":len(claims),
            "source_sha256":source_sha,"report_sha256":report_sha,
            "manifest_sha256":manifest_sha,"execution_authorized":False}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

class GitHubRead:
    """No token, no redirect, no write methods, no arbitrary caller-supplied URLs."""
    def __init__(self,timeout=15):
        self.opener=urllib.request.build_opener(NoRedirect())
        self.timeout=timeout

    def get(self,repository,resource):
        assert_value(isinstance(repository,str) and REPO.fullmatch(repository),
                     "invalid provider repository")
        assert_value(re.fullmatch(r"[A-Za-z0-9_./-]+",resource)
                     and not any(x in ("",".","..") for x in resource.split("/")),
                     "invalid immutable provider resource")
        url="https://api.github.com/repos/"+repository+"/"+resource
        req=urllib.request.Request(url,method="GET",headers={
            "Accept":"application/vnd.github+json","User-Agent":"onb-rwi-wp5-readonly",
            "X-GitHub-Api-Version":"2022-11-28"})
        try:
            with self.opener.open(req,timeout=self.timeout) as result:
                if result.geturl()!=url:
                    raise VerificationError("provider redirect")
                raw=result.read(1000000)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            raise VerificationError("provider source currently unavailable") from exc
        try:obj=json.loads(raw)
        except ValueError as exc:raise VerificationError("provider returned invalid JSON") from exc
        if not isinstance(obj,dict):raise VerificationError("non-object provider metadata")
        return obj

def check_live_heads(manifest,provider):
    """Freshly READ BOTH default-branch and selected draft PR heads. Never infer merge."""
    heads=manifest.get("source_heads")
    candidates=manifest.get("candidate_heads")
    if not isinstance(heads,dict) or not isinstance(candidates,dict):
        raise VerificationError("missing live-bound HEAD manifest")
    checks=[]
    for repo,expected in heads.items():
        meta=provider.get(repo,"meta") if getattr(provider,"is_fake",False) else None
        # REST repository metadata is /repos/owner/repo, without a trailing suffix.
        # Prefer a caller-provided method so mocks cannot be conflated with production.
        if meta is None:
            if not hasattr(provider,"get_repo"):
                raise VerificationError("provider metadata method unavailable")
            meta=provider.get_repo(repo)
        default=meta.get("default_branch")
        if not isinstance(default,str) or not re.fullmatch(r"[A-Za-z0-9_.-]+",default):
            raise VerificationError("invalid default-branch identity")
        current=provider.get(repo,"commits/"+default).get("sha")
        if current!=expected:
            raise VerificationError("STALE: "+repo+" main revision changed")
        checks.append({"repo":repo,"kind":"default_head","sha":current})
    for url,expected in candidates.items():
        p=urllib.parse.urlsplit(url)
        if p.scheme!="https" or p.netloc!="github.com" or p.query or p.fragment:
            raise VerificationError("invalid PR source reference")
        seg=p.path.strip("/").split("/")
        if len(seg)!=4 or seg[2]!="pull" or not seg[3].isdigit():
            raise VerificationError("invalid PR ref")
        repo="/".join(seg[:2])
        if repo not in heads:raise VerificationError("foreign candidate")
        result=provider.get(repo,"pulls/"+seg[3])
        head=result.get("head")
        if not isinstance(head,dict) or head.get("sha")!=expected:
            raise VerificationError("STALE: "+url+" candidate revision changed")
        if result.get("state") not in ("open","closed"):
            raise VerificationError("PR state not received")
        checks.append({"repo":repo,"kind":"pr","number":int(seg[3]),
                       "sha":expected,"state":result["state"],"draft":result.get("draft")})
    return {"state":"LIVE_HEADS_MATCH_OBSERVED","checked":checks,
            "owner_approval_verified":False,"execution_authorized":False}

def get_repo(self,repo):
    """GET repository root through the same strict token-free transport."""
    assert_value(isinstance(repo,str) and REPO.fullmatch(repo),"invalid repository")
    url="https://api.github.com/repos/"+repo
    req=urllib.request.Request(url,method="GET",headers={
        "Accept":"application/vnd.github+json","User-Agent":"onb-rwi-wp5-readonly"})
    try:
        with self.opener.open(req,timeout=self.timeout) as response:
            if response.geturl()!=url:raise VerificationError("redirected metadata")
            data=response.read(1000000)
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
        raise VerificationError("provider metadata unavailable") from exc
    try:meta=json.loads(data)
    except ValueError as exc:raise VerificationError("invalid metadata JSON") from exc
    if not isinstance(meta,dict) or meta.get("full_name")!=repo:
        raise VerificationError("canonical repository not confirmed")
    return meta
GitHubRead.get_repo=get_repo

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",required=True);p.add_argument("--report",required=True)
    p.add_argument("--manifest",required=True);p.add_argument("--verdict",required=True)
    p.add_argument("--live",action="store_true")
    a=p.parse_args()
    try:
        packet=json.loads(Path(a.input).read_text(encoding="utf-8"))
        report=Path(a.report).read_text(encoding="utf-8")
        manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
        verdict=json.loads(Path(a.verdict).read_text(encoding="utf-8"))
        output=local_verify(packet,report,manifest,verdict)
        if a.live:output["freshness"]=check_live_heads(manifest,GitHubRead())
        print(json.dumps(output,sort_keys=True))
        return 0
    except (VerificationError,ValueError,TypeError,OSError) as exc:
        print(json.dumps({"status":"BLOCKED_OR_STALE","reason":str(exc),
                          "execution_authorized":False},sort_keys=True))
        return 2
if __name__=="__main__":raise SystemExit(main())
