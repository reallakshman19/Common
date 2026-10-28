#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, posixpath, subprocess
from pathlib import Path
from typing import Any
import yaml
from coordlib import dump_yaml, load_yaml, validate as schema_validate

KIND_TO_CLAIM = {"PRESERVATION":"PRESERVATION","COMPATIBILITY":"COMPATIBILITY","AUTHORITY":"AUTHORITY"}
SOURCE_HEADING = "## Precommitted L1 selector source"

def extract_precommitted_source(markdown: str) -> dict[str, Any]:
    if not isinstance(markdown, str):
        raise ValueError("GitHub issue body must be text")
    if markdown.count(SOURCE_HEADING) != 1:
        raise ValueError("GitHub issue must contain exactly one precommitted L1 source heading")
    tail = markdown.split(SOURCE_HEADING, 1)[1]
    start = tail.find("```yaml")
    if start < 0:
        raise ValueError("Precommitted L1 source must use a yaml code fence")
    after = tail[start + len("```yaml"):]
    end = after.find("```")
    if end < 0:
        raise ValueError("Precommitted L1 source code fence is not closed")
    payload = after[:end].strip()
    try:
        value = yaml.safe_load(payload)
    except yaml.YAMLError as exc:
        raise ValueError(f"Precommitted L1 source is invalid YAML: {exc}") from exc
    errors = validate_source(value, "github-child-contract-source")
    if errors:
        raise ValueError("; ".join(errors))
    return value

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def canonical_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def manifest_digest(manifest: dict[str, Any]) -> str:
    payload=dict(manifest); payload.pop("manifest_digest",None); return canonical_digest(payload)

def _safe_repo_path(path:str)->bool:
    if not path or path.startswith("/") or "\\" in path: return False
    normalized=posixpath.normpath(path)
    return normalized==path and normalized not in {".",".."} and all(p not in {"",".",".."} for p in path.split("/"))

def source_semantic_errors(source:dict[str,Any])->list[str]:
    errors=[]
    ids=[r["id"] for r in source["selectors"]]
    d=sorted({x for x in ids if ids.count(x)>1})
    if d: errors.append("selector ids must be globally unique: "+", ".join(d))
    req=[r["evidence_requirement"]["id"] for r in source["selectors"]]
    d=sorted({x for x in req if req.count(x)>1})
    if d: errors.append("evidence requirement ids must be globally unique: "+", ".join(d))
    for r in source["selectors"]:
        if not _safe_repo_path(r["path"]): errors.append(f"{r['id']}: unsafe repository path")
        if not r["pointer"].startswith("/"): errors.append(f"{r['id']}: pointer must be an absolute JSON pointer")
    return errors

def validate_source(source:Any,label="l1-baseline-source")->list[str]:
    errors=schema_validate("l1-baseline-source",source,label)
    if errors:return errors
    return [f"{label}: {e}" for e in source_semantic_errors(source)]

def manifest_semantic_errors(manifest:dict[str,Any])->list[str]:
    errors=[]
    if manifest["manifest_digest"]!=manifest_digest(manifest): errors.append("manifest_digest does not match canonical manifest content")
    ids=[r["id"] for r in manifest["obligations"]]
    if len(ids)!=len(set(ids)): errors.append("manifest obligation ids must be globally unique")
    req=[r["evidence_required"]["id"] for r in manifest["obligations"]]
    if len(req)!=len(set(req)): errors.append("manifest evidence requirement ids must be globally unique")
    for r in manifest["obligations"]:
        if r["evidence_required"]["independence"]!="BASELINE_DERIVED": errors.append(f"{r['id']}: L1 evidence requirement must be BASELINE_DERIVED")
        if r["baseline_observation"]["value_digest"]!=canonical_digest(r["baseline_observation"]["value"]): errors.append(f"{r['id']}: baseline value digest mismatch")
    return errors

def _validate_manifest_semantics(manifest:Any,label="l1-baseline-obligation-manifest")->list[str]:
    errors=schema_validate("l1-baseline-obligation-manifest",manifest,label)
    if errors:return errors
    return [f"{label}: {e}" for e in manifest_semantic_errors(manifest)]

def _git(repo_root:Path,*args:str)->str:
    p=subprocess.run(["git","-C",str(repo_root),*args],capture_output=True,text=True)
    if p.returncode!=0: raise ValueError(p.stderr.strip() or p.stdout.strip() or "git command failed")
    return p.stdout

def _assert_exact_commit(repo_root:Path,sha:str)->None:
    resolved=_git(repo_root,"rev-parse",f"{sha}^{{commit}}").strip()
    if resolved!=sha: raise ValueError(f"declared base SHA resolved to {resolved}, expected {sha}")

def _read_base_yaml(repo_root:Path,sha:str,path:str)->Any:
    if not _safe_repo_path(path): raise ValueError(f"unsafe repository path: {path}")
    raw=_git(repo_root,"show",f"{sha}:{path}")
    try: value=yaml.safe_load(raw)
    except yaml.YAMLError as exc: raise ValueError(f"{path}: baseline content is not valid YAML: {exc}") from exc
    if value is None: raise ValueError(f"{path}: baseline YAML is empty")
    return value

def _decode_pointer_token(token:str)->str:
    out=""; i=0
    while i<len(token):
        if token[i]!="~": out+=token[i]; i+=1; continue
        if i+1>=len(token) or token[i+1] not in {"0","1"}: raise ValueError(f"invalid JSON pointer escape in token: {token}")
        out += "~" if token[i+1]=="0" else "/"; i+=2
    return out

