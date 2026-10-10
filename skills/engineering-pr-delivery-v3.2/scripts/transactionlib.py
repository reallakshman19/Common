from __future__ import annotations

import copy
import hashlib
import json
import os
import re
import shutil
from fnmatch import fnmatch
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from nomenclature import canonical_ids_in_text, parse_canonical_id
from v3lib import load_yaml, repo_path, require_identifier, validate_schema


COMMAND_TARGET_PATTERNS = {
    # Issue-scoped immutable Markdown messages; not lease/scoreboard/plan authority.
    "PUBLISH_BUDDY_MARKDOWN": ["relay/CONTINUITY/episodes/ISSUE-*/messages/*.md"],
    "ACTIVATE_LEASE": [
        "relay/EVENTS.jsonl",
        "relay/STATE.yaml",
        "relay/GENERATED/CURRENT_SNAPSHOT.yaml",
        "relay/LEASES/LEASE-*.yaml",
    ],
    "RENEW_LEASE": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/GENERATED/CURRENT_SNAPSHOT.yaml",
    ],
    "RECORD_RECOVERY_RECONSTRUCTED": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
    ],
    "RECORD_CHANGE_HYPOTHESIS": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/CHANGES/CHANGE-*.yaml",
    ],
    "VERIFY_CHANGE_DELTA": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/CHANGES/CHANGE-*.yaml",
    ],
    "PROPOSE_CHANGE_DELTA": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/CHANGES/CHANGE-*.yaml",
    ],
    "AUTHORIZE_CHANGE_DELTA": [
        "relay/EVENTS.jsonl",
        "relay/CHANGES/CHANGE-*.yaml",
    ],
    "RESOLVE_CONTROL": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/CONTROLS/controls.yaml",
        "relay/GENERATED/CURRENT_SNAPSHOT.yaml",
    ],
    "RECONCILE_ROADMAP": [
        "relay/EVENTS.jsonl",
        "relay/LEASES/LEASE-*.yaml",
        "relay/ROADMAP/ROADMAP.yaml",
        "relay/STATE.yaml",
        "relay/GENERATED/CURRENT_SNAPSHOT.yaml",
        "relay/CHANGES/CHANGE-*.yaml",
    ],
    "SYNC_HANDOVER_LEDGER": [
        "relay/EVENTS.jsonl",
        "relay/GENERATED/HANDOVER_PROVIDER_STATUS.yaml",
        "relay/GENERATED/HANDOVER_LEDGER.yaml",
        "relay/GENERATED/HANDOVER_LEDGER.md",
        "relay/GENERATED/PARENT_RELAY_SUMMARY.md",
    ],
    "FREEZE_LEGACY_CUTOVER": [
        "relay/EVENTS.jsonl",
        "relay/PROTOCOL_SELECTION.yaml",
    ],
    "ADMIT_TASK": [
        "relay/EVENTS.jsonl",
        "relay/ROADMAP/ROADMAP.yaml",
        "relay/STATE.yaml",
        "relay/GENERATED/CURRENT_SNAPSHOT.yaml",
        "relay/WORK/EP-*.yaml",
        "relay/LEASES/LEASE-*.yaml",
    ],
}


# One canonical stage allowlist for all native Relay Buddy Markdown writers.
BUDDY_MESSAGE_STAGES = frozenset({
    "READINESS", "STAGE1_INTAKE", "DISPATCH_REQUEST", "DISPATCH_OBSERVATION",
    "STAGE1_BASELINE", "STAGE1_PLAN", "STAGE1_FREEZE_CANDIDATE",
})


