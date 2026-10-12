# Engineering PR Delivery v3.6 — independent GitHub lifecycle (DRAFT)

**Status:** v1.1.0 Owner label approved; this implementation remains DRAFT. **Owning issue:** [Common #341](https://github.com/reallakshman19/Common/issues/341). **Plan:** V36-341-PLAN-02. **Owner aim card:** V35-LIFECYCLE / CP-V35-LIFECYCLE-01, approved master v1.1.0 / label_sha 775f2bc.

## Scope, independence and safety

v3.6 starts its own lifecycle. All of its runtime scripts, schemas, templates, prompt packs and tests must be under this directory. It never imports or executes v3.5, v3.2, v3.1, Local PR Delivery or DELP. Those historical systems are not its authority. No existing skill is changed by v3.6 work.

The Owner controls aim approval, criticality, material scope, use of publisher credentials, acceptance and merge decisions. Source text, GitHub comments and sample labels do **not** grant those decisions. Until explicitly authorized, operate read-only; CLI WP1 commands are validation/rendering only. Engineering-critical technical doubt stops the doubtful step and asks the Owner. No merge, close, rebase, automatic release or write authority is inferred by this draft.

## Outcomes

- **O1:** Parent issue decomposes into child issues and a visible, versioned plan.
- **O2:** A completed task posts truthful TASK_EVIDENCE on its *child* issue, with first lines `Outcome`, `For the user`, `Proof`.
- **O3:** Parent and child issue titles update from current GitHub facts, never from an agent-asserted percentage.
- **O4:** PR titles identify actual delivered outcome and current PR state, from current GitHub refs and valid evidence.
- **O5:** A cold successor can reconstruct the aim, plan, task/evidence and live PR heads from GitHub alone.

## Proposed data flow / work packages

```text
relay/AIM/<WORK>.yaml (Owner-approved external record)
  -> validated aim/criticality [WP1]
  -> versioned plan, parent-child issues [WP2]
  -> provider-observed issues/evidence/live PR heads [WP3]
  -> dry-run title/status diff -> approved publisher -> readback [WP4]
  -> GitHub-only handover and BuddyRunner v1.6 [WP5]
  -> aim/evidence-bound 2-pass or 3-pass prompts [WP6]
  -> independent lab positive/negative acceptance [WP7]
```

**No secondary scoreboard database:** current GitHub child issue state, accepted evidence comments, plan version, and PR head/state are the only source facts. A closed child issue or merged PR does not by itself mean accepted evidence. Missing, stale, unverified or inaccessible facts are `UNKNOWN`, not green, zero or complete. Plan revisions must preserve the denominator or show an explicit approved scope change.

## WP1 — runnable foundation (draft)

Install `requirements.txt` into an isolated Python environment. This is a new dependency for *this* skill, not an import of older code.

```sh
python -m pip install -r skills/engineering-pr-delivery-v3.6/requirements.txt
python -m unittest discover -s skills/engineering-pr-delivery-v3.6/tests -v
python skills/engineering-pr-delivery-v3.6/scripts/lifecycle_v36.py validate-label relay/AIM/V35-LIFECYCLE.yaml
```

The `validate-label` command only parses and validates an explicit `relay/AIM/<WORK>.yaml` path; no GitHub write. `render-evidence` formats a comment from supplied verified task facts and refuses an empty placeholder proof; rendering is **not publication**. See `templates/sticky-label-v36.yaml` and `templates/task-evidence-v36.md`. The example label is a pinned read-only fixture of the approved master; only the master at relay/AIM/V35-LIFECYCLE.yaml governs. Label fields remain the Owner's exact words.

The v3.6 module requires Python 3.10+ and PyYAML 6.x. All public CLI commands remain read-only in WP1. Every future write command must implement dry-run as its default, fail closed on missing approval, verify selected exact repository/issue/PR and read back results. One scripting language: Python.

## WP2–WP7 admission / acceptance intent

WP2 must validate stable workpack/task IDs, sizes, outcome and acceptance before materialization; replay must not duplicate children. WP3 must validate evidence references, current candidate, negative/stale tests and provider visibility. WP4 must preserve unmanaged human title text and refuse unauthorized writes; repeated runs must be idempotent and read back exact output. WP5 must implement BuddyRunner v1.6 as **1a execution HOLD → 1b independent reconstruction → 2 single reconciliation**, with an optional **Y** response to later Xb evidence, *not* a loop. WP6 must honor the Owner's pending D-V36-2 packaging decision. WP7 requires a real lab run with a fresh cold successor; synthetic lab proof must not be promoted to authentic programme acceptance.

**Current state:** Master label v1.1.0 approved; scope of automatic lab writes and future prompt-pack choices remains subject to explicit Owner direction. WP1 draft scaffolding is not approval of these decisions. WP4/WP7 live publisher writes HOLD pending explicit scoped permission. Older #294 decisions are **not v3.6 inputs**.

## WP2 — parent → real child issues (O1)

The approved master is always loaded from `relay/AIM/V35-LIFECYCLE.yaml`, not from this skill's fixture. The plan `plans/V36-341-PLAN-02.yaml` pins `work/version/label_sha` and each task's stable ID, size, single primary outcome, acceptance and owner-visible result. The WP2 implementation and tests are in `scripts/decompose_v36.py` and `tests/test_decompose_v36.py`.

```sh
# Repo root, read-only provider snapshot and proposed child list (default)
python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py \
  --label relay/AIM/V35-LIFECYCLE.yaml \
  --plan skills/engineering-pr-delivery-v3.6/plans/V36-341-PLAN-02.yaml

# Only with an explicit scoped writing instruction and usable token:
GITHUB_TOKEN=<token> python skills/engineering-pr-delivery-v3.6/scripts/decompose_v36.py \
  --label relay/AIM/V35-LIFECYCLE.yaml \
  --plan skills/engineering-pr-delivery-v3.6/plans/V36-341-PLAN-02.yaml \
  --apply --confirm-scope 'reallakshman19/Common#341'
```

WP2 is **not** a title/evidence publisher; it only makes missing child issues and a managed parent-plan index. GitHub reads precede every write; duplicate child matches or multiple parent indexes fail closed; existing manually created WP1 #345 is uniquely adopted, not recreated. Repeated `--apply` should produce zero new children and an unchanged index. The 12 Oct Common #341 child list #345–#351 was created using connected GitHub tooling and read back, *not* by executing the Python `--apply` command; do not count it as script-level integration proof or the final lab acceptance.

Exact-source WP1/WP2 offline tests have not yet been executed at branch head; the earlier 14/14 run only covered the superseded draft shape. The independent v3.6 acceptance suite must be rerun before claiming the implementation green.
