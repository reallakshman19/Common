"""Preparatory CSV input reader for V3.2 R01 source lab (not admitted evidence)."""
from __future__ import annotations
import csv
from io import StringIO


class CsvInputError(ValueError):
    """Stable local negative-oracle error; not native DELP status."""


def read_csv(text: str) -> list[dict[str, str]]:
    """Read strict CSV into source-preserving value dicts; enforce unique IDs.

    Contract is assistant-authored from Common #285/#282 R01 descriptions;
    compare against the original starter tests before reuse in any real lab.
    """
    if not isinstance(text, str):
        raise CsvInputError("INPUT_TEXT_REQUIRED")
    rows = []
    seen = set()
    try:
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if not header:
            raise CsvInputError("MISSING_HEADER")
        if any(not field for field in header):
            raise CsvInputError("EMPTY_HEADER_COLUMN")
        if len(set(header)) != len(header):
            raise CsvInputError("DUPLICATE_HEADER")
        if "id" not in header:
            raise CsvInputError("MISSING_ID_COLUMN")
        id_index = header.index("id")
        for row in reader:
            if len(row) != len(header):
                raise CsvInputError("ROW_WIDTH_MISMATCH")
            value = row[id_index]
            if not value.strip():
                raise CsvInputError("EMPTY_ID")
            if value in seen:
                raise CsvInputError("DUPLICATE_ID")
            seen.add(value)
            rows.append(dict(zip(header, row)))
    except csv.Error as exc:
        raise CsvInputError("MALFORMED_CSV") from exc
    return rows
