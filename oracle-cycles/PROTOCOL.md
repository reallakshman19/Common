# Oracle Cycle — GitHub-first standalone relay

Version: 0.1.0 DRAFT · Applies only when explicitly selected · No OTM

## Contract in one sentence

**Owner speaks to Oracle; Oracle publishes one authoritative next assignment;
Owner prompts the intended participant with one line; participant reads current
GitHub instructions, executes and posts a verifiable return receipt; Oracle
reconciles evidence and proposes the next state plus Progress Page projection.**

The trigger **does not** wake other chats or run in the background. GitHub
comments do not mutate assignments automatically; a published revised
`CURRENT.json` does. Without a real GitHub-accessible actor, use the stated
private Drive fallback and label the missing verification.

## 1. Discovery and one-line grammar

First-time/cold chat:

```text
Cycle now: https://github.com/reallakshman19/Common/tree/main/oracle-cycles/<project>
```

Established conversation that has already read, verified and retained the
project locator and its own role:

```text
Cycle now
```

If the chat lacks either the locator or role binding, it **must not guess**
a task from the phrase alone. Ask for or use the URL form. If the URL points
to a draft branch, the agent may inspect a proposal but must not treat it
as the activated live assignment.

On every invocation, the **recipient**:

1. Open the actual `CURRENT.json` at the provided folder on `main`
   (not a cached chat paraphrase). Read this protocol and only the task's
   links/fixtures necessary for safe execution.
2. Check `mode=standalone`, `activation=ACTIVE`, schema, revision,
   assignment identifier, role, the Owner-supplied short chat ID,
   responsibility and current artifact. Read any open relay issue
   receipts needed to avoid duplicating completed work.
3. **If not assigned:** reply briefly “NO ACTION — next is <role>”,
   with current state revision. Do not invent a new task or modify files.
4. **If assigned and a new bounded action is authorized:** verify actual
   access/authority and candidate identity, perform only that action,
   retain native self-test/negative-test evidence, then post a redacted
   `ORACLE-CYCLE-RECEIPT v1` to the configured `receipt_issue_url`.
   For work already returned, or a missing receipt, follow the
   **lightweight continuation** exception below instead of re-execution.
5. Fetch the actual comment URL/readback and return that permalink,
   artifact identity, executed checks, limitations, and next suggested
   action. If GitHub is inaccessible, follow §4 and explicitly label
   `FALLBACK_NOT_POSTED`.

### Lightweight continuation — already bound participants

A **new recipient** with no verified project locator/role grounds the assigned issue, relevant WBS/Home and actual original inputs. For an **established recipient** whose project locator and role were previously checked, `Cycle now` means **refresh current assignment → compare changed evidence → continue the next authorized bounded action**, not rebuild the complete project model.

Each invocation still reads fresh canonical `CURRENT.json` on `main` and checks `mode=standalone`, `activation=ACTIVE`, revision, assignment ID/generation, intended recipient/role, current candidate, limits and engineering HOLDs. Read the **latest relevant** issue/native evidence and Cycle receipt (including `receipt_id`/accepted IDs) before acting. Compare source/candidate, authority, access, task status and receipt with the last verified working state; reopen **affected** originals/WBS/Home/relay records only where changed, newly consequential or contradicted. Prior understanding can be reused; **previous access is never a substitute for a required current original-file/byte check**.

- **Unassigned/wrong recipient:** `NO ACTION`; **inactive Cycle:** `NOT ACTIVE`. A one-line trigger creates no task or engineering PASS.
- **Already returned with no new authorized action:** do **not** rerun or post another completed-work receipt, even if the stale assignment still appears active. Report **AWAIT_ORACLE_RECONCILIATION** with the existing native evidence and published receipt permalink; only the Oracle may reconcile/publish a subsequent assignment.
- **Native return exists but required Cycle receipt is absent/unposted:** inspect the configured receipt inbox and accepted receipt IDs. Repair the *missing routing envelope*, using v1's existing revision/idempotency/readback rules and referencing **the same native evidence**; do not rerun engineering. If publication is inaccessible, report `FALLBACK_NOT_POSTED` and the actual blocker, not a fabricated GitHub receipt.
- **Changed generation, recipient, authorization, candidate/original bytes, lost access or contradiction:** recheck affected sources/authority/fixture identity and required native qualification; full onboarding only if the prior grounding is no longer applicable. A task can remain `BLOCKED` or `NOT_RUN` despite an unchanged candidate SHA.

The Oracle owns the **Home → WBS → issue** task choice, purpose, source/fixture and Common [artifact relay](../skills/agent-work/ARTIFACT_RELAY.md) locator, one plausible wrong case, limits, native evidence target and next consequential dependency. The recipient follows **assigned issue → relevant WBS → Home as needed**, then reads/checks the actual authorized relay input and uses its **selected native protocol**. The recipient reports contradictions rather than independently replanning the roadmap or becoming a second Nudge Designer. All of these rules apply **only to an activated standalone Cycle**, not OTM/native dispatch by default.

### Cycle receipt is a routing envelope, not duplicate engineering evidence

