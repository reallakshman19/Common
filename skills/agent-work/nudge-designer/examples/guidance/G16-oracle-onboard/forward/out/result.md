# ONBOARD-DEMO-01 — local persistence repair

**Local task status: PASS.** The issued B2 source loses explicit zero drafts. The repaired save filter preserves zero and ordinary nonzero values while excluding `None`. All seven focused local tests pass. Actual application navigation, full-model native export, Owner acceptance, and release remain unproven.

## Inputs and identity

All commands below ran in `/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/`. All writes stayed in that folder. No other histories or reference cases were consulted; no delegation was used.

| Input | Original path | Verified SHA-256 before editing |
| --- | --- | --- |
| Owner record | `/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/OWNER.md` | `dc42488aa420006c253f0437ba89039a1b8930c202871727cb6cc0ba6164c7e5` |
| Candidate B2 | `/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/drafts.py` | `3242f3fd9ba204045000a732f04f7a7adc4ca9ca2fcb30f450275b630c43df2a` |

Commands: `cat OWNER.md drafts.py`, `python3 --version`, and `sha256sum OWNER.md drafts.py` all exited 0. Python reported `Python 3.12.14`. Both digests matched the issued identity. A separate Python byte comparison against the issued B2 literal returned `MATCH` before editing. No input mismatch or tool-readiness error occurred.

The following preserves the issued B2 source bytes as UTF-8 text with LF line endings and exactly one final newline:

```python
"""Synthetic B2 persistence operation; upstream validation is not represented."""


def save_drafts(workspace, model, edits):
    workspace[model] = {key: value for key, value in edits.items() if value}


def load_drafts(workspace, model):
    return dict(workspace.get(model, {}))
```

## Diagnosis and pre-repair evidence

- **FACT — source inspection:** B2 already assigns a new dictionary to `workspace[model]`; `load_drafts` reads that model entry and returns a dictionary copy. The supplied functions do not support the earlier render-local-Map explanation. No workspace migration was justified.
- **CLAIM — historical only:** the Owner record mentions a predecessor's focused pass on an earlier candidate. No B2 receipt accompanied that claim, and it was not counted as execution evidence.
- **HYPOTHESIS checked locally:** the truthiness condition removes explicit numeric zero along with `None`. The following runtime observation confirms that defect in B2.
- **UNKNOWN:** whether callers save before leaving Review, retain the same workspace, or use the correct model. No caller or full application was supplied.

Before changing `drafts.py`, this exact command exited **1** at the Owner-required assertion:

```sh
python3 -B - <<'PY'
from pathlib import Path
import hashlib

issued = b'''"""Synthetic B2 persistence operation; upstream validation is not represented."""\n\n\ndef save_drafts(workspace, model, edits):\n    workspace[model] = {key: value for key, value in edits.items() if value}\n\n\ndef load_drafts(workspace, model):\n    return dict(workspace.get(model, {}))\n'''
actual = Path('drafts.py').read_bytes()
print('Issued B2 byte comparison:', 'MATCH' if actual == issued else 'DIFFERENT')
print('Observed B2 SHA-256:', hashlib.sha256(actual).hexdigest())
assert actual == issued
from drafts import save_drafts, load_drafts
workspace = {}
edits = {'explicit_zero': 0, 'normal': 12.5, 'unset': None}
save_drafts(workspace, 'model-a', edits)
loaded = load_drafts(workspace, 'model-a')
print('Input edits:', edits)
print('Loaded drafts:', loaded)
print('Explicit zero present:', 'explicit_zero' in loaded)
print('Normal value:', loaded.get('normal'))
print('None key present:', 'unset' in loaded)
print('Absent key present:', 'absent' in loaded)
assert loaded == {'explicit_zero': 0, 'normal': 12.5}, 'Owner-required explicit zero was lost'
PY
```

Observed stdout:

```text
Issued B2 byte comparison: MATCH
Observed B2 SHA-256: 3242f3fd9ba204045000a732f04f7a7adc4ca9ca2fcb30f450275b630c43df2a
Input edits: {'explicit_zero': 0, 'normal': 12.5, 'unset': None}
Loaded drafts: {'normal': 12.5}
Explicit zero present: False
Normal value: 12.5
None key present: False
Absent key present: False
```

Observed failure: `AssertionError: Owner-required explicit zero was lost`. This was an intentional failing behavior check, not a Python/tool availability error.

`test_drafts.py` was then added and run against unchanged B2 with `python3 -B -m unittest -v test_drafts.py`. Exit code: **1**. Six tests passed; the zero/nonzero round-trip test failed at line 16:

```text
AssertionError: {'normal': 12.5} != {'zero': 0, 'float_zero': 0.0, 'normal': 12.5}
- {'normal': 12.5}
+ {'float_zero': 0.0, 'normal': 12.5, 'zero': 0}

Ran 7 tests in 0.010s

FAILED (failures=1)
```

