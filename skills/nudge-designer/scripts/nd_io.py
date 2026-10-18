"""Strict local data handling; no provider reads, execution or authority checks."""
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlsplit


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def _constant(value):
    raise ContractError("non-finite JSON number: " + value)


def _float(value):
    number = float(value)
    require(math.isfinite(number), "non-finite JSON number: " + value)
    return number


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_float)
    except (OSError, ValueError) as error:
        raise ContractError(str(error)) from error


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as error:
        raise ContractError("invalid canonical JSON: " + str(error)) from error


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def indexed(rows, label):
    result = {}
    for row in rows:
        key = row["id"]
        require(key not in result, "duplicate " + label + " ID: " + key)
        result[key] = row
    return result


def references(values, known, label):
    for value in values:
        require(value in known, "unknown " + label + " reference: " + str(value))


def acyclic(edges, label):
    """Validate parent/dependency graphs without recursive Python stack limits."""
    state = {}
    for start in edges:
        if state.get(start) == 2:
            continue
        stack = [(start, False)]
        while stack:
            node, leaving = stack.pop()
            if leaving:
                state[node] = 2
                continue
            require(state.get(node) != 1, label + " cycle at " + node)
            if state.get(node) == 2:
                continue
            state[node] = 1
            stack.append((node, True))
            stack.extend((neighbor, False) for neighbor in edges[node])


def safe_locator(value):
    """Check display syntax only. Never dereference a locator or authorize access."""
    if value is None:
        return
    require(not any(ord(c) < 32 or ord(c) == 127 for c in value), "unsafe source locator")
    if "://" not in value:
        require(not value.lower().startswith(("javascript:", "data:", "mailto:")),
                "unsafe source locator")
        return
    try:
        parts = urlsplit(value)
        require(parts.scheme in ("https", "skill") and bool(parts.netloc), "unsafe source locator")
        require(parts.username is None and parts.password is None, "credential-bearing source locator")
        _ = parts.port
    except ValueError as error:
        raise ContractError("invalid source locator") from error


def quoted(value):
    """Keep source multiline prose as a single quoted data value in Markdown."""
    return json.dumps(value, ensure_ascii=False).replace("`", "\\u0060").replace("<", "\\u003c")
