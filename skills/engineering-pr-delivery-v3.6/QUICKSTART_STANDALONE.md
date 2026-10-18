# Standalone v3.6.1 — Owner's one-page pilot

Use a **throwaway Git repository**, not a live project. Work with one
coding agent; there is **no TeamCoordinator**, shared registry, chat-send
route or CoordinatorLandingpage access. The Owner approves every scope,
review and merge. The agent never approves its own work.

**Windows shells:** Commands work in **Git Bash** and **PowerShell 5.1**.
Open either shell and change directory to this skill folder:
`skills/engineering-pr-delivery-v3.6` in your Common checkout. Use
Python 3 and Git. **One-time prerequisite**, if PyYAML is missing:
run `python -m pip install "PyYAML>=6.0,<7.0"` from this folder.
This dependency install may access a package index; it is **manual
setup**, not one of the offline/read-only pilot commands below.
Check the installed Python and PyYAML first (expected exit 0).
If this check reports `No module named yaml`, **use `py` on Windows**
if `python` fails the PyYAML check: try `py -c "import yaml;print(yaml.__version__)"`.
Use the *same* interpreter (`py` or `python`) for the guide commands,
and run `py -m pip install "PyYAML>=6.0,<7.0"` if that interpreter also
lacks the dependency. The commands below show `python` for consistency.

```bash exit=0
python -c "import yaml;print('PyYAML '+yaml.__version__)"
```

Every executable `bash exit=N` fence is a shell-neutral Python command
with expected exit N (0 = success; 1 = intentionally unqualified score);
the tag **does not require** Git Bash instead of PowerShell. Allowed
non-command fences (`yaml`, `text`) are examples only. All these
pilot command blocks run **from this skill folder**, are local
read-only or dry-run and never post to GitHub.

**Windows paths:** Replace `__NAME__` tokens with the actual approved
values. In quoted `python -c` commands use **forward slashes**, e.g.
`C:/pilot/my-repo/relay/AIM/MY-WORK.yaml` and `C:/pilot/my-repo`.
Do **not** paste `C:\pilot\my-repo`: backslash escapes can break
Python strings and `os.chdir` (WinError 123). Quote paths with spaces.
The temporary-repo and measurement examples are **not** Owner or CI
evidence; use real sources for an actual pilot.

## 1. Standalone label

### 1A. Create the label file in `relay/AIM/`

**Do this before validation.** In the throwaway repository, create
the folder `relay/AIM/` and save the Owner-approved **full** master
label at `relay/AIM/<WORK>.yaml`. Replace `<WORK>` with the actual
label `work:` value, including matching case: for example,
`C:/pilot/my-repo/relay/AIM/MY-WORK.yaml` for `work: MY-WORK`.
Do **not** put the file at repository root, in `relay/` alone, or
use `<WORK>` literally: the validator checks this exact directory,
filename and work identity. **The validator also rejects any `<...>`
text inside the real label**, even in a genuine descriptive sentence,
as an unresolved placeholder. Write `FILE` instead of `<file>`, or
rephrase without angle brackets. These angle brackets appear only in
this guide's illustrative placeholders, not in the final YAML label.
The top-level selection is:

```yaml
mode: standalone
```

Also set your throwaway `repository: owner/repo`, genuine O1–O5
outcomes, work name, label hash and Owner constraints. Without a
mode, the tool deliberately uses coordinator mode. Keep an explicit
plan with `parent: owner/repo#N`, matching label binding and child
tasks. **Never** copy the checked sample's identity as Owner approval.

Validate the label offline (expected exit 0):

```bash exit=0
python scripts/lifecycle_v36.py validate-label "__LABEL__"
```

Validate the matching plan offline, **without** creating issues
(expected exit 0):

```bash exit=0
python -c "import sys;sys.path.insert(0,'scripts');from lifecycle_v36 import load_label;from decompose_v36 import load_plan; print(load_plan('__PLAN__',load_label('__LABEL__'))['parent'])"
```

## 2. Freeze the Owner's criteria

**Agent's first reply:** restate every MUST, CONSTRAINT and human
JUDGMENT from the *actual initial prompt/issue* as `CRITERIA v1`.
Each numbered line needs its ID, type, **quoted source words**, a
measurable outcome after the arrow and a source reference; include
the closing inventory and source-coverage total. The **Owner confirms**
the precise words, numbers, exclusions and decision rights *before*
implementation. Preserve the confirmed block unchanged, with its
source URL and digest. A changed aim needs an attributable new freeze.
The required first line is exactly
`CRITERIA v1 · <WORK> · FROZEN <date> by Owner · source: #N <text>`
(replace angle fields in the **criteria**, not literally in the label).
A measured row looks like
`AC1 MUST "Add a word-count CLI" → CLI runs and tests pass · tool + tests`.
The source can contain a comma; retain the full text after `source:`
as the authority for the companion.

Check the local frozen file (expected exit 0):

```bash exit=0
python -c "import sys;sys.path.insert(0,'scripts');from pathlib import Path;from criteria_v36 import parse_criteria_v1; print('source coverage='+parse_criteria_v1(Path('__CRITERIA__').read_text(encoding='utf-8'))['source_coverage'])"
```

Coverage such as 15/15 means all **declared** clauses are present;
it does not prove their wording matches the actual Owner prompt.
Do not use #430's checked sample as your project's frozen criteria.

