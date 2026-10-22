# Local-agent operating protocol · receive, execute, self-check, hand over

This is an **optional field instruction** for fast/low-reasoning local agents taking over work in any project. Use it with the [Common agent-work guide](../START_HERE.md), [handover protocol](PROTOCOL.md), [GitHub comment relay](COMMENT_RELAY.md) and [self-check form](forms/SELF_CHECK.md). It is not a fifth skill, agent admission exam, new lifecycle, standing grant to publish private files, or substitute for a project's actual rules.

## The job in seven actions

1. **READ ORIGINALS.** Open the Owner's actual task issue, effective amendments, accepted plan, selected mode and original acceptance IDs. Keep the complete parent result and preserved constraints visible. A predecessor's summary is context, **not authority**. If a necessary source can't be accessed, record the exact missing source; continue independent safe work.
2. **IDENTIFY BYTES.** Inspect the actual checkout, base/candidate commits, downloaded files, fixture/golden and provenance. For any received ZIP, record exact filename, size, SHA-256, ZIP entry list/CRC and source lineage. A producer's manifest proves only consistency with its own file list, not authenticity, safe patch applicability or correctness. Mark claims `REPORTED_BY_PREDECESSOR` until checked.
3. **CHECK THE METHOD.** Explain the minimal input → function/state/decision → real consumer/output path. Specify a plausible wrong result and a test that would detect it. For software: record before-state/known failures and test first where native policy requires; do not replace the original oracle with easy self-generated expectations.
4. **EXECUTE ONLY AUTHORIZED WORK.** Confirm source and dirty tree before applying a patch. Check **forward** applicability on the exact clean base. A repair delta may depend on a **previous candidate** and must not be applied directly to the original base. Preserve unrelated work and original fixtures. Never auto-accept human approval, weaken hard blockers, hide a failed test or adjust numerical conventions merely for green output.
5. **LOOK AT THE RESULT.** Run the real consumer/end-to-end route where required, inspect the opened/downloaded output, and retain positive **and** contrary/failure evidence. Source-only or mocked checks are valid with explicitly limited scope; don't call them browser, solver or production acceptance. Log commands, environments, exit codes, artifacts, counts and skipped checks.
6. **SELF-CHECK.** Complete [12-question local self-check](forms/SELF_CHECK.md) with one row per *original* acceptance ID and one row per planned test, including `MET / NOT_MET / NOT_RUN / UNKNOWN`, raw witnesses, introduced vs pre-existing failures and the next blocker. Preserve native project forms, canonical receipts and LOG where selected (e.g. engineering-pr-delivery-v3.6.1 A13 **300 physical lines**, A14 **SELF-CHECK v1**); this form does **not** replace those.
7. **RETURN A RETRIEVABLE HANDOFF.** Post a new [delimited GitHub issue comment](forms/COMMENT_BLOCK.md) to the *original task issue* and **read back** its permalink. Disclose authorship/exposure, exact candidate, observed vs reported checks, unresolved criteria, links to actual artifacts and next useful action. Don't merge/release/deploy without Owner authority.

## Transferring actual files, without Owner copy/paste

**Default communication:** the original GitHub issue plus the delimited comment block. The next agent retrieves the comment using `gh api repos/OWNER/REPO/issues/comments/COMMENT_ID --jq .body`, opens the sources and posts its **own** comment. A link is a locator, not proof it was opened.

**Private files: the Owner's one common handoff folder.** The Owner keeps ONE private Google Drive folder for every handoff and source fixture file of every project, saved project-wise: one subfolder per project key (the same slug as `local-agent-handoffs/<project-slug>`). A file goes only into its own project's subfolder, named `<name>_<sha256 first 12>.<ext>`. The Owner (or the OwnerTeammember) gives the folder link in chat; it is never written to GitHub, this public repository, a pull request, an evidence post or the Progress page. Posts name the subfolder, file name, byte size and full SHA-256 instead. Do not make the folder or a file more public.

**Existing Google Drive binary:** when the Owner provides an actual Google Drive ZIP link, the agent downloads the file bytes, computes a **local** SHA-256/size, checks archive integrity and confirms the right candidate before applying anything. A Drive link with verified remote SHA-256 establishes **transport identity**, not code correctness. No need to ask the Owner to paste base64 or download/reupload the same file. Treat Drive permissions as they are; do **not** make it more public without explicit authority.

