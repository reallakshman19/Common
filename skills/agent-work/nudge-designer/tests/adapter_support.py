"""Synthetic declarations for adapter tests; never qualification evidence."""
import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from nd_io import load_json
from nd_profiles import load_profiles


def team_case(name="logic"):
    folder = ROOT / "examples" / name
    intent, plan = load_json(folder / "intent.json"), load_json(folder / "plan.json")
    source = intent["sources"][0]["id"]
    claim = {"id": "source_trace", "status": "AVAILABLE", "basis": "OBSERVED",
             "evidence_refs": [source], "note": "Synthetic fixture declaration only."}
    tool = dict(claim, id="python")
    worker = {"id": "W", "label": "Guided worker", "roles": ["WORKER"],
              "capabilities": [claim], "tools": [tool], "model": None, "reasoning_effort": None,
              "configuration_basis": "UNKNOWN; no host configuration was observed."}
    designer = copy.deepcopy(worker)
    designer.update(id="D", label="Designer", roles=["DESIGNER", "SPECIALIST", "COORDINATOR", "SUCCESSOR"])
    reviewer = copy.deepcopy(worker)
    reviewer.update(id="R", label="Reviewer", roles=["REVIEWER"])
    plan.update(schema="nudge-designer.plan/v1.1", participants=[worker, designer, reviewer])
    plan["nudges"][0]["assignment"] = {"role": "WORKER", "participant_id": "W",
        "capabilities": [{"id": "source_trace", "importance": "ESSENTIAL"}],
        "tools": [{"id": "python", "importance": "ESSENTIAL"}],
        "support": "GUIDED", "method": plan["nudges"][0]["deliverable"], "worked_example": None,
        "reserved_decisions": ["Consequential design/model choice stays with the Designer."], "review_of": []}
    return intent, plan, load_profiles()


def native_return(binding):
    return {"binding": binding, "actor_id": "W", "claimed_status": "COMPLETE",
        "native_report": {"format": "project-markdown", "locator": "work-report.md", "revision": None,
                          "content": "# Existing report\nNative result: PASS (supplied claim).\n"},
        "attempts": [{"id": "A1", "action": "Run supplied local probe", "state": "EXECUTED",
                      "observed": "Recorded the output", "evidence": ["probe.log"]}],
        "findings": [{"kind": "OBSERVATION", "text": "Actual result needs interpretation.",
                      "item_refs": [], "attempt_refs": ["A1"]}],
        "source_observations": [], "contributors": ["W"], "unresolved": ["Integrated outcome unassessed"],
        "next_proposal": "Designer should reconcile the evidence; independent work remains eligible."}
