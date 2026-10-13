# BuddyRunner v1.6 — Stage 1a preparation for IMO issue #183

**Scope selected from the active chat:** Grade9v3.5 issue [#183](https://github.com/reallakshman19/Grade9v3.5/issues/183), its 68-question QRT mapping, and the Owner's authentic Core2 + concept-specific Core1A aim. The [Common repository](https://github.com/reallakshman19/Common) supplies **BuddyRunner v1.6** as the process authority; this handover does not attempt to implement BuddyRunner itself.

**Phase:** `1a` (outgoing G1 prepares for distinct incoming G2). **Result:** source-bound investigation prompt exists. **Execution:** `HOLD`. **Incoming G2:** `G2_FRESH_IMO183` is a target role identifier, **not evidence that a new agent has been launched, assigned or independently responded**. No `1b`, final `2`, product coding or writer-custody transfer was performed.

## Artifacts

1. [ARTIFACT_1A.md](ARTIFACT_1A.md) — full successor-ready investigative prompt. Its embedded packet is deliberately converted to `phase: 1b` for the *future* G2 according to the v1.6 renderer. The `1b | SUBMITTED` ending is a prospective instruction, **not a claimed publication**.
2. [buddy-v16-1a-intake.json](buddy-v16-1a-intake.json) — declarative v1.6 request (`phase: 1a`) with exact issue, roadmap, actor roles, frozen source SHA and non-custodial constraints.
3. This file — evidence and execution boundary.

## Pinned authority

- Skill: `skills/buddy-runner-v1-6/SKILL.md` in Common/main at `80a5f66022177fc2884b04917cd31379112fbd3f`, `SKILL.md` blob `6f021469a55092f0e22f924f5a1f081a26e1cab6`; [contract](https://github.com/reallakshman19/Common/blob/80a5f66022177fc2884b04917cd31379112fbd3f/skills/buddy-runner-v1-6/references/CONTRACT.md) blob `fe26f7a`; [1b template](https://github.com/reallakshman19/Common/blob/80a5f66022177fc2884b04917cd31379112fbd3f/skills/buddy-runner-v1-6/references/1B_INVESTIGATE.md) blob `3f6a6bb`.
- [Grade9v3.5 issue #183](https://github.com/reallakshman19/Grade9v3.5/issues/183), [parent #137](https://github.com/reallakshman19/Grade9v3.5/issues/137), [roadmap #130](https://github.com/reallakshman19/Grade9v3.5/issues/130); frozen Grade9 assessed branch `agent/183-q003-private-core2-test-6acc303b@7cc27b7508282f1efed07b78e0285e2128aae643`; independently observed Grade9 main at `4dbedc6773482bbecb146ff8959614b2c32dcc6e`, not treated as the frozen branch.
- [Owner aim v3.1.0](https://github.com/reallakshman19/Common/blob/80a5f66022177fc2884b04917cd31379112fbd3f/relay/AIM/IMO-CORE2-CORE1A-68.yaml) label SHA `64a4e9c`; this repository's writer/governance/lease controls are preserved.

## Reproduce / validate

From a clean Common working tree with `jsonschema>=4.18,<5` and Python 3.10+:

```bash
python skills/buddy-runner-v1-6/scripts/buddy_runner_v16.py \
  --input coordination/Session_Oct09/Tab2_imo_core2_core1a/buddy-v16-stage1a-20261013/buddy-v16-1a-intake.json \
  --output /tmp/imo183-buddy-v16-artifact-1a.md
```

The committed artifact was constructed to match the **published v1.6 renderer composition exactly** (header, pinned contract and 1b template, response target, sorted embedded 1b intake) and verified by GitHub exact readback; **the native Python CLI was NOT_RUN in this session**. This distinction is material: successful source/structure verification does not imply an actual G2 investigation.

**On real invocation:** an independent incoming agent must receive the artifact, re-read the actual issue, Owner purpose, original/competing source and output, and return **one** `1b` response. Any actual role binding, provider publication and digest must be recorded on the existing issue/coordination surface before G1 proceeds to one final `2`. This does not create a new source writer, reviewer, licence, release or merge authority. Because G1 has already inspected current Grade9/COMMON source, **G1 cannot impersonate the independent G2**.

## Current work boundary

The 68-position map is source-safe research: 67 **tentative** QRT cell placements including 59 low-confidence metadata-only candidates, 1 figure hold; Owner-accepted QRT **0/28**, original Core2 admitted **0/68**, Core1A admitted **0**, rights **NOT_GRANTED**. Owner-approved `G-IMO-CORE2-UI-R1` is an *authored UI visual reference*, not source authenticity or a golden promotion of the lost native page. Reported A4 media-box geometry was local; Owner print quality remains pending. Keyboard/AX follow-up remains `DEFERRED_BY_USER`.

No changes to Common/main, Grade9v3.5 files, Common/relay writer state, issues #212 or #183 acceptance counters, PRs or original protected documents.

**Required ending:** `1a | EXECUTION=HOLD | NEXT=G2 independently investigates and submits 1b`
