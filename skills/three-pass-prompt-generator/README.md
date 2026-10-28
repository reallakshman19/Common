# Standalone Three-Pass Prompt Generator

Use this package when the task is to **generate five prompts** under the three-pass method (GLOBAL IMAGINE → LOCAL IMAGINE → UNDERSTAND → RECONCILE → REVALIDATE AND MOVE FORWARD).

Canonical entrypoint:

```text
skills/three-pass-prompt-generator/SKILL.md
```

Canonical schema:

```text
skills/three-pass-prompt-generator/schema.md
```

Canonical validator:

```text
skills/three-pass-prompt-generator/validate.py
```

Recommended invocation:

```text
Use the current-main standalone three-pass generator:
https://github.com/reallaksh19/Common/blob/main/skills/three-pass-prompt-generator/SKILL.md

Create 3-pass prompts for <target>. The artifact must contain Prompt 0.5, Prompt 1, Prompt 2, Prompt 2.5 and Prompt 3.
Show them in chat.
<optional: add complex Q1–Q5 questions>.
```

The launcher must fetch the current-main schema and prove the live schema handshake before target reasoning.

The legacy path under `engineering-pr-delivery-v2.5/schemas/` is redirect-only.
