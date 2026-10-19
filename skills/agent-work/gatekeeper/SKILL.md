---
name: gatekeeper
description: Decide what a deliverable's evidence actually supports before it is labelled, shown or released. Use for learner products, published pages, item banks and any work where a coordinator, producer or single agent could otherwise certify its own output. Prefers evidence the claimant cannot rewrite and gives every check a fallback, so a missing anchor narrows the label instead of stopping useful work. Works in coordinator mode and standalone agent mode.
---

# Gatekeeper

Prototype v0.1. Every check here comes from one documented failure on 19 October
2026, recorded in [the lessons source](references/LESSONS_20261019.md). A
coordinator built a learner product from a script in minutes. The Owner judged it
"not even 10%" of the existing baseline: it had 13 questions against 39, with a
median of 215 words per question against 362. Yet it passed every check, because
the same participant ran the checks, wrote the evidence and reported the result. Checks that the claimant
runs and reports alone can support CHECKED at most, never VERIFIED or RELEASED.
A coordinator's checks on work it issued are notes and raise no label.

This module does two things:

1. It binds each claim to evidence the claimant cannot rewrite, wherever that
   evidence exists (an *anchor*).
2. It names a fallback for every check. A missing anchor lowers or qualifies the
   label; it does not stop work.

Gatekeeper adds label rules, not execution gates. Work always continues, and a
private DRAFT preview to the Owner is always allowed. What is refused is a label
stronger than its evidence. Two checks also limit actions:
- the coordinator does not produce the work it issued (GK3), except as GK3's
  fallback allows;
- only the Owner's words, or a recorded Owner grant, release work (GK7).

Each of these has a fallback: keep the weaker label, or use the fallback the check
names.

