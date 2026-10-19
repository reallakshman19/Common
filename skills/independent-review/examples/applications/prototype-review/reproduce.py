"""Read-only reproductions against the reviewed independent-review prototype."""

from copy import deepcopy
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/scratch/52eed2252c51/Common-independent-review/skills/independent-review')
OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
OUT.mkdir(parents=True, exist_ok=True)
if (OUT / 'duplicate-result.json').exists() or (OUT / 'loop-result.json').exists():
    raise SystemExit('Preserve existing review receipts; pass a new output directory to rerun.')
sys.path.insert(0, str(ROOT / 'scripts'))
from review_records import check_files, compare_candidates, read_json, schema_check


def cli(*args):
    process = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/review.py'), *args],
                             capture_output=True, text=True)
    return {'exit_code': process.returncode, 'stdout': process.stdout, 'stderr': process.stderr}


case = read_json(ROOT / 'examples/records/case.json')
duplicate = deepcopy(case['candidates'][0])
duplicate['revision'] = 'fixture-r2'
case['candidates'].append(duplicate)
observations = [deepcopy(duplicate)]
(OUT / 'duplicate-case.json').write_text(json.dumps(case, indent=2) + '\n')
(OUT / 'duplicate-current.json').write_text(json.dumps(observations, indent=2) + '\n')
duplicate_result = {
    'schema_check': schema_check(case),
    'direct_compare': compare_candidates(case, observations),
    'cli': cli('compare', str(OUT / 'duplicate-case.json'),
               '--observations', str(OUT / 'duplicate-current.json')),
}
(OUT / 'duplicate-result.json').write_text(json.dumps(duplicate_result, indent=2) + '\n')

files = OUT / 'loop-files'
files.mkdir(exist_ok=True)
(files / 'good.txt').write_bytes(b'good\n')
loop = files / 'loop'
if not loop.is_symlink():
    loop.symlink_to('loop')
records = [
    {'id': 'KNOWN_BAD', 'local_path': 'good.txt', 'sha256': '0' * 64},
    {'id': 'LOOP', 'local_path': 'loop'},
    {'id': 'LATER_GOOD', 'local_path': 'good.txt',
     'sha256': hashlib.sha256(b'good\n').hexdigest()},
]
try:
    local_result = {'observations': check_files(records, files)}
except Exception as error:
    local_result = {'exception_type': type(error).__name__, 'exception': str(error)}
loop_case = read_json(ROOT / 'examples/records/case.json')
loop_case['candidates'][0]['local_path'] = 'good.txt'
loop_case['candidates'][0]['sha256'] = '0' * 64
loop_case['sources'][0]['local_path'] = 'loop'
(OUT / 'loop-case.json').write_text(json.dumps(loop_case, indent=2) + '\n')
loop_result = {
    'direct_check': local_result,
    'cli': cli('check-evidence', str(OUT / 'loop-case.json'), '--root', str(files)),
}
(OUT / 'loop-result.json').write_text(json.dumps(loop_result, indent=2) + '\n')
print(json.dumps({'duplicate_identity': duplicate_result, 'symlink_loop': loop_result}, indent=2))
