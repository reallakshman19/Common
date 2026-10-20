# Owner's 60-second review of a fast local agent's return

**This is a reading aid, not a new acceptance gate.** If the agent made useful progress, retain it even when a claim must be qualified.

1. **What exact artifact changed?** Can you open the returned file/branch/patch, not just its filename or a promised ZIP? Is the candidate hash/revision tied to the tests?
2. **Were the actual Owner criteria preserved?** Count complete original IDs, not only the ones the agent chose to mention. Who supplied the original criteria snapshot?
3. **Where are the bad results?** Find the exact failed/skipped/blocked/old failure ledger. If everything supposedly passed, ask what was not run and why.
4. **What really ran?** Look for command, exit, environment, raw log and actual output. A screenshot of a green button, producer-provided manifest and a test command pasted in prose do not establish execution.
5. **Did the contrary case fail?** Could the same test accept a known wrong outcome? Was the negative run on the real owner/consumer or only a toy?
6. **Is the state protected?** Ask whether original bytes, settings, reviewer identity, transactions, other work and authorization remained correct.
7. **Is a failure still open?** If an agent claims the issue is fixed, find the new-candidate witness for that exact old defect. Old reviews do not self-update.
8. **What decision is actually requested?** More authorized work, missing input, Owner acceptance, merge or deployment are different actions.

**Link-based review:** Ask for the **existing task issue/comment permalink**, not another pasted chat. If the handover claims to ship a ZIP, check the **separate DRAFT artifact PR** in [Common project-wise local-agent-handoffs](../../../local-agent-handoffs/README.md) when the project is permitted to publish there, confirm the server diff is **exactly one file**, inspect its SHA-256/size and whether it is the exact file the tests cite. A produced manifest or un-read-back comment alone isn't independent evidence. See [GitHub relay](COMMENT_RELAY.md).

If an answer is absent, request **one precise piece of evidence or the real artifact**; do not demand an elaborate reconstruction exam. A local agent can continue other authorized tasks while the specific claim stays NOT_RUN/UNKNOWN.