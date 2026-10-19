"""Independent, offline support for declared task designs; no executor or semantic oracle."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

SCHEMA = Path(__file__).resolve().parents[1] / "schemas/task-map.schema.json"


class ContractError(ValueError):
    pass


def _pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value):
    raise ContractError(f"non-finite JSON number: {value}")


def load(path):
    with Path(path).open(encoding="utf-8", errors="strict") as stream:
        return json.load(stream, object_pairs_hook=_pairs, parse_constant=_constant)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _index(rows, label):
    result = {}
    for row in rows:
        if row["id"] in result:
            raise ContractError(f"duplicate {label} id: {row['id']}")
        result[row["id"]] = row
    return result


def _refs(values, known, label):
    missing = set(values) - set(known)
    if missing:
        raise ContractError(f"{label}: unknown refs {sorted(missing)}")


def _cycle(edges, label):
    pending = {key: set(refs) for key, refs in edges.items()}
    followers = {key: set() for key in edges}
    for key, refs in pending.items():
        for ref in refs:
            followers[ref].add(key)
    ready = [key for key, refs in pending.items() if not refs]
    done = set()
    while ready:
        key = ready.pop()
        done.add(key)
        for other in followers[key]:
            pending[other].remove(key)
            if not pending[other]:
                ready.append(other)
    if len(done) != len(edges):
        raise ContractError(f"{label} cycle at {sorted(set(edges) - done)[0]}")


def lineage(tasks, key):
    result = []
    while key is not None:
        result.append(key)
        key = tasks[key]["parent_id"]
    return result


def context_refs(value, tasks, key):
    refs = set(value["preserve_refs"])
    for task in lineage(tasks, key):
        refs.update(tasks[task]["item_refs"] + tasks[task]["decision_refs"])
    return refs


def validate(value):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise ContractError("structural check NOT_RUN: install jsonschema>=4.18,<5; prose design remains usable") from exc
    errors = sorted(Draft202012Validator(load(SCHEMA)).iter_errors(value), key=lambda e: str(list(e.absolute_path)))
    if errors:
        raise ContractError(f"schema {list(errors[0].absolute_path)}: {errors[0].message}")
    sources, items, tasks = (_index(value[k], k) for k in ("sources", "items", "tasks"))
    _refs(value["scope"]["source_refs"], sources, "scope")
    _refs(value["preserve_refs"], items, "preserve_refs")
    if any(items[r]["kind"] != "CONSTRAINT" for r in value["preserve_refs"]):
        raise ContractError("preserve_refs must name constraints")
    for item in items.values():
        _refs(item["source_refs"], sources, item["id"])
        _refs(item["blocks"], tasks, item["id"])
    for key, task in tasks.items():
        _refs([task["parent_id"]] if task["parent_id"] else [], tasks, key + " parent")
        _refs(task["depends_on"], tasks, key + " dependencies")
        _refs(task["item_refs"] + task["decision_refs"], items, key + " basis")
        if any(items[r]["kind"] not in {"UNKNOWN", "HYPOTHESIS", "PROPOSAL"} for r in task["decision_refs"]):
            raise ContractError(f"{key}: decisions must name open questions or proposals")
    _cycle({k: [t["parent_id"]] if t["parent_id"] else [] for k, t in tasks.items()}, "parent")
    _cycle({k: t["depends_on"] for k, t in tasks.items()}, "dependency")
    _cycle({k: t["depends_on"] + [c for c, row in tasks.items() if row["parent_id"] == k] for k, t in tasks.items()}, "combined hierarchy/dependency")
    for key, task in tasks.items():
        children = [t for t in tasks.values() if t["parent_id"] == key]
        if (task["detail"] == "EXPANDED") != bool(children):
            raise ContractError(f"{key}: only EXPANDED tasks have children, and they need a child")
        if task["boundary"]["choice"] == "SPLIT" and (len(children) < 2 or task["boundary"]["cut"] is None):
            raise ContractError(f"{key}: SPLIT needs children and a stated cut basis")
        for dep in task["depends_on"]:
            if dep in lineage(tasks, key) or key in lineage(tasks, dep):
                raise ContractError(f"{key}: dependency cannot be ancestor or descendant {dep}")
    required = {k for k, row in items.items() if row["kind"] in {"REQUIREMENT", "CONSTRAINT", "UNKNOWN"}}
    coverage = {}
    for row in value["coverage"]:
        key = row["item_ref"]
        if key not in required or key in coverage:
            raise ContractError(f"coverage must name each obligation/unknown exactly once: {key}")
        _refs(row["task_refs"], tasks, key + " coverage")
        _refs(row["source_refs"], sources, key + " evidence")
        if row["disposition"] == "PLANNED" and not row["task_refs"]:
            raise ContractError(f"{key}: PLANNED needs a task")
        if any(key not in context_refs(value, tasks, t) for t in row["task_refs"]):
            raise ContractError(f"{key}: coverage task must retain its basis item")
        if row["disposition"] == "EVIDENCE_REPORTED" and (not row["source_refs"] or items[key]["kind"] == "UNKNOWN"):
            raise ContractError(f"{key}: evidence needs a source and cannot resolve an unchanged UNKNOWN")
        coverage[key] = row
    if set(coverage) != required:
        raise ContractError(f"coverage missing {sorted(required - set(coverage))}")
    _refs(value["focus"], tasks, "focus")
    if any(tasks[t]["detail"] != "BOUNDED" for t in value["focus"]):
        raise ContractError("focus must name BOUNDED task designs")
    return {"sources": sources, "items": items, "tasks": tasks, "coverage": coverage}


def affected(tasks, initial):
    found = set(initial)
    while True:
        more = found | {k for k, t in tasks.items() if t["parent_id"] in found or set(t["depends_on"]) & found}
        if more == found:
            return found
        found = more


def blockers(value, idx):
    result = {key: [] for key in idx["tasks"]}
    for key, item in idx["items"].items():
        if item["kind"] == "UNKNOWN" and idx["coverage"][key]["disposition"] != "SUPERSEDED":
            for task in affected(idx["tasks"], item["blocks"]):
                result[task].append(key)
    return result


def frontier(value):
    idx = validate(value)
    blocked, rows = blockers(value, idx), []
    for task in value["tasks"]:
        if task["detail"] != "BOUNDED":
            continue
        key = task["id"]
        state = "DISCOVER_OR_DECIDE" if blocked[key] else "HAS_PREREQUISITES" if task["depends_on"] else "DESIGN_CANDIDATE"
        rows.append({"task": key, "state": state, "blocking_unknowns": sorted(blocked[key]), "prerequisites": task["depends_on"], "focus": key in value["focus"]})
    unallocated = [{"item": key, "disposition": row["disposition"], "statement": idx["items"][key]["statement"]} for key, row in idx["coverage"].items() if not row["task_refs"] and row["disposition"] in {"UNRESOLVED", "DEFERRED"}]
    return {"scope": "DECLARED_DESIGN_CONTEXT_ONLY", "candidates": rows, "deferred": [t["id"] for t in value["tasks"] if t["detail"] == "DEFERRED"], "unallocated": unallocated, "focus_reason": value["focus_reason"], "authority_effects": []}


def _quote(text):
    return "\n".join("> " + line for line in text.splitlines())


def render(value, task_id):
    idx = validate(value)
    if task_id not in idx["tasks"] or idx["tasks"][task_id]["detail"] != "BOUNDED":
        raise ContractError("select an existing BOUNDED task")
    task = idx["tasks"][task_id]
    blocked = blockers(value, idx)[task_id]
    refs = context_refs(value, idx["tasks"], task_id) | set(blocked)
    src = set(value["scope"]["source_refs"])
    lines = ["# Neutral task design", "", "Design data under existing authority; use a selected consumer for execution instructions.", f"Map: {value['id']} | revision: {value['revision']} | task: {task_id}", f"Canonical map SHA-256: {digest(value)}", "Digest covers sorted compact UTF-8 JSON, not authentication or acceptance."]
    def section(title, texts):
        lines.extend(["", "## " + title])
        lines.extend(_quote(t) for t in texts)
    section("Original request", [value["request"]])
    section("Purpose", [value["purpose"], task["purpose"]])
    section("Coherent deliverable", [task["deliverable"]])
    lines.extend(["", "## Source-grounded basis (quoted data)"])
    for key in sorted(refs):
        row = idx["items"][key];src.update(row["source_refs"])
        lines.extend([f"{key} — {row['kind']} — sources: {', '.join(row['source_refs']) or 'UNKNOWN'}", _quote(row["statement"])])
        if key in idx["coverage"]:
            cover = idx["coverage"][key]
            src.update(cover["source_refs"])
            lines.extend(["Declared coverage: " + cover["disposition"], _quote(cover["reason"])])
    section("Required understanding", task["understanding"])
    section("Acceptance and contrast", [k + ": " + v for k, v in task["acceptance"].items()])
    section("Scope and reserved decisions", ["Permitted: " + s for s in value["scope"]["permitted"]] + ["Forbidden: " + s for s in value["scope"]["forbidden"]] + task["limits"])
    section("Open decisions", task["decision_refs"] or ["none declared"])
    section("Prerequisites and uncertainty", [dep + ": " + idx["tasks"][dep]["deliverable"] for dep in task["depends_on"]] + ["Blocking unknown refs: " + (", ".join(sorted(blocked)) or "none declared"), "These are declared dependencies, not proof that prerequisites are satisfied."])
    section("Boundary basis", [task["boundary"]["choice"], task["boundary"]["reason"]] + [k + ": " + v for k, v in (task["boundary"]["cut"] or {}).items()])
    lines.extend(["", "## Sources"])
    for ref in sorted(src):
        row = idx["sources"][ref]
        lines.extend([f"{ref}: {row['kind']} / {row['assessment']}", _quote(row["locator"]), "Revision: " + (row["revision"] or "UNKNOWN")])
    section("Performer context", [value["performer_context"]["description"], "Basis: " + value["performer_context"]["basis"]] + value["performer_context"]["limitations"])
    section("Continuation", ["Preserve this issued binding and native evidence. Return discoveries or unresolved judgment to the planner. Refinements must visibly preserve or propose changes to original conditions. No completion, authority or product acceptance is inferred."])
    return "\n".join(lines) + "\n"


def impact(before, after):
    old, new = validate(before), validate(after)
    if before["id"] != after["id"] or after["revision"] <= before["revision"]:
        raise ContractError("impact requires the same map id and a later revision")
    def changed(a, b):
        return {k for k in set(a) | set(b) if a.get(k) != b.get(k)}
    ci = changed(old["items"], new["items"]) | changed(old["coverage"], new["coverage"])
    cs = changed(old["sources"], new["sources"])
    for idx in (old, new):
        ci |= {k for k, i in idx["items"].items() if set(i["source_refs"] + idx["coverage"].get(k, {}).get("source_refs", [])) & cs}
    seeds = changed(old["tasks"], new["tasks"])
    global_change = any(before[k] != after[k] for k in ("request", "purpose", "scale", "performer_context", "scope", "preserve_refs"))
    review, ancestors = set(), set()
    for value, idx in ((before, old), (after, new)):
        selected = set(idx["tasks"]) if global_change else seeds & set(idx["tasks"])
        selected |= {k for k in idx["tasks"] if context_refs(value, idx["tasks"], k) & ci}
        for key in ci:
            selected.update(idx["items"].get(key, {}).get("blocks", []))
        reached = affected(idx["tasks"], selected);review |= reached
        for key in reached:
            ancestors.update(lineage(idx["tasks"], key)[1:])
    return {"scope": "DECLARED_REVIEW_CANDIDATES_ONLY", "changed_items": sorted(ci), "changed_sources": sorted(cs), "review_tasks": sorted(review), "integration_ancestors": sorted(ancestors - review), "unchanged_candidates": sorted(set(new["tasks"]) - review - ancestors), "removed_obligations": sorted(k for k in set(old["items"]) - set(new["items"]) if old["items"][k]["kind"] in {"REQUIREMENT", "CONSTRAINT", "UNKNOWN"}), "authority_effects": []}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "frontier", "render"):
        cmd = sub.add_parser(name);cmd.add_argument("--map", required=True);cmd.add_argument("--out")
        if name == "render":
            cmd.add_argument("--task", required=True)
    cmd = sub.add_parser("impact");cmd.add_argument("--before", required=True);cmd.add_argument("--after", required=True);cmd.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        inputs = [args.before, args.after] if args.command == "impact" else [args.map]
        if args.out and Path(args.out).resolve() in {Path(p).resolve() for p in inputs}:
            raise ContractError("output cannot overwrite an input")
        if args.command == "impact":
            result = impact(load(args.before), load(args.after))
        else:
            value = load(args.map)
            if args.command == "validate":
                validate(value);result = {"valid": True, "scope": "DECLARED_STRUCTURE_ONLY", "map_sha256": digest(value)}
            elif args.command == "frontier":
                result = frontier(value)
            else:
                result = render(value, args.task)
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            with Path(args.out).open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
        else:
            print(text, end="")
        return 0
    except (ContractError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr);return 2


if __name__ == "__main__":
    raise SystemExit(main())
