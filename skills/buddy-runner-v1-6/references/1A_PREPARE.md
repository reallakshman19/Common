# G1 preparation template — produce artifact 1a, then HOLD

**Think:** What should the successor investigate independently to discover a better route toward the Owner's actual outcome?

1. If my proposed solution disappeared, what outcome would still be required by the parent issue and roadmap?
2. Which exact source, inputs, consumers, competing implementations and acceptance conditions must G2 inspect? Which predecessor conclusions remain hypotheses?
3. Which uncertainty should G2 resolve before implementation, and which established semantics must survive?

Fill the reusable intake with real values. Record the handover ID, outgoing/incoming agent IDs, repository, current/parent issue, roadmap refs, immutable inherited SHA, source refs, preservation constraints and original intent provenance. Use `owner_source_grade: UNKNOWN` when necessary; a narrative hint is not authority. Point to existing coordination rather than creating another ledger.

Use [1B_INVESTIGATE.md](1B_INVESTIGATE.md) with [CONTRACT.md](CONTRACT.md), or render `phase: "1a"` using `buddy_runner_v16.py`. Return **one successor-ready prompt**, labeled artifact 1a, with the expected response 1b and execution HOLD until the incoming agent is invoked. Do not prescribe the diagnosis, run G2, edit product source or begin tests. Preserve unrelated already-authorized work outside this handover.

Required ending: `1a | EXECUTION=HOLD | NEXT=G2 independently investigates and submits 1b`