def resolve_pointer(value:Any,pointer:str)->Any:
    if pointer=="": return value
    if not pointer.startswith("/"): raise ValueError("JSON pointer must start with '/'")
    current=value
    for raw in pointer[1:].split("/"):
        token=_decode_pointer_token(raw)
        if isinstance(current,dict):
            if token not in current: raise ValueError(f"JSON pointer token not found: {token}")
            current=current[token]
        elif isinstance(current,list):
            if not token.isdigit(): raise ValueError(f"JSON pointer list token is not an index: {token}")
            idx=int(token)
            if idx>=len(current): raise ValueError(f"JSON pointer list index out of range: {token}")
            current=current[idx]
        else: raise ValueError(f"JSON pointer traverses scalar at token: {token}")
    return current

def compile_source(source:dict[str,Any],repo_root:Path)->dict[str,Any]:
    errors=validate_source(source)
    if errors: raise ValueError("; ".join(errors))
    base_sha=source["base"]["sha"]; _assert_exact_commit(repo_root,base_sha)
    obligations=[]
    for s in source["selectors"]:
        doc=_read_base_yaml(repo_root,base_sha,s["path"]); value=resolve_pointer(doc,s["pointer"])
        source_ref=f"git:{base_sha}:{s['path']}#{s['pointer']}"
        oracle=f"git-baseline://{base_sha}/{s['path']}#{s['pointer']}"
        noun={"PRESERVATION":"baseline value","COMPATIBILITY":"baseline compatibility value","AUTHORITY":"baseline authority value"}[s["preservation_kind"]]
        obligations.append({
          "id":s["id"],"severity":s["severity"],
          "claim":{"type":KIND_TO_CLAIM[s["preservation_kind"]],"statement":f"Preserve the {noun} selected from {s['path']}#{s['pointer']} at the declared base.","subject_refs":[s["path"]]},
          "expected_observation":"A later acceptance candidate retains the selected baseline value or carries an explicit governed disposition before this preservation obligation can be treated as satisfied.",
          "plausible_green_but_wrong":"Candidate-focused tests remain green while the selected baseline contract changes and no explicit preservation disposition exists.",
          "oracle_refs":[oracle],
          "evidence_required":{"id":s["evidence_requirement"]["id"],"method":s["evidence_requirement"]["method"],"independence":"BASELINE_DERIVED","oracle_ref":oracle},
          "source_refs":[source_ref],
          "baseline_observation":{"path":s["path"],"pointer":s["pointer"],"value":value,"value_digest":canonical_digest(value)}
        })
    out={"schema_version":"L1_BASELINE_OBLIGATION_MANIFEST_V1","authority":"BASELINE_DERIVED_EXPECTATIONS","identity":dict(source["identity"]),
         "source":{"kind":"BASELINE_SELECTION_CONTRACT","digest":canonical_digest(source)},
         "baseline":{"ref":source["base"]["ref"],"sha":base_sha},
         "freeze":{"state":"FROZEN","basis":"EXACT_GIT_BASE","freeze_ref":f"git:{base_sha}"},
         "obligations":obligations,"forbidden_outcomes":list(source["forbidden_outcomes"]),"non_goals":list(source["non_goals"]),
         "authority_boundaries":{"consumes_candidate_state":False,"consumes_candidate_diff":False,"consumes_implementation_evidence":False,"consumes_coder_rationale":False,"consumes_reviewer_verdict":False,"emits_engineering_pass":False,"performs_lifecycle_advance":False,"grants_merge_authority":False,"grants_production_cutover":False}}
    out["manifest_digest"]=manifest_digest(out)
    errors=_validate_manifest_semantics(out)
    if errors: raise ValueError("; ".join(errors))
    return out

def validate_manifest(
    manifest:Any,
    source:Any|None=None,
    repo_root:Path|None=None,
    label="l1-baseline-obligation-manifest",
)->list[str]:
    errors=_validate_manifest_semantics(manifest,label)
    if errors:return errors
    if source is None or repo_root is None:
        return [f"{label}: source-bound exact-base replay is required"]
    source_errors=validate_source(source,"l1-source")
    if source_errors:return source_errors
    if manifest["source"]["digest"]!=canonical_digest(source):
        return [f"{label}: source.digest does not match supplied source"]
    try:
        fresh=compile_source(source,repo_root)
    except Exception as exc:
        return [f"{label}: exact-base replay failed: {exc}"]
    if fresh!=manifest:
        errors.append(f"{label}: stored content does not equal fresh exact-base replay")
    return errors

def validate_stored(source:dict[str,Any],manifest:dict[str,Any],repo_root:Path)->list[str]:
    return validate_manifest(manifest,source,repo_root,"manifest")

def main()->None:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    c=sub.add_parser("compile"); c.add_argument("source"); c.add_argument("--repo-root",default="."); c.add_argument("--output")
    v=sub.add_parser("validate"); v.add_argument("source"); v.add_argument("manifest"); v.add_argument("--repo-root",default=".")
    a=p.parse_args(); source=load_yaml(Path(a.source)); root=Path(a.repo_root).resolve()
    if a.command=="compile":
        m=compile_source(source,root); rendered=dump_yaml(m)
        if a.output: Path(a.output).write_text(rendered,encoding="utf-8")
        else: print(rendered,end="")
    else:
        m=load_yaml(Path(a.manifest)); errors=validate_manifest(m,source,root,Path(a.manifest).name)
        if errors:
            for e in errors: print(e)
            raise SystemExit(1)
        print(f"OK: L1 exact-base replay: {a.source} + {a.manifest}")
if __name__=="__main__": main()
