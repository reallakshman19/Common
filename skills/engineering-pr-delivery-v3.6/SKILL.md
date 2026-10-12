# Engineering PR Delivery v3.6 — independent GitHub lifecycle (DRAFT)

**Status:** v1.2.1 Owner label approved; this implementation remains DRAFT. **Owning issue:** [Common #341](https://github.com/reallakshman19/Common/issues/341). **Plan:** V36-341-PLAN-02 (source plan); current execution revision PLAN-05 on Common #341. **Owner aim card:** V35-LIFECYCLE / CP-V35-LIFECYCLE-01, approved master v1.2.1 / label_sha 4b90240.

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

WP2 must validate stable workpack/task IDs, sizes, outcome and acceptance before materialization; replay must not duplicate children. WP3 must validate evidence references, current candidate, negative/stale tests and provider visibility. WP4 must preserve unmanaged human title text and refuse unauthorized writes; repeated runs must be idempotent and read back exact output. WP5 must implement BuddyRunner v1.6 as **1a execution HOLD → 1b independent reconstruction → 2 single reconciliation**, with an optional **Y** response to later Xb evidence, *not* a loop. WP6 must implement the Owner-approved D-V36-2: two separate 2-pass and 3-pass generators with distinct purposes and independent tests, inside v3.6. WP7 requires a real lab run with a fresh cold successor; synthetic lab proof must not be promoted to authentic programme acceptance.

**Current state (12 Oct 2026):** Master label v1.2.1 / label_sha 4b90240 governs. D-V36-1/2/3 approved independence, two separately invoked generators, and writes confined to the new v3.6 lab; no wider writes/merge. WP1–WP3 are draft source-tested, WP4 E01/E02 verified with installed lab Actions workflow; E03 metadata reconciliation is underway. WP5, WP6 and WP7 remain unaccepted. Owner outcome acceptance remains 0/5. Older #294 decisions are **not v3.6 inputs**.

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

Earlier WP1/WP2 test claims came from previous source heads and are not CI proof for the current PR head. Hosted v3.6 O4 publisher regression passed **15/15** at e046d3c (lab Actions run 38198821650); the full branch-head suite and integrated WP7 acceptance must still be run independently. Do not carry CI from earlier SHAs.

## Benchmark repository boundary

The approved master is maintained in Common, but its guidance explicitly names `Writable lab: reallakshman19/relay-v36-e2e-lab`. WP2 plan validation therefore permits only the master repository and that exact named lab repository, always with an exact `owner/repo#parent` `--confirm-scope` and current provider permissions; arbitrary repositories are rejected. To run the final benchmark, a fresh lab plan must bind the lab parent number and stable task IDs; the Common #341 plan remains a coordination example, not the lab's actual plan. As rechecked 12 Oct 2026, the connected GitHub identity has `push=true`, `triage=true` on the writable v3.6 lab. Lab parent #1, children #2/#3 and PR #4 are real; an unrelated negative PR #5 is also a fixture. Scoped v3.6 GitHub Actions title writes are proven by runs 38197870074, 38197925293, 38197962621 (E01) and 38198821650 (E02), with readbacks and zero-diff replay. These runs do not prove full WP7 or authorize Common merge.

## Owner decisions — 12 October 2026

D-V36-1: independent architecture APPROVED. D-V36-2: two **separate** generators, 2-pass and 3-pass, with distinct purposes; do not merge them into modes of one generator. D-V36-3: lab write intent approved; actual GitHub provider write permission must be observed before attempted lab mutations. Development and Common read-only/safe testing continue independently. Plan-03: https://github.com/reallakshman19/Common/issues/341#issuecomment-6116096075.

WP3 script `scripts/snapshot_v36.py` is a GitHub read-only provider snapshot. It recognizes finished-task evidence only when the child issue, task/outcome, proof PR, 40-character candidate SHA and live PR head match. It reports stale or unknown evidence explicitly. Even CURRENT_EVIDENCE is *not* independently accepted completion; every output's complete flag remains false until a future separately specified acceptance mechanism. Workpack status and lab acceptance are distinct.

## v1.2.1 lab acceptance target
The only approved writable benchmark target for WP4/WP7 is `reallakshman19/relay-v36-e2e-lab` identified by the approved master guidance `Writable lab:`. Common v3.6 source changes stay on draft PR #344, not main. The existing Common seven-child managed index predates v1.2.1 and is metadata to reconcile; preserve child bodies and previous evidence comments as historical, not as current Owner-label authority. Older `reallaksh19/relay-v35-e2e-lab` is reference-only, and any prior `Lab:` note is not permission. See Common #341 PLAN-04. Lab parent #1, children #2/#3, PR #4 are real. Title changes must be computed from GitHub facts, scoped, applied and read back with no hand-authored completion number.
