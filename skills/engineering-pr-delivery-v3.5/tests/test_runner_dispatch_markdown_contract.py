"""Regression: Runner dispatch Markdown is an unambiguous two-column source-identity contract.

Prevents a malformed cell from silently combining a current-repository identity
with a historical issue identifier. Text checks do not authenticate the provider:
an external current-repo GET and read-scope attestation remain mandatory.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "relay/CONTINUITY/TEMPLATES/RUNNER_DISPATCH_REQUEST.md"


def parse_dispatch_fields(source: str) -> dict[str, str]:
    lines = source.splitlines()
    header = "| Required field | Source / permitted value |"
    if lines.count(header) != 1:
        raise ValueError("dispatch table header must occur exactly once")
    offset = lines.index(header)
    if lines[offset + 1].strip() != "| --- | --- |":
        raise ValueError("dispatch table must have an exact two-column separator")
    fields: dict[str, str] = {}
    for row in lines[offset + 2:]:
        if not row.strip():
            break
        if not row.startswith("| ") or not row.endswith(" |") or row.count("|") != 3:
            raise ValueError(f"dispatch table row must contain exactly two cells: {row!r}")
        key, value = (cell.strip() for cell in row.strip(" |").split("|"))
        if not key or not value:
            raise ValueError("dispatch table field and value must be nonempty")
        if key in fields:
            raise ValueError(f"duplicate dispatch field: {key}")
        fields[key] = value
    if not fields:
        raise ValueError("dispatch table contains no fields")
    return fields


class RunnerDispatchMarkdownContractTests(unittest.TestCase):
    def test_real_template_has_unambiguous_source_identity_fields(self):
        fields = parse_dispatch_fields(TEMPLATE.read_text(encoding="utf-8"))
        for key in (
            "Parent issue / existing leaf or Local responsibility",
            "Old-repository lineage (if any)",
            "Current issue binding receipt",
            "Episode and idempotency key",
            "External launch-capable operator",
            "Launch/isolation mechanism",
            "Actual B session already launched?",
        ):
            self.assertIn(key, fields)
        self.assertIn("provider-fetched", fields["Parent issue / existing leaf or Local responsibility"])
        self.assertIn("old issue refs remain historical", fields["Parent issue / existing leaf or Local responsibility"])
        self.assertIn("provider GET/identity", fields["Current issue binding receipt"])
        self.assertIn("HOLD_REPOSITORY_IDENTITY", fields["Current issue binding receipt"])
        self.assertIn("a numeric TX ID alone is insufficient", fields["Current issue binding receipt"])
        self.assertIn("not proof of the same new-repo object", fields["Old-repository lineage (if any)"])

    def test_merged_cells_fail_closed(self):
        good = TEMPLATE.read_text(encoding="utf-8")
        old = "| Current issue binding receipt |"
        self.assertEqual(good.count(old), 1)
        broken = good.replace(old, "| Parent issue / existing leaf or Local responsibility | duplicated || Current issue binding receipt |")
        with self.assertRaisesRegex(ValueError, "exactly two cells"):
            parse_dispatch_fields(broken)

    def test_duplicate_identity_field_fails_closed(self):
        good = TEMPLATE.read_text(encoding="utf-8")
        after = "| Old-repository lineage (if any) |"
        source_row = next(x for x in good.splitlines() if x.startswith(after))
        broken = good.replace(source_row, source_row + "\n" + source_row)
        with self.assertRaisesRegex(ValueError, "duplicate dispatch field"):
            parse_dispatch_fields(broken)

    def test_missing_table_header_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "header must occur exactly once"):
            parse_dispatch_fields("# A valid-looking document without the table\n")


if __name__ == "__main__":
    unittest.main()
