# Handover folder disposition — post-Master source audit

Source basis Common main `eff86f7885d759449c4125c9c8c346376caa871e`; Owner direction: merge Handover Master and move **truly superseded** folders under `/superseded/`.

| Folder/surface | Decision | Proven reason |
|---|---|---|
| `coordination/Session_Oct07/Tab6_Dashboard_V2/` | **MOVE to `superseded/coordination/Session_Oct07/Tab6_Dashboard_V2/`** | Historical Dash V2 coordination workspace, superseded by the Owner's CoordinatorLandingpage #21 decision. Two original files relocated by blob SHA, old-path redirect retained; no native workflow imports observed in Common's current source audit |
| `relay/CONTINUITY/TEMPLATES/` | **RETAIN** | HANDOVER_TECHNICAL_V2 remains a Stage2-after-freeze native template; moving risks blind privacy/legacy provenance |
| `skills/two-pass-prompt-generator/` | **RETAIN** | Standalone live schema+validator and references in v3/v3.1 and other source material |
| `skills/three-pass-prompt-generator/` | **RETAIN** | Native five-prompt schema+validator, referenced by older integrations and generator contracts |
| `skills/engineering-pr-delivery-v3.5/` | **RETAIN, VERSION-PINNED** | Historical v3.5 scripts, handover and tests require original paths; v3.6 is independent, but a newer version is not proof of full decommissioning |
| `skills/engineering-pr-delivery-v3.6/` | **RETAIN** | Active separate lifecycle and native pass generators; explicit source and Owner scopes |
| `skills/buddy-runner-v1-6/` | **RETAIN** | v3.6 currently pins BuddyRunner v1.6 |
| `skills/buddy-runner-v1-7/` | **RETAIN, OPT-IN** | Separate supported successor-phase contract, not drop-in substitution |
| `skills/relay-onboarding-rwi/` | **RETAIN** | WP5 source report/manifest/validator are merged into main; other workpacks still separate drafts |
| Other engineering delivery version folders | **HOLD / NOT AUDITED FOR RELOCATION** | Common AGENTS.md marks v2/v3.1/v3.2 governance-critical and current CI references versions; never bulk-move by name |

**Acceptance boundary:** Only Dash V2 coordination records are eligible for this scope-limited physical move. Archive location does not become a runtime execution path. Preserving old Git blob identity is not Owner semantic acceptance. Existing Dash V2 issue text/PRs remain historical unmodified GitHub records.
