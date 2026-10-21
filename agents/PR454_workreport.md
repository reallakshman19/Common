# PR454 — Oracle/reviewer contributions and coding handoff

HANDOVER_READINESS: READY (recoverable; not independent acceptance)
PR_RECOVERY_STATE: HEALTHY
WORK_INTENT: IMPLEMENT
CRITICALITY: STANDARD (agent-work prose only)
TAKEOVER_AUTHORITY: WRITE_ALLOWED within the Owner assignment; no merge authority
REPOSITORY: reallakshman19/Common
PR_OR_WIP: PR454
BRANCH: codex/agent-work-contribution-handoff-20261021
REPORT_BASIS_HEAD: e3b16da523ed243a1e2003cf50328d7adb84f406
PR_HEAD_OBSERVED: e3b16da523ed243a1e2003cf50328d7adb84f406 before report-only synchronization
MAIN_HEAD_LAST_CHECKED: d7365707dca0039f9a529f7309b635ff160c9dd0
MERGE_BASE: d7365707dca0039f9a529f7309b635ff160c9dd0
REPORT_SYNC: CURRENT (only recovery metadata follows the content basis)
APPENDIX_A_STATUS: NOT_REQUIRED (standard guidance update)
GROUNDING_EPOCH: GE-agent-work-contribution-20261021-01
CURRENT_STAGE: AWAITING_REVIEW
CURRENT_BLOCKER: independent acceptance NOT_RUN
EXACT_NEXT_ACTION: Refresh live head/checks, review the nine guidance paths and scoped independence/authority semantics; use existing Owner merge authority.

## Handover in 60 seconds

The Owner endorsed an Oracle contributing High/Medium ROI work before a coding
successor continues, requested that the process apply to Oracles and independent
reviewers, then instructed: "now think again and update" the agent-work collection
at the main SHA above. These are current-conversation instructions; no durable
message URL is available. The assignment authorizes this bounded source update,
not merge, global skill installation or downstream product edits.

Implemented one shared contribution/handoff recipe, linked from the existing
Oracle and reviewer entry points. It selects work by actual context advantage,
keeps contributions bounded, preserves decisions/evidence and names the exact
continuation. Review-only authority and selected coordinator separation survive.
Candidate contributions are self-assessed for affected claims; writing independent
checking evidence alone does not turn the reviewer into the product's author.

## Decisions and preserved boundaries

- DEC-001: Put detailed guidance in one shared reference and short entry links.
  Rejected a new installable skill/controller/schema because native reports and
  current modules already carry the work. Falsifier: an entry cannot supply usable
  instructions without silently importing another module.
- DEC-002: Treat High/Medium ROI as prospective, qualitative judgments. Require a
  reason based on impact/context/cost/risk, not an invented score or claim that this
  actor is better than all others. Measured causal savings remain unestablished.
- DEC-003: Separate candidate contribution, review-evidence authorship, exposure
  and expectation derivation. Reject both self-approval and blanket disqualification
  of reviewers who write diagnostic scripts. Reuse unaffected evidence only with
  candidate/dependency analysis; preserve historical verdicts.
- DEC-004: Stop at an Owner-requested handoff, with an exact next unit. A routine
  checkpoint alone must not end an otherwise authorized execution assignment.

No runtime, schema, workflow, engineering-delivery policy, historical Relay record
or global installed skill is changed. Existing optional module/package operation,
coordinator separation, independent-review requirements and release authority remain.

## Changed-file ledger

| Path under skills/agent-work/ | Purpose |
|---|---|
| CONTRIBUTION_HANDOFF.md | Shared selection, authority, contribution, independence, recording and continuation recipe; native-record template. |
| START_HERE.md | Discoverability and compact operating rule. |
| independent-review/SKILL.md | Trigger and authorized contribution guidance, bounded self-review. |
| independent-review/references/INDEPENDENCE.md | Contributor scope and dependency-aware review reuse. |
| independent-review/assets/prompts.md | Copyable review-plus-contribution instruction. |
| nudge-designer/SKILL.md | Oracle contribution entry without a module dependency. |
| nudge-designer/references/ORACLE_EXECUTION.md | Contribution/coding-successor boundary. |
| nudge-designer/assets/prompts/oracle.md | Copyable Owner instruction. |
| task-decomposer/references/ORACLE_USE.md | Preserve contribution rationale and exact continuation in existing map/native records. |

Recovery metadata: this report replaces the unique bootstrap WIP report. The PR
has ten final paths: nine guidance paths plus this report. Extra local fixtures,
unchanged helper dependencies and forward outputs are not uploaded as source edits.

## Validation ledger

All author checks remain author evidence, not independent acceptance of this skill.

