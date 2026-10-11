# R3-N02 — real-public provider GET canary, source-shape PASS / Owner-graph HOLD

**Date:** 2026-10-11, chat `6acb76ac`. **Plan:** [#325 `TAB1-G6-R3` PLAN_UPDATE 6109161373](https://github.com/reallakshman19/Common/issues/325#issuecomment-6109161373). **Candidate:** draft [#337](https://github.com/reallakshman19/Common/pull/337) at source `8882aab2965e8beed3fbb641406bf3b0d1463b98` stacked on #313 `690dd1565bfb4c15067528a51c7146fc0f75faaf2`. **Target consumer:** #326 `generic_source_preflight._read_source` / `BoundReadOnlyGitHubProvider` at `6b138b63d4347500a4fba2cad59f1fcfed0bfaf2`. **No product change in this unit;** five public GitHub REST GET endpoints read **twice** in two bounded passes. **No raw human body/comment data published.**

## 1. Current public provider observation — 10 GETs, two passes

Endpoints: `GET /repos/reallakshman19/Common`, `GET /issues/289`, `GET /issues/325`, `GET /pulls/326`, and `GET /commits/main`, then the same sequence again. Values below are actual provider-returned fields and were compared between two passes, not recreated from issue descriptions.

| Required property | Pass A | Pass B | Assessment |
| --- | --- | --- | --- |
| Repository | `reallakshman19/Common` ID **1412133785**, default `main` | Exactly same | `PUBLIC_PROVIDER_SHAPE_MATCH` |
| Root-like issue 289 | number **289**, state **open**, title present, body present (36,925 chars) | Exactly same | Verified actual issue GET `number/state/title/body`, not evidence of root graph binding |
| Leaf-like issue 325 | number **325**, state **open**, title present, body present (9,433 chars) | Exactly same | Verified actual issue GET `number/state/title/body`, not a graph-selected released leaf |
| Selected code PR 326 | number **326**, state **open**, `draft=true`, `merged=false`; `head.sha=6b138b63d4347500a4fba2cad59f1fcfed0bfaf2` | Exactly same | Verified required `number/state/merged/draft` booleans, no inferred default |
| PR head/base repository | both full name `reallakshman19/Common`, ID **1412133785**; `base.ref=main`, recorded PR base SHA `c4bcd4e3a98d6d9bfaf2520213e2a819e80d6c2a` | Exactly same | Provider same-object check. PR recorded base SHA is a historical PR base snapshot and need not equal moving current main |
| Current main commit | `5e0cd7a1ae6c69a2aeaadffe9a7092326ea6bc8f` | Exactly same | Bounded pass stability only, **not** GitHub-wide transaction |
| Original/main graph file at that commit | `.github/v32-evidence-spine/718-proposal-v2.json`, Git blob `d35019b416cb3b573280e166027d3f65ba61f59c` declares `programme.repository=reallaksh19/Common`, root `Common#718` | Graph file read separately at pinned main SHA | **`GRAPH_REPOSITORY_MISMATCH` for new repo: HOLD**. Do not edit original graph bytes or invent a current released version |

This deliberately checks public provider **source-shape only**. The above issues are demonstration *public issue objects*, **not** a new Owner-adopted source graph or claim that they are the actual original lab root/leaf. The actual private lab `reallaksh19/relay-v32-e2e-lab` was not used; its GET remains 404 to this actor. The graph's old repo name cannot be changed to make T02 pass.

## 2. What is compatible and what still cannot pass

- **PASS — accessible GitHub REST GET source fields:** issue `number/state/title/body`, PR `number/state/merged/draft/head/base`, repo numeric full ID and exact candidate SHA exist as provider observations. R3-N01 #337 changes the existing #313 private capture to **validate and retain exactly those source fields**, with an eight-case adversarial fixture, preserving original metadata rather than fabricating it. This is a concrete improvement in the #313→#326 integration seam.
- **HOLD — actual graph and Owner authority:** historical pinned graph still names `reallaksh19/Common` not current `reallakshman19/Common` and is **not** an authorized current-repo graph. A true #326 `preflight(graph=that graph,repository=newRepo)` would refuse `REPOSITORY_SELECTION_MISMATCH` by source inspection. No program executed against an Owner-approved current original graph, and no native eligible E was accepted.
- **HOLD — full #326 T02 method completeness:** #313 `SnapshotGET` lacks `compare` and graph-provider `get_repository/get_file_bytes`; #326's `BoundReadOnlyGitHubProvider` is three injected GET methods, not full original source transport. This canary does not create those methods or claim `NATIVE_READONLY_GET_METHODS_REQUIRED`/graph custody satisfied. Live comment/compare pages and required CI policy were not traversed as complete native facts.
- **HOLD — qualified fact/reviewer/custody:** branch protection GET 403 and #326/#336 zero submitted review observations from prior Stage2, required-policy source and independent issuer/reviewers unproven. No real root/leaf/PR managed external write, independent B or Owner acceptance. Bounded 10 GETs are not a global atomic snapshot; main can move after the reported interval.
- **Separate native full-ref defect:** `source_bound_responsibility_core` protected basename-prefix check rejects valid full `owner/repo#PR` and remains parked until #316 exact Owner-approved, independently reviewed base-resident frozen amendment. The original graph must not be shortened.

## 3. Verification grade, follow-up and rollback

**Decision:** `PUBLIC_GET_SURFACE_COHERENT_UNQUALIFIED / OWNER_GRAPH_MISMATCH_HOLD`. N02's defined read-only acceptance is **DONE**: actual provider field values and two-pass source stability were checked; the full Owner lifecycle is **NOT_PROVEN**. No code, settings, original graph, user content, comments, PR metadata or production status were modified in this N02 canary. There is no rollback operation.

**Next:** R3-N03 exact-head workflow/step applicability for #337; report dedicated PW04 and Local steps separately from native V3.2/DELP skips, plus changed-path/frozen safety and result. Do not merge PR #337 or #313, claim current eligible E, actual original lab, T04/T05 or source-authorized B. **Root AC0/8, release HOLD, handover=no.**
