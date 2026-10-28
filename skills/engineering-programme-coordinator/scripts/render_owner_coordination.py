#!/usr/bin/env python3
"""Render an Owner-facing coordination report from a derived observation.

This script is reporting-only. It never grants or denies production action.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from coordlib import dump_yaml, load_yaml, require_valid


def _append_unique(rows: list[str], value: str | None) -> None:
    text = str(value or "").strip()
    if text and text not in rows:
        rows.append(text)


def build_report(observation: dict[str, Any], mode: str) -> dict[str, Any]:
    require_valid("coordination-observation", observation, "COORDINATION_OBSERVATION")

    changed: list[str] = []
    cross = observation.get("cross_workstream") or {}
    semantic = observation.get("semantic_boundary") or {}

    if semantic.get("changed"):
        _append_unique(changed, f"Semantic boundary changed: {semantic.get('reason') or 'reason not supplied'}")

    for value in cross.get("newly_discovered_dependencies") or []:
        _append_unique(changed, f"New dependency: {value}")
    for value in cross.get("satisfied_dependencies") or []:
        _append_unique(changed, f"Dependency satisfied: {value}")
    for value in cross.get("conflicting_assumptions") or []:
        _append_unique(changed, f"Conflicting assumption: {value}")
    for value in cross.get("overlapping_ownership") or []:
        _append_unique(changed, f"Ownership overlap: {value}")

    workstreams = []
    local_coordination: list[str] = []
    uncertainties: list[str] = []

    for stream in observation.get("workstreams") or []:
        sid = str(stream.get("id") or "")
        expected = (stream.get("expected") or {}).get("description") or ""
        observed = (stream.get("observed") or {}).get("summary") or ""
        consequence = stream.get("consequence") or ""
        conformance = str(stream.get("plan_conformance") or "")

        workstreams.append({
            "id": sid,
            "expected": expected,
            "observed": observed,
            "consequence": consequence,
        })

        if conformance not in {"ALIGNED", "INSUFFICIENT_EVIDENCE"}:
            _append_unique(changed, f"{sid}: plan conformance is {conformance}")

        helper = stream.get("helper_recommendation") or {}
        if helper.get("recommended"):
            _append_unique(
                local_coordination,
                f"{sid}: helper recommended"
                + (f" — {helper.get('purpose')}" if helper.get("purpose") else ""),
            )

        for evidence in stream.get("evidence") or []:
            if evidence.get("promotion_required"):
                _append_unique(
                    local_coordination,
                    f"{sid}: promote local evidence {evidence.get('ref')} to shared durable evidence",
                )

        for uncertainty in stream.get("uncertainties") or []:
            _append_unique(
                uncertainties,
                f"{sid} [{uncertainty.get('kind')}]: {uncertainty.get('statement')}",
            )

        for dep in stream.get("dependencies") or []:
            state = dep.get("state")
            if state == "DISCOVERED":
                _append_unique(
                    changed,
                    f"{sid}: discovered dependency on {dep.get('required_output')}",
                )
            elif state == "SATISFIED":
                _append_unique(
                    changed,
                    f"{sid}: dependency satisfied for {dep.get('required_output')}",
                )

    for risk in (observation.get("owner") or {}).get("material_risks") or []:
        _append_unique(uncertainties, str(risk))

    if not changed:
        changed.append("No meaningful coordination change observed.")

    next_obs = observation.get("next_observation") or {}
    next_text = str(next_obs.get("reason") or "").strip()
    expected_evidence = [str(x) for x in next_obs.get("expected_evidence") or [] if str(x)]
    if expected_evidence:
        next_text = (next_text + " Watch for: " + "; ".join(expected_evidence)).strip()

    programme = observation.get("programme_context") or {}
    exit_rows = []
    for row in observation.get("exit_criteria") or []:
        exit_rows.append({
            "id": str(row.get("id") or ""),
            "status": str(row.get("status") or "OPEN"),
            "note": row.get("note"),
        })

    nonterminal_prs = [
        f"{row.get('ref')} [{row.get('workstream')}] {row.get('lifecycle')}"
        + (f" @ {row.get('head')}" if row.get("head") else "")
        for row in observation.get("nonterminal_prs") or []
    ]

    negative_knowledge = [
        str(row.get("statement") or "")
        for row in observation.get("negative_knowledge") or []
        if str(row.get("statement") or "")
    ]

    report = {
        "schema_version": "engineering-coordinator-owner-report-v1",
        "authority": "DERIVED_OWNER_COORDINATION_REPORT",
        "observed_at": observation["observed_at"],
        "reporting_mode": mode,
        "programme_context": {
            "parent_ref": programme.get("parent_ref"),
            "basis_revision": programme.get("basis_revision"),
        },
        "programme_exit": exit_rows,
        "nonterminal_prs": nonterminal_prs,
        "negative_knowledge": negative_knowledge,
        "what_changed": changed,
        "workstreams": workstreams,
        "cross_workstream": {
            "new_dependencies": list(cross.get("newly_discovered_dependencies") or []),
            "satisfied_dependencies": list(cross.get("satisfied_dependencies") or []),
            "conflicts": list(cross.get("conflicting_assumptions") or [])
            + list(cross.get("overlapping_ownership") or []),
        },
        "local_coordination": local_coordination,
        "uncertainties_risks": uncertainties,
        "needs_you": list((observation.get("owner") or {}).get("decisions_needed") or []),
        "next_observation": next_text,
        "note": "Derived coordination report only; never production authority.",
    }
    require_valid("owner-coordination-report", report, "OWNER_COORDINATION_REPORT")
    return report


def _items(values: list[str]) -> str:
    return "; ".join(values) if values else "none"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Programme Coordination — {report['observed_at']}",
        "",
        f"Reporting mode: **{report['reporting_mode']}**",
        "This report is derived coordination context, not production permission.",
        "",
        "## What changed",
    ]
    lines.extend(f"- {row}" for row in report.get("what_changed") or [])

    lines += ["", "## Workstreams"]
    for stream in report.get("workstreams") or []:
        lines += [
            f"### {stream['id']}",
            f"- Expected: {stream.get('expected') or 'none'}",
            f"- Observed: {stream.get('observed') or 'none'}",
            f"- Consequence: {stream.get('consequence') or 'none'}",
        ]

    cross = report.get("cross_workstream") or {}
    programme = report.get("programme_context") or {}
    if programme.get("parent_ref") or programme.get("basis_revision"):
        lines += [
            "",
            "## Programme basis",
            f"- Parent: {programme.get('parent_ref') or 'unknown'}",
            f"- Basis revision: {programme.get('basis_revision') or 'unknown'}",
        ]

    if report.get("programme_exit"):
        lines += ["", "## Programme exit criteria"]
        for row in report.get("programme_exit") or []:
            note = f" — {row.get('note')}" if row.get("note") else ""
            lines.append(f"- {row.get('id')}: **{row.get('status')}**{note}")

    if report.get("nonterminal_prs"):
        lines += [
            "",
            "## Nonterminal PRs",
            f"- {_items(report.get('nonterminal_prs') or [])}",
        ]

    if report.get("negative_knowledge"):
        lines += [
            "",
            "## Negative knowledge",
            f"- {_items(report.get('negative_knowledge') or [])}",
        ]

    lines += [
        "",
        "## Cross-workstream",
        f"- New dependencies: {_items(cross.get('new_dependencies') or [])}",
        f"- Satisfied dependencies: {_items(cross.get('satisfied_dependencies') or [])}",
        f"- Conflicts/overlap: {_items(cross.get('conflicts') or [])}",
        "",
        "## Local coordination",
        f"- {_items(report.get('local_coordination') or [])}",
        "",
        "## Uncertainties / risks",
        f"- {_items(report.get('uncertainties_risks') or [])}",
        "",
        "## Needs you",
        f"- {_items(report.get('needs_you') or [])}",
        "",
        "## Next observation",
        f"- {report.get('next_observation') or 'No scheduled observation is semantically necessary.'}",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render Owner coordination reporting from a disposable coordination observation."
    )
    parser.add_argument("observation", help="Path to coordination observation YAML")
    parser.add_argument(
        "--mode",
        choices=["SEMANTIC_DELTA", "CADENCED"],
        default="SEMANTIC_DELTA",
    )
    parser.add_argument("--yaml", action="store_true", help="Emit normalized report YAML instead of Markdown")
    args = parser.parse_args()

    observation = load_yaml(Path(args.observation))
    report = build_report(observation, args.mode)
    if args.yaml:
        print(dump_yaml(report), end="")
    else:
        print(render_markdown(report), end="")


if __name__ == "__main__":
    main()