| Check | Status / observation / oracle | Result and limitation |
|---|---|---|
| quick_validate.py on both edited SKILL.md packages | PASS / LOCAL_EXECUTION / NONE | Both valid; interface metadata still describes their unchanged purpose. |
| Candidate source links | PASS / LOCAL_EXECUTION / NONE | 109 relative/Common-main source links resolve in the candidate tree. Canonical main URLs to the new reference become available after merge; use this PR's content basis meanwhile. |
| git diff --check | PASS / LOCAL_EXECUTION / NONE | No whitespace errors in the guidance delta. |
| Existing Independent Reviewer helper suite | PASS, one NOT_RUN / LOCAL_EXECUTION / IMPLEMENTATION_COUPLED | 29 discovered: 28 passed, one optional jsonschema check skipped because that dependency is unavailable. No helper, schema or original test was changed. |
| Fresh Oracle application | PASS within fixture / LOCAL_EXECUTION / IMPLEMENTATION_COUPLED | Bounded repair, four regression checks, explicit self-review and next coding unit; author replay also passed. |
| Fresh reviewer application | PASS within fixture / LOCAL_EXECUTION / IMPLEMENTATION_COUPLED | No product edit, self-assessment under supplied prior authorship, 364 finite cases and three detected seeded defects; author replay matched. |
| Exact GitHub content readback | PASS / ARTIFACT_INSPECTION / NONE | All nine files match prepared bytes at REPORT_BASIS_HEAD. |
| Hosted content-head checks | PASS / ARTIFACT_INSPECTION of hosted receipts / NONE | Six success, two unrelated skipped at REPORT_BASIS_HEAD. Includes Nudge Designer contract-and-cli on Python 3.10/3.12: https://github.com/reallakshman19/Common/actions/runs/39554132900. Generic success or skip alone does not certify contribution semantics. Refresh checks on any later live head. |
| Independent skill acceptance / downstream project application | NOT_RUN / NOT_OBSERVED / NONE | Two simple applications establish limited feasibility, not general capability, causal ROI, blind discovery or product acceptance. |

ISS-001 (environment, resolved): the first helper-suite attempt lacked six original
examples/records fixtures in the selected local materialization. It produced 23
setup errors. Fetching those unchanged exact-base fixtures restored execution;
the final result is 28 pass/one optional skip. No production or test weakening.

## Fresh application witnesses

Both agents received fresh task context without this author's diagnosis/expected
patch. They read the revised recipe SHA-256
`50d02a4b8ab09304d827b931e474888110cb37e2368cf765ed185b3f6fef8b2b`.
The reviewer also recorded core SHA-256
`0318853840bf2100d7a0753e39d9bd60aa45d3a4c12521414a7cb2c9da7b3fc3`.
They used local tools only, with explicit fixture write boundaries; no delegated
external writes or live product changes were authorized. The skill-creator guidance
explicitly selected fresh forward applications. These were applications of the
recipe, not a distinct-principal approval of its author.

Oracle raw task: use the recipe for a queue project, read original requirements
and source, contribute High/Medium ROI work within the existing report's authority,
then hand off to the coding successor. The supplied requirement was new list,
ascending numeric priority, stable ties and unchanged caller input. Original code:

```python
def ordered(items):
    items.sort(key=lambda item: item["priority"])
    return items
```

The report reserved filter/CLI for the successor. The application reproduced
mutation/aliasing, changed the function to return sorted(items, key=...), and left
filter/CLI untouched. Actual author replay: `python3 -B test_ordered.py` exited 0,
four checks passed (unchanged input, distinct empty/already-ordered output, numeric
ordering/stable ties). Tested repaired source SHA-256:
`d849704a7769dd977d4d2ccc31259e0409804ccb349abc50c4a82ce2daca467e`.
It recorded the missing filter/CLI contract and proposed successor pickup without
claiming delivery. Baseline failure details are application-reported; final checks
were separately replayed by this author. Full fixture scope remains synthetic.

Reviewer raw task: assess the supplied preview requirements, with known authorship
of preview.py in an earlier session, product edits forbidden, evidence/report only
permitted. The supplied requirement was stable ties, a new list and unchanged input;
score direction was deliberately unspecified. Candidate source was
`return sorted(rows, key=lambda row: row["score"])`, SHA-256
`46197c961088644047ffce18b5e97b9731b4e597409d078efb8fff38e885c073`.
The application left it unchanged, labelled SELF-ASSESSED, retained a Medium ROI
checking artifact and supplied exact continuation. Actual author replay of
review_checks.py exited 0: 364 sequences (lengths 0–5, scores -1/0/1), zero candidate
failures, and detected tie reversal, alias return and in-place mutation seeds.
Checking script SHA-256:
`bc19d729ea12019eef22d383f15983f061408ebc7d31c2c3bdb88a3c53801c9b`.
It preserved unspecified behavior and did not manufacture a High ROI repair.

The complete fixture files remain local working evidence. The source conditions,
observed results and hashes above are the durable summary; this PR does not claim
to ship a new automated behavior-test harness or complete reproduction archive.

## Grounding, risk and continuation

AGENTS.md was read; selected v3.2 guidance remains scoped to its own slice. No
nested agent-work AGENTS.md, agents master index or active claims/status surface was
found on this base. All 79 pre-existing open PR changed-file lists were inspected;
none changes agent-work/**. PR439 changes the separate skills/nudge-designer copy.
Before content publication main and all other open heads were unchanged. This PR
preserves that separate copy and creates no downstream authority.
At final content-head readback PR454 was OPEN/DRAFT with no submitted reviews,
inline review comments or requested reviewers. Report-only synchronization is the
only later change in this checkpoint; fetch any newly triggered check runs live.

RISK-001: scenario coverage is narrow; selected Gatekeeper coordinator arrangements
and complex engineering author/oracle lineage need project-specific assessment.
RISK-002: hosted statuses are mutable; current live acceptance is not inferred from
the local check results or unrelated green/skipped workflows.

Next reviewer/coder: refresh PR454, main, actual diff and current claims. Start at
skills/agent-work/CONTRIBUTION_HANDOFF.md, then inspect entry-point changes. Check
review-only use, authorized repair, diagnostic-only evidence, shared test/model
premises and Owner-requested stop boundaries against actual project policy. Reuse
this decision basis rather than restarting the concept. If changing semantics,
recheck affected applications and record a new basis. No merge or release authority
is granted by this handoff.
