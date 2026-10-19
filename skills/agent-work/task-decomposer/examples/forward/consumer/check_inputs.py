"""Finite sender checks of the exact issued inputs; no application execution."""
import hashlib
import json
import platform
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parent / "single"
NAMES = ("task-design.md", "task-map.json", "owner.md", "guard.js", "events.json", "analysis-checks.json")
RAW = {name: (UPSTREAM / name).read_bytes() for name in NAMES}
RAW["consumer/owner.md"] = (HERE / "owner.md").read_bytes()
HASHES = {name: hashlib.sha256(value).hexdigest() for name, value in RAW.items()}
TEXT = {name: value.decode("utf-8", errors="strict") for name, value in RAW.items()}


def strict_json(text):
    def pairs(rows):
        result = {}
        for key, value in rows:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


task_map = strict_json(TEXT["task-map.json"])
events = strict_json(TEXT["events.json"])
prior = strict_json(TEXT["analysis-checks.json"])
checks = []


def check(name, condition, witness):
    checks.append({"name": name, "result": "PASS" if condition else "FAIL", "witness": witness})


canonical_map = json.dumps(task_map, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
map_digest = hashlib.sha256(canonical_map).hexdigest()
declared_map_digest = re.search(r"Canonical map SHA-256: ([0-9a-f]{64})", TEXT["task-design.md"]).group(1)
check("issued_map_identity_and_canonical_binding",
      task_map["id"] == "MAP-SINGLE-SOURCE-IDENTITY" and task_map["revision"] == 1
      and task_map["focus"] == ["T-INVESTIGATE"]
      and task_map["tasks"][0]["id"] == "T-INVESTIGATE"
      and map_digest == declared_map_digest,
      {"map_id": task_map["id"], "revision": task_map["revision"],
       "task_id": task_map["tasks"][0]["id"], "canonical_sha256": map_digest,
       "declared_canonical_sha256": declared_map_digest})

pin_rows = []
for source in task_map["sources"]:
    name = {"S-OWNER": "owner.md", "S-GUARD": "guard.js", "S-EVENTS": "events.json",
            "S-ANALYSIS": "analysis-checks.json"}[source["id"]]
    pin_rows.append({"source_id": source["id"], "file": name,
                     "actual_sha256": HASHES[name], "declared_revision": source["revision"],
                     "locator_matches_exact_allowed_file": source["locator"] == str(UPSTREAM / name),
                     "sha256_matches": source["revision"] == "sha256:" + HASHES[name]})
check("upstream_source_pins_match_actual_bytes",
      all(row["sha256_matches"] and row["locator_matches_exact_allowed_file"] for row in pin_rows), pin_rows)
check("upstream_receipt_raw_input_hashes_match",
      all(prior["source_file_sha256"][name] == HASHES[name] for name in ("owner.md", "guard.js", "events.json")),
      {name: {"actual": HASHES[name], "receipt": prior["source_file_sha256"][name]}
       for name in ("owner.md", "guard.js", "events.json")})

literal_guard = "export function mayDisplay(selected, completed) {\n  return selected.revision === completed.revision;\n}\n"
check("unchanged_literal_guard_recognized", TEXT["guard.js"] == literal_guard,
      {"guard_expression": "selected.revision === completed.revision",
       "interpretation": "Python equality only for the finite integer revisions below; no JS execution"})
expected_events = [
    {"step": 1, "action": "select", "source": "ALPHA", "revision": 11},
    {"step": 2, "action": "start", "source": "ALPHA", "revision": 11},
    {"step": 3, "action": "select", "source": "BETA", "revision": 11},
    {"step": 4, "action": "complete", "source": "ALPHA", "revision": 11},
    {"step": 5, "action": "display", "source": "ALPHA", "revision": 11},
]
check("exact_original_event_order_and_synthetic_limit", events["events"] == expected_events
      and events["kind"] == "synthetic supplied event record"
      and events["limits"] == "No production application or browser execution is represented.",
      {"events": events["events"], "kind": events["kind"], "limits": events["limits"]})

trace = []
selected = started = completed = displayed = None
for event in events["events"]:
    identity = {"source": event["source"], "revision": event["revision"]}
    if event["action"] == "select":
        selected = identity
    elif event["action"] == "start":
        started = identity
    elif event["action"] == "complete":
        completed = identity
    elif event["action"] == "display":
        displayed = identity
    trace.append({"step": event["step"], "action": event["action"], "selected": selected,
                  "started": started, "completed": completed, "displayed": displayed})


def evaluate(case_id, selected_value, completed_value, basis):
    for value in (selected_value, completed_value):
        if type(value["revision"]) is not int:
            raise ValueError("Only the finite integer revisions are modeled")
    return {"id": case_id, "selected": selected_value, "completed": completed_value,
            "revision_only_guard_model": selected_value["revision"] == completed_value["revision"],
            "owner_source_and_revision_invariant":
                (selected_value["source"], selected_value["revision"]) ==
                (completed_value["source"], completed_value["revision"]), "basis": basis}


rows = [evaluate("original_same_revision_wrong_source", selected, completed, "Reconstructed original supplied sequence"),
        evaluate("current_source_and_revision", selected,
                 {"source": selected["source"], "revision": selected["revision"]}, "Constructed positive contrast"),
        evaluate("current_source_stale_revision", selected,
                 {"source": selected["source"], "revision": selected["revision"] - 1}, "Constructed stale-revision contrast")]
check("independently_derived_finite_state_and_contrasts",
      started == completed == displayed and selected != displayed
      and [(row["revision_only_guard_model"], row["owner_source_and_revision_invariant"]) for row in rows]
      == [(True, False), (True, True), (False, False)],
      {"state_trace": trace, "analytic_contrasts": rows})
prior_rows = prior["analytic_contrasts"]
check("derived_claims_agree_with_supplied_receipt",
      len(rows) == len(prior_rows) and all(
          all(row[key] == previous[key] for key in ("id", "selected", "completed",
                                                    "revision_only_guard_model", "owner_source_and_revision_invariant"))
          for row, previous in zip(rows, prior_rows)),
      "Compared freshly reconstructed pairs and both predicates, not copied PASS labels or expected totals.")

receipt = {
    "kind": "Actual local sender checks for a prepared downstream assignment",
    "runtime": {"python": platform.python_version(), "python_invocation": "python -B",
                "model": "UNKNOWN", "reasoning_effort": "UNKNOWN", "formal_qualification": "UNKNOWN"},
    "allowed_input_sha256": HASHES,
    "representation": "Original bytes preserved; strict UTF-8 decoding succeeded. Decodability is not encoding provenance or authority authentication.",
    "canonical_map_sha256": map_digest,
    "checks": checks,
    "state_trace": trace,
    "analytic_contrasts": rows,
    "result": "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL",
    "limits": [
        "Only the explicitly issued files and this local assignment were read for task evidence.",
        "This is a separate sender derivation by the same Designer, not independent-agent review or capability qualification.",
        "Supplied synthetic records and Python finite integer comparisons do not establish JavaScript, browser or production behavior.",
        "No product edit, repair execution, architecture selection, agent dispatch, external write or product acceptance occurred.",
        "Current-selection capture, publication path, authoritative source representation and all-ordering correctness remain unverified."
    ]
}
(HERE / "source-checks.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"result": receipt["result"], "checks": len(checks), "output": str(HERE / "source-checks.json")}))
raise SystemExit(0 if receipt["result"] == "PASS" else 1)
