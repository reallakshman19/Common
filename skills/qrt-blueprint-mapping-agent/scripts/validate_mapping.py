#!/usr/bin/env python3
"""Structural preflight for QRT blueprint-mapping records.

Does not inspect mathematics, learner cognition, academic expertise,
actual GitHub authorization, genuine reviewer signatures or golden rights.
Never emits a QRT/Owner acceptance decision.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

DEMANDS = {"RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY"}
BANDS = {"D1", "D2", "D3", "D4"}
COMPONENTS = {
    "concept_model_selection", "representation_translation",
    "reasoning_chain_length", "algebra_computational_load",
    "trap_exception_sensitivity"
}
ASKS = {"H1", "H2", "H3", "S1", "S2", "S3", "P1", "P2", "P3", "M1", "M2", "M3"}
ROLES = {"CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"}
SHA40 = re.compile(r"^[a-f0-9]{40}$")
SHA64 = re.compile(r"^[a-f0-9]{64}$")


def validate(data: dict) -> list[str]:
    """Return actionable structural problems; an empty list is NOT approval."""
    bad = []

    def err(key, description):
        bad.append(f"{key}: {description}")

    if not isinstance(data, dict):
        return ["root: expected JSON object"]
    if data.get("schema") != "qrt-blueprint-mapping/v1":
        err("schema", "unknown or missing schema")
    if data.get("record_status") not in {
        "DRAFT_UNREVIEWED", "PENDING_REVIEW", "BLOCKED", "REVIEWED_UNSIGNED",
        "REVIEWED_SIGNED", "OWNER_DECIDED"
    }:
        err("record_status", "must be a declared draft/review/decision state")
    for key in ("task", "source", "math", "qrt", "roles", "golden",
                "browser", "ci", "academic", "owner", "evidence_refs", "limitations"):
        if key not in data:
            err(key, "missing top-level field")
    if bad:
        return bad

    task, source, qrt, golden = (data["task"], data["source"], data["qrt"], data["golden"])
    academic, owner = data["academic"], data["owner"]
    if any(not isinstance(x, dict) for x in (task, source, qrt, golden, academic, owner)):
        return ["root: task/source/qrt/golden/academic/owner must be objects"]
    if not isinstance(data["roles"], list):
        err("roles", "must be an array")
        return bad

    for key in ("head_sha", "base_sha"):
        v = task.get(key)
        if v is not None and not (isinstance(v, str) and SHA40.fullmatch(v)):
            err(f"task.{key}", "must be a full 40-char git SHA or null")
    if task.get("mode") not in {"ANALYZE_ONLY", "DRAFT_TEST_BUILD", "REVIEW_ONLY"}:
        err("task.mode", "unknown execution mode")
    if source.get("kind") not in {"AUTHORED_TEST", "ORIGINAL_VERIFIED", "SOURCE_UNVERIFIED"}:
        err("source.kind", "declare test, original verified, or unverified")
    for key in ("source_git_blob",):
        v = source.get(key)
        if v is not None and not (isinstance(v, str) and SHA40.fullmatch(v)):
            err(f"source.{key}", "must be full 40-char git blob or null")
    v = source.get("source_sha256")
    if v is not None and not (isinstance(v, str) and SHA64.fullmatch(v)):
        err("source.source_sha256", "must be 64-char SHA256 or null")
    if source.get("kind") != "ORIGINAL_VERIFIED" and source.get("real_source_admitted"):
        err("source.real_source_admitted", "official source cannot be admitted from an unverified/test record")
    if source.get("kind") == "AUTHORED_TEST" and source.get("source_rights") != "WHOLLY_AUTHORED_TEST_ONLY":
        err("source.source_rights", "authored TEST cannot claim original/publication rights")
    if source.get("kind") == "SOURCE_UNVERIFIED" and source.get("verified_exact_text"):
        err("source.verified_exact_text", "cannot assert source verification when source is unverified")

    if qrt.get("primary_demand") is not None and qrt["primary_demand"] not in DEMANDS:
        err("qrt.primary_demand", "unknown cognitive demand")
    if qrt.get("alternative_demand") is not None and qrt["alternative_demand"] not in DEMANDS:
        err("qrt.alternative_demand", "unknown competing cognitive demand")
    if qrt.get("band") is not None and qrt["band"] not in BANDS:
        err("qrt.band", "not D1..D4")
    difficulty = qrt.get("difficulty_components")
    if not isinstance(difficulty, dict) or set(difficulty) != COMPONENTS:
        err("qrt.difficulty_components", "must have exactly the five canonical components")
    else:
        for name, value in difficulty.items():
            if not isinstance(value, dict):
                err("qrt.difficulty_components." + name, "expected score/evidence object")
                continue
            score = value.get("score")
            if score is not None and (type(score) is not int or score not in (0, 1, 2)):
                err("qrt.difficulty_components." + name, "only null/0/1/2 allowed")
            if score is not None and not value.get("evidence"):
                err("qrt.difficulty_components." + name, "scored components need concrete evidence")
    if qrt.get("y_evidence") == "DEMONSTRATED" and (
        not qrt.get("y") or not qrt.get("y_proof_ref")
    ):
        err("qrt.y_evidence", "cannot claim learner demonstration without Y and a proof ref")

    asks = qrt.get("asks")
    if not isinstance(asks, dict) or set(asks) != ASKS:
        err("qrt.asks", "must contain H1-H3, S1-S3, P1-P3, M1-M3, no omissions")
    else:
        for name, row in asks.items():
            if not isinstance(row, dict):
                err("qrt.asks." + name, "must be object")
                continue
            verdict = row.get("verdict")
            if verdict not in {"PENDING", "YES", "PARTLY", "NO", "NOT_APPLICABLE"}:
                err("qrt.asks." + name, "unknown verdict")
            elif verdict != "PENDING" and not all(
                row.get(field) for field in ("reviewer_id", "reason", "evidence_ref")
            ):
                err("qrt.asks." + name, "signed judgement requires reviewer, reason, actual evidence")

    seen = set()
    for i, row in enumerate(data["roles"]):
        if not isinstance(row, dict):
            err(f"roles[{i}]", "must be object")
            continue
        name = row.get("role")
        if name not in ROLES:
            err(f"roles[{i}]", "unknown Core role")
        elif name in seen:
            err(f"roles[{i}]", "duplicate Core role")
        else:
            seen.add(name)
        if row.get("native_html_sha256") is not None:
            if not isinstance(row["native_html_sha256"], str) or not SHA64.fullmatch(row["native_html_sha256"]):
                err(f"roles[{i}].native_html_sha256", "need actual 64-char page SHA256")
            if not row.get("registered_blueprint") or not row.get("render_receipt_ref"):
                err(f"roles[{i}]", "rendered role requires blueprint ref and renderer receipt")
    if "CORE2" in seen and source.get("kind") != "ORIGINAL_VERIFIED":
        err("roles.CORE2", "no authentic Core2 from wholly-authored or unverified source")
    if "CORE2" in seen and not source.get("real_source_admitted"):
        err("roles.CORE2", "verified source alone does not admit original rights")
    if task.get("mode") == "DRAFT_TEST_BUILD" and not seen:
        err("roles", "building native pages requires selected roles")

    if golden.get("comparison_mode") not in {
        "CROSS_QUESTION_TECHNIQUE", "SAME_QUESTION_EXACT", "NO_VALID_COMPARATOR"
    }:
        err("golden.comparison_mode", "must choose explicit comparator kind")
    if golden.get("comparison_mode") == "SAME_QUESTION_EXACT" and golden.get("same_question_as_fixture") is not True:
        err("golden.comparison_mode", "byte exact comparison requires genuinely same source")
    if golden.get("comparison_mode") == "CROSS_QUESTION_TECHNIQUE" and golden.get("same_question_as_fixture") is True:
        err("golden.comparison_mode", "same-question fixture should use exact condition comparator when eligible")
    if golden.get("new_golden_designation") not in {"NOT_AUTHORIZED", "OWNER_AUTHORIZED"}:
        err("golden.new_golden_designation", "no implicit golden status")

    if academic.get("status") not in {"PENDING_INDEPENDENT", "REVISE", "RECLASSIFY", "REJECT", "ACCEPT_SIGNED"}:
        err("academic.status", "must be explicit pending or signed academic disposition")
    signed = academic.get("status") in {"REVISE", "RECLASSIFY", "REJECT", "ACCEPT_SIGNED"}
    if signed:
        required = ("reviewer_identity", "qualifications", "conflict_declaration",
                    "reviewed_on", "signature_ref")
        if not all(academic.get(k) for k in required) or academic.get("independent_of_author") is not True:
            err("academic", "signed review requires independently verified identity, expertise, COI, date, signature")
        if not isinstance(asks, dict) or any(asks.get(a, {}).get("verdict") == "PENDING" for a in ASKS):
            err("academic", "signed academic outcome requires all twelve judgements")
    if owner.get("status") not in {"PENDING", "ACCEPT", "REVISE", "REJECT"}:
        err("owner.status", "unknown Owner decision")
    if owner.get("status") != "PENDING":
        if not owner.get("decision_id") or not owner.get("decision_date"):
            err("owner", "Owner decision needs its own dated decision ID")
        if not signed:
            err("owner", "do not infer Owner decision from unsigned academic review")
    if any(owner.get(k) for k in ("release_authorized", "merge_authorized",
                                  "successor_golden_approved")) and owner.get("status") == "PENDING":
        err("owner", "release/merge/golden authorizations must be separately evidenced")
    if data.get("record_status") == "OWNER_DECIDED" and owner.get("status") == "PENDING":
        err("record_status", "cannot claim Owner-decided without decision")

    for key in ("evidence_refs", "limitations"):
        if not isinstance(data[key], list):
            err(key, "must be array")
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("record", type=Path)
    args = ap.parse_args()
    try:
        data = json.loads(args.record.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"STRUCTURAL_PREFLIGHT_FAIL: {exc}")
        return 2
    errors = validate(data)
    for err in errors:
        print("ERROR:", err)
    if errors:
        print(f"STRUCTURAL_PREFLIGHT_FAIL ({len(errors)} problem(s)); NO ACCEPTANCE")
        return 1
    print("STRUCTURAL_PREFLIGHT_PASS; ACADEMIC/OWNER/TRUTH VERIFICATION NOT PERFORMED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
