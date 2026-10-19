# Generate options that demand the intended thinking

Use for selected-response learning items, with the original tile/learning target,
verb, learner level, allowed content and answer basis. This is task-specific
support, not a universal teaching phase count or a new delivery protocol.

## Preserve the verb in the assignment

| Required action | What the options must let the learner choose | Insufficient substitute |
|---|---|---|
| Explain | A causal relation/reason under the stated conditions | Bare numbers or labels when choosing a reason is the actual target |
| Justify | An argument linking the claim to a relevant principle/evidence | A true fact or final value with no supporting relation |
| Retrieve/recognise | The requested fact, unit, symbol or sign | Requiring a causal essay where the target is recognition |

Read the source definition before choosing a format. A verb alone is not a complete
pedagogical model; local curriculum/task definitions govern. For a compound demand,
retain its parts and the existing roll-up rule. Banning numeric-only options is
not sufficient: all four sentence options can still test retrieval instead of
explanation. A complex or long option does not establish higher demand.

Put verb, intended response type, answer basis and a meaningful off-demand contrast
in the task design. Reserve an unresolved interpretation with the available
Designer/Oracle; do not let a narrower generator invent the target to fit its draft.

## Generator self-check before handing over

The generator runs a script over its actual final items to compute option word
counts and flag question words shared only by the keyed option. Use
`nd_item_cues.py` below or a stated equivalent script. Keep the exact input/revision,
actual output, counting rule and dispositions. If execution is unavailable, report
NOT_RUN and the affected check; do not claim a judge ran it for you.

Inspect each flag and the item itself:

- Longest-key cue: is the correct option more detailed or uniquely qualified?
- Reasoning-marker cue: do because/therefore or similar words reveal the key?
- Parallel grammar: do all options fit the stem with comparable form?
- Verb-option match: does choosing an option actually require the specified action?
- Question-word cue: could overlap identify the key without subject knowledge?

Do not ban reasoning words needed for explain/justify items. Balance plausible
alternatives without adding wrong science or deleting essential conditions. A
technical term shared with the correct answer may be legitimate; inspect its
selection effect and record the decision rather than blindly replacing it.
A shared-word/length screen does not establish the existence or correctness of
an alternative. Re-run affected checks after a revision and retain correction
history. A format fix must preserve the original concept, demand and answer basis.

Return the final items, script report, manual verb/grammar/cue assessment, each
flag's disposition and unresolved scope. Mark your own judgment SELF-ASSESSED.
Do not wait for a judge to discover mechanically detectable defects. Subject
correctness and actual learner transfer remain separate assessments.

## Optional helper and selected profile

Select profile `selected-response` alongside an appropriate domain profile when
rendering such a generator brief. Its concrete pre-return method reaches the
rendered assignment. Existing profiles and bindings remain unchanged. The Designer
must still fill the specific target and input conditions; the renderer does not
infer task family from a few words in the Owner request.

The local helper takes ordinary JSON, not another required plan/schema:

```json
{"items":[{"id":"SYN-UNIT","verb":"retrieve","question":"Which unit represents force?","options":[{"id":"A","text":"N"},{"id":"B","text":"J"},{"id":"C","text":"Pa"}],"answer":"A"}]}
```

```bash
python scripts/nd_item_cues.py --items final-items.json
python scripts/nd_item_cues.py --items final-items.json --max-words 12
```

Use the second command only if the actual task stipulates that limit. Words are
whitespace-separated tokens; standalone signs and units count as tokens. Shared
words include all casefolded Unicode words; a separate subset excludes a small
English stopword set for inspection. There is no stemming, multilingual grammar
analysis or semantic inference.
Reasoning-marker and numeric-only checks are conservative signals. A value with
a unit may need manual inspection even when not automatically flagged.

Exit 0 means screening ran, even if it found flags. Exit 2 reports invalid input.
The report always leaves format, verb fit and physics unapproved. A no-flag report
can hide a wrong key, unsupported model, off-demand item or an obvious distractor.
No provider call, artifact rewrite or publication is performed.

## Evidence basis

The Owner supplied G6–G8 lessons on 19 Oct 2026: reported verb-fit counts changed
from 2/7 in G7 to 5/5 in G8, and two G8 issues were shared-word cues. These reports
motivate this support; the source artifacts were not independently inspected here,
and changes between episodes do not establish a causal effect or model capability.
The reported 15/15 agreement with the Owner is not a learner-understanding measure.
Use the synthetic [raw/golden case](../examples/guidance/G14-option-demand/raw.md)
to inspect these distinctions; do not supply its golden verdict during discovery.
