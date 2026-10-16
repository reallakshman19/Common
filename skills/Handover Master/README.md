# Handover Master — your one link

> **Invoke:** [SKILL.md](SKILL.md) — "Use Handover Master for this repository, issue and purpose; pick the correct native mode."

This folder is the **single decision entry point** for source-first technical handover, zero-exit successor onboarding, two-pass and three-pass thinking prompts, project-governed v3.6, BuddyRunner and read-only progress.

- [SKILL.md](SKILL.md) — single agent-facing master invocation
- [DECISION_GUIDE.md](DECISION_GUIDE.md) — full mode selection, authority, safeguards, good engineering practices and examples
- [MODULE_INDEX.md](MODULE_INDEX.md) — every original module as a clickable canonical link, with "when" and "don't"
- [sources.json](sources.json) — structured native path registry (NO code duplication)
- [route.py](route.py) — offline non-mutating recommendation of one native path and its prerequisites
- [tests/test_route.py](tests/test_route.py) — route selection, ambiguity, version/freeze and security regressions

**The one link is a router, not a move of code.** Existing source trees remain unchanged to prevent breaking hardcoded schema paths, shell scripts, import roots, CI, native privacy rules and v3.6 workflows. All choices can now be made starting here.

## Agent example

> Use [Handover Master](SKILL.md) to handle \`reallakshman19/<repo>\` issue \`#N\`. Inspect the current governing skill/source and latest Owner decisions. Decide whether I need technical handover, source-first zero-exit, two-pass, three-pass, BuddyRunner, or progress. Fetch current canonical source and validate its protocol; preserve blind-stage isolation, issue scope and approval. Explain why you selected the module. Do the next authorized step and report actual evidence.

## Interactive-ish local decision, without network or side effects

~~~
python "skills/Handover Master/route.py" --intent "three pass on our v3.6 issue"
python "skills/Handover Master/route.py" --mode two-pass --workflow standalone --format json
python "skills/Handover Master/route.py" --mode buddy --workflow v3.6 --phase 1a
python "skills/Handover Master/route.py" --mode zero-exit
~~~

A READ_SOURCE_NOW result is not a stage execution command or Owner approval. The selected native module owns schema live fetch, source SHA verification, preflight, actual execution and any external publication.

**Release boundary:** Common #391 remains open, ONB WP5 merged, earlier WP1a–WP4 drafts remain pending until independently reviewed. CoordinatorLandingpage #21, not Dash V2, is the possible later read-only consumer. This PR changes **nothing** in CoordinatorLandingpage, v3.6/3.5, BuddyRunner or native prompt modules.
