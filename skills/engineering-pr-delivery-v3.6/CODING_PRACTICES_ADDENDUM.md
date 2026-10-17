# Engineering PR Delivery v3.6 — coding and task-continuity ADDENDUM

> **Provenance:** base text from draft [Common PR #402](https://github.com/reallakshman19/Common/pull/402) (head 727eac11), reused per #409 V36-ECO-01. Extended with the A01–A14 agent requirements of [#409](https://github.com/reallakshman19/Common/issues/409) and the Owner's A13/A14 ([CoordinatorLandingpage #1 6230407705](https://github.com/reallakshman19/CoordinatorLandingpage/issues/1#issuecomment-6230407705); wording = Codex Q12, #409 comment 6230450337). #402's renderer script, fixture and workflow are **not** included here; their reuse is decided in ECO-02.

**Owner authority:** [Common #400](https://github.com/reallakshman19/Common/issues/400), additional Owner direction [#6220465115](https://github.com/reallakshman19/Common/issues/400#issuecomment-6220465115). Additive guidance only. The accepted native v3.6 O1–O5 lifecycle, exact AIM label, canonical TASK_EVIDENCE v3.6 parser, snapshot, publisher, separate v3.6 two-/three-pass generators and BuddyRunner 1a→1b→2 must not be changed by this addendum. Historical v3.5 practices are **copied as independent design invariants**, not imported as runtime dependencies.

## Original problem

After several engineers, activity reports and PR titles say that tasks progressed but do not preserve the original Owner WHY, original inputs/golden/benchmark, root-cause-to-code path, competing approaches, chat-delivered Owner technical amendments, parked improvements and reason for adopting a high-ROI fix. Ad hoc agents asked simply "follow v3.6" can also omit task-evidence entirely, because no coordinating agent appointed a governing work label and child. Make the issue **the navigable and lossless engineering record**; do not make a reporting tool another execution authority.

## Source-level v3.5 practice port audit (not a bulk version migration)

| v3.5 source | Behavior worth retaining independently in v3.6 | Native disposition |
|---|---|---|
| `operating-model/architecture-preservation-contract.md` | ROADMAP/Owner > bounded task; status projections distinct from material/execution/merge/release; recovery vs handoff; source-specific drift; immutable receipts | ADDENDUM rule, no v3.5 import |
| `scripts/owner_commands.py` / `SKILL.md` | Lossless direct Owner intent; meaningful chat amendments before technical normalization; quoted source cannot fake direct Owner instruction | Input custody for C2/C3, not auto-publication |
| `operating-model/agent-task-publication.md` | Owned child ISSUE with IMPLEMENTATION_PLAN, PLAN_UPDATE, TASK_EVIDENCE, TASK_RESULT; cross-issue links; conversation record for material changes | Preserve structure via issue chain; do not create unnecessary issue per reply |
| `templates/checkpoint-facts-v35.md` + `delp_projection_v35.py` | Agents publish facts for their own leaf, not percentages or titles; exact SHA/evidence refs; empty proof visible; changed HEAD invalidates old proof | Native v3.6 governed O2 stays mandatory; optional ad hoc receipt cannot set E count |
| `operating-model/parent-handover-ledger.md` | Parent=WHAT/WHY/roadmap, child=implementation/repro/test, handover=index; source before chat memory | C1/C2/C3 issue spine, append-only receipts |
| `operating-model/durable-execution-lineage-projection-v35.md` | Stable task identity/lineage, rejected stale bindings, continuity from current provider truth, E/P separate from Owner acceptance | C2/C3 and future C4; do not import DELP |
| `operating-model/owner-reporting-delta.md` | Report only what changed; status failure cannot become a new material-write safety gate | Read model, no new writer authority |
| `SKILL.md` continuation/coordination | Reconcile parent+Owner decisions, selected frontier, exact PR/CI, negative knowledge before “proceed”; recover missing checkpoints | C3 successor and this addendum |
| v3.5 BuddyRunner/2-/3-pass integration | Independent thinking, reconcile KEEP vs high-ROI IMPROVE, park ideas with return condition | Use current selected native v3.6 BuddyRunner or Handover Master version (no stage graft) |

**Caution:** Some v3.5 operating-model files document historical v3.1 recorder semantics and conflict with stronger security invariants elsewhere. Do not blindly port policies (e.g. permissive takeover, external lease weakness) into v3.6. Use current native v3.6 and actual selected product protocol as binding authority.

## Ad-hoc task evidence — optional only when NO protocol is selected

Precedence is explicit:

| Conditions observed | Result |
|---|---|
| Project Team Protocol `TASK EVIDENCE v2`, or another explicit programme protocol | It wins; its evidence is mandatory on its governed surface |
| Approved v3.6 `relay/AIM/<WORK>.yaml` + matching plan + actual owned child | Existing `TASK_EVIDENCE v3.6` **mandatory** at finished task boundaries; original parser unchanged |
| Someone says "use v3.6" but no approved label/plan/child exists | No fictitious v3.6 O2 or task progress; HOLD native admission, allow harmless investigation |
| Genuine ad hoc agent, no explicit/project evidence scheme | OFFER optional `TASK_EVIDENCE — ADHOC` (readable evidence), chat-only unless authorised issue target |
| Ad hoc agent expressly selects another evidence protocol | Follow it; DO NOT add a v3.6 receipt in parallel |
| Explicit and project protocols conflict | HOLD/conflict disclosure; do not choose the lax one |

Ad-hoc receipt is a helpful default **invitation**, not a mandatory protocol on a foreign agent. It must not begin the exact three-line "Outcome / For the user / Proof" native `TASK_EVIDENCE v3.6` opening or include the literal `TASK_EVIDENCE v3.6` parser token. It is never eligible for v3.6 publisher progress, issue title mutation, material/merge/release permissions, or TeamOwner TASK EVIDENCE v2 credit. An explicit selected protocol is respected and validated by *its* real governing code.

### Optional ad-hoc receipt example (not proof)

~~~text
TASK_EVIDENCE — ADHOC / ADVISORY (NOT v3.6 O2)
Issue chain: #123 → ~~#125~~ (INVALID_REPORTED: out-of-scope; decision ref) → #126
User outcome: <what changed for the user, or nothing yet>
Exact source/candidate SHA: <40-character actual SHA or UNKNOWN>
Implementation crux: <entrypoint -> adapter -> worker -> consumer; source links>
Original fixture / golden / benchmark: <original hashes or specific UNKNOWNs>
Tests on exact SHA: <hosted run, negatives, environment; else NOT_RUN>
Observed result / negative knowledge: <precise claim, hypothesis vs proof>
Next source-first verification: <one reproducible check, blocking authority>
Owner/academic/merge acceptance: NOT_GRANTED
~~~

If no exact commit exists, the **programmatic receipt refuses** instead of printing fake SHA. Human-only draft can explicitly say UNKNOWN without claiming an exact source. Never publish Owner-provided private chat or source files to public GitHub without authorization.


### Native v3.6: continuity must be a SEPARATE issue-context receipt

Source-first compatibility: `lifecycle_v36.validate_evidence` requires the **exact eight-line canonical task-evidence comment** produced by `render_evidence`. It rejects **all trailing lines**. `snapshot_v36.snapshot` scans issue comments for the exact `TASK_EVIDENCE v3.6` marker before applying validation, so even an explanatory human comment containing that marker may generate a spurious invalid-evidence observation.

Therefore, on a **governed** child publish:
1. The existing **unchanged canonical eight-line task-evidence comment** on that child's issue (exact source, proof, candidate, tests).
2. A **different** linked comment, headed `CONTINUITY_CONTEXT v3.6`, containing the issue genealogy (`#123 → ~~#125~~ → #126`), original fixture/golden/benchmark source pointers, actual implementation crux, Owner amendments, causal known gaps, parked/adopted decisions, and one next verification. **Do not include the canonical task-evidence marker anywhere in this context comment.**
3. Link the context comment in the parent/child evidence spine, or if the protocol disallows a comment, in a separate authorized versioned issue index. It is **advisory context, not a second O2 proof or acceptance record**.

This is not yet an automatic publisher or index writer. The two-comment pattern is **planned** until the source-custody/provider integration C2/C3 is implemented, and requires the same authorized issue publication scope and privacy review as other technical Owner context.

## Issue lineage as a complete time-indexed path

Use a historical list/graph, not only today's active issue hops. An invalid/superseded middle step still represents a real attempted agent handoff, source decision or fixture.

### Example — purely illustrative, not actual Common issue status

`[#123](https://github.com/example/tracker/issues/123) → ~~[#125](https://github.com/example/tracker/issues/125)~~ (INVALID_REPORTED — wrong responsibility; [decision](https://github.com/example/tracker/issues/123#issuecomment-12345)) → [#126](https://github.com/example/tracker/issues/126)`

The arrow from #125 to #126 **remains**. The tombstone is not removed or replaced by a shortcut #123→#126. Each node keeps issue number, previous hop, status, reason and source-bearing decision receipt. A *status claim* can be shown as a reported tombstone; it is NOT verified by the renderer. A future C2 provider verifier must confirm actor, exact Owner decision and source before upgrading it to authenticated invalid/deleted.

Status rules:

| Status | Display | Reason |
|---|---|---|
| ACTIVE | Plain linked | Current candidate/path; not guaranteed accepted |
| SUPERSEDED_REPORTED, INVALID_REPORTED, DELETED_REPORTED | Strikethrough **plus** status/reason/decision link | Preserves history; indicates the disposition is reported, NOT authenticated |
| INACCESSIBLE_UNVERIFIED, NOT_FOUND_UNVERIFIED, UNKNOWN | Not struck; explicit warning/reason | A 404 can mean deleted, private, no permission or transient absence |
| Future DELETED_VERIFIED | Not in current C1 renderer | Requires independently corroborated deletion record beyond unauthenticated 404 |

Draft #402's synthetic fixture and pure renderer (not included in this PR) test duplicate #s, broken parent edges, unsafe/foreign decision links, missing reasoning and false deletion classification. They cannot know about unknown *unpublished* intermediate issues; complete history depends on the owning issue index (C2/C3), append-only evidence and source actor/fixture verification.

## Agent requirements A01–A14 (#409 §4, plus the Owner's A13/A14)

| ID | Requirement (short form; #409 §4 is authoritative for A01–A12) |
|---|---|
| A01 | Select the actual governing protocol, approved work/plan/owned child and valid permission. Titles, START or a checker PASS are not grants |
| A02 | Reconcile the original Aim, effective amendments, task benefit and non-goals at assignment and on material change |
| A03 | Capture material Owner technical input with complete conditions, source and provenance grade; an agent quotation never authenticates Owner authority |
| A04 | Identify original positive/negative input, full/partial golden and benchmark at exact source/hash, or declare missing/unknown/synthetic |
| A05 | Explain input → owning function/decision → consumer/output, before/after, preserved components, falsifier and excluded claims |
| A06 | Publish unchanged canonical evidence on the real own child when valid; keep the LOG; link richer context separately |
| A07 | Report real failures/PARTIAL/BLOCKED/NOT_RUN, tested source and capability needs, with no fake completion |
| A08 | Preserve older contributions, causal decisions and sourced superseded/invalid issue hops; a 404 stays availability-unverified |
| A09 | Keep improvement rationale, author, source, disposition and revisit trigger; KEEP/NO_CHANGE is valid; no unilateral redesign |
| A10 | Link PR → task/issue/evidence → conversation or a permitted restricted reference; acknowledge missing provenance and shared-account limits |
| A11 | Use the actually selected native successor/multipass method and protected phase inputs; no stage graft or automatic version migration |
| A12 | Supply facts to the one scoreboard/title publisher; no hand-authored inflated progress, self-granted acceptance or extra timers |
| **A13** | **Coding practice** (Owner): see below |
| **A14** | **Self-check and issue reconciliation before a task claim** (Owner): see below |

## A13 — coding practice within authorized scope

**A13 — coding practice within authorized scope.** New authored source/test files and materially changed source/test files must satisfy the 300-line file limit. An existing file already over 300 lines must not grow; when materially touched it is split along a coherent responsibility boundary as part of that authorized change. Unrelated oversized files are not a mandate for a big-bang rewrite. If the necessary split crosses allowed paths or changes an interface/scope beyond the grant, report that precise prerequisite; do not perform the wider refactor or claim compliance.

Use one documented, deterministic size basis: physical file lines, including blank/comment lines, at the exact comparison base and candidate; report each changed file's before/after count. Identify the authored source/test file set and any generated/vendor/data exclusions explicitly. An exclusion is a scope rule to justify, not a loophole for hiding authored logic. Do not compress statements, delete useful explanation or scatter coupled code merely to pass a number.

Functions should normally be approximately 50 lines or fewer, using a documented language-aware span measurement. A deviation is recorded with its reason and reviewed for cohesion; an approximate target does not silently become a hard universal parser gate.

Keep one coherent responsibility per module, reuse established modules, and avoid duplicate engines/parallel implementations of the same responsibility. The required independent reviewer assesses these properties and any claimed deviation; line counts alone do not establish them.

Changed behavior has applicable tests, including changed failure boundaries where relevant. Report the actual tested source, commands/environment, results, failures/skips and NOT_RUN reasons. Scope-preserving structural changes still need appropriate regression evidence. A read-only or blocked task uses its own stage-appropriate criteria, not invented future implementation tests.

Mechanical checks may verify size measurements and explicit ratchet violations; they do not judge understanding, architecture, benefit, correctness or acceptance. New workflow changes or widening shared paths require their own applicable authority.

## A14 — self-check and issue reconciliation before a task claim

**A14 — self-check and issue reconciliation before a task claim.** Before a new DONE, PARTIAL or BLOCKED claim, publish one source-bound SELF-CHECK v1 companion on the task's actual evidence issue. Use the real stable task ID, governing plan/criteria revision, issue and assessed candidate/source. Where the native task has no candidate or accessible source yet, state UNKNOWN/NOT_AVAILABLE and identify the resolver; never invent an identity.

Reconcile each applicable done-when item for the current authorized task/stage against actual proof, the planned/changed scope, A13 where applicable, actual tests, the issue checklist and every known unresolved task obligation. Mark MET only when the cited proof supports that criterion; otherwise use NOT_MET, NOT_RUN or UNKNOWN with its limit. NOT_APPLICABLE requires an explicit stage/scope basis and cannot waive an unmet criterion.

List pending items with their stable existing task/issue reference where one exists, responsible actor, smallest next action, dependency/unblock condition and whether they prevent this task's done-when. Unknown ownership is reported UNKNOWN and routed, not invented. This is reconciliation of existing work, not another task-number/counter scheme.

DONE is supportable only when all applicable task done-when criteria are MET, no unresolved obligation needed for that task remains, and the scope/required checks are satisfied. Separate future work may remain open if genuinely outside the approved unit; retain its source/owner and limits. Do not shrink criteria, rename the unit or move pending work merely to obtain DONE. PARTIAL/BLOCKED reports remain honest when evidence or capability is missing.

A self-check is the author's report, not independent verification, approval, release or Owner acceptance. The coordinator assesses its applicability/sufficiency against the real issue, plan, source and authority. Missing or stale self-check means the new completion claim is unqualified; it does not erase material work, prove a failure, or prohibit reporting a blocker.

Keep native evidence/LOG unchanged. The self-check is linked supporting context, earns no native evidence/progress/acceptance credit by itself, and creates no new lifecycle/phase. Corrections append with the replaced companion's reference; changed plan/candidate/proof invalidates affected current claims while preserving history.

The coordinator reconciles pending facts into the existing issue/control/status records, keeping actual ownership, next action and unresolved decisions visible. Use Next Move only where the project's real opt-in and authority permit it. A pending row or “next” instruction is neither dispatch nor permission to work. Do not tick issues, expand scope or approve work merely from the self-check.

**OTM extension (labelled, not Owner wording):** the same self-check also applies before a FAILED claim.

### A14 in native v3.6: the exact linkage (Codex Q12 §4)

1. Publish the `SELF-CHECK v1` companion **first**, on the real own-child issue.
2. Keep the **canonical 8-line comment byte-identical**. Retain the actual user benefit on its native `For the user:` line and append a short inline `Self-check: <companion permalink>` **on that same line**. This uses an existing text field; it is not a ninth line.
3. **`Proof:` stays the qualifying PR or exact PR-commit URL.** The snapshot rejects an issue-comment proof, so the self-check permalink must never go in Proof.
4. **Never put the canonical marker in the companion,** even in a quotation; the snapshot scans comments for it. No code fences, extra Proof lines or commentary in the canonical comment. The terminal LOG stays in its native place.
5. **Blocked before a candidate or a real test run exists:** publish the honest companion plus a status/context report with NOT_RUN/UNKNOWN/NOT_POSTED. Never manufacture a canonical receipt, tests (no 0/0) or a PR. No native E credit is earned.
6. **Standalone (non-governed) work, e.g. #409 itself:** publish the companion on the registered team evidence issue. Do not create fake governed children.

Companion template (plain text; **not** a completion receipt):

```text
SELF-CHECK v1 · <stable task ID> · <own evidence issue>
Basis: plan/criteria <source + revision>; candidate <repo@sha or UNKNOWN with reason>; source/fixtures <refs or limits>
Done-when: <criterion> → MET <proof> | NOT_MET <gap> | NOT_RUN <why> | UNKNOWN <missing source>
Scope: approved <paths/ref>; actual changed <paths>; extras <none or grant/gap>
A13: applicable <yes/no + basis>; files <before→after/count source>; legacy split <result/gap>
A13 review: function-span findings <refs>; cohesion/reuse/duplicates <author's assessment + limits>
Tests: <command/environment> @ <tested sha> → <actual result>; failures/skips/NOT_RUN <limits>
Issue reconciliation: <criterion/checklist ref> → <actual proof or mismatch>
Pending: <existing ref or descriptive item> · owner <actor/UNKNOWN> · next <action> · unblocks <event> · prevents task DONE <yes/no + basis>
Proposed claim: DONE | PARTIAL | BLOCKED · reason/limits <text>
Native report: <permalink when published, or PENDING/NOT_POSTED with reason>
```

## Workstream implementation coding checklist

- [ ] Verify current main, exact PR head, selected Owner AIM label/plan and original user problem before coding.
- [ ] Determine real source→effect chain, actual Writer/calc/adapter/Worker boundaries, dedicated source files and exclusive ownership.
- [ ] Identify original positive and negative fixtures, source blob/content SHA and golden completeness; never use synthetic data as acceptance proof.
- [ ] Reconstruct previous agents' meaningful contribution/false turns and Owner corrections from durable issues and relevant technical chat receipts.
- [ ] Choose KEEP vs bounded IMPROVE; record ADOPTED/REJECTED/PARKED with actual decision source, evidence and revisit trigger. No forced innovation.
- [ ] Declare tests that could falsify the proposed fix and check baseline-red vs introduced red, in actual user flow.
- [ ] Deliver small main-rooted PR, no patchwork or duplicate calculation engine; after tests reconcile candidate SHA to exact hosted results.
- [ ] Publish governed TASK_EVIDENCE on own child when required; in unbound ad hoc work *offer* an advisory evidence receipt, never mark native O2.
- [ ] A13: report each changed file's physical line count base→candidate; no file over 300 lines grows; split legacy files along a coherent boundary when materially touched; record any function-span deviation with its reason.
- [ ] A14: publish the SELF-CHECK v1 companion before DONE/PARTIAL/BLOCKED (and FAILED), link it from `For the user:`, and keep Proof as the PR URL.
- [ ] Capture one human implementation crux: changed modules/functions, preserved consumers, before/after, observed failures and next verification.
- [ ] After source/issue drift, pause the affected unsafe step and re-evaluate; do not infer Owner merge/release or task priority from current titles.
- [ ] Never hide historical invalid issues or close chain history because an intermediate node is removed. Keep a tombstone with attributable evidence.

## Phase-safe relation to existing protocols

Handover Master chooses the currently approved process. BuddyRunner 1a remains HOLD, 1b independently reconstructs and 2 reconciles once, Xb→Y once; version selected by the project's real governing source. V3.6 native two-/three-pass keep their own stage definitions. No authored answer, finished fix or later chat solution goes to a blind Pass A. This addendum is **coding practice and read-only receipt/view only**, not another coordinator, module-scoring system, provider fetcher or execution lease.

## Next stages / limits

This is a separate main-rooted addendum PR, independent of draft #401 C1. Real source-provider attestation of Owner input/issue deletion, full original fixture/golden/benchmark, native successor wiring and the C4 automatic title/labels are NOT implemented here. Those require the Issue #400 C2–C7 programme and independently tested exact-head source. No current v3.6 source protocol, TeamOwner mode, hard-coded LAB title or protected decision is altered.