def _prior_buddy_message(root: Path, issue: int, current_seq: int, stage: str) -> tuple[bytes, dict[str, Any]] | None:
    """Read only earlier COMMITTED native Relay message receipts, not loose files."""
    folder = root / f"relay/CONTINUITY/episodes/ISSUE-{issue}/messages"
    candidates: list[tuple[int, bytes, dict[str, Any]]] = []
    for path in folder.glob(f"TX.{issue}.*-{stage}.md"):
        match = re.fullmatch(rf"TX\.{issue}\.([1-9][0-9]*)-{re.escape(stage)}\.md", path.name)
        if not match or int(match.group(1)) >= current_seq:
            continue
        if path.is_symlink():
            raise TransactionError("BUDDY_PRIOR_MESSAGE_SYMLINK_FORBIDDEN")
        seq = int(match.group(1))
        tx_path = root / f"relay/TRANSACTIONS/TX.{issue}.{seq}/manifest.yaml"
        if tx_path.is_symlink():
            raise TransactionError("BUDDY_PRIOR_RECEIPT_SYMLINK_FORBIDDEN")
        if not tx_path.is_file():
            raise TransactionError("BUDDY_PRIOR_MESSAGE_UNRECORDED")
        receipt = load_manifest(tx_path)
        payload = path.read_bytes()
        operations = receipt.get("operations") or []
        if (
            receipt.get("id") != f"TX.{issue}.{seq}"
            or receipt.get("status") != "COMMITTED"
            or receipt.get("command") != "PUBLISH_BUDDY_MARKDOWN"
            or len(operations) != 1
            or operations[0].get("path") != path.relative_to(root).as_posix()
            or operations[0].get("after_digest") != _digest_bytes(payload)
        ):
            raise TransactionError("BUDDY_PRIOR_MESSAGE_RECEIPT_MISMATCH")
        candidates.append((seq, payload, receipt))
    if not candidates:
        return None
    _, payload, receipt = max(candidates, key=lambda item: item[0])
    return payload, receipt


def _require_buddy_sequence(root: Path, issue: int, seq: int, stage: str, actor: str) -> None:
    """All latest SAME-ISSUE receipts must form one ordered, unbroken Stage1 attempt.

    This proves only local transaction ordering. It does not authenticate actor
    identity, source-read isolation or the factual accuracy of a run claim.
    """
    stages = (
        "STAGE1_INTAKE", "DISPATCH_REQUEST", "DISPATCH_OBSERVATION",
        "STAGE1_BASELINE", "STAGE1_PLAN",
    )
    target_index = len(stages) if stage == "STAGE1_FREEZE_CANDIDATE" else (
        stages.index(stage) if stage in stages else -1
    )
    if target_index <= 0:
        return
    # Missing the immediate prerequisite is a missing-stage defect, not a stale
    # predecessor-chain defect. Check it first even when earlier stages are absent.
    required = stages[target_index - 1]
    if _prior_buddy_message(root, issue, seq, required) is None:
        raise TransactionError(f"BUDDY_STAGE_ORDER_MISSING_{required}")
    chain: dict[str, tuple[bytes, dict[str, Any]]] = {}
    last_seq = 0
    for predecessor in stages[:target_index]:
        observation = _prior_buddy_message(root, issue, seq, predecessor)
        if observation is None:
            if predecessor == stages[target_index - 1]:
                raise TransactionError(f"BUDDY_STAGE_ORDER_MISSING_{predecessor}")
            raise TransactionError("BUDDY_STALE_STAGE_CHAIN")
        prior_seq = int(observation[1]["id"].split(".")[-1])
        if prior_seq <= last_seq:
            raise TransactionError("BUDDY_STALE_STAGE_CHAIN")
        chain[predecessor] = observation
        last_seq = prior_seq
    if target_index >= 3:
        observed = chain["DISPATCH_OBSERVATION"][0].decode("utf-8")
        if not observed.startswith("# RUNNER_EXECUTION_OBSERVED\n"):
            raise TransactionError("BUDDY_DISPATCH_NOT_EXECUTED")
        if not re.search(r"(?m)^Session ref: \S+", observed) or not re.search(
            r"(?m)^Read-scope ref: \S+", observed
        ):
            raise TransactionError("BUDDY_DISPATCH_REFERENCES_MISSING")
    if stage == "STAGE1_BASELINE":
        if actor == chain["DISPATCH_OBSERVATION"][1].get("actor"):
            raise TransactionError("BUDDY_OPERATOR_AND_RUNNER_NOT_SEPARATE")
    if stage == "STAGE1_PLAN":
        if actor != chain["STAGE1_BASELINE"][1].get("actor"):
            raise TransactionError("BUDDY_STAGE1_AUTHOR_CHANGED")
    if stage == "STAGE1_FREEZE_CANDIDATE":
        if chain["STAGE1_BASELINE"][1].get("actor") != chain["STAGE1_PLAN"][1].get("actor"):
            raise TransactionError("BUDDY_STAGE1_AUTHOR_CHANGED")
        if actor == chain["STAGE1_PLAN"][1].get("actor"):
            raise TransactionError("BUDDY_FREEZE_OPERATOR_NOT_SEPARATE")




