# Independent Reviewer prototype review

Two actionable findings affect optional offline helpers. The standalone prose method, optional adapters, adaptive arrangements and authority boundaries match the supplied Owner brief within the inspected scope. This is an advisory review of a skill prototype, not independent P2 qualification or acceptance evidence for AA3, LFEA, Writer2 or any other product.

## Subject and review limits

- Package: `/workspace/scratch/52eed2252c51/Common-independent-review/skills/independent-review`.
- Repository HEAD observed: `b5f8c5d53d319789e0b1219de2c6ec5302b02846`.
- Reviewed helper `scripts/review_records.py`: SHA-256 `a5d435e7f7f152cb10f6ed168329b0e7777592b802048cc19a1942cff73eba98`.
- Full captured package manifest: `candidate-manifest.json`; manifest-file SHA-256 `f89f47972982deee228e06bd9099d7b3b304857be548507c2f1bd7d17e0b11f6` (28 files).
- The working tree changed during the review. `candidate-drift.json` records subsequently observed changes to `references/CONTRACTS.md` and `tests/test_local_helpers.py`. The two reproductions below apply to the exact helper hash above. They must not be relabeled as assessment of a later corrected candidate.
- I inspected every file in the package, its repository `AGENTS.md`, and the supplied Owner brief; executed only local helper tests/reproductions; and made no package edits or external publication. I did not inspect other agents' application returns.
- The reviewer did not contribute to this candidate. This review has the inherited task brief and full package exposure, including golden outcomes. It does not establish blind discovery, authenticated principal separation, an independent physical-model oracle, low-thinking participant capability or real user acceptance.

## IR-01 — P2: duplicate issued candidate IDs silently become an unqualified MATCH

Location: `scripts/review_records.py`, `compare_candidates`, line 201 in the reviewed helper.

The issued side is indexed with a plain dictionary comprehension, whereas the observation side uses `_index` and reports duplicate IDs. A case containing two candidates with ID `SUBJECT`, one at `fixture-r1` and one at `fixture-r2`, passes the JSON Schema check. Supplying a current observation of `fixture-r2` yields only `SUBJECT: MATCH` and `issues: []`. The first issued identity disappears. Reversing the duplicate entries can change the comparison result without changing the candidate multiset.

Reproduction:

```bash
python -B scripts/review.py compare \
  /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/duplicate-case.json \
  --observations /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/duplicate-current.json
```

Run from the reviewed skill directory. Exact issued files and observed stdout/stderr are preserved in `duplicate-case.json`, `duplicate-current.json` and `duplicate-result.json`. The latter also records `schema_check: CHECKED` with no schema issues.

Expected: report ambiguous/duplicate issued identity and avoid an unqualified MATCH for that identity, while continuing unaffected comparisons. No release gate or nonzero project-decision code is needed. Reusing the existing duplicate diagnostic on the issued side would keep the helper within its declared offline scope.

Consequence and scope: a user running the documented standalone `compare` command can receive misleading freshness evidence after an accidental ID collision. Running `validate` separately would report the duplicate, but the `compare` command has no documented validation prerequisite and silently discards it. This finding is limited to the optional supplied-identity helper; it does not negate prose review or authenticate any current observation.

## IR-02 — P3: one symlink loop aborts the entire byte-check batch

Locations: `scripts/review_records.py`, `check_files`, lines 179 and 190; `scripts/review.py`, top-level exception handler, line 77.

On the Python 3.12 runtime used for this review, `Path.resolve(strict=True)` raises `RuntimeError` for a self-referential symlink. The per-file handler catches only `OSError` and `ValueError`, and the CLI handler also omits `RuntimeError`. A loop therefore produces a traceback and exit 1 with empty stdout. Previously collected observations are lost and later independent records are not checked.

Reproduction:

```bash
python -B scripts/review.py check-evidence \
  /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/loop-case.json \
  --root /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/loop-files
```

The root contains `good.txt` and `loop -> loop`. The case's first candidate deliberately gives the wrong digest for `good.txt`; its source then names `loop`. `loop-result.json` preserves the CLI traceback/exit status. It also records a direct three-record check containing a known mismatch, the loop, and a later valid file; that invocation raises `RuntimeError` rather than returning individual observations.

Expected: retain the known MISMATCH, classify the loop as UNAVAILABLE, and continue to the later valid file. A root-level invocation problem may remain a technical input error; a single bad member should not discard a usable batch.

Consequence and scope: this rare but stable filesystem condition violates the documented per-file continuation and can erase the visible distinction between a known mismatch and unavailable coverage. It does not escape the selected root or execute any record command. The reproduction is confirmed on Python 3.12; path-library exception behavior may differ on other supported Python versions.

## Evidence supporting the remainder of the brief

- `SKILL.md` starts directly from Owner intent, original sources and actual candidate, permits ordinary prose/native reporting, and treats records/scripts/other skills as conveniences.
- Available arrangements combine responsibilities, continue without absent roles, and select DIRECT/GUIDED support from actual task capability. Domain guidance covers UI, logic/data, concurrency, learning, calculation/FEA and research without declaring domain qualification.
- `ADAPTERS.md` makes Task Decomposer, Nudge Designer, project profiles and native trackers optional reference mappings. It preserves selected external contracts and existing authority, and makes no live NextNudge implementation claim.
- Independence guidance separates authorship, exposure, expectation, method, execution and upstream lineage; it retains useful self-review while forbidding relabeling it as distinct review.
- Native templates and reconciliation preserve known defects alongside NOT_RUN scope, original reviewer verdicts, historical candidate bindings, integrated outcomes and empty finding sets.
- The helpers have no network, dispatch, auto-fix, release or authority functions. Their success exit is explicitly advisory, so exit 0 on a reported contradiction is intentional.
- `assets/lfea-pilot.md` explicitly starts after prototype publication. Its historical AA3 pointers are leads to refresh, not claimed diagnosis or completed review; the package does not claim actual LFEA or Writer2 acceptance.

## Checks and remaining coverage

The supplied local test suite passed all 27 tests when first run with:

```bash
PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps \
  python -B -m unittest discover -s tests -v
```

This baseline run preceded the captured manifest and subsequent in-progress edits; it is not a regression receipt for a later candidate. Tests included optional full JSON Schema validation, no-site-package command use, raw-byte mismatch/missing-file separation, path escape/symlink escape rejection, binding/coverage contradictions, preservation of known failure plus NOT_RUN, and native result rendering. The focused reproductions above then established both findings against the explicitly hashed helper.

The reproduction driver is `reproduce.py`. To rerun against a changed package without overwriting the historical receipts, pass a new output directory:

```bash
PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps \
  python -B /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/reproduce.py \
  /workspace/scratch/52eed2252c51/tmp/ir-prototype-review/recheck-new-candidate
```

No real AA3 browser, deployment, issue authority, physical model, native tracker import, messaging integration, fresh withheld-reference application or participant qualification was assessed. No such work was required to inspect this prototype. The next useful action is to correct these two helper behaviors and rerun their focused cases plus the relevant local tests on an explicitly captured new candidate. Publication and any subsequent real pilot remain under existing Owner/project authority.
