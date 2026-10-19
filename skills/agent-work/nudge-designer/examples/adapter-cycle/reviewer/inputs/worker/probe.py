"""Reproduce both completion orders by calling the unchanged supplied receive."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source.py"
SOURCE_BEFORE = SOURCE.read_bytes()
SPEC = importlib.util.spec_from_file_location("supplied_source", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

REQUESTS = {
    "OLD": {"request_revision": 9, "payload": "OLD"},
    "NEW": {"request_revision": 10, "payload": "NEW"},
}


def run_order(order):
    # Source replacement to rev10 has already happened. No result is published.
    state = {"current_revision": 10, "result": None}
    initial_state = copy.deepcopy(state)
    expected_result = None
    events = []
    for index, name in enumerate(order, start=1):
        request = REQUESTS[name]
        before = copy.deepcopy(state)
        obsolete = request["request_revision"] != state["current_revision"]
        if not obsolete:
            expected_result = request["payload"]
        returned = MODULE.receive(
            state, request["request_revision"], request["payload"]
        )
        after = copy.deepcopy(state)
        events.append({
            "completion_index": index,
            "request_name": name,
            "request_revision": request["request_revision"],
            "payload": request["payload"],
            "obsolete_at_completion": obsolete,
            "state_before": before,
            "state_after": after,
            "expected_result_under_invariant": expected_result,
            "current_result_invariant_holds": after["result"] == expected_result,
            "obsolete_completion_preserved_result": (
                after["result"] == before["result"] if obsolete else None
            ),
            "current_completion_published": (
                after["result"] == request["payload"] if not obsolete else None
            ),
            "current_revision_preserved": after["current_revision"] == 10,
            "returned_same_state": returned is state,
        })
    violations = [
        event["completion_index"] for event in events
        if not event["current_result_invariant_holds"]
    ]
    return {
        "completion_order": list(order),
        "initial_state": initial_state,
        "events": events,
        "first_violation_completion_index": violations[0] if violations else None,
        "contract_holds_for_all_events": not violations,
        "final_state": copy.deepcopy(state),
        "final_result_is_current": state["result"] == "NEW",
    }


results = [run_order(("NEW", "OLD")), run_order(("OLD", "NEW"))]
source_after = SOURCE.read_bytes()
print(json.dumps({
    "probe": "N-PROBE supplied receive completion-order contrast",
    "runtime": {
        "python_version": sys.version,
        "bytecode_writes_disabled": sys.dont_write_bytecode,
        "model": "UNKNOWN",
        "reasoning_effort": "UNKNOWN",
        "configuration_basis": "Host model and reasoning settings were unobserved.",
    },
    "source": {
        "path": str(SOURCE),
        "function_called": "supplied_source.receive",
        "sha256_before": hashlib.sha256(SOURCE_BEFORE).hexdigest(),
        "sha256_after": hashlib.sha256(source_after).hexdigest(),
        "bytes_unchanged": SOURCE_BEFORE == source_after,
    },
    "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "prediction_from_source_before_execution": (
        "Every completion writes its payload: NEW then OLD should end OLD; "
        "OLD then NEW should temporarily publish OLD and end NEW."
    ),
    "invariant": (
        "With current_revision 10, an obsolete rev9 completion must leave the "
        "published result unchanged, and a rev10 completion must publish NEW."
    ),
    "requests": REQUESTS,
    "results": results,
    "product_repair_executed": False,
    "browser_or_external_execution": False,
}, indent=2))