def _validate_freeze_candidate(root: Path, issue: int, serial: int, content: str) -> None:
    """Bind ALL five latest Stage1 receipts; never claim independent admission."""
    if not content.startswith("# STAGE1_FREEZE_CANDIDATE\n"):
        raise TransactionError("BUDDY_FREEZE_HEADING_REQUIRED")
    verdicts = re.findall(r"(?m)^Isolation verdict: (.*)$", content)
    if verdicts != ["NOT_ATTESTED"]:
        raise TransactionError("BUDDY_FREEZE_CANNOT_SELF_CERTIFY_ISOLATION")
    phases = (
        ("STAGE1_INTAKE", "Intake"),
        ("DISPATCH_REQUEST", "Dispatch request"),
        ("DISPATCH_OBSERVATION", "Dispatch observation"),
        ("STAGE1_BASELINE", "Baseline"),
        ("STAGE1_PLAN", "Plan"),
    )
    for stage, label in phases:
        prior = _prior_buddy_message(root, issue, serial, stage)
        if prior is None:
            raise TransactionError(f"BUDDY_FREEZE_MISSING_{stage}")
        receipt = prior[1]
        tx_id = receipt["id"]
        digest = _digest_bytes(prior[0])
        tx_lines = re.findall(rf"(?m)^{re.escape(label)} tx: (.*)$", content)
        digest_lines = re.findall(rf"(?m)^{re.escape(label)} digest: (.*)$", content)
        if tx_lines != [tx_id] or digest_lines != [digest]:
            raise TransactionError(f"BUDDY_FREEZE_{stage}_REF_MISMATCH")


def _validate_buddy_markdown_transaction(
    root: Path,
    tx_id: str,
    actor: str,
    replacements: dict[str, bytes],
) -> None:
    """Prevent direct execute() from bypassing the immutable message boundary."""
    if len(replacements) != 1:
        raise TransactionError("BUDDY_SINGLE_MESSAGE_TRANSACTION_REQUIRED")
    relative, payload = next(iter(replacements.items()))
    match = re.fullmatch(
        r"relay/CONTINUITY/episodes/ISSUE-([1-9][0-9]*)/messages/"
        r"TX\.([1-9][0-9]*)\.([1-9][0-9]*)-([A-Z0-9_]+)\.md",
        relative,
    )
    if not match or int(match.group(1)) != int(match.group(2)):
        raise TransactionError("BUDDY_MESSAGE_ISSUE_PATH_INVALID")
    expected_tx = f"TX.{match.group(1)}.{match.group(3)}"
    if tx_id != expected_tx or match.group(4) not in BUDDY_MESSAGE_STAGES:
        raise TransactionError("BUDDY_MESSAGE_TX_OR_STAGE_INVALID")
    if not isinstance(payload, bytes) or not 4 <= len(payload) <= 2_000_000:
        raise TransactionError("BUDDY_MARKDOWN_BYTES_INVALID")
    try:
        content = payload.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TransactionError("BUDDY_MARKDOWN_UTF8_REQUIRED") from exc
    if not content.startswith("# ") or "\x00" in content:
        raise TransactionError("BUDDY_MARKDOWN_HEADING_REQUIRED")
    target = repo_path(root, relative, "buddy Markdown message")
    expected = root.resolve() / relative
    if target != expected or target.exists() or expected.is_symlink():
        raise TransactionError("BUDDY_MESSAGE_IMMUTABLE_OR_SYMLINKED")
    _require_buddy_sequence(root, int(match.group(1)), int(match.group(3)), match.group(4), actor)
    if match.group(4) == "STAGE1_FREEZE_CANDIDATE":
        _validate_freeze_candidate(root, int(match.group(1)), int(match.group(3)), content)


