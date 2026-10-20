# Local-agent evidence handover · v2.0 (optional reference)

**Purpose:** Let the Owner transfer work among fast, sometimes low-reasoning local agents without having to forward the entire conversation or accept their self-reported success. Applicable to software, websites, calculations, analysis, research, documents, media, data migration and investigations. This is a *practical instruction and evidence aid*, not a new Common skill, mandatory reviewer/role, qualification exam, CI gate, or project permission.

**Precedence:** Original Owner instructions and effective amendments → actual project plan, acceptance conditions, permissions and native workflow → actual sources/fixtures → candidate bytes → observed execution → earlier agent statements. If two sources conflict, preserve both and disclose the discrepancy; do not silently choose an easier target. A handoff or verifier does not make a claim true, permit a merge, or release work. For a project governed by `engineering-pr-delivery-v3.6.1`, use its actual selected standalone/coordinator mode; do not infer standalone from this document.

## 1. Seven things that must survive any handoff

1. **Purpose:** exact Owner outcome/WHY, authentic original source and applicable amendments, including replaced requirements.
2. **Subject:** one coherent deliverable and its stable task ID; preserve the entire parent's remaining criteria.
3. **Understanding:** causal input → decision/owner → consumer/output; assumptions and a plausible alternative/falsifier.
4. **Inputs:** actual source and candidate revisions, byte/commit identity where important, original fixture/golden/baseline, accessibility and privacy limits.
5. **Boundaries:** allowed edits/tools, protected data, numerical/behavioral invariants, roles actually available, Owner-reserved actions.
6. **Method and actual result:** commands and interactions, exit codes, raw logs/artifacts, positive and adverse observations, coverage denominator, certainty type.
7. **Continuation:** unresolved known defects versus unavailable observations, affected original criteria, smallest useful next action/actor and a reproducible return location.

This is the same minimum meaning as Common `skills/agent-work/START_HERE.md`, augmented with a small evidence ledger where needed. Prefer the native project issue/receipt rather than duplicate it.

## 2. Rule for a fast local agent: evidence before adjectives

Use **FACT_OBSERVED** only for a direct inspectable witness tied to exact bytes/time/source. Use **EXECUTED_HERE** only for a command or interaction this agent actually performed and recorded. Use **REPORTED_BY_PREDECESSOR** for inherited PASS, hashes and completion statements, even when the report looks confident. Use **INFERRED**, **UNKNOWN**, **NOT_RUN**, **BLOCKED** or **DISPUTED** separately. Hashes prove identity of supplied bytes relative to a reference, not engineering correctness; a manifest authored by the candidate's producer is not an independent source of truth.

Never output an unqualified “all tests pass” if (a) some tests failed or were skipped, (b) only a subset ran, (c) the test used a mock/stub, (d) the candidate differs from the tested bytes, or (e) the result comes only from a predecessor's text. Preserve raw failures even after later fixes. **Missing input, a crash or a broken checker is NOT_RUN/BLOCKED, not PASS.** A failing expected RED belongs to a labelled RED run; it is not a green final suite. A test assertion written to match a wrong implementation is not evidence of the Owner's expected result.

**A useful negative contrast is required for a substantive claimed check:** identify a plausible wrong outcome, run a seeded defect or contrary case where feasible, and preserve what it proves and cannot prove. A negative harness check on a toy does not become a production RED commit. Avoid copying the known final answer into an allegedly independent test.

## 3. Operational sequence (adapt to the task, not a ritual)

**A. Intake.** The receiving agent reads Owner intent, effective amendments, native rules, prior defects and exact candidate. Check source access and authority. Disclose whether earlier proposed answers/findings are visible. Do not perform a qualification exam, demand an Oracle title or treat a fresh chat as blind independence.

**B. Freeze comparison.** Before evaluating the candidate, write the Owner-defined criteria set (all IDs/denominator), the existing best baseline where available and at least one decisive failure condition. If targets are post-hoc, mark this. Record task ID, original source revision, candidate or `UNCOMMITTED`, test-run ID and reviewer identity separately. For software, compare the exact working tree/patch with the exact authorized base and preserve dirty work.

**C. Admit actual artifacts.** Inventory what arrived. Independently read and hash the real file, patch and fixture. For a ZIP: check file list/CRC, path safety, manifest completeness, extra files, hash identity, differences between patch and file copies and line-ending/BOM hazards. If repo work is authorized: inspect **before** applying, then forward `git apply --check` on a clean exact-base worktree; reverse checks against a modified producer tree do not substitute. For noncode work, verify the *rendered/opened* artifact against its raw source.

**D. Preserve a before-state.** Establish the relevant pre-candidate baseline and original input/golden. Record **pre-existing failure**, **introduced failure**, **fixed**, **still failing** or **not attributable** per comparable test. Do not merge counts from different commands into “0 failures”. If tooling/lockfiles unavailable, state exactly what is blocked and continue unaffected inspection.

**E. Execute and look at outputs.** Use existing project tools, actual consumer path, and representative original inputs. Check the observable outcome and its failure/recovery path. For UI, inspect real interactions, focus and output; for CSV/files, open the **downloaded bytes**; for scientific calculations, preserve units, sign, assumptions and independent numerical contrast; for research, read sources and verify citations/date; for documents, inspect layout and source fidelity. Include both what changed and what remained protected.

