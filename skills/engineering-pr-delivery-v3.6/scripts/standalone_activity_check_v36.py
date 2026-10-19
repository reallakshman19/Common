"""Environment-scoped activity duty for the standalone pre-DONE declaration."""
import hashlib
import re
from pathlib import Path
from standalone_activity_v36 import SURFACES, parse_log, summarize


def check_activity(surface, log_path, episode_id, body):
    if surface not in SURFACES:
        raise ValueError('unknown declared agent surface')
    if surface != 'chatgpt-agent':
        return {'policy_applies': None if surface == 'unknown' else False, 'surface_declared': surface,
                'applicability': 'UNKNOWN' if surface == 'unknown' else 'EXEMPT'}, []
    if not log_path or not episode_id:
        return {'policy_applies': True, 'surface_declared': surface}, ['ChatGPT agent activity log and episode ID required']
    path = Path(log_path)
    if path.is_symlink():
        raise ValueError('activity log must not be a symlink')
    raw = path.read_bytes()
    summary = summarize(parse_log(raw))
    digest = hashlib.sha256(raw).hexdigest()
    gaps = []
    if summary['surface'] != surface or summary['session_id'] != episode_id:
        gaps.append('activity surface or episode differs from declared agent episode')
    if summary['buddy_suggestion_due']:
        gaps.append('BuddyRunner suggestion is due; suggest it and retain the actual reference')
    lines = [x for x in body.splitlines() if x.startswith('Issue reconciliation: ')]
    binding = re.escape(f'activity episode {episode_id}; activity sha256 {digest}')
    if len(lines) != 1 or not re.search(r'(?:^|; )' + binding + r'(?:;|$)', lines[0]):
        gaps.append('native self-check must bind the retained activity episode and exact log bytes')
    return {**summary, 'log_sha256': digest, 'surface_declared': surface}, gaps
