# Tandem Execution — one-way, two-agent delivery

**Purpose:** obtain the benefits of two different engineering investigations without multiplying coordination, duplicated patches or report-only returns. The second agent advances the working product, rather than sending findings back to the first.

This is an execution method for Agent A and Agent B. It uses one actual task and the existing permission/acceptance boundaries. It does not create a new role or a dispatch service.

## Start with the smallest suitable path

- **New pair:** use the [single assignment](templates/ASSIGNMENT.md), hand both agents the original outcome and permitted source. A starts first; B may investigate the baseline in a separate read-only scratch space while A builds. A completes and uploads; B begins its write turn from A's Drive checkpoint.
- **Two agents already investigated:** keep both original discovery records. Give A the useful findings from both, reconcile while implementing; B reads the actual A candidate and fixes the remainder. No extra discovery or review-only round.
- **A has already built:** B receives the verified Drive package and proceeds directly. Do not send A a request for another status report.
- **A partially completes or is interrupted:** B can continue from the last usable checkpoint once A's write turn has ended. If no usable candidate exists, B reconstructs from the original baseline and available native deltas. Be precise about what A did not deliver. Do not manufacture a successful A turn.
- **A fully solves the issue:** B still runs an original-source-derived adverse case and contributes executable coverage or integration proof, not needless production edits.

## Read map

[Protocol](PROTOCOL.md) — ownership, allowed transitions, recovery, convergence.
[Methodology](METHODOLOGY.md) — evidence, actual code execution and cross-checks.
[Drive handoff](DRIVE_HANDOFF.md) — package contract, actual byte verification and worked recovery.
[Agent A prompt](templates/AGENT_A.md) · [Agent B prompt](templates/AGENT_B.md) · [Final return](templates/FINAL_RETURN.md).

## Golden TA-G01

[Raw case](examples/golden/RAW_CASE.md) · [baseline implementation](examples/golden/baseline.py) · [A candidate](examples/golden/candidate_a.py) · [B candidate](examples/golden/candidate_b.py) · [worked handoff](examples/golden/WORKED_HANDOFF.md). Run `python -m unittest discover -s tests -v` from the skill directory. The synthetic case is about distinct occurrence IDs and durable saved-plan preservation. It proves the example's executable behavior, not the real NWv7 product or a real multi-agent transfer.

## Why the method matters

The original execution failure is not insufficient commentary. It is the loss of delivery ownership whenever new defects appear. A report identifying a fix is not that fix. A clean test run on a predecessor's candidate is not current evidence for a changed successor. A shared folder link is not verified file custody. Both agents must create useful engineering value, but the active candidate has one owner at a time. B resolves the discrepancies and publishes the final cumulative result.

## Boundaries

Drive is the only handoff and delivery channel. Source code may still originate in an authorized repository; a required native PR/merge operation is distinct from handing work between agents. The assignment grants the two turns once, and no new authorization is needed for the planned conditional succession. Actual invocation of B requires an available agent transport or a resume in B's session; Drive alone does not run an agent. Do not claim dispatch, receipt or independent product approval from an upload. No mandatory third role.