## Actual change

Only the save predicate changed:

```diff
-    workspace[model] = {key: value for key, value in edits.items() if value}
+    workspace[model] = {key: value for key, value in edits.items() if value is not None}
```

`None` entries are omitted and absent keys are never synthesized. Explicit numeric zero values retain their supplied values and types. The public signatures, supplied workspace owner, per-model storage, save replacement semantics, and `load_drafts` dictionary-copy behavior remain intact. No merge architecture, export, acceptance logic, browser scaffolding, or upstream validation was added.

Changed files:

- `drafts.py` — repaired save predicate.
- `test_drafts.py` — added seven focused local tests.
- `result.md` — this native return artifact.

Final digests from `sha256sum OWNER.md drafts.py test_drafts.py` (exit 0):

```text
dc42488aa420006c253f0437ba89039a1b8930c202871727cb6cc0ba6164c7e5  OWNER.md
388a475fd473f8031df16f1a9d9eb8dc651d6717b3ed7fb581d3ff808bd64484  drafts.py
f6b6b48d1fe58e6d667d5a4a3f6fa20ef4b0a33e581a87fdfceeae92dc009ee0  test_drafts.py
```

`OWNER.md` remained unchanged. Final source inspection used `cat drafts.py test_drafts.py` (exit 0); it confirmed the single predicate edit and unchanged `load_drafts` implementation.

## Post-repair runtime evidence

The same test file and expectations were retained. Command: `python3 -B -m unittest -v test_drafts.py`. Exit code: **0**.

```text
test_explicit_zero_and_nonzero_survive_round_trip (test_drafts.DraftPersistenceTests.test_explicit_zero_and_nonzero_survive_round_trip) ... ok
test_loaded_dictionary_is_a_copy (test_drafts.DraftPersistenceTests.test_loaded_dictionary_is_a_copy) ... ok
test_none_and_absence_do_not_become_zero_drafts (test_drafts.DraftPersistenceTests.test_none_and_absence_do_not_become_zero_drafts) ... ok
test_none_only_and_empty_saves_replace_with_empty_drafts (test_drafts.DraftPersistenceTests.test_none_only_and_empty_saves_replace_with_empty_drafts) ... ok
test_save_replaces_previous_drafts (test_drafts.DraftPersistenceTests.test_save_replaces_previous_drafts) ... ok
test_saving_one_model_does_not_disturb_another (test_drafts.DraftPersistenceTests.test_saving_one_model_does_not_disturb_another) ... ok
test_unknown_model_loads_empty_without_creating_entry (test_drafts.DraftPersistenceTests.test_unknown_model_loads_empty_without_creating_entry) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.007s

OK
```

These checks establish the following local behavior:

| Case | Observed result |
| --- | --- |
| Explicit integer `0`, float `0.0`, and ordinary `12.5` | Survive save/load with supplied values; zero types also checked |
| `None` and an absent key | Neither becomes a zero draft or appears in the loaded dictionary |
| Save model A after model B | Both retain their separate values |
| Unknown model | Loads as `{}` without creating a workspace entry |
| Mutate a loaded dictionary | Stored values and subsequent loads remain unchanged |
| Save over prior model drafts | Replaces prior entries, without merging |
| Save only `None`, or save an empty dictionary | Replaces that model's drafts with an empty dictionary |

## Limits and continuation

| Outcome | Status and evidence limit |
| --- | --- |
| Bounded persistence repair | **PASS** — reproduced B2 zero loss; same focused tests pass after repair |
| Leaving and returning to Review in the real app | **NOT_RUN; UNKNOWN** — no browser, caller, or full app supplied |
| Correct caller workspace/model and save timing | **UNKNOWN** — local functions cannot settle this |
| Full-model native export | **NOT_RUN** — still required later; not implemented or validated here |
| Owner acceptance and release | **NOT_RUN; UNKNOWN** — no acceptance or release was performed |

The local result does not establish navigation persistence or an accepted decision. The fixture is synthetic and establishes nothing about an intended model configuration. No unrelated finding warranted expanding this task.

**Next justified action:** the Owner or an authorized integrator should validate leaving and returning to Review in the real app using explicit zero and nonzero drafts, `None`/absence, and separate models. The Owner record authorizes this local repair; real-app integration must be performed by an actor with access and the appropriate integration authority. No real-app action was attempted because no full app/browser was supplied. The feasible route is to run the scenario in that environment with this repaired candidate.

If navigation still loses drafts, that observation changes the recommendation to tracing the caller's save invocation, workspace lifetime/identity, and model identifier before proposing more persistence changes. If focused local checks fail under integration inputs, retain the exact input and runtime witness and reassess the relevant local assumption. If navigation passes, the Owner can evaluate acceptance separately and commission/validate the still-needed trustworthy full-model native export. This task does not confer acceptance or release authority.
