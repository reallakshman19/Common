# OnBoard IR protocol — source-first judgment, controlled disclosure, durable reconciliation

Status: reusable onboarding method, **not** an active task, independent approval credential, new WBS or role controller. Applies to a genuinely new independent reviewer of a high-consequence candidate, or a skeptical fresh pass when substantial shared-model error is possible. Read [IR SKILL](../independent-review/SKILL.md) first for review authority.

## Authority and custody prerequisites (not a new gate)

The actual Owner/Oracle or appointed coordinator resolves the existing **one WBS**, task issue/revision, current product baseline, review candidate/head, permitted source access, scope, read-only boundary, expected native return, restrictions and who will reconcile findings. A reviewer may discover missing source evidence; it must not infer access or edit authority from a chat title or this instruction. Where no independent principal exists, use SELF_REVIEW with explicit exposure.

Source identities include original file byte SHA and URL/custody, staged config/Datum and input revision; product baseline and candidate are **different objects**. An inaccessible private source stays NOT_RECEIVED (dependent execution NOT_RUN), not a substitute public fixture. Follow [Artifact Relay](../ARTIFACT_RELAY.md): an uploader's hash is not recipient-byte verification; local sandbox or "I sent it" is NOT_TRANSFERRED until actually delivered and checked.

## Protocol stages

| Stage | Input allowed | Executed work | Return/decision |
| --- | --- | --- | --- |
| 0. Bind | Owner purpose, one native WBS/task, baseline commit, exact original source/spec, review authority and custody | Verify actual recipient, available access, current source identity and separation of baseline/candidate | Source/authority ledger; missing input scoped |
| 1. Independent derivation | Baseline code and authoritative source, **not** author solution PR, diagnosis, green status or answer fixture | Independently reconstruct source→meaning→output, expected invariants, alternative hypotheses and at least one surviving-error challenge | Record Stage-1 baseline and exposure in original native task; immutable reference and timestamp if available |
| 2. Disclose | Stage-1 native return exists; record candidate head, proposed PRs, producer explanations, tests and CI | Compare actual code/diffs to Stage-1 model; replay or inspect falsifiers, count independent source members and product output evidence | Claim-by-claim findings bound to exact source+candidate, not merely a PR title |
| 3. Reconcile | Stage-1 return, Stage-2 return, original issue/WBS, live candidate and private custody status | Oracle/Owner decide ACCEPT / CORRECT / INVESTIGATE per consequential claim, preserve dissent and scope; preserve reviewer independence statements | One native return/decision; no new phantom WBS or separate approval controller |
| 4. Continue | Changed source/head/config, new source evidence, replaced reviewer, later return | Invalidate only affected evidence; repeat relevant test/meaning trace; keep old verdict on its old candidate | Delta-only return; one next actor/action and exact native location |

**Information embargo is methodological, not secrecy theater.** Do not withhold essential original requirements, risk constraints or safety facts. "Cold" means hold the author's *solution and claimed expected outcomes*, not necessary facts. Prior exposure cannot be undone; record it and narrow independence claim.

## Review contract

Every consequential judgment must contain: (1) original expected behavior and derivation; (2) actual original and candidate identity; (3) review method/execution vs inspected report; (4) negative or surviving wrong case; (5) result and limits; (6) affected WBS/dependency; (7) current decision owner and exact native receipt. Distinguish SOURCE_PROVEN, CODE_INSPECTED, TEST_EXECUTED, REPORTED_ONLY, NOT_RUN and UNKNOWN. A hash establishes bytes, not engineering correctness. A same-agent second explanation does not add a second independent witness.

**Required states for an evidence row:** UNASSESSED, SUPPORTED, CONTRADICTED, UNKNOWN_SOURCE, NOT_RUN, STALE or NOT_APPLICABLE. Keep the original defect open when its runtime experiment is NOT_RUN; do not clear by absence of evidence.

### Hard stop on the affected claim

Stop claiming product/engineering PASS when original source is missing, source-to-graph authority is unresolved, a relevant negative control was not observed, tested candidate differs from current head, native output was not inspected, or the reviewer authored the scope being independently accepted. Continue unrelated feasible read-only review.

No post-Final node surgery, physical snap/merge, silent support loss, mass duplication or release authorization can be inferred from a successful documentation/CI check. The actual project approval and selected native engineering gates remain controlling.

## Oracle and Agent interaction

Use [Oracle continuity bridge](ORACLE_CONTINUITY_BRIDGE.md) and [Agent OnBoard bridge](AGENT_ONBOARD_BRIDGE.md). Return through the *already established native issue/PR/relay*, not a second registry; when Cycle now is selected, report [Task Evidence v2](../TASK_EVIDENCE_V2.md) using the acting reviewer's five-line task card, with POSTED/DELIVERED/ACK distinct. A successor reviewer receives the exact source/candidate and Stage-1 return, not an authorization to rubber-stamp it; it must identify inherited expectations and independently test an opposite case.

**Status meanings:** PREPARED ≠ DELIVERED ≠ REVIEWER_RECEIVED ≠ REVIEW_EXECUTED ≠ ORACLE_RECONCILED ≠ OWNER_ACCEPTED ≠ RELEASED. Never conflate these transitions. Nothing here creates background agent dispatch or permissions.
