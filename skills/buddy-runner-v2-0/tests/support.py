"""Self-contained test cases; no historical BuddyRunner runtime."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def request(mode="RECOVERY", policy="CONTINUE_AUTHORIZED_TASK"):
    return {
        "version": "buddy-runner/v2", "id": "relay-42", "mode": mode,
        "continuation": policy, "phase": "RECOVERY", "actor": "incoming",
        "incoming": "incoming", "outgoing": "previous", "owner": "owner",
        "repository": "example/project", "issue": "https://github.com/example/project/issues/1",
        "assessed_commit": "a" * 40,
        "assignment": {
            "purpose": "Let the user export complete trace evidence.",
            "deliverable": "Reconstruct purpose, source flow and best route.",
            "inputs": ["https://github.com/example/project/issues/1"],
            "boundaries": ["Preserve original fixtures and export semantics."],
            "success": ["Explain the real input to export path and a falsifier."],
            "uncertainty": "Trace missing input custody; escalate only the affected change.",
            "continuation": "Publish source-backed understanding and next action."
        },
        "profile": {
            "model": "explicit-capable-model", "effort": "xhigh",
            "observed_model": "explicit-capable-model", "observed_effort": "xhigh",
            "basis": "runtime://selected-session", "assurance": "HOST_OBSERVED"
        }
    }


def reconstruction():
    return {
        "takeover_id": "relay-42", "actor": "incoming", "phase": "RECOVERY", "assessed_commit": "a" * 40,
        "sections": [
            {"id": i, "text": "Source-backed section " + str(i),
             "state": "REPORTED", "refs": ["https://github.com/example/project/issues/1"]}
            for i in range(1, 13)
        ],
        "route_challenge": "The old route waits on unrelated UI CI; inspect the export consumer.",
        "choices": [
            {"id": "reuse", "decision": "IMPROVE", "benefit": "Reuse the complete exporter.",
             "route": "Connect the existing exporter through its adapter.",
             "evidence": ["src/export.py:write_trace"], "effort": "S",
             "risk": "Input identity could change.", "falsifier": "Original rows differ."},
            {"id": "keep", "decision": "KEEP", "benefit": "Preserve current behavior.",
             "route": "Continue the inherited integration.",
             "evidence": ["src/ui.py:build"], "effort": "M",
             "risk": "Retains an unnecessary dependency.", "falsifier": "Exporter cannot be reused."}
        ],
        "chosen": "reuse", "rationale": "Existing exporter preserves the oracle with less work.",
        "next_action": "Verify original input identity through the existing adapter.",
        "findings": []
    }


def source(body, author="owner", owner_instruction=True, kinds=None):
    return {"body": body, "author": author, "owner_instruction": owner_instruction,
            "instruction_kinds": kinds if kinds is not None else ["RECONSTRUCTION_APPROVAL", "TASK_PROMPT"]}

