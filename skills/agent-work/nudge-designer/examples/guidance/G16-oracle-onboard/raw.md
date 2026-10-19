# G16 — Oracle OnBoard application inputs

Synthetic teaching cases inspired by an instruction/continuation discussion. They
do not assert any real project's current source, PR, CI or acceptance status.
Use the Oracle OnBoard guide/template. Give a fresh recipient only the chosen
case and relevant source artifacts; withhold golden.md and completed returns.

## A — Stable direction, unfinished parent outcome

Owner: “Keep draft masses when I leave and return to Review. Drafts are not
accepted decisions. I still need a trustworthy full-model native export later.”

Supplied source record at fixture revision A1:

- `review-state.js:12–28` stores drafts in a Map created inside each render.
- `workspace.js:4–20` owns a model-scoped store used across navigation.
- Six model components exist; the Review filter shows four. No rule permits
  excluding the other two from a later export census.
- Match-1/Final acceptance is explicit. Skip/UNKNOWN does not approve zero mass.
- A reported focused persistence test passed on a different earlier candidate.
  It does not establish current browser persistence or native export correctness.

Allowed work: persist draft edits through navigation in the model-scoped store;
retain model separation and explicit zero. No acceptance-policy or native export
implementation is authorized. A checkout and test runner are available. Browser
availability has not been established.

Prepare a receiver instruction for one bounded persistence repair. Include useful
evidence, a contrary case, remaining outcome and a conditional next action.

## B — Current source differs from the explanation

Owner: same draft/acceptance outcome. The brief's proposed explanation is still
“render-local Map is lost; move drafts to workspace.” Current candidate is B2.

Accessible source at B2 instead shows:

```python
def save_drafts(workspace, model, edits):
    workspace[model] = {key: value for key, value in edits.items() if value}

def load_drafts(workspace, model):
    return dict(workspace.get(model, {}))
```

Navigation reuses `workspace`; a separate model uses another key. Owner's original
rule allows an explicit zero draft, rejects negative/non-finite values upstream,
and distinguishes absent/None from an explicit zero. Existing input validation
is outside this repair. The supplied operation is not the acceptance store.

The current authorizing instruction is to repair draft persistence in this
function while preserving model separation. You may run local Python and edit a
copy of the fixture. No browser or full product is supplied. Show actual checks
and a relevant contrary case; return to the original outcome with the next action.
Use the OnBoard instruction as working context, not as an unchallengeable diagnosis.

## C — Completed context flow, missing runtime route

A completed three-pass record contains a usable source model, checked candidate
C3 and a failing original-pointer test. The next task is authorized: reproduce
the remaining ordinary-pointer failure and report a discriminating trace.

The successor's host returns `browser route unavailable` when opening the app.
Source files and the failing receipt are accessible. Programmatic DOM activation
is reported to work; it is not the original pointer scenario. The browser test
itself has not passed. Owner did not authorize weakening the assertion.

Prepare the next instruction or return. Retain completed-flow reuse, actual
attempt/restriction, useful available work, unresolved proof and feasible next route.