**F. Self-check before completion claims.** Fill `forms/SELF_CHECK.md` for a human reader or `forms/self-check.json` for the offline checker. Give every original criterion one explicit status, proof and contrary case or an exact NOT_RUN reason. List all actual failures, skipped tests, open defects and unfinished parent obligations. Check current candidate identity after tests. A *self-check is not independent review or Owner acceptance.* If a project mandates native A14/receipt/LOG, publish those **in the native sequence and format**; this local form is not a replacement.

**G. Reconcile.** A reviewer/next agent verifies the real candidate against original criteria, not just producer claims. Retain prior review as historical evidence for its exact candidate, and annotate what a new revision may invalidate. Distinguish **repair recommended**, **ready for further tests**, **candidate evidence sufficient for Owner review** and **Owner accepted**. Only already-authorized participants execute publication, merges, deployments or destructive operations. A report or verification tool never grants those powers.

If inputs are missing: `attempt → observed restriction → affected test/claim → smallest unblocking resource → unaffected useful action`. Don't loop failed downloads/network calls, fabricate tests or repeatedly post a status report instead of implementing when access becomes available.

## 4. Minimum artifact and response contract

An outgoing packet normally contains `HANDOFF.md`, original criteria/source references, the actual candidate or durable locator, a manifest where byte identity matters, and actual evidence receipts or explicit missing states. The incoming return is a **separate** document tied to the actual candidate and original criteria. Prefer one directory/archive revision; never silently overwrite previous packets or edit an independent verdict. A corrected handoff has a new revision and hashes.

A plain-text or Markdown handoff is sufficient when scripts/files are not available. JSON and the optional local checker support repetitive verification but do not substitute for judgment. `tools/capture_run.py` is an optional evidence recorder; its logs are mutable local files, not independent attestations. `tools/check_self_check.py` verifies declared completeness/linked byte witnesses, not execution honesty, citation quality, numerical correctness, independence or acceptance.

For restricted data, leave the source private; include a permitted locator, a locally measured digest, the access restriction and a privacy-safe explanation. Never copy passwords, tokens, private conversations or sensitive customer records into public issues/ZIPs to make the checker green. Redaction changes the shown artifact; verify the redacted copy separately.

## 5. Project adapters rather than universal rules

- **Software/patch:** exact base/candidate, `git status`, locked dependencies, patch forward applicability, baseline→RED→final, changed module/consumer, negative tests, test counts, optional A13 **only if selected project mandates it**.
- **UI/website:** true route and viewport, actions, accessibility, state synchronization, timing, original screens and actual output/download. An enabled button is not output verification.
- **Data/import/migration:** original bytes/row IDs, schema/units, idempotency, transactional failure and rollback, reconciliation and source conservation.
- **Math/science/FEA:** original givens/model, sign/conventions/units, boundary conditions, independent comparison/oracle coverage, solver versus code-compliance distinction.
- **Research:** current primary sources, publication date, source-to-claim map, contested interpretation, uncertainty and no invented references.
- **Documents/content:** complete source and coverage N, baseline version, direct copy fidelity, rendered artifact/page inspection, omitted/reordered material, formatting and editable output where required.
- **Media/design:** actual source rights, target dimensions, editable versus flattened distinction, actual preview, prohibited or missing elements, revision identity.
- **Operational workflow:** target system and permissions, dry-run evidence, idempotence, rollback/side effects, safe/no-write default, confirmation before destructive action.
- **Blocked/read-only task:** what was inspected, what could not run, exact blocker and single route to unblock; not a false completion receipt.
- **Multi-agent/successor:** disclosed authorship/exposure, candidate-to-review identity, immutable historical returns, no blind independence claim, old defects resolved by new exact evidence only.

Use `SCENARIO_PLAYBOOKS.md` for short, runnable prompts/checks per scenario. When a project has its own authoritative rules (e.g., A13 300 lines), those apply; this protocol must not generalize them to unrelated work.

## 6. Native Common alignment (informative; no automatic selection)

This is an optional local aid derived from [Common agent-work START_HERE](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/START_HERE.md) (read Git blob `dec6762df5ab5399d3fed2d6d9b35bbee55a449e`), [task-decomposer](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/task-decomposer/SKILL.md) (`58d9ec08dd651ee4ac0e9a27627b87a84cdf6ad1`), [nudge-designer](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/nudge-designer/SKILL.md) (`012088c60a2d7fbb27776812dfd95fde11ffe786`), [independent-review](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/independent-review/SKILL.md) (`b80f8297d2c067fbab0a43528a7c9eba61928398`) and [gatekeeper](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/gatekeeper/SKILL.md) (`ed9ae6f70f419f958424960e5acef795adf1df98`). Optional modules are aids, not required people or lifecycle passes.

Where separately selected, [engineering-pr-delivery-v3.6.1 standalone](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/MODE_STANDALONE.md) (`50e312f7c86aa6a1b4cbae1bee828a4f25714dba`) requires test-first reporting, source-bound pre-DONE SELF-CHECK, owner-only acceptance/merge, and [A13 300 physical lines](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/CODING_PRACTICES_ADDENDUM.md) (`c70d01d49635b6cc97db2b5d333f11a38790fa69`) for new/materially modified authored source/test. Do not use a convenient 500-line substitution, infer a standing waiver, or fabricate native label/plan approval. Handover Master/BuddyRunner/two-pass/three-pass, if separately selected, use their own native stages; do not graft stages together.

**Location:** optional `Common/skills/agent-work/local-handover/` reference. Publication documents a method, not an installed skill, authority, release gate or AA3 implementation.
