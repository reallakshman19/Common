#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


HERE = Path(__file__).resolve().parents[1]
SCHEMAS = HERE / "schemas"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def dump_yaml(value: Any) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True)


def schema(name: str) -> dict[str, Any]:
    return load_yaml(SCHEMAS / f"{name}.schema.yaml")


def validate(name: str, value: Any, label: str | None = None) -> list[str]:
    validator = Draft202012Validator(schema(name), format_checker=FormatChecker())
    prefix = label or name
    errors: list[str] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        where = ".".join(str(part) for part in error.path)
        errors.append(f"{prefix}{'.' + where if where else ''}: {error.message}")
    return errors


def require_valid(name: str, value: Any, label: str | None = None) -> None:
    errors = validate(name, value, label)
    if errors:
        raise ValueError("; ".join(errors))
