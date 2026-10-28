#!/usr/bin/env python3
"""Read-only GitHub issue comment observations; never certify workflow completion."""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "workflow-progress-monitor/v1"
DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "workflows.json"


def fetch(url, token):
    headers = {"Accept":"application/vnd.github+json",
               "User-Agent":"universal-workflow-progress/1.1",
               "X-GitHub-Api-Version":"2022-11-28"}
    if token:
        headers["Authorization"] = "Bearer " + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def read_comments(repository, number, token):
    path = "/".join(urllib.parse.quote(piece, safe="") for piece in repository.split("/"))
    records = []
    for page in range(1, 51):
        url = f"https://api.github.com/repos/{path}/issues/{number}/comments?per_page=100&page={page}"
        chunk = fetch(url, token)
        if not isinstance(chunk, list):
            raise ValueError("Invalid GitHub response")
        records.extend(chunk)
        if len(chunk) < 100:
            return records
    raise RuntimeError("Exceeded 5000 comments: refusing partial observation")


def validate(config):
    if config.get("schema") != SCHEMA or not isinstance(config.get("workflows"), list):
        raise ValueError("Wrong configuration schema")
    workflow_ids = set()
    for wf in config["workflows"]:
        wid = wf.get("id")
        if not isinstance(wid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", wid) or wid in workflow_ids:
            raise ValueError("Invalid or duplicate workflow id")
        workflow_ids.add(wid)
        if type(wf.get("enabled")) is not bool:
            raise ValueError("enabled must be boolean")
        if not isinstance(wf.get("repository"), str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", wf["repository"]):
            raise ValueError("Invalid repository")
        if type(wf.get("issue")) is not int or wf["issue"] < 1:
            raise ValueError("Invalid issue number")
        stages = wf.get("stages")
        if not isinstance(stages, list) or not stages:
            raise ValueError("No stages")
        stage_ids = set()
        for stage in stages:
            sid = stage.get("id")
            if not isinstance(sid, str) or not sid or sid in stage_ids:
                raise ValueError("Invalid or duplicate stage")
            stage_ids.add(sid)
            if not isinstance(stage.get("title"), str) or not stage["title"].strip():
                raise ValueError("Missing stage title")
            markers = stage.get("evidence_markers")
            if not isinstance(markers, list) or not markers or any(not isinstance(m,str) or len(m)<5 for m in markers):
                raise ValueError("Invalid stage evidence markers")
            authors = stage.get("trusted_authors")
            if not isinstance(authors, list) or any(not isinstance(x,str) or not x for x in authors):
                raise ValueError("Invalid trusted author list")
            if wf["enabled"] and not authors:
                raise ValueError("Enabled stage requires nonempty trusted author allowlist")


def snapshot(wf, comments, stamp):
    output = {"id":wf["id"],"repository":wf["repository"],"issue":wf["issue"],
              "observed_at":stamp,"scope":"comment observation only; no execution/acceptance assertion","stages":[]}
    for stage in wf["stages"]:
        authors = set(stage["trusted_authors"])
        matches = []
        for comment in comments:
            author = (comment.get("user") or {}).get("login")
            if author not in authors:
                continue
            body = comment.get("body") or ""
            if any(token in body for token in stage["evidence_markers"]):
                matches.append({"comment_id":comment.get("id"),"source_ref":comment.get("html_url"),
                                "author":author,"sha256":hashlib.sha256(body.encode("utf-8")).hexdigest()})
        matches.sort(key=lambda e:(str(e["comment_id"]),e["sha256"]))
        output["stages"].append({"id":stage["id"],"title":stage["title"],
                                 "state":"SUBMITTED" if matches else "UNKNOWN",
                                 "verification":"UNVERIFIED" if matches else "UNKNOWN",
                                 "evidence":matches})
    return output


def identity(wf):
    return {s["id"]:(s["state"],[(e["comment_id"],e["sha256"]) for e in s["evidence"]]) for s in wf["stages"]}


def compare(previous, current):
    if previous is None:
        return []
    old = {w["id"]:w for w in previous.get("workflows",[])}
    changes = []
    for wf in current["workflows"]:
        if wf["id"] not in old:
            continue
        before = identity(old[wf["id"]])
        after = identity(wf)
        for stage in wf["stages"]:
            if before.get(stage["id"]) != after[stage["id"]]:
                changes.append({"workflow":wf["id"],"stage":stage["id"],
                                "state":stage["state"],"verification":stage["verification"],
                                "issue_url":f"https://github.com/{wf['repository']}/issues/{wf['issue']}",
                                "evidence_refs":[e["source_ref"] for e in stage["evidence"] if e["source_ref"]]})
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",type=Path,default=DEFAULT_CONFIG)
    parser.add_argument("--previous",type=Path,default=Path(".state/previous.json"))
    parser.add_argument("--output",type=Path,default=Path(".state/latest.json"))
    parser.add_argument("--changes",type=Path,default=Path(".state/changes.json"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    validate(config)
    token = os.getenv("WF_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN","")
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    current = {"schema":SCHEMA,"observed_at":stamp,"workflows":[]}
    for wf in config["workflows"]:
        if wf["enabled"]:
            current["workflows"].append(snapshot(wf,read_comments(wf["repository"],wf["issue"],token),stamp))
    previous = json.loads(args.previous.read_text(encoding="utf-8")) if args.previous.exists() else None
    if previous is not None and previous.get("schema") != SCHEMA:
        raise ValueError("Invalid previous snapshot")
    changes = compare(previous,current)
    for path, data in ((args.output,current),(args.changes,{"schema":SCHEMA,"changes":changes})):
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Observed {len(current['workflows'])} workflow(s); {len(changes)} changed stage(s)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"OBSERVATION_FAILED: {exc}",file=sys.stderr)
        sys.exit(2)
