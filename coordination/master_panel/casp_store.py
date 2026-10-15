"""Private append-only CASP source/context recorder, not an authority registry.

Exact public-comment and supplied-context bytes stay in local SQLite only.
No network, publication, execution, acceptance, authentication or invalidation
authority is inferred. Scanner/read integration is a separate F07-B unit.
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone

from . import casp_validation as cv
from .models import SourceIdentity, SourceKind
from .storage import SourceConflict


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def bounded_text(value, name, optional=False):
    if optional and value is None:
        return None
    if not isinstance(value, str) or len(value.encode("utf-8")) > 65536:
        raise ValueError(name + " must be bounded UTF-8 text")
    return value


class CaspStore:
    """Caller owns the private DB and source capture; contexts remain supplied."""
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, timeout=10)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
          CREATE TABLE IF NOT EXISTS casp_versions(
            project_id TEXT NOT NULL, repo_id TEXT NOT NULL,
            entity_id TEXT NOT NULL, version INTEGER NOT NULL,
            observed_at TEXT NOT NULL, source_json TEXT NOT NULL,
            revision_id TEXT NOT NULL, provider_updated_at TEXT, body_sha256 TEXT NOT NULL,
            input_sha256 TEXT NOT NULL, raw_body TEXT NOT NULL,
            actor_json TEXT, descriptor_raw TEXT, request_raw TEXT,
            descriptor_sha256 TEXT, request_sha256 TEXT,
            disposition TEXT NOT NULL, action TEXT NOT NULL, ordered_capture INTEGER NOT NULL,
            claim_json TEXT NOT NULL, message_id TEXT,
            envelope_sha256 TEXT, request_id TEXT, assignment_id TEXT,
            kind TEXT,
            PRIMARY KEY(project_id,repo_id,entity_id,version));
          CREATE TABLE IF NOT EXISTS casp_observations(
            observation_id TEXT PRIMARY KEY, input_sha256 TEXT NOT NULL,
            project_id TEXT NOT NULL, repo_id TEXT NOT NULL,
            entity_id TEXT NOT NULL, version INTEGER NOT NULL,
            observed_at TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS casp_message_identity
            ON casp_versions(project_id,repo_id,message_id);
          CREATE INDEX IF NOT EXISTS casp_request_identity
            ON casp_versions(project_id,repo_id,assignment_id,request_id,kind);
        """)

    def close(self):
        self.conn.close()

    def record(self, observation_id, source, body, *, observed_at=None,
               actor=None, descriptor_raw=None, request_raw=None):
        if not isinstance(source, SourceIdentity) or source.kind != SourceKind.ISSUE_COMMENT:
            raise ValueError("exact comment source required")
        if not isinstance(observation_id, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", observation_id):
            raise ValueError("safe observation identity required")
        bounded_text(body, "body")
        bounded_text(descriptor_raw, "descriptor", optional=True)
        bounded_text(request_raw, "request", optional=True)
        if sha(body) != source.body_sha256:
            raise ValueError("observed raw-body fingerprint mismatch")
        if actor is not None and (not isinstance(actor, dict) or
                set(actor) != {"id", "login"} or
                not isinstance(actor["id"], str) or not re.fullmatch(r"[1-9][0-9]{0,19}", actor["id"]) or
                not isinstance(actor["login"], str) or
                not re.fullmatch(r"[A-Za-z0-9-]{1,64}", actor["login"])):
            raise ValueError("bounded provider actor observation required")
        observed_at = observed_at or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        cv.timestamp(observed_at)
        provider_time = None
        if source.updated_at_utc is not None:
            provider_time = datetime.fromisoformat(source.updated_at_utc.replace("Z", "+00:00"))
            if provider_time.tzinfo is None:
                raise ValueError("provider timestamp requires timezone")
        provider_stamp = provider_time.astimezone(timezone.utc).isoformat() if provider_time else None
        source_json = cv.canonical(source.public_dict()).decode()
        actor_json = cv.canonical(actor).decode() if actor is not None else None
        descriptor_sha = sha(descriptor_raw) if descriptor_raw is not None else None
        request_sha = sha(request_raw) if request_raw is not None else None
        for name, expected in cv.SCHEMA_SHA256.items():
            if hashlib.sha256((cv.ROOT / "casp_schemas" / name).read_bytes()).hexdigest() != expected:
                raise cv.ContractError("pinned schema digest mismatch")
        fingerprint = cv.digest(dict(source=source.public_dict(), actor=actor,
                                     descriptor_sha256=descriptor_sha,
                                     request_sha256=request_sha))
        # Retain only a safe invalid disposition: schema errors may contain
        # private field names/prose, so they are not exported or logged here.
        disposition, claim = "INVALID", {}
        try:
            # Wire/source identity survives a failing supplied correlation.
            # It cannot borrow matched-context status but must remain indexed
            # so a conflicting message cannot be forgotten after restart.
            claim = cv.inspect_comment(body, source)
            session = cv.loads(descriptor_raw) if descriptor_raw is not None else None
            request = cv.loads(request_raw) if request_raw is not None else None
            claim = cv.inspect_comment(body, source, session=session, request=request)
            claim["context_validation"] = "MATCHES_SUPPLIED_CONTEXT" if session is not None else "NOT_CONFIGURED"
            disposition = "STRUCTURAL_CLAIM_VALID"
        except (ValueError, TypeError, KeyError, IndexError):
            if claim:
                claim["context_validation"] = "INVALID"
        key = (source.project_id, source.repo_id, source.entity_id)
        with self.conn:
            # Acquire the write lock before reading identities: competing
            # processes cannot both allocate a source version from a stale row.
            self.conn.execute("BEGIN IMMEDIATE")
            prior = self.conn.execute("SELECT * FROM casp_observations WHERE observation_id=?",
                                      (observation_id,)).fetchone()
            if prior:
                if prior["input_sha256"] != fingerprint:
                    raise SourceConflict("observation identity reused with different input")
                return self._projection(key, prior["version"], replay=True)
            latest = self.conn.execute("""SELECT * FROM casp_versions
                WHERE project_id=? AND repo_id=? AND entity_id=? AND ordered_capture=1 ORDER BY version DESC LIMIT 1""", key).fetchone()
            last_capture = self.conn.execute("""SELECT * FROM casp_versions
                WHERE project_id=? AND repo_id=? AND entity_id=? ORDER BY version DESC LIMIT 1""", key).fetchone()
            if last_capture and last_capture["input_sha256"] == fingerprint:
                version = last_capture["version"]
                self._observation(observation_id, fingerprint, key, version, observed_at)
                return self._projection(key, version, replay=True)
            count = self.conn.execute("""SELECT max(version) FROM casp_versions
                WHERE project_id=? AND repo_id=? AND entity_id=?""", key).fetchone()[0]
            version = (count or 0) + 1
            ordered = int(provider_time is not None)
            if not ordered:
                disposition = "UNORDERED_SOURCE_REVISION"
            if latest and latest["provider_updated_at"] is not None:
                previous_time = datetime.fromisoformat(latest["provider_updated_at"].replace("Z", "+00:00"))
                if provider_time is None:
                    disposition, ordered = "UNORDERED_SOURCE_REVISION", 0
                elif provider_time < previous_time:
                    disposition, ordered = "STALE_SOURCE_REVISION", 0
            action = "NEW" if not latest else "EDIT" if latest["body_sha256"] != source.body_sha256 else "CONTEXT_OR_SOURCE_CHANGED"
            same_revision = self.conn.execute("""SELECT 1 FROM casp_versions
                WHERE project_id=? AND repo_id=? AND entity_id=?
                AND (revision_id=? OR (provider_updated_at IS NOT NULL AND provider_updated_at=?))
                AND body_sha256<>? LIMIT 1""",
                (*key, source.revision_id, provider_stamp, source.body_sha256)).fetchone()
            if same_revision and ordered:
                disposition = "SOURCE_REVISION_CONFLICT"
            if claim:
                conflict = self.conn.execute("""SELECT 1 FROM casp_versions
                    WHERE project_id=? AND repo_id=? AND message_id=? AND envelope_sha256<>? LIMIT 1""",
                    (*key[:2], claim["message_id"], claim["canonical_envelope_sha256"])).fetchone()
                if conflict and not same_revision and ordered:
                    disposition = "MESSAGE_ID_CONFLICT"
                if claim["kind"] == "REQUEST":
                    conflict = self.conn.execute("""SELECT 1 FROM casp_versions
                        WHERE project_id=? AND repo_id=? AND assignment_id=? AND request_id=?
                        AND kind='REQUEST' AND envelope_sha256<>? LIMIT 1""",
                        (*key[:2], claim["assignment_id"], claim["request_id"], claim["canonical_envelope_sha256"])).fetchone()
                    if conflict and disposition == "STRUCTURAL_CLAIM_VALID":
                        disposition = "REQUEST_KEY_CONFLICT"
            self.conn.execute("""INSERT INTO casp_versions VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (*key, version, observed_at, source_json, source.revision_id,
                 provider_stamp, source.body_sha256, fingerprint, body, actor_json, descriptor_raw, request_raw,
                 descriptor_sha, request_sha, disposition, action, ordered, cv.canonical(claim).decode(),
                 claim.get("message_id"), claim.get("canonical_envelope_sha256"),
                 claim.get("request_id"), claim.get("assignment_id"), claim.get("kind")))
            self._observation(observation_id, fingerprint, key, version, observed_at)
            return self._projection(key, version)

    def _observation(self, observation_id, fingerprint, key, version, at):
        self.conn.execute("INSERT INTO casp_observations VALUES (?,?,?,?,?,?,?)",
                          (observation_id, fingerprint, *key, version, at))

    def _projection(self, key, version, replay=False):
        row = self.conn.execute("""SELECT * FROM casp_versions
            WHERE project_id=? AND repo_id=? AND entity_id=? AND version=?""", (*key, version)).fetchone()
        if row is None:
            return None
        claim = json.loads(row["claim_json"])
        return dict(project_id=row["project_id"], repo_id=row["repo_id"],
                    entity_id=row["entity_id"], version=row["version"],
                    observed_at=row["observed_at"], replay=replay, action=row["action"],
                    source_body_sha256=row["body_sha256"],
                    descriptor_raw_sha256=row["descriptor_sha256"],
                    request_raw_sha256=row["request_sha256"],
                    disposition=row["disposition"], claim=claim,
                    source_ordering="OBSERVED_VERSION" if row["ordered_capture"] else "NON_CURRENT_CAPTURE",
                    provider_actor_observation=json.loads(row["actor_json"]) if row["actor_json"] else None,
                    authentication="UNKNOWN", registry_admission="NOT_CONFIGURED",
                    current_applicability="UNKNOWN", independent_acceptance="UNKNOWN",
                    invalidation_effect="NOT_APPLIED", liveness="UNKNOWN")

    def history(self, source, *, after=0, limit=100):
        if type(after) is not int or after < 0 or type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("bounded source history required")
        key = (source.project_id, source.repo_id, source.entity_id)
        rows = self.conn.execute("""SELECT version FROM casp_versions
            WHERE project_id=? AND repo_id=? AND entity_id=? AND version>? ORDER BY version LIMIT ?""", (*key, after, limit)).fetchall()
        return [self._projection(key, row["version"]) for row in rows]

    def latest(self, source):
        key = (source.project_id, source.repo_id, source.entity_id)
        row = self.conn.execute("""SELECT version FROM casp_versions
            WHERE project_id=? AND repo_id=? AND entity_id=? AND ordered_capture=1 ORDER BY version DESC LIMIT 1""", key).fetchone()
        return self._projection(key, row["version"]) if row else None
