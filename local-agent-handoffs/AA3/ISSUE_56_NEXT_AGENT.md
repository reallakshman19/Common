# AA3 #56 — next local-agent instruction (Owner's original task remains controlling)

**Read these original sources, not just this handover:**
- [AA3 #56 — full Owner AC1–AC12](https://github.com/reallakshman19/AA3/issues/56), including later amendments and native v3.6.1 standalone requirements.
- [Previously published repair delta handover](https://github.com/reallakshman19/AA3/issues/56#issuecomment-6283589908), [project-wise GitHub routing](https://github.com/reallakshman19/AA3/issues/56#issuecomment-6284048540).
- [Common handover protocol](../../skills/agent-work/local-handover/COMMENT_RELAY.md) and [artifact-only draft PR checklist](../../skills/agent-work/local-handover/forms/ARTIFACT_PR_CHECKLIST.md).
- **Pinned baseline:** AA3 PR #48 head `f26689a22598bc2c374c335a821d87d83493a02d` at the recorded observation; verify its **live** state before use.

## Handoff bytes and what they mean

1. Previous **full** local-agent candidate archive `AA3-56-local-agent-handoff(1).zip`: **325,898 bytes**; SHA256 `81bef5a678fd0cfff78c6fb8e4bae1315e7d160b68d22bea4f1d5e9af7705f66`.
2. **Incremental** repair archive `AA3-56-error-check-repair-delta.zip`: **32,053 bytes**; SHA256 `8d96cf3023b0e7c78cdb4ce106a50896c4af26a7422f43c7f44afe8596930c74`; **15 ZIP entries**, including `repair.patch`, eight source/test postimages, manifest, red/green logs and `README-REPAIR.md`.
3. This repair archive **is not a clean-base implementation patch**. Its `repair.patch` must apply to the **prior full handoff candidate**, not directly to the clean PR #48 head. A passing synthetic/controller-source test does not prove authentic ACCDB/browser/solver/CSV success.
4. The real fixture is `benchmarks/LFEA/BM4/BM4_L/BM4_L.ACCDB`, **5,136,384 bytes**, expected SHA256 `64c05a50e9ed0452622ff5880335460486f24ac8e6adecc9a300b549c9aa82f8`. Only claim original-byte verification after rehashing actual original bytes in the checkout.

## A. First: put the 32 KB actual ZIP on GitHub, without copy/paste

The outgoing agent should transfer **this actual ZIP**, not a text placeholder or encoded text mislabeled as ZIP.

- Obtain local ZIP bytes (Owner can download it from the ChatGPT handover if not already on the same machine); independently check **size 32053 and exact SHA256 above**, ZIP integrity, path safety and PUBLIC content suitability. **Common is public, including draft PRs**; do not upload private conversation, credentials, protected fixture or restricted inputs.
- With authenticated `gh` and `git`, clone **`reallakshman19/Common` at its actual `main`** into a clean isolated working directory. Create a new branch, e.g. `handoff/AA3/issue-56/consent-stale-recovery-8d96cf30-<unique-time>`.
- Stage **one single new ZIP path**: `local-agent-handoffs/AA3/issue-56/consent-stale-recovery-8d96cf30-<unique-time>.zip`. `git diff --cached --name-only` must contain *exactly that path*. Commit and push **only that ZIP**.
- Create a **separate draft PR in Common targeting `main`**, e.g. `gh pr create --repo reallakshman19/Common --base main --head <branch> --draft --title ... --body ...`. Do not mix this with an AA3 source PR, change Common main, mark ready or merge.
- Read back `gh pr view <PR> -R reallakshman19/Common --json isDraft,state,headRefOid,baseRefOid,files,url`. Require OPEN, draft=true, **files.length==1 and files[0].path exactly the ZIP path**. Re-download the **actual binary** from the head commit and check SHA256 and bytes. An unverified single-file claim is not a verified PR.
- Post a fresh [LOCAL-HANDOVER v1 comment block](../../skills/agent-work/local-handover/forms/COMMENT_BLOCK.md) to **AA3 #56**, recording the exact draft PR URL, head SHA, single file path, ZIP SHA256/size, download verification, old candidate dependency, real test limits and next action. **Read back the posted issue comment** and provide its permalink.
- If GitHub authentication, public-visibility permission or original ZIP bytes are not available, report `NOT_RUN/BLOCKED` and the smallest required input. **Do not invent a draft PR**.

## B. Then: test the actual repaired product, not only the source

1. Recover the actual authorized checkout at pinned PR #48 head. Preserve dirty/pre-existing work and record the real original baseline. Check the full original handoff `changes.patch` against **that** clean base before applying it, and inspect its postimages. **Only then** apply the new `repair.patch` against that prior candidate; verify its 8/8 expected postimages. Preserve solver, fixture, workflow and PR #54/#55 boundaries.
2. Review reviewer signoff: empty name/reason until explicitly provided by a human, no preset-generated credentials; settings-only preparation can be previewed without a fake property approver; genuine property corrections demand attributable approval; prior override attribution survives new batches/Undo.
3. Exercise **real** detached Preview/Cancel/Apply/Undo transaction code: stale/replayed/conflicting tokens must fail atomically with **no live state mutation**, and recovery must inspect before/after rather than print an unproven success. Don't accept a hard BLOCK as a prototype assumption.
4. Install exact locked dependencies in actual checkout, rerun genuine module tests and applicable pre-existing regressions. Run root Playwright on real imported ACCDB; measure 5–7 primary clicks separately from keyboard/type/setup, focus and narrow viewport.
5. Verify the authenticated actual IXP-W/allowed cases, real LFEA Run, OUTPUT and downloaded **signed numerical CSV** values/identities/units/frame; record limitations and `NOT_PERFORMED` code-assessment truthfully. Open the actual CSV bytes and preserve the result and browser trace; no button-only or mock proof.
6. Apply A13 **300 physical lines** to every new/materially changed authored source/test at exact base and candidate. Preserve A14 source-bound standalone SELF-CHECK v1 **before** any qualified completion claim, full AC1–AC12 matrix, prior failures, actual logs/exits, and terminal LOG on real issue. Never claim Owner acceptance/merge/deploy.
7. Post an `INCOMING_RESULT` block as a **new** AA3 #56 issue comment. Distinguish `EXECUTED_HERE`, `REPORTED_BY_PREDECESSOR`, `NOT_MET`, `NOT_RUN` and `UNKNOWN`. Include changed understanding, remaining criteria, accurate model/source identity and next useful action.

**Expected outcome:** First a real, verified one-file draft artifact PR (if safe/authorized and the ZIP is accessible), followed by real candidate repair+test evidence, **not** another unsupported “delivery complete” paragraph. No merge or deployment.
