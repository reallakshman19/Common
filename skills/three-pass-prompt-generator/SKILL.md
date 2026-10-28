# Three-Pass Prompt Generator

## Finished publication example

Use `examples/clean-five-prompt-packet.md` as the agent-facing publication reference.

Keep internal generator/compiler diagnostics out of the durable engineering issue unless the diagnostic itself is under investigation. The published artifact should foreground the five prompts, target, basis and schema revision. — Standalone Launcher

This skill exists only to generate the five sequential prompts defined by its canonical three-pass schema.

It is deliberately isolated from engineering-delivery, takeover, certification, qualification, execution-package, relay, and admission workflows.

## Canonical files

```text
LAUNCHER:
skills/three-pass-prompt-generator/SKILL.md

SCHEMA:
skills/three-pass-prompt-generator/schema.md

VALIDATOR:
skills/three-pass-prompt-generator/validate.py
```

## Entry rule — before target reasoning

When the user asks to create, regenerate, review, or apply three-pass prompts, including wording such as:

```text
3 pass
three-pass
Prompt 0.5 / Prompt 1 / Prompt 2 / Prompt 2.5 / Prompt 3
complex Q1 to Q5
complex Q1–Q5
```

execute this sequence exactly:

1. **Do not inspect the target issue/repository/product yet.**
2. Fetch `skills/three-pass-prompt-generator/schema.md` from current `main`.
3. Read the protocol revision from that live file.
4. Record the actual fetched blob/content SHA.
5. Only if the live fetch succeeded, enter `GENERATOR MODE = THREE_PASS_ONLY`.
6. The generated artifact must start with the schema's required `# SCHEMA EXECUTION HANDSHAKE`.
7. Only after the handshake basis is established may you inspect the user-named target and supporting evidence.
8. Freeze the user's explicit operational intent separately from the target/problem; do not let an analyze-then-act request collapse into recommendation-only output.
9. Generate exactly the artifact required by the live schema.
10. Validate the artifact with `skills/three-pass-prompt-generator/validate.py` using the fetched schema SHA when executable validation is available.
11. Return the schema-defined artifact and **STOP**.

## Isolation rule

For this task, do **not** load or apply:

```text
skills/engineering-pr-delivery-v2.5/SKILL.md
skills/engineering-pr-delivery-v2.5/operating-model/**
skills/engineering-pr-delivery-v2.5/templates/**
skills/engineering-pr-delivery-v2.5/schemas/**
```

except when the user explicitly asks to combine protocols.

Those files govern a different engineering-delivery workflow.

They are not supplementary instructions for three-pass prompt generation.

Repository and issue files for the **user's target** may of course be inspected after the schema handshake because they are evidence, not generator-control instructions.

## Early-pass interaction contract

Prompt 0.5 and Prompt 1 must be **independently framed** from the same stable project truth.

- Prompt 0.5 asks what the governing area must contribute to the programme.
- Prompt 1 asks what excellent handling of the exact local responsibility demands in the lived problem.
- Prompt 1 MUST NOT inherit Prompt 0.5's speculative conclusions, reframings or proposed missing capabilities.
- The generator may use detailed target/task/witness taxonomy internally, but the downstream prompts should normally speak in natural project/domain language.
- Do not impose novelty quotas such as "find three non-obvious ideas".
- When a real witness exists, Prompt 1 should work it and then vary/contrast one material feature to discover what generalizes.
- When no honest witness exists, do not invent one.

The intended relationship is:

```text
stable programme truth ──► Prompt 0.5 independent contribution view
          │
          └──────────────► Prompt 1 independent situated-problem view

Prompt 0.5 result ─┐
Prompt 1 result   ─┼──► Prompt 2.5 reconciliation
Prompt 2 reality ──┘
```

## Complex Q1–Q5

When the user requests complex Q1–Q5, those are the five human reasoning territories defined by the live standalone schema.

They remain inside Prompt 1 as **coverage diagnostics**, not a mandatory five-part rhetorical skeleton. Prompt 0.5 is the separate programme-level independent pass and Prompt 2.5 is the separate integrated reality+reconciliation bridge.

Do not create any extra workflow stage, machine metadata block, or evaluator requirement beyond the five schema-defined prompts.

Only expose visible Q1–Q5 headings when the user explicitly asks to see those labels. Otherwise the generated Prompt 1 should remain one coherent, natural practitioner prompt.

## Fail closed

If the canonical schema cannot be fetched from current `main`, do not reconstruct it from memory, prior chat context, another skill, or an older revision.

Return only the schema handshake failure required by the schema and stop.

If an output begins with target analysis, Prompt 0.5, or Prompt 1 before proving the live schema handshake, that run is invalid.
