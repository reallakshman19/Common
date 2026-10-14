# M1 GitHub source/row seam v1.0.0 — source-derived contract

Status: **M1-U01 implementation candidate**, not an accepted product API. Source pin: `Common@7c1543a3e3ee5ba08314c20a4a70c1d94299476a` (AGENTS.md, v3.2/SKILL.md, coordination/indexer.py, projections.py, contracts.py, command_service.py, tests). Owner scope: [#360](https://github.com/reallakshman19/Common/issues/360); assigned leaf: [#373](https://github.com/reallakshman19/Common/issues/373). Owner claim mapping: C1 to M1; C3a ordered, private/conditional, also M1; C2/C3b to M2, C4 to independent M3.

## Invariants and observed limitations

* Public allowlist for the first observable slice: repository identity `1412133785 / reallakshman19/Common` and `1363905693 / reallakshman19/AA3` (verified GitHub identities). These are **sources**, not automatic work/agent attribution. Every work/agent comes from a separately explicit, compatible, versioned registry binding. Unknown or unregistered providers stay UNKNOWN/unassigned.
* The stable GitHub object key is `(numeric repo_id, source kind, provider entity_id)`. Use the GitHub numeric comment id for ISSUE_COMMENT, issue id for ISSUE, PR id for PR, check-run id for CHECK_RUN. Issue number is navigation, not globally unique identity. `revision_id` is an observation revision identifier scoped to the stable object key, not authentication of author. Source body `body_sha256` hashes exact UTF-8 bytes.
* A source edit is a new observation when (provider updated_at, body SHA) changes; replay of the same exact observation is idempotent. A→B→A with three distinct edit timestamps must yield three ordered revisions even though only two content digests exist. If the same provider timestamp gives different bodies, mark conflict rather than silently select one. Missing historical timestamps must be typed UNKNOWN and never synthesized as verified identity.
* Full pagination (including resume/restart after partial pages) is necessary before inferring an entity is absent or deleted; failed/partial/permission-limited scans keep the previous known row, mark source unavailable and do not emit a tombstone. After a completed consistent scan, absence is `ABSENT` and history is retained, never hard deleted.
* Provider status per source is independent: REACHABLE/PARTIAL/RATE_LIMITED/FORBIDDEN/UNAVAILABLE/UNKNOWN; freshness is FRESH/STALE/UNKNOWN and must be clock/source-grounded. Missing does **not** mean zero or offline. 401 remains authentication failure, 403 authorization, 429 rate-limit and 5xx unavailable in intake error metadata. Per-repo failures cannot erase another repository.
* Provider report, coordinator observation and independent evidence review are disjoint provenance layers. A provider's PASS cannot be independent review. A reviewer verdict requires a separately attributed review ref. An OLD_HEAD review is historical, never current-head approval. Skipped/path-scoped CI is `NOT_APPLICABLE`, not PASS. No new universal native workflow/stage evaluator.
* Privacy: public rows are whitelisted typed IDs/statuses, canonical public GitHub URLs and digests. They do not contain raw body, tokens, private owner command queue, private chat/browser URL, cookies, local paths or unfiltered free prose. Never expose `command_db` through a public endpoint.

## Exact public row shape

`coordination/master_panel/models.py` implements `build_row`. Consumers MUST negotiate `schema_version == "1.0.0"`; unknown fields/versions must not be silently interpreted as acceptance.

| Field | Type and meaning |
|---|---|
| `schema_version` | exact string `1.0.0` |
| `source` | `{project_id,repo_id,repo_full_name,kind,entity_id,revision_id,issue_number?,comment_id?,body_sha256?,created_at_utc?,updated_at_utc?,url?}`; stable object and revision source |
| `binding` | `{state: BOUND/UNASSIGNED/CONFLICT, project_id, work_id?,lane_id?,assignment_id?,run_id?,provider_kind,conflicts:[]}` |
| `report` | `{provenance: PROVIDER_REPORT, task_id?,candidate_sha?,reported_status?}`; nullable/unknown, never acceptance |
| `coordinator_observation` | `{provenance: COORDINATOR_OBSERVATION, observed_at_utc?,liveness: ALIVE/STALE/STOPPED/UNKNOWN,probe_status?,source_ref?}`; independent of GitHub silence |
| `evidence` | `{reported_verdict,review_verdict,review_ref?,review_candidate_sha?,current_pr_head_sha?,candidate_relation:CURRENT/OLD_HEAD/UNKNOWN,applicability:APPLICABLE/NOT_APPLICABLE/UNKNOWN}` |
| `source_health` | `{state,observed_at_utc?,freshness,scan_completed}`; U02 adds cursor/error details to its source-status endpoint |
| `absence` | `PRESENT/ABSENT/UNAVAILABLE` at object level; identity/binding disagreement is separately `binding.state=CONFLICT` |

The proposed M2 read seam for M1-U03 is local GET `/api/master/v1/projects`, GET `/api/master/v1/rows?project_id=&limit=&cursor=`, and GET `/api/master/v1/sources`, with a generation-bound opaque cursor, bounded responses, selected project and strict loopback/Host/Origin controls. These three routes are implemented in `coordination/master_panel/read_api.py` as an isolated loopback read server. `GET /api/master/v1/rows` supports `project_id`, `limit` (1–200) and generation-bound opaque `cursor`; stale cursors return 409, unavailable DB returns 503, unknown projects return 400. `GET /api/master/v1/projects` and `/sources` expose allowlisted source health only. `GET` never fetches GitHub, dispatches a command or infers review. Default model displays UNKNOWN/UNASSIGNED until explicit, validated bindings/reviewer inputs are separately provided. Integration into M2 owner panel, live installed parity, load/performance and independent verified reviews remain NOT_RUN/NOT_IMPLEMENTED. No real SEND or private browser delivery is included. No real SEND or private browser delivery is included.

## Synthetic discriminating fixtures

`coordination/tests/fixtures/master_panel/positive.json` and `negative.json` carry strictly synthetic bodies and expected typed outputs; verified Common/AA3 repository IDs are locators, not live fixture evidence. U01 model tests check A→B→A, idempotent replay, same-number different-repo collision isolation, independent review separation, stale SHA and binding/scan failures. U02 must add durable restart, full/partial pagination, disappeared-comment tombstones and source HTTP/rate tests before those claims can qualify.

## Integration and writer boundaries

U01 uses isolated new `coordination/master_panel/` and new tests/fixtures only. U02 may add `github_source.py` plus `storage.py`. U03 may add read API and a justified minimal integration with existing `coordination_ui.py`; M2 owns visual panel and C3b. U04 is conditioned on an actual authorized private destination and coordinator consumption policy; existing `command_service.py` has local admission but does not authorize SEND. M1 final handoff ends M1 writes; Codex repairs and M3 independently verifies its corrected SHA. No changes to project policy, oracle, skills, workflows, public deploy or protected controls.
