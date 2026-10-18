# Verification checkpoint — 18 October 2026

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
