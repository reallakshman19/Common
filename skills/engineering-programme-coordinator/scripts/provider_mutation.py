#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from coordlib import load_yaml, validate as schema_validate


OPERATION_POLICY = {
    "CREATE_ISSUE": ("CREATE_ONCE", "ISSUE"),
    "PUBLISH_COMMENT": ("CREATE_ONCE", "COMMENT"),
    "CREATE_PULL_REQUEST": ("CREATE_ONCE", "PULL_REQUEST"),
    "UPDATE_ISSUE": ("MUTATE_EXISTING_ONCE", "ISSUE"),
    "UPDATE_PULL_REQUEST": ("MUTATE_EXISTING_ONCE", "PULL_REQUEST"),
    "UPDATE_REF": ("MUTATE_EXISTING_ONCE", "REF"),
    "MERGE_PULL_REQUEST": ("MUTATE_EXISTING_ONCE", "PULL_REQUEST"),
}


def canonical_provider_key(identity: dict[str, Any]) -> str:
    material = [
        identity["programme_or_parent_id"],
        identity["prd_id"],
        identity["resource_kind"],
        identity["mutation_slot"],
    ]
    encoded = json.dumps(
        material,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return "pm:v1:" + hashlib.sha256(encoded).hexdigest()


def _action(action_type: str, reason_code: str) -> dict[str, str]:
    return {"type": action_type, "reason_code": reason_code}


def derive_provider_action(value: dict[str, Any]) -> dict[str, str]:
    mutation = value["mutation"]
    lookup = value["lookup"]
    readback = value["readback"]

    if not lookup["performed"]:
        return _action("LOOKUP", "LOOKUP_REQUIRED")

    matches = lookup["matches"]
    if len(matches) > 1:
        return _action("RECONCILE_DUPLICATES", "DUPLICATE_MACHINE_IDENTITY")

    if readback["performed"]:
        if not readback["found"]:
            return _action("RECONCILE_MISSING_TARGET", "TARGET_NOT_FOUND")

        expected_key = value["identity"]["canonical_key"]
        expected_digest = mutation["payload_digest"]
        if (
            readback["canonical_key"] != expected_key
            or readback["payload_digest"] != expected_digest
        ):
            return _action("RECONCILE_MISMATCH", "READBACK_MISMATCH")

        if len(matches) == 1 and readback["provider_id"] != matches[0]["provider_id"]:
            return _action("RECONCILE_MISMATCH", "READBACK_MISMATCH")

        if (
            mutation["provider_id"] is not None
            and readback["provider_id"] != mutation["provider_id"]
        ):
            return _action("RECONCILE_MISMATCH", "READBACK_MISMATCH")

        return _action("COMPLETE", "TRANSACTION_COMPLETE")

    # Once a provider mutation was attempted, no retry path may emit mutation again.
    if mutation["attempted"]:
        return _action("READBACK_AFTER_MUTATION", "MUTATION_READBACK_REQUIRED")

    if len(matches) == 1:
        if mutation["class"] == "CREATE_ONCE":
            return _action("READBACK_EXISTING", "EXISTING_RESOURCE_REUSE")
        return _action("MUTATE_ONCE", "MUTATION_ALLOWED")

    if mutation["class"] == "CREATE_ONCE":
        return _action("CREATE_ONCE", "CREATE_ALLOWED")

    return _action("RECONCILE_MISSING_TARGET", "TARGET_NOT_FOUND")


def semantic_errors(value: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    identity = value["identity"]
    mutation = value["mutation"]
    lookup = value["lookup"]
    readback = value["readback"]

    expected_key = canonical_provider_key(identity)
    if identity["canonical_key"] != expected_key:
        errors.append("identity.canonical_key does not match machine-derived provider key")

    expected_class, expected_kind = OPERATION_POLICY[mutation["operation"]]
    if mutation["class"] != expected_class:
        errors.append(
            f"operation {mutation['operation']} requires mutation class {expected_class}"
        )
    if identity["resource_kind"] != expected_kind:
        errors.append(
            f"operation {mutation['operation']} requires resource_kind {expected_kind}"
        )

    if not lookup["performed"] and lookup["matches"]:
        errors.append("lookup.matches must be empty before lookup is performed")
    for match in lookup["matches"]:
        if match["canonical_key"] != expected_key:
            errors.append("lookup match canonical_key differs from transaction identity")

    if mutation["attempted"]:
        if not lookup["performed"]:
            errors.append("provider mutation cannot be attempted before lookup")
        if not mutation["attempt_id"]:
            errors.append("attempted provider mutation requires attempt_id")
        if len(lookup["matches"]) > 1:
            errors.append("provider mutation cannot be attempted with duplicate lookup matches")
        if mutation["class"] == "CREATE_ONCE" and len(lookup["matches"]) == 1:
            errors.append("CREATE_ONCE cannot be attempted when lookup found an existing resource")
        if mutation["class"] == "MUTATE_EXISTING_ONCE" and len(lookup["matches"]) == 0:
            errors.append("MUTATE_EXISTING_ONCE cannot be attempted without a lookup target")
    else:
        if mutation["attempt_id"] is not None:
            errors.append("unattempted provider mutation cannot carry attempt_id")
        if mutation["provider_id"] is not None:
            errors.append("unattempted provider mutation cannot carry provider_id")

    if readback["performed"]:
        if not lookup["performed"]:
            errors.append("provider readback cannot precede lookup")
        if readback["found"]:
            if not readback["provider_id"]:
                errors.append("found readback requires provider_id")
            if not readback["canonical_key"]:
                errors.append("found readback requires canonical_key")
            if not readback["payload_digest"]:
                errors.append("found readback requires payload_digest")
        else:
            if any(
                item is not None
                for item in (
                    readback["provider_id"],
                    readback["canonical_key"],
                    readback["payload_digest"],
                )
            ):
                errors.append("not-found readback cannot carry provider observation fields")
    else:
        if readback["found"]:
            errors.append("unperformed readback cannot claim found=true")
        if any(
            item is not None
            for item in (
                readback["provider_id"],
                readback["canonical_key"],
                readback["payload_digest"],
            )
        ):
            errors.append("unperformed readback cannot carry provider observation fields")

    derived = derive_provider_action(value)
    if value["next_action"] != derived:
        errors.append(
            "stored next_action must exactly equal transaction-derived next_action "
            f"(stored={value['next_action']!r}, derived={derived!r})"
        )

    return errors


def validate_provider_mutation(
    value: Any,
    label: str = "provider-mutation",
) -> list[str]:
    errors = schema_validate("provider-mutation", value, label)
    if errors:
        return errors
    if not isinstance(value, dict):
        return [f"{label}: provider mutation must be an object"]
    return [f"{label}: {error}" for error in semantic_errors(value)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a deterministic provider mutation transaction."
    )
    parser.add_argument("path")
    args = parser.parse_args()

    path = Path(args.path)
    value = load_yaml(path)
    errors = validate_provider_mutation(value, path.name)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"OK: provider mutation: {path}; next={derive_provider_action(value)['type']}")


if __name__ == "__main__":
    main()
