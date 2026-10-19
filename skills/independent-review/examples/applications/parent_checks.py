"""Verify this archived application evidence, not any real product acceptance."""

from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
RAW = ROOT.parent / 'raw'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


checks = []
for name in ('direct', 'guided', 'lesson'):
    for path in (ROOT / name / 'inputs').iterdir():
        assert sha(path) == sha(RAW / path.name), path
checks.append('All archived task-local inputs match the corresponding raw files.')

spec = importlib.util.spec_from_file_location('original_estimator', ROOT / 'direct/inputs/rate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
# Source-derived adjacent threshold witnesses, without using the worker formula.
assert module.estimate(9500, 499) == 9999
assert module.estimate(9500, 500) == 9050
assert 9500 + 500 == 10000  # No item discount permitted below 10000.
checks.append('Parent recomputation confirms delivery crossing contradicts the Owner rule.')
direct = load(ROOT / 'direct/out/check_evidence.json')
assert direct['existing_tests']['exit'] == 0
assert direct['inputs_unchanged']
assert len(direct['observations']) == 1058
assert sum(not row['passed'] for row in direct['observations']) == 277
assert all(sha(ROOT/'direct/inputs'/name) == value for name,value in direct['hashes_before'].items())
checks.append('Direct receipt counts, execution result and input hashes agree with preserved artifacts.')

custody = load(ROOT / 'guided/out/custody-log.json')
for record in custody['originals']:
    assert record['match'] and record['preserved_at_recheck']
    assert record['actual_sha256'] == sha(ROOT / 'guided/inputs' / record['id'])
negative = custody['negative_control']
assert negative['rejected'] and negative['sha256sum_check_exit'] == 1
assert negative['actual_sha256'] == sha(ROOT / 'guided/out/owner.altered.md')
assert negative['actual_sha256'] != negative['expected_sha256']
checks.append('Custody receipt matches original bytes and the retained altered copy is rejected.')

stop = Fraction(3, 2)
right = 3 * stop - stop**2
displacement = 3 * 4 - 4**2
distance = right + right - displacement
assert right == Fraction(9, 4) and displacement == -4 and distance == Fraction(17, 2)
assert sha(ROOT/'lesson/inputs/lesson.md') == sha(RAW/'lesson.md')
checks.append('Parent exact arithmetic corroborates lesson displacement and distance; source unchanged.')

result = {'checked_utc': datetime.now(timezone.utc).isoformat(), 'checks': checks,
          'limits': ['Synthetic local applications only; no LFEA/Writer2 acceptance.',
                     'No model/effort qualification, authenticated distinct principal or causal ROI established.']}
(ROOT / 'parent-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
