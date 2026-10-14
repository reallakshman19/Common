# BuddyRunner v1.7 — versioned enhancement

**Purpose:** Improve incoming-engineer comprehension **inside** existing BuddyRunner, avoiding an extra VAHO or Owner-approval round.

## Delta from v1.6

- 1a prompts outgoing G1 to supply predecessor/peer/fixture evidence for G2, not an imposed solution.
- 1b explicitly reconciles successor role, prior owner, vertical responsibilities, authoritative inputs/schema/blueprint/golden/benchmark **approval scope**, user-visible gap to the original issue, and up to three falsifiable ROI opportunities.
- 2 preserves the twelve-section self-contained handover, with more precise role/input/approval and delivery-gap language.
- Optional Owner nudge available for later material misunderstandings during **normal successor work**; not a new step/required receipt, never reopens 1b or 2.
- Xb → Y, phase enum, outgoing/incoming role split, evidence digests, source-commit validation, canonical response identities and duplicate-claim behavior remain the same.
- v1.6 remains **unchanged** for existing interactions; new invitations explicitly select `buddy-runner-v1.7`. No retroactive migration of a closed v1.6 handover.

## Tests

```bash
python -m pip install 'jsonschema>=4.18,<5'
python -m unittest discover -s skills/buddy-runner-v1-7/tests -p 'test_buddy_runner_v17.py' -v
python -m unittest discover -s skills/buddy-runner-v1-6/tests -p 'test_buddy_runner_v16.py' -v
python skills/buddy-runner-v1-7/scripts/buddy_runner_v17.py --input skills/buddy-runner-v1-7/examples/handover-1a.json --output /tmp/buddy-v17-1a.md
```

**Release state:** review candidate. This repository change grants no Owner policy approval, new lease, code-writer role, merge, deployment or academic rights.
