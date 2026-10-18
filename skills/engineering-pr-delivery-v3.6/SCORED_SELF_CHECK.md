# v3.6.1 · Frozen criteria and scored SELF-CHECK v2

The Owner freezes **CRITERIA v1** from the actual initial issue/prompt
before implementation. Its header identifies the source issue. Each row
has a stable ID, class (MUST / CONSTRAINT / JUDGMENT), literal quoted
source words for AC items, an arrow and an observable measure. A final
count line specifies the 10/4/1 inventory in #430's frozen example.
**Never quietly rewrite the criteria to improve a score.** Any later
amendment needs its own attributable Owner decision and new freeze.

Use `scripts/criteria_v36.py` to parse, or the scoring CLI to include
its result. `source_coverage` counts traceable, declared source clauses
(e.g. 15/15), **not** an independently verified word-for-word match to
the actual upstream issue; the Owner checks fidelity to the prompt.
`tests/fixtures/V36-430-FROZEN.criteria.txt` is the **real frozen**
#430 sample. It is not a universal project rubric.

## SELF-CHECK v2 format

An unambiguous standalone v2 companion has exactly one line for **each**
frozen ID, including the human JUDGMENT. Example (abridged; a valid
record must include every criterion from its frozen source):

```text
SELF-CHECK v2 · TASK-ID · owner/repo#123
Basis: CRITERIA v1 · source #123 body · candidate owner/repo@<sha40>
Criterion: AC1 → MET · proof: exact-head test/diff reference
Criterion: J1 → UNKNOWN · proof: Owner readability decision pending
Score: 1/1 · claim: PARTIAL
Proposed claim: PARTIAL · reason: Owner review pending
```

A full companion reports the machine-checkable count only. A MUST or
CONSTRAINT earns one point only for MET with a nonempty proof statement.
A JUDGMENT is recorded but is **not** machine-scored; it never becomes
Owner approval through arithmetic. Missing, extra, duplicated or
unparseable criteria block the scored check.

The native SELF-CHECK **v1 stays valid**. The read-only
`scripts/selfcheck_score_v36.py` compatibility reader accepts the
actual #409 v1 companion, including its annotated task header, while
retaining the original parser's nonconformant and unresolved flags.
It never silently upgrades a v1 companion to scored v2. The current
native evidence parser, eight-line TASK_EVIDENCE and terminal LOG
remain unchanged; v2 scoring is a **separate, optional verification
view** and not a new task completion record or the team's NextMove.

## Recompute from inputs, not an agent's reported score

```bash
python scripts/score_v36.py \
  --criteria frozen.txt --self-check selfcheck.txt \
  --before base_tests.json --after head_tests.json --diff diff.json
```

The before/after JSON documents `run`, `passed` and exact `sha`.
The diff JSON supplies `paths`, `allowed_paths`, `removed_tests`
and `test_first`. The evaluator recalculates count, test-suite
integrity, candidate head identity and whether changed files stayed
in approved paths. A false DONE, altered score, failed tests or
out-of-scope diff results in **qualified=NO**, a nonzero exit and a
single-line report. Even a positive result is only
`claim=PARTIAL, owner_accepted=NO` when J1 is open.

Inputs are **supplied local observations**, not authenticated provider
attestation; the non-doer/Owner checks CI run IDs and actual Git diff
before acceptance. The tool performs no network calls or writes.
Record all NOT_RUN and gaps in the human SELF-CHECK. Native approval,
independent review and the Owner's release decision remain separate.

The plan task may add a nonempty, unique list `criteria:` alongside
its existing single `acceptance:` sentence. Older plans without the
list remain valid. Do not use a list to narrow existing acceptance.
