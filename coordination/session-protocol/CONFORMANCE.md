# Conformance and readiness

## Implemented now

The first release is the **MANUAL interchange profile** plus an offline helper. It includes session/message/source-observation schemas, file creation/render/extraction, exact-target checks, request/reply correlation and a supplied-history conflict audit. It has no network client, daemon, private mailbox provisioning, persistent admission journal or automatic delivery.

The helper supports only the schema keywords used in this package: `$ref` (package-local), type, const, enum, required, properties, additionalProperties, items, array/string/integer limits, uniqueItems, pattern and UTC date-time. JSON Schema consumers may use the published 2020-12 schemas; semantic checks below remain additional requirements. A valid schema/envelope never proves authority, source authenticity, expiry at actual execution, or task acceptance.

## Offline checks

Run `python -m unittest discover -s coordination/session-protocol/tests -v`. The existing `coordination/tests` entrypoint includes this suite through `test_session_protocol.py`.

| Requirement | Check in `test_contract.py` |
|---|---|
| Separate same-provider sessions and projects | `test_all_four_sessions_two_providers_of_same_kind_two_projects`, `test_unknown_provider_supported` |
| Explicit per-project binding within one session | `test_multiple_projects_in_one_session_need_explicit_binding` |
| Every WP5 target dimension checked | `test_every_target_dimension_is_checked` |
| Revision, hold, retirement and priority stop shape | `test_stale_revision_and_held_and_retired` |
| Repository/mailbox/sender isolation | `test_wrong_repository_and_mailbox_and_sender` |
| Typed actions and decision shape | `test_disallowed_action_and_decision_shape` |
| Full request/reply correlation | `test_reply_correlation_all_fields` |
| Replay versus conflicting IDs | `test_identical_replay_and_conflicting_ids`, `test_same_request_uuid_in_different_project_does_not_collide` |
| Edited instruction cannot match old reply | `test_edited_instruction_invalidates_prior_correlation` |
| Unknown fields/actions/versions rejected | `test_unknown_fields_and_versions_fail` |
| Canonical bytes, duplicates, NaN, Unicode and integer bounds | `test_json_canonical_vector` |
| Unknown basis/NOT_RUN preserved | `test_null_unknown_basis_and_notrun_are_retained` |
| Expiry and invalid/future times | `test_expiry_invalid_time_and_future_request` |
| Single comment-envelope extraction | `test_comment_extract_roundtrip_and_multiple_blocks` |
| Placeholder registration cannot activate | `test_template_is_not_a_live_registration` |
| Duplicate binding/read-only write scope | `test_duplicate_binding_and_readonly_write_paths` |
| Source schema cannot grant authenticated role | `test_source_schema_does_not_authenticate_claims` |
| CLI roundtrip and existing file preservation | `test_cli_new_request_reply_does_not_overwrite` |

## Required before claiming automated intake/delivery

These are future integration acceptance tests, **NOT_RUN** by this package:

| Profile | Required evidence |
|---|---|
| INTAKE | Actual authenticated actor/repository/comment reads; shared-login human-authority negative; registered PR-vs-issue routing; edited/deleted source snapshots and UNKNOWN history gaps |
| INTAKE | Concurrent same-assignment requests, durable monotonic sequence/CAS, dropped notification replay, restart before/after admission, source-location conflict, no lost writes |
| INTAKE | Priority STOP during an active command, stale-worker fencing, preserved uncertain slot after expired lease, explicit authorized resume |
| INTAKE | Real 403/429/Retry-After response handling with restart-safe budgets; crash before/after comment publication and no duplicate write |
| DELIVERY | Real exact-account/conversation/draft/generation observations, one send, independently observed real receipt, no sender-manufactured receipt |
| DELIVERY | Crash before/after possible Send, unknown provider message ID, composer draft protection, generating chat, wrong route and stale UI; no blind resend |
| ALL LIVE | Two providers, two sessions of one provider and two projects; no cross-project authority leakage or unintended writes; privacy export audit |
| PROJECT REVIEW | Exact candidate/fixture/preparation evidence, independently reviewed task result, retained historical counters and unresolved failures |

Report each demonstrated profile separately. A fictional example, green CI, queue record or reported result cannot substitute for these tests. An unsupported automation profile does not prevent authorized manual use of the base contract.
