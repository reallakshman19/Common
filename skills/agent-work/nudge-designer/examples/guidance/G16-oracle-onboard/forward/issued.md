# Oracle OnBoard Prompt — ONBOARD-DEMO-01

You are continuing the authorized task in the supplied receiver copy. Read the essential originals and current candidate, then execute the repair within the existing authority. Treat this explanation as revisable. No questionnaire, admission test, separate reconstruction report, or additional role is requested. This is a context handover, not an independent or blind review.

## Purpose

The original Owner says: “Keep draft masses when I leave and return to Review. Drafts are not accepted decisions. I still need a trustworthy full-model native export later.” The Owner also states that an explicit zero draft is legitimate; an absent value or `None` is not an approved zero. Keep models separate. Negative and non-finite values are rejected upstream, outside this task.

The authorized local task is to repair draft persistence in `save_drafts` / `load_drafts` using the supplied workspace owner. This supports returning to Review with the user's draft values intact. Full-model native export, integration validation, and Owner acceptance remain unfinished after this local task. Do not add export or change acceptance authority.

## One bounded task

Repair `drafts.py`, add focused local tests as useful, and return the actual change and evidence in `result.md` in the receiver folder.

FACT from current B2 source inspection: `save_drafts` already writes to `workspace[model]`; `load_drafts` reads that model's entry and returns a dictionary copy. The earlier explanation that a render-local Map is discarded does not describe these supplied functions. Do not implement a workspace migration on that premise.

Working explanation: the save comprehension keeps entries only `if value`, so it discards explicit numeric zero along with `None`. HYPOTHESIS: that truthiness filter is the local persistence defect relevant to the Owner's zero requirement. Check this against the original Owner record and local behavior before repairing it. A plausible alternative or additional cause of navigation loss is a caller using a different workspace/model or failing to save; no caller or full application is supplied, so local function checks cannot settle that integration question.

Use this guided method:

1. Read `OWNER.md` and `drafts.py` at the paths below. Verify and retain the issued B2 identity before editing. If the bytes differ, record the observed digest and exact difference; do not silently label a different candidate B2.
2. Use local Python to establish the relevant current behavior, including explicit zero, a normal nonzero draft, `None`, and an absent key. Preserve a decisive failing pre-repair observation where possible. Do not change expectations merely to obtain a pass.
3. Repair the save/load behavior according to the Owner's distinction: keep an explicitly provided zero as a draft, and do not turn `None` or a missing value into an approved zero. Keep the current function signatures, workspace-per-model ownership, and dictionary-copy behavior. Retain the existing replacement behavior of a save unless evidence from the supplied originals requires a change; there is no authorization here to invent merge semantics or a new state architecture.
4. Run focused checks on the repaired functions, including a save/load round trip and the contrary cases below. Inspect the final source and report what the checks establish. No browser or full-app result can be inferred from them.

## Authoritative inputs and issued identity

All receiver writes must stay under:

`/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/`

Original Owner record:

`/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/OWNER.md`

SHA-256: `dc42488aa420006c253f0437ba89039a1b8930c202871727cb6cc0ba6164c7e5`

Candidate B2:

`/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/drafts.py`

SHA-256: `3242f3fd9ba204045000a732f04f7a7adc4ca9ca2fcb30f450275b630c43df2a`

The issued B2 source is reproduced here to preserve the original bytes and comparison basis: UTF-8 text, LF line endings, one final newline.

```python
"""Synthetic B2 persistence operation; upstream validation is not represented."""


def save_drafts(workspace, model, edits):
    workspace[model] = {key: value for key, value in edits.items() if value}


def load_drafts(workspace, model):
    return dict(workspace.get(model, {}))
```

Preparation consisted of reading the two originals and calculating their digests. No Python behavior, test, or repair was executed during preparation. The Owner reports a predecessor's focused pass on an earlier candidate; no B2 execution receipt was supplied. That report is historical context, not proof about B2. No completed context-flow outputs are supplied or need to be repeated.

## Boundaries

You may modify `drafts.py` and add local tests in the receiver copy. Write the required native return artifact `result.md` there. Preserve the issued source and digest in that return, alongside the final candidate's digest and the actual change. Do not edit `OWNER.md`, this issued prompt, or anything outside the receiver folder.

Keep draft state distinct from accepted decisions. Preserve model separation and the existing public API. Do not add export, acceptance logic, browser scaffolding, or upstream negative/non-finite validation. The synthetic fixture is not a real product task and establishes nothing about an intended model configuration. Do not consult golden/reference cases or other histories, and do not delegate.

## Success criteria

Local PASS requires evidence that explicit zero and ordinary nonzero drafts survive save/load with their values intact; missing and `None` inputs are not manufactured into zero drafts; saving one model does not disturb another; and an unknown model loads as empty. Preserve and check the returned-dictionary copy behavior so editing a loaded result does not silently mutate stored drafts.

The discriminating contrary cases are zero versus `None`/absence and one model versus another. A test that only saves positive values does not distinguish the suspected defect. A correct local repair must satisfy both sides of these distinctions.

Report local completion as PASS, FAIL, or BLOCKED, with the actual evidence. Use UNKNOWN for claims the available evidence cannot settle, and NOT_RUN for checks not executed. A local PASS may complete this repair task; navigation in the actual app, full-model export, Owner acceptance, and release remain separate and unproven here.

## Uncertainty handling

Local Python and source are supplied as the receiver's available tools; Python was not exercised by the preparer. No browser/full app is provided. Check readiness early and record actual tool errors, if any.

If the originals or observations contradict the working explanation, cite the exact witness and revise the affected diagnosis or method within scope. Do not repair on a falsified premise. Resolve discoverable facts directly. Return only consequential missing intent or authority to the Owner. A tool or input restriction limits dependent proof; continue unaffected authorized work and state the feasible route for the missing validation.

## Evidence and continuation

Return via the native file:

`/workspace/scratch/52eed2252c51/onboard-forward-20261020/receiver/result.md`

Use assignment identity `ONBOARD-DEMO-01`; do not invent an ACK or competing task ID. A chat summary alone is not the artifact. Include:

- The original Owner/candidate paths and verified digests, preserved issued B2 bytes, final candidate digest, and changed files.
- Actual commands, observations, decisive failures/passes, or NOT_RUN. Distinguish source inspection from runtime evidence and historical claims.
- What changed in understanding, marking FACT, CLAIM, HYPOTHESIS, or UNKNOWN where useful.
- Local task status, limits of proof, and the remaining parent outcome.
- The next justified action, its actor and authority, and what observation would change that recommendation. For a blocked action include the attempt, observed restriction, affected scope, and feasible execution route.

You have standing authority to finish this bounded persistence repair and its focused local checks. If the local repair passes, recommend that the Owner or an authorized integrator validate leaving and returning to Review in the real app with zero/nonzero drafts and separate models. Retain the Owner's later need for a trustworthy full-model native export, without implementing it. Record unrelated findings for prioritization; do not expand this task to repair them.
