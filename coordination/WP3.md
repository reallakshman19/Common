# WP3 — Private materialized Control Tower read models

**Scope:** Issue [#353](https://github.com/reallakshman19/Common/issues/353), WP3 only. This is **not** the WP4 public feed or WP5 Owner command API. It does not replace coordinator v3.28 decisions, alter AIM authority, or start a browser/PowerShell process when queried.

## Authority and input contracts

1. **Identity:** `ControlTowerRegistry` populated from an explicitly pinned private manifest. Registry display names, tab aliases and chat IDs alone are never global identities.
2. **Engineering evidence/CI:** existing WP1 SQLite WAL source. Child-issue canonical evidence is project-level *UNATTRIBUTED* until an explicit `task_attributions[]` record has valid, source-pinned Work/Assignment/Run/Task/child-issue IDs and a validity interval. This is a declaration of join authority, **not** Owner acceptance or a new lifecycle verdict.
3. **Runtime:** explicit WP2 private `coordinator_observation_snapshot` files, source hash, project/coordinator/session/chats/binding generation. The ten coordinator strings remain verbatim.
4. **Provider status:** WP1 `project_cursors` observation. When no cursor exists, provider reachability is `UNKNOWN` even if a UI config says `ACTIVE`.
5. **PR head:** optional `pr_bindings[]` *source-verified by its upstream producer* with Work, immutable repo ID, PR number, current provider-observed SHA, observation timestamp, URL and applicable required jobs. Old, skipped or stale checks never become `EXACT_HEAD_PASSED`. Owner `acceptance_status` remains unchanged.

## Explicit materialization (a trusted local operator step)

Run a local, separately scheduled process, **not** an API GET:

```bash
python -m coordination.projections \
  --manifest /private/coordination/wp3-manifest.json \
  --evidence-db /private/coordination/evidence_index.db \
  --projection-db /private/coordination/projection_index.db \
  --as-of-utc 2026-10-12T12:00:00Z
```

The manifest is `WP3_PRIVATE_MANIFEST_V1` with **required** `registry_source_ref` (a trustworthy HTTPS source), `source_watermarks` (explicit version vector), and arrays `projects`, `works`, `execution_lanes`, `assignments`, `runs`, `tab_bindings`, `observation_files`. Entity dictionaries have exactly the corresponding dataclass fields in `contracts.py`; snapshot filenames are relative to the manifest directory and cannot escape it. Optional `task_attributions` and `pr_bindings` are not invented by WP3. The coordinator registration/manifest publisher is **not automated here**; only supply entries whose provenance has been independently checked.

Sample optional attribution record:

```json
{
  "project_id": "common",
  "task_id": "WP3-353-W01",
  "child_issue": "reallakshman19/Common#353",
  "work_id": "common-work-0",
  "assignment_id": "common-assignment-0",
  "run_id": "common-run-0",
  "source_ref": "https://github.com/reallakshman19/Common/issues/353",
  "source_revision": "approved-plan-r3",
  "valid_from_utc": "2026-10-12T00:00:00Z",
  "valid_to_utc": null
}
```

Example optional PR binding requires `project_id, work_id, repo_id, pr_number, current_head_sha, observed_at_utc, source_ref, required_jobs[]`. `observed_at_utc` must be no older than 3600 seconds relative to the explicit `as_of_utc` for a current CI conclusion.

The materializer writes a transactionally consistent SQLite generation, a content digest derived from sorted rows and explicit clocks/watermarks, and read indexes. Replaying identical source inputs/as-of produces the same digest. A new generation expires prior-generation pagination cursors with HTTP 410.

## Internal read API

Set trusted local server config `server.projection_db_path` to the materialized file. Then:

```text
GET /api/v3/projections?view=portfolio
GET /api/v3/projections?view=works&project=common
GET /api/v3/projections?view=assignments&limit=50
GET /api/v3/projections?view=unassigned_observations
GET /api/v3/projections?view=evidence&project=common&cursor=...
GET /api/v3/projections?view=recovery
```

Views: `portfolio`, `works`, `assignments`, `unassigned_observations`, `evidence`, `recovery`. Pages contain at most 200 rows. Responses retain a generation watermark; cursors are only valid for the exact view/project/generation and expire when new materialization is published. An absent index returns 503 rather than synthesizing agent or project observations. API performs no SQLite writes or PowerShell calls.

**Limitations:** No automatic registry publisher, no unattended refresh scheduler, no public redaction/export, no inferred missing BuddyRunner stages, no final lifecycle evidence qualification for WP1 records, and no Owner command/delivery plane. Data is only as fresh as explicitly materialized sources; the API never asserts live agent activity from task evidence.
