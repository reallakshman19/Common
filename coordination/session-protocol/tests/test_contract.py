"""Offline conformance: no real provider, identity, publication or acceptance claims."""
import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("casp_v1", ROOT / "tools" / "casp.py")
casp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(casp)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.fixture = casp.load(ROOT / "examples" / "exchange.json")
        self.session = copy.deepcopy(self.fixture["sessions"][0])
        self.request, self.response = copy.deepcopy(self.fixture["exchanges"][0])

    def rejected(self, function, *args):
        with self.assertRaises((casp.ContractError, ValueError)):
            function(*args)

    def test_all_four_sessions_two_providers_of_same_kind_two_projects(self):
        sessions = self.fixture["sessions"]
        self.assertEqual(4, len({s["session_id"] for s in sessions}))
        self.assertEqual(2, sum(s["provider"]["kind"] == "claude" for s in sessions))
        self.assertEqual(2, len({s["bindings"][0]["target"]["project_id"] for s in sessions}))
        for s, (request, response) in zip(sessions, self.fixture["exchanges"]):
            casp.validate_message(request, s)
            casp.validate_message(response, s)
            casp.correlate(request, response)

    def test_unknown_provider_supported(self):
        self.session["provider"]["kind"] = "new-vendor"
        casp.validate_session(self.session)

    def test_multiple_projects_in_one_session_need_explicit_binding(self):
        b = copy.deepcopy(self.fixture["sessions"][2]["bindings"][0])
        b["target"]["session_id"] = self.session["session_id"]
        self.session["bindings"].append(b)
        casp.validate_session(self.session)
        request = copy.deepcopy(self.fixture["exchanges"][2][0])
        request["target"] = b["target"]
        casp.validate_message(request, self.session)
        self.rejected(casp.validate_message, self.request, self.fixture["sessions"][2])

    def test_every_target_dimension_is_checked(self):
        for key, value in self.request["target"].items():
            with self.subTest(key=key):
                changed = copy.deepcopy(self.request)
                changed["target"][key] = value + 1 if type(value) is int else "different" if key != "expected_label_sha" else "b" * 64
                self.rejected(casp.validate_message, changed, self.session)

    def test_stale_revision_and_held_and_retired(self):
        self.session["revision"] = 2
        self.rejected(casp.validate_message, self.request, self.session)
        self.session["revision"] = 1
        for state in ["REGISTERED", "HOLD", "RETIRED"]:
            self.session["lifecycle"] = state
            self.rejected(casp.validate_message, self.request, self.session)
        self.request["action"] = "PAUSE_WORK"
        self.session["lifecycle"] = "HOLD"
        casp.validate_message(self.request, self.session)
        self.session["lifecycle"] = "RETIRED"
        self.rejected(casp.validate_message, self.request, self.session)

    def test_wrong_repository_and_mailbox_and_sender(self):
        for field in ["repository", "mailbox"]:
            changed = copy.deepcopy(self.request)
            changed[field] = self.fixture["exchanges"][2][0][field]
            self.rejected(casp.validate_message, changed, self.session)
        self.response["sender_id"] = "other-agent"
        self.rejected(casp.validate_message, self.response, self.session)

    def test_disallowed_action_and_decision_shape(self):
        self.request["action"] = "RESUME_WORK"
        self.rejected(casp.validate_message, self.request, self.session)
        self.request["action"] = "DECISION_RESOLVE"
        self.rejected(casp.validate_message, self.request)
        self.request["payload"]["decision"] = {"card_id": "card-example", "outcome": "DEFERRED"}
        casp.validate_message(self.request)
        self.request["action"] = "DIRECTIVE"
        self.rejected(casp.validate_message, self.request)

    def test_reply_correlation_all_fields(self):
        for field in ["request_id", "reply_to", "request_digest", "target", "repository", "mailbox", "expected_revision", "action"]:
            changed = copy.deepcopy(self.response)
            changed[field] = ("b" * 64 if field == "request_digest" else
                              2 if field == "expected_revision" else
                              "RECON_MODE" if field == "action" else
                              self.fixture["exchanges"][2][1][field])
            self.rejected(casp.correlate, self.request, changed)

    def test_identical_replay_and_conflicting_ids(self):
        self.assertEqual(1, casp.check_history([self.request, self.request]))
        changed = copy.deepcopy(self.request)
        changed["payload"]["text"] += " edited"
        self.rejected(casp.check_history, [self.request, changed])
        changed["message_id"] = self.response["message_id"]
        self.rejected(casp.check_history, [self.request, changed])

    def test_same_request_uuid_in_different_project_does_not_collide(self):
        other = copy.deepcopy(self.fixture["exchanges"][2][0])
        other["request_id"] = self.request["request_id"]
        self.assertEqual(2, casp.check_history([self.request, other]))

    def test_edited_instruction_invalidates_prior_correlation(self):
        self.request["payload"]["text"] += " changed"
        self.rejected(casp.correlate, self.request, self.response)

    def test_unknown_fields_and_versions_fail(self):
        for key, value in [("progress_percent", 100), ("protocol_version", "2.0.0"), ("action", "EXEC_SHELL")]:
            changed = copy.deepcopy(self.request)
            changed[key] = value
            self.rejected(casp.validate_message, changed)

    def test_json_canonical_vector(self):
        self.assertEqual(b'{"a":"\xc3\xa9","z":1}', casp.canonical({"z": 1, "a": "é"}))
        self.assertEqual(casp.digest({"z": 1, "a": "é"}), casp.digest(casp.loads('{"a":"é", "z":1}')))
        for text in ['{"a":1,"a":2}', '{"n":1.0}', '{"n":NaN}', '{"n":9007199254740992}', '"\\ud800"']:
            self.rejected(casp.loads, text)

    def test_null_unknown_basis_and_notrun_are_retained(self):
        self.assertIsNone(self.response["basis"]["candidate"])
        self.response["evidence"] = [{"criterion": "live-delivery", "outcome": "NOT_RUN", "basis": self.response["basis"], "proof_ref": None}]
        casp.validate_message(self.response)
        self.assertEqual("NOT_RUN", self.response["evidence"][0]["outcome"])

    def test_expiry_invalid_time_and_future_request(self):
        now = datetime(2026, 10, 13, 1, tzinfo=timezone.utc)
        casp.request_allowed_now(self.request, now)
        self.request["expires_at"] = "2026-10-13T00:10:00Z"
        self.rejected(casp.request_allowed_now, self.request, now)
        self.request["expires_at"] = "2026-02-30T01:00:00Z"
        self.rejected(casp.validate_message, self.request)
        self.request["expires_at"] = None
        self.rejected(casp.request_allowed_now, self.request, datetime(2026, 1, 1, tzinfo=timezone.utc))

    def test_comment_extract_roundtrip_and_multiple_blocks(self):
        rendered = casp.render(self.request)
        self.assertEqual(self.request, casp.extract(rendered))
        self.assertEqual(self.request, casp.extract(rendered.replace("\n", "\r\n")))
        self.rejected(casp.extract, rendered + rendered)
        self.rejected(casp.extract, "FOR LA: no envelope")

    def test_template_is_not_a_live_registration(self):
        self.rejected(casp.validate_session, casp.load(ROOT / "templates" / "session.json"))

    def test_duplicate_binding_and_readonly_write_paths(self):
        self.session["bindings"].append(copy.deepcopy(self.session["bindings"][0]))
        self.rejected(casp.validate_session, self.session)
        self.session["bindings"].pop()
        self.session["bindings"][0]["write_paths"] = ["src/**"]
        self.rejected(casp.validate_session, self.session)

    def test_source_schema_does_not_authenticate_claims(self):
        source = {"protocol_version": "1.0.0", "event_id": self.request["request_id"], "message_id": self.request["message_id"],
                  "repository": self.request["repository"], "issue_number": 1, "comment_id": "101", "actor": {"id": "102", "login": "fictional"},
                  "source_created_at": self.request["created_at"], "source_updated_at": self.request["created_at"], "observed_at": self.request["created_at"],
                  "source_body_sha256": "a" * 64, "envelope_sha256": casp.digest(self.request), "source_action": "READBACK",
                  "observation_method": "MANUAL_PROVIDER_READ", "observation_proof_ref": "https://example.invalid/fictional"}
        casp.schema_check(source, "source-observation.schema.json")
        source["authenticated_owner"] = True
        self.rejected(casp.schema_check, source, "source-observation.schema.json")

    def test_cli_new_request_reply_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            session = folder / "session.json"
            text = folder / "text.txt"
            request, reply = folder / "request.json", folder / "reply.json"
            session.write_text(casp.canonical(self.session).decode(), encoding="utf-8")
            text.write_text("Plan: report only. Evidence: NOT_RUN. LOG: offline.", encoding="utf-8")
            cmd = [sys.executable, str(ROOT / "tools" / "casp.py"), "make-request", str(session), "--binding", "binding-1", "--sender-id", "owner-example", "--text-file", str(text), "--authority-ref", "https://example.invalid/authority", "--output", str(request)]
            self.assertEqual(0, subprocess.run(cmd, capture_output=True).returncode)
            original = request.read_bytes()
            self.assertEqual(2, subprocess.run(cmd, capture_output=True).returncode)
            self.assertEqual(original, request.read_bytes())
            check = [sys.executable, str(ROOT / "tools" / "casp.py"), "check-request", str(request)]
            self.assertEqual(2, subprocess.run(check, capture_output=True).returncode)
            self.assertEqual(0, subprocess.run(check + ["--session", str(session)], capture_output=True).returncode)
            cmd = [sys.executable, str(ROOT / "tools" / "casp.py"), "make-reply", str(request), "--sender-id", "agent-1", "--text-file", str(text), "--output", str(reply)]
            self.assertEqual(0, subprocess.run(cmd, capture_output=True).returncode)
            casp.correlate(casp.load(request), casp.load(reply))


if __name__ == "__main__":
    unittest.main()
