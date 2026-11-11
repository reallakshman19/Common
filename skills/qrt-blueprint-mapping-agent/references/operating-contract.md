# QRT Blueprint Mapping Agent — detailed operating / falsification contract

This reference is part of [../SKILL.md](../SKILL.md). The skill teaches an engineering agent to produce **draft, reproducible mapping evidence**; it does not empower that agent to issue independent cognitive verdicts or Owner decisions.

## Inputs / authority resolution

| Input | Actual authority | Fail-closed handling |
| --- | --- | --- |
| Question/source | Original authorized source and source-integrity register, plus exact Git blob/hash | `SOURCE_UNVERIFIED`; never reconstruct an original from memory |
| QRT semantics | Repo QRT method and `Shared/quality/question-demand-matrix.v1.json` | If mismatch/unknown, stop classification |
| Primary learner work | Exact stem, options, representation, and learner-displayed text | State competing demand and how question may already supply W |
| Difficulty | Five existing canonical components + D1–D4 policy, with individualized grounds | All null/pending if source or math insufficient |
| Blueprint | Live `Shared/web/interactive-page-blueprints.v1.json` with role IDs / component order | Reuse. Structural error classified; do not clone |
| Renderer | Live `Shared/tools/render_core.py` only | Local mock/browser reconstruction is not product |
| Golden | Owner original immutable snapshot lock, source role and mode | Different question: compare technique, not bytes |
| Academic result | Dated named qualified independent mathematics/QRT reviewer plus COI | Keep every unsigned H/S/P/M as PENDING |
| Owner status | Explicit decision ID tied to specific cell and source SHA | Keep PENDING; no inference from green CI |

