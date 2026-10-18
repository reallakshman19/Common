"""Execute the original receive function against the issued synthetic orders."""

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source.py"
source_hash_before = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location("issued_receive_source", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

completions = {
    "A12": ("A", 12, "A12"),
    "B12": ("B", 12, "B12"),
    "B11": ("B", 11, "B11"),
}
payload_origins = {
    payload: {"source": source, "revision": revision}
    for source, revision, payload in completions.values()
}
orders = [("A12", "B12"), ("B12", "A12"), ("B11", "B12")]
traces = []
for order in orders:
    state = {"selected_source": "B", "current_revision": 12, "result": None}
    oracle_state = copy.deepcopy(state)
    steps = []
    for label in order:
        source, revision, payload = completions[label]
        before = copy.deepcopy(state)
        expected_before = copy.deepcopy(oracle_state)
        should_publish = (
            source == oracle_state["selected_source"]
            and revision == oracle_state["current_revision"]
        )
        # The oracle is separate from the imported function. It computes only
        # the assignment's expected result, never the actual execution path.
        if should_publish:
            oracle_state["result"] = {"source": source, "payload": payload}

        returned = module.receive(state, source, revision, payload)
        after = copy.deepcopy(state)
        result = after["result"]
        origin = payload_origins[result["payload"]] if result else None
        publication_valid = result is None or (
            result["source"] == after["selected_source"]
            and origin["source"] == after["selected_source"]
            and origin["revision"] == after["current_revision"]
        )
        steps.append({
            "completion": label,
            "input": {"source_id": source, "request_revision": revision, "payload": payload},
            "before": before,
            "after": after,
            "expected_before": expected_before,
            "expected_after": copy.deepcopy(oracle_state),
            "expected_action": "publish" if should_publish else "ignore",
            "actual_result_changed": before["result"] != after["result"],
            "returned_same_state": returned is state,
            "published_payload_origin": origin,
            "published_payload_satisfies_invariant": publication_valid,
            "actual_matches_expected": after == oracle_state,
        })
    traces.append({"order": list(order), "steps": steps})

source_hash_after = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
output = {
    "scope": "unchanged local receive function with synthetic inputs",
    "source_path": str(SOURCE),
    "source_sha256_before": source_hash_before,
    "source_sha256_after": source_hash_after,
    "source_unchanged": source_hash_before == source_hash_after,
    "bytecode_disabled": sys.dont_write_bytecode,
    "host_model": "UNKNOWN",
    "reasoning_configuration": "UNKNOWN",
    "formal_qualification": "UNKNOWN",
    "traces": traces,
}
rendered = json.dumps(output, indent=2) + "\n"
(ROOT / "output.json").write_text(rendered, encoding="utf-8")
print(rendered, end="")
