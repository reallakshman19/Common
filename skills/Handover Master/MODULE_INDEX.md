# Handover Master — one navigable index of canonical source modules

This is **one directory containing all module links**, not copies of the native implementations. From here, any agent can choose the correct workflow and then read the native source at current main. Version-specific protocols and privacy gates are not replaced. Links below are actual files identified at Common main `b92b6096c656c0c7f8f51b896ec4ea1da3c5a22e`; source HEAD may later move.

| Native module | When to select | Actual source link |
|---|---|---|
| technical | Native Stage2-only 12-section technical explanation; NOT allowed before authenticated freeze | [relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md](https://github.com/reallakshman19/Common/blob/main/relay/CONTINUITY/TEMPLATES/TECHNICAL_HANDOVER.md) |
| two_standalone | Two-prompt task-blind system baseline then Owner-governed reconciliation | [skills/two-pass-prompt-generator/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/two-pass-prompt-generator/SKILL.md) |
| three_standalone | Three main passes represented by native five prompts 0.5,1,2,2.5,3 | [skills/three-pass-prompt-generator/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/three-pass-prompt-generator/SKILL.md) |
| v36 | Project-governed engineering lifecycle including two/three-pass generators and cold successor | [skills/engineering-pr-delivery-v3.6/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/SKILL.md) |
| buddy17 | Explicit project-governed v1.7 role/peer source verification and 1a→1b→2 | [skills/buddy-runner-v1-7/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/buddy-runner-v1-7/SKILL.md) |
| buddy16 | Pinned v1.6 1a→1b→2 and one Xb→Y; native v3.6 requires this version | [skills/buddy-runner-v1-6/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/buddy-runner-v1-6/SKILL.md) |
| onb | WP5 zero-exit 12-section report/manifest/verdict; source truth BLOCKED without proof | [skills/relay-onboarding-rwi/reporting/WP5.md](https://github.com/reallakshman19/Common/blob/main/skills/relay-onboarding-rwi/reporting/WP5.md) |
| v35_legacy | Historical v3.5 projection/scripts, not current v3.6 | [skills/engineering-pr-delivery-v3.5/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.5/SKILL.md) |
| observer | Read-only workflow state/progress; does not start a phase | [skills/universal-workflow-progress/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/universal-workflow-progress/SKILL.md) |
| mcda | Optional independently approved qualitative/quantitative assessment, no override of Owner gates | [skills/software-mcda/SKILL.md](https://github.com/reallakshman19/Common/blob/main/skills/software-mcda/SKILL.md) |

## Additional precise entrypoints

### Standalone two-pass

- schema: [skills/two-pass-prompt-generator/schema.md](https://github.com/reallakshman19/Common/blob/main/skills/two-pass-prompt-generator/schema.md)
- validator: [skills/two-pass-prompt-generator/validate.py](https://github.com/reallakshman19/Common/blob/main/skills/two-pass-prompt-generator/validate.py)

### Standalone three-pass

- schema: [skills/three-pass-prompt-generator/schema.md](https://github.com/reallakshman19/Common/blob/main/skills/three-pass-prompt-generator/schema.md)
- validator: [skills/three-pass-prompt-generator/validate.py](https://github.com/reallakshman19/Common/blob/main/skills/three-pass-prompt-generator/validate.py)

### v3.6 native work

- two_script: [skills/engineering-pr-delivery-v3.6/scripts/prompt_2pass_v36.py](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/scripts/prompt_2pass_v36.py)
- three_script: [skills/engineering-pr-delivery-v3.6/scripts/prompt_3pass_v36.py](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/scripts/prompt_3pass_v36.py)
- cold_script: [skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.6/scripts/successor_v36.py)

### Pinned BuddyRunner v1.6

- script: [skills/buddy-runner-v1-6/scripts/buddy_runner_v16.py](https://github.com/reallakshman19/Common/blob/main/skills/buddy-runner-v1-6/scripts/buddy_runner_v16.py)

### Explicit BuddyRunner v1.7

- script: [skills/buddy-runner-v1-7/scripts/buddy_runner_v17.py](https://github.com/reallakshman19/Common/blob/main/skills/buddy-runner-v1-7/scripts/buddy_runner_v17.py)

### Merged zero-exit WP5 only

- compiler: [skills/relay-onboarding-rwi/reporting/compile_report.py](https://github.com/reallakshman19/Common/blob/main/skills/relay-onboarding-rwi/reporting/compile_report.py)
- validator: [skills/relay-onboarding-rwi/reporting/validate_report.py](https://github.com/reallakshman19/Common/blob/main/skills/relay-onboarding-rwi/reporting/validate_report.py)

### Historical v3.5 reader

- script: [skills/engineering-pr-delivery-v3.5/scripts/handover_context.py](https://github.com/reallakshman19/Common/blob/main/skills/engineering-pr-delivery-v3.5/scripts/handover_context.py)

## Not a relocated runtime

The existing paths are load-bearing in imports, workflow jobs and original source contracts. Copying or moving them without migration tests would silently break consumers and could violate Stage-1 isolation. Master routes by user intent/governing version and points to current canonical files; it does not clone scripts or install draft WP1a–WP4. A later deliberate relocation needs separate Owner-approved migration with compatibility shims, exact import/Actions census, independent cold agent pilot, rollback and readback.

**Source authority:** Common #391, accepted v3.6 #341, and CoordinatorLandingpage #21/#7 are the decision anchors. Historical #360 Dash V2 is superseded for downstream read-only consumer design. A link alone does not mean Owner approval or current source correctness.

## Current vs superseded (please do not confuse them)

**Current Handover Master** is [SKILL.md](SKILL.md). All native paths in the table remain available as explicitly governed or version-pinned modules. The Master does NOT make its underlying two-pass, three-pass, v3.6, BuddyRunner or ONB implementation folders obsolete.

**Truly superseded Dash V2 workspace** has moved byte-for-byte to [`/superseded/coordination/Session_Oct07/Tab6_Dashboard_V2/`](../../superseded/coordination/Session_Oct07/Tab6_Dashboard_V2/). Its old location now has a compatibility navigation README. The active UI destination is [CoordinatorLandingpage #21](https://github.com/reallakshman19/CoordinatorLandingpage/issues/21). See [archive migration audit](../../superseded/HANDOVER_FOLDER_AUDIT.md).

Return to [one entrypoint](SKILL.md) or [decision guideline](DECISION_GUIDE.md).