class TransactionError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _digest_path(path: Path) -> str | None:
    if not path.exists():
        return None
    return _digest_bytes(path.read_bytes())


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-relay-v3.1")
    temp.write_bytes(data)
    os.replace(temp, path)


def _atomic_write_yaml(path: Path, value: Any) -> None:
    _atomic_write_bytes(path, yaml.safe_dump(value, sort_keys=False).encode("utf-8"))


def load_manifest(path: Path) -> dict[str, Any]:
    value = load_yaml(path)
    errors = validate_schema("transaction", value, f"TRANSACTION {path}")
    if errors:
        raise TransactionError("; ".join(errors))
    return value


TERMINAL_STATUSES = {"COMMITTED", "ROLLED_BACK"}


def _transaction_dirs(base: Path) -> list[Path]:
    if not base.exists():
        return []
    return sorted(
        path
        for path in base.iterdir()
        if path.is_dir() and (path.name.startswith("TX-") or path.name.startswith("TX."))
    )


def _compact_terminal_manifest(
    root: Path,
    manifest_path: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Retain a digest receipt; discard byte payload no longer needed for recovery."""

    if manifest.get("status") not in TERMINAL_STATUSES:
        return manifest

    compact = copy.deepcopy(manifest)
    for operation in compact.get("operations") or []:
        operation.pop("staged_path", None)
        operation.pop("backup_path", None)
    compact["payload_state"] = "PRUNED"
    _atomic_write_yaml(manifest_path, compact)

    tx_dir = manifest_path.parent
    for name in ("staged", "backups"):
        payload_dir = tx_dir / name
        if payload_dir.exists():
            try:
                shutil.rmtree(payload_dir)
            except OSError:
                # Payload cleanup is an optimisation, not transaction authority.
                # The compact terminal receipt is already durable; a later
                # transaction will opportunistically retry physical pruning.
                pass
    return compact


def prune_terminal_payloads(root: Path) -> list[str]:
    """Clean terminal payload residue left by a crash after commit marking."""

    base = root / "relay/TRANSACTIONS"
    if not base.exists():
        return []

    pruned: list[str] = []
    for tx_dir in _transaction_dirs(base):
        manifest_path = tx_dir / "manifest.yaml"
        if not manifest_path.exists():
            continue
        try:
            manifest = load_manifest(manifest_path)
        except Exception:
            continue
        if manifest.get("status") not in TERMINAL_STATUSES:
            continue
        has_payload = (tx_dir / "staged").exists() or (tx_dir / "backups").exists()
        has_payload_refs = any(
            "staged_path" in operation or "backup_path" in operation
            for operation in manifest.get("operations") or []
        )
        if has_payload or has_payload_refs or manifest.get("payload_state") != "PRUNED":
            _compact_terminal_manifest(root, manifest_path, manifest)
            pruned.append(str(manifest.get("id") or tx_dir.name))
    return pruned


def incomplete_transactions(root: Path) -> list[tuple[Path, dict[str, Any] | None, str | None]]:
    base = root / "relay/TRANSACTIONS"
    if not base.exists():
        return []
    out = []
    for tx_dir in _transaction_dirs(base):
        path = tx_dir / "manifest.yaml"
        if not path.exists():
            out.append((path, None, "MISSING_MANIFEST"))
            continue
        try:
            manifest = load_manifest(path)
        except Exception as exc:
            out.append((path, None, str(exc)))
            continue
        if manifest.get("status") in {"PREPARED", "APPLYING", "RECOVERY_REQUIRED"}:
            out.append((path, manifest, None))
    return out


LEASE_MUTATION_COMMANDS = {
    "ACTIVATE_LEASE",
    "RENEW_LEASE",
    "ADMIT_TASK",
    "RELEASE_LEASE",
    "CLOSE_TASK",
}


def _validate_lease_mutations(
    root: Path,
    command: str,
    actor: str,
    replacements: dict[str, bytes],
) -> None:
    lease_targets = [
        path for path in replacements
        if path.startswith("relay/LEASES/") and path.endswith(".yaml")
    ]
    if not lease_targets or command in LEASE_MUTATION_COMMANDS:
        return

    for relative in lease_targets:
        target = repo_path(root, relative, "lease liveness target")
        if not target.exists():
            raise TransactionError(f"{command} cannot create lease authority: {relative}")
        before = load_yaml(target)
        after = yaml.safe_load(replacements[relative])
        if not isinstance(before, dict) or not isinstance(after, dict):
            raise TransactionError(f"{command} lease liveness mutation must preserve a mapping")
        if str(((before.get("executor") or {}).get("id") or "")) != str(actor):
            raise TransactionError(
                f"{command} cannot renew liveness for a lease owned by another executor"
            )

        before_top = copy.deepcopy(before)
        after_top = copy.deepcopy(after)
        before_custody = before_top.pop("custody", {}) or {}
        after_custody = after_top.pop("custody", {}) or {}
        if before_top != after_top:
            raise TransactionError(
                f"{command} may only mutate lease custody liveness fields"
            )
        if before.get("state") != "ACTIVE" or after.get("state") != "ACTIVE":
            raise TransactionError(f"{command} liveness renewal requires an ACTIVE lease")

        for key in set(before_custody) | set(after_custody):
            if key in {"renewed_at", "activity_basis"}:
                continue
            if before_custody.get(key) != after_custody.get(key):
                raise TransactionError(
                    f"{command} may not mutate lease custody.{key}"
                )


def _target_matches(path: str, pattern: str) -> bool:
    if fnmatch(path, pattern):
        return True
    if "-*" in pattern:
        return fnmatch(path, pattern.replace("-*", ".*"))
    return False


def _validate_command_targets(command: str, replacements: dict[str, bytes]) -> None:
    patterns = COMMAND_TARGET_PATTERNS.get(command)
    if not patterns:
        return
    invalid = [
        path for path in replacements
        if path.startswith("relay/")
        and not any(_target_matches(path, pattern) for pattern in patterns)
    ]
    if invalid:
        raise TransactionError(
            f"{command} cannot mutate target(s): {', '.join(sorted(invalid))}"
        )


def _jsonl_records(data: bytes) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for raw in data.decode("utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TransactionError(
                f"EVENT_HISTORY_INVALID_JSON: {exc.msg}"
            ) from exc
        if not isinstance(value, dict):
            raise TransactionError("EVENT_HISTORY_INVALID_RECORD: expected JSON object")
        records.append(value)
    return records


def _validate_append_only_history(root: Path, replacements: dict[str, bytes]) -> None:
    relative = "relay/EVENTS.jsonl"
    after = replacements.get(relative)
    if after is None:
        return
    target = root / relative
    before_records = _jsonl_records(target.read_bytes()) if target.exists() else []
    after_records = _jsonl_records(after)
    if (
        len(after_records) < len(before_records)
        or after_records[: len(before_records)] != before_records
    ):
        raise TransactionError(
            "EVENT_HISTORY_NOT_APPEND_ONLY: relay/EVENTS.jsonl replacement must extend the exact current durable event sequence"
        )


def _prepare(
    root: Path,
    *,
    tx_id: str,
    command: str,
    actor: str,
    replacements: dict[str, bytes],
) -> tuple[Path, dict[str, Any]]:
    try:
        require_identifier(tx_id, "TX-", "transaction id")
    except ValueError as exc:
        raise TransactionError(str(exc)) from exc
    if command == "PUBLISH_BUDDY_MARKDOWN":
        _validate_buddy_markdown_transaction(root, tx_id, actor, replacements)
    prune_terminal_payloads(root)
    if incomplete_transactions(root):
        raise TransactionError("another incomplete V3 transaction exists; recover it before starting a new command")
    _validate_command_targets(command, replacements)
    _validate_lease_mutations(root, command, actor, replacements)
    _validate_append_only_history(root, replacements)
    tx_dir = repo_path(root, f"relay/TRANSACTIONS/{tx_id}", "transaction directory")
    manifest_path = tx_dir / "manifest.yaml"
    try:
        tx_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise TransactionError(f"transaction already exists: {tx_id}") from exc

    operations = []
    for index, (relative, after_bytes) in enumerate(sorted(replacements.items())):
        target = repo_path(root, relative, "transaction target")
        before_exists = target.exists()
        before_digest = _digest_path(target)
        staged_rel = f"relay/TRANSACTIONS/{tx_id}/staged/{index:03d}.after"
        backup_rel = f"relay/TRANSACTIONS/{tx_id}/backups/{index:03d}.before" if before_exists else None
        staged = root / staged_rel
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(after_bytes)
        if backup_rel:
            backup = root / backup_rel
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(target, backup)
        operations.append({
            "path": relative,
            "before_exists": before_exists,
            "before_digest": before_digest,
            "after_digest": _digest_bytes(after_bytes),
            "staged_path": staged_rel,
            "backup_path": backup_rel,
        })

    identity_reservations: set[str] = set()
    if parse_canonical_id(tx_id) is not None:
        identity_reservations.add(tx_id)
    # Free-form Buddy Markdown can quote historical TX/EP/EVT IDs as evidence.
    # Those mentions are REFERENCES, not freshly allocated Relay identities.
    if command != "PUBLISH_BUDDY_MARKDOWN":
        for payload in replacements.values():
            try:
                identity_reservations.update(canonical_ids_in_text(payload.decode("utf-8")))
            except UnicodeDecodeError:
                continue

    now = _now()
    manifest = {
        "schema_version": "relay-v3.1-transaction",
        "id": tx_id,
        "command": command,
        "actor": actor,
        "status": "PREPARED",
        "created_at": now,
        "updated_at": now,
        "operations": operations,
        "applied": [],
        "identity_reservations": sorted(identity_reservations),
        "payload_state": "RECOVERY_PAYLOAD",
    }
    errors = validate_schema("transaction", manifest, "TRANSACTION")
    if errors:
        raise TransactionError("; ".join(errors))
    _atomic_write_yaml(manifest_path, manifest)
    return manifest_path, manifest


def execute(
    root: Path,
    *,
    tx_id: str,
    command: str,
    actor: str,
    replacements: dict[str, bytes],
    fail_after: int | None = None,
) -> dict[str, Any]:
    manifest_path, manifest = _prepare(
        root,
        tx_id=tx_id,
        command=command,
        actor=actor,
        replacements=replacements,
    )
    manifest["status"] = "APPLYING"
    manifest["updated_at"] = _now()
    _atomic_write_yaml(manifest_path, manifest)

    try:
        for index, operation in enumerate(manifest["operations"], 1):
            target = repo_path(root, operation["path"], "transaction target")
            current = _digest_path(target)
            if current != operation["before_digest"]:
                manifest["status"] = "RECOVERY_REQUIRED"
                manifest["updated_at"] = _now()
                _atomic_write_yaml(manifest_path, manifest)
                raise TransactionError(
                    f"precondition changed for {operation['path']}: expected {operation['before_digest']}, got {current}"
                )
            staged = repo_path(root, operation["staged_path"], "transaction staged path")
            _atomic_write_bytes(target, staged.read_bytes())
            manifest["applied"].append(operation["path"])
            manifest["updated_at"] = _now()
            _atomic_write_yaml(manifest_path, manifest)
            if fail_after is not None and index >= fail_after:
                raise TransactionError("injected transaction interruption")
    except Exception:
        if manifest.get("status") != "RECOVERY_REQUIRED":
            manifest["status"] = "RECOVERY_REQUIRED"
            manifest["updated_at"] = _now()
            _atomic_write_yaml(manifest_path, manifest)
        raise

    manifest["status"] = "COMMITTED"
    manifest["updated_at"] = _now()
    _atomic_write_yaml(manifest_path, manifest)
    return _compact_terminal_manifest(root, manifest_path, manifest)


def recover(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if manifest.get("status") not in {"PREPARED", "APPLYING", "RECOVERY_REQUIRED"}:
        return manifest

    states = []
    for operation in manifest["operations"]:
        digest = _digest_path(repo_path(root, operation["path"], "transaction target"))
        if digest == operation["after_digest"]:
            states.append("AFTER")
        elif digest == operation["before_digest"]:
            states.append("BEFORE")
        else:
            states.append("OTHER")

    if all(state == "AFTER" for state in states):
        manifest["status"] = "COMMITTED"
        manifest["recovery"] = {
            "strategy": "CONFIRM_COMMIT",
            "basis": ["Every target matches the staged after-image digest."],
        }
        manifest["applied"] = [operation["path"] for operation in manifest["operations"]]
        manifest["updated_at"] = _now()
        _atomic_write_yaml(manifest_path, manifest)
        return _compact_terminal_manifest(root, manifest_path, manifest)

    basis = [f"{operation['path']}={state}" for operation, state in zip(manifest["operations"], states)]
    if any(state == "OTHER" for state in states):
        manifest["status"] = "RECOVERY_REQUIRED"
        manifest["recovery"] = {
            "strategy": "ROLLBACK",
            "basis": basis + ["Automatic rollback refused because at least one target matches neither before nor after digest."],
        }
        manifest["updated_at"] = _now()
        _atomic_write_yaml(manifest_path, manifest)
        raise TransactionError(
            "transaction recovery found external/unknown target changes; manual reconciliation is required"
        )

    for operation in reversed(manifest["operations"]):
        target = repo_path(root, operation["path"], "transaction target")
        if operation["before_exists"]:
            backup = repo_path(root, str(operation["backup_path"]), "transaction backup path")
            if not backup.exists():
                raise TransactionError(f"cannot rollback {operation['path']}: backup is missing")
            _atomic_write_bytes(target, backup.read_bytes())
        elif target.exists():
            target.unlink()

    manifest["status"] = "ROLLED_BACK"
    manifest["recovery"] = {"strategy": "ROLLBACK", "basis": basis}
    manifest["updated_at"] = _now()
    _atomic_write_yaml(manifest_path, manifest)
    return _compact_terminal_manifest(root, manifest_path, manifest)


def recover_all(root: Path) -> list[dict[str, Any]]:
    results = []
    for path, manifest, error in incomplete_transactions(root):
        if error == "MISSING_MANIFEST":
            tx_dir = path.parent
            tx_id = tx_dir.name
            shutil.rmtree(tx_dir)
            results.append({
                "id": tx_id,
                "status": "ROLLED_BACK",
                "recovery": {
                    "strategy": "ROLLBACK",
                    "basis": ["Transaction had no manifest; canonical targets had not entered the apply phase."],
                },
            })
            continue
        if error:
            raise TransactionError(f"cannot parse transaction manifest {path}: {error}")
        results.append(recover(root, path))
    return results


def yaml_bytes(value: Any) -> bytes:
    return yaml.safe_dump(value, sort_keys=False).encode("utf-8")


def jsonl_bytes(events: list[dict[str, Any]]) -> bytes:
    return ("".join(json.dumps(item, sort_keys=True) + "\n" for item in events)).encode("utf-8")
