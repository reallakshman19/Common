# Standalone completion: source-bound A14 before DONE

Use this within **engineering-pr-delivery-v3.6**, only when the Owner selects
`mode: standalone`. It adds a completion method to the existing native lifecycle.
It has no dependency on another skill, Oracle, coordinator, tracker, shared
registry, Independent Review or Nudge Designer. Optional adapters may help with
a difficult task; they do not become required roles or grant permission.

Contents: [Use](#use), [Checklist](#common-checklist), [Record](#native-record),
[Helper](#optional-local-helper), [Example](#worked-application), [Limits](#limits).

## Use

A short invocation is sufficient:

> Use engineering-pr-delivery-v3.6 in standalone mode only. Complete this task
> against my original intent; apply its standalone completion checklist before
> claiming DONE. Keep uncertainty and remaining work visible.

1. Read the original task and effective Owner amendments. Select the actual
   standalone label, bound plan/task and own child. Reuse clear existing Owner
   authorization and confirmed criteria; do not ask for confirmation again.
2. Identify what this bounded task must deliver, its preserved behavior and
   source references. Keep the wider aim visible. Do not narrow acceptance to
   whatever a patch happens to pass. Retain the frozen source and its byte digest.
3. Execute the task with suitable tests/observations, including a discriminating
   negative case. Before DONE, inspect the actual result against each criterion
   and the common checklist below. Resolve evidence gaps or report them honestly.
4. Publish the **native SELF-CHECK v1 first**, on the real own-child issue.
   Link it inline from the native `For the user:` field, keep the eight-line
   receipt unchanged, and retain the terminal LOG. Read back published records.
5. Report bounded-task DONE only when its applicable obligations are met. Keep
   actual Owner acceptance, merge and any required product qualification separate.
   A separate future issue may remain open; a necessary task obligation cannot
   be moved there to make this task look done.

A missing resource prevents only the claim/action that depends on it. Continue
independent useful work. A blocked report gives the attempted action, observed
restriction, affected scope and smallest feasible next action. Reconstruction,
a plan or a published receipt is not execution of the proposed continuation.

For cold continuation, retain the standalone invocation and re-read the actual
label. Existing generic packets omit mode, and scoreboard actor text can say
coordinator; neither creates that role in standalone. The available Owner/agent
handles the applicable responsibility under existing authority. The packet's
generic acceptance reminder does not make an optional reviewer compulsory.

## Common checklist

For each group, write **what you checked, expected versus observed, the witness,
and what would overturn the conclusion**. Reuse one concise evidence report for
several groups where appropriate. Rows represent an assessed obligation, not a
word count, score or claim that a tool executed merely because it was mentioned.

| ID | Question to answer before DONE | Evidence that can change the conclusion |
|---|---|---|
| SC_INTENT | Does the delivered result serve the original bounded task and wider Owner aim? | Original request/amendments; criterion-to-result mapping; any drift or excluded outcome |
| SC_INPUTS | Did the task use the right original inputs, versions and authority? | Actual source/file revision and hashes where material; synthetic/private/missing limits; artifact/reference provenance |
| SC_SCOPE | What changed, and was the granted scope respected? | Actual diff or produced artifact; protected behavior; preserved earlier contributions; outside-scope findings |
| SC_FLOW | Does the real consumer receive the intended result? | Input → function/decision → output → consumer; original UI journey or output inspection where applicable; integration exclusions |
| SC_TESTS | Which applicable checks ran, and could they reject a plausible wrong result? | Commands, environment, exact tested SHA, before/after results, negative case, failures/skips/NOT_RUN; inspected test oracle |
| SC_CODE | Are the applicable A13/code-quality obligations met? | Changed file counts, cohesion, reuse, function deviations, source review; for non-code tasks, explicit stage applicability |
| SC_PENDING | Is any known obligation necessary for this task still unresolved? | Issue/criterion reconciliation; each pending item's owner, next action, dependency and effect on DONE; new issues/improvements |
| SC_FRESHNESS | Does this claim still describe the current task, sources and candidate? | Plan/label/criteria identities, tested candidate versus current local/remote head, scope/source changes and affected rechecks |

Include **one additional Done-when row per frozen criterion**, using its exact
AC/K/J identifier. No missing/duplicate IDs or silent waivers. Keep the original
source accessible instead of retyping quotations into restricted native fields.

Choose checks from the task, not a fixed list of tools. UI work needs observation
of the real route and interactions; a source assertion alone does not prove the
visible journey. Calculation work needs justified givens/model and a meaningful
contrast; correct arithmetic alone does not validate the model. Documentation or
investigation work needs source/output checks, not invented future code tests.

For a group without an applicable implementation requirement, explain the actual
stage and inspect that boundary (e.g. read-only investigation, no code changed).
MET means the **assessment** and its applicable obligations are supported. It must
never conceal an unrun required test. Unmet frozen criteria stay NOT_MET,
NOT_RUN or UNKNOWN. A justified scope exclusion needs its attributable basis.
Do not invent a JUDGMENT criterion just to satisfy a scoring tool.

## Native record

Start with [the native template](../templates/standalone-self-check-v36.txt).
It is the existing `SELF-CHECK v1`, with stable checklist IDs and file witnesses;
it is not a second task receipt. The existing native reader can consume it.
Replace every uppercase token; retain real pending items or use `Pending: none`.
Add every exact frozen criterion ID. Never publish the unfilled template.

For human use, evidence can use ordinary pinned sources and durable locators.
The optional helper below expects a precise witness-file syntax for each row:

```text
Done-when: SC_FLOW → MET ; proof: evidence/flow.txt ; sha256: FULL_64_HEX
Done-when: AC1 → UNKNOWN ; reason: original fixture unavailable ; proof: NONE ; sha256: NOT_AVAILABLE
```

The second row cannot support DONE. For PARTIAL/BLOCKED/FAILED, use the same
native A14 format with truthful states and pending items; this helper deliberately
checks only proposed DONE. Publish an honest blocked report without waiting for
a successful helper result. No fixture or fake canonical test count is needed.

The `Basis` binds the plan, selected label, confirmed frozen criteria bytes,
exact candidate and original source. The confirmed digest must come from the
retained confirmed snapshot. Rehashing a rewritten file is not confirmation.
Hash **file bytes**; do not normalize newlines or silently strip a BOM.

For example, compute a witness digest locally:

```bash
python -c "import hashlib; from pathlib import Path; print(hashlib.sha256(Path('evidence/flow.txt').read_bytes()).hexdigest())"
```

**SELF-CHECK v2 remains an optional scoring view**, not the native companion.
Do not replace v1 with v2 or append v2 lines to v1. Existing v2 scoring limitations
remain unchanged, including its no-JUDGMENT vocabulary mismatch. The standalone
completion route does not depend on the score, C1 CI discovery or team mirrors.

## Optional local helper

From the Common checkout, substitute the actual values:

```bash
python skills/engineering-pr-delivery-v3.6/scripts/standalone_done_v36.py \
  --label /PROJECT/relay/AIM/WORK.yaml --plan /PROJECT/plan.yaml \
  --task-id V36-1-WP1 --issue-ref owner/repo#2 \
  --candidate owner/repo@FULL_40_HEX \
  --criteria /PROJECT/frozen.txt --criteria-sha256 CONFIRMED_FULL_64_HEX \
  --self-check /PROJECT/selfcheck.txt --repo /PROJECT \
  --evidence-root /PROJECT
```

Use shell-appropriate line continuation (`\` in Bash, backtick in PowerShell),
or paste one line. Python/PyYAML and Git are the existing module prerequisites.
No CI workflow, additional dependency, provider credentials or network is needed.
The helper is optional; the evidence-based pre-DONE assessment is the requirement.

It refuses coordinator/default-mode labels before reading the plan, Git or proof
files. It checks the exact row inventory, basis and candidate bindings, native
format, local HEAD/clean tracked tree, pending blockers and witness hashes.
It reads witnesses only inside the explicit evidence root, without following an
escaping symlink. Witnesses can be untracked reports produced from the committed
candidate; they must be retained and published appropriately afterwards.

Exit 0 means the **structured declaration and local bytes** passed these checks;
`owner_accepted` stays false. Exit 1 lists gaps; exit 2 reports invalid inputs.
Preserve the output, actual files and publication links as traceability evidence.
Before publishing, separately compare the real PR head with the assessed commit.
After publication, use the existing native snapshot/read model for provider
identity, child linkage and current PR evidence. Local verification cannot attest
that those provider checks happened. Do not present a local path as a successor-
accessible source; publish permitted evidence and read it back.

## Worked application

Owner: “The selected file should give a word count; a missing file must give a
clear error. Keep the existing output format.” The task is one CLI repair.

The agent preserves the Owner's source, records the original file bytes and
baseline, writes a failing behavioral test, implements the authorized fix and
runs the full applicable suite plus the missing-file negative case. Its flow
witness names the CLI entrypoint, parser and stdout consumer, and records the
actual command, expected single-number output and observed result at the commit.
It traces the protected format to the original instruction and actual diff.

Its A14 record has all common groups, each frozen criterion and real witness
hashes. SC_TESTS says “local Python run; no CI” if that is the actual environment.
An unrelated wording improvement is retained as a nonblocking pending proposal.
A still-broken required empty-file case makes the task PARTIAL, even if every
other check passes. A passing local helper does not resolve that semantic defect.
The Owner's eventual review/merge stays separate from the coding result unless
it was explicitly included in that task's frozen done-when.

The local regression fixtures exercise this native record, absent CI, no JUDGMENT
items, witness tampering, changed criteria/candidate, missing rows and partial
obligations. They are constructed cases, not a live application acceptance pilot.
The [fresh documentation application](../tests/evidence/standalone-completion-2026-10-19/RECEIPT.md)
retains actual source inputs and a PARTIAL return despite an all-MET author record
passing the structural helper. It demonstrates one use, not agent qualification.

## Limits

A checklist with all MET can still be wrong. Read its witnesses: does the negative
case distinguish the intended result from a credible failure? Was its expected
answer independently justified? Was a generated artifact copied from its judging
reference? Earlier context is exposure; self-review remains self-review.

The helper deliberately does not interpret prose, authenticate Owner confirmation,
execute tests, decide engineering truth or establish an independent reviewer.
Use task-appropriate stronger judgment when required; correct bounded evidence
from a narrower agent remains useful. No fixed reviewer count or automatic model
upgrade is introduced. A distinct reviewer is needed only under the actual task's
requirements; a missing optional participant is not a new workflow blocker.

All existing coordinator runtime scripts, mode defaults, native formats,
publication behavior and review rules remain unchanged. Use MODE_COORDINATOR.md
when that mode is selected; never apply this standalone extension to it.
