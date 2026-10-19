"""Package the actual local probe evidence into the native return envelope."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


binding = read_json("issued-binding.json")
assert binding == read_json("packet.json")["binding"], "Issued packet differs from bind output"
probe = read_json("probe-output.json")
validation = read_json("validation.json")
assert validation["status"] == "STRUCTURALLY_VALID"
assert probe["source"]["bytes_unchanged"]
assert probe["source"]["sha256_after"] == hashlib.sha256((ROOT / "source.py").read_bytes()).hexdigest()
assert probe["probe_sha256"] == hashlib.sha256((ROOT / "probe.py").read_bytes()).hexdigest()

native = """# N-PROBE diagnostic report

The bounded diagnostic is COMPLETE. The unchanged supplied receive function
violates the current-result invariant; no repair or product acceptance is claimed.

## Actual execution and basis

Read this run: case.md, intent.json, plan.json, packet.json and source.py. These are
local synthetic inputs. Skill instructions, relevant references, profile library
and support scripts were inspected. No examples, tests, other task folders or
earlier agent outputs were read.

probe.py dynamically imports this task's source.py and calls its receive function
four times, using two fresh states and both controlled completion orders. It does
not reimplement or monkeypatch receive. Both states begin with
current_revision=10 and result=null, representing source replacement already done.
OLD is request revision 9 with payload OLD; NEW is revision 10 with payload NEW.

The oracle requires an obsolete completion to leave the published result unchanged
and a current completion to publish NEW. This checks intermediate state as well
as final state. Source inspection predicted unconditional publication in both
orders before the probe ran.

| Completion order | Event | Current revision | Result before | Result after | Expected result | Invariant |
|---|---|---|---|---|---|---|
| NEW then OLD | NEW rev10 | 10 | null | NEW | NEW | holds |
| NEW then OLD | OLD rev9 | 10 | NEW | OLD | NEW | violated |
| OLD then NEW | OLD rev9 | 10 | null | OLD | null | violated |
| OLD then NEW | NEW rev10 | 10 | OLD | NEW | NEW | holds |

In NEW then OLD, the first violation is completion 2: OLD overwrites the already
published NEW result. Final state is current_revision=10, result=OLD.

In the reverse order, the first violation is completion 1: OLD publishes despite
current_revision=10. The current completion then succeeds and restores NEW.
Final correctness alone would miss the earlier obsolete publication. Both current
rev10 completions publish successfully. Current revision remains 10 throughout.

