#!/usr/bin/env python3
"""ONB-RWI WP3: independent, read-only evidence-history reconstruction.

This consumes caller-supplied source references and text. A valid GitHub URL, claimed
Owner role, SHA or byte digest is never proof of real source/Owner approval.
The provenance-bearing provider collector and independent reviewer remain separate.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
EVENT_KINDS = frozenset({
    "ORIGINAL_PROBLEM", "OWNER_AMENDMENT", "DECISION", "INVESTIGATION",
    "CODE_CHANGE", "TEST_RESULT", "BENCHMARK", "REJECTED_PATH", "BLOCKER"
})
ACTORS = frozenset({"REPORTED_OWNER", "ENGINEER", "REVIEWER", "COORDINATOR", "UNKNOWN"})
VISIBILITY = frozenset({"PUBLIC", "RESTRICTED", "PRIVATE"})
CODE_ROLES = frozenset({"ENTRYPOINT", "OWNING_LAYER", "DOWNSTREAM_CONSUMER", "TEST_ORACLE"})
STATUSES = frozenset({"PASS", "FAIL", "NOT_RUN", "NOT_APPLICABLE"})
TARGET_FIELDS = frozenset({"repository", "issue", "source_heads", "candidate_heads", "observed_at"})
EVENT_FIELDS = frozenset({"id", "kind", "repository", "source_sha", "source_url",
                          "recorded_at", "actor", "summary", "visibility", "supersedes"})
CODE_FIELDS = frozenset({"id", "repository", "revision", "source_url", "path",
                         "symbol", "role", "line_start", "line_end", "line_sha256"})
RESULT_FIELDS = frozenset({"id", "repository", "candidate_sha", "source_url",
                           "command", "status", "oracle", "expected", "observed"})
BUNDLE_FIELDS = frozenset({"schema", "target", "events", "code_path", "test_results",
                           "first_verification"})


class ReconstructionError(ValueError):
    """A source claim could not be safely normalized."""


def exact(obj, keys, name):
    if not isinstance(obj, dict) or set(obj) != keys:
        raise ReconstructionError(name + ": missing or extra fields")
    return obj


def text(value, label, maxlen=5000):
    if not isinstance(value, str) or not value.strip() or len(value) > maxlen:
        raise ReconstructionError(label + " must be bounded nonempty text")
    return value


def repository(value):
    if not isinstance(value, str) or not REPO_RE.fullmatch(value):
        raise ReconstructionError("invalid repository identity")
    return value


def sha(value):
    if not isinstance(value, str) or not SHA40.fullmatch(value):
        raise ReconstructionError("invalid 40-character SHA")
    return value


def date(value):
    if not isinstance(value, str):
        raise ReconstructionError("missing timestamp")
    try:
        timestamp = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as e:
        raise ReconstructionError("invalid timestamp") from e
    if timestamp.utcoffset() is None:
        raise ReconstructionError("timestamp must specify timezone")
    return timestamp.astimezone(dt.timezone.utc)


def source_url(url, repo):
    text(url, "evidence URL", 2000)
    try:
        parsed = urlsplit(url)
    except ValueError as e:
        raise ReconstructionError("malformed source URL") from e
    parts = parsed.path.strip("/").split("/")
    if (parsed.scheme != "https" or parsed.netloc != "github.com"
            or parsed.username or parsed.password or parsed.query
            or len(parts) < 3 or "/".join(parts[:2]) != repo
            or any(part in (".", "..", "") for part in parts)
            or (parsed.fragment and not re.fullmatch(r"(?:issuecomment-[0-9]+|L[1-9][0-9]*(?:-L[1-9][0-9]*)?)", parsed.fragment))):
        raise ReconstructionError("source URL is not bound to its declared repository")
    return url


def citation(label, url):
    # All input remains untrusted textual data, and URLs are checked separately.
    return {"label": label, "url": url, "provider_verified": False}


def validate(bundle):
    b = exact(bundle, BUNDLE_FIELDS, "reconstruction bundle")
    if b["schema"] != "onboarding.reconstruction/v1":
        raise ReconstructionError("unknown reconstruction schema")
    t = exact(b["target"], TARGET_FIELDS, "target")
    root = repository(t["repository"])
    if type(t["issue"]) is not int or t["issue"] < 1:
        raise ReconstructionError("invalid parent issue")
    date(t["observed_at"])
    heads = t["source_heads"]
    if not isinstance(heads, dict) or root not in heads:
        raise ReconstructionError("missing explicit source-head inventory")
    for repo, candidate in heads.items():
        repository(repo)
        sha(candidate)
    candidate_heads = t["candidate_heads"]
    if not isinstance(candidate_heads, dict):
        raise ReconstructionError("candidate_heads must be an explicit mapping")
    for url, rev in candidate_heads.items():
        parts = urlsplit(url).path.strip("/").split("/") if isinstance(url, str) else []
        if (len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit()
                or int(parts[3]) < 1):
            raise ReconstructionError("candidate-head key must be an exact PR URL")
        rep = "/".join(parts[:2])
        if rep not in heads:
            raise ReconstructionError("candidate head outside authorized repositories")
        source_url(url, rep)
        sha(rev)

    events = b["events"]
    if not isinstance(events, list):
        raise ReconstructionError("events must be a list")
    by_id = {}
    for event in events:
        e = exact(event, EVENT_FIELDS, "event")
        key = text(e["id"], "event identity", 120)
        if key in by_id:
            raise ReconstructionError("duplicated event identity")
        by_id[key] = e
        rep = repository(e["repository"])
        if rep not in heads:
            raise ReconstructionError("cross-repository history not authorized")
        sha(e["source_sha"])
        source_url(e["source_url"], rep)
        if date(e["recorded_at"]) > date(t["observed_at"]):
            raise ReconstructionError("event recorded after source observation cut")
        text(e["summary"], "summary")
        if e["kind"] not in EVENT_KINDS or e["actor"] not in ACTORS or e["visibility"] not in VISIBILITY:
            raise ReconstructionError("unknown event classification")
        if (not isinstance(e["supersedes"], list) or
                any(not isinstance(v, str) or not v for v in e["supersedes"]) or
                len(e["supersedes"]) != len(set(e["supersedes"]))):
            raise ReconstructionError("invalid supersession IDs")
    superseded = {}
    for e in events:
        for parent in e["supersedes"]:
            if parent not in by_id or parent == e["id"]:
                raise ReconstructionError("supersession points to absent/self event")
            old = by_id[parent]
            if old["repository"] != e["repository"]:
                raise ReconstructionError("cross-repository supersession")
            if date(e["recorded_at"]) <= date(old["recorded_at"]):
                raise ReconstructionError("superseding event must be later")
            if parent in superseded:
                raise ReconstructionError("ambiguous concurrent supersession")
            superseded[parent] = e["id"]

    paths = b["code_path"]
    if not isinstance(paths, list):
        raise ReconstructionError("code_path must be an array")
    seen = set()
    for entry in paths:
        c = exact(entry, CODE_FIELDS, "code path")
        ident = text(c["id"], "code path identity", 120)
        if ident in seen:
            raise ReconstructionError("duplicate code path identity")
        seen.add(ident)
        rep = repository(c["repository"])
        if rep not in heads:
            raise ReconstructionError("foreign source code path")
        sha(c["revision"])
        source_url(c["source_url"], rep)
        if (not isinstance(c["path"], str) or not c["path"] or c["path"].startswith("/")
                or any(part in ("", ".", "..") for part in c["path"].split("/"))):
            raise ReconstructionError("path traversal or invalid source path")
        expected_blob_url = ("https://github.com/" + rep + "/blob/" + c["revision"]
                             + "/" + c["path"])
        if c["source_url"].split("#", 1)[0] != expected_blob_url:
            raise ReconstructionError("code URL is not bound to the claimed file and revision")
        text(c["symbol"], "symbol", 200)
        if c["role"] not in CODE_ROLES:
            raise ReconstructionError("invalid architecture role")
        if (type(c["line_start"]) is not int or type(c["line_end"]) is not int
                or c["line_start"] < 1 or c["line_end"] < c["line_start"]):
            raise ReconstructionError("invalid source line span")
        digest = c["line_sha256"]
        if not isinstance(digest, str) or not re.fullmatch("[0-9a-f]{64}", digest):
            raise ReconstructionError("invalid source slice digest")

    results = b["test_results"]
    if not isinstance(results, list):
        raise ReconstructionError("test_results must be a list")
    results_seen = set()
    for value in results:
        r = exact(value, RESULT_FIELDS, "test result")
        key = text(r["id"], "test id", 120)
        if key in results_seen:
            raise ReconstructionError("duplicated test receipt")
        results_seen.add(key)
        rep = repository(r["repository"])
        if rep not in heads:
            raise ReconstructionError("foreign test receipt")
        sha(r["candidate_sha"])
        source_url(r["source_url"], rep)
        text(r["command"], "test command")
        text(r["expected"], "expected")
        if r["oracle"] not in ("REPORTED_INDEPENDENT", "SYNTHETIC", "IMPLEMENTATION_COUPLED", "UNKNOWN"):
            raise ReconstructionError("unsupported oracle class")
        if r["status"] not in STATUSES:
            raise ReconstructionError("unknown test status")
        if r["status"] == "NOT_RUN" and r["observed"] is not None:
            raise ReconstructionError("NOT_RUN cannot claim observed result")
        if r["status"] in ("PASS", "FAIL") and (not isinstance(r["observed"], str) or not r["observed"].strip()):
            raise ReconstructionError("claimed execution needs observed value")
    first = b["first_verification"]
    if first is not None:
        text(first, "first verification", 2000)
    return b, by_id, superseded


def reconstruct(bundle):
    b, by_id, superseded = validate(bundle)
    target = b["target"]
    heads = target["source_heads"]
    candidates = target["candidate_heads"]
    live = {repo: {base} for repo, base in heads.items()}
    for url, candidate in candidates.items():
        rep = "/".join(urlsplit(url).path.strip("/").split("/")[:2])
        live[rep].add(candidate)
    events = sorted(by_id.values(), key=lambda e: (date(e["recorded_at"]), e["id"]))
    public = []
    for e in events:
        active = e["id"] not in superseded
        is_public = e["visibility"] == "PUBLIC"
        public.append({
            "id": e["id"], "kind": e["kind"],
            "repository": e["repository"] if is_public else "[REDACTED]",
            "recorded_at": e["recorded_at"] if is_public else None,
            "actor_claim": e["actor"] if is_public else "UNKNOWN",
            "source_sha": e["source_sha"] if is_public else None,
            "source_url": e["source_url"] if is_public else "[REDACTED_SOURCE]",
            "head_matches_current": e["source_sha"] in live[e["repository"]] if is_public else None,
            "superseded_by": superseded.get(e["id"]),
            "active": active, "visibility": e["visibility"],
            "summary": e["summary"] if is_public else "[REDACTED]",
            "provider_verified": False,
            "owner_approval_verified": False
        })
    active_ids = {e["id"] for e in public if e["active"]}
    required = [e for e in public if e["kind"] == "ORIGINAL_PROBLEM"]
    active_owner = [e for e in public if e["kind"] == "OWNER_AMENDMENT" and e["id"] in active_ids]
    failures = [r for r in b["test_results"] if r["status"] == "FAIL"]
    active_code = [c for c in b["code_path"] if c["revision"] in live[c["repository"]]]
    roles = {c["role"] for c in active_code}
    gaps = []
    if not required:
        gaps.append("ORIGINAL_PROBLEM_MISSING")
    if not active_owner:
        gaps.append("OWNER_AMENDMENT_NOT_OBSERVED")
    if not active_code:
        gaps.append("CURRENT_CODE_TRACE_MISSING")
    elif not {"ENTRYPOINT", "OWNING_LAYER", "DOWNSTREAM_CONSUMER"}.issubset(roles):
        gaps.append("CODE_PATH_INCOMPLETE")
    if not b["test_results"]:
        gaps.append("TEST_EVIDENCE_MISSING")
    if failures:
        gaps.append("FAILED_TESTS_UNRECONCILED")
    if b["first_verification"] is None:
        gaps.append("FIRST_VERIFICATION_MISSING")
    if not any(e["visibility"] == "PUBLIC" and e["kind"] in {"DECISION", "OWNER_AMENDMENT"} for e in public):
        gaps.append("OWNER_DECISION_AUTHORITY_UNVERIFIED")
    # Local snapshots are never provider-attested; they may aid investigation only.
    gaps.append("PROVIDER_READBACK_REQUIRED")
    code = [{
        "id": c["id"], "repository": c["repository"], "role": c["role"],
        "source_url": c["source_url"], "path": c["path"], "symbol": c["symbol"],
        "revision": c["revision"], "line_start": c["line_start"],
        "line_end": c["line_end"], "line_sha256": c["line_sha256"],
        "current_head": c["revision"] in live[c["repository"]],
        "line_bytes_attested_by_provider": False,
        "call_edge_verified": False,
    } for c in b["code_path"]]
    tests = [{
        "id": r["id"], "repository": r["repository"],
        "candidate_sha": r["candidate_sha"],
        "matches_current_head": r["candidate_sha"] in live[r["repository"]],
        "status_claim": r["status"], "status_provider_verified": False,
        "oracle_claim": r["oracle"], "source_url": r["source_url"],
        "command": r["command"], "expected": r["expected"],
        "observed": r["observed"]
    } for r in b["test_results"]]
    return {
        "schema": "onboarding.reconstructed-history/v1",
        "repository": target["repository"], "issue": target["issue"],
        "source_heads": heads, "candidate_heads": candidates,
        "observed_at": target["observed_at"],
        "status": "CONDITIONAL" if required else "BLOCKED",
        "reason_codes": sorted(set(gaps)),
        "timeline": public,
        "code_path": code,
        "test_results": tests,
        "first_verification": b["first_verification"] or "Locate and verify the original Owner issue",
        "rwi_disposition": "NOT_EVALUATED",
        "owner_approval_verified": False,
        "source_provider_verified": False,
        "execution_authorized": False,
        "predecessor_exit_required": False,
    }


def render_markdown(report):
    """Intermediate evidence-first summary. Not the required final 12-section handover."""
    lines = [
        "# ONB WP3 — technical reconstruction scaffold (NOT VERIFIED)",
        "",
        "Repository: " + report["repository"] + "  Issue: #" + str(report["issue"]),
        "Observed at: " + report["observed_at"],
        "Knowledge state: " + report["status"] + " | implementation authority: HELD",
        "",
        "## Original problem and Owner amendment claims",
    ]
    owners = [e for e in report["timeline"] if e["kind"] in
              ("ORIGINAL_PROBLEM", "OWNER_AMENDMENT", "DECISION")]
    for e in owners:
        lines.append("- " + e["kind"] + " " + e["id"] + ": " + e["summary"] +
                     " — " + e["source_url"] + " (PROVIDER_UNVERIFIED)" +
                     (" [SUPERSEDED]" if not e["active"] else ""))
    lines += ["", "## Investigations, rejected paths and engineering changes"]
    for e in report["timeline"]:
        if e["kind"] in ("INVESTIGATION", "REJECTED_PATH", "CODE_CHANGE", "BLOCKER"):
            lines.append("- " + e["kind"] + " " + e["id"] + ": " + e["summary"] +
                         " — " + e["source_url"] + " (CLAIM)")
    lines += ["", "## Reconstructed code-path hypotheses (NOT semantic proof)"]
    for c in report["code_path"]:
        lines.append("- " + c["role"] + ": " + c["path"] + "::" + c["symbol"] +
                     f" lines {c['line_start']}-{c['line_end']}, source " + c["source_url"] +
                     " (provider bytes and call edge unverified)")
    lines += ["", "## Test status and limitations"]
    for t in report["test_results"]:
        lines.append("- " + t["id"] + ": " + t["status_claim"] + " (CLAIM; " +
                     ("CURRENT HEAD" if t["matches_current_head"] else "HISTORICAL/STale") +
                     "), " + t["source_url"])
    lines += ["", "## Knowledge gaps / next action"]
    lines.extend("- " + reason for reason in report["reason_codes"])
    lines += ["", "First verification: " + report["first_verification"],
              "RWI: NOT_EVALUATED — no automatic implementation, approval or KEEP/IMPROVE verdict.",
              ""]
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser(description="WP3 untrusted claim-history reconstruction")
    p.add_argument("--input", required=True, help="reviewed JSON bundle of source references")
    p.add_argument("--markdown", action="store_true")
    args = p.parse_args(argv)
    try:
        report = reconstruct(json.loads(Path(args.input).read_text(encoding="utf-8")))
        print(render_markdown(report) if args.markdown else
              json.dumps(report, sort_keys=True, indent=2))
        return 0 if report["status"] == "CONDITIONAL" else 2
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({"schema": "onboarding.reconstruction-error/v1",
                          "status": "BLOCKED", "reason": str(exc),
                          "execution_authorized": False}), file=__import__("sys").stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
