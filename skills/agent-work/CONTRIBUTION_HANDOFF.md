# Oracle and reviewer: contribute, then hand over

## Contents

- [Bound every PASS](#bound-every-pass)
- [Choose the next task from evidence](#choose-the-next-task-from-evidence)
- [Choose useful work](#choose-useful-work)
- [Keep authority and independence explicit](#keep-authority-and-independence-explicit)
- [Make one coherent contribution](#make-one-coherent-contribution)
- [Record the contribution](#record-the-contribution)
- [Continue from the checkpoint](#continue-from-the-checkpoint)

Use this recipe when an Oracle or reviewer has useful context and the Owner wants
that participant to contribute before another coding agent continues. Preserve
insight as a usable artifact, verified behavior or executable next task. Review-only
work can end with a complete assessment; it carries no implicit repair assignment.

Apply the recipe inside existing project authority and native records. It adds no
skill dependency, runtime controller, mandatory team, score or approval ceremony.
An Oracle title establishes neither technical competence nor permission to write.

## Bound every PASS

Apply these two rules to implementing agents, reviewers and Oracle alike:

**Rule 1 — No PASS beyond evidence.** Bind every PASS to a precisely bounded claim,
an identified expectation source and actual execution evidence on the named
candidate/input. Record commands or interactions, outputs, exit status and input
hashes where consequential. Source/artifact inspection supports only the inspected
claim; it cannot establish unexecuted runtime behavior. Keep independently reviewed
expectations distinguishable from author-generated assertions.

**Rule 2 — No consequential PASS without a surviving-error challenge.** Ask what
significant wrong behavior could still pass the proposed test. Identify a materially
plausible error within the claimed scope, then strengthen the evidence or narrow
the verdict. Do not use an artificial objection merely to fill a field. Where the
checked scope is exhaustive, justify that scope rather than inventing an error.
An error outside the bounded claim does not invalidate supported evidence; it must
not disappear when the result is used to support a broader requirement.

Use the five-step evidence discipline: state the hypothesis and source requirement;
construct a genuine competing interpretation; construct or reuse a fixture on
which their predicted outcomes differ; record predictions before actual execution;
retain unresolved contradictions with precise witnesses and a next action. Preserve
FAIL for demonstrated defects, NOT_RUN for unavailable execution and UNKNOWN for
unsettled interpretation. A claim-level HOLD withholds that verdict; it does not
alter project control records or stop unrelated authorized work. Keep the record
concise; no private reasoning transcript or duplicate fixture is required.

Oracle challenges the **test design** (could the wrong behavior pass?), the **source
model** (is the expectation grounded independently of candidate assumptions?) and
the **handoff** (are facts, conditional explanations and unknowns still distinct?).
Inspect shared fixture/reference lineage: agreement between agents or methods
sharing a disputed premise is not independent confirmation.

For example, a clock changing on screen supports a ticking-display claim. It does
not establish that agent activity is fresh. A suitable freshness contrast holds
the agent observation fixed while advancing the clock and refreshing capture;
the claimed freshness must still follow the governing observation rule. A valid
file or successful parser similarly does not establish preserved field meaning.

## Choose the next task from evidence

Use an adaptive sequence, without imposing a fixed agent count or extra ceremony:

Bounded execution → Oracle claim-and-test challenge → next justified task → Oracle
integration challenge → separately required independent review → authorized Owner
acceptance (or the Owner's explicitly scoped acceptance delegate).

| Evidence after the challenge | Next useful assignment |
|---|---|
| The contract is established and important failure modes are adequately tested for the intended decision. | Implement the next bounded feature. |
| The correctness criterion remains disputed, or a consequential error could survive the evidence required for that decision. | Assign suitably independent falsification, preserving actual authorship, exposure and expectation lineage. |
| A defect is demonstrated and the criterion and remedy are established. | Assign the bounded repair and affected checks; do not repeat an already decisive investigation merely to occupy an agent stage. |
| Oracle patches code or changes a candidate's expected behavior. | Treat the patch/premise as contributor work; obtain independently required assessment of affected claims, not an Oracle self-approval. |

Choose the assignment from actual evidence and risk; do not automatically turn the
next agent into either another implementer or another reviewer. Preserve original
requirements, artifacts/revisions, decisions, unresolved alternatives and why they
matter. A speculative diagnosis may travel as a hypothesis or conditional next
test, never as an established instruction to implement its guessed repair.
Integration must be checked against the whole outcome. Technical review, merge,
release and authorized acceptance remain distinct.

Premature convergence and claim inflation are separate failures: challenge the
chosen explanation and also prevent narrow evidence from being promoted into a
broader PASS, even when the implementation happens to be correct.

## Choose useful work

For each material opportunity, compare contributing now with handing it to the next
available agent. State the expected project benefit, why the current participant's
context helps, bounded cost/risk and what the successor would otherwise repeat.
Do not claim superiority to every other agent or measured savings without evidence.

| Priority | Useful basis | Typical contribution |
|---|---|---|
| High ROI | Resolve a consequential ambiguity or remove a blocker using understanding already established; substantial rework or lost meaning is otherwise likely. | Reproduce the failure, settle a source/invariant boundary, implement a small integrated correction, or establish a discriminating validation method. |
| Medium ROI | Carry a bounded adjacent improvement through with modest context/coordination cost and checkable value. | Complete an adapter seam, integration guard, focused regression, or usability correction that makes the handoff usable. |
| Defer | The next agent can do it with the durable brief more efficiently, or this participant lacks authority, fit, validation access or a coherent stopping point. | Routine expansion, bulk polish or a separate unresolved architecture/domain decision. |

Treat High/Medium as prospective judgments, not proof of realized ROI. Record
observed outcomes and available effort separately; causal savings need a comparable
baseline. Do not invent token, time, capability or cost measurements.

Prefer the smallest coherent contribution that improves the real outcome. Include
the production consumer when claiming implemented behavior. Do not substitute
unused scaffolding or a longer plan for authorized execution. Conversely, a sound
diagnosis, reproduction or source decision can be the highest-value deliverable;
there is no code quota and no requirement to perform every medium-priority item.

## Keep authority and independence explicit

- Use already granted task authority. Check actual candidate/base, applicable
  instructions, active claims, write scope and downstream dependencies before
  editing. Do not re-request permission for an authorized reversible contribution.
  A review-only/no-edit assignment still forbids product edits; return the finding
  and prepared repair direction, and seek a scope change only if needed.
- Preserve a selected coordinator/producer separation. An Oracle who is also that
  coordinator routes production work to the producer, unless the Owner/project
  explicitly changes the arrangement. ROI does not waive Gatekeeper or delivery
  policy. Do not silently change hats to bypass a reserved responsibility.
- Disclose becoming a contributor **before editing**. Identify affected claims,
  paths, expected values, tests and integration assumptions. Keep prior review
  findings and their exact candidate intact; do not rewrite them as later approval.
- Treat assessments of your own candidate contribution, including its specification,
  expected answers or tests, as SELF-ASSESSED for the affected claims. Designing a shared
  premise can matter even when someone else types the code. Independence is scoped
  to actual contribution, derivation and exposure, not only changed filenames.
- Do not independently approve your affected contribution. Retain useful local
  checks, state the missing independence dimension, and route any independently
  required assessment to a suitably independent participant under existing policy.
  A fresh chat, role name or shared GitHub account does not establish that basis.
- Reuse an unaffected review only with a stated claim/dependency analysis. Bind
  old evidence to its old candidate; establish applicability to the new candidate
  and relevant integration. Never carry an overall PASS forward by assumption.

Distinguish candidate authorship from authoring independent review evidence.
Writing a diagnostic check against someone else's candidate does not by itself
make that candidate your work. Record the method/expectation derivation and any
candidate repair separately; do not disqualify useful independent assessment merely
because the reviewer wrote its checking script.

If no independent reviewer is available, continue feasible authorized work and
report that limit. Do not invent a reviewer or relabel self-review. This recipe
creates no universal second-review gate; it preserves any review already required
by the actual project and the honesty of claims made to the Owner.

## Make one coherent contribution

1. Recover the purpose, current working explanation and decisive source evidence.
   Separate facts, reported work, hypotheses and unknowns. Keep useful predecessor
   work; do not restart reasoning merely because the executing agent changed.
2. Select a bounded contribution and stopping point. State the outcome, protected
   behavior, discriminating check and what would falsify the explanation. Record
   the High/Medium rationale in the existing work report or equivalent.
3. Produce the usable result within authority. Capture actual inputs, commands,
   observations and exact candidate. Keep validation expectations grounded in
   original requirements; do not change the oracle to match the implementation.
4. Check the affected behavior, a relevant contrary case and integration. Record
   executed versus inspected evidence and NOT_RUN checks. A test count, green CI
   or source inspection alone does not establish browser, domain or acceptance
   claims outside its coverage.
5. Persist a coherent checkpoint with the decision basis and exact continuation.
   Follow the selected protocol's checkpoint/custody rules. If the Owner requested
   a handoff, stop at that boundary instead of taking over the remaining backlog.
   Without such a request, a checkpoint alone is no reason to end authorized work.

## Record the contribution

Use the existing report, decision log, review finding and task/Next Move records;
link them instead of creating a second tracker. Add only missing meaning. Preserve
source-backed conclusions, alternatives rejected with reasons, constraints and
falsifiers. Do not require private reasoning transcripts or the entire chat.

```text
Purpose/source: <Owner outcome, amendments, actual authority reference or UNKNOWN>
Basis: <repository/task, base, exact candidate/input revision; live observation>
Contribution: <actor/session as actually known; advisory/review/contributor scope>
ROI judgment: <High/Medium/Defer; impact, context advantage, bounded cost/risk>
Decision: <chosen approach, decisive evidence, rejected alternative and falsifier>
Change/result: <exact commit/artifact, affected paths/claims; implemented/partial>
Validation: <candidate, actual command/witness, expected/actual, PASS/FAIL/NOT_RUN>
Claim/expectation: <precise PASS scope, requirement/source and expectation provenance>
Challenge: <plausible surviving error, discriminating fixture/predictions and disposition>
Independence: <authorship, expectation derivation, exposure; self-assessed scope>
Remaining: <known defects, missing checks, deferred parent outcomes and dependencies>
Handoff: <starting path, next actor/responsibility and exact next action, stop point>
Next-task basis: <implementation/falsification/integration; evidence and unresolved alternatives>
```

Do not fabricate an identity, source URL or future containing-commit SHA. When a
report follows the implementation commit, name that implementation basis; observe
the live branch head separately. Follow native freshness rules for later changes.
Mark another actor's future work PROPOSED until actual pickup/delivery is observed.
A recoverable checkpoint is not Owner acceptance, release or custody transfer.

## Continue from the checkpoint

Have the incoming coder read the original outcome, compact decision basis, actual
diff and decisive evidence. Refresh live source/head, claims and applicable
authority. Reconcile only material drift; do not repeat a completed investigation
or impose another exam merely to prove that the handoff was read. Existing
project-specific takeover qualification remains applicable where selected.

Continue the named next unit from the established seam. Reopen a decision when
its falsifier, source change or new evidence warrants it; record the correction.
Recheck affected claims on the resulting candidate. A coding successor does not
thereby become an independent reviewer of its own additions or prove integrated
acceptance by inheriting a predecessor's green checks.

For established context, carry this record through the existing Oracle OnBoard
Prompt or native handoff. For an independent assessment, provide original criteria,
exact candidate and necessary safety/model knowledge; disclose prior exposure and
shared derivations. Keep worked answers out of a genuinely withheld-reference
exercise. Preserve any feedback as guidance without claiming blind discovery.