This confirms the supplied F-RACE source observation and supplies the previously
missing U-ORDER runtime evidence. source.py ignores request_revision and writes
state[\"result\"] unconditionally. Rejecting every completion would fail the
current-completion contrast. Changing completion order changes the final result
but does not make obsolete publication permissible.

## Reproduction and structural checks

Run from /workspace/scratch/52eed2252c51/tmp/nd-adapter-forward/worker:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps python -B probe.py > probe-output.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps python -B /workspace/scratch/52eed2252c51/Common-nudge-designer/skills/nudge-designer/scripts/nudge_designer.py validate --intent intent.json --plan plan.json --out validation.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps python -B /workspace/scratch/52eed2252c51/Common-nudge-designer/skills/nudge-designer/scripts/nudge_designer.py bind --intent intent.json --plan plan.json --nudge N-PROBE --out issued-binding.json
```

All three commands exited 0. The probe command's exact stdout is probe-output.json.
Exit 0 means the diagnostic ran; its event invariant checks report violations.
Validation reports STRUCTURALLY_VALID, with semantic quality NOT_MACHINE_VERIFIED.
The bind command's output exactly matches packet.json's issued binding. Binding
does not authenticate the actor, execution or authority.

Python runtime: 3.12.14. Bytecode writes were disabled. Model and reasoning effort
are UNKNOWN because their host configuration was unobserved.

source.py SHA-256 before and after execution:
03a94c76eba2802a7688d8bb8923cbb4ed37d8f624381428ef81120d6debdc34

probe.py SHA-256:
04456c42bc2dff692d9718b6335e08e0252f588e70582dccd9637b484d7f694a

## Limits, unresolved work and continuation

This is actual local Python execution of the tiny synthetic function in controlled
event order. It does not execute a browser, external application, scheduler or
production integration. The source is unchanged. Source revisions in the issued
intent are unpinned; file hashes identify the observed bytes without authenticating
their origin. No command or dependency problem occurred.

N-PROBE is complete. O-CURRENT and R-CURRENT remain unsatisfied in this supplied
implementation. N-REPAIR was NOT_RUN: repair and product editing are outside this
assignment. The Designer can use the measured violation to scope subsequent
repair work, preserving successful current completions and checking both orders.

R-EXPORT / O-EXPORT remain separate pending CSV-format work. CSV requirements are
unspecified, and no CSV implementation or verification ran. This diagnostic does
not resolve that obligation. No plan, intent, packet or source edit was made.
"""
(ROOT / "diagnostic.md").write_text(native, encoding="utf-8")

report = {
    "binding": binding,
    "actor_id": "W",
    "claimed_status": "COMPLETE",
    "native_report": {
        "format": "text/markdown",
        "locator": "diagnostic.md",
        "revision": "1",
        "content": native,
    },
    "attempts": [
        {
            "id": "A-READ",
            "action": "Inspect the five supplied task inputs and relevant skill support.",
            "state": "EXECUTED",
            "observed": "source.py unconditionally assigns payload to state.result; host model and reasoning settings are UNKNOWN.",
            "evidence": ["case.md", "intent.json", "plan.json", "packet.json", "source.py"],
        },
        {
            "id": "A-PROBE",
            "action": "Run python -B probe.py with bytecode disabled, calling the actual unchanged source.receive in NEW/OLD and OLD/NEW completion order.",
            "state": "EXECUTED",
            "observed": "Four actual calls completed. NEW/OLD produces NEW then OLD (first violation 2; final OLD). OLD/NEW produces OLD then NEW (first violation 1; final NEW). Both rev10 completions succeed; rev9 publication violates the invariant in both orders.",
            "evidence": ["probe.py", "probe-output.json", "source.py", "diagnostic.md"],
        },
        {
            "id": "A-VALIDATE",
            "action": "Run the skill's validate command against the supplied intent.json and plan.json.",
            "state": "EXECUTED",
            "observed": "Exit 0; STRUCTURALLY_VALID; semantic quality NOT_MACHINE_VERIFIED.",
            "evidence": ["validation.json"],
        },
        {
            "id": "A-BIND",
            "action": "Run the skill's bind command for N-PROBE and compare its exact output with packet.json binding.",
            "state": "EXECUTED",
            "observed": "Exit 0; issued-binding.json exactly equals the supplied issued packet binding.",
            "evidence": ["issued-binding.json", "packet.json", "package_return.py"],
        },
        {
            "id": "A-REPAIR",
            "action": "Implement or edit product behavior under N-REPAIR.",
            "state": "NOT_RUN",
            "observed": "Repair and product editing are outside this assignment; the supplied source remains unchanged.",
            "evidence": ["case.md", "probe-output.json"],
        },
        {
            "id": "A-EXPORT",
            "action": "Implement or verify the separate CSV-format requirement.",
            "state": "NOT_RUN",
            "observed": "CSV requirements are unspecified and separate; no export completion is claimed.",
            "evidence": ["case.md", "intent.json"],
        },
    ],
    "findings": [
        {
            "kind": "OBSERVATION",
            "text": "Actual calls establish the completion-order evidence missing in U-ORDER and confirm unconditional stale publication described in F-RACE.",
            "item_refs": ["F-RACE", "U-ORDER"],
            "attempt_refs": ["A-READ", "A-PROBE"],
        },
        {
            "kind": "DRIFT",
            "text": "The supplied implementation violates the original current-result requirement and attribution constraint: rev9 OLD overwrites NEW when it completes last and publishes obsolete state when it completes first.",
            "item_refs": ["R-CURRENT", "C-SOURCE"],
            "attempt_refs": ["A-PROBE"],
        },
        {
            "kind": "OBSERVATION",
            "text": "Valid rev10 NEW completions publish in both orders. Any later repair must preserve this positive case; rejecting all completions would fail the contrast.",
            "item_refs": ["R-CURRENT", "C-SOURCE"],
            "attempt_refs": ["A-PROBE"],
        },
    ],
    "source_observations": [
        {"source_id": "S-CASE", "revision": None},
        {"source_id": "S-CODE", "revision": None},
    ],
    "contributors": ["W"],
    "unresolved": [
        "The supplied implementation still violates R-CURRENT / O-CURRENT; no repair, regression of a repaired version or integrated acceptance was executed.",
        "CSV-format requirements remain unspecified, separate and unverified under R-EXPORT / O-EXPORT.",
        "Sources have no pinned source revision in the issued intent; observed source bytes are hashed in the native report.",
        "Model and reasoning effort are UNKNOWN; no host configuration was observed. No external/browser or production integration execution occurred.",
    ],
    "next_proposal": "Designer reviews the actual four-call trace and scopes any subsequent N-REPAIR within actual authority; keep both completion orders and current-completion success as verification conditions. Preserve the independent CSV question without marking it complete.",
}
(ROOT / "return.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps({
    "status": "PACKAGED",
    "packet_binding_matches": True,
    "native_content_sha256": hashlib.sha256(native.encode("utf-8")).hexdigest(),
    "native_content_matches_file": report["native_report"]["content"] == (ROOT / "diagnostic.md").read_text(encoding="utf-8"),
    "source_and_probe_hashes_match_output": True,
}, indent=2))
