# Oracle slicing prompt

The Owner can use two lines:

> Use prototype-first to slice [aim] into steps that each end in something I can run.
> Write the next step as a slice card on my real inputs, and say how much checking it needs.

```text
Use Prototype-first at {{SKILL_ROOT}}/prototype-first (SKILL.md, schemas/slice-card.v1.json,
examples/CIIFR-S1.json as the benchmark R0).
Aim, in the Owner's words: {{aim}}
Real inputs and where they live: {{names and folders; never links}}
What the user can do today: {{current can-do lines, or "nothing yet"}}
Earlier benchmarks: {{keeps}}

Continuity when workers or the Oracle change:
- Preserve the slice/WBS identity; bind a fresh session to a new assignment generation.
- Carry the baseline, decisions/alternatives, pending returns and exact next action.
- Confirm accessible real inputs and actual delivery; reconcile old execution before
  activating a successor on the same write surface. Isolate outputs while uncertain.
- Carry authorship and evidence scope forward. At Oracle cutover explicitly adopt
  ongoing assignments and preserve the next two connected cards.
Use the optional Oracle Continuity Protocol at {{SKILL_ROOT}}/oracle-continuity/PROTOCOL.md;
native slice cards/reports remain the operating format unless JSON is selected.

1. Slice the aim into thin steps. Each step ends in something the user runs on the
   real inputs, within a timebox of at most 40 builder hours (aim for hours, not days).
   Order steps by what the user most needs to do first; infrastructure the user cannot
   see becomes the hardening of a visible step, not a step of its own.
2. Write the next step as a slice card (state written). Set check by consequence:
   independent only where a mistake would reach the real world, and say why.
3. Name the builder you recommend (a browser chat, or a local agent when the inputs
   live on the user's computer) and what its capability probe must confirm.
4. After the user tries a step, turn their reaction into the next card, and record
   any direct steering by the user as a visible card or WBS change.
Keep WBS numbers stable; never renumber when an agent changes. Do not demand proof
before a prototype exists; the evidence rules of the delivery protocol apply from
hardening on and to every independent check.
```
