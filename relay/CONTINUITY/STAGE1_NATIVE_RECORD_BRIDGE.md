# Stage 1 record bridge — one independent B submission, native two-part transactions, external freeze

**Record:** RELAY_STAGE1_NATIVE_RECORD_BRIDGE_V1 · **Scope:** Common planned Runner only · **Status:** SOURCE-REVIEWED CONTRACT / NOT LIVE-ATTESTED · **Governance:** new Common [issue #4](https://github.com/reallakshman19/Common/issues/4), draft [PR #2](https://github.com/reallakshman19/Common/pull/2). This is a Markdown interface map, **not** a second execution state machine, a provenance attestor or a new transaction command.

## Why this bridge exists

The independent Runner format `STAGE1_RECONSTRUCTION_V1` requires **Part A observed original-system baseline before Part B provisional Owner-problem reasoning**, both genuinely authored by Runner B. The native candidate transport `PUBLISH_BUDDY_MARKDOWN` accepts **one message per transaction**, with ordered `STAGE1_BASELINE` and `STAGE1_PLAN` records. Separately, its `STAGE1_FREEZE_CANDIDATE` is only an integrity candidate; `STAGE1_FREEZE_V1` is an external controller/Owner decision with verified visibility. **These are not interchangeable objects.**

## Required logical and physical mapping

| Logical event | Actual authored object | Native record type / source identity | Result / trust boundary |
| --- | --- | --- | --- |
| Original permitted Owner WHAT/WHY and historical source | Controller-curated immutable intake with allowed historical bytes | `STAGE1_INTAKE` | Does not prove fresh B |
| Ask external capable operator to launch B | Separate request, not an actual session | `DISPATCH_REQUEST` | Does not launch B |
| Observe actual B process and read boundary | Provider/controller report with session and read-scope receipt | `DISPATCH_OBSERVATION` | The existing runtime checks format/claimed refs **only**, not their authenticity |
| **B Part A**: independent observed system and genuine source→consumer→output witness | An **unchanged, separately B-authored** Markdown document with top-level `# STAGE1_BASELINE` heading, bound to the same original Stage1 submission/session | `STAGE1_BASELINE` with B's claimed actor | Actual author/session evidence is external, not the string `actor` |
| **B Part B**: independent original problem and provisional hypotheses | A **second unchanged, separately B-authored** Markdown document with top-level `# STAGE1_PLAN` heading, delivered only *after* Part A was completed | `STAGE1_PLAN` with the same B actor claim | Provisional, **not** an approved implementation plan |
| Verify record bytes from all five above | Controller's **candidate-only** digest cross-reference | `STAGE1_FREEZE_CANDIDATE` with five exact TX IDs/digests and `Isolation verdict: NOT_ATTESTED` | No read-scope or stage release authority |
| Decide whether B was actually blind and exact answer externally frozen | Controller-only, source/provider-attested `STAGE1_FREEZE_V1` receipt | **No** `PUBLISH_BUDDY_MARKDOWN` stage for this | Separate authenticated external decision; NOT produced by existing CLI |
| Disclose A's current reality and native technical handover | Existing authority plus genuine Stage1 freeze and separately approved stage admission | Existing `PLAN_HANDOVER` / `HANDOVER_CONTEXT`, then `STAGE2_RECONCILIATION` by permitted route | No automatic execution/merge/lease transfer |

### Original bytes and author custody

1. In an actual isolated B session, request the original **one logical Stage1 response** as **two separately deliverable original Markdown files** authored by B in that same session. Part A must have been completed before B considers Part B. Each file begins with its own `# ` heading to satisfy native message validation, and each must cite the approved original source evidence. B's complete exact raw output, including ordering, is retained as an immutable provider receipt in the controller's evidence store.
2. The external controller compares file bytes against B's original submission and records its provider identifiers, digests, effective tool-read identity and verified positive/negative read probes. **Do not transcribe, summarize, splice, add headers to, or silently manufacture** `STAGE1_BASELINE`/`STAGE1_PLAN` from a combined human-formatted answer.
3. Native `buddy-message` can record B-origin files with a *claimed* actor and durable SHA-256. The CLI's `actor` is a recorded claim, not an authenticated writer signature; external provider facts are essential. The actual publishing operator must not self-certify an independent B author by choosing `--actor runner-b`.
4. If B delivered only one combined file, or the controller cannot prove that both file bytes originated from B in the same permitted run, **HOLD**: preserve the combined raw file unchanged, do not backfill two apparent B messages, and request an authorized real B continuation/re-submission or a separately approved native schema change. No forged split is an acceptable bridge.
5. No new B data is valid if the historical intake changed mid-run, a dispatch supersedes the B output, the tool boundary let B inspect current A/Stage2, or independent source/actor custody is unproven. A locally `COMMITTED` manifest alone is never `STAGE1_FREEZE_ATTESTED`.

## Exact technical limitations of the current V3.2 candidate

The code at `skills/engineering-pr-delivery-v3.2/scripts/transactionlib.py` validates message path, committed receipt, SHA-256, single-stage chronology and two actor claims. It requires an observed dispatch message beginning `# RUNNER_EXECUTION_OBSERVED`, a session and read-scope reference, but **cannot authenticate those external observations**. `STAGE1_FREEZE_CANDIDATE` references `Intake`, `Dispatch request`, `Dispatch observation`, `Baseline`, `Plan`; it refuses any verdict except `Isolation verdict: NOT_ATTESTED`. The CLI's allowed stages do **not** include final `STAGE1_FREEZE_V1`, actual Stage2 reconciliation or `TECHNICAL_HANDOVER`.

Therefore this bridge is an **interface definition and negative acceptance contract**, not evidence that the current runtime supports a completed clean Runner handover. A future native producer-to-provider attestation feature must be separately designed and **authorized through the frozen-tree guard**, before promising automated final stage admission.

## Adversarial examples and acceptance questions

| Input / attempted shortcut | Required treatment | Reason |
| --- | --- | --- |
| Operator copies one combined B answer into two synthetic stage files | **REJECT / HOLD** | Distorts original B record and claimed provenance |
| B submits two separate original files, but current-A GitHub remained readable | **CONTAMINATED / no independent credit** | Content validity is not access isolation |
| Five transaction digests match, but actor/session are only Markdown self-claims | **CANDIDATE ONLY** | No provider-authenticated B identity |
| Agent edits baseline after first digest recorded | **REJECT** by native prior-receipt mismatch | Exact committed source must remain unchanged |
| New intake or dispatch supersedes former B output | **REJECT** stale stage chain | Existing latest chronology cannot be bypassed |
| Controller writes `STAGE1_FREEZE_V1` and invokes native CLI with that as `--stage` | **REJECT** unsupported stage | External freeze is not a local candidate stage |
| Controller has genuine clean B and external freeze, but no native Local/Owner permission | **NO writer promotion** | Stage2 read admission differs from source-writer custody |

**STOP:** Preserve both the original isolated output and the separately committed native message receipts. Do not accept controller-authored reconstruction as independent B, do not label `NOT_ATTESTED` as `STAGE2_RELEASE_PERMITTED`, and do not rewrite the canonical handover/DELP/lease authority. This contract is safe to review as documentation, but its genuine live exercise is **NOT_RUN**.
