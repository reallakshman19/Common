"""Independent local review checks. Writes only within this reviewer directory."""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
assert ROOT == Path('/workspace/scratch/52eed2252c51/tmp/nd-adapter-forward/reviewer')
assert sys.dont_write_bytecode


def read_json(relative):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(name, value):
    target = ROOT / name
    assert target.parent == ROOT
    target.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


issued_paths = [ROOT / name for name in ('case.md', 'intent.json', 'plan.json', 'packet.json')]
issued_paths += sorted(path for path in (ROOT / 'inputs').rglob('*') if path.is_file())
assert all(path.resolve().is_relative_to(ROOT) for path in issued_paths)
before = {str(path.relative_to(ROOT)): sha(path) for path in issued_paths}
write_json('input-manifest-before.json', before)

intent = read_json('intent.json')
source_matches = []
for source in intent['sources']:
    actual = 'sha256:' + sha(ROOT / source['locator'])
    source_matches.append({
        'source_id': source['id'], 'locator': source['locator'],
        'issued_revision': source['revision'], 'observed_revision': actual,
        'matches_pinned_revision': None if source['revision'] is None else actual == source['revision'],
    })

# Execute the inspected supplied implementation, using an independently authored
# reference oracle. Do not run either supplied check script.
source_path = ROOT / 'inputs/worker/source.py'
spec = importlib.util.spec_from_file_location('reviewed_receive_source', source_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
probe_output = read_json('inputs/worker/probe-output.json')
observed_orders = []
for sequence in [('NEW', 'OLD'), ('OLD', 'NEW')]:
    state = {'current_revision': 10, 'result': None}
    ideal = None
    events = []
    for index, label in enumerate(sequence, 1):
        revision = {'NEW': 10, 'OLD': 9}[label]
        previous = deepcopy(state)
        current = revision == previous['current_revision']
        if current:
            ideal = label
        returned = module.receive(state, revision, label)
        events.append({
            'completion_index': index, 'request_name': label,
            'request_revision': revision, 'state_before': previous,
            'state_after': deepcopy(state), 'expected_result': ideal,
            'invariant_holds': state['result'] == ideal,
            'current_completion_published': state['result'] == label if current else None,
            'obsolete_completion_preserved_result': state['result'] == previous['result'] if not current else None,
            'returned_same_state': returned is state,
        })
    supplied = next(row for row in probe_output['results'] if row['completion_order'] == list(sequence))
    match = all(
        actual['state_before'] == supplied_event['state_before']
        and actual['state_after'] == supplied_event['state_after']
        and actual['expected_result'] == supplied_event['expected_result_under_invariant']
        and actual['invariant_holds'] == supplied_event['current_result_invariant_holds']
        for actual, supplied_event in zip(events, supplied['events'], strict=True)
    )
    observed_orders.append({
        'completion_order': list(sequence), 'events': events,
        'first_violation': next(row['completion_index'] for row in events if not row['invariant_holds']),
        'final_state': deepcopy(state), 'matches_supplied_trace': match,
    })

# Recompute from the original givens using exact decimal arithmetic rather than
# executing the supplied Fraction script or accepting its PASS field.
u, gravity = Decimal('18'), Decimal('9')
acceleration = -gravity
times = [Decimal(value) for value in ('0', '1', '1.9', '2', '2.1', '3')]
arithmetic = read_json('inputs/specialist/arithmetic.json')
computed_rows = []
for time, supplied in zip(times, arithmetic['rows'], strict=True):
    velocity = u - gravity * time
    height = u * time - gravity * time * time / 2
    matches = (
        Fraction(time) == Fraction(supplied['time_s'])
        and Fraction(velocity) == Fraction(supplied['velocity_m_per_s'])
        and Fraction(height) == Fraction(supplied['displacement_m'])
        and Fraction(acceleration) == Fraction(supplied['acceleration_m_per_s_squared'])
    )
    computed_rows.append({'time_s': str(time), 'velocity_m_per_s': str(velocity),
                          'height_m': str(height), 'acceleration_m_per_s_squared': str(acceleration),
                          'matches_supplied_row': matches})
turning_time = u / gravity
height_from_velocity_relation = u * u / (2 * gravity)
height_at_top = u * turning_time - gravity * turning_time * turning_time / 2
around_top_rate = ((u - gravity * Decimal('2.1')) - (u - gravity * Decimal('1.9'))) / Decimal('.2')
held_acceleration = (Decimal(0) - Decimal(0)) / Decimal('.2')
physics_checks = {
    'turning_time_2_s': turning_time == Decimal(2),
    'velocity_at_top_zero': u - gravity * turning_time == 0,
    'height_18_m_by_two_relations': height_from_velocity_relation == height_at_top == 18,
    'velocity_rate_through_top_minus_9': around_top_rate == acceleration == -9,
    'all_six_supplied_rows_match': all(row['matches_supplied_row'] for row in computed_rows),
    'held_interval_acceleration_zero': held_acceleration == 0,
    'zero_instant_velocity_does_not_imply_zero_acceleration': acceleration != held_acceleration,
}
specialist_plan = read_json('inputs/specialist/plan.json')
handover = specialist_plan['handover']['next_action']
physics = {
    'method': 'Independent exact Decimal arithmetic from case givens, with rational comparison of recorded values.',
    'rows': computed_rows, 'turning_time_s': str(turning_time),
    'turning_height_m': str(height_at_top), 'checks': physics_checks,
    'analytic_acceleration': 'd(18 - 9t)/dt = -9 m/s^2 at every free-flight time, including t=2 s.',
    'units': ['(m/s^2)*s = m/s', '(m/s)*s = m', '(m/s^2)*s^2 = m', '(m/s)/s = m/s^2'],
    'held_model': 'Velocity is constant over an interval; upward holding force balances downward weight.',
    'issued_handover': handover,
    'handover_20_m_per_s_conflicts_with_case_18': '20 m/s' in handover,
    'if_wrong_20_used': {'turning_time_s_exact': str(Fraction(20, 9)),
                        'turning_height_m_exact': str(Fraction(200, 9))},
}

envelopes = []
for role, worksheet_name in [('worker', 'receive-worksheet.json'), ('specialist', 'reconciliation.json')]:
    base = ROOT / 'inputs' / role
    report = json.loads((base / 'return.json').read_text())
    native = report['native_report']
    native_path = base / native['locator']
    old = json.loads((base / worksheet_name).read_text())
    new = read_json(role + '-intake-check.json')
    missing = sorted({locator for attempt in report['attempts'] for locator in attempt['evidence']
                      if not (base / locator).is_file()})
    envelopes.append({
        'role': role, 'native_locator': native['locator'],
        'native_exact_bytes_match': native['content'].encode('utf-8') == native_path.read_bytes(),
        'native_content_sha256': hashlib.sha256(native['content'].encode('utf-8')).hexdigest(),
        'recomputed_intake_status': new['status'],
        'changed_shared_worksheet_fields': sorted(key for key in old.keys() & new.keys() if old[key] != new[key]),
        'new_only_worksheet_keys': sorted(new.keys() - old.keys()),
        'old_only_worksheet_keys': sorted(old.keys() - new.keys()),
        'evidence_locators_not_supplied_in_copy': missing,
        'independent_candidates_from_intake': new['independent_candidates'],
        'sources_unpinned_in_original_intent': new['unpinned_observations'],
    })

after = {str(path.relative_to(ROOT)): sha(path) for path in issued_paths}
unchanged = before == after
write_json('input-manifest-after.json', after)
checks = {
    'all_pinned_review_source_revisions_match': all(row['matches_pinned_revision'] is not False for row in source_matches),
    'all_worker_trace_events_reproduced': all(row['matches_supplied_trace'] for row in observed_orders),
    'two_obsolete_publications_observed': sum(not event['invariant_holds'] for row in observed_orders for event in row['events']) == 2,
    'both_current_completions_succeed': all(event['current_completion_published'] is not False for row in observed_orders for event in row['events']),
    'physics_recomputed': all(physics_checks.values()),
    'native_snapshots_exact': all(row['native_exact_bytes_match'] for row in envelopes),
    'no_shared_worksheet_field_changes': all(not row['changed_shared_worksheet_fields'] for row in envelopes),
    'all_issued_inputs_unchanged': unchanged,
}
output = {
    'purpose': 'Independent reviewer reproduction; no product or learner acceptance.',
    'runtime': {'python': sys.version, 'bytecode_disabled': sys.dont_write_bytecode,
                'host_model': 'UNKNOWN', 'reasoning_effort': 'UNKNOWN', 'formal_qualification': 'UNKNOWN'},
    'input_file_count': len(issued_paths), 'source_revisions': source_matches,
    'worker': {'actual_calls': 4, 'source_sha256_before': before['inputs/worker/source.py'],
               'source_sha256_after': after['inputs/worker/source.py'], 'orders': observed_orders},
    'physics': physics, 'envelopes': envelopes, 'checks': checks,
    'result': 'REVIEW_CHECKS_COMPLETED' if all(checks.values()) else 'REVIEW_CHECK_DISCREPANCY',
    'limits': ['No original execution or actor authentication.',
               'Original packets and some supporting receipts were not supplied.',
               'The specialist self-check remains distinct from this independent recomputation.',
               'No implementation, transfer problem, learner contact, publication or external execution.'],
}
write_json('independent-checks.json', output)
print(json.dumps({'result': output['result'], 'input_file_count': len(issued_paths),
                  'checks': checks, 'physics_checks': physics_checks,
                  'first_violations': [row['first_violation'] for row in observed_orders]}, indent=2))
raise SystemExit(0 if all(checks.values()) else 1)