**Common GitHub artifact route:** for a *separately requested* GitHub handoff artifact, use the Owner-selected [project-wise Common folder](../../../local-agent-handoffs/README.md). Create a **dedicated DRAFT PR with exactly one ZIP path** (`local-agent-handoffs/<project>/issue-<id>/<candidate-id>.zip`) on a fresh branch against `Common/main`. Check server `isDraft`, base/head, complete PR changed-file list, archive SHA-256 and remote bytes when accessible. This is an additional discoverable transfer artifact and must **not delay otherwise authorized engineering checks** when the Drive bytes are already verified. Common is **public**, including DRAFT PR contents: do not publish secrets, private files, protected inputs, customer data or restricted chats. If public storage is unsafe, report `NOT_CREATED(PRIVACY)` and use a permitted private handoff. Keep the draft PR OPEN/DRAFT; do not merge.

For PowerShell on Windows, measure a downloaded file with `(Get-Item .\handoff.zip).Length` and `(Get-FileHash -Algorithm SHA256 .\handoff.zip).Hash.ToLower()`. On POSIX use `wc -c < handoff.zip` and `sha256sum handoff.zip`. Run `python -c "import zipfile; z=zipfile.ZipFile('handoff.zip'); print('BAD:', z.testzip()); print(len(z.namelist()), 'entries')"` for CRC/entry count. A passing CRC does not audit ZIP path safety or patch meaning; inspect paths and contents independently.

**Drive or OneDrive, recorded as fixtures** (Owner, 22 Oct 2026, Lesson 1: CoordinatorLandingpage #1 comments 6339599529, 6339795835, 6339862645). Private files go through the Owner's handoff folder in Google Drive or OneDrive, in the project's subfolder. Record each file as a grounding fixture on the Progress page (list `inputs`): subfolder, file name, size and full SHA-256; never the link (the page checker refuses Drive, OneDrive and SharePoint links).

## Fill the return; avoid fake PASS

Apply **No PASS beyond evidence** and **No consequential PASS without a
surviving-error challenge** to local agents and any Oracle. Name the precise claim,
expectation source/review status, candidate/input hashes and actual executed
witness. Identify significant plausible wrong behavior within the claim that could
still pass; strengthen the evidence or narrow the verdict. A genuine alternative
and differing predicted outcomes matter more than filling five evidence fields.
Keep FAIL, NOT_RUN, UNKNOWN and claim-level HOLD distinct; continue unrelated work.

Choose the next task from actual evidence: settled implementation, an established
repair, or suitably independent falsification of disputed correctness. A fixed
agent count is not required. Transfer original requirements, facts, artifacts,
revisions and conditional explanations without making a speculative diagnosis a
required fix. Oracle-authored patches remain contributor artifacts; preserve any
required independent review and authorized Owner acceptance separately.

| Situation | Accurate statement |
|---|---|
| Predecessor says test passed; you did not run it | `REPORTED_BY_PREDECESSOR` + witness link and dependency |
| You executed a command with inspected output | `EXECUTED_HERE` + command, environment, exit, log, exact candidate |
| A source-only script passed, browser was unavailable | Source check `PASS`; browser `NOT_RUN`, exact blocker |
| Genuine test failed | `FAIL`, captured counterexample and baseline/introduced classification |
| Received ZIP hash equals published Drive hash | `TRANSFER_HASH_MATCH` only; product validity remains unverified |
| A draft artifact PR contains one ZIP | `ARTIFACT_PR_READY` only after server readback; never `PRODUCT_DONE` |
| Original criterion still lacks decisive proof | `NOT_MET / NOT_RUN / UNKNOWN`, actor and smallest next observation |

**Do not hide failures or silently drop criteria.** A structurally complete self-check can be dishonest; validation, fresh model context, ZIP CRC and matching hashes do **not** establish independence, technical judgment or Owner acceptance. A blocker limits only work depending on it; keep moving on safe authorized tasks. New source bytes require updated checks. The Owner retains acceptance, merge and deployment.
