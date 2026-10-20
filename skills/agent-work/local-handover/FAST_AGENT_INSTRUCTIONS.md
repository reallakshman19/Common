# Exact instruction for a fast/low-reasoning local agent

**Use this file as an instruction, not as evidence of compliance. Execute independently within the Owner's actual authorization.** Do not echo this text as a fake completion report. Do not invent permissions, APIs, tests, sources, timestamps, hashes, credentials or outcomes.

## Start: six actions

1. **READ** the original Owner request, effective changes, and project-specific rules. Copy *all* Owner acceptance IDs into the self-check before changing code/content. Identify the actual target consumer and protected parts.
2. **INSPECT** what is really available on your machine. Record working directory, input paths, source/base/candidate identity, `git status` for code, and what is missing. Do not call a ZIP/reported branch a working checkout.
3. **COMPARE** the outgoing agent's claims with the **actual files**. Make a two-column note: `claimed` versus `observed`. If you did not execute a command yourself, write `REPORTED`; if a file is absent, write `NOT_RUN`, not `PASS`.
4. **TEST BEFORE REPAIR** when the selected project requires it. Preserve the real baseline and one failing/contrary case before editing. Keep every original failure. Check complete outcome, not only a helper module.
5. **REPAIR** only within authorized scope. Preserve original input and protected behavior. Re-run relevant tests and open the actual output. Do not weaken an expected result solely to make green.
6. **FILL SELF-CHECK AND RETURN** with exact file/line or output witnesses, actual command + exit, test counts, all criteria, open failures and the smallest next step. A reviewer/Owner may disagree; your own PASS is not their acceptance.

## Do not make the Owner copy reports

With authorized GitHub access, read the relevant predecessor [issue comment block](forms/COMMENT_BLOCK.md) directly. Post and read back your own INCOMING_RESULT or OUTGOING comment on that **same existing issue**. For a ZIP, use the Owner-selected public [Common project-wise folder](../../../local-agent-handoffs/README.md), e.g. `local-agent-handoffs/AA3/issue-56/<candidate-id>.zip`, and create a **separate one-ZIP-only DRAFT PR**, verify the actual server diff has one path and the PR is draft, then link its URL, head SHA and artifact SHA-256/bytes in the issue comment. See [relay instructions](COMMENT_RELAY.md). Do not include sidecars as extra PR files, merge a handoff PR or claim a comment proves acceptance. If no GitHub access or the bytes are unsafe for public Common, report the specific blocker rather than inventing a PR.

## Mandatory honesty rules in your response

- Say **“I ran”** only when you actually ran it and can cite a local log/output; otherwise **“the outgoing agent reports”**.
- Say **“verified original input”** only when you independently read actual bytes and compared them with an authoritative *separate* reference. Self-authored manifest equality does not prove authenticity.
- Say **“patch applies”** only after **forward** applicability check in the exact authorized clean base. Reverse check on an edited worktree != forward check.
- Say **“end-to-end passed”** only after using the real consumer/input/output, recording the actual result. Source text, mocks, screenshots of buttons or synthetic-only runs are insufficient.
- Say **“no failures”** only with complete declared test denominator, skipped/failed counts and scope; do not hide a pre-existing failure to make the final state green.
- Say **“independent”** only with a valid basis; a fresh model reading the prior agent's expected result is not a blind reviewer. Disclose what you read.
- Say **“complete”** only if every original required criterion is actually met and no blocking obligations remain; Owner acceptance/release remains separate.

## Decision table (use directly)

| You observe | Write in self-check | Next action |
|---|---|---|
| Real command exited 0 with inspected expected output | `PASS / EXECUTED_HERE` | Record log/bytes/limit |
| Real command exited nonzero | `FAIL / EXECUTED_HERE` | Record raw log, whether baseline/introduced/expected RED; repair or retain |
| Previous agent wrote PASS but you haven't run it | `REPORTED` | Inspect exact files, rerun if relevant |
| Test is skipped, dependencies are missing or tool unavailable | `NOT_RUN` or `BLOCKED` | Name missing input/tool, smallest unblock |
| Source is present, candidate result is uncertain | `UNKNOWN` | State decisive observation needed |
| Criterion is outside authorized task scope | `NOT_APPLICABLE` only with original-source justification | Keep parent obligation visible |
| New revised artifact arrives | New candidate identity | Reassess affected tests, do not silently transfer old green |
| You discover an unauthorized/destructive operation | `BLOCKED` for that action | Stop that action and request correct authority; continue safe work |

## Return only these seven things (no ceremonial essay)

1. **Identity:** project/task, original criteria revision, base/source/candidate hash and your accessible inputs.
2. **What changed:** actual files/behavior/decision, with causal explanation; no unreviewed bundle dumped as a final answer.
3. **Evidence:** actual commands and exit codes, log links/hashes, test counts and original-vs-candidate output.
4. **Bad news:** every failed, skipped, blocked, disputed or missing check; baseline versus introduced.
5. **Criteria:** one MET/NOT_MET/NOT_RUN/UNKNOWN row **per original ID**, linked to decisive evidence and a contrary case.
6. **Boundaries:** privacy/protected behavior/permissions and what was NOT changed.
7. **Next:** one smallest useful action (actor, required input/authority) and whether the full Owner outcome remains pending.

No need for a competence exam, extra role or repeated approval ceremony. If you can proceed safely, proceed. If a decisive input or authority is absent, report the exact blocker without inventing progress.