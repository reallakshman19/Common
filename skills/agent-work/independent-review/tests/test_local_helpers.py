import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from review_records import check_files, read_json


class LocalChecks(unittest.TestCase):
    def test_original_bytes_mismatch_and_missing_are_independent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'original'
            raw = b'\xef\xbb\xbfA\r\nB\r\n'
            path.write_bytes(raw)
            records = [{'id': 'GOOD', 'local_path': 'original', 'sha256': hashlib.sha256(raw).hexdigest()},
                       {'id': 'BAD', 'local_path': 'original', 'sha256': hashlib.sha256(b'A\nB\n').hexdigest()},
                       {'id': 'MISSING', 'local_path': 'absent'}]
            report = check_files(records, directory)
            self.assertEqual([row['status'] for row in report], ['MATCH', 'MISMATCH', 'UNAVAILABLE'])
            self.assertEqual(path.read_bytes(), raw)

    def test_no_locator_fetch_or_embedded_command_execution(self):
        report = check_files([{'id': 'URL', 'locator': 'https://example.invalid/missing',
                               'command': 'do not execute me'}], ROOT)
        self.assertEqual(report[0]['status'], 'NOT_CHECKED')

    def test_path_escape_and_symlink_are_not_followed_outside_root(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'root'
            root.mkdir()
            (base / 'outside').write_bytes(b'outside')
            (root / 'link').symlink_to(base / 'outside')
            report = check_files([{'id': 'UP', 'local_path': '../outside'},
                                  {'id': 'LINK', 'local_path': 'link'},
                                  {'id': 'ABS', 'local_path': str(base / 'outside')}], root)
            self.assertEqual([row['status'] for row in report], ['UNAVAILABLE'] * 3)

    def test_symlink_loop_preserves_known_mismatch_and_later_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'valid').write_bytes(b'actual')
            (root / 'loop').symlink_to('loop')
            actual_hash = hashlib.sha256(b'actual').hexdigest()
            report = check_files([{'id': 'KNOWN_MISMATCH', 'local_path': 'valid', 'sha256': '0' * 64},
                                  {'id': 'LOOP', 'local_path': 'loop'},
                                  {'id': 'GOOD', 'local_path': 'valid', 'sha256': actual_hash}], root)
            self.assertEqual([row['status'] for row in report], ['MISMATCH', 'UNAVAILABLE', 'MATCH'])

    def test_json_duplicate_keys_and_nonfinite_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'record.json'
            for text in ('{"id":"one","id":"two"}', '{"x":NaN}', '{"x":Infinity}', '{"x":1e9999}'):
                path.write_text(text)
                with self.assertRaises(ValueError):
                    read_json(path)

    def test_all_cli_commands_work_without_other_skills_or_optional_packages(self):
        # -S excludes site-packages, demonstrating optional schema validation.
        case = ROOT / 'examples/records/case.json'
        result = ROOT / 'examples/records/result.json'
        commands = [('bind',), ('render',), ('validate', '--result', str(result)),
                    ('check-evidence', '--result', str(result), '--root', str(case.parent)),
                    ('compare', '--observations', str(case.parent / 'current.json'))]
        environment = dict(os.environ)
        environment.pop('PYTHONPATH', None)
        for command in commands:
            process = subprocess.run([sys.executable, '-B', '-S', str(ROOT / 'scripts/review.py'), command[0],
                                      str(case), *command[1:]], capture_output=True, text=True,
                                     env=environment, check=True)
            self.assertTrue(process.stdout)
            if command[0] == 'validate':
                report = json.loads(process.stdout)
                self.assertIn('SCHEMA_NOT_RUN', [row['code'] for row in report['issues']])

    def test_reported_inconsistency_is_advisory_not_an_admission_exit_code(self):
        case = ROOT / 'examples/records/case.json'
        result = read_json(ROOT / 'examples/records/result.json')
        result['review_type'] = 'SEPARATE_REVIEW'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'result.json'
            path.write_text(json.dumps(result))
            process = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/review.py'), 'validate',
                                      str(case), '--result', str(path)], capture_output=True, text=True)
        self.assertEqual(process.returncode, 0)
        self.assertIn('INDEPENDENCE_DECLARATION', process.stdout)

    def test_real_cli_byte_check_reads_all_fixture_and_report_files(self):
        case = ROOT / 'examples/records/case.json'
        process = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/review.py'), 'check-evidence',
                                  str(case), '--result', str(case.parent / 'result.json'),
                                  '--root', str(case.parent)], capture_output=True, text=True, check=True)
        observations = json.loads(process.stdout)['files']
        self.assertEqual([row['status'] for row in observations], ['MATCH'] * 4)

    def test_input_error_is_technical_and_does_not_claim_project_failure(self):
        process = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/review.py'), 'bind',
                                  str(ROOT / 'absent.json')], capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(json.loads(process.stderr)['project_decision'], 'NONE')


if __name__ == '__main__':
    unittest.main()
