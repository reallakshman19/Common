"""Verify final review packaging and preservation, with no writes outside here."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
assert ROOT == Path('/workspace/scratch/52eed2252c51/tmp/nd-adapter-forward/reviewer')
assert sys.dont_write_bytecode


def load(name):
    return json.loads((ROOT / name).read_text())


baseline = load('input-manifest-before.json')
actual = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in baseline}
returned = load('return.json')
worksheet = load('receive-worksheet.json')
native = (ROOT / 'review.md').read_bytes()
checks = {
    'all_22_supplied_files_unchanged': len(actual) == 22 and actual == baseline,
    'binding_matches_cli_and_issued_packet': returned['binding'] == load('issued-binding.json') == load('packet.json')['binding'],
    'native_report_exact_utf8_bytes': returned['native_report']['content'].encode('utf-8') == native,
    'worksheet_preserves_exact_native_report': worksheet['native_report'] == returned['native_report'],
    'worksheet_native_sha256_matches': worksheet['native_content_sha256'] == hashlib.sha256(native).hexdigest(),
    'return_recorded': worksheet['status'] == 'RETURN_RECORDED',
    'no_outcome_acceptance': worksheet['accepted_outcomes'] == [],
    'no_execution_or_authority_authentication': not worksheet['execution_verified'] and not worksheet['authority_verified'] and not worksheet['evidence_authenticated'],
    'no_scope_expansion_or_plan_mutation': not worksheet['scope_expanded'] and not worksheet['plan_modified'] and not worksheet['workflow_locked'],
    'no_source_discrepancies': worksheet['source_discrepancies'] == [] and worksheet['sources_not_observed'] == [],
    'all_review_attempt_evidence_available': all((ROOT / name).is_file() for attempt in returned['attempts'] for name in attempt['evidence']),
}
assert all(checks.values()), checks
result = {'status': 'PACKAGING_VERIFIED', 'checks': checks, 'input_hashes': actual,
          'unpinned_observations': worksheet['unpinned_observations'],
          'independence': worksheet['independence'],
          'native_content_sha256': worksheet['native_content_sha256'],
          'host_model': 'UNKNOWN', 'reasoning_effort': 'UNKNOWN', 'formal_qualification': 'UNKNOWN'}
(ROOT / 'final-checks.json').write_text(json.dumps(result, indent=2) + '\n')
commands = load('commands.json')
prefix = 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps python -B '
cli = '/workspace/scratch/52eed2252c51/Common-nudge-designer/skills/nudge-designer/scripts/nudge_designer.py '
commands['commands'].extend([
    {'command': prefix + cli + 'receive --intent intent.json --plan plan.json --report return.json --out receive-worksheet.json',
     'exit_code': 0, 'observed': 'RETURN_RECORDED; exact native text snapshot; no accepted outcomes or authentication.'},
    {'command': prefix + 'verify_packaging.py', 'exit_code': 0,
     'observed': 'PACKAGING_VERIFIED; all 11 final checks passed, including preservation of all 22 supplied files.'},
])
(ROOT / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'checks': checks,
                  'unpinned_observations': result['unpinned_observations'],
                  'independence': result['independence']}, indent=2))
