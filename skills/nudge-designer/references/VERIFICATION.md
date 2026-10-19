# Verification checkpoint — 18 October 2026

## Contents

- [Scope and provenance](#scope-and-provenance)
- [Executed local checks](#executed-local-checks)
- [Fresh-agent pilots](#fresh-agent-pilots)
- [Unexecuted and remaining limits](#unexecuted-and-remaining-limits)
- [Role-adapter extension checkpoint](#role-adapter-extension-checkpoint)
- [Prompt and Applying guidance extension](#prompt-and-applying-guidance-extension)
- [Adaptive support amendment](#adaptive-support-amendment)
- [Task-local context amendment](#task-local-context-amendment)

## Scope and provenance

New standalone `skills/nudge-designer/` package and one path-scoped read-only CI
workflow. Existing skills, NextNudge, AA3 and product behavior are outside the
change. The implementation uses exactly two JSON schemas and a composable profile
library. Agent synthesis is distinct from deterministic support.

The LFEA reference retains public reports and candidate source identity. It does
not reproduce the browser failure here or authenticate the original fixture.
The other three initial cases are synthetic. Three additional synthetic cases
were forward-tested without their answers and then saved as reviewed replays.

## Executed local checks

Python 3.12 with `jsonschema` 4.x:

```bash
python -B -m unittest discover -s skills/nudge-designer/tests -v
```

Result: **49 tests PASS**. They include actual CLI validation and rendering of
every nudge in all seven examples, not just direct function calls. Coverage:

- Both Draft 2020-12 schema documents pass their schema meta-checks.
- Duplicate IDs/JSON keys, non-finite numbers, broken references and cycles fail.
- Stale intent/profile content bindings and invented authority fields fail.
- Declared requirements, constraints, unknowns and outcomes cannot disappear.
- Coverage links must reference their target; relevant constraints reach workers.
- Custom domain operations/evidence work through the CLI without core edits.
- Conditions, meaningful negative cases and all seven brief elements survive.
- Source multiline prose remains visibly quoted; math comparisons display clearly.
- Source/constraint/knowledge changes reach relevant nudges and dependents, while
  an independent export task survives a targeted race-fact change.
- An 80-level outcome hierarchy with 83 nudges validates and retains other work.
- CLI rejects input overwrite and symlink aliases; checks leave inputs unchanged.

Skill Creator `quick_validate.py`: PASS. Python syntax, interface metadata,
local Markdown links, JSON parsing and `git diff --check`: PASS. The package was
initialized using Skill Creator's `init_skill.py`, then replaced with the actual
standalone instructions and resources.

Tests-first evidence: initial execution failed at two missing-module imports;
no behavioral assertion ran in that initial RED. Later, four added revision tests
failed on missed new constraints, knowledge-only sources and scope-basis sources.
Those failures were repaired by sharing actual worker context with impact logic.
Do not describe the import failures as a reproduced product defect.

## Fresh-agent pilots

Three separate agents received raw requests and access to the skill/references,
schemas, profiles and scripts. They were instructed not to read examples, tests
or other agents' outputs. These restrictions are reported execution conditions,
not a sandbox proof. Model/reasoning controls were unavailable; configuration was
recorded UNKNOWN, with no claim of changing it.

| Unseen request | Observed substantive result | Original → final brief words |
|---|---|---:|
| UI + logic: late A under selected B | Source/order diagnostic with intermediate-state contrast; CSV independently eligible; no repair/browser success claim | 2,086 → 989 |
| Grade 11: release from rest | Correct zero-velocity/nonzero-acceleration method; held/released contrast and separate transfer key; learning unknown | 2,716 → 1,346 |
| FEA: mixed-unit axial bar | Reproducible reference and unit-error contrast; conditional numerical comparison; bucket suitability unresolved | 2,151 → 1,036 |

Counts use `len(text.split())`; final counts include the last renderer fixes and
portable source-locator relocation. These combine Designer instruction changes,
authored-object condensation and renderer refinement. They do not isolate a model
effect or demonstrate lower-thinking worker success.

The pilots exposed repeated context, escaped newlines and difficult unknown/math
display. The renderer now quotes multiline text visibly, omits generic profile
checklist duplication, separates conditions and displays UNKNOWN/unselected values.
Agent review condensed the authored objects while preserving original conditions.
Retests also exposed a stale authored coverage link; the agent corrected it, and
the validator now names the offending nudge and target for future corrections.

Portable reviewed artifacts and assessment/checksum notes:

- [UI/logic replay](../examples/forward-ui-logic/ASSESSMENT.md)
- [Education replay](../examples/forward-education/ASSESSMENT.md)
- [FEA replay](../examples/forward-fea/ASSESSMENT.md)

Copies relocate raw-source paths to `case.md` and rebind canonical intent digests.
READ_THIS_RUN records the historical pilot run; a new run must reassess its
sources. Source prose remains data and cannot grant current authority.

Parent readback independently checked the arithmetic from supplied givens using
Fraction/standard Python arithmetic: the forward bar gives +0.25 mm displacement,
175/12 MPa stress and 437.5 N·mm energy. Grade 11 pre-impact time and transfer
quantities agree under g = 9.6 m/s². This is arithmetic checking, not an independent
solver or pedagogical outcome study. A unit-error case must compare the original
quantity conversion; dimensional consistency alone cannot detect a wrong magnitude.

## Unexecuted and remaining limits

At this recorded prepublication checkpoint, hosted CI and Python 3.10 execution
are **NOT_RUN**. The workflow runs the focused suite on Python 3.10 and 3.12;
consult the delivery PR for actual hosted results after publication.

No actual LFEA browser investigation/repair, ordinary UI journey, narrower-worker
implementation, finished teaching pack, learner study, FE solver or bucket design
qualification was executed by this package. No UI/import adapter, automatic
dispatch, authorization service or change to other protocols is included.

Worker briefs still contain technical IDs and repeated necessary scope/evidence
limits. Even the improved teaching brief is much longer than the intended
learner-facing explanation. Inspect usability in real work before adding UI or
claiming that a lower-capability worker can succeed. Structural validation,
declared coverage and content digests do not establish semantic adequacy, source
completeness, authenticity, acceptance or permission.

## Role-adapter extension checkpoint

The preceding sections preserve the original v1 prepublication record. The Owner's
later broad-application request adds role/capability, manual surface and native
return adapters, scoped entirely to this package. Exactly two schemas remain;
`intent/v1` and old `plan/v1` stay valid, with explicit `plan/v1.1` team support.

Current local result: **84 tests PASS** on Python 3.12. All original checks remain,
with additional coverage for seven audiences across UI/logic/education/FEA, task
requirements and guidance, all five manual surfaces, strict issued binding,
same-participant review conflicts, transitive dependency/review propagation,
source discrepancies, unknown tools/configuration, binary reference-only reports,
Unicode/CRLF content preservation, malformed returns, no auto-acceptance, no input
mutation, missing dependency fallback and actual CLI exchanges. A runtime check
executes the unchanged original fixture function and carries its actual result
through intake/review/successor views; it does not implement a repair.

Tests-first adapter checkpoint: two missing imports initially prevented behavioral
assertions from running. Later added assertions exposed real adapter defects:
indirect dependents listed as independent, absent native content/attempts in the
review view, ignored per-task guidance in the normal renderer, Python numeric
equality accepting nonexact binding types, and a combined dependency/review cycle.
Those assertions failed before the corresponding fixes and now pass. These are
adapter defects, not reproduced product failures.

Three additional fresh task threads performed actual bounded work: unchanged
source execution (four calls/two completion orders), specialist study drafting and
nine exact-arithmetic checks, and separate local review with eight review checks
and seven numerical checks. No model/effort override or formal qualification was
observed. The reviewer used an independent oracle/Decimal recomputation after
seeing reports; this is not blind review or authenticated independence.

The specialist caught a stale 20 m/s handover against the supplied 18 m/s case;
the reviewer also caught an unsupported learner-prerequisite FACT. The Designer
read the actual artifacts, corrected the handover, reclassified the item as a
PROPOSAL and kept learning/transfer outcomes unresolved in working revision 2.
All 65 archived files remain exact, including 22 supplied review inputs. Each
native return still binds to its issued snapshots; the historical specialist
return is rejected against the revised plan. Coverage records partial evidence,
not accepted outcomes. See [the full role-cycle reference](../examples/adapter-cycle/ASSESSMENT.md).

The execution scripts/receipts retain original machine paths and are archival;
automated tests replay structure/binding/hash checks without rewriting that history.
The portable NOT_RUN team fixture remains distinct from actual execution evidence.
Current Skill Creator validation, syntax, interface metadata, local-link and diff
checks are run before publication; the delivery PR records their results and
hosted Python 3.10/3.12 CI. No live UI repair, actual learner assessment, solver or
engineering acceptance, native import, automatic transport or new authority is
claimed by these adapters.

## Prompt and Applying guidance extension

The next Owner amendment requests role prompts, golden fixtures and the thought
process for applying the flows, with superfluous assumptions/traps made explicit.
Nine copyable resources cover seven roles, a seven-element assignment and native
result aid. The Owner resource includes short general, narrower-worker, recovery
and onboarding entry variants. [Applying guidance](APPLYING_GUIDANCE.md) explains
purpose/uncertainty/evidence decisions, assumption discipline, selective warnings,
support choice, reconciliation and 14 concrete traps. It imposes no new stages,
team size, runtime configuration, authority or approval ritual.

[Seven paired raw/golden references](../examples/guidance/INDEX.md) cover UI,
event order, teaching, physical models, cold onboarding, mixed teams and findings.
They are synthetic semantic references, not machine-graded unique answers
or newly executed product evidence. Exactly two formal schemas remain; runtime
and schema contracts are unchanged. The existing 84 checks pass locally on Python
3.12. Skill validation, syntax, metadata, local links, reference arithmetic and diff
checks pass. Hosted results for this exact extension are recorded on the draft PR.

Four fresh task threads applied the prompts without golden/example answers:
worker execution, specialist derivation/arithmetic, successor onboarding and UI
assignment design. A fifth fresh Designer retested the same raw case after
proportionality guidance. The worker executed six transitions and distinguished
source identity from equal revision numbers. The specialist retained 160 GPa,
computed 0.405 mm and 72 MPa, and exposed the 200 GPa substitution. The successor
kept production acceptance unverified and honored the onboarding wait, reporting
missing `jsonschema` as NOT_RUN. A later parent check with isolated dependencies
validated its objects without rewriting that receipt.

The first UI brief was useful but 1,170 words; the fresh retest was 927 words.
These are observed lengths, not controlled model effects or usability acceptance.
Parent review found an unnecessary inferred screenshot mapping in the retest;
the final guide clarifies coordinate-contract evidence and a separate compact
operational brief removes that assumption. Native outputs are preserved. That
last clarification is parent-reviewed, not another fresh execution. Parent replay
also reproduced the six worker transitions and specialist values; it is not blind
review or physical validation. [Actual artifacts and assessment](../examples/guidance-forward/ASSESSMENT.md)
preserve 27 archived files and all nine raw inputs byte for byte.

No low-thinking model was selected/qualified, no live UI repair or native journey,
FE solver, learner outcome or external dispatch was performed, and no broader
reliability claim follows from these local tasks. Actual host configuration and
formal qualification remain UNKNOWN. Prose guidance still needs substantive use;
filled templates, golden wording and compatibility PASS cannot establish it.

## Adaptive support amendment

The later Owner request generalizes the NLM pilot lessons, especially for limited
or unestablished task fit, and authorizes updating then merging after verification.
The new change starts from main; the separately held pilot-specific PR #439 is
unchanged. Its linter and fixed report/weakness rules are not imported. Runtime,
schemas, APIs and profiles remain unchanged, with exactly two formal schemas.

Added adaptive support guidance, selective role/assignment instructions and G08–G10
raw/golden references. These cover evidence for conceptual factors, strict declared
input interpretation and a correct computation attached to the wrong revision.
The golden values are synthetic expected distinctions, not execution receipts.
The worker prompt now permits a self-contained brief without loading the whole
process library. No fixed calibration gate, pass count, weakness quota or binary
verdict ban was added.

Four fresh raw-task applications produced actual artifacts. The first three used
the guide/role resources; the fourth used only its short assignment and payload.
The worker counted 4/2 after declared cp1252 decoding and retained both valid
claims. The reviewer rejected zero acceleration while retaining velocity −3.60 m/s
under the supplied model. The Designer traced issued R20 versus delivered R19,
retained the useful R19 count and drafted a source-bound correction. Its optional
schema/render startup was blocked by missing `jsonschema`; NOT_RUN remains, with
no intent/plan files or subsequent parent validation claimed. The brief-only worker
counted 0/3 including the empty record, reporting one match and one mismatch.

Parent source-derived checks confirmed the material quantities and worker file
receipts. All nine raw inputs and 22 archived native/input files remain exact.
See [actual artifacts and assessment](../examples/adaptive-forward/ASSESSMENT.md)
for provenance, checks and limits. There was no corrected-task dispatch, production
or learner outcome, selected low-thinking configuration or formal qualification.
Different tasks/sessions/instruction exposure cannot establish a causal support or
model comparison. A usable bounded result is not broader capability acceptance.

The existing 84 compatibility checks passed locally on Python 3.12. Skill Creator
validation, syntax/JSON/metadata, local-link, reference-value, archive-identity and
diff checks are performed before publication; the delivery PR records exact-head
hosted Python 3.10/3.12 results and remote readback before the authorized merge.

## Task-local context amendment

The Owner's 19 October request adopts qualified fresh-NLM lessons and asks about
small fresh-worker nudges. This amendment changes guidance, prompts and fixtures
only; runtime/schema/profile contracts remain unchanged. The focused local suite
passed **84 tests** on Python 3.12. Tool compatibility is separate from the
semantic application evidence and does not establish lower-model capability.

The [actual isolated role cycle](../examples/isolated-forward/ASSESSMENT.md) retains
Oracle preparation, a parent-assisted 1,065 → 484 word view, brief-only production,
prompt-only separate assessment and continued-Oracle evidence reconciliation.
Original inputs/native results stayed exact. The assessor's UNKNOWN full-artifact
coverage was preserved and bridged explicitly rather than relabeled independent
review. This is a synthetic default-runtime observation, not low-thinking-model
qualification, guaranteed blinding, automatic compression or a causal effect.

Four new paired references (G11–G14) and a pre-send self-check address provenance,
exposure, small task context, multipart verdicts and identity/transport. The reported
NLM case retains absent-original-artifact limits. Runtime, schemas and APIs were not
changed; the separate Task Decomposer change is not a dependency of this skill.
