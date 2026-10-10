# OWNER_DECISION_V1 — authenticated plan disposition and custody reference (template)

**Only an authorized Owner/controller** may issue this decision after inspecting exact evidence; agent-created Markdown with “APPROVED” is a claim, not authorization.

| Field | Independent authority reference / unresolved |
| --- | --- |
| Existing responsibility, episode, current candidate HEAD | [exact checked provider state; observation time] |
| Source of Owner identity and actual approval | [authorized provider/role mechanism; missing => UNKNOWN] |
| Stage 1 independent frozen original | [immutable receipt / read isolation verdict] |
| Stage 2 reconcile / tests / golden readback | [actual current exact SHA, verified or NOT_RUN] |
| Existing Relay/Local transaction + accepted graph/plan revision | [canonical refs, no invented unit] |
| Plan disposition | `APPROVED_SCOPE_ONLY` / `REVISION_REQUIRED` / `HOLD` |
| Accepted or rejected High/Medium items | [why, evidence, Owner authority] |
| Execution disposition | `PLAN_READY_READ_ONLY` / `EXTERNALLY_ADMITTED` / `HOLD_DUAL_WRITER` |
| Writer/lease authorization **external receipt** | [true old A revocation + no in-flight/UNKNOWN + new scoped B lease, or NONE] |
| Next admitted action | [one bounded operation or HOLD] |

**Source of truth rule:** this document merely **references** authorized Local/Relay authority and provider receipts. It must not create an approval, grant, epoch, merge permission or change DELP projection itself. Never infer write permission from GitHub issue edit or a matching Markdown heading.

**STOP:** On missing independent Owner identity, old-agent direct credential revocation, ambiguous pushes, current-head mismatch or protected scope uncertainty, execution is HOLD regardless of a convincing Runner plan.
