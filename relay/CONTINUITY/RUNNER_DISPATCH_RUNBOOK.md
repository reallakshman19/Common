# Runner dispatch and stalled-handoff recovery — Relay Markdown operating contract

**Governed by:** [Common #890](https://github.com/reallaksh19/Common/issues/890), [candidate PR #893](https://github.com/reallaksh19/Common/pull/893). **Mode:** Markdown communication, not an executable agent launcher. This runbook corrects the observed Core1B loop where source integrity was repeatedly checked while no independent Runner B was started.

## Five gates that must never be collapsed

| Gate | Only acceptable evidence | Responsible actor | Do NOT say |
| --- | --- | --- | --- |
| `SOURCE_INTEGRITY_VERIFIED` | Exactly named allowed files/blobs read back at historical SHA; packet at immutable commit | Preparing A / external verifier | "Runner ready" or "isolated" |
| `DISPATCH_REQUEST_PUBLISHED` | A **single** versioned dispatch request with immutable input refs, actual permitted read surface, external operator, expected response, capability status | A prepares; controller/operator receives | "Runner launched" |
| `RUNNER_STARTED_ATTESTED` | A separately identified new Runner B session/process, actual *enforced* read-tool/namespace limits, controller attestation and denied-read evidence | **External agent-launch-capable controller** | Agent A says "I created a restricted folder" |
| `STAGE1_OUTPUT_SUBMITTED` | Independent B's actual source-grounded factual baseline **before** provisional hypotheses; immutable output ref and real fresh actor/session | Runner B / controller readback | A-authored Stage 1 plan or sample answers |
| `STAGE1_FREEZE_ATTESTED` | Controller verifies unchanged B output, chronology, no unauthorized reads, immutable source and verified access before Stage 2 disclosure | External controller/Owner | SHA alone proves blind session |

**State progression is monotonic by evidence, not by prose.** `DISPATCH_REQUEST_PUBLISHED` does not start B. `STAGE1_SOURCE_VERIFIED` never implies `RUNNER_STARTED`. Never write a future state without its *distinct* external receipt.

## Mandatory dispatch boundary

After preparing an original-only packet, Agent A must **determine whether the current environment exposes a real capability to create a fresh, independently isolated Runner session with restricted read access**. If unavailable, A must:

1. Write **one** [`RUNNER_DISPATCH_REQUEST_V1`](TEMPLATES/RUNNER_DISPATCH_REQUEST.md) under the permitted Relay Markdown channel, naming the external dispatch Owner/operator (or `UNASSIGNED`), exact historical packet Git commit/paths, expected B output and denied reads.
2. Set `DISPATCH_CAPABILITY=UNAVAILABLE_IN_THIS_SESSION` and `RUNNER_STARTED=NO`. Transfer the **request**, not the fiction of a session. Do not promise asynchronous launching or imply the human has already acted.
3. Send one concise exception to the Owner: **`EXTERNAL_RUNNER_LAUNCH_REQUIRED`** with the exact dispatch record/ref and who can perform the action. If the operator is unassigned, flag `OPERATOR_UNASSIGNED` and ask for that assignment rather than rereading content.
4. **STOP the Runner-preparation subtask.** Agent A may resume its independently authorized coding work; it must not write B's answer, fake a denial log, expose Stage 2, or revalidate the same nine blobs as if that advances a gate.

If an actual launch tool exists, the controller must use that supported capability, not a GitHub comment. Record its real new-session ID, restricted tool manifest, source allowlist and forbidden-read attempts. If no actual technical tool/credential restriction exists, the result is `BLINDNESS_UNVERIFIED`, even for a separately opened chat.

### External Stage 1 release decision (not a file-hash gate)

Before declaring `RUNNER_STARTED_ATTESTED` or releasing a B-answer task, the controller must execute the [Stage 1 operator release contract](OPERATOR_STAGE1_RELEASE_CONTRACT.md) and record an actual [release preflight receipt](TEMPLATES/STAGE1_RELEASE_PREFLIGHT.md). Denials must be observed using the **fresh B identity**, including alternate source routes and unallowlisted Stage 2/reviewer paths. If access remains broad or untested, report `REHEARSAL_NOT_BLIND` / `READ_BOUNDARY_NOT_ATTESTED` instead of a clean trial. This never grants source-writing authority.

### Idempotency and no-progress rule

Use a human-readable idempotency key: `<existing-responsibility>|<historical packet commit/path>|<source snapshot tree SHA>|<packet revision>`. It is a claim reference only, **not** a cryptographic authorization token.

When the **same key, source tree, external operator and evidence state** are unchanged, return a one-line prior-record pointer/status and **do not** create another "verified" checkpoint, clone the bundle, ask the same question, or imply elapsed work. A new transition requires a specific new fact: new Runner session, new access-control receipt, actual B output, controller freeze, Owner decision, or a changed packet/allowlist revision. Do not poll an external operator from a session that cannot observe their execution.

For subsequent messages:
- If someone says "check again" without a changed ref, inspect **only the missing gate** (e.g. fresh B submission file or attested controller status), not the already verified source inputs.
- If B still has not started, report the same `DISPATCH_BLOCKED` status with the original request; stop.
- If session/isolation is verified, ask B to produce the actual independently authored baseline; do not declare Stage 1 complete.
- If B claims output exists, read back that **output** and verify origin/freeze, not the source packet again.

## The minimal operator action

The external operator must **actually** initiate a new independent Runner B context/process under enforced controls and pass **only**:
- the Stage 1 historical source packet **or its sanitized content**;
- its listed source snapshot files at exact pinned SHA, plus *only* separately approved direct dependencies;
- the [Stage 1 response instruction](TEMPLATES/STAGE1_RECONSTRUCTION.md) **without** any current implementation or Stage 2 material.

The operator must restrict B's model-context, browser, GitHub connector and filesystem access from current A material. An unrestricted GitHub token with repository-wide read access defeats a file allowlist, even if B is told not to browse. If controls cannot be enforced, mark `DISPATCH_BLOCKED_ISOLATION` or `RESEARCH_REHEARSAL_NOT_BLIND`, not a clean study.

Expected actual B artifact: `STAGE1_RECONSTRUCTION_V1` with Part A **what the historical system did**, real source/consumer witness, variation and observed/UNKNOWN facts, *then* Part B provisional problem reasoning; authored and submitted by B. A may not create it on B's behalf.

## Preparation quality gate — protect the baseline from answer contamination

A pre-bundled packet with original Owner task cases is **TASK_AWARE**, not strictly task-blind. It must not supply A's selected fix, ranked risks/Medium priorities, implementations, current diff/test status, **a ready-made independent B answer**, or demand a copy-ready Stage 1 plan. Prewritten challenge questions, "exactly two designs" and "three counterexamples" can over-frame independent thought. The safer packet states user-visible WHAT/WHY and historical source; B discovers factual source edges and poses its **own** falsifying questions from them.

If the Owner deliberately supplies three questions, separate them as **OWNER QUESTIONS** with provenance, not `B_INDEPENDENT_QUESTIONS`, and require B to first independently demonstrate factual source comprehension. Original user-facing cases/learning outcomes can remain; keep golden answers/Agent A approach hidden.

## Core1B incident example

See [the pinned-source postmortem](EXAMPLES/CORE1B_20261009_DISPATCH_POSTMORTEM.md). There were nine authentic historical blob matches and an unchanged Stage 1 packet. **Zero** attested independent Runner B starts, **zero** submitted B reconstructions, and **zero** independent freeze receipts were observed. The correct durable result is **`INPUTS_VERIFIED; DISPATCH_BLOCKED_NO_SESSION_CAPABILITY`**, not repeated "workspace ready" reports.

**Never make this runbook a platform-wide background timer, automatic agent launcher, or Local/Relay custody authority.** The existing handover, DELP, Owner and Local writer gates remain separately binding.