Keep **every field, action value, revision check, idempotency rule and readback** of `ORACLE-CYCLE-RECEIPT v1` unchanged. Point `public_evidence` to the actual native child issue/`TASK_EVIDENCE`/PR/commit/reviewer result; scope `result`, `limits` and `next` precisely. Do not paste full test logs, A14 SELF-CHECK narratives or implementation descriptions into the Cycle receipt. Actual **input/output bytes and verified custody** belong to the separate [Common artifact relay](../skills/agent-work/ARTIFACT_RELAY.md); project state belongs to canonical `CURRENT.json`; Progress Page is Oracle-reconciled projection. The Oracle reads native evidence before updating an assignment or the Page. A linked claim, digest, received file or readback is **not** technical PASS, independent review or Owner acceptance.

For **Oracle**, Cycle now additionally means read the full issue inbox
since the last accepted receipt, reconcile new returns with the
current task, current model/revision, protected invariants and Owner
decisions, update the Owner-facing routing board, and choose one
authorized continuation. On an actual connected checkout, use
`pp_cli.py` to propose Progress Page updates; otherwise show
`PROGRESS_UPDATE_PENDING` and do not claim a live update.

## 2. Responsibilities and boundary

| Role | May do | Must not infer |
|---|---|---|
| Owner | Discuss aim, choose scope/participants, paste one-line trigger, approve acceptance and merges | A message sent proves ZIP read |
| Oracle | Maintain aim, active assignment, task/gate evidence, reconcile receipts, propose state and Progress Page update | An IR “PASS” for a narrow test means release |
| Coder | Read own assignment, verify exact inputs, implement permitted repair, post artifact receipt and own tests | Self-test equals independent verification |
| Reviewer | Read exact artifact, check source/fixture independence, post scoped findings and NOT_RUN | Different chat ID proves independence |
| New agent | Bootstrap from the URL, respect role assignment, return a receipt or NO ACTION | “Cycle now” alone discovers a repository |
| GitHub | Durable public-safe state proposal/revision, append-only issue transport and reviewable PRs | Signed identity for a browser chat |
| Drive | Private artifact bytes and restricted verification manifests | Delivery, acceptance or consent to publish |

Chat IDs are **display routing labels**. A GitHub authenticated user identity,
where available, is evidence about who posted a comment, not proof that the
named ChatGPT conversation acted. The receiver's declared role/id is
checked against `CURRENT.json` but is not an access-control mechanism.
Never grant repository writes, private Drive access or engineering approval
solely because a comment claims the right role.

## 3. One canonical state + one inbox

`CURRENT.json` in the project folder is the **sole current snapshot**.
It contains:

- `revision` (monotonic), `activation`, Owner's aim and exact
  protected invariants;
- `chats` with role/short display IDs and provenance;
- `active_assignment` with id, generation, role, scope, prerequisites,
  current candidate identity and expected return;
- `gates` with bounded claim, evidence type, last observed receipt and
  PASS/FAIL/BLOCKED/NOT_RUN status;
- `receipt_issue_url` and accepted `receipt_ids`;
- `progress_projection` including desired project key and last
  **actually observed** published revision (or PENDING).

No full chat URLs, private Drive file links or credentials in public
`CURRENT.json`. Do not duplicate authority in README or stale
handwritten “current status” docs. `CURRENT.json` is a proposal until
merged to the authorized canonical branch.

The **one dedicated GitHub issue** is an append-only transport inbox,
not a competing status tracker. Each worker comment begins:

```text
ORACLE-CYCLE-RECEIPT v1
project: <slug>
receipt_id: <globally unique per attempted return>
assignment_id: <exact assigned id>
observed_revision: <CURRENT.json revision at start>
role: <coder|reviewer|oracle|owner>
chat_id8: <Owner-reported display ID>
action: <received|bytes_checked|work_returned|review_returned|blocked>
candidate: <opaque version, public-safe>
result: <PASS|FAIL|PARTIAL|BLOCKED|NOT_RUN; precise scope>
public_evidence: <safe GitHub link or NONE>
private_receipt: <opaque private token or NONE>
limits: <brief contrary/untested cases>
next: <recommendation, not authority>
END-ORACLE-CYCLE-RECEIPT
```

A worker should **not** post private manifest text, full source model
labels, customer names, raw approvals, signatures, complete browser chat URLs,
Drive child-file URLs or private ZIPs in the issue. Use opaque tokens and
private Drive evidence. A returned comment is **self-reported content**
unless Oracle independently verifies the concrete claim. Readback of a
comment confirms its presence only.

The Oracle uses the pair `(project,receipt_id)` as an idempotency key.
If identical comments are retried, do not double-count; if the same key
has inconsistent content, stop that receipt and investigate.
`observed_revision` lower than current is **stale** unless Oracle
explicitly adopts the return without overriding newer evidence.
Comments on future revisions or unrelated assignments are quarantined.
A reviewer comment never silently changes a coder's assignment or
promotes Owner acceptance.

**Publishing a new current state:** Oracle reads current `main` HEAD,
reconciles evidence/Owner authority, proposes `CURRENT.json` changes
on a dedicated branch/PR, checks the preimage again, and obtains the
repository's authorized merge. Concurrent proposals cannot silently
overwrite state; reread/resolve if canonical HEAD or state revision moved.
No automatic merge, unconditional force update or self-granted acceptance.

