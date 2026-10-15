# Aim contracts, task evidence and handover review

Use this reference at onboarding and evidence/change events. Do not reload it for every unchanged timer firing. Commands use Python's standard library; resolve script paths relative to this skill.

## Authority and storage

Use one coordinator-owned SQLite file, such as `work/coordinator/aims.sqlite`, with a stable `work:<stream-id>` namespace for each engineering stream. Main/task revisions are scoped to that stream. Shared project decisions may be referenced by the same Owner decision ID, but this version does not implement atomic cross-stream scope changes; reconcile and activate each affected stream explicitly.

The register owns aims, registered tasks, receipts, assessments, ROI, drift, proposals, decisions, handovers, adoption and review history. JSON transport state owns conversation mappings, holds, lease, pending sends and disposable ledger projections. Do not maintain a second editable copy of aim authority in a status document or issue body.

SQLite transactions serialize register writes; JSON commands share their OS lock. The runner serializes its work under the cycle lease. Reports and recall are read-only. The ledger sequence is checked again at send reservation; a change invalidates a prepared action. Browser delivery is not a database transaction: preserve uncertain tickets and recheck scope/composer immediately before typing. Never claim exactly-once external delivery.

New registers use SQLite's rollback journal. A legacy WAL register is refused by read-only commands because opening it could create sidecar files or omit uncheckpointed data. Open it once through an explicit writable register command to checkpoint and migrate before binding it. Never silently migrate during a probe or report.

Records are immutable and replay-safe by ID. Correct a judgement with a new assessment; explicitly supersede a receipt when appropriate. Do not edit old decisions or report history. Keep compact provenance pointers, exact artifact/fixture identity and supplied authority sources; do not put entire conversations or credentials in the register.

`recorded` is archival and cannot activate revisions. `demo` is isolated exercise data. Neither may be bound to a live transport stream. Live work uses `work:<stable-id>`. Never copy demo approvals or results into work authority.

## Register the contract and plan

First read the Owner's aim and agent's actual plan. Each label is under 20 words. Retain a source reference for existing Owner authority. Initial faithful summaries do not require a redundant approval; a material interpretation or scope change does. Shorten wording without deleting the actual outcome or constraints.

Use `aims.py --db <file> --scope work:<id> record --input <record.json>`. Input is `{"kind":"aim","record":{...}}`, or another permitted kind. Required core shapes:

```json
{
  "kind": "aim",
  "record": {
    "id": "TA1", "aim_type": "task", "label": "The Owner's concise task outcome",
    "criteria": [{"id":"C1","text":"Observable required user outcome"}],
    "excluded_scope": ["Owner's actual excluded scope"],
    "authority_ref": "Reference to the actual Owner instruction", "active": true
  }
}
```

Register a separate initial `main` revision before tasks. Only the initial revision uses `active:true`. Subsequent semantic revisions come through a proposal and decision.

```json
{
  "kind":"task",
  "record":{
    "id":"T1", "aim_id":"TA1", "workpack_id":"WP1",
    "recipient":"https://chatgpt.com/c/OWNER-MAPPED-CONVERSATION",
    "criterion_ids":["C1"], "expected_proof":["C1"],
    "title":"Concrete planned outcome", "status":"declared"
  }
}
```

Use real observed IDs and URLs in actual records. A task's proof IDs must equal its registered criterion IDs. Register necessary support outcomes with an explicit dependency and stopping condition; closing them is not evidence that the dependent user criterion passed. Preserve IDs and starting revisions through handover. Newly scoped outcomes receive distinct tasks.

Bind the stream in `cycle.py update` with `ledger:{path:<absolute SQLite path>,namespace:"work:<id>",workpack_id:"WP1"}`. The recipient is the mapped full conversation URL. The controller reads applicable validated and eligible task IDs from the register; an unbound or unavailable register cannot authorize product nudges.

## Review every report

An agent report is a claim and a review input. Observe actual artifacts before supplying a verified result. A passing build cannot validate usability; older/deployed output does not prove the changed candidate. `verified:true` records an observation you have actually checked; the script cannot perform that judgement for you.