For standalone and composed use, see the shared
[Start here guide](https://github.com/reallakshman19/Common/blob/main/skills/agent-work/START_HERE.md).
This module adds no dependency on the other modules and grants no authority. It
does not dispatch, approve, merge or publish anything.

## Labels

| Label | Supported by |
|---|---|
| DRAFT | The default for anything produced |
| DRAFT · CHECKED | Targets sealed (GK2), and the producer's own checks, proven by seeded defects that fail (GK4), meet them. In standalone mode these are the agent's own checks. |
| DRAFT · VERIFIED | A fresh participant (GK5) ran its own proven checks on the exact bytes and found the targets met. Producer checks that are UNPROVEN-CHECK don't prevent this. |
| RELEASED | GK7: the Owner's words, or a recorded Owner grant covering this class of work, name the verified bytes. The Owner may also release bytes below VERIFIED by naming their sha; the label then keeps its qualifier, for example RELEASED (Owner; SELF-ASSESSED). |

When a fallback was used, qualify the label instead of hiding the fallback. For
example:
- DRAFT · CHECKED (targets post hoc)
- DRAFT · VERIFIED (Owner spot-check of sections 2–4)
- DRAFT · VERIFIED (separate session; shared account)
- DRAFT · CHECKED (SELF-ASSESSED)
- DRAFT · VERIFIED (NO-BASELINE): checked against the blueprint only
- DRAFT · CHECKED except section 3 (NOT_RUN)
- DRAFT · CHECKED (1 source sentence under query)

Qualified work can still be shown to the Owner as DRAFT. The qualifier stays on
until its cause is resolved.

Every label carries its scope:
- the sha of the bytes it describes;
- coverage as x of N, with N taken from the blueprint, or "N unknown";
- what was not tested (GK6).

A label describes bytes. When bytes change, claims about the changed parts go back
to DRAFT. Claims about unchanged parts can be carried forward when a diff shows
they did not change. Removing the DRAFT label at release is the one change that
doesn't reset a label, provided a diff shows nothing else changed (GK7).

## Anchors and their fallbacks

| Anchor | Typical use | If unavailable |
|---|---|---|
| A1: the Owner's own words as the host records them, or a standing Owner grant quoted with its link | Release; accepting a scope change or deviation | Quote the Owner's message verbatim with its host timestamp. If the Owner can't be reached, keep the work DRAFT and continue other work. |
| A2: a verdict the host captures from a fresh participant (a subagent result returned by the harness, or a separate agent's own post) | GK5 | See the GK5 fallbacks. |
| A3: an external clock and id (a GitHub comment or commit id and its created_at time, or an app-issued packet id) | Sealing targets; packet ids | Post the full targets text in the Owner's chat, with the sha256 of the targets and of the baseline. Proceed without waiting for an acknowledgement; the host timestamp is the seal. Otherwise use a dated message to any second party who keeps it. Failing both, write a local file and quote its sha in your next outbound message, recorded as LOCAL-SEAL. |
| A4: a check the claimant cannot edit (a required CI status, an admin-managed hook, a reviewer-owned script) | Repeatable checks | Run the same check, paste its output together with its seeded-defect result, and mark it ADVISORY. |
| A5: a separate identity for each role (own account, bot or app identity, a host-recorded session) | Returns and verdicts | Put a role line and the session or chat id in each post, and state the shared-account limit in the label. |

Anchors make shortcuts visible; they do not make anyone honest. Deliberately forging
an anchor is tampering, and this module cannot prevent it. The Owner's preview of
the exact bytes remains the backstop.

## Checks

Use the checks the work needs. Each pairs a primary route with its fallback. State
every fallback you use in the same message. Record it as a deviation (GK8) when it
lowers or qualifies a label, or skips a step.

| Check | Do | Fallback |
|---|---|---|
| GK1. Locate before building | Before producing a product, find three inputs. (1) The blueprint: the definition of each artifact type and the coverage set N. (2) The existing best version, which is the baseline or quality bar. (3) The content source. Read the blueprint's definition of each artifact type; never infer it from a filename. Search the product registry (see Records), the project repository and its history, the published site, and the workspaces of the producers who built earlier versions. Ask the producer Agent where it keeps them. A link you cannot open is not a read: ask for a copy, and record its sha once it arrives. | Send the Owner one message with one specific question for each missing input, naming what you searched. Meanwhile continue with the parts that don't depend on the answer. If the Owner can't answer: if no existing product is found, build against the blueprint alone, labelled NO-BASELINE. NO-BASELINE work can still be CHECKED and VERIFIED against blueprint-only targets, but the qualifier stays on the label until a baseline comparison is done. A first build with no earlier product is simply blueprint-only; say so. If the blueprint or content source is the missing input, state the definition you assume as a HYPOTHESIS, build on it, and label the work DRAFT (blueprint assumed) or DRAFT (source assumed). |
| GK2. Seal targets before results | Write targets and a falsifier, and seal them with A3, before the first measurement of the candidate. In coordinator mode that means before the return is read. Drafting before sealing is fine; measuring the candidate before sealing makes the targets post hoc. A falsifier is a stated result that rejects the work outright, whatever the other targets show, such as a changed key or altered reviewed wording. Targets compare against the baseline per section and per item, not only in total. For an extension, say: unchanged parts are byte-identical or equal by count; new parts match the baseline's per-item rates, such as length, worked reasons and reveals; coverage is x of N; reused reviewed content is reproduced faithfully. | See the A3 fallbacks. If a result has already arrived unread, seal now and mark the seal AFTER-RETURN (unread). If it has been read, the targets are post hoc: the label is at most DRAFT · CHECKED (targets post hoc). A fresh verifier who seals its own targets before measuring can still reach VERIFIED. |
| GK3. Keep producing separate from issuing | The participant who issues and coordinates work does not produce, repair or assemble the deliverable. Assembly, such as inserting new items into a page, is production: the producer or a separate Agent delivers the assembled file. A repair goes back as a new brief. | Typo-level fixes that change no meaning, key, number or answer may be made by the coordinator. Label them COORDINATOR-EDITED in the record and show the diff to the verifier. Anything touching meaning, keys or numbers goes to the producer or another capable Agent. If none can be reached, the coordinator may make that repair too, labelled COORDINATOR-EDITED. The work then stays at most DRAFT · CHECKED until a fresh verifier has seen the diff. In standalone mode the agent is the producer, and GK5 provides the separation. |
| GK4. Prove each check can fail | Any check whose PASS raises a label is paired with a seeded defect that must fail. Whoever runs the check runs its seeded defect: the producer for CHECKED, the verifier for VERIFIED. Briefs ask producers to ship their seeded-defect cases with their validators. Fit the defect to the work. For copied or converted content: a dropped sentence or a truncated stem. For new items: a wrong key, a key typo, a length-skewed option or a duplicate id. For pages: a missing section or a lowered count. A crash, a timeout or a missing input is NOT_RUN, never PASS. | Use a known-bad historical case instead. If neither exists, report the result as UNPROVEN-CHECK; it doesn't raise a label, but it is still useful evidence. If a validator crashes, retry after one fix or switch to another method. Any method change applies to the baseline and the candidate alike. If it still crashes, the affected part is NOT_RUN, and the label names that part as untested. |
| GK5. Verify the exact bytes, freshly | For the first verification of a work order, the verifier is a participant who didn't produce it. It checks the sha-bound bytes against the sealed targets and the baseline. It counts both files with the same method, runs its own seeded defects, and names a plausible wrong result its check could miss. Its verdict is kept unedited (A2). If the verifier can't reach a file, place a copy with its sha where it can. A small repair round may go back to the same verifier for the changed parts only, disclosed as such. Use a new verifier when the repair is substantial, or when the earlier verdict is itself in dispute. | See [verification without a subagent](#verification-without-a-subagent): a separate session gives VERIFIED (separate session); an Owner spot-check gives VERIFIED (spot-check: named sections); a minimum self-review gives DRAFT · CHECKED (SELF-ASSESSED). |
| GK6. Tie claims to bytes and denominators | A claim names the sha of the bytes shown, the coverage x of N with N from the blueprint, and what was not tested. For an extension, state both the new part ("8 new items cover 6 of 28 cells") and the whole. An Owner-set scope is the scope, but still report it against the blueprint's N. A display that truncates or reformats content is a new artifact and needs its own check. Fix a misleading label; don't just add a caveat next to it. N is the blueprint's coverage set for the deliverable's scope; if the blueprint nests sets, for example a topic within a core, name which set you used. | Without a hashing tool, use the size plus the first and last line. If N can't be found after GK1, write "N unknown" and continue. RELEASED with N unknown needs the Owner to see that phrase. |
| GK7. Release on the Owner's words | Releasing means removing DRAFT, publishing to learners or merging into a product path. It needs A1 naming the bytes being released, normally the verified bytes, either by their sha or by the preview that showed them. Releasing below VERIFIED keeps the qualifier on the label. Show any release code in the preview page or message, outside the product bytes. At release, diff the released bytes against the verified bytes: only the label may differ. | If the Owner can't be reached, use the offline handover below. Nothing else waits on the release. |
| GK8. Say when a step is skipped | When a step is blocked or costly, or you are under budget or context pressure, say so in the same message with a deviation record: what was skipped, why, the effect on the label, and the fix. Retry a failed tool at least once by another route before calling it unavailable. Never trade quality silently. Under pressure, choose in this order: (1) checkpoint and defer to a successor (see the Nudge Designer [successor prompt](../nudge-designer/assets/prompts/successor.md)); (2) narrow the scope visibly; (3) drop GK5 and accept DRAFT · CHECKED (SELF-ASSESSED). Never drop the label, the scope statement or the deviation record. | If the Owner can't answer, take the feasible path, record the deviation and qualify the affected label. Continue unaffected work. |
| GK9. Notice changes to sealed bytes | Keep a sha list of the sealed inputs: the registry entry, baseline, targets and reviewed items. Recompute it before verifying and again before release. | Without hashing, compare size and modified time and say the check is weaker. An unexplained change is a deviation: verify the affected claims again, and continue unrelated work. |

## Verification without a subagent

Use these in order when the host cannot start a fresh participant:

1. **Separate session.**
   - Give the Owner one paste-ready bundle: the verifier brief, the exact file
     paths or copies with their shas, the sealed targets, and the baseline.
   - Leave out your history, notes and verdict.
   - The Owner pastes the bundle into a fresh chat and returns its reply unedited.
   - Label: VERIFIED (separate session).
2. **Owner spot-check.**
   - Name two or three sections most likely to be wrong, with what to compare in
     each, so the Owner can check them in minutes.
   - Label: VERIFIED (spot-check: named sections).
3. **Minimum self-review.**
   - Re-derive the decisive counts from the files alone, by a different method
     from the one you produced them with, without consulting earlier notes.
   - Run the seeded defects again, and name the plausible wrong result this review
     could miss.
   - Label: DRAFT · CHECKED (SELF-ASSESSED).

Any of these can be shown to the Owner the same day, under its label.

## Source defects

When the content source itself looks wrong (a factual error, a contradiction, a
broken figure), don't fix it silently and don't drop it from the fidelity check.
Do both of these:
- Record it as a HYPOTHESIS with the exact sentence and your reason.
- Ask the Owner, or the source's owner, in the same message as other questions.

Until there is an answer, either reproduce the sentence verbatim with a visible
note, or apply a correction listed in an errata note. Either way, list the
sentence as a named exemption in the fidelity check, and qualify the label, for
example "1 source sentence under query". The Owner's answer (A1) settles it. Other
work continues.

## Offline Owner

When work is ready and the Owner is away, leave one message containing:
- a private DRAFT preview;
- the label with its scope;
- the deviations;
- the release code, if one is used;
- any open decisions.

Then continue other work. When the Owner returns, recompute the shas (GK9) before
releasing. Work never waits idle on the Owner. Only the release does.

## Records

One work-order folder or issue per deliverable is enough. It holds:
- the targets, with their seal;
- the brief and its packet id;
- the return link and output sha;
- the verifier's verdict, unedited;
- deviations;
- the release line.

Use plain prose; no schema is required. In standalone mode the agent's reply
thread can serve as the record, and packet ids are not needed.

**Packet ids** come from the channel (a comment id or an id issued by an app). If
no channel issues one, use the work-order id plus the first 8 hex characters of
the brief's sha, marked LOCAL-ID. Never make up an id that imitates an app's format.

**Product registry:** keep a short table in the project repository. Each row
records a topic, its blueprint (path and sha), its baseline (path and sha), its
content source and its N. Add a row from a located file or from the Owner's words.
If no registry exists, start one with this work's row. Include the registry in
GK9's sha list.

## Modes

| | Coordinator mode | Standalone agent mode |
|---|---|---|
| Who produces and assembles | A producer Agent briefed by the coordinator | The agent the Owner asked |
| Who seals targets | The coordinator, before briefing | The agent, before its first measurement of the candidate |
| Who verifies | A fresh participant the coordinator briefs | A fresh subagent or session; otherwise [verification without a subagent](#verification-without-a-subagent) |
| Status of the coordinator's own checks | Notes, never raising a label | Not applicable |
| Who releases | The Owner, or a recorded Owner grant | The Owner, or a recorded Owner grant |

[The walkthrough](references/WALKTHROUGH.md) follows both modes end to end, with
the blocker and fallback at each step. It contains worked answers, so withhold it
from fresh exercises. [Enforcement](references/ENFORCEMENT.md) covers optional
mechanical support (hooks, CI and managed settings) and what to do on a host that
has none.

## Limits

The evidence base is one coordinator, one domain and one day. The mechanisms come
from failure analysis, a red-team review, and two cold walkthroughs (coordinator
mode and standalone mode) whose findings were folded in. They have not
yet run as a complete release cycle. Known limits:
- Fresh verifiers from the same model family can share blind spots.
- A shared account weakens A5.
- Instruction-only isolation is not access control.

These limits narrow labels; they don't block work. The module doesn't replace a
project's own review, merge or acceptance rules. Where those are stricter, follow
them; where a standing Owner grant already covers a step, use it.