## 4. GitHub first, Google Drive for restricted artifacts/fallback

Prefer public-safe GitHub **text and receipts**. Store private ZIPs,
customer models, screenshots with identifiers, executable evidence and
private manifests in the Owner's authorized project subfolder under
**Handoffs** on Google Drive. A recipient must check actual ability to
read and download the bytes; “the folder exists” is not an access test.

After downloading, recipient computes actual SHA-256/size and ZIP
integrity, compares against the expected private receipt, and records
whether input identity is VERIFIED, MISMATCH or NOT_RUN. A coder-provided
hash is REPORTED until recipient independently checks it.

If the GitHub issue cannot be accessed or commented, a recipient may
save a private `FALLBACK_RECEIPT` in Drive and send the Oracle
the opaque reference via the permitted private channel. Until Oracle
can read it, public state is PENDING. When/if it later becomes possible,
Oracle can add an explicitly labeled reconciliation event; it must not
backdate a GitHub receipt or claim the participant posted it.

Drive folder URL disclosure on a **public** Progress Page requires
an explicit project-specific Owner policy check. Progress Page PR #8
introduces an optional folder-only exception, but a draft PR does not
activate it. Publishing a folder link does not change Drive permissions
or imply that child files are safe to expose.

## 5. Progress Page projection — no second tracker

`CURRENT.json` and accepted receipts define the working meaning.
The Progress Page displays the same **role ID8 + bounded current state +
one next actor + gate evidence**. It does not hold private files and
cannot upgrade reported facts to verified facts.

The Oracle proposes `pp_cli.py plan chat`, `card set`,
`fixture add` and only genuinely necessary other operations for a
separate `p25b` standalone project; do not alter legacy
`ciifr` tasks. Each CLI write has `--actor`, an allowed
`--src` (a safe GitHub comment link or `OWNER_PRIVATE_REF:<token>`),
and a reason, and appends the site's existing audit event.
Run `python tools/pp_cli.py check` and `check --base origin/main`.
Updates require a real checkout/authorized executor and a published
PR/merge. `PENDING` remains explicit if tooling or approval is absent.
This protocol itself does not install an automatic GitHub → Progress
publisher.

## 6. Fast Oracle answer after every invocation

Render the Owner's next useful view, not raw JSON or a long status report.

```text
ORACLE CYCLE — <project> · canonical revision <n>
Oracle [id8]   · owns meaning       · <status>
Coder  [id8]   · owns artifact      · <status/evidence limit>
IR     [id8]   · owns review        · <status/evidence limit>
Owner          · acceptance         · <status>
NOW → <single role and short chat ID>
PASTE → Cycle now
RETURNS → <exact receipt/artifact/decision expected>
BLOCKS → <one or two live blocking criteria>
PAGE → <published revision or PROGRESS_UPDATE_PENDING>
```

If the next actor is an **unregistered/cold chat**, display the full
one-line URL form instead. If no Owner action is required, say
“No additional message or attachment needed” rather than
fabricating an automatic send.

## 7. Required falsification before calling the pilot operational

- An established agent's identical assignment/recipient/generation/candidate continues **without redoing full onboarding**, after relevant current source/authority/access and receipt checks.
- Work already returned, while `CURRENT.json` remains active with no newly authorized step, yields `AWAIT_ORACLE_RECONCILIATION`, not duplicate execution or a second receipt.
- A missing/unposted Cycle receipt for actual native work is repaired by the existing v1 idempotent receipt/readback contract, **without** repeating native execution.
- Candidate/assignment-generation/authority drift or loss of source-file access at the **same SHA** causes targeted requalification, never a stale-access PASS.
- The routing envelope points to complete native issue/PR evidence (and separate Common relay custody); logs and self-check text are not copied into it.
- A previously sent instruction displays **No additional paste required**, not another dispatch.
- “Cycle now” to a cold unregistered chat cannot assume a folder.
- Wrong role/short ID, inactive project and missing capability return
  **NO ACTION/BLOCKED**, not work.
- Duplicate or conflicting receipt IDs cannot advance state twice.
- Stale revision and old candidate returns remain historical.
- No ZIP hash is VERIFIED from a filename, uploader report or manifest.
- A mock/injected-browser PASS does not establish native Windows PASS.
- A new artifact does not inherit the old artifact's final review PASS.
- GitHub issue receipt does not automatically mutate state or Progress.
- No private Drive file URL leaks into GitHub/Progress public content.
- Two concurrent Oracle proposals require explicit head/revision
  reconciliation, not a silent force push.
- Unmerged draft state/Progress change is described as **proposed**.

## 8. Non-negotiable current engineering guardrails

When applied to the P2.5-B pilot: preserve frozen P2.1 code byte-for-byte;
do not silently approve ambiguous engineering correspondence; reject
stale approvals and mixed nonuniform source values; distinguish Preview
from Apply; retain independently bounded evidence; native Windows
acceptance and Owner authority remain outstanding unless verified.
No P3 assignment arises from a cycle command.
