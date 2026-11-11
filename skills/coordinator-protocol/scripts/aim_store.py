"""Local, append-only aim registry. Structural checks never infer semantic truth.

The ``recorded`` namespace is archival. ``demo`` and isolated ``work:<stream>``
namespaces can activate revisions only through an explicitly supplied decision.
Authority, verification and delivery fields record runner-supplied judgements;
the store does not authenticate an Owner, inspect artifacts or contact agents.
"""
from __future__ import annotations

import copy
import json
import re
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


KINDS = ("aim", "task", "evidence", "assessment", "proposal", "decision",
         "handover", "roi", "drift", "control", "adoption", "review",
         "source", "review_input", "report")
THRESHOLDS = (5, 10, 15, 19)
NAMESPACES = ("recorded", "demo")
WORK_NAMESPACE = re.compile(r"work:[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
EVENT_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS {name} (
        sequence INTEGER PRIMARY KEY AUTOINCREMENT,
        namespace TEXT NOT NULL CHECK(namespace IN ('recorded','demo') OR
            (substr(namespace,1,5)='work:' AND length(namespace) BETWEEN 6 AND 69
             AND substr(namespace,6,1) GLOB '[A-Za-z0-9]'
             AND substr(namespace,6) NOT GLOB '*[^A-Za-z0-9._-]*')),
        event_id TEXT NOT NULL, kind TEXT NOT NULL, record_id TEXT NOT NULL,
        payload TEXT NOT NULL, created_at TEXT NOT NULL,
        UNIQUE(namespace, event_id), UNIQUE(namespace, kind, record_id)
    )
"""


class InvariantError(ValueError):
    """The submitted record does not satisfy the recorded contract."""


class Store:
    def __init__(self, path, read_only=False):
        self.path = str(path)
        if type(read_only) is not bool:
            raise InvariantError("read_only must be boolean")
        self.read_only = read_only
        if read_only:
            if self.path == ":memory:" or not Path(self.path).is_file():
                raise FileNotFoundError("read-only store requires an existing database file")
            with Path(self.path).open("rb") as database_file:
                header = database_file.read(20)
            if len(header) == 20 and header[:16] == b"SQLite format 3\x00" and header[18:20] == b"\x02\x02":
                # SQLite mode=ro may create WAL/SHM files for a legacy WAL DB.
                # Refuse that side effect rather than use immutable=1, which
                # would ignore pending WAL commits and concurrent read locks.
                raise InvariantError("read-only access requires a rollback-journal registry; explicitly open this legacy WAL registry writable once to checkpoint and migrate")
            database = Path(self.path).resolve().as_uri() + "?mode=ro"
        elif self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            database = self.path
        else:
            database = self.path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(database, uri=read_only, isolation_level=None,
                                   check_same_thread=False, timeout=10)
        self._db.row_factory = sqlite3.Row
        try:
            if read_only:
                self._db.execute("PRAGMA query_only=ON")  # Connection setting; no database mutation.
                self._db.execute("SELECT sequence FROM events LIMIT 0")
            else:
                # Rollback journaling supports consistent mode=ro readers without
                # creating WAL/SHM sidecars in a coordinator's read-only cycle.
                self._db.execute("PRAGMA journal_mode=DELETE")
                self._install_schema()
        except BaseException:
            self._db.close()
            raise

    def _install_schema(self):
        with self._transaction():
            existing = self._db.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='events'").fetchone()
            if existing and "work:" not in existing[0]:
                # A schema migration copies every immutable row and sequence;
                # it neither rewrites nor drops any logical event.
                self._db.execute(EVENT_TABLE_SQL.format(name="events_v328"))
                self._db.execute("INSERT INTO events_v328 SELECT * FROM events ORDER BY sequence")
                old_count = self._db.execute("SELECT count(*) FROM events").fetchone()[0]
                new_count = self._db.execute("SELECT count(*) FROM events_v328").fetchone()[0]
                if old_count != new_count:
                    raise InvariantError("namespace migration did not preserve all events")
                self._db.execute("DROP TABLE events")
                self._db.execute("ALTER TABLE events_v328 RENAME TO events")
            else:
                self._db.execute(EVENT_TABLE_SQL.format(name="events"))
            self._db.execute("CREATE INDEX IF NOT EXISTS events_scope ON events(namespace,kind,sequence)")
            self._db.execute("""CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT,'events are immutable'); END""")
            self._db.execute("""CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT,'events are append-only'); END""")
            self._db.execute("PRAGMA user_version=2")

    def close(self):
        with self._lock:
            self._db.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @contextmanager
    def _transaction(self):
        with self._lock:
            if self.read_only:
                raise InvariantError("read-only store cannot append or decide")
            self._db.execute("BEGIN IMMEDIATE")
            try:
                yield
                self._db.execute("COMMIT")
            except BaseException:
                self._db.execute("ROLLBACK")
                raise

    @contextmanager
    def _read_transaction(self):
        with self._lock:
            own_transaction = not self._db.in_transaction
            if own_transaction:
                self._db.execute("BEGIN")
            try:
                yield
                if own_transaction:
                    self._db.execute("COMMIT")
            except BaseException:
                if own_transaction:
                    self._db.execute("ROLLBACK")
                raise

    @staticmethod
    def _namespace(namespace):
        if not isinstance(namespace, str) or (namespace not in NAMESPACES and not WORK_NAMESPACE.fullmatch(namespace)):
            raise InvariantError("namespace must be recorded, demo or work:<safe stream ID of 1..64 characters>")

    @staticmethod
    def _recipient(value):
        if not isinstance(value, str) or not value.strip():
            raise InvariantError("recipient must be a full chat URL")
        parsed = urlparse(value)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.path in ("", "/"):
            raise InvariantError("recipient must be a full chat URL")
        return value

    @staticmethod
    def _text(record, key):
        value = record.get(key)
        if not isinstance(value, str) or not value.strip():
            raise InvariantError(f"{key} must be a nonempty string")
        return value

    @staticmethod
    def _ids(record, key, nonempty=True):
        value = record.get(key)
        if not isinstance(value, list) or (nonempty and not value):
            raise InvariantError(f"{key} must be a {'nonempty ' if nonempty else ''}list")
        if any(not isinstance(x, str) or not x.strip() for x in value):
            raise InvariantError(f"{key} must contain string IDs")
        if len(set(value)) != len(value):
            raise InvariantError(f"{key} contains duplicate IDs")
        return set(value)

    @staticmethod
    def _json(record):
        return json.dumps(record, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False, allow_nan=False)

    def _get(self, kind, record_id, namespace):
        row = self._db.execute(
            "SELECT payload FROM events WHERE namespace=? AND kind=? AND record_id=?",
            (namespace, kind, record_id)).fetchone()
        return json.loads(row[0]) if row else None

    def _require(self, kind, record_id, namespace):
        found = self._get(kind, record_id, namespace)
        if found is None:
            raise InvariantError(f"unknown {kind} {record_id!r} in {namespace}")
        return found

    def _list(self, kind, namespace):
        return [json.loads(r[0]) for r in self._db.execute(
            "SELECT payload FROM events WHERE namespace=? AND kind=? ORDER BY sequence",
            (namespace, kind))]

    def _insert(self, kind, record, namespace, event_id=None):
        payload = self._json(record)
        event_id = event_id or f"{kind}:{record['id']}"
        row = self._db.execute(
            "SELECT kind,payload FROM events WHERE namespace=? AND event_id=?",
            (namespace, event_id)).fetchone()
        if row:
            if row["kind"] != kind or row["payload"] != payload:
                raise InvariantError("event ID already exists with a different payload")
            return json.loads(row["payload"])
        existing = self._get(kind, record["id"], namespace)
        if existing is not None:
            if self._json(existing) != payload:
                raise InvariantError("record ID already exists with a different payload")
            raise InvariantError("record already exists under a different event ID; retry the original event")
        self._db.execute(
            "INSERT INTO events(namespace,event_id,kind,record_id,payload,created_at) VALUES(?,?,?,?,?,?)",
            (namespace, event_id, kind, record["id"], payload,
             datetime.now(timezone.utc).isoformat()))
        return copy.deepcopy(record)

    def _normalize(self, kind, record, namespace):
        if not isinstance(record, dict):
            raise InvariantError("record must be a dictionary")
        result = json.loads(self._json(record))
        self._text(result, "id")
        if kind == "task":
            existing = self._get(kind, result["id"], namespace)
            current = self._current_aims(namespace)
            if current["main"] is None:
                raise InvariantError("new task requires an active main aim")
            result.setdefault("main_aim_id", (existing or {}).get("main_aim_id") or
                              (current["main"] or {}).get("id"))
            result.setdefault("status", "declared")
        if kind == "evidence":
            result.setdefault("supersedes", [])
        return result

    def append(self, kind, record, namespace="demo", event_id=None):
        """Append one immutable record; protected kinds receive normal checks.

        Decisions in demo/work must use decide(), so arbitrary ROI/control records
        cannot activate aims. A matching event/record ID is an idempotent retry.
        """
        self._namespace(namespace)
        if kind not in KINDS:
            raise InvariantError(f"unknown kind {kind!r}")
        if kind == "decision" and namespace != "recorded":
            raise InvariantError("demo/work decisions must use decide()")
        with self._transaction():
            candidate = self._normalize(kind, record, namespace)
            existing = self._get(kind, candidate["id"], namespace)
            event = None
            if event_id:
                event = self._db.execute(
                    "SELECT kind,payload FROM events WHERE namespace=? AND event_id=?",
                    (namespace, event_id)).fetchone()
            if event and (event["kind"] != kind or event["payload"] != self._json(candidate)):
                raise InvariantError("event ID already exists with a different payload")
            if existing is not None:
                return self._insert(kind, candidate, namespace, event_id)
            self._validate(kind, candidate, namespace)
            return self._insert(kind, candidate, namespace, event_id)

    def list(self, kind, namespace="demo"):
        self._namespace(namespace)
        if kind not in KINDS:
            raise InvariantError(f"unknown kind {kind!r}")
        with self._lock:
            return self._list(kind, namespace)

    def events(self, namespace="demo"):
        self._namespace(namespace)
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM events WHERE namespace=? ORDER BY sequence", (namespace,)).fetchall()
            return [{"sequence": r["sequence"], "namespace": r["namespace"],
                     "event_id": r["event_id"], "kind": r["kind"],
                     "record": json.loads(r["payload"]), "created_at": r["created_at"]}
                    for r in rows]

    def snapshot(self, namespace="demo"):
        self._namespace(namespace)
        with self._read_transaction():
            return {kind: self._list(kind, namespace) for kind in KINDS}

    def _current_aims(self, namespace):
        result = {"main": None, "task": None}
        rows = self._db.execute(
            "SELECT kind,payload FROM events WHERE namespace=? AND kind IN ('aim','decision') ORDER BY sequence",
            (namespace,))
        for row in rows:
            record = json.loads(row["payload"])
            if row["kind"] == "aim" and record.get("active") is True:
                result[record["aim_type"]] = record
            elif (row["kind"] == "decision" and namespace != "recorded" and
                  record.get("activation_committed") is True):
                for aim_id in record["activated_aim_ids"]:
                    aim = self._require("aim", aim_id, namespace)
                    result[aim["aim_type"]] = aim
        return result

    def current_aims(self, namespace="demo"):
        self._namespace(namespace)
        with self._lock:
            return self._current_aims(namespace)

    def _criteria(self, aim):
        criteria = aim.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise InvariantError("aim criteria must be a nonempty list of {id,text}")
        ids = []
        for criterion in criteria:
            if not isinstance(criterion, dict):
                raise InvariantError("each aim criterion must contain id and text")
            ids.append(self._text(criterion, "id"))
            self._text(criterion, "text")
        if len(ids) != len(set(ids)):
            raise InvariantError("aim criterion IDs must be unique")
        return set(ids)

    def _check_aim(self, record):
        if record.get("aim_type") not in ("main", "task"):
            raise InvariantError("aim_type must be main or task")
        if len(re.findall(r"\S+", self._text(record, "label"))) >= 20:
            raise InvariantError("aim label must contain fewer than 20 words")
        self._criteria(record)
        self._text(record, "authority_ref")
        excluded = record.get("excluded_scope")
        if not isinstance(excluded, list) or any(not isinstance(x, str) for x in excluded):
            raise InvariantError("excluded_scope must be an explicit list")
        if "active" in record and not isinstance(record["active"], bool):
            raise InvariantError("active must be boolean")

    def _validate(self, kind, record, namespace):
        if kind == "aim":
            self._check_aim(record)
            if record.get("active") is True and self._current_aims(namespace)[record["aim_type"]]:
                raise InvariantError("only an initial aim can register active; use an approved decision")
        elif kind == "task":
            aim = self._require("aim", self._text(record, "aim_id"), namespace)
            current = self._current_aims(namespace)
            if aim["aim_type"] != "task" or (current["task"] or {}).get("id") != aim["id"]:
                raise InvariantError("new task must bind the active task aim")
            if (current["main"] or {}).get("id") != record.get("main_aim_id"):
                raise InvariantError("new task must bind the active main aim")
            self._text(record, "workpack_id")
            criteria = self._ids(record, "criterion_ids")
            proof = self._ids(record, "expected_proof")
            if criteria != proof or not criteria <= self._criteria(aim):
                raise InvariantError("expected_proof must cover exactly the task's registered criterion IDs")
            if record["status"] not in ("declared", "claimed"):
                raise InvariantError("task status can only be declared or claimed; completion requires assessment")
            if namespace.startswith("work:"):
                self._recipient(record.get("recipient"))
        elif kind == "evidence":
            task = self._require("task", self._text(record, "task_id"), namespace)
            aim = self._require("aim", self._text(record, "aim_id"), namespace)
            if aim["aim_type"] != "task" or record["aim_id"] not in self._allowed_task_aims(task, namespace):
                raise InvariantError("evidence aim revision does not belong to the task or its approved transition")
            if not self._ids(record, "criterion_ids") <= self._criteria(aim):
                raise InvariantError("evidence contains unknown criterion IDs")
            for key in ("artifact", "summary", "proof_source", "test_input", "limitation"):
                self._text(record, key)
            if record.get("result") not in ("PASS", "FAIL", "NOT_RUN", "INCONCLUSIVE"):
                raise InvariantError("invalid evidence result")
            if not isinstance(record.get("verified"), bool):
                raise InvariantError("verified must be a boolean recorded judgement")
            for prior_id in self._ids(record, "supersedes", nonempty=False):
                prior = self._require("evidence", prior_id, namespace)
                if any(prior[key] != record[key] for key in ("task_id", "aim_id", "artifact")):
                    raise InvariantError("superseded evidence must have the same task, aim and exact artifact")
                if not set(prior["criterion_ids"]) <= set(record["criterion_ids"]):
                    raise InvariantError("replacement evidence must cover every superseded criterion")
                if not record["verified"]:
                    raise InvariantError("only verified evidence can supersede a receipt")
                if record["result"] not in ("PASS", "FAIL"):
                    raise InvariantError("NOT_RUN or INCONCLUSIVE cannot supersede a tested result")
        elif kind == "assessment":
            self._check_assessment(record, namespace)
        elif kind == "proposal":
            self._check_proposal(record, namespace)
        elif kind == "adoption":
            self._check_adoption(record, namespace)
        elif kind == "review":
            self._text(record, "workpack_id")
            self._text(record, "reason")
            values = record.get("thresholds")
            if (not isinstance(values, list) or
                any(type(x) is not int or x not in THRESHOLDS for x in values) or
                len(set(values)) != len(values)):
                raise InvariantError("thresholds must contain unique members of 5/10/15/19")
            if not values:
                if record.get("trigger") not in ("response_2", "y", "handover", "closure", "contradiction"):
                    raise InvariantError("a non-count review requires an explicit response_2/y/handover/closure/contradiction trigger")
                self._text(record, "source_ref")
            count = len(self._validated_tasks(namespace, record["workpack_id"]))
            if any(x > count for x in values):
                raise InvariantError("cannot review an unearned checkpoint")
        elif kind == "handover" and namespace.startswith("work:"):
            for key in ("from", "to", "workpack_id", "main_aim_id", "task_aim_id", "response_2_id", "authority_ref"):
                self._text(record, key)
            self._recipient(record["from"])
            self._recipient(record["to"])
            if record.get("owner_authorized") is not True:
                raise InvariantError("handover requires an existing Owner-authorized mapping assertion")
            self._check_baseline(record["main_aim_id"], record["task_aim_id"], namespace)
            response = self._require("review_input", record["response_2_id"], namespace)
            if (response.get("input_type") != "response_2" or response.get("verified") is not True or
                response.get("recipient") != record["from"] or
                any(response.get(key) != record[key] for key in ("workpack_id", "main_aim_id", "task_aim_id"))):
                raise InvariantError("handover requires verified response-2 input matching outgoing recipient, workpack and aim revisions")
            self._text(response, "source_ref")
            self._text(response, "digest")
            unfinished = self._ids(record, "unfinished_task_ids", nonempty=False)
            validated = {t["id"] for t in self._validated_tasks(namespace, record["workpack_id"])}
            for task_id in unfinished:
                task = self._require("task", task_id, namespace)
                transition = self._latest_transition(task_id, namespace)
                if (task["workpack_id"] != record["workpack_id"] or task_id in validated or
                    self._task_recipient(task, namespace) != record["from"] or
                    (transition and transition["action"] == "STOP")):
                    raise InvariantError("handover unfinished tasks must be valid open workpack tasks assigned to the outgoing recipient")
        elif kind == "control":
            # These receipts are assertions supplied to the register.
            # Planned records may exist but cannot satisfy adoption.
            if record.get("control_type") == "TASK_PLAN":
                self._text(record, "recipient")
                self._require("task", self._text(record, "task_id"), namespace)
                aim = self._require("aim", self._text(record, "aim_id"), namespace)
                # A Main Aim update is delivered under its own revision ID, but
                # a task plan still names the Task Aim's acceptance criteria.
                proof_aim = aim if aim["aim_type"] == "task" else self._current_aims(namespace)["task"]
                if proof_aim is None or not self._ids(record, "criterion_ids") <= self._criteria(proof_aim):
                    raise InvariantError("task plan uses unknown criteria")
                self._text(record, "next_action")
            elif record.get("control_type") == "TASK_REPORT_REVIEW":
                for key in ("recipient", "workpack_id", "message_id", "report_id", "reason", "source_ref", "alignment"):
                    self._text(record, key)
                if namespace.startswith("work:"):
                    self._recipient(record["recipient"])
                report = self._require("report", record["report_id"], namespace)
                if any(report.get(key) != record[key] for key in ("message_id", "recipient", "workpack_id")):
                    raise InvariantError("task report review must match the exact message, recipient and workpack")
                for assessment_id in self._ids(record, "assessment_ids", nonempty=False):
                    assessment = self._require("assessment", assessment_id, namespace)
                    task = self._require("task", assessment["task_id"], namespace)
                    if task["workpack_id"] != record["workpack_id"]:
                        raise InvariantError("reviewed assessment belongs to another workpack")

    def register_aim(self, record, namespace="demo"):
        return self.append("aim", record, namespace)

    def register_task(self, record, namespace="demo"):
        return self.append("task", record, namespace)

    def record_evidence(self, record, namespace="demo"):
        return self.append("evidence", record, namespace)

    def assess_task(self, record, namespace="demo"):
        return self.append("assessment", record, namespace)

    def _latest_transition(self, task_id, namespace):
        if namespace == "recorded":
            return None
        transition = None
        for decision in self._list("decision", namespace):
            if decision.get("activation_committed") is True:
                for item in decision.get("affected_tasks", []):
                    if item["task_id"] == task_id:
                        transition = item
        return transition

    def _allowed_task_aims(self, task, namespace):
        ids = {task["aim_id"]}
        transition = self._latest_transition(task["id"], namespace)
        if transition and transition.get("new_task_aim_id"):
            ids.add(transition["new_task_aim_id"])
        return ids

    def _recipient_context(self, task, namespace):
        """Replay explicit handovers; a task's original assignment stays immutable."""
        recipient = task.get("recipient", "unassigned")
        transfer_sequence = None
        rows = self._db.execute("SELECT sequence,payload FROM events WHERE namespace=? AND kind='handover' ORDER BY sequence", (namespace,))
        for row in rows:
            handover = json.loads(row["payload"])
            task_ids = handover.get("unfinished_task_ids", [])
            if (task["id"] in task_ids and handover.get("from") == recipient and
                isinstance(handover.get("to"), str) and handover["to"].strip()):
                recipient = handover["to"]
                transfer_sequence = row["sequence"]
        return recipient, transfer_sequence

    def _task_recipient(self, task, namespace):
        return self._recipient_context(task, namespace)[0]

    def _active_receipts(self, namespace):
        receipts = self._list("evidence", namespace)
        superseded = {old for receipt in receipts if receipt.get("verified") is True
                      for old in receipt.get("supersedes", [])}
        return {r["id"]: r for r in receipts if r["id"] not in superseded}

    def _activated_aim_ids(self, namespace):
        if namespace == "recorded":
            return set()
        return {aim_id for decision in self._list("decision", namespace)
                if decision.get("activation_committed") is True
                for aim_id in decision.get("activated_aim_ids", [])}

    def _adopted_task_plan(self, task, aim_id, namespace, recipient, after_sequence=None):
        required = set(task["expected_proof"])
        found = None
        for adoption in self._list("adoption", namespace):
            if (adoption.get("aim_id") != aim_id or adoption.get("recipient") != recipient or
                adoption.get("owner_authorized") is not True):
                continue
            if after_sequence is not None:
                sequence = self._db.execute("SELECT sequence FROM events WHERE namespace=? AND kind='adoption' AND record_id=?",
                                            (namespace, adoption["id"])).fetchone()[0]
                if sequence <= after_sequence:
                    continue
            for plan_id in adoption.get("task_plan_ids", []):
                plan = self._require("control", plan_id, namespace)
                if (plan.get("task_id") == task["id"] and plan.get("recipient") == recipient and
                    plan.get("aim_id") == aim_id and plan.get("owner_authorized") is True and
                    set(plan.get("criterion_ids", [])) == required):
                    found = plan
        return found

    def _validation_problem(self, task, assessment, namespace):
        transition = self._latest_transition(task["id"], namespace)
        expected_aim = task["aim_id"]
        required = set(task["expected_proof"])
        activated = self._activated_aim_ids(namespace)
        recipient, transfer_sequence = self._recipient_context(task, namespace)
        required_adoptions = {aim_id for aim_id in (task["aim_id"], task.get("main_aim_id"))
                              if aim_id in activated}
        if transition:
            if transition["action"] == "STOP":
                return "task is stopped by the approved transition"
            expected_aim = transition.get("new_task_aim_id") or expected_aim
            if expected_aim != task["aim_id"]:
                required_adoptions.add(expected_aim)
            new_main = transition.get("new_main_aim_id")
            if new_main and new_main != task.get("main_aim_id"):
                required_adoptions.add(new_main)
        if transfer_sequence is not None:
            required_adoptions.add(expected_aim)
        for aim_id in required_adoptions:
            if self._adopted_task_plan(task, aim_id, namespace, recipient, transfer_sequence) is None:
                return "new aim requires adopted task criteria before validation"
        if assessment.get("aim_id") != expected_aim:
            return "assessment must use the task's effective approved aim revision"
        active = self._active_receipts(namespace)
        artifact = assessment.get("artifact")
        coverage = set()
        for evidence_id in assessment.get("evidence_ids", []):
            receipt = active.get(evidence_id)
            if receipt is None:
                return "assessment references missing or explicitly superseded evidence"
            if (receipt["task_id"] != task["id"] or receipt["aim_id"] != expected_aim or
                receipt["artifact"] != artifact):
                return "receipt must match task, aim revision and exact assessment artifact"
            if receipt["verified"] is True and receipt["result"] == "PASS":
                coverage.update(receipt["criterion_ids"])
        if not required <= coverage:
            return "verified PASS receipts do not cover every expected proof criterion"
        for receipt in active.values():
            if (receipt["task_id"] == task["id"] and receipt["aim_id"] == expected_aim and
                receipt["artifact"] == artifact and receipt["verified"] is True and
                receipt["result"] == "FAIL" and required.intersection(receipt["criterion_ids"])):
                return "active verified FAIL contradicts the PASS evidence"
        return None

    def _check_assessment(self, record, namespace):
        task = self._require("task", self._text(record, "task_id"), namespace)
        self._require("aim", self._text(record, "aim_id"), namespace)
        if record["aim_id"] not in self._allowed_task_aims(task, namespace):
            raise InvariantError("assessment aim revision does not belong to this task")
        if record.get("verdict") not in ("VALIDATED", "VERIFY_FIRST", "DRIFT", "ALIGNED"):
            raise InvariantError("invalid assessment verdict")
        self._text(record, "reason")
        self._ids(record, "evidence_ids", nonempty=False)
        for evidence_id in record["evidence_ids"]:
            receipt = self._require("evidence", evidence_id, namespace)
            if receipt["task_id"] != task["id"]:
                raise InvariantError("assessment evidence belongs to another task")
        if record["verdict"] == "VALIDATED":
            self._text(record, "artifact")
            problem = self._validation_problem(task, record, namespace)
            if problem:
                raise InvariantError(problem)

    def _validated_tasks(self, namespace, workpack_id=None):
        latest = {a["task_id"]: a for a in self._list("assessment", namespace)}
        result = []
        for task in self._list("task", namespace):
            if workpack_id is not None and task["workpack_id"] != workpack_id:
                continue
            assessment = latest.get(task["id"])
            if (assessment and assessment["verdict"] == "VALIDATED" and
                self._validation_problem(task, assessment, namespace) is None):
                result.append(task)
        return result

    def validated_tasks(self, namespace="demo", workpack_id=None):
        self._namespace(namespace)
        with self._lock:
            return self._validated_tasks(namespace, workpack_id)

    def _impact_ids(self, proposal, namespace):
        changes = {a["aim_type"] for a in proposal["new_aims"]}
        done = {t["id"] for t in self._validated_tasks(namespace)}
        result = set()
        for task in self._list("task", namespace):
            if task["id"] in done:
                continue
            transition = self._latest_transition(task["id"], namespace)
            if transition and transition["action"] == "STOP":
                continue
            effective_task = (transition or {}).get("new_task_aim_id") or task["aim_id"]
            effective_main = (transition or {}).get("new_main_aim_id") or task.get("main_aim_id")
            if (("task" in changes and effective_task == proposal["baseline_task_id"]) or
                ("main" in changes and effective_main == proposal["baseline_main_id"])):
                result.add(task["id"])
        return result

    def _check_baseline(self, main_id, task_id, namespace):
        current = self._current_aims(namespace)
        if ((current["main"] or {}).get("id") != main_id or
            (current["task"] or {}).get("id") != task_id):
            raise InvariantError("stale aim baseline")

    def _check_proposal(self, record, namespace):
        self._text(record, "baseline_main_id")
        self._text(record, "baseline_task_id")
        self._check_baseline(record["baseline_main_id"], record["baseline_task_id"], namespace)
        if len(re.findall(r"\S+", self._text(record, "suggestion"))) >= 50:
            raise InvariantError("suggestion must contain fewer than 50 words")
        self._text(record, "benefit_claim")
        if "displaced_work" not in record:
            raise InvariantError("proposal must explicitly describe displaced_work")
        new_aims = record.get("new_aims")
        if not isinstance(new_aims, list) or not new_aims or len(new_aims) > 2:
            raise InvariantError("new_aims must contain one or two full revision records")
        seen = set()
        for aim in new_aims:
            self._text(aim, "id")
            self._check_aim(aim)
            if aim.get("active") is True:
                raise InvariantError("proposed revisions cannot already be active")
            if aim["aim_type"] in seen:
                raise InvariantError("proposal contains duplicate aim types")
            seen.add(aim["aim_type"])
            if self._get("aim", aim["id"], namespace):
                raise InvariantError("proposed revision ID already exists")
        impact = self._ids(record, "impact_task_ids", nonempty=False)
        if impact != self._impact_ids(record, namespace):
            raise InvariantError("proposal impact must exactly cover currently affected active tasks")
        actions = record.get("task_actions", {i: "REPLAN" for i in impact})
        if not isinstance(actions, dict) or set(actions) != impact or any(
                a not in ("CONTINUE", "STOP", "REPLAN", "REVERIFY") for a in actions.values()):
            raise InvariantError("task_actions must cover every impacted task with a valid action")

    def propose(self, record, namespace="demo"):
        return self.append("proposal", record, namespace)

    def decide(self, proposal_id, outcome, authority_ref,
               expected_baseline_main_id, expected_baseline_task_id,
               namespace="demo", decision_id=None, new_aims=None):
        """Atomically record a supplied decision and optionally activate revisions.

        No score/ROI can call this automatically. New revisions must exactly match
        the immutable proposal. APPROVE records an explicitly supplied Owner
        decision. A work authority_ref is a runner-supplied Owner source assertion,
        never authentication of the human; demo decisions remain simulated.
        """
        self._namespace(namespace)
        if outcome not in ("APPROVE", "REJECT", "DEFER", "RETAIN"):
            raise InvariantError("outcome must be APPROVE, REJECT, DEFER or RETAIN")
        if not isinstance(authority_ref, str) or not authority_ref.strip():
            raise InvariantError("decision requires an explicit authority reference")
        if namespace == "recorded" and outcome == "APPROVE":
            raise InvariantError("recorded namespace cannot activate revisions")
        decision_id = decision_id or f"decision:{proposal_id}:{outcome.lower()}"
        with self._transaction():
            proposal = self._require("proposal", proposal_id, namespace)
            if new_aims is not None and self._json(new_aims) != self._json(proposal["new_aims"]):
                raise InvariantError("decision revisions differ from the exact proposal")
            existing = self._get("decision", decision_id, namespace)
            if existing:
                fields = (existing.get("proposal_id") == proposal_id and
                          existing.get("outcome") == outcome and
                          existing.get("authority_ref") == authority_ref and
                          existing.get("expected_baseline_main_id") == expected_baseline_main_id and
                          existing.get("expected_baseline_task_id") == expected_baseline_task_id)
                if not fields:
                    raise InvariantError("decision ID already exists with different decision input")
                return existing
            if any(d.get("proposal_id") == proposal_id and d.get("outcome") in ("APPROVE", "REJECT", "RETAIN")
                   for d in self._list("decision", namespace)):
                raise InvariantError("proposal already has a terminal decision")
            if (expected_baseline_main_id != proposal["baseline_main_id"] or
                expected_baseline_task_id != proposal["baseline_task_id"]):
                raise InvariantError("decision expected baseline differs from exact proposal")
            self._check_baseline(expected_baseline_main_id, expected_baseline_task_id, namespace)
            impact = self._impact_ids(proposal, namespace)
            if impact != set(proposal["impact_task_ids"]):
                raise InvariantError("active-task impact changed; a fresh proposal is required")
            decision = {"id": decision_id, "proposal_id": proposal_id, "outcome": outcome,
                        "authority_ref": authority_ref,
                        "expected_baseline_main_id": expected_baseline_main_id,
                        "expected_baseline_task_id": expected_baseline_task_id,
                        "activation_committed": outcome == "APPROVE" and namespace != "recorded",
                        "activated_aim_ids": [], "affected_tasks": [],
                        "evidence_applicability": "No automatic transfer between aim revisions"}
            if decision["activation_committed"]:
                updated = {a["aim_type"]: a["id"] for a in proposal["new_aims"]}
                actions = proposal.get("task_actions", {i: "REPLAN" for i in impact})
                for aim in proposal["new_aims"]:
                    self._check_aim(aim)
                    if self._get("aim", aim["id"], namespace):
                        raise InvariantError("new revision ID already registered")
                    self._insert("aim", aim, namespace)
                    decision["activated_aim_ids"].append(aim["id"])
                for task_id in sorted(impact):
                    decision["affected_tasks"].append({"task_id": task_id, "action": actions[task_id],
                        "new_main_aim_id": updated.get("main", expected_baseline_main_id),
                        "new_task_aim_id": updated.get("task", expected_baseline_task_id)})
                # Durable outbox records are plans only. They never imply delivery.
                recipients = {self._task_recipient(t, namespace) for t in self._list("task", namespace)
                              if t["id"] in impact}
                for recipient in sorted(recipients):
                    for aim_id in decision["activated_aim_ids"]:
                        self._insert("control", {"id": f"outbox:{decision_id}:{recipient}:{aim_id}",
                            "control_type": "UPDATE_OUTBOX", "decision_id": decision_id,
                            "recipient": recipient, "aim_id": aim_id, "status": "PLANNED",
                            "task_ids": sorted(t["id"] for t in self._list("task", namespace)
                                               if t["id"] in impact and self._task_recipient(t, namespace) == recipient)}, namespace)
            return self._insert("decision", decision, namespace)

    def _check_adoption(self, record, namespace):
        recipient = self._text(record, "recipient")
        aim_id = self._text(record, "aim_id")
        aim = self._require("aim", aim_id, namespace)
        if (self._current_aims(namespace)[aim["aim_type"]] or {}).get("id") != aim_id:
            raise InvariantError("adoption must target the current approved revision")
        self._text(record, "authority_ref")
        if record.get("owner_authorized") is not True:
            raise InvariantError("adoption requires an explicit owner-authorized input assertion")
        delivery = self._require("control", self._text(record, "delivery_id"), namespace)
        acknowledgement = self._require("control", self._text(record, "acknowledgement_id"), namespace)
        for control, expected_type, expected_status in (
                (delivery, "DELIVERY", "DELIVERED"),
                (acknowledgement, "ACKNOWLEDGEMENT", "ACKNOWLEDGED")):
            if (control.get("control_type") != expected_type or control.get("status") != expected_status or
                control.get("verified") is not True or control.get("recipient") != recipient or
                control.get("aim_id") != aim_id):
                raise InvariantError("adoption needs verified exact-recipient delivery and acknowledgement receipts")
        if acknowledgement.get("delivery_id") != record["delivery_id"]:
            raise InvariantError("acknowledgement must reference the exact delivery")
        for plan_id in self._ids(record, "task_plan_ids"):
            plan = self._require("control", plan_id, namespace)
            if (plan.get("control_type") != "TASK_PLAN" or plan.get("recipient") != recipient or
                plan.get("aim_id") != aim_id or plan.get("owner_authorized") is not True):
                raise InvariantError("adoption requires recipient-specific authorized task plans")
            self._text(plan, "authority_ref")
            task = self._require("task", plan["task_id"], namespace)
            if self._task_recipient(task, namespace) not in ("unassigned", recipient):
                raise InvariantError("task plan recipient differs from the assigned task agent")
            plan_criteria = self._ids(plan, "criterion_ids")
            if plan_criteria != set(task["criterion_ids"]) or plan_criteria != set(task["expected_proof"]):
                raise InvariantError("adopted plan must preserve the task's registered required proof criteria; this version has no approved per-task proof override")
            proof_aim = aim if aim["aim_type"] == "task" else self._current_aims(namespace)["task"]
            if proof_aim is None or not plan_criteria <= self._criteria(proof_aim):
                raise InvariantError("adopted plan criteria do not belong to this revision")
            self._text(plan, "next_action")

    def record_adoption(self, record, namespace="demo"):
        return self.append("adoption", record, namespace)

    def checkpoint_due(self, namespace="demo", workpack_id=None):
        self._namespace(namespace)
        with self._lock:
            if workpack_id is None:
                workpacks = {t["workpack_id"] for t in self._list("task", namespace)}
                if len(workpacks) > 1:
                    raise InvariantError("checkpoint_due requires a workpack_id when multiple workpacks exist")
                if workpacks:
                    workpack_id = next(iter(workpacks))
            validated = self._validated_tasks(namespace, workpack_id)
            covered = {x for review in self._list("review", namespace)
                       if workpack_id is None or review["workpack_id"] == workpack_id
                       for x in review["thresholds"]}
            return {"workpack_id": workpack_id, "count": len(validated),
                    "validated_task_ids": [t["id"] for t in validated],
                    "due": [x for x in THRESHOLDS if x <= len(validated) and x not in covered]}

    def record_review(self, record, namespace="demo"):
        return self.append("review", record, namespace)

    def _eligibility_problem(self, task, namespace, current, latest_assessments):
        transition = self._latest_transition(task["id"], namespace)
        if transition and transition["action"] == "STOP":
            return "STOPPED"
        assessment = latest_assessments.get(task["id"])
        if assessment and assessment.get("verdict") == "DRIFT":
            return "DRIFT"
        latest_drift = None
        for drift in self._list("drift", namespace):
            if drift.get("task_id") == task["id"] or task["id"] in drift.get("task_ids", []):
                latest_drift = drift
        if latest_drift and latest_drift.get("verdict") in ("CONFIRMED", "DRIFT", "OUT_OF_AIM"):
            return "DRIFT"
        if not current["main"] or not current["task"]:
            return "NO_APPROVED_AIM"
        effective_task = (transition or {}).get("new_task_aim_id") or task["aim_id"]
        effective_main = (transition or {}).get("new_main_aim_id") or task.get("main_aim_id")
        if effective_task != current["task"]["id"] or effective_main != current["main"]["id"]:
            return "REVISION_REPLAN_REQUIRED"
        required = set(task.get("expected_proof", []))
        if (not required or required != set(task.get("criterion_ids", [])) or
            not required <= self._criteria(current["task"])):
            return "REGISTERED_PROOF_NOT_PRESERVED"
        activated = self._activated_aim_ids(namespace)
        recipient, transfer_sequence = self._recipient_context(task, namespace)
        for aim_id in (effective_main, effective_task):
            needs_adoption = aim_id in activated or (transfer_sequence is not None and aim_id == effective_task)
            if needs_adoption and self._adopted_task_plan(task, aim_id, namespace, recipient, transfer_sequence) is None:
                return "RECIPIENT_ADOPTION_REQUIRED"
        return None

    def projection(self, namespace, workpack_id, recipient):
        """Compact, transaction-consistent authority and dispatch eligibility.

        Counts cover the whole workpack across handovers. Eligibility alone is
        recipient-specific; it is a structural gate, not a semantic judgement or
        permission to send a browser message. Initial approved assignments need
        no extra adoption. Transferred unfinished tasks and activated scope revisions require exact-recipient
        delivery, acknowledgement and a plan preserving that task's proof.
        """
        self._namespace(namespace)
        if not isinstance(workpack_id, str) or not workpack_id.strip():
            raise InvariantError("projection requires a workpack_id")
        if not isinstance(recipient, str) or not recipient.strip():
            raise InvariantError("projection requires an exact recipient")
        if namespace.startswith("work:"):
            self._recipient(recipient)
        with self._read_transaction():
            sequence = self._db.execute(
                "SELECT coalesce(max(sequence),0) FROM events WHERE namespace=?", (namespace,)).fetchone()[0]
            current = self._current_aims(namespace)
            tasks = [t for t in self._list("task", namespace) if t["workpack_id"] == workpack_id]
            task_ids = {t["id"] for t in tasks}
            validated = self._validated_tasks(namespace, workpack_id)
            validated_ids = {t["id"] for t in validated}
            assessments = [a for a in self._list("assessment", namespace) if a["task_id"] in task_ids]
            latest_assessments = {a["task_id"]: a for a in assessments}
            eligible = [t["id"] for t in tasks if t["id"] not in validated_ids and
                        self._task_recipient(t, namespace) == recipient and
                        self._eligibility_problem(t, namespace, current, latest_assessments) is None]
            controls = [c for c in self._list("control", namespace)
                        if c.get("recipient") == recipient and c.get("workpack_id") == workpack_id]
            reviews = [c for c in controls if c.get("control_type") == "TASK_REPORT_REVIEW"]
            reviewed_messages = list(dict.fromkeys(c["message_id"] for c in reviews))
            observed_messages = list(dict.fromkeys(c["message_id"] for c in controls
                if c.get("control_type") == "TASK_REPORT_OBSERVATION" and isinstance(c.get("message_id"), str)))
            latest = assessments[-1] if assessments else None
            if latest is not None:
                latest = {key: copy.deepcopy(latest[key]) for key in
                          ("id", "task_id", "aim_id", "verdict", "artifact", "reason", "evidence_ids")
                          if key in latest}
                if isinstance(latest.get("reason"), str):
                    latest["reason"] = latest["reason"][:500]
            terminal = {d.get("proposal_id") for d in self._list("decision", namespace)
                        if d.get("outcome") in ("APPROVE", "REJECT", "RETAIN")}
            checkpoint = self.checkpoint_due(namespace, workpack_id)
            reviewed_thresholds = sorted({threshold for review in self._list("review", namespace)
                                          if review["workpack_id"] == workpack_id
                                          for threshold in review["thresholds"]})
            return {"sequence": sequence,
                    "main": {k: current["main"][k] for k in ("id", "label")} if current["main"] else None,
                    "task": {k: current["task"][k] for k in ("id", "label")} if current["task"] else None,
                    "validated_ids": [t["id"] for t in validated],
                    "registered_ids": [t["id"] for t in tasks], "eligible_ids": eligible,
                    "alignment": reviews[-1]["alignment"] if reviews else (latest or {}).get("verdict", "UNASSESSED"),
                    "latest_assessment": latest, "reviewed_message_ids": reviewed_messages,
                    "latest_reviewed_message_id": reviews[-1]["message_id"] if reviews else None,
                    "unreviewed_message_ids": [mid for mid in observed_messages if mid not in set(reviewed_messages)],
                    "due": checkpoint["due"], "reviewed_thresholds": reviewed_thresholds,
                    "pending_proposal_ids": [p["id"] for p in self._list("proposal", namespace) if p["id"] not in terminal]}

    def recall(self, query=None, ids=None, kinds=None, namespace="demo", max_items=20):
        """Return bounded scoped records, excluding duplicated report snapshots.

        Reports are available deliberately through kinds=['report'] or an exact
        report ID in ids. Substring searches normally inspect underlying records.
        """
        self._namespace(namespace)
        if type(max_items) is not int or max_items < 1 or max_items > 200:
            raise InvariantError("max_items must be between 1 and 200")
        wanted = set(ids or [])
        if kinds is None:
            kinds = KINDS if wanted else tuple(kind for kind in KINDS if kind != "report")
        if any(kind not in KINDS for kind in kinds):
            raise InvariantError("recall contains an unknown kind")
        query = query.casefold() if isinstance(query, str) else None
        clauses, params = ["namespace=?"], [namespace]
        if not kinds:
            return {"items": [], "total": 0, "truncated": False}
        clauses.append("kind IN (" + ",".join("?" for _ in kinds) + ")")
        params.extend(kinds)
        if wanted:
            clauses.append("record_id IN (" + ",".join("?" for _ in wanted) + ")")
            params.extend(sorted(wanted))
        items, total = [], 0
        with self._lock:
            rows = self._db.execute("SELECT sequence,kind,payload FROM events WHERE " +
                                    " AND ".join(clauses) + " ORDER BY sequence", params)
            for row in rows:
                if query and query not in row["payload"].casefold():
                    continue
                total += 1
                if len(items) < max_items:
                    items.append({"kind": row["kind"], "record": json.loads(row["payload"]),
                                  "sequence": row["sequence"]})
        return {"items": items, "total": total, "truncated": total > max_items}
