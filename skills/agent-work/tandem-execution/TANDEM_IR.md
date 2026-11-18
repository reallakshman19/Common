# TANDEM_IR — implement, challenge, contribute, reconcile

Select this mode when one primary engineer must retain the whole outcome while a second engineer adds independent scrutiny and useful corrections. One existing task/WBS, two onboarded agents, one cumulative product, one final handover. This is a composition of existing Common modules, not a new role, controller, independent certification or release gate.

## 1. Assign once

The Owner/authorized coordinator selects TANDEM_IR explicitly and binds A (primary implementation and final reconciliation), B (reviewer then contributor), original observable outcome and requirements, exact baseline C0, source/fixture access, protected invariants, bounded write/test authority for both, done-list and finite review/return boundary. Use [one assignment](templates/TANDEM_IR_ASSIGNMENT.md) and the [A](templates/TANDEM_IR_AGENT_A.md)/[B](templates/TANDEM_IR_AGENT_B.md) prompts. Retain the existing WBS, coordination mode, native engineering/custody authority and acceptance/release policy. No extra routine approval to make an already authorized bounded correction.

## 2. Overlap useful work, not competing products

| Responsibility | Agent A | Agent B |
| --- | --- | --- |
| Start | Understand originals, implement actual outcome, test and preserve known failures | Independently understand originals, derive expected behavior and wrong cases, prepare executable controls immediately |
| First coherent checkpoint | Publish immutable C1 with exact identity, native changes and evidence | Verify receipt of exact C1; inspect it against independently grounded expectations |
| Contribution | Continue nonconflicting authorized work in own tree; preserve C1 | Preserve C1 review findings, declare contributor scope, fix material defects and add justified improvements/controls in isolated C1-derived tree; return C2 |
| Reconciliation | Review C2 delta and B's original findings, challenge B's corrections, integrate against current A tree, correct residual defects and validate whole outcome C3 | Supply targeted clarification or repair only if justified and requested within the existing grant |
| Handover | Publish one final C3 with actual outcome, lineage, evidence and limitations | No finalization authority; retain useful late evidence without silently replacing C3 |

A need not finish the full task before sharing a reviewable checkpoint. It should cover a coherent behavioral slice with original criteria and a usable native entrypoint or delta. A may continue other work while B checks C1. Checkpoints are immutable; A and B never write the same mutable tree. B records its C1 parent; A reconciles C1→C2 with C1→current-A, checking semantic dependencies even if text merges cleanly. If another checkpoint matters, use a new immutable revision and review only affected claims. No routine full duplicate implementation, waiting for the entire peer workload, or forced extra loop.

## 3. Source-first review, then contribution

Use [OnBoard IR](../onboard-ir/SKILL.md) for a genuinely cold reviewer: supply original intent, C0, original sources, constraints and necessary risk facts, not A's diagnosis, solution or claimed PASS. B records Stage 1 independently derived expectations and a consequential wrong case in the existing task before solution disclosure. After verified C1 receipt, use Stage 2 to challenge actual candidate behavior and test the test oracle. For established or exposed B, reuse still-valid context; derive changed expectations independently where possible, disclose prior exposure/authorship, and never claim a cold review retrospectively. Full OnBoard IR is not an administrative prerequisite for already onboarded agents.

Follow [Independent Review](../independent-review/SKILL.md): bind every finding to exact candidate, original expectation, actual witness, negative case, scope and limits. Preserve the C1 findings before editing the affected scope. Then follow [Contribution & Handoff](../CONTRIBUTION_HANDOFF.md): declare contributor role, affected claims and authorized edit scope; implement material fixes and test them. Do not stop at a report when justified feasible corrections are authorized. Conversely, no gratuitous edit quota: an independently derived executable falsifier or stronger validation can be a meaningful contribution where no legitimate production fix is needed. Record no-op or rejected alternatives honestly.

