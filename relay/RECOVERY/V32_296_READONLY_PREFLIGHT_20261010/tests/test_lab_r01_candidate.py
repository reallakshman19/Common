"""Preparatory R01 CSV-input oracle reconstructed from #285/#282.

These are NEW assistant-authored tests of the parent-documented intent, NOT the
unavailable precommitted nine tests from relay-v32-e2e-lab-starter.zip.
Their success cannot qualify the old lab, its Owner graph, or native V3.2 E.
"""
from pathlib import Path
import sys
import unittest

CANDIDATE = Path(__file__).resolve().parents[1] / "lab_r01_candidate"
sys.path.insert(0, str(CANDIDATE))
from csv_input import CsvInputError, read_csv  # intentionally RED until module exists


class R01PreparatoryInputContract(unittest.TestCase):
    def test_u01_reject_duplicate_ids(self):
        with self.assertRaisesRegex(CsvInputError, "DUPLICATE_ID"):
            read_csv("id,value\nA,first\nA,second\n")

    def test_u01_accept_distinct_ids(self):
        self.assertEqual([r["id"] for r in read_csv("id,value\nA,first\nB,second\n")],
                         ["A", "B"])

    def test_u01_reject_blank_id(self):
        with self.assertRaisesRegex(CsvInputError, "EMPTY_ID"):
            read_csv("id,value\n,empty\n")

    def test_u02_reject_absent_header(self):
        with self.assertRaisesRegex(CsvInputError, "MISSING_HEADER"):
            read_csv("")

    def test_u02_require_id_column(self):
        with self.assertRaisesRegex(CsvInputError, "MISSING_ID_COLUMN"):
            read_csv("name,value\nA,foo\n")

    def test_u02_reject_duplicate_columns(self):
        with self.assertRaisesRegex(CsvInputError, "DUPLICATE_HEADER"):
            read_csv("id,value,value\nA,foo,bar\n")

    def test_u03_preserve_csv_quoted_values_and_order(self):
        rows = read_csv('id,value,remark\nB,"two, parts","  spaced  "\nA,one,"x"\n')
        self.assertEqual(rows, [
            {"id": "B", "value": "two, parts", "remark": "  spaced  "},
            {"id": "A", "value": "one", "remark": "x"},
        ])

    def test_u03_preserve_newlines_inside_quoted_fields(self):
        rows = read_csv('id,note\nA,"one\ntwo"\n')
        self.assertEqual(rows[0]["note"], "one\ntwo")

    def test_u03_reject_short_row(self):
        with self.assertRaisesRegex(CsvInputError, "ROW_WIDTH_MISMATCH"):
            read_csv("id,value\nA\n")

    def test_u03_reject_unclosed_quote(self):
        with self.assertRaisesRegex(CsvInputError, "MALFORMED_CSV"):
            read_csv('id,value\nA,"unclosed\n')


if __name__ == "__main__":
    unittest.main()