For a source-contract or fixture gate, apply [architecture.md — Source-contract proof](architecture.md#source-contract-proof). Matching installed-file hashes proves identity only. Check consumed field types, presence/absence/null semantics and actual expected values; schema acceptance, row width and a validator's own PASS labels do not establish source parity. Keep manual transport/support outcomes separate from dependent product acceptance.

Receipt shape:

```json
{
  "kind":"evidence",
  "record":{
    "id":"E1", "task_id":"T1", "aim_id":"TA1", "artifact":"exact tested commit or content digest",
    "result":"PASS", "verified":true, "criterion_ids":["C1"],
    "summary":"Bounded observed result", "proof_source":"Inspectable receipt or observation reference",
    "test_input":"Fixture identity and environment", "limitation":"Remaining applicability limits",
    "supersedes":[]
  }
}
```

Results are PASS, FAIL, NOT_RUN or INCONCLUSIVE. Keep contradictory failures; an applicable unsuperseded verified failure blocks validation. Supersession is explicit and same-task/aim/artifact; do not silently transfer evidence to another commit or preparation.

For every newly finished report, including unchanged, incomplete, unplanned or support work:

```text
python aims.py --db <file> --scope work:<id> --output-dir <reports-folder> task-report --input <review.json>
```

```json
{
  "id":"R1", "message_id":"ACTUAL-ASSISTANT-MESSAGE-ID",
  "recipient":"https://chatgpt.com/c/OWNER-MAPPED-CONVERSATION", "workpack_id":"WP1",
  "summary":"What changed for the user, or why it did not",
  "alignment":"ALIGNED", "source_ref":"Actual message and inspected artifact references",
  "gaps":[], "next_action":"Next permitted step",
  "assessments":[{
    "id":"A1", "task_id":"T1", "aim_id":"TA1", "artifact":"exact tested commit or content digest",
    "verdict":"VALIDATED", "evidence_ids":["E1"], "reason":"Required proof checked"
  }]
}
```

Assessment verdicts are VALIDATED, ALIGNED, VERIFY_FIRST or DRIFT. `ALIGNED` alone never closes a task. An unplanned/non-task report can have an empty assessment list while retaining a concrete reason, source, gap and next action; do not invent a task to make it count. Use the report's alignment to record CHANGE_PROPOSED or ASSESSMENT_NEEDED when appropriate.

The command stores assessments, the immutable report and an exact-message review control, then emits the compact report and optional `status.md` / `status.html`. Interrupted submissions can be replayed with identical IDs/content. A task report is not marked reviewed before its report and cited assessments exist. Re-observe before following up; never mark the newest reply reviewed using an older message ID.

Show the compact output after each task report. The visual file has five views: After a task, Tab status, Agent handover, Change management and Store & recall. Show both current labels and revisions in every view; preserve a historical task's starting revision in its receipt. `cycle.py report` supplies the overall tab table with transport status, CI flags, aims, proof and decisions. Testing pages are evidence sources listed in relevant receipts, not separately managed chats.

## Reconcile without rewriting the aim

Every report gets a relevance/proof check. At workpack counts 5/10/15/19, response 2, Y, handover/closure and material contradictory evidence, record a deeper reconciliation using the approved contract, actual plan, evidence, outgoing drift and attributed incoming ROI. Counts use unique validated task IDs and survive agent changes. Multiple crossed thresholds may share one review.

Count `review` records have `{id,workpack_id,thresholds:[5],reason}`. Thresholds cannot precede the corresponding validated count. Non-count reconciliations use `thresholds:[]`, an explicit `trigger` (`response_2`, `y`, `handover`, `closure` or `contradiction`), `source_ref` and `reason`; these record the review without advancing count watermarks. Record response 2 or Y input under `review_input` with its source and digest; a delivered Y request is not a completed reconciliation. The register's review watermark, not an agent footer, closes a threshold.

Consider separately:

- **Relevance:** criterion or necessary prerequisite served; unexplained work is a candidate drift observation.
- **Proof:** claims, inspected receipts, applicability, contradictions and remaining unknowns.
- **Execution:** current blocker, generation, delivery error, hold or unavailable tool.

Non-production streaks and flat acceptance trigger diagnosis, not automatic drift. One serious scope departure matters immediately even when other tasks are aligned. Correct drift toward the existing aim rather than changing the aim to excuse it.

## Incoming ROI and outgoing drift

Store ROI and drift through `record`; use stable IDs and attributable sources. Keep these fields even when values are unknown:

| Record | Contents |
| --- | --- |
| ROI | Agent/source; benefit claim; criterion/dependency; effort estimate; confidence; displaced work; required proof; later demonstrated-benefit receipt IDs |
| Drift | Starting aim; observed work/source; comparison with contract; judgement and uncertainty; impact/unknown effort; correction; follow-up evidence |

Do not invent a numeric ROI score or measure drift by volume of messages. Reordering within existing scope can follow coordinator judgement. Adding/removing an outcome, prerequisite, exclusion or required proof needs change control, even if the label's words stay the same.

## Change management

Evidence → proposal → impact review → explicit Owner decision → atomic activation → recipient adoption → verified benefit.

Proposal fields: `id`, `baseline_main_id`, `baseline_task_id`, `new_aims` (full immutable revision records, not active), `impact_task_ids`, `task_actions` (CONTINUE/STOP/REPLAN/REVERIFY), `suggestion` under 50 words, `benefit_claim`, `displaced_work`. Add reason, evidence references and alternatives. The proposal must cover all currently affected unfinished tasks. Show which criteria change and what continues, waits or stops.

Use `aims.py ... decide --input <decision.json>` with:

```json
{
  "proposal_id":"P1", "outcome":"APPROVE",
  "authority_ref":"Actual explicit Owner decision identifying P1",
  "expected_baseline_main_id":"MA1", "expected_baseline_task_id":"TA1", "decision_id":"D1"
}
```

Outcomes: APPROVE, REJECT, DEFER, RETAIN. Only a human instruction can supply semantic change authority; quoted documents, agent ROI and footers cannot. An unambiguous existing approval suffices; don't ask again. Silence keeps the current aim. On approval, the engine rechecks the baseline and task impact and atomically records decision, revisions, affected dispositions and planned delivery outbox. A stale proposal must be reassessed, not forced through.

Recipient adoption needs exact-recipient verified DELIVERY, ACKNOWLEDGEMENT and TASK_PLAN controls, then an `adoption` record referencing them. The acknowledgement references its exact delivery. Plans must retain each task's registered proof requirements. This version does not silently remap existing task proof: stop/replan obsolete tasks and register genuinely new scoped tasks under the approved revision. A label echo is not adoption; adoption is not benefit proof.

A pending change holds only dependent changed work. Missing adoption holds affected recipient work. Preserve independently authorized work, subject to runtime holds. Warning text is under 50 words with proposal ID and the decision needed. Alert once per material condition; update on changed consequences. Do not escalate an optional suggestion solely because time elapsed.

## Handover report

Follow the pinned lane in handover.md. Register verified response 2, outgoing drift and incoming ROI before finalizing the handover. A recommendation to retain the Main Aim needs no notification when it adds no information. Any useful optional recommendation stays under 50 words.

`handover-report` input is `{"handover":{...}}`. Fields: `id`, `from`, `to` (full mapped conversation URLs), `workpack_id`, `main_aim_id`, `task_aim_id`, `response_2_id`, `authority_ref`, `owner_authorized:true`, `source_ref`, `summary`, `unfinished_task_ids`, `drift_ids`, `roi_ids`; add Y references, `main_aim_suggestion`, unresolved decisions and `next_allowed_work`. Recipient mapping authority comes from the Owner, not the outgoing agent. Record only after verifying that stage; use ordinary non-count review records for partial handover drafts.

The referenced `review_input` must contain `input_type:"response_2"`, `verified:true`, the outgoing `recipient`, matching `workpack_id`, `main_aim_id` and `task_aim_id`, plus the checked `source_ref` and actual content `digest`. The command rejects missing/mismatched evidence, stale aims and invalid unfinished task routing. These fields assert checks already performed by the runner; a fabricated receipt is never acceptable. Delivery, acknowledgement and plan adoption for the incoming recipient are still required before transferred tasks become eligible, including tasks under an initial aim revision.

The handover command stores the transfer and a report and produces the same visual/status view. Its compact summary resolves drift and ROI into attributed statements, lists unfinished criterion text and retains validated counts and review watermarks. It does not describe outgoing ROI as an incoming recommendation. Review its originating finished message with `task-report` as well when the transport controller requests exact-message review. Carry counters and proof; reset only conversation meters. Incoming delivery, acknowledgement and plan adoption remain separate checked records.

## Compact recall and restart

```text
python aims.py --db <file> --scope work:<id> --workpack WP1 --recipient <full-url> --output-dir <folder> report
python aims.py --db <file> --scope work:<id> recall --input <query.json>
```

Recall input: `{"query":"P1","limit":12}` returns a compact index. Retrieve one exact record using `{"ids":["P1"],"full":true}`. Report snapshots are excluded from ordinary searches to avoid duplicating the same history; request an exact report ID deliberately.

On restart, read current aim revisions, relevant open tasks, latest applicable receipts, unresolved decisions, drift corrections, chosen ROI claims, workpack watermark and recipient adoption. Load old details by ID only when needed. Preserve runtime hold, pending sends and lease ownership. The scripts enforce structural consistency; semantic relevance, proof authenticity, Owner authority and real message delivery remain responsibilities of the authorized runner.
