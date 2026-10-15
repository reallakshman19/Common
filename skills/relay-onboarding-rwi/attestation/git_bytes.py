#!/usr/bin/env python3
"""ONB-RWI WP4 public Git commit→tree→blob byte attestor. GET only, no acceptance."""
import argparse
import base64
import binascii
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PART = re.compile(r"^[A-Za-z0-9_.@+ -]+$")
MAX_SOURCE_BYTES = 8_000_000
MAX_JSON_BYTES = 12_000_000

class AttestationError(ValueError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class GitHubGet:
    """HTTP GET strictly on Git object endpoints, never mutable branch paths."""
    def __init__(self, timeout=25):
        self.timeout = timeout
        self.opener = urllib.request.build_opener(NoRedirect())

    def get_object(self, repository, kind, oid):
        repository = require_repo(repository)
        require_sha(oid)
        if kind not in ("commits", "trees", "blobs"):
            raise AttestationError("unapproved Git REST route")
        url = f"https://api.github.com/repos/{repository}/git/{kind}/{oid}"
        req = urllib.request.Request(url, method="GET",
            headers={"Accept":"application/vnd.github+json",
                     "X-GitHub-Api-Version":"2022-11-28","User-Agent":"onb-rwi-wp4"})
        try:
            with self.opener.open(req, timeout=self.timeout) as response:
                if response.geturl() != url:
                    raise AttestationError("Git object REST redirect denied")
                raw = response.read(MAX_JSON_BYTES + 1)
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError) as exc:
            raise AttestationError("Git provider object unavailable") from exc
        if len(raw) > MAX_JSON_BYTES:
            raise AttestationError("provider payload over size budget")
        try:
            obj = json.loads(raw)
        except (ValueError,UnicodeDecodeError) as exc:
            raise AttestationError("invalid Git provider JSON") from exc
        if not isinstance(obj,dict):
            raise AttestationError("non-object Git response")
        return obj

def require_repo(value):
    if not isinstance(value,str) or not REPO.fullmatch(value):
        raise AttestationError("invalid owner/repo")
    return value

def require_sha(value,bits=40):
    patt = HEX40 if bits == 40 else HEX64
    if not isinstance(value,str) or not patt.fullmatch(value):
        raise AttestationError("invalid digest")
    return value

def parts_of(path):
    if not isinstance(path,str) or not path or len(path) > 1024:
        raise AttestationError("invalid path length")
    parts=path.split("/")
    if len(parts)>24 or any(not PART.fullmatch(x) or x in (".","..") for x in parts):
        raise AttestationError("path traversal or unsupported path")
    return parts

def blob_id(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()

def blob_bytes(blob,oid):
    if blob.get("sha")!=oid or blob.get("encoding")!="base64":
        raise AttestationError("Git blob identity or encoding invalid")
    n=blob.get("size")
    if type(n) is not int or n<0 or n>MAX_SOURCE_BYTES:
        raise AttestationError("source size exceeds policy")
    encoded=blob.get("content")
    if not isinstance(encoded,str) or len(encoded)>11_000_000:
        raise AttestationError("invalid source encoding")
    try:
        data=base64.b64decode("".join(encoded.split()),validate=True)
    except (ValueError,binascii.Error) as exc:
        raise AttestationError("invalid source base64") from exc
    if len(data)!=n or blob_id(data)!=oid:
        raise AttestationError("Git byte/size digest mismatch")
    return data

def get_verified_bytes(provider,repository,revision,path):
    repo=require_repo(repository)
    rev=require_sha(revision)
    parts=parts_of(path)
    commit=provider.get_object(repo,"commits",rev)
    if commit.get("sha")!=rev or not isinstance(commit.get("tree"),dict):
        raise AttestationError("commit or root tree does not match pinned SHA")
    tree_id=require_sha(commit["tree"].get("sha"))
    trace=[]
    for i,part in enumerate(parts):
        tree=provider.get_object(repo,"trees",tree_id)
        if tree.get("sha")!=tree_id or tree.get("truncated") is True:
            raise AttestationError("incomplete or mismatched source tree")
        records=tree.get("tree")
        if not isinstance(records,list):
            raise AttestationError("source tree has no entries")
        entries=[e for e in records if isinstance(e,dict) and e.get("path")==part]
        if len(entries)!=1:
            raise AttestationError("pinned path absent or ambiguous")
        entry=entries[0]
        oid=require_sha(entry.get("sha"))
        if i<len(parts)-1:
            if entry.get("type")!="tree":
                raise AttestationError("parent is not a tree")
            tree_id=oid
        elif entry.get("type")!="blob" or entry.get("mode") not in ("100644","100755"):
            raise AttestationError("final path is not regular file")
        trace.append({"name":part,"object":oid,"kind":entry.get("type")})
    oid=trace[-1]["object"]
    return blob_bytes(provider.get_object(repo,"blobs",oid),oid),oid,trace

def verify(provider,repository,revision,path,claimed_sha256=None,line_start=None,line_end=None):
    if claimed_sha256 is not None: require_sha(claimed_sha256,64)
    if (line_start is None)!=(line_end is None):
        raise AttestationError("source-line range must have two bounds")
    data,oid,trace=get_verified_bytes(provider,repository,revision,path)
    digest=hashlib.sha256(data).hexdigest()
    comparison=("NO_OWNER_HASH" if claimed_sha256 is None
                else "MATCH" if digest==claimed_sha256 else "MISMATCH")
    line_digest=None
    if line_start is not None:
        if type(line_start) is not int or type(line_end) is not int or line_start<1 or line_end<line_start:
            raise AttestationError("invalid line bounds")
        try:
            lines=data.decode("utf-8").splitlines(keepends=True)
        except UnicodeDecodeError as exc:
            raise AttestationError("line source cannot decode UTF-8") from exc
        if line_end>len(lines):
            raise AttestationError("line span exceeds file")
        line_digest=hashlib.sha256("".join(lines[line_start-1:line_end]).encode("utf-8")).hexdigest()
    return {"schema":"onboarding.git-byte-attestation/v1",
            "repository":repository,"revision":revision,"path":path,
            "blob_oid":oid,"size":len(data),"observed_sha256":digest,
            "claimed_sha256":claimed_sha256,"comparison":comparison,
            "line_range":[line_start,line_end] if line_start is not None else None,
            "line_sha256":line_digest,"tree_walk":trace,
            "provider_git_bytes_read":True,
            "owner_approval_verified":False,"semantic_code_path_verified":False,
            "benchmark_complete":False,"execution_authorized":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True);ap.add_argument("--rev",required=True)
    ap.add_argument("--path",required=True);ap.add_argument("--claimed-sha256")
    ap.add_argument("--line-start",type=int);ap.add_argument("--line-end",type=int)
    a=ap.parse_args()
    try:
        result=verify(GitHubGet(),a.repo,a.rev,a.path,a.claimed_sha256,a.line_start,a.line_end)
        print(json.dumps(result,sort_keys=True))
        return 3 if result["comparison"]=="MISMATCH" else 0
    except AttestationError as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc),
                          "execution_authorized":False}),file=sys.stderr)
        return 2

if __name__=="__main__": raise SystemExit(main())
