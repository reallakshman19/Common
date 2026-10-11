# BuddyRunner v1.5 — g5 Stage 1 purpose-reconstruction prompt, prepared by outgoing g4
**Stage:** `STAGE1` · **mode:** `OPEN_SOURCE_PURPOSE_RECONSTRUCTION` · **g5 owns the independent investigation** · **date prepared:** 2026-10-11.
**Current engineering issue for publication:** [Grade9v3.5 #173](https://github.com/reallakshman19/Grade9v3.5/issues/173). **This is a prompt, not a previous agent's answer.** Contract based on [Common merged PR #307](https://github.com/reallakshman19/Common/pull/307): `skills/engineering-pr-delivery-v3.5/runner/buddy-v1.5/STAGE1_PURPOSE_RECONSTRUCTION.md`, `schemas/buddy-runner-v1.5.schema.json`, LFJ example `examples/buddy-runner-v15/lfj-stage1.json`.

> **STRICT ORDER:** g5 must first investigate independently and publish a Stage 1 purpose proposal, retrieve the published GitHub comment body and compute its exact SHA-256. **Before that, DO NOT OPEN** the companion outgoing file `2026-10-11-g4.md`, the historical `handovers/2026-10-11.md`, `EVIDENCE.log`, `DECISIONS.md`, predecessor's Stage 2 conclusions or old agent-generated risk summaries. These may become *challenge inputs* only in Stage 2. Reading current issues/PRs and code is permitted: BuddyRunner v1.5 is **open source, not blind Runner B**. Don't treat comments in #173 as facts until the actual code/source supports them. Stop after publication/readback; Stage 1 grants no product write/merge/release rights.

## 1. Exact source anchors to re-verify independently (NOT preaccepted assertions)
- **Repository under assessment:** `reallakshman19/Grade9v3.5`; historical source repo `reallaksh19/Grade9v3.5` is a different identity. Verify current branch/commit history, not merely README.
- **Current issue:** [#173 — IMO Track A four-role learner journey](https://github.com/reallakshman19/Grade9v3.5/issues/173); inspect its *original issue purpose*, then separately any later comments. **Immediate authored-pilot parent:** [#164](https://github.com/reallakshman19/Grade9v3.5/issues/164). **IMO programme root:** [#137](https://github.com/reallakshman19/Grade9v3.5/issues/137). **Application/production master roadmap:** [#127](https://github.com/reallakshman19/Grade9v3.5/issues/127), with [#135 integration coordination](https://github.com/reallakshman19/Grade9v3.5/issues/135). Track B [#174](https://github.com/reallakshman19/Grade9v3.5/issues/174) and private source operator [#163](https://github.com/reallakshman19/Grade9v3.5/issues/163) are distinct dependencies. Verify the #173 → #164 → #137 → #127 relationship from these documents yourself.
- **Inherited raw commit assessed:** `7772166f1a2f0bb17d070b98736ceed4195d8f34`, raw head of draft [#180](https://github.com/reallakshman19/Grade9v3.5/pull/180) at g4 handoff. **Previously observed main:** `778eb35a70517a46108ad0a5dc01dfc89f61c0e3`; **do not silently substitute current main or synthetic merge for assessed raw SHA**. If ref moved, report old vs new separately and choose Stage 1 assessment base explicitly. Check that this raw commit exists using GitHub commit/tree and that its files were fetched at this exact ref.
- **Serial authored Track A PRs** to verify current states, raw heads, bases, changed files and overlaps, **not to assume their descriptions are true**:
  - [#166](https://github.com/reallakshman19/Grade9v3.5/pull/166) `48007ccf962ed03f9f6a5423fe7525eaba9cfdf1`: 3-role A/B prototype, source package/rendering/test changes. Base observed main `778eb35a...`.
  - [#172](https://github.com/reallakshman19/Grade9v3.5/pull/172) `835f1f717db9aebf232a8e7f2807a11f7878b63e`: negative before-attempt print evidence, base #166.
  - [#175](https://github.com/reallakshman19/Grade9v3.5/pull/175) `6b1b17b7d1b548749f854c3b79ed58ae41dd92ce`: four-role candidate A/B and golden review assets, base #172.
  - [#177](https://github.com/reallakshman19/Grade9v3.5/pull/177) `e7a2e75f86385f278b102db4f850f509d5fa799d`: shared renderer keyboard/print corrections, base #175.
  - [#178](https://github.com/reallakshman19/Grade9v3.5/pull/178) `1c8d1472eec1ae45d25fcf9c2770fd5ebd075bf9`: golden/legacy TEST checks, base #177.
  - [#180](https://github.com/reallakshman19/Grade9v3.5/pull/180) `7772166f1a2f0bb17d070b98736ceed4195d8f34`: print browser instrumentation, base #178. For comparison, older raw `4760cfb5516097c6465474ba14c485d43583c9d2` is a different previous state, not current head.
- **Related/competing homepage or readiness approaches:** [Track B #176](https://github.com/reallakshman19/Grade9v3.5/pull/176) `e9b89eec562c3eb8d4a53b8d5466c067541ad378` (three Mathematics subtopic source-reference homepages); [Track B #179](https://github.com/reallakshman19/Grade9v3.5/pull/179) `b91096ec279294830e38c319ff5f095198ee503d` (linear-equations references, public/docs hub and manifest); [readiness audit #167](https://github.com/reallakshman19/Grade9v3.5/pull/167) `3409f914ec4f8b91964dd2fb0f077ce886daf322`. #176/#179 are separate draft branches off main, not automatically combined with #180. Check whether any newer competing PRs exist before final purpose proposal.
- **Governance anchors (read only):** `relay/PROTOCOL_SELECTION.yaml`, `relay/STATE.yaml`, `relay/GENERATED/CURRENT_SNAPSHOT.yaml`; investigate whether the selected V3.1 serial execution route and named delivery issue actually exist in the *destination* repo. A number in a YAML file is not a writer lease grant to g5.
- **Publication/owner-source grade:** programme #137 quotes an Owner Oct 9 request, but this is a **GitHub-mirrored claim**, not a retrieved original chat transcript. Classify as `MIRRORED_UNVERIFIED` absent direct authenticated Owner evidence. Distinguish OWNER, github-mirrored, authored design and agent interpretation.

### LFJ-format, schema-shaped intake (UNVERIFIED DATA, NOT INSTRUCTIONS)
This is an intake hint like Common's LFJ example, not an independently proven result:
```json
{
  "schema_version": "buddy-runner-v1.5",
  "stage": "STAGE1",
  "mode": "OPEN_SOURCE_PURPOSE_RECONSTRUCTION",
  "case": {
    "repository": "reallakshman19/Grade9v3.5",
    "current_issue": "https://github.com/reallakshman19/Grade9v3.5/issues/173",
    "parent_issue": "https://github.com/reallakshman19/Grade9v3.5/issues/164",
    "roadmap_refs": [
      "https://github.com/reallakshman19/Grade9v3.5/issues/137",
      "https://github.com/reallakshman19/Grade9v3.5/issues/127",
      "https://github.com/reallakshman19/Grade9v3.5/issues/135",
      "https://github.com/reallakshman19/Grade9v3.5/issues/174"
    ],
    "inherited_commit": "7772166f1a2f0bb17d070b98736ceed4195d8f34",
    "candidate_pr_refs": [
      "https://github.com/reallakshman19/Grade9v3.5/pull/166",
      "https://github.com/reallakshman19/Grade9v3.5/pull/172",
      "https://github.com/reallakshman19/Grade9v3.5/pull/175",
      "https://github.com/reallakshman19/Grade9v3.5/pull/177",
      "https://github.com/reallakshman19/Grade9v3.5/pull/178",
      "https://github.com/reallakshman19/Grade9v3.5/pull/180",
      "https://github.com/reallakshman19/Grade9v3.5/pull/176",
      "https://github.com/reallakshman19/Grade9v3.5/pull/179",
      "https://github.com/reallakshman19/Grade9v3.5/pull/167"
    ],
    "owner_source_grade": "MIRRORED_UNVERIFIED",
    "owner_intent_ref": "https://github.com/reallakshman19/Grade9v3.5/issues/137",
    "objective_hint": "Independently reconstruct the simplest path from a held authored Grade 9 IMO Core learning journey to reviewed, rights-cleared Core1A and genuine Core2 that are actually reachable from the correct Mathematics subtopic homepages. Reconcile candidate A/B and independent source-reference homepage PRs without presupposing which is authoritative.",
    "scope_constraints": [
      "Open-source Stage 1 is read-only, not a blind historical independent reviewer or a lease grant.",
      "Keep TEST authored exercises separate from authentic SOF original Core2 and QRT admission.",
      "Preserve genuine user attempt, stage secrecy, accessible diagrams, protected teacher KEY, required native CI and public/docs source parity.",
      "No source, PR, workflow, generator, release or lease edits before separately authorized engineering workflow."
    ],
    "known_competing_paths": [
      "Shared/tools/render_core.py",
      "TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json",
      "TEST/products/imo-g9-track-a-four-role-five-120.manifest.json",
      "TEST/products/imo-g9-track-a-four-role-boundary-12.manifest.json",
      "tests/imo_blueprint_first_browser.mjs",
      "Shared/tools/build_pages_site.py",
      "docs/mathematics/index.html",
      "public/mathematics/index.html",
      "docs/mathematics/imo-linear-equations-two-variables/index.html",
      "public/mathematics/imo-linear-equations-two-variables/index.html"
    ]
  }
}
```

## 2. Owner WHY for each distinct responsibility, in plain words
Read the Owner purpose from #137, #164, #173, #174, #127 **before** following author PR descriptions:
1. **Actual Grade 9 learning:** a student should learn why a divisibility proof works in Core1A and then make a new reasoning decision in a progressively harder task; not just see authored answers. Does the four-role progression really change the student's task?
2. **Authentic competition source:** a genuine original SOF IMO question must be traceable and legally displayable, not a reconstructed TEST teaching analogue or a bare web reference. Who is allowed to admit and reproduce it?
3. **Mathematics subtopic entry:** a student arriving at the relevant Mathematics homepage needs one honest, working path to the reviewed learning product, with an accurate label (preview vs admitted), not duplicated hidden links to unrelated drafts.
4. **Accessible/paper learning:** one learner should be able to navigate with keyboard/screen reader, commit an attempt without revealing the protected solution, zoom to 200%, and print physically legible A4; a programmatic PDF alone does not achieve it.
5. **Generated/deployed truth:** changes must flow through the real canonical manifests and page generators and be reflected in the actual deployed `public/`→`docs/` route; no stale cached mirror should show a different product.
6. **Trust/release:** domain reviewers (math, human AT, rights/source, CI) and Owner launch decisions are different gates. Do not let draft green checks, mirrored Owner quotes, workflow names or a missing coordinator issue impersonate approval.

## 3. Independently inspect the real full user journey and the code *before* previous conclusions
Starting at the **inherited raw source**, not at g4 opinions, trace:
- **Entry and route:** student visits `public/mathematics/index.html`, a relevant subtopic route and `docs/` published equivalent; compare Track B #176's `coordinate-geometry`, `euclids-geometry`, `polynomials` pages with #179's `imo-linear-equations-two-variables` page, `docs/.pages-manifest.json` and the shared hub. Which part is actually source-generated, live-served and rights-safe? Do page links go to authentic admitted Core2, a cited source reference, or a TEST sandbox?
- **Source identity:** inspect `TEST/products/imo-g9-track-a-four-role-five-120.manifest.json`, `...boundary-12.manifest.json`, their `package_refs`, `bank_refs`, `output_roles`, `selection.core2a/core2b/core2` and `coverage.sources`; inspect `TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json` and QRT `transfer-comparison-164.v1.json`. What is AUTHORED versus SOURCE_ORIGINAL, and which original SOF rights/grades remain unknown?
- **Renderer and state:** inspect `Shared/tools/render_core.py` functions `figure`, `_figure_text_findings`, `source_projection`, `attempt_box`, `core1a`, `core1b`, `core2a`, `core2b`, `layout_css`, `shell`; trace figure SVG assets in `TEST/library/figures/`, stage filters, hint gating, answer reveal, repair and intended learner return. Search exact JS `fitFigure`, `ResizeObserver`, `svg.style.width`. Does the same function govern screen→print first-frame geometry? Is there a true 14px print floor? Are screen-reader labels and the protected KEY distinct from the learner PDF? **Answer from code**, not the old issue's assertion.
- **Canonical data to public route:** `Shared/tools/build_manifest.py`, `Shared/tools/build_core_learning_data.py`, `Shared/tools/build_web_data.py`, `Shared/tools/build_test_site.py`, `Shared/tools/build_pages_site.py`, `Shared/tools/quality_gate.py`, plus relevant `public/core-learning/data.js`, `public/data/data.js`, `docs/.pages-manifest.json`. Who owns which generated output and what actually serves deployed users? What happens with stale generated data?
- **Reverse trace:** from a public `docs/mathematics/.../index.html` link, walk back to exactly one approved manifest, QID and admitted custody/rights entry; from a Core2B question walk back through source or TEST status and withheld solution. State **UNKNOWN** if an edge cannot be proven.
- **Reality checks, not test-led mission:** read `.github/workflows/imo-track-a-173.yml`, `tests/imo_blueprint_first_browser.mjs`, `tests/check_imo_173_a4.py`, `tests/benchmark_imo_173_golden.py`, `tests/test_imo_173_four_role.py` for what they actually assert. Only *then* inspect exact SHA workflows. Ask whether prior reports of a 728px→488px print transition, one later green artifact, seven pinned CI regressions and still-open #168/#169 genuinely match code and source evidence.

**Independent rule:** every significant observation includes Parent/Roadmap plain-language purpose, exact raw commit/path/function, what it does/calls/feeds, uncertainty and whether a change actually helps the learner. Never quote a predecessor claim as proof. Stage 1 is not a testing campaign; don't run another bulk test suite to avoid answering the architecture question.

## 4. Mandatory competing-implementation reconciliation map
Do not say “merge both” or choose by higher PR number. Build a real responsibility-and-seam matrix:
| Conflicting / overlapping responsibility | Concrete candidates g5 must inspect | Competing authority question |
|---|---|---|
| Authored teaching + answer/safe-stage semantics | #166 original three-role + renderer changes; #172 print denial; #175 four-role manifests; #177 keyboard/KEY; #178 golden assertions; #180 print test | What is the one authoritative four-role journey, and which file actually owns reveal gating versus merely testing it? |
| Candidate transfer challenge | #175 A and B manifest selections + `blueprint-first-five-transfer.v1.json`, `transfer-comparison-164.v1.json`; #164/#168 author vs independent reviewer | Which candidate survives prior exposure and independent difficulty criteria? Must Stage 1 keep both provisional? |
| Shared diagram responsiveness | `render_core.py` renderer code from #166/#177 vs added `imo_blueprint_first_browser.mjs` checks from #180 | Does a code repair belong in one shared function rather than making a special TEST CSS clone? |
| Mathematics homepage authority | #176 three subtopic `public/`+`docs/` links vs #179 linear-equations route, hub and `.pages-manifest` | Do paths overlap, how are QIDs indexed, which generated artifact serves learners and who owns an approved homepage route? |
| Real original SOF question | Track A `TEST` package/manifests vs Track B #174, source operator #163, source-ref PRs #176/#179, readiness audit #167 | Is any item genuinely original/rights-cleared and admitted? A link is not the question. |
| Generated data / deployment | `build_core_learning_data`, `build_web_data`, `build_test_site`, `build_pages_site`, Core-learning vs TEST data, `public/` vs `docs/` | Which one tool owns each output; is freshness preserved without hand edits and without publishing TEST? |
| Native gate and academic/AT evidence | #178/#180 golden/browser, #171 native owner, #91 generated, #168 academic, #169 manual A4/AT | What is only automated confidence, what is independently accepted, and what blocks release? |

For every row record: **one proposed owner, retained reusable component, any obsolete/duplicate component, conflict seam, Owner benefit, source evidence, acceptance needed and rollback**. If source cannot decide, write OWNER_DECISION_REQUIRED; don't create a hybrid of unrelated source/right modes.

## 5. Your independent purpose — g5 must write it, not adopt g4's
After direct inspection, write **one paragraph beginning exactly**:
> Given the Owner's purpose and this inherited source, I propose...

State what learner experience should work end-to-end, *which precise technical connection is actually missing or unsafe*, what can be reused, smallest bounded change, and why that is more valuable than more tests/draft PRs. Include a plain-language Parent/Roadmap explanation for every module decision. A defensible **NO_CHANGE + authority-blocked** conclusion is valid if the code needs a named writer first.

## 6. Module-change table — concrete source-first hypotheses to test, NOT preselected verdicts
You must independently return a module table with **REUSE, MODIFY, ADD, PRESERVE/LEAVE UNTOUCHED, DEPENDENCY or NO_CHANGE**; the table below is a *starting investigation grid* and may be overturned by actual source:
| Module/function, anchored at assessed source | Provisional action to evaluate | Parent/root reason tied to actual learner outcome | What must be proven before recommendation |
|---|---|---|---|
| `TEST/imo-research/pilots/blueprint-first-five-transfer.v1.json` and two Track A four-role manifests | **REUSE** (both candidates as held previews) | #164/#173 learner concept-to-transfer journey should not be rewritten to mask missing release | Confirm both actual role/content selections and safe pre-attempt stages, no original source admission |
| `Shared/tools/render_core.py` `layout_css` /`fitFigure` / `figure` | **MODIFY conditionally** with one bounded responsive-print repair | #173 asks for legible accessible diagram and truthful A4 learner output | First inspect exact print-mode race, min text floor, cross-subject impacts and sole writer authority |
| `Shared/tools/build_pages_site.py` + `public/mathematics` and `docs/mathematics` mirror | **REUSE** canonical generation; **MODIFY** only if chosen approved route currently missing | #137 asks for reviewed products on respective subtopic homepages | Establish actual deployed artifact and route owner; source/QRT/stage rights must precede live links |
| `TEST/imo-research/pilots/transfer-comparison-164.v1.json` | **PRESERVE / LEAVE UNTOUCHED** without independent reviewer | #164/#168 needs genuine independent D-band/QRT decision | Keep author-proposed field values provisional, no g5 self-signing |
| `Shared/tools/build_core_learning_data.py`, `build_manifest.py`, `build_web_data.py`, `build_test_site.py` | **REUSE** governed generators, **DEPENDENCY** for #91 owner | #127/#137 needs one trustworthy source-to-page projection, not stale generated claims | Trace byte-level outputs, rights and true owner; no manual generated JS |
| `tests/imo_blueprint_first_browser.mjs`, `tests/check_imo_173_a4.py` | **PRESERVE** strong first-frame assertions and previous failure evidence | #173 safe printed learner journey | Identify what browser checks do not establish (real paper/true 200%/screenreader) |
| `#176/#179` homepage link variants | **PRESERVE AS DRAFT** pending independent route owner; **MODIFY** only a selected lawful path | #137 user should find one correct original-source-linked product, not competing routes | Check which routes reflect approved source and actual deployment, no bulk merge |
| `#171` native CI, `#168/#169` review, `#174/#163` source custody | **LEAVE UNTOUCHED / DEPENDENCY** for their named owners | #137 product must be safe, academically sound and rights-cleared | Confirm assignable owners and independent signatures rather than altering their controls |
| Possible small route/registry adapter (only if trace proves missing) | **ADD conditionally** a minimal approved connection, not a new router/framework | #137 respective Mathematics subtopic placement | Only after Owner stage, rights and exact source-page contract; no speculative helper before confirmation |

In your own result explicitly mark each action as REUSE, MODIFY, ADD or PRESERVE and justify it; you are **not** required to agree with g4's suggested dispositions.

## 7. At most three high-ROI candidates — rank them independently, recommend one
Assess each on **user impact, recurrence prevented, effort, semantic risk, dependency and rollback**. Do not prescribe large revamps as XS/S.
1. **Narrow shared SVG print-first-frame correction**, **S (~one day of authorized coding)**, conditional: remove stale width snapshot only if source/trace confirms; keep ≥14px text, untouched stage/KEY logic, immediate/settled containment, cross-subject, rollback on clipping. Benefit: prevents a genuine learner diagram being cut off. Risk: shared renderer behavior; **blocked until valid V3.1 sole-writer scope**.
2. **Seven-case native source/owner triage**, **XS for assignment, remediation possibly S/M/L**. Benefit: avoids falsely passing a branch while enforced historical baseline remains red; needs named code/generated owner, no baseline waiver.
3. **One source-safe Mathematics subtopic route contract**, **XS decision, S later scoped implementation**. Benefit: ensures the Owner's actual learner homepage, not duplicated source-reference draft links; risk: original SOF custody and mode decisions are not yet accepted.
**Provisional single recommendation for g5 to challenge:** candidate **1**, *as a conditional engineering outcome after authority*, not a permitted Stage 1 code change. If actual code already fixes it or serial writer cannot be resolved, explicitly park and recommend the best unblocked course correction instead. Recommend **exactly one** in Stage 1 and explain what evidence would falsify it.

## 8. Preservation boundaries and claims you must not make
- This is not a blind isolated Runner B run and grants no g5 writer/coder, Owner, math/AT reviewer, security, CI baseline waiver, merge or release authority.
- Preserve authored TEST vs publisher-authentic SOF separation, all original private custody/rights, QRT independence and existing pupil learning semantics. No source original text reproduction without permitted custody.
- Preserve pre-attempt withheld solution/stages, hint/repair ordering, ≥14px figure labels, keyboard/screen-reader behavior and real physical A4 acceptance as external gate. Keep Core1B private KEY separate from learner PDF.
- Never hand-edit generated `public/`/`docs/` JS or Pages mirrors or claim a docs tree equals the deployed live artifact; determine actual generator first.
- Never weaken current Guardrails/Canonical or historical pinned-main comparator because a previous engineer reported “0 new vs stacked base.” No fabricated test scores or grade acceptances.
- Keep V3.1 serial `relay/STATE.yaml` selected until legitimately changed by Owner. A missing destination issue number is an authority blocker, not an invitation to choose another route. Preserve all old heads/artifacts as historic.
- Do not open/read the g4 Stage 2 companion file until Stage 1 publication is verified. Stage 2 reconciliation must criticize both g5's own proposals and g4's past decisions against source.

## 9. Evidence and fixtures — architectural orientation, not Stage 1's mission
Inspect **read-only**, pinned at inherited raw SHA:
`TEST/imo-research/pilots/issue-173-track-a-review-handoff.md`,
`TEST/imo-research/pilots/transfer-comparison-164.v1.json`,
`tests/benchmark_imo_173_golden.py`,
`tests/test_imo_173_four_role.py`,
`tests/imo_173_core1b_browser.mjs`,
`tests/imo_blueprint_first_browser.mjs`,
`tests/check_imo_173_a4.py`,
`.github/workflows/imo-track-a-173.yml`,
`tests/test_web_blueprint_projection.py`,
`Shared/tools/quality_gate.py` and the respective `public/docs` route files. Distinguish which checks compare DOM/HTML, A4 PDF structure, keyboard actions, original test names and genuine source admission. Relevant current/raw workflow references to independently inspect *after source*: [Track A #38136898930](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38136898930), [Guardrails #38136898928](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38136898928), [Canonical #38136898937](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38136898937), [older negative Track A #38128440281](https://github.com/reallakshman19/Grade9v3.5/actions/runs/38128440281). Treat green/red claims on issues as **questions to verify**, not automatic ground truth. Do not run new bulk CI to substitute for module-purpose reconstruction.

## 10. Stage 1 publication on the **existing current issue**, required
When your independent source inspection is complete, publish **one** GitHub issue comment on [Grade9v3.5 #173](https://github.com/reallakshman19/Grade9v3.5/issues/173), with the exact title:

**`PLAN_UPDATE — BUDDY_V15_STAGE1_PURPOSE_PROPOSAL`**

Include Owner purpose with provenance grade, current/parent/root/roadmap exact links, assessed inherited raw SHA (and any newly observed divergence), true learner flow, independent proposed purpose, each module decision with plain-language parent rationale, competing responsibility owner map, no more than three ROI choices, one recommended, preservation and unknowns, explicit Stage 2 review questions and planned next implementation *outcome*. The comment is a **proposal, not TASK_EVIDENCE, CHECKPOINT_FACTS, human acceptance or Owner authorization**. Do not start writing code, merging, rerunning suites, or publishing Stage 2.

After actual authorized GitHub publication, **fetch the same issue comment via provider** and hash its **body exactly as returned**: `sha256(UTF8(returned_comment.body))`, including all returned line breaks, excluding JSON quoting, metadata, URL or Markdown rendering. Record the provider comment URL `https://github.com/reallakshman19/Grade9v3.5/issues/173#issuecomment-<real id>`, the 64-character lowercase SHA-256 digest, and the assessed raw 40-hex commit. If cannot publish/read back, say `NOT_PUBLISHED` or `STAGE1_NOT_VERIFIED` and **STOP; do not forge a URL/digest or open g4's Stage 2 file.**

## 11. Exact required final answer and LOG line
Respond in **this exact heading order**:
1. **OWNER WANTED** — actual learner outcome in plain words and provenance.
2. **I FOUND** — only independently verified code/route/module facts, with refs.
3. **THE REAL GAP** — smallest user-visible missing link or risk, not just counts.
4. **MY PROPOSED PURPOSE** — paragraph beginning “Given the Owner's purpose and this inherited source, I propose...”.
5. **MODULES I WOULD CHANGE AND WHY** — REUSE/MODIFY/ADD/PRESERVE matrix with parent purpose.
6. **HIGH-ROI IMPROVEMENT** — up to three candidates, name one as recommended and say dependency, risk, effort XS/S/M/L.
7. **WHAT I WOULD PRESERVE** — originals, learner contract, stage/KEY, native CI, generated and rights gates.
8. **WHAT REMAINS UNPROVEN** — candid UNKNOWN/NOT_RUN and owner/reviewer dependencies.
9. **NEXT IMPLEMENTATION OUTCOME** — a bounded result later engineering should deliver if independently authorized, **not** a claimed merge.

End with **one full LOG line**, literally shaped:
```text
LOG | chat=<g5_chat_id> | agent=g5 | tab=Tab1_track-a-integration | folder=coordination/Session_Oct09/Tab1_track-a-integration | stage=BUDDY_S1 | pub=https://github.com/reallakshman19/Grade9v3.5/issues/173#issuecomment-<real_id>#sha256:<64_lowercase_hex_of_provider_returned_comment_body> | assessed=<40_hex_commit_actually_assessed> | recommendation=<one_candidate_or_NO_CHANGE> | status=PROPOSAL_ONLY | next=BUDDY_S2_GATE
```
If publication/readback failed, use `pub=NOT_PUBLISHED` or `pub=STAGE1_NOT_VERIFIED` **without a fake SHA**, and `next=STOP_STAGE1_PUBLICATION_REQUIRED`. The user explicitly wants this LOG format for traceability. **Only after a genuine g5 Stage1 issue-comment/digest and Stage1 stop** may Stage 2 reconciliation begin; Stage 2 must re-fetch/check that immutable Stage 1 comment body SHA against the provided digest and ensure exact assessed commit.

## 12. Stop boundary and success in the Owner's words
**Stop Stage 1 after the #173 proposal has been published and its provider-returned body has been SHA-256 checked.** No product source write, no test campaign, no invented role grant, no proposal to launch without admission, and **do not open `2026-10-11-g4.md` before Stage 1 stop**. A valid Stage 1 can recommend NO_CHANGE because external authority/source/rights are blocking.

Stage 1 success is an *independent, code-grounded plan* for what the Owner actually said: **“prepare core 2, 1A for them and launch in respective subtopic home page”**, while clearly distinguishing authored TEST pilots from future **authentic source Core2** and showing exactly which small module connections would achieve that outcome after lawful review and authorization. It is **not** success to claim the original product has already launched.

---
**Outgoing file provenance (not a g5 Stage 1 log):** prepared in chat `6acb71eb` by g4, using the BuddyRunner v1.5 LFJ-style intake and independently fetched refs. **No Stage 1 publication exists at file creation.** G5 must make its own, then produce and verify the actual `stage=BUDDY_S1` LOG.
