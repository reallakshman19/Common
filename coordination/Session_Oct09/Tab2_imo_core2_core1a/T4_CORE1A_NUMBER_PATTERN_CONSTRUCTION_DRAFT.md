# 183-T4 — AUTHOR-MADE Core 1A construction draft: finding and defending a numerical outsider
Date: 2026-10-12 | chat=6acc303b | Owner aim v1.1.0 | outcome=O2
Status: RESEARCH/AUTHORING DRAFT ONLY. NOT a source-Core2 item, not an admitted Core1A, not a rendered page, not QRT accepted, not permission to publish. All examples and explanations below are newly authored, not sourced or paraphrased from any SOF paper.

## Context and strict binding limit
Provisional candidate lesson ID: MIC-IMO-AUTHORED-LOGIC-NUMBER-PATTERNS-CANDIDATE
Potential consumer question ID: SOF-IMO-G09-L1-2023-24-A-Q003, owner seed entry 44 (printed number 3 claim).
Basis: TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl@80816f9bb5a579f4c822a477ce53e8b98be1381b describes the preliminary learning demand as “Identify numerical odd-one-out rule”, at LOGIC-NUMBER-PATTERNS. Source register@800a2f693e1b46162a026375c5854ad4b8b05257 has NOT_VERIFIED stem/options and QRT NOT_CLASSIFIED; no particular Q003 crux_move_ref is known. This draft teaches one possible numerical-invariant method, NOT a claim that squares or cubes are Q003's actual pattern. Actual question binding and reuse across all 68 require source and academic review.
Blueprint: BP-CORE1A-CONSTRUCTION v1.8.0, registry blob 591ba061b8771c30fdffc4506aa720ca9ba89335.
Golden comparator: G-MATH-LINEAR-CONSTRAINT (CANDIDATE), blob 0cf42ead25564a71de824b4e41a62e1502af6183, for T02 single decision / T03 staged representation / T11 compact anchor ONLY; content is NOT copied.
No SOF original text, options, figure, answer or key stored here. No external PDFs downloaded.

## Learner-facing lesson draft (all AUTHOR-MADE)

**Concept header.** Numerical odd-one-out: find a rule, test every candidate, and explain why exactly one fails it.

**Learning decision.** When several values look related, what check proves that a chosen property belongs to the other values and excludes the outsider? A visually persuasive sequence alone is not an argument.

**Entry assumptions.** Learner can multiply whole numbers, recognize square numbers, compare integers, and use a simple list/table. For the *changed* exit task, the page must also explain that a cube is a product of three equal factors (e.g. 2×2×2=8); do not presume cubes are mastered.

**Elicit a prediction (construction, not a graded source-question attempt).** Consider these newly authored numbers: 9, 16, 25, 36, 37. Write down a candidate property of four values before checking any outsider.

**Construction unit CU-01 / key step:** Turn the candidate property into a complete, falsifiable test covering all five numbers.

**Teaching path** (steps MUST state action, local warrant, output):
1. `TC-01 | CONNECT` — Action: Translate “looks patterned” into “is a perfect square of an integer.” Why valid: a perfect square has the exact form k×k with whole-number k; resemblance to an increasing sequence is weaker evidence. Output: the property P(n) = “n = k² for some non-negative integer k”.
2. `TC-02 | REPRESENT` — Action: Construct the table [9=3², 16=4², 25=5², 36=6²] while keeping 37 unclassified. Why valid: evaluating the square explicitly verifies P on four separate values. Output: four certified instances of P; the fifth still needs a decision.
3. `TC-03 | DECIDE` — Action: Compare 37 with consecutive squares 6²=36 and 7²=49. Why valid: squares of nonnegative integers increase with their base; no integer base lies strictly between 6 and 7. Output: 36 < 37 < 49, hence 37 is NOT a perfect square.
4. `TC-04 | VERIFY` — Action: State the separation rule precisely: four listed values satisfy P; 37 does not. Ask whether another rule is plausible, and distinguish “supported by this property” from “uniquely mandated by the question” when no criterion is specified. Why valid: a finite set can often admit competing artificial rules; the stated rule is defensible by complete positive and negative checks, but uniqueness needs a task convention. Output: 37 is the outsider **under the perfect-square rule**, with the ambiguity disclosed.

