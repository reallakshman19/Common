# Walkthrough: one deliverable, end to end, in both modes

This file contains worked answers. Withhold it from a participant whose fresh use
of the guidance is being tested.

## Contents

- [The deliverable](#the-deliverable)
- [Coordinator mode](#coordinator-mode)
- [Standalone agent mode](#standalone-agent-mode)
- [Where each blocker lands](#where-each-blocker-lands)
- [How this guidance was tested](#how-this-guidance-was-tested)

## The deliverable

Both walkthroughs use the same real request, in a Grade 9 physics suite. A learner
suite already exists (the *master*). It contains Core 1A lessons, Core 1B recall
and reconstruction, and 39 Core 2 questions. Thirteen new questions passed review
in a separate pilot. Each question has a stem, four options, a key and a reviewed
worked reason. The Owner wants a v2 suite: the master plus those 13 questions,
with nothing else becoming less complete.

The coordinator-mode run is real: work order WO-001, with packets and returns on
[Grade9v3.5 #300](https://github.com/reallakshman19/Grade9v3.5/issues/300). Each
step records what actually happened, including deviations. The standalone run is
a desk walkthrough of the same request and was not executed.

## Coordinator mode

Participants:
- the Owner;
- a coordinator, here OTM;
- a producer Agent in Antigravity, here nlmv2;
- a fresh verifier, here a subagent with no earlier part in the work.

The coordinator issues work, seals targets and routes records. It does not
produce, repair or assemble the product.

### 1. Locate before building (GK1)

- **Do:** look up the registry entry, then read three things: the blueprint's
  definitions of Core 1A, 1B and 2 and its 28-cell coverage grid; the master's path
  and sha; and the content source.
- **If blocked:** send one specific question per missing input, naming the places
  searched. Continue with the work that doesn't depend on the answer.
- **Seen on 19 October:** the first attempt skipped this step. It searched two
  folders, missed the master, built from the content source alone, and was
  deleted. On the second attempt the Owner named the master, which measured 39
  questions, 15 svg and 89 reveals.

### 2. Seal the targets (GK2)

- **Do:** write targets T1–T7 relative to the master:
  - the master is unchanged;
  - 52 questions, each new id present once;
  - every reviewed sentence present verbatim;
  - Core 1A and 1B complete;
  - counts per section >= the master;
  - keys unchanged;
  - gates pass.

  Add a falsifier: if reviewed wording or a key changed, reject. Post the full
  targets text with its sha as a GitHub comment before reading any return.
- **If blocked:** if `gh` fails, retry once by another route (GK8). Then post the
  full targets text with its sha in the Owner's chat and proceed. If the return
  has already arrived, seal at once and mark the seal AFTER-RETURN (unread).
- **Seen on 19 October:**
  - The targets were written only after the brief was sent (DR-001).
  - The first `gh` call used an invalid flag and posted nothing.
  - The retry landed four minutes after the return had arrived, unread (DR-003).
  - So the seal is AFTER-RETURN (unread). Checking the post's result before moving
    on (GK8) would have caught the failure at once.

### 3. Brief the producer

Use Nudge Designer, or a plain brief.

- **Do:** write one self-contained brief containing:
  - the purpose;
  - the master path, with "do not edit";
  - the 13 items, with "keep wording exactly";
  - the blueprint definitions;
  - boundaries;
  - a return contract: one counting script run on both files, gate results with
    their seeded-defect cases, and the output sha.

  Run a fresh check of the brief. The GitHub comment id of the post is the packet id.
- **If blocked:** if no channel issues an id, use a disclosed LOCAL-ID.
- **Seen on 19 October:**
  - The brief used a packet id the coordinator made up, in the app's format (DR-002).
  - It did not ask for seeded-defect cases. Step 5 shows the cost.

### 4. Produce and assemble (GK3)

- **Do:** the producer Agent builds and assembles v2. The coordinator writes
  nothing into the product path.
- **If blocked:**
  - If the producer is silent, retry by a second route, then assign another
    producer.
  - Only a typo-level fix, labelled COORDINATOR-EDITED, may be made by the
    coordinator. If no producer can be reached for a larger repair, the
    coordinator may make it, labelled COORDINATOR-EDITED. The work then stays at
    most DRAFT · CHECKED until a fresh verifier has seen the diff.
- **Seen on 19 October:** the producer built v2 at 18:58 local time. The
  coordinator did not touch it.

### 5. Record the return

- **Do:** the reply's first line quotes the packet id. Record the output sha.
- **Evidence:** the reply comment
  [#300 6270322095](https://github.com/reallakshman19/Grade9v3.5/issues/300#issuecomment-6270322095)
  and v2 sha256 `f128218c…98ace`.
- **Seen on 19 October:** the reply reported every gate passing and "Blockers:
  None". The verifier later found:
  - two of those gates were fixed "PASSED" print lines;
  - a third gate printed failures when re-run, though those were false positives
    from page styling;
  - in the mode used, the official validator does not run three of the gates, and
    it missed two of the verifier's seeded defects.

  Without seeded defects, those PASS results are UNPROVEN-CHECK. They support no
  label above DRAFT.

### 6. Check sealed bytes (GK9)

- **Do:** recompute the shas of the master, the targets and the items.
- **Seen on 19 October:** all three matched. The master is still `29057edb…`.

### 7. Verify freshly (GK5)

- **Do:** brief a subagent that has never seen the work. Give it only:
  - the exact input paths and shas;
  - the targets;
  - the method rules: one counting script for both files, its own seeded defects,
    and its own results written down before reading the producer's reply.

  Keep its report unedited.
- **If blocked:** see "verification without a subagent" in SKILL.md.
- **Seen on 19 October:** the result is [below](#wo-001-verification-result).

### 8. Coordinator note

The coordinator may spot-check and record a note. A note never moves a label.

### 9. Claim (GK6)

State the label with its scope. For WO-001 the honest claim is:

> DRAFT (NOT VERIFIED; shared account), sha `f128…`:
> - 52 questions.
> - Core 1A and 1B structure and word counts equal the master's.
> - The 13 new questions keep their stems, options and keys, and cover 13 of the
>   28 grid cells. REPRESENT and D4 are not covered.
> - The reviewed worked reasons were replaced by unreviewed text, so the falsifier
>   fired.
> - Not tested: rendering and clicks; the physics of the unreviewed hints, ladders
>   and badges.
> - Known issue: the stale "25 Cards" tab label.

Do not write "Core 2 complete" or "52 verified questions".

### 10. Repair, then preview and release (GK3, GK7)

**Repair.** It goes back to the producer as a new brief:
- restore the reviewed worked reasons verbatim;
- fix the typo the verifier found;
- ship validators with seeded-defect cases.

The coordinator does not patch the page. A small repair can go back to the same
verifier for the changed parts only, disclosed as such.

**Release.** It comes after the label reaches DRAFT · VERIFIED:
- Publish a private DRAFT preview of the exact bytes, with a release code in the
  preview page, outside the product bytes.
- When the Owner types the code, remove DRAFT. Diff the released bytes against the
  verified bytes: only the label may differ.
- If the Owner is away, leave the offline handover message and continue other work.

### Throughout: deviations (GK8)

WO-001 carries six deviations:
1. DR-001: the targets were written late.
2. DR-002: the packet id was made up.
3. DR-003: the seal is AFTER-RETURN (unread).
4. The brief did not ask for seeded-defect cases.
5. The verifier's report was copied by the coordinator, because the host did not
   capture it (an A2 fallback).
6. All posts come from one account (an A5 fallback).

Each one weakens what can be claimed. None stopped the work.

### WO-001 verification result

The fresh verifier returned **NOT VERIFIED** for v2 sha `f128218c…`. Its findings
by target:
- **T1, T2, T4, T5, T6 met:** the master is unchanged; 52 questions with each id
  once; Core 1A and 1B structure and word counts equal the master's (1A differs
  only in line-ending bytes); per-section counts equal to or above the master;
  keys correct in all three places they are encoded.
- **T3 not met, so the falsifier fired:** all 63 stem sentences and 52 options are
  present, but 0 of the 30 reviewed worked-reason sentences are. The producer
  replaced them with its own step-by-step text. A positive control showed the
  check passes when the reviewed text is present.
- **T7 unknown:**
  - two producer gates were print statements;
  - one producer gate printed false-positive failures when re-run;
  - the official validator misses two seeded defects that the verifier's own
    gates catch.

The verifier caught all of its own seeded defects except one first attempt, which
it then tightened. Rendering was not checked: the browser could not open the local
file.

What this run shows:
- The producer's self-report ("all gates pass, no blockers") was wrong. In this
  run, the fresh check against sealed targets found the problem; the producer's
  own gates did not.
- Labels kept the work at DRAFT, but no step had to stop. Repair is the next step.

## Standalone agent mode

Participants: the Owner and one agent, for example an Antigravity agent in the
product workspace. There is no coordinator. The agent produces, and the
separation comes from fresh context or from the Owner.

| Step | The agent does | If blocked |
|---|---|---|
| 1. Locate (GK1) | Reads the blueprint definitions and grid, finds the master and measures it, and notes the content source. Starts a registry row if none exists. | If the baseline isn't found, it asks one question per missing input, naming the places searched. Meanwhile it writes its counting and fidelity scripts and their seeded defects. If it can't open a named file, it asks for a copy. |
| 2. Seal (GK2) | Before the first measurement of its own output, posts the full targets text with the sha256 of the targets and the master. It uses GitHub if it can; otherwise the Owner's chat, without waiting for an acknowledgement. | With no channel at all, it writes a LOCAL-SEAL file and quotes its sha in the next message. Drafting before sealing is fine; measuring before sealing makes the targets post hoc. |
| 3. Produce (GK3) | Builds and assembles v2, copying reviewed wording exactly. | If a source sentence looks wrong, it follows "source defects": it records a hypothesis, asks, reproduces the sentence or lists an erratum, and qualifies the label. It never retouches the sentence silently. |
| 4. Validate (GK4) | Runs its checks, each with a seeded defect that must fail. Its proven checks can support DRAFT · CHECKED. | If a validator crashes, it retries once or changes method on both files. If the crash persists, the part is NOT_RUN and the label names it. If no seeded defect can be made, the check is UNPROVEN-CHECK. |
| 5. Verify (GK5) | Starts a fresh subagent or conversation with only the verifier bundle. | Without one, it gives the Owner a paste-ready bundle for a fresh chat, or names two or three sections for an Owner spot-check. Failing both, it runs the minimum self-review: DRAFT · CHECKED (SELF-ASSESSED). |
| 6. Check bytes (GK9) | Re-hashes the master, targets and items before claiming anything. | If hashing is unavailable, it compares size and modified time, and says the check is weaker. |
| 7. Claim (GK6) | Gives the label, its qualifiers, the sha, x of 28 and the not-tested list, in one message. | If N is unknown, it writes "N unknown" and continues. |
| 8. Release (GK7) | Shows the DRAFT preview, and releases on the Owner's words or a recorded grant, diffing so only the label changes. | If the Owner is away, it leaves the offline handover and the work stays DRAFT. |
| Throughout (GK8) | Lists every fallback and skipped step in the same reply. Retries a failed tool by a second route. | Under pressure: checkpoint, then narrow visibly, then accept SELF-ASSESSED. |

How standalone differs from coordinator mode:
- GK3 reduces to "don't retouch reviewed content silently".
- GK5 matters most, because it is the only separation between producing and judging.
- Sealing happens before the agent's first measurement, so a late seal is avoidable.

On the WO-001 request, step 4 asks for a fidelity check covering every reviewed
sentence, including the worked reasons. Such a check fails when they are missing:
the WO-001 verifier's check did. Whether a standalone agent would run it fully is
untested.

## Where each blocker lands

No blocker in either mode stops all work. The worst outcome of a fully blocked run
is a DRAFT or DRAFT · CHECKED (SELF-ASSESSED) deliverable that carries:
- its qualifiers;
- its deviations;
- its scope.

The Owner can still preview it the same day and decide. The only refused action
is showing it under a stronger label than that.

## How this guidance was tested

Two fresh subagents walked through the guidance cold, without this file:
- **Coordinator mode:** a chemistry extension scenario with a lost baseline, a
  failed seal post, a validator with no seeded defect, a key typo, a six-hour
  Owner absence and budget pressure.
- **Standalone mode:** an agent with no GitHub, no hooks and no subagents, a late
  Owner answer, a crashing validator and a wrong source sentence.

Neither was forced to stop all work, but both found steps with no fallback,
gates that didn't fit, and contradictions. These were fixed in SKILL.md. A
pre-publication check then found four more steps without fallbacks; those were
fixed too. A desk walkthrough is not a field trial; the
coordinator-mode WO-001 run above is the only executed cycle so far.
