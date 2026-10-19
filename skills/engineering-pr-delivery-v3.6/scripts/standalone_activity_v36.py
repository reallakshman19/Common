"""Local ChatGPT-agent activity observations; no host installation or provider I/O."""
from datetime import datetime, timezone
import json
from pathlib import Path

SURFACES = ('chatgpt-agent', 'chatgpt-work', 'other', 'unknown')
EVENTS = ('session', 'turn-start', 'turn-end', 'github', 'gap', 'buddy-suggested')


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be nonempty text')
    return value


def stamp(value):
    parsed = datetime.fromisoformat(text(value, 'timestamp').replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp requires timezone')
    return parsed.astimezone(timezone.utc)


def union_seconds(intervals):
    end, total = None, 0.0
    for start, stop in sorted(intervals):
        if end is None or start >= end:
            total += (stop - start).total_seconds()
        elif stop > end:
            total += (stop - end).total_seconds()
        end = max(end, stop) if end is not None else stop
    return total


def session_of(rows):
    if not rows or not isinstance(rows[0], dict) or rows[0].get('event') != 'session':
        raise ValueError('first event must declare the agent episode and surface')
    first = rows[0]
    text(first.get('session_id'), 'session_id')
    if first.get('surface') not in SURFACES:
        raise ValueError('unknown agent surface')
    if first.get('observation') not in ('SELF_RECORDED', 'HOST_OBSERVED'):
        raise ValueError('declare actual observation basis')
    if first['observation'] == 'HOST_OBSERVED':
        text(first.get('source'), 'actual host trace source')
    return first


def consume(row, at, state):
    kind = row['event']
    if kind in ('turn-start', 'turn-end'):
        turn = text(row.get('turn_id'), 'turn_id')
        if kind == 'turn-start':
            if turn in state['open']:
                raise ValueError('turn already active')
            state['open'][turn] = at
        else:
            if turn not in state['open']:
                raise ValueError('turn-end has no observed start')
            state['intervals'].append((state['open'].pop(turn), at))
    elif kind == 'github':
        text(row.get('tool'), 'GitHub tool name')
        if row.get('outcome') not in ('success', 'failure', 'unknown'):
            raise ValueError('GitHub outcome must be success/failure/unknown')
        state['calls'] += 1
        if isinstance(row.get('turn_id'), str) and row['turn_id'].strip():
            state['turns'].add(row['turn_id'])
        else:
            state['gaps'].append('GitHub call has no observed turn identity')
    elif kind == 'gap':
        state['gaps'].append(text(row.get('reason'), 'gap reason'))
    elif kind == 'buddy-suggested':
        text(row.get('reference'), 'actual suggestion reference')
        if len(state['turns']) > 5 or union_seconds(state['intervals']) > 35 * 60:
            state['suggested'] = True


def summarize(rows):
    """Metrics are observed lower bounds, not proof of complete platform telemetry."""
    first = session_of(rows)
    state = {'open': {}, 'intervals': [], 'turns': set(), 'calls': 0,
             'gaps': [], 'suggested': False}
    previous = stamp(first.get('at'))
    for row in rows[1:]:
        if not isinstance(row, dict) or row.get('event') not in EVENTS or row['event'] == 'session':
            raise ValueError('invalid event or attempted episode reset')
        at = stamp(row.get('at'))
        if at < previous:
            raise ValueError('event clock/order moved backwards')
        consume(row, at, state)
        previous = at
    if state['calls'] and not state['intervals'] and not state['open']:
        state['gaps'].append('active-turn duration has not been observed')
    minutes = union_seconds(state['intervals']) / 60
    crossed = len(state['turns']) > 5 or minutes > 35
    applies = None if first['surface'] == 'unknown' else first['surface'] == 'chatgpt-agent'
    incomplete = bool(state['gaps'] or state['open'])
    return {'session_id': first['session_id'], 'surface': first['surface'],
            'policy_applies': applies, 'applicability': 'UNKNOWN' if applies is None else 'APPLIES' if applies else 'EXEMPT',
            'observation': first['observation'],
            'observation_authentication': 'NOT_ESTABLISHED_BY_THIS_LOCAL_HELPER',
            'github_tool_calls_observed': state['calls'],
            'github_access_turns_observed': len(state['turns']),
            'closed_active_minutes_observed': round(minutes, 6),
            'open_turns': sorted(state['open']), 'gaps': state['gaps'],
            'coverage': 'INCOMPLETE' if incomplete else 'RECORDED_ONLY',
            'threshold_state': 'CROSSED_OBSERVED' if crossed else 'UNKNOWN' if incomplete else 'NOT_OBSERVED',
            'threshold_crossed_observed': crossed,
            'buddy_suggestion_due': bool(applies and crossed and not state['suggested']),
            'suggestion_recorded_after_threshold': state['suggested'],
            'action': 'SUGGEST_BUDDY_RUNNER' if applies and crossed and not state['suggested'] else 'NONE',
            'automatic_handover': False, 'owner_accepted': False}


def parse_log(raw):
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    summarize(rows)
    return rows


def read_log(path):
    return parse_log(Path(path).read_bytes())


def append_event(path, row):
    """Append via this CLI; an agent-writable file is not a tamper-proof host log."""
    path = Path(path)
    if path.is_symlink():
        raise ValueError('activity log must not be a symlink')
    rows = read_log(path) if path.exists() else []
    result = summarize(rows + [row])
    with path.open('a', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
    return result


def utc_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
