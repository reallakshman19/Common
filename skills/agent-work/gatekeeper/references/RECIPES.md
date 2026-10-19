# Recipes for less common situations

These recipes give the how-to behind rules stated in [SKILL.md](../SKILL.md). They
add no new rules.

## Verification routes 3 to 5

Use these when neither a fresh participant nor coordinator review is available
([verification routes](../SKILL.md#verification-routes)).

**3. Separate session via the Owner.**
- Give the Owner one paste-ready bundle containing:
  - the verifier brief;
  - the exact files, or their paths, with shas;
  - the sealed targets;
  - the baseline.
- Leave out your history, notes and verdict.
- The Owner pastes the bundle into a fresh chat and returns the reply unedited.
- Label: VERIFIED (separate session).

**4. Owner spot-check.**
- Name the two or three sections most likely to be wrong, and what to compare in
  each, so the Owner can check them in minutes.
- Label: VERIFIED (spot-check: named sections).

**5. Minimum self-review.**
- Re-derive the decisive counts from the files alone, by a different method from
  the one used to produce them, without earlier notes.
- Rerun the seeded defects.
- Name the plausible wrong result this review could miss.
- Label: DRAFT · CHECKED (SELF-ASSESSED).

Each route's result can be shown to the Owner the same day, under its label.

## Source defects

When the content source itself looks wrong (a factual error, a contradiction, a
broken figure), don't fix it silently and don't drop it from the fidelity check.
- Record a HYPOTHESIS with the exact sentence and your reason.
- Ask the Owner, or the source's owner, alongside your other questions.

Until the answer arrives, either reproduce the sentence verbatim with a visible
note, or apply a correction listed in an errata note. In both cases, list the
sentence as a named exemption in the fidelity check, and qualify the label, for
example "1 source sentence under query". The answer (A1) settles it. Other work
continues meanwhile.

## Offline Owner

When work is ready and the Owner is away, leave one message containing:
- a private DRAFT preview;
- the label with its scope;
- the deviations;
- any release code;
- the open decisions.

Then continue other work. When the Owner returns, recompute the shas (GK9) before
releasing. Only the release, or another action that needs the Owner, waits.

## Displays that read the claim block

These are optional. None of them is evidence; the claim block and its links are.
- **GitHub issue labels:** `gk:draft`, `gk:checked`, `gk:verified`, `gk:released`,
  `gk:deviation` and `gk:override`.
  - Anyone with write access can set a label.
  - If the labels can't be created, skip them.
- **A dashboard**, such as a coordinator landing page, shows one chip per work
  order, taken from GK-LABEL and linked to the block. If it can't parse a block, it
  shows "label unknown", never a stronger label.
- **A packet tool**, such as a nudge tab, uses the channel's comment id as the
  packet id. When it records a return, it captures the return link and output sha
  for GK-EVIDENCE and GK-SHA.
