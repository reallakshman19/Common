# Methodology — make the second contribution materially better

The question is: **What useful result still fails after the first repair, and how can B deliver a better working candidate without replaying A's work?** A and B reason from original intent and actual source. A passing test is evidence for its actual input/candidate, not the whole system.

## A: first divergence to functioning repair

Trace input/authority → normalization/identity → transformation → consumer → observable output. For each consequential defect derive expected output, capture the actual wrong output, locate the earliest failing boundary, correct it, and execute the same failing case plus a valid positive control. Inspect real callers rather than assuming a helper is used. When deeper upstream/downstream tracing is needed, follow actual dependency edges, not an arbitrary depth quota. Prefer a small coherent repair over a broad rewrite. Record native code and test commands. Do not hide remaining failures from B.

## B: preserve, challenge, fix forward

Read A's actual source delta, current candidate, original requirements and selected evidence. Reuse verified unchanged evidence, rerun affected controls and choose one adverse case that would pass A's tests but violate the required outcome. Derive the expectation before running it. Try different input order, duplicate identity, stale state, malformed values, concurrent request ordering, or another domain-relevant contrary case. If the output is wrong, fix the earliest boundary and ensure downstream behavior. Do not just attach another review report. If the case passes, add a useful executable control or integration observation; no arbitrary code quota.

## Evidence levels

| Evidence | Supports | Does not support alone |
| --- | --- | --- |
| Original requirement and bytes | Expected behavior and exact input | Actual runtime result |
| Source inspection | Reachability, likely mechanism | Executed integrated behavior |
| Native focused test | Observed contract for that case | Untested real-world conditions |
| Negative control reaching target | Detection of a material wrong case | Universal correctness |
| Historical replay at recorded clock | Behavior for that snapshot | Live deployed output |
| Full native/boundary/browser execution | Observed integrated result for exact candidate | Release permission |
| Drive upload/readback | Transfer of identified bytes | Correctness or recipient execution |

Use `SUPPORTED`, `CONTRADICTED`, `NOT_RUN`, `UNKNOWN` at claim level. Do not turn a crash before the tested condition into a successful negative control. Keep assumptions, actual outputs, input hashes, source/candidate hashes, flags, commands and exit codes. A and B label self-authored changes and tests; neither agent's agreement alone proves independent correctness of the combined candidate.

## Efficient reconciliation

Use a single finding matrix inside the handoff bundle if multiple reports exist. Preserve original IDs, map equivalent first-divergence mechanisms, distinguish same symptom from same cause, record source/input/output and disposition. Do not stop execution because two reviewers chose different IDs. B can correct A's claim and implementation with actual evidence. An unavailable tool is a reason to narrow a claim, not to abandon executable work. Do not add HOLD-only scaffolding and call it a completed repair.

## Practical acceptance pattern

A's before/after control catches bug X. B uses A's exact candidate and shows bug Y survives, implements a minimal correction and runs X and Y. B delivers C2 and both witnesses. If B's Y fix regresses X, B repairs X now. The example in `examples/golden/` is executable and demonstrates this sequence without invoking any separate reviewer or third agent.