**Staged representation (expected, not yet rendered).** Accessible text table with columns Value / Candidate square base / Is exact square?; start with blank test entries, then reveal the four equalities, and finally the numerical interval for 37. The table is instructionally meaningful; do not substitute a decorative SVG or color-only cues. Renderer-specific `representation_ref`/asset and reveal stages are TODO, NOT falsely supplied.

**Key step / inferential jump.** The outsider is established not by its visual difference but by a reason that disqualifies it while confirming the same property for every other candidate.

**Compact anchor.** Claim → verify for each member → disprove for the remaining member → explain whether the rule is unique or conditional.

**Worked anchor (AUTHOR-MADE).** Four squares: 9, 16, 25, 36. The fifth, 37, falls between 6²=36 and 7²=49. Four satisfy the shared invariant; 37 fails. This is a justified classification under the stated invariant. Avoid presenting it as an SOF official answer.

**Quick check (separate, optional).** In 16, 25, 36, 49, 63, choose the outsider under the perfect-square rule, and show the test without guessing. Protected answer: 63; it lies between 7²=49 and 8²=64. All four others are squares.

**Independent changed-case exit (required).** Recall that a whole-number cube has the form k×k×k. For 8, 27, 64, 125, 217, name a common property of four numbers, name the outsider, justify the negative case with two consecutive cubes, and state what (if anything) this proves about unique possible rules. Write a response before opening the answer. Protected answer: 8=2³, 27=3³, 64=4³, 125=5³; 217 lies between 6³=216 and 7³=343, so it is not an integer cube. Thus 217 is the outsider under the cube rule; uniqueness without a declared property is not established.

**Non-diagnostic repair note.** Do not assert a learner misconception. If a learner merely guesses by last digit, ask for a complete positive/negative property test; only evidence from their actual response permits a diagnosis. No `TRAP_REPAIR` content is instantiated here.

## Explicit blueprint/golden gap crosswalk
- CONCEPT_HEADER: DRAFT content present; official package metadata missing.
- UNIT_HEADER: CU-01 decision present; final reference ID pending.
- CONSTRUCTION_STEPS: TC-01..TC-04 authored, each with action/warrant/output; renderer schema and learner readability untested.
- KEY_STEP: present as draft inferential jump; source question's *actual* crux unknown.
- EXIT_RECALL: changed cube task and protected reasoning drafted; page commitment/answer protection not rendered.
- MODEL_CONTRACT: prerequisites drafted; no bound package.
- STAGED_VISUAL: table design specified; no final source asset or staged renderer receipt.
- WORKED_EXAMPLE: authored square example; human pedagogical review pending.
- EQUATIONS/MathML: mathematical expressions here are plain markdown; governed relation records/MathML not authored.
- GOLDEN: intended T02 one decision, T03 structured reveal, T11 compact invariant anchor; no screenshot or actual page delta test.
- QUESTION_BRIDGE/return link: NOT bound to Q003; never attach until faithful source stem/options and actual crux verified.
- A4 same-page PDF and QRT: NOT_RUN / NOT_CLASSIFIED; Owner D-183-2 and D-183-4 remain OPEN.

## Independent bounded mathematical checks, 2026-10-12
Executable pure arithmetic comparison performed in JS (not product renderer):
- worked [9,16,25,36,37] with integer-square test -> sole non-square 37 PASS;
- quick check [16,25,36,49,63] with integer-square test -> sole non-square 63 PASS;
- independent exit [8,27,64,125,217] with integer-cube test -> sole non-cube 217 PASS.
These checks only falsify arithmetic mistakes in three authored examples. They are NOT schema, accessibility, PDF, golden visual, source custody, QRT, or learner comprehension tests.

## Exit criteria for finishing r1 183-T4
1. Verify authentic Q003 content and classify its actual concept/crux; if this generic lesson doesn't teach its decisive bridge, do NOT attach it.
2. Obtain a nonoverlapping authorized product/TEST writer lane and build a proper package using the existing sole `Shared/tools/render_core.py`, not a handwritten HTML substitute.
3. Run schema and renderer qualification, inspect a real learner Core1A page, bind safe navigation to the actual Q003 only if justified, capture golden deltas.
4. Keep the authored material clearly differentiated from the original question and from official source hints/answer.
5. Obtain QRT/curriculum/publishing decisions from the authorized human; no self-promotion to accepted lesson.

Result: an independent source-safe slice of O2 authoring exists, but no Core1A page has yet been built or admitted.
