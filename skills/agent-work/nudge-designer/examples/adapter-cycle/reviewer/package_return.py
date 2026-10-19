"""Package the unchanged native review against the CLI-issued binding."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
assert ROOT == Path('/workspace/scratch/52eed2252c51/tmp/nd-adapter-forward/reviewer')
assert sys.dont_write_bytecode


def load(name):
    return json.loads((ROOT / name).read_text())


binding = load('issued-binding.json')
assert binding == load('packet.json')['binding']
checks = load('independent-checks.json')
assert all(checks['checks'].values())
note = (ROOT / 'review.md').read_text(encoding='utf-8')
report = {
    'binding': binding,
    'actor_id': 'R',
    'claimed_status': 'COMPLETE',
    'native_report': {'format': 'text/markdown', 'locator': 'review.md', 'revision': '1', 'content': note},
    'attempts': [
        {'id': 'A-READ', 'action': 'Read the issued review contract and all supplied worker/specialist artifacts; inspect permitted skill support.',
         'state': 'EXECUTED',
         'observed': 'Reviewed original cases, source, reports, study note, scripts, numeric output, issued intents/plans, envelopes and worksheets without reading original agents\u2019 other directories, worked examples or tests.',
         'evidence': ['case.md', 'intent.json', 'plan.json', 'packet.json', 'review.md']},
        {'id': 'A-COMPUTE', 'action': 'Run the independently authored local checker against the unchanged supplied receive function and original physics givens.',
         'state': 'EXECUTED',
         'observed': 'Exit 0. Four actual receive calls reproduce both stale publications and both valid current completions. Independent Decimal calculations match all six supplied rows: top at 2 s, rise 18 m, free-flight acceleration -9 m/s^2, held-at-rest acceleration zero. Eight review checks and seven numerical checks pass.',
         'evidence': ['independent_check.py', 'independent-checks.json', 'inputs/worker/source.py', 'inputs/worker/probe-output.json', 'inputs/specialist/arithmetic.json']},
        {'id': 'A-INTAKE', 'action': 'Validate the issued review intent/plan and recompute supplied worker and specialist return intakes using the skill CLI.',
         'state': 'EXECUTED',
         'observed': 'All three commands exit 0. Review intent/plan STRUCTURALLY_VALID; both supplied envelopes RETURN_RECORDED with unchanged native snapshots. Recomputed worksheets agree on all shared fields; current output additionally includes native_representation TEXT_SNAPSHOT.',
         'evidence': ['reviewer-validation.json', 'worker-intake-check.json', 'specialist-intake-check.json', 'independent-checks.json']},
        {'id': 'A-BIND', 'action': 'Run bind for N-REVIEW and compare the exact returned header with the issued packet binding.',
         'state': 'EXECUTED',
         'observed': 'Bind exits 0; issued-binding.json exactly equals packet.json binding. The return preserves review.md as exact UTF-8 text.',
         'evidence': ['issued-binding.json', 'packet.json', 'review.md', 'package_return.py']},
        {'id': 'A-PRESERVE', 'action': 'Hash every supplied file before and after independent checking.',
         'state': 'EXECUTED',
         'observed': 'All 22 supplied files have unchanged hashes; all six pinned review source revisions match. No issued intent, plan, packet, source or report was edited.',
         'evidence': ['input-manifest-before.json', 'input-manifest-after.json', 'independent-checks.json']},
        {'id': 'A-INTEGRATED', 'action': 'Implement repair, assess an actual learner, publish or accept an integrated outcome.',
         'state': 'NOT_RUN',
         'observed': 'These actions are outside the bounded local review. Source still violates the invariant; transfer material and actual learner evidence remain unresolved.',
         'evidence': ['case.md', 'review.md']},
    ],
    'findings': [
        {'kind': 'OBSERVATION', 'text': 'The diagnostic is substantiated by four independent actual calls: first violations at event 2 for NEW/OLD and event 1 for OLD/NEW; both current completions publish. This proves the supplied function violates the original invariant, not product acceptance.',
         'item_refs': ['R-REVIEW'], 'attempt_refs': ['A-READ', 'A-COMPUTE']},
        {'kind': 'OBSERVATION', 'text': 'The 18 m/s study note and all six recorded arithmetic rows agree with the stipulated model. Zero velocity at the top coexists with acceleration -9 m/s^2; supported rest has zero acceleration over an interval. Correct content does not prove learner understanding.',
         'item_refs': ['R-REVIEW', 'U-QUALIFICATION'], 'attempt_refs': ['A-READ', 'A-COMPUTE']},
        {'kind': 'ASSUMPTION_CONFLICT', 'text': 'The specialist issued plan handover uses 20 m/s while its original case and intent C-PHYSICS specify 18 m/s. The specialist correctly used 18 and reported drift. Preserve the issued snapshot and reconcile the working handover before reuse.',
         'item_refs': ['R-REVIEW'], 'attempt_refs': ['A-READ', 'A-COMPUTE']},
        {'kind': 'NEW_ISSUE', 'text': 'The original specialist intent F-PREREQ declares synthetic learner prerequisites and misconception beyond what its supplied case supports. Preserve this as a scenario assumption unless a source is supplied; do not treat it as learner evidence.',
         'item_refs': ['R-REVIEW', 'U-QUALIFICATION'], 'attempt_refs': ['A-READ']},
        {'kind': 'OBSERVATION', 'text': 'Copied envelopes pass current intake and native snapshots match exact bytes, but some historical evidence locators were not supplied. Intake and role labels establish no authenticated execution, independence, authority, formal qualification or integrated acceptance.',
         'item_refs': ['U-QUALIFICATION'], 'attempt_refs': ['A-INTAKE', 'A-BIND']},
        {'kind': 'OBSERVATION', 'text': 'All supplied input bytes remain unchanged; only reviewer-local artifacts were written.',
         'item_refs': ['C-LOCAL'], 'attempt_refs': ['A-PRESERVE']},
    ],
    'source_observations': [{'source_id': row['source_id'], 'revision': row['observed_revision']} for row in checks['source_revisions']],
    'contributors': ['R'],
    'unresolved': [
        'Original current-result implementation remains faulty; no repair or product integration acceptance was executed.',
        'CSV requirements remain independent, unspecified and unverified.',
        'The 20 m/s handover conflict and unsupported synthetic prerequisite provenance need Designer reconciliation in working revisions; issued inputs were preserved.',
        'N-TRANSFER material, actual learner understanding, transfer response, delayed retrieval and learning gain remain unestablished.',
        'Host model/reasoning configuration, formal domain qualification and authenticated review independence remain UNKNOWN or unverified.',
        'Original packets and some supporting receipts were not supplied; historical execution/packet-comparison claims and source authenticity cannot be authenticated from these copies.',
    ],
    'next_proposal': 'Designer reconciles the supported findings, preserves all issued history and prepares a corrected working handover with explicit scenario assumptions. Use the measured event traces to scope subsequent repair under actual authority, keep CSV independent, and separately prepare transfer material while leaving learner and integrated outcome acceptance unresolved.',
}
(ROOT / 'return.json').write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

prefix = 'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/workspace/scratch/52eed2252c51/tmp/br20-deps python -B '
cli = '/workspace/scratch/52eed2252c51/Common-nudge-designer/skills/nudge-designer/scripts/nudge_designer.py '
commands = [
    (cli + 'validate --intent intent.json --plan plan.json --out reviewer-validation.json', 'STRUCTURALLY_VALID; semantic quality NOT_MACHINE_VERIFIED.'),
    (cli + 'receive --intent inputs/worker/intent.json --plan inputs/worker/plan.json --report inputs/worker/return.json --out worker-intake-check.json', 'RETURN_RECORDED; no accepted outcomes or authenticated execution.'),
    (cli + 'receive --intent inputs/specialist/intent.json --plan inputs/specialist/plan.json --report inputs/specialist/return.json --out specialist-intake-check.json', 'RETURN_RECORDED; no accepted outcomes or authenticated execution.'),
    ('independent_check.py', 'REVIEW_CHECKS_COMPLETED; 8 review checks and 7 numerical checks passed; invariant violations reproduced.'),
    (cli + 'bind --intent intent.json --plan plan.json --nudge N-REVIEW --out issued-binding.json', 'Binding generated and exact packet match verified.'),
    ('package_return.py', 'Return constructed with exact native report and CLI-issued binding.'),
]
(ROOT / 'commands.json').write_text(json.dumps({'cwd': str(ROOT), 'commands': [
    {'command': prefix + command, 'exit_code': 0, 'observed': observed}
    for command, observed in commands
]}, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'return': 'return.json', 'native_report': 'review.md', 'packet_binding_matches': True,
                  'claimed_status': report['claimed_status'], 'model_configuration': 'UNKNOWN'}))
