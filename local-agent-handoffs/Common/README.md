# Common — local-agent artifact index

## Project identity

- Owning project: `reallakshman19/Common` — https://github.com/reallakshman19/Common
- Project slug: `Common`
- Governing sources: [repository instructions](https://github.com/reallakshman19/Common/blob/main/AGENTS.md) and [local-agent handoff route](https://github.com/reallakshman19/Common/blob/main/local-agent-handoffs/README.md).
- Common is public. Only synthetic or otherwise explicitly public-safe bytes belong here.

## Transport qualification

Non-issue transport tasks use `task-<stable-id>` under this directory. The initial `task-transfer-canary-20261025-a1` checks byte delivery only, using a synthetic archive; it has no product acceptance, implementation, release or deployment scope. It has no original project issue. Test authority and detailed operational receipts remain with the initiating session; the dedicated draft artifact PR records the public transfer evidence.

Binary transfers follow the existing one-file OPEN/DRAFT PR route: a fresh artifact-only branch from observed `Common/main`, exactly one ZIP path, and recorded SHA-256/byte length. The archive includes its README, manifest and applicable executed checks. Publication, recipient retrieval, hash verification and acceptance are distinct. No automatic merge, ready transition, cleanup or retention promise is introduced.