Current examples to explore, not authorities to assume in later work:
- [#201 seven authored D2 TEST candidate registry](https://github.com/reallakshman19/Grade9v3.5/issues/201)
- [#205 draft native benchmark](https://github.com/reallakshman19/Grade9v3.5/pull/205)
- [#211 two high-risk reviewer tasks](https://github.com/reallakshman19/Grade9v3.5/issues/211)
- [#214 other-five academic review](https://github.com/reallakshman19/Grade9v3.5/issues/214)

## The two-layer separation that made the earlier process effective

The same learner act travels across three layers. The agent must expose, not collapse, them:

| Layer | Decides | Must not decide |
| --- | --- | --- |
| **Canonical question** | Mathematical facts, statements/figures, conditions, source integrity, stable decisive crux | A learner's past mastery or approved disclosure controls |
| **QRT resolution** | Demand, D band, X/Y/Z/W, H/S/P/M semantics, learner-relative support judgment | HTML slots, CSS, renderer choice, frozen golden mutation |
| **Core blueprint and render** | Role structure, components, page slots, attempt/reveal policy, native bytes | Whether the item is truly RETRIEVE instead of APPLY; signed QRT acceptance |

Classify **before rendering**, then verify **after rendering** that authoring/figure/ARIA did not leak W. A structural golden match can coexist with a cognitively wrong question. A correct mathematics proof can coexist with a premature pre-attempt hint.

## First worksheet, one question at a time

Produce this before deciding which pages to build:

```text
QUESTION_ID:
SOURCE_KIND: ORIGINAL_VERIFIED / AUTHORED_TEST / SOURCE_UNVERIFIED
PROVENANCE: repo@40SHA file@blob source-rights decision
EXACT STEM/OPTIONS/DIAGRAM: path/ref and immutable digest
MATHEMATICAL MODEL AND ANSWER:
DOMAIN/UNIT/CROSSCHECK:
CHANGED CASE and why it changes reasoning:
DECISIVE INDEPENDENT LEARNER ACT:
PRIMARY DEMAND / nearest competing demand + falsifier:
FIVE DIFFICULTY COMPONENTS + exact justification each:
D1/D2/D3/D4 boundary:
X / Y / Z / W: what the learner already has vs must supply
STEM_ALREADY_GIVES (including named variable, formula, operations):
ROLE BLUEPRINT MAP:
  CORE2 (only with genuine source+rights):
  CORE2A (new attempt+H1/H2/precommit):
  CORE1A (teach stable construction+independent changed exit):
  CORE1B (reconstruct+different boundary):
  CORE1 (orient without W):
  CORE2B (changed-condition independent transfer):
GOLDEN PAIR (why same question or why cross-question):
WHAT WOULD DISPROVE THIS MAPPING:
PAUSE/PROCEED: cause and authority
```

If no genuine student learning profile is present, do not use Y=`DEMONSTRATED`. Record the proposed bridge as **unverified** and ask a reviewer to validate the support level.

## Five roles: progression rather than five clones

An illustrative mathematical relationship, not a universal lesson:

- Core2A asks the learner to construct the governing choice or inference. Precommit H1/H2 focus X/Y, **not Z's answer or W itself**.
- Core1A teaches the stable relation in a different worked example and demands a **fresh independent exit**; its explanation can be complete without pre-answering the separate assessed Core2A.
- Core1B removes guidance and adds a boundary/exception making memorized arithmetic insufficient.
- Core1 provides orientation and navigational context without solving the assessed question.
- Core2B changes the relation, condition, representation or feasibility so transfer is more than "same sum with new integers."

In a true source-question package, include Core2 from eligible source input; the seven #201 examples deliberately exclude Core2 because they are authored TEST, not an official exam bank.

## Twelve QRT review objectives (never a global numerical score)

| Ask | Required content-specific question for reviewer |
| --- | --- |
| H1 | Does the first hint clarify **X** without giving W? |
| H2 | Does it connect X to legitimately held **Y**, not pre-select W? |
| H3 | **After a nonblank attempt**, does it open the way to Z while leaving W? |
| S1 | Does a first visual reveal situation/X, including accessible text, not solution? |
| S2 | Does a stage show held Y in this exact question? |
| S3 | Does a later stage support construction toward Z, without completing W? |
| P1 | Do all preattempt exposures (including SVG title/desc, ARIA, keyboard behavior, stage metadata) preserve W? |
| P2 | Does concept navigation really land on the relevant X/Y bridge? |
| P3 | Does the solution explain each move and independently check correctness? |
| M1 | Is the wrong idea plausible for **this** learner/question? |
| M2 | Does diagnosis distinguish misconception from an arithmetic slip? |
| M3 | Does repair demonstrate why the wrong idea fails and supply a transferable correct rule? |

An irrelevant visual may receive an independently justified applicability note; do **not** create decorative SVG to manufacture S1–S3 passes. Tests can detect blank-commit and answer-string leaks; they cannot certify pedagogical judgment of W.

## Golden method: one source pair at a time

1. Record exact question, role, blueprint version, selected renderer mode, snapshot-lock git blob and SHA256 hashes.
2. Verify frozen lock matches actual unmodified snapshot bytes. If altered, STOP.
3. Decide whether source question **equals** golden input. If yes, compare byte equality only under identical renderer/mode, with intentional version deltas segregated. If not, do **semantic technique** comparison: slot/component order, role job, disclosure, real figure behavior, learner exit and transfer.
4. For each observed mismatch, write `SYMPTOM, EXPECTED_GOLDEN_MOVE, ACTUAL_NATIVE_MOVE, FILE_AND_SHA, OWNER_LAYER=[INPUT|RENDERER|BLUEPRINT|ORACLE], FALSIFIER, MINIMAL_FIX`.
5. Fix authored INPUT where content causes the problem. To propose BLUEPRINT edit, first prove no valid authoring through registered slots can realize the golden-required move. Require an explicit isolated authorization and replay every affected role.

**Never:** duplicate a blueprint per QRT cell; change the golden by test update; call unrelated HTML text unequal a structural failure; claim "golden-approved" from a shape match; conflate graphical stage presence and correctness.

## Falsification minimum

| Check | Counterexample the agent must attempt |
| --- | --- |
| Maths | Counter-condition, infeasible domain, wrong unit, misleading coincidental equality |
| Cognitive | Demonstrate solving by a *different* primary demand than label |
| D band | Demonstrate D1 simple execution OR D3 bridge vs claimed D2 |
| W | List stem/H1/H2/diagram/ARIA words that already specify the protected choice |
| Precommit | Initial/H2 SVG `<title>` / `<desc>`, hidden template payload, accessible labels and no-attempt cases |
| Commit | Blank submit must NOT unlock H3, solution, Core1B/2B transfer |
| Transfer | Changed case must need a fresh structural decision; not simple numeric substitution |
| Native | Wrong role count, wrong active BP ID, missing slot/component, nonzero gaps, bad digest |
| Visual | Actual CSS+JS via local HTTP; responsive overflow, JS errors, unstyled fallback, focus, print link |
| CI | Exact PR HEAD vs stacked base failed **test IDs**; non-green pipelines remain non-green |

For real evidence on #205, scoped workflow `IMO 201 D2 native golden semantic benchmark` emits `render-receipt.json`, seven five-role packages, golden technique checks, staged Chromium screenshots and candidate `imo-qrt-cell-evidence/v1` records. Any future agent must **recheck the workflow and artifact at the new exact head** rather than lift old results.

## Output / integration contract

Write one `qrt-blueprint-mapping/v1` record **per question** (see template), a plain-English reader packet with questions and falsifiers, native renderer receipts where applicable, and a terse issue/PR update linking exact candidate/base refs.

The validator `python skills/qrt-blueprint-mapping-agent/scripts/validate_mapping.py path/to/mapping.json` verifies **only record shape and impossible self-approval patterns**; no source rights, respondent identity, mathematical proof or pedagogy is verified. Its PASS must be called `STRUCTURAL_PREFLIGHT_PASS`, never `QRT_ACCEPTED`.

Do not call an implementation responsibility completed when:
- a designated independent reviewer is still missing;
- a required QRT item is PENDING/NO/PARTLY;
- a known math, source, attempt, projection or golden invariant is broken;
- a shared required CI gate fails without resolved policy;
- an Owner decision is pending.

An authored TEST package can be technically complete and still receive **BLOCKED FOR ACADEMIC ADOPTION**. Maintain source safety and separate decision tracks.
