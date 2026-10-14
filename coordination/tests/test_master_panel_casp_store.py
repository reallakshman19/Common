"""F07-A2 restart, conflict, atomicity and non-promotion counterexamples."""
import copy
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from coordination.master_panel import casp_validation as cv
from coordination.master_panel.casp_store import CaspStore
from coordination.master_panel.storage import SourceConflict
from coordination.tests.test_master_panel_casp_validation import context, observe


class CaspStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = str(Path(self.temp.name) / "private.sqlite")
        self.store = CaspStore(self.path)
        self.addCleanup(lambda: self.store.close())
        self.request, self.reply, self.session = context()

    def record(self, ident="capture-1", message=None, *, stamp="2026-10-14T05:00:00Z", prefix="A", **kwargs):
        message = self.reply if message is None else message
        body, source = observe(message, body=prefix + "\n```casp\n" + json.dumps(message) + "\n```\n")
        source = replace(source, revision_id=stamp, updated_at_utc=stamp)
        out = self.store.record(ident, source, body, actor={"id": "277598171", "login": "example"},
                                descriptor_raw=json.dumps(self.session), request_raw=json.dumps(self.request), **kwargs)
        return out, source, body

    def test_a_b_a_exact_outer_edits_retain_three_versions(self):
        a, source, _ = self.record()
        b, _, _ = self.record("capture-2", stamp="2026-10-14T05:01:00Z", prefix="B")
        c, _, _ = self.record("capture-3", stamp="2026-10-14T05:02:00Z")
        self.assertEqual([x["version"] for x in self.store.history(source)], [1, 2, 3])
        self.assertEqual(a["source_body_sha256"], c["source_body_sha256"])
        self.assertNotEqual(a["source_body_sha256"], b["source_body_sha256"])
        self.assertEqual(a["claim"]["canonical_envelope_sha256"], b["claim"]["canonical_envelope_sha256"])
        self.assertEqual(c["disposition"], "STRUCTURAL_CLAIM_VALID")

    def test_replay_survives_restart_and_does_not_rewrite_versions(self):
        first, source, body = self.record()
        self.store.close(); self.store = CaspStore(self.path)
        replay, _, _ = self.record()
        later, _, _ = self.record("capture-2")
        self.assertTrue(replay["replay"]); self.assertTrue(later["replay"])
        self.assertEqual(len(self.store.history(source)), 1)
        row = self.store.conn.execute("SELECT * FROM casp_versions").fetchone()
        self.assertEqual(row["raw_body"], body)
        self.assertEqual(row["descriptor_raw"], json.dumps(self.session))
        self.assertEqual(row["request_raw"], json.dumps(self.request))

    def test_observation_identity_collision_rolls_back(self):
        _, source, _ = self.record()
        with self.assertRaises(SourceConflict):
            self.record(prefix="different", stamp="2026-10-14T05:01:00Z")
        self.assertEqual(len(self.store.history(source)), 1)

    def test_changed_canonical_message_id_conflict_survives_restart_and_restore(self):
        _, source, _ = self.record()
        changed = copy.deepcopy(self.reply); changed["payload"]["text"] = "edited"
        out, _, _ = self.record("capture-2", changed, stamp="2026-10-14T05:01:00Z")
        self.assertEqual(out["disposition"], "MESSAGE_ID_CONFLICT")
        self.store.close(); self.store = CaspStore(self.path)
        restored, _, _ = self.record("capture-3", stamp="2026-10-14T05:02:00Z")
        self.assertEqual(restored["disposition"], "MESSAGE_ID_CONFLICT")
        self.assertEqual(len(self.store.history(source)), 3)

    def test_request_key_conflict_is_durable(self):
        # Requests have no request-response correlation context.
        body, source = observe(self.request)
        source = replace(source, updated_at_utc="2026-10-14T05:00:00Z")
        self.store.record("request-1", source, body, descriptor_raw=json.dumps(self.session))
        changed = copy.deepcopy(self.request)
        changed.update(message_id="00000000-0000-4000-8000-000000000099")
        changed["payload"]["text"] = "changed request"
        body2, source2 = observe(changed)
        source2 = replace(source2, entity_id="223", comment_id="223", revision_id="next", updated_at_utc="2026-10-14T05:01:00Z")
        out = self.store.record("request-2", source2, body2, descriptor_raw=json.dumps(self.session))
        self.assertEqual(out["disposition"], "REQUEST_KEY_CONFLICT")
        self.store.close(); self.store = CaspStore(self.path)
        self.assertEqual(self.store.latest(source2)["disposition"], "REQUEST_KEY_CONFLICT")

    def test_same_provider_timestamp_different_body_is_conflict(self):
        _, source, _ = self.record()
        body, changed = observe(self.reply, body="outer edit\n```casp\n" + json.dumps(self.reply) + "\n```\n")
        changed = replace(changed, revision_id="distinct-local-id", updated_at_utc=source.updated_at_utc)
        out = self.store.record("capture-2", changed, body)
        self.assertEqual(out["disposition"], "SOURCE_REVISION_CONFLICT")
        equivalent = replace(changed, revision_id="other-local-id", updated_at_utc="2026-10-14T06:00:00+01:00")
        out = self.store.record("capture-3", equivalent, body)
        self.assertEqual(out["disposition"], "SOURCE_REVISION_CONFLICT")

    def test_exact_raw_newline_hash_separate_and_borrowed_hash_rejected(self):
        _, source, body = self.record()
        raw = body.replace("\n", "\r\n")
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.store.record("capture-bad", source, raw)
        _, changed = observe(self.reply, body=raw)
        changed = replace(changed, revision_id="2026-10-14T05:01:00Z")
        out = self.store.record("capture-2", changed, raw)
        self.assertNotEqual(out["source_body_sha256"], source.body_sha256)
        self.assertEqual(out["claim"]["canonical_envelope_sha256"], cv.digest(self.reply))

    def test_invalid_edit_stays_latest_no_fallback_to_valid_claim(self):
        _, source, _ = self.record()
        bad = copy.deepcopy(self.reply); bad["request_digest"] = "0" * 64
        out, _, _ = self.record("capture-2", bad, stamp="2026-10-14T05:01:00Z")
        self.assertEqual(out["disposition"], "MESSAGE_ID_CONFLICT")
        self.assertEqual(out["claim"]["context_validation"], "INVALID")
        self.record()  # old exact capture replay cannot move latest backwards
        self.assertEqual(self.store.latest(source)["disposition"], "MESSAGE_ID_CONFLICT")

    def test_wrong_scope_and_context_are_retained_as_invalid(self):
        for field in ("mailbox", "repository", "project", "revision", "generation"):
            msg = copy.deepcopy(self.reply)
            if field == "mailbox": msg["mailbox"]["issue_number"] = 374
            elif field == "repository": msg["repository"]["id"] = "1363905693"
            elif field == "project": msg["target"]["project_id"] = "aa3"
            elif field == "revision": msg["expected_revision"] = 2
            else: msg["target"]["binding_generation"] = 2
            out, _, _ = self.record("capture-" + field, msg, stamp="2026-10-14T05:01:00Z")
            self.assertIn(out["disposition"], ("INVALID", "SOURCE_REVISION_CONFLICT"))
            self.assertNotEqual(out["claim"].get("request_correlation"), "MATCHES_SUPPLIED_REQUEST")

    def test_review_and_invalidation_are_claims_not_authority(self):
        for kind, status in (("REVIEW", "ACCEPTED"), ("INVALIDATION", "INVALIDATED")):
            msg = copy.deepcopy(self.reply)
            msg.update(kind=kind, status=status, message_id="00000000-0000-4000-8000-0000000000" + ("04" if kind == "REVIEW" else "05"))
            out, _, _ = self.record("capture-" + kind, msg, stamp="2026-10-14T05:01:00Z")
            self.assertEqual(out["claim"]["reported_status"], status)
            for field in ("authentication", "current_applicability", "independent_acceptance", "liveness"):
                self.assertEqual(out[field], "UNKNOWN")
            self.assertEqual(out["invalidation_effect"], "NOT_APPLIED")
            self.assertEqual(out["registry_admission"], "NOT_CONFIGURED")
            self.assertNotIn("synthetic private prose", json.dumps(out))

    def test_interrupted_record_rolls_back_and_retry_is_safe(self):
        with patch.object(self.store, "_observation", side_effect=RuntimeError("interrupted")):
            with self.assertRaises(RuntimeError): self.record()
        self.assertEqual(self.store.conn.execute("SELECT count(*) FROM casp_versions").fetchone()[0], 0)
        self.assertEqual(self.store.conn.execute("SELECT count(*) FROM casp_observations").fetchone()[0], 0)
        out, _, _ = self.record(); self.assertEqual(out["version"], 1)

    def test_integrity_failure_and_input_bounds_write_nothing(self):
        with patch.object(cv, "SCHEMA_SHA256", dict(cv.SCHEMA_SHA256, **{"message.schema.json": "0" * 64})):
            with self.assertRaisesRegex(ValueError, "digest mismatch"): self.record()
        body, source = observe(self.reply)
        for kwargs in ({"actor": {"id": "1", "login": "x", "authenticated": True}},
                       {"descriptor_raw": "x" * 65537}, {"observed_at": "not-time"}):
            with self.assertRaises(ValueError): self.store.record("bad", source, body, **kwargs)
        self.assertEqual(self.store.conn.execute("SELECT count(*) FROM casp_versions").fetchone()[0], 0)

    def test_history_is_bounded_and_latest_is_not_page_selection(self):
        _, source, _ = self.record()
        self.record("capture-2", stamp="2026-10-14T05:01:00Z", prefix="B")
        self.record("capture-3", stamp="2026-10-14T05:02:00Z", prefix="C")
        self.assertEqual([x["version"] for x in self.store.history(source, limit=2)], [1, 2])
        self.assertEqual([x["version"] for x in self.store.history(source, after=2, limit=2)], [3])
        self.assertEqual(self.store.latest(source)["version"], 3)
        for kwargs in ({"limit": 201}, {"limit": True}, {"after": -1}, {"after": True}):
            with self.assertRaises(ValueError): self.store.history(source, **kwargs)

    def test_same_numeric_comment_and_message_id_other_repository_is_isolated(self):
        _, first, _ = self.record()
        other = copy.deepcopy(self.reply)
        other["repository"].update(id="1363905693", name="reallakshman19/AA3")
        other["mailbox"]["repository"] = copy.deepcopy(other["repository"])
        other["target"]["project_id"] = "aa3"
        body, source = observe(other)
        source = replace(source, project_id="aa3", repo_id="1363905693", repo_full_name="reallakshman19/AA3", updated_at_utc="2026-10-14T05:00:00Z")
        out = self.store.record("other-source", source, body)
        self.assertEqual(out["disposition"], "STRUCTURAL_CLAIM_VALID")
        self.assertEqual(len(self.store.history(first)), 1)
        self.assertEqual(len(self.store.history(source)), 1)

    def test_correlation_invalid_identity_remains_conflicting_after_restart_restore(self):
        _, source, _ = self.record()
        bad = copy.deepcopy(self.reply); bad["request_digest"] = "0" * 64
        self.record("capture-2", bad, stamp="2026-10-14T05:01:00Z")
        self.store.close(); self.store = CaspStore(self.path)
        out, _, _ = self.record("capture-3", stamp="2026-10-14T05:02:00Z")
        self.assertEqual(out["disposition"], "MESSAGE_ID_CONFLICT")
        self.assertEqual(self.store.latest(source)["disposition"], "MESSAGE_ID_CONFLICT")

    def test_old_revision_and_reformatted_context_do_not_replace_newer_invalid_source(self):
        _, source, body = self.record()
        bad = copy.deepcopy(self.reply); bad["created_at"] = "not-time"
        self.record("capture-2", bad, stamp="2026-10-14T05:02:00Z")
        older, _, _ = self.record("capture-3", stamp="2026-10-14T05:01:00Z", prefix="unseen old")
        self.assertEqual(older["disposition"], "STALE_SOURCE_REVISION")
        out = self.store.record("capture-4", source, body, descriptor_raw=json.dumps(self.session, indent=2), request_raw=json.dumps(self.request))
        self.assertEqual(out["disposition"], "STALE_SOURCE_REVISION")
        self.assertEqual(self.store.latest(source)["version"], 2)
        self.assertEqual(self.store.latest(source)["disposition"], "INVALID")

    def test_unknown_provider_time_cannot_replace_known_ordered_source(self):
        _, source, body = self.record()
        unknown = replace(source, revision_id="unknown-time", updated_at_utc=None)
        out = self.store.record("capture-2", unknown, body)
        self.assertEqual(out["disposition"], "UNORDERED_SOURCE_REVISION")
        self.assertEqual(self.store.latest(source)["version"], 1)

    def test_provider_actor_id_is_positive_bounded_ascii_decimal(self):
        body, source = observe(self.reply)
        for ident in ("0", "1" * 21, "١٢٣", "-1", "01"):
            with self.assertRaises(ValueError):
                self.store.record("bad-actor", source, body, actor={"id": ident, "login": "example"})
        self.assertEqual(self.store.conn.execute("SELECT count(*) FROM casp_versions").fetchone()[0], 0)

    def test_first_unknown_timestamp_is_non_current_and_replays_without_duplicates(self):
        body, source = observe(self.reply)
        first = self.store.record("capture-unknown", source, body)
        self.assertEqual(first["disposition"], "UNORDERED_SOURCE_REVISION")
        self.assertEqual(first["source_ordering"], "NON_CURRENT_CAPTURE")
        self.assertIsNone(self.store.latest(source))
        self.store.close(); self.store = CaspStore(self.path)
        replay = self.store.record("capture-unknown-again", source, body)
        self.assertTrue(replay["replay"])
        self.assertEqual(len(self.store.history(source)), 1)
        self.assertIsNone(self.store.latest(source))


if __name__ == "__main__": unittest.main()
