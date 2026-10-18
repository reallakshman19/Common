# Owner prompts

Replace `<SKILL_URL>` with the immutable BuddyRunner v2.0 revision selected for the pilot. Replace one starting reference; the incoming agent discovers the governing issue, amendments, source, history and real scope. The Owner need not fill an internal schema.

## Recovery: continue the existing authorized task

```text
Use BuddyRunner v2.0 at <SKILL_URL> in RECOVERY mode; the previous agent is unavailable.
Recover <owning issue/PR URL> from my original intent and current source, select the highest-ROI next action, and continue within existing authority. Keep any PR draft.
```

## Onboarding: understand first, receive the task later

```text
Use BuddyRunner v2.0 at <SKILL_URL> in ONBOARD mode.
Reconstruct <repository/owning issue URL>, explain my intended outcome and the best route forward, then wait for my reconstruction approval and next task before coding.
```

## Approve onboarding without a task

```text
I approve this reconstruction with its stated evidence and limits. Wait for my next task; do not resume an older assignment.
```

## Approve onboarding and assign a task together

```text
I approve this reconstruction with its stated evidence and limits.
Next task: <one concrete outcome>. Boundaries: <only new restrictions or amendments>. Keep any PR draft.
```

The task may differ from the recommendation. Reuse understanding and refresh affected facts; do not restart the entire handover.

## Assisted predecessor becomes unavailable

```text
Continue the existing takeover in RECOVERY mode; G1 is unavailable.
Retain the same takeover identity and completed source-backed work, resolve remaining uncertainty, and continue within the existing task authority.
```

## Optional one-line context

- If original purpose is absent from the linked source: `What I ultimately want is <human outcome>.`
- Label a pasted predecessor report: `Previous agent report: verify these claims against current source.`
- For a restricted session: `Read-only reconstruction; return the direction here without publishing or changing project files.`

Select an explicit capable model and High/Extra High effort in the actual launcher/UI where supported. Prompt wording does not switch the runtime. Record actual configuration evidence and its limits; do not turn an unverified profile into a qualified takeover.

Ask the agent for its engineering result and first justified action. Twelve headings, test totals, a published comment or populated configuration fields do not establish semantic understanding, product acceptance or executed continuation.
