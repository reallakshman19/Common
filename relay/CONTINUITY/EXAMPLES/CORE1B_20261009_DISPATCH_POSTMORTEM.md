# Core1B Runner Stage 1 — repeated verification without dispatch (incident record)

**Evidence grade:** repository facts independently read from GitHub; conversation statements about attempts and timing are **user-supplied incident transcript**, not independent platform runtime logs. **Governing issue:** [Common #890](https://github.com/reallaksh19/Common/issues/890).

## Source facts — verified, but only inputs

| Observation | Evidence |
| --- | --- |
| Original packet | [STAGE1_RUNNER_INPUT.md at \`aa1c1f2\`](https://github.com/reallaksh19/Common/blob/aa1c1f2fc40dfbfb6bbaf47f1847977ad171cb99/relay/CORE1B_GOLDENS_RUNNER_20261009/STAGE1_RUNNER_INPUT.md); blob `8746fb911f5f5d63a82e459e5439b2033b7017f1` |
| Source bundle commit | [Common \`d60c366\`](https://github.com/reallaksh19/Common/commit/d60c36605e988dcc160647421973f170fd87e0eb); packet unchanged |
| Bundle tree | `relay/CORE1B_GOLDENS_RUNNER_20261009/SOURCE_SNAPSHOT/`; tree SHA `927192e073c78ef464aa737738b239d4c9f3874c` |
| Source files | Nine historical `Grade9v3.5` blob entries matching the packet's allowlist (committed under `SOURCE_SNAPSHOT/Grade9v3.5/`) |
| Top-level entries | Exactly `STAGE1_RUNNER_INPUT.md` and `SOURCE_SNAPSHOT/` at frozen bundle commit |
| Runner actual execution | **NOT ESTABLISHED**: no independent B session or artifact documented in incident |
| Independent Stage 1 output/freezing | **NOT ESTABLISHED**: no externally submitted/frozen B reconstruction |
| Stage 2 disclosure | Not demonstrated |

**Correct conclusion:** `SOURCE_INTEGRITY_VERIFIED` and `DISPATCH_BLOCKED_NO_SESSION_CAPABILITY`, **NOT** `RUNNER_READY` / `RUNNER_STARTED` / `STAGE1_FROZEN`. Exact provider-readback of input files is useful once; repeating it is not a new gate.

## Failure chain and causes

1. Preparation agent published Stage 1 packet with explicit "start a fresh technically restricted Runner" requirement, and added nine source files.
2. Subsequent responding agent could read from the connected GitHub repository but **could not spawn or control a fresh independent model session and its tool restrictions**.
3. Rather than raising a durable one-time external dispatch request and stopping, the agent repeatedly re-read the same packet/directory, reporting essentially identical `RUNNER_LAUNCH_PENDING` states. "Worked for 37/43/12s" and repeated hash comparisons are not progress evidence.
4. The packet itself includes three Owner cases, **preselected Q1/Q2/Q3 engineering investigations**, "at least two designs", "three counterexamples" and a "bounded next implementation plan". This is **task-aware and prescriptive**, potentially prematurely steering B even though Agent A's current source and answer keys are withheld.
5. The packet and snapshot reside in public/broadly readable Common repository surfaces. A new B with unrestricted GitHub search cannot be declared restricted by a Markdown message. A copied nine-file snapshot proves source identity, **not** read isolation.

The missing work is a **dispatch-owner/capability boundary**, plus a baseline-first content audit, not another attempt to reverify nine source blobs.

## Correct resolution of this exact episode

1. Keep original committed packet and blob at immutable SHA; never silently rewrite it as though it had been frozen/reviewed.
2. An authorized controller should publish a versioned [RUNNER_DISPATCH_REQUEST_V1](../TEMPLATES/RUNNER_DISPATCH_REQUEST.md) referencing packet `aa1c1f2...`, bundle tree `927192e...`, source commit `778eb35a...`, actual external launch operator and exactly what B may read. If no operator/agent factory exists, say `UNASSIGNED` / `UNAVAILABLE_IN_THIS_SESSION` and **stop**.
3. Before **actual** independent B use, curate a revised task-aware Stage 1 input in a NEW revision that removes preselected B design quotas and copy-ready implementation plan, retains authentic Owner/three learner-facing cases, demands historical system baseline first, and distinguishes Owner questions from questions B develops.
4. Use an actually new, restricted independent B actor/context. Require a denied-read proof (A current PR and Stage 2 inaccessible) or honestly record `BLINDNESS_NOT_VERIFIED`.
5. B produces `STAGE1_RECONSTRUCTION_V1` at an authorized immutable path; independently verify B identity, output digest and source reference; an **external controller** creates `STAGE1_FREEZE_V1` before any current A reality release.

**Negative regression:** When input blob and nine files are unchanged and no external runner tool is available, a follow-up **must return one unchanged blocked status and external operator action, not another verification report or new workspace**.

**Authority:** This is an engineering postmortem and proposal, not a real external Runner launch or a replacement of Common's prior history. Local writer, Owner approvals and DELP progress remain untouched.
