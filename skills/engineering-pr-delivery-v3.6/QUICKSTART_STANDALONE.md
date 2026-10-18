# Standalone v3.6.1 — Owner's one-page pilot

Use a **throwaway Git repository**, not a live project. Work with one
coding agent; there is **no TeamCoordinator**, shared registry, chat-send
route or CoordinatorLandingpage access. The Owner approves every scope,
review and merge. The agent never approves its own work.

The commands below run **from this skill folder**
(`skills/engineering-pr-delivery-v3.6`) with Python 3, Git and the
existing PyYAML dependency installed. Replace each `__NAME__` token
with your **local path or verified value** before copying a command.
Quoted paths also work when directories contain spaces. Each executable
fence records its expected exit code (0 = success; 1 = intentional
unqualified score). These commands are **local read-only or dry-run**
and do not post to GitHub. For the checked example, tests use
temporary local Git repos and invented measurement JSON; those files
are **illustrations, never Owner or CI evidence**.

## 1. Standalone label

In your throwaway repo, create `relay/AIM/<WORK>.yaml` using the
approved full v3.6 master-label structure. The top-level selection is:

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
**separate SELF-CHECK v2 companion first on that real child issue**:
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
`run`, `passed`, exact `sha`; save `diff.json` with
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
