# R8 — link-only synthetic cold-process recovery (NOT independent-agent or real Owner acceptance)

**Canonical Owner:** [parent #787](https://github.com/reallaksh19/Common/issues/787), [R8 task #847](https://github.com/reallaksh19/Common/issues/847), latest merged source head baseline `bb1b02dfc9fc47346c0c53dc7b87dc5399bf8dc0`. Active reviews [#841](https://github.com/reallaksh19/Common/issues/841) and #824/#827/#831/#835/#840/#844 are not accepted. Original real Owner chat source UNKNOWN, do not publish private ChatGPT/Codex/Claude exchanges.

## What is genuinely new
The merged full-chain test `full-chain-rehearsal-v1.test.mjs` supplied R1 synthetic Owner seed, event bindings and SHA expectations inside its own test process. Passing native GitHub GET proved module integration, **not** fresh-executor reconstruction with no in-memory conversation. R8 moves these **public synthetic-only** expectations into a bounded, hash-pinned GitHub manifest under `fixtures/cold-synthetic-recovery-manifest-v1.json`.

`cold-recovery-v1.mjs` accepts **only**:
1. `manifest_url`: literal immutable GitHub blob permalink `https://github.com/reallaksh19/Common/blob/<40hex-PR-HEAD>/skills/engineering-relay-v1/fixtures/cold-synthetic-recovery-manifest-v1.json`
2. `manifest_sha256`: *caller-supplied expected raw manifest SHA256*, not derived from native provider answer;
3. `pr_url`: `https://github.com/reallaksh19/Common/pull/<number>`;
4. `expected_head_sha`: exact original 40hex PR commit.

It first rejects mismatched repo, path, commit/head and unknown fields; performs **real read-only GitHub Contents GET** at `?ref=<expected_head_sha>`; verifies path/type/base64/decoded size/Git blob SHA1 and caller-pinned raw manifest SHA256. A separate GitHub GET for the journal is performed by **actual merged G2c/R2-B1/R2-A/R1**, and R3 fetches live parent/child/PR HEAD and selected Actions state, followed by R4 pure same-snapshot title/scoreboard/handover previews. A moved head fails closed. The external expected digest proves agreement with the caller's pointer only; it is **not a signature or independent Owner-authentication root**.

A fresh Node CLI process receives only the permalink, expected hash and PR URL/HEAD in argument/environment values; it reconstructs the R1 seed/bindings from the immutable public manifest, **not from parent process memory**. The CLI emits **one content-free JSON witness**, no source/journal/Owner text, including digests, PR and bounded source facts, with all authority flags false. Errors are sanitized to a code, never secret or user content. No GitHub issue or PR mutation is possible from this source.

## Reproduce from a cold command (only synthetic fixture)
Within a source checkout at this PR head (Node22/24):

```bash
export RELAY_COLD_PR_URL='https://github.com/reallaksh19/Common/pull/<CURRENT_PR_NUMBER>'
export RELAY_COLD_EXPECTED_HEAD_SHA='<CURRENT_FULL_PR_HEAD_SHA>'
export RELAY_COLD_READ_TOKEN='<READ_ONLY_GITHUB_TOKEN>'
node skills/engineering-relay-v1/cold-recovery-v1.mjs \
  --manifest-url "https://github.com/reallaksh19/Common/blob/${RELAY_COLD_EXPECTED_HEAD_SHA}/skills/engineering-relay-v1/fixtures/cold-synthetic-recovery-manifest-v1.json" \
  --expected-manifest-sha256 '<PRECOMPUTED_HASH_FROM_PINNED_MANIFEST>'
```

The caller/reviewer should obtain and hold the expected hash **independently of this process**; in CI the local checked-out manifest hash is a **producer-controlled test fixture**, explicitly not a separate trust anchor. The returned `recovery_mode` says `FRESH_PROCESS_READ_ONLY_NOT_INDEPENDENT_AGENT`: this proves process isolation, not that a different reviewer or agent performed an independent Owner-intent reconstruction. A true link-only *different-principal* cold challenge must happen later with a distinct agent independently checking Owner instruction/source references and making a verdict, not by a subprocess with the same code/principal.

## Anti-draft and CI
The read-only PR workflow `relay-reset-cold-process.yml` executes Node22 + Node24 fixture negatives and a true fresh-subprocess native GitHub read at its **exact PR head**: no skipped native smoke. Tests mutate a self-consistent SHA manifest's claimed Owner consent, source repo/parent, binding, path, workflow, session graph; wrong immutable permalink/head; bad SHA; oversized/invalid manifest and raw leakage; subprocess errors never echo token. Output is intentionally synthetic.

**Permissions:** only contents/issues/PRs/Actions read; `persist-credentials:false`; no `pull_request_target`, write token, publication workflow or auto-review. The GitHub output is a read-only **proposal** and may change after the R3 double-read. CI selected-path green does not imply all branch required checks.

## Safety and acceptance
This manifest contains a **public synthetic prompt**, not an authenticated real Owner message. No private transcript ingestion, independent retained external anchor, accepted real TaskEvidence, human retention/consent grant, release writer, automatic issue scoreboard/title or genuine new-agent acceptance. None of AC1–AC8 is automatically satisfied. Original parent section 0 remains the Owner authority envelope; this manifest cannot supplant it. `authorization_granted:false`, `owner_message_authenticated:false`, `independently_accepted:false`, `live_writer_enabled:false`, programme **AC0/8**. B2b/R5 remains HOLD.
