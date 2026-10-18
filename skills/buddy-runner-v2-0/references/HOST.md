# Host integration and evidence limits

## Local preparation

The CLI reads JSON and writes local output. It never fetches providers, changes model settings, dispatches an agent or grants authority. Its status facts remain separate from real execution.

Optional request `progress` (or CLI `--progress`, never both) describes a supplied stage claim. `reconstruction_status` records structural availability; `continuation_evidence` separately reports NOT_STARTED, OWNER_WAIT, planned/reported execution or supported/unsupported restriction reporting. All supplied evidence remains SUPPLIED_UNVERIFIED. Even EXECUTED input cannot set `workflow_executed` or `coding_authorized`.

A restriction needs action, attempted boolean, observed restriction, affected scope, evidence and next feasible action. An unattempted action needs a sourced reason. Missing facts yield BLOCKER_UNSUPPORTED without globally denying unrelated work. Publication with activity RECONSTRUCTION never counts as continuation. ONBOARD's Owner wait remains normal; a coding-execution claim cannot bypass it.

Optional request `known_items` lists declared source-linked IDs. Record `dispositions` maps IDs to RETAIN/RESOLVED/SUPERSEDED/PARK, reason and references. `carry_forward.unaddressed` exposes missing dispositions without granting acceptance or proving a complete risk census. Semantic source/impact review remains the engineer's job.

relay_contract validates declared shapes, role and takeover bindings, exact source identity and required source/ROI reasoning fields. It cannot judge whether prose demonstrates understanding. profile_status reports the supplied host/UI configuration evidence; it does not query a model service.

## Source reader

collect(case, reader) validates the entire explicit source batch before calling reader(ref). Support permitted GitHub project resources only; reject foreign repositories, ambiguous paths, credentials and CoordinatorLandingpage case-insensitively before I/O.

reader returns exact body, optional ref and revision. collect hashes the exact UTF-8 body and reports HOST_FETCHED_NOT_OWNER_APPROVAL. These are host reports with their actual trust boundary, never authenticated Owner decisions by themselves.

For assess(..., reader=...), decision events contain ref, exact body digest and reconstruction subject digest. The reader must additionally return author, owner_instruction=True and instruction_kinds containing RECONSTRUCTION_APPROVAL and/or TASK_PROMPT only when the actual source supports those meanings.

The host must establish that classification from the live/direct source. Do not set it from a JSON approval flag or author login alone; agents can share the Owner's GitHub account. An Owner chat instruction may be captured by its actual trusted conversational host with explicit provenance. The CLI cannot install this trust by reading supplied files.

Use the exact same body for byte verification and continuation. Do not re-fetch an event after verification and execute a different body.

## Native coding

relay_native.preflight(checkout, label, plan, task_id, child, lab=None) extracts the selected v3.6 scripts and instructions from commit 54c0f172e0ec017e338e9cc3596348a23abc1bf0 using Git objects. It runs the real native validators in an isolated subprocess.

The child object, local label and plan remain supplied observations. binding_valid is structural, coding_authorized=False and provider_verified=False. The actual agent/host must verify the real approved sources, current child/head, criteria, write scope and ownership before coding.

A selected OWNER_DECISION_REQUIRED route waits for that specific decision; it does not stop independent investigation. An explicitly approved onboarding task may supersede the recommendation.

The actual successor reads the pinned SKILL, MODE_STANDALONE and addendum and executes the authorized task. Native evidence and LOG remain unchanged. No legacy buddy route is called.

invoke(report, assignment, authorize=..., executor=..., receipts=...) supports an external host. authorize must independently check the complete real native binding, source freshness, task scope and actual grant. executor must actually invoke the selected protocol. Neither callback is loaded from request JSON.

No callbacks means CODING_ASSIGNMENT_PREPARED, never an invoked agent. A real returned reference yields HOST_INVOCATION_REPORTED, workflow_executed=False and no claim that coding/product acceptance occurred. Errors or missing references yield INVOCATION_UNCONFIRMED; reconcile host state instead of blind retry.

Matching supplied receipts yield VERIFY_EXISTING_INVOCATION. This is advisory duplicate avoidance, not persistent state, a concurrency fence or verified delivery.

## Limits

The package supplies contracts, prompt workflow, local checks and host seams. It does not install a GitHub connector, launcher, persistent controller, Owner attestation service or global model profile. An interactive agent uses its real connected tools under the skill instructions. Optional Y and an automated production host adapter remain outside this first implementation.
