# Tandem Execution — two implementers, one final outcome

**Purpose:** use two agents' engineering capacity concurrently without waiting for a predecessor or routing ordinary defects back to their author. The final owner B chooses, integrates, repairs and validates the working product. This is an execution recipe for A and B only; it is not a reviewer onboarding, succession of project control, additional WBS or agent dispatcher.

## Choose execution at assignment

| Pattern | When | Starting work | Final ownership |
| --- | --- | --- | --- |
| **PARALLEL (default)** | Two capable agents can build from the same source or recoverable checkpoints | A and B independently write isolated candidates immediately | B converges available contributions and fixes remaining work |
| SERIAL (explicit opt-in) | A's coherent product is a genuinely necessary input to a later refinement | A produces C1; B can prepare tests and isolated repairs without touching A's mutable tree | B continues C1 or reconstructs if missing |

Do not infer SERIAL from A/B names, numbered stages, an absent READY file or the fact that one agent finished earlier. In either pattern, only a real shared-write conflict restricts writes to that particular tree.

## Minimal route

- **New pair:** [one assignment](templates/ASSIGNMENT.md) → [A prompt](templates/AGENT_A.md) and [B prompt](templates/AGENT_B.md) → actual native work in isolated candidates → [Drive exchange](DRIVE_HANDOFF.md) → B's [final return](templates/FINAL_RETURN.md).
- **Both already investigated:** reuse the evidence. Allocate complementary corrections. Both implement now. No extra audit stage.
- **B already implemented before A delivers:** keep B1, run more useful controls, publish it. It is a working candidate; A is not an implementation prerequisite. Integrate later if A's usable work arrives before the selected final snapshot.
- **A unavailable:** B completes the bounded task on B1/C0 with an honest B-only lineage. Missing A is not a defect in a complete B product.
- **Both touched the same file:** resolve the behavior against original intent, not the number of edits or which agent arrived first. B owns the final integration.
- **Previous v2 serial assignment:** explicit parallel amendment supersedes the sequencing restriction; preserve both agents' existing code. Do not restart. If no amendment has been granted, do not infer new write authority.

## Read map

[Protocol](PROTOCOL.md) — execution states, isolation, convergence boundary, late/absent peer, acceptance and recovery.
[Methodology](METHODOLOGY.md) — independent derivation, meaningful repair, three-way semantic integration, falsifiers and evidence.
[Drive contract](DRIVE_HANDOFF.md) — immutable candidate packages, markers, byte verification and fallback.
[Checklist](CHECKLIST.md) — inspect the actual outcome, not the presence of ceremonial files.
[NWv7 worked allocation](examples/NWV7.md) — example grounded in the A08/A09 audit pairs.

## Executable goldens

- **TA-G02 (parallel, default):** [worked case](examples/parallel/WORKED_HANDOFF.md). Both A1 and B1 are produced from C0; each corrects a separate failure in the same native file. B combines them, tests both, and the fallback case shows B proceeding when A1/READY is absent.
- **TA-G01 (serial, legacy):** [raw case](examples/golden/RAW_CASE.md) · [baseline](examples/golden/baseline.py) · [C1](examples/golden/candidate_a.py) · [C2](examples/golden/candidate_b.py) · [worked handoff](examples/golden/WORKED_HANDOFF.md). Retained as an explicitly selected alternative.

Run `python -m unittest discover -s tests -v` from this directory. The tests execute synthetic native implementations, offline archive verification and a small policy reference. They do not dispatch agents, authenticate Drive access, enforce writer leases, or certify any real NWv7 repair.

## Why this revision exists

The previous recipe let B prepare tests but withheld implementation until A-READY. That is serial execution and can leave a capable B idle. A single writer across a whole task is unnecessary when each agent owns its own isolated candidate. Restrict only competing writes to the same candidate; make B's final integration exclusive, not its initial work conditional. An incomplete peer contribution is a lineage limitation, not an engineering blocker.

Drive is the sole handoff channel; authorized repository access remains a source and native development mechanism. An inactive separate conversation still needs invocation; an upload is not dispatch. Existing product approval/release rights remain unchanged. No extra participant or approval step.