B's C1 review remains evidence on that exact C1. B's assessment of its own changes is SELF-ASSESSED; authorship, expectation derivation and exposure determine scope-specific independence. A's reciprocal review of B's delta is a second engineering challenge, not blanket independent approval of the jointly authored C3. Preserve actual reviewer verdicts separately from A's decisions. A cannot independently approve its own authored or shared-premise scope. Existing independent acceptance requirements remain in force; no mandatory third agent is invented by this mode. If required independent evidence is unavailable, narrow claims and report the affected requirement NOT_RUN/UNVERIFIED or PARTIAL, without fabricating PASS.

## 4. Reconcile and return

A verifies exact B bytes, parent C1 and actual delta, original findings, executable evidence and known limitations. For each material finding, record retained/adapted/rejected/reimplemented/unresolved with source-based rationale and affected evidence. Run the final consumer/entrypoint, affected positive and negative controls from both agents, and a consequential combined wrong case. Check surviving defects in B's correction and fix them directly where feasible. A may send one targeted correction request when B's context makes it materially useful and the existing authority/budget permits it; additional iterations are evidence-driven, not compulsory. Do not require B to re-onboard or repeat unaffected checks.

Use [Drive handoff](DRIVE_HANDOFF.md#tandem_ir-route) for immutable C1/C2/C3 artifacts and verified recipient receipts; the existing native task/relay carries findings and decisions. The assignment authorizes the selected Drive transport; keep protected inputs and private locators out of public records and obey stronger existing custody policy. A-FINAL is the final publication, never B-FINAL. Use [A's final return](templates/TANDEM_IR_FINAL_RETURN.md).

## Completion and fallback

The assignment sets the practical review return and final reconciliation boundary (e.g. A's completed scope and B's agreed review/return opportunity within active invocations, plus final discovery and combined test run). At a boundary with B pending, distinguish still available work from missing invocation/permission/bytes. A continues feasible authorized implementation and validation; do not silently bypass B while a timely verified return can still be reconciled. No sleep, repeated pings or assumption that an inactive chat is executing. Perform one final discovery of authorized artifacts; if a timely B return exists, reconcile it before finalizing within the assigned budget. If the review is genuinely unavailable or the explicit boundary/budget is exhausted, A may deliver its best supported result with actual review and lineage status; if mandatory verification is unmet, report partial/unverified and preserve the acceptance boundary. The absence of B does not itself prove product failure or independent PASS.

| Situation | Action |
| --- | --- |
| A's C1 not yet available | B works from authorized original sources on expectations, negative controls and isolated exploratory evidence; do not claim C1 review or invent a competing final candidate. A continues. |
| B not available / C2 missing or corrupt | A continues; recover verifiable B findings/deltas if feasible; no fake contribution or independent review. |
| A unavailable | B preserves verified review, native changes and exact continuation; B does not inherit final ownership. Owner/authorized coordinator may explicitly reassign it. |
| C2 arrives while A has continued | A reconciles against actual current A checkpoint and C1 parent; test semantic drift. |
| C2 arrives after final closure | Preserve as late evidence, no silent replacement or automatic reopening. |
| Native dependency/authorization unavailable | Scope the blocker to affected operations; keep other authorized work moving. No invented test, transfer or authority. |

Before handover, A accounts for the actual original done-list on exact C3 (PASS/FAIL/NOT_RUN), review scope and limits, and disposition of material findings. Record outcome COMPLETE only for the proven done-list and applicable required checks; otherwise PARTIAL. Record retained production/evidence lineage separately (A_AND_B or A_ONLY), review status (REVIEWED/PARTIAL/NOT_RUN with scope and independence), and actual publication/recipient verification. An independently derived B check retained as evidence counts as a contribution, not as authorship of A's production code. A rejected patch or unavailable B is not a retained contribution. A's technical handover does not confer Owner acceptance, merge or release.

[Executable synthetic worked case](examples/tandem_ir/WORKED_HANDOFF.md) demonstrates the reciprocal cycle, not a live two-agent execution or proof of independence.