## 3. Child task evidence and SELF-CHECK v2

Agent creates tests first, records the RED commit and baseline/head
full-suite results, and links the real child issue and PR. Publish a
**separate SELF-CHECK v2 companion first on that real child issue**.
The required header is
`SELF-CHECK v2 · <TASK> · owner/repo#N` followed **immediately** by
`Basis: CRITERIA v1 · source #N <text> · candidate owner/repo@<sha40>`.
The Basis source must match the CRITERIA `source:` **exactly**,
including commas, repository spelling and spacing. Then provide
one `Criterion: ID → STATE · proof: source` per frozen criterion,
plus `Score: n/d · claim: PARTIAL|BLOCKED`, exact candidate,
before/after test references, diff and pending Owner decisions.
Mark unrun or unreviewed criteria UNKNOWN; never invent proof.
Human judgment is recorded but never machine-approved.

Prepare the **unchanged eight-line** native TASK_EVIDENCE locally
(expected exit 0). Substitute the true tested SHA, Proof PR URL,
real child issue/task and real test totals; don't post this example:

```bash exit=0
python scripts/lifecycle_v36.py render-evidence --outcome O1 --for-user "__BENEFIT__" --proof "__PROOF__" --task-id "__TASK__" --issue-ref "__CHILD__" --candidate "__CANDIDATE__" --tests-passed __PASS__ --tests-run __RUN__
```

Once real provider evidence exists, post those **exact eight lines**
on the child with a `Self-check: <companion permalink>` reference
inside the existing `For the user:` line, never a ninth line.
Keep `Proof:` as the real PR/commit link, and append the mandatory
terminal LOG in its own location. **No command above posts anything.**
There is no `--apply`, authorization or GitHub write in this page.

## 4. Run the A13 checkpoint gate

Freeze `policy.json` in the **base Git commit** of your throwaway
repo: its allowed `paths`, `ci_workflow`, `ci_pattern`,
`protected` and `forbidden_literals`. Commit a test-only RED first,
then the fix. The checker insists base/head Git copies of the
policy match and inspects 9 categories. Read failures rather than
editing the policy after the fact.

Run the actual `a13_check_v36.py` from this skill folder. The
Python wrapper changes only the process's local working directory
to your throwaway repo; **no GitHub call or write** (expected exit 0):

```bash exit=0
python -c "import os,runpy,sys; p=os.path.abspath('scripts/a13_check_v36.py'); sys.path.insert(0,os.path.dirname(p)); os.chdir('__REPO__'); sys.argv=[p,'--base','__BASE__','--head','__HEAD__','--scope','policy.json']; runpy.run_path(p,run_name='__main__')"
```

**Windows:** `core.autocrlf=true` is fine. The checker compares
Git blobs, not worktree line-ending bytes. Temporary fixture repos
pin `core.autocrlf=false` and write explicit LF bytes; the test also
covers CRLF working-tree content. A GREEN script does not replace
the actual full test suite or independent source review.

## 5. Recompute the score

Save the verified `before.json` and `after.json` with
`run`, `passed`, exact `sha`. **`before.json` is the baseline suite before the change,
not the RED commit**. A new throwaway project may
start with no tests; declare a zero-test baseline explicitly, using
`"zero_test_baseline": true` only with `"run": 0` and `"passed": 0`.
For the actual pilot baseline, the filled `before.json` is:

```text
{"sha": "0bd3d9312196da49422efe4da54ca34e6c8a354b", "run": 0, "passed": 0, "zero_test_baseline": true}
```

This is the *historical* baseline, not the first tests-only RED commit;
its head counterpart used `"run": 8, "passed": 8`. A baseline with
0 tests but without the explicit flag is NOT qualified, and the
candidate head must have `run > 0` and a completely passing suite.
Save `diff.json` with
`paths`, `allowed_paths`, `removed_tests` and `test_first`.
Keep the complete SELF-CHECK v2 text in `__SELFCHECK__`.
The next command reports score, claim and qualification
(expected exit 0 for a **consistent** sample):

```bash exit=0
python scripts/score_v36.py --criteria "__CRITERIA__" --self-check "__SELFCHECK__" --before "__BEFORE__" --after "__AFTER__" --diff "__DIFF__"
```

An altered claimed score is deliberately refused (expected exit 1):

```bash exit=1
python scripts/score_v36.py --criteria "__CRITERIA__" --self-check "__INFLATED__" --before "__BEFORE__" --after "__AFTER__" --diff "__DIFF__"
```

**Important:** `score_v36.py` / `selfcheck_score_v36.py` is a
**consistency check over author-supplied JSON**. It **does not verify**
test results against Git or CI, and does not prove the diff was real.
The Owner must **spot-check test counts and diff paths** directly
against the actual pinned Git changes and run logs. The machine's
score never makes a human JUDGMENT MET and never grants acceptance.

## 6. Owner decision

The Owner compares the frozen source words, checked child evidence,
real before/after tests, Git diff and code, all unresolved criteria,
pending items and the pilot's visible outcome. The Owner may **accept or reject**
the proposed task; a passing score or draft PR is not
approval. If an item is missing, mark PARTIAL/BLOCKED, request evidence
or repair, and keep the decision open. If satisfied, the Owner records
an explicit acceptance decision and controls the permitted merge.
Independent review is optional here; agent self-approval is forbidden.
