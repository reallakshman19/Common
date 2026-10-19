"""Standalone-only pre-DONE checks over native A14 v1 and local witnesses.

No provider access, dispatch, acceptance, scoring or coordinator behavior.
A successful result checks declarations/bytes, never the truth of the argument.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import re

from a13_git_v36 import git
from criteria_v36 import parse_criteria_v1
from decompose_v36 import validate_plan
from lifecycle_v36 import ISSUE_REF, label_mode, validate_label
from selfcheck_v36 import parse_self_check

GROUPS = ('SC_INTENT', 'SC_INPUTS', 'SC_SCOPE', 'SC_FLOW', 'SC_TESTS',
          'SC_CODE', 'SC_PENDING', 'SC_FRESHNESS')
SHA256 = re.compile(r'[0-9a-f]{64}')
CANDIDATE = re.compile(r'([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([0-9a-f]{40})')
ROW = re.compile(
    r'Done-when: (?P<id>SC_[A-Z]+|(?:AC|K|J)[1-9]\d*) → '
    r'(?P<state>MET|NOT_MET|NOT_RUN|UNKNOWN|NOT_APPLICABLE)'
    r'(?: ; reason: (?P<reason>[^;\n]+))? ; proof: (?P<path>[^;\n]+)'
    r' ; sha256: (?P<digest>[0-9a-f]{64}|NOT_AVAILABLE)')
FIELDS = ('Basis', 'Scope', 'A13', 'A13 review', 'Tests',
          'Issue reconciliation', 'Pending', 'Proposed claim', 'Native report')
LIMITS = [
    'Owner confirmation and semantic sufficiency of criteria/evidence need source review.',
    'Local HEAD is checked; remote PR freshness, publication and actual child binding are not attested.',
    'Tests, UI behavior, engineering correctness and reviewer independence are not inferred from hashes.',
    'No Owner acceptance, merge, dispatch or release authority is granted.',
]


def require_standalone(label):
    """Reject other modes before reading Git, witnesses or constructing providers."""
    if label_mode(label) != 'standalone':
        raise ValueError('this helper requires explicit standalone mode')
    return validate_label(label)


def identity_gaps(label, plan, task_id, issue_ref, candidate):
    validate_plan(plan, label)
    gaps = []
    tasks = [t for t in plan['tasks'] if t['task_id'] == task_id]
    if len(tasks) != 1:
        gaps.append('task is not uniquely selected in the approved plan')
    repo = plan['parent'].split('#')[0]
    if (not ISSUE_REF.fullmatch(issue_ref) or issue_ref.split('#')[0] != repo
            or issue_ref == plan['parent']):
        gaps.append('child must be a declared same-repository issue distinct from parent')
    hit = CANDIDATE.fullmatch(candidate)
    if not hit or hit[1] != repo:
        gaps.append('candidate must bind the selected repository and exact SHA')
    return gaps


def local_candidate_gaps(repo, candidate):
    """Current local candidate only; no claim that a remote head was inspected."""
    try:
        top = Path(git(repo, 'rev-parse', '--show-toplevel').decode().strip()).resolve()
        head = git(repo, 'rev-parse', 'HEAD').decode().strip()
        dirty = git(repo, 'diff', '--name-only', 'HEAD').strip()
    except ValueError:
        return ['local Git candidate unavailable']
    gaps = []
    if top != Path(repo).resolve():
        gaps.append('--repo must name the repository root')
    if candidate.rsplit('@', 1)[-1] != head:
        gaps.append('local HEAD differs from assessed candidate')
    if dirty:
        gaps.append('tracked worktree differs from candidate')
    return gaps


def native_check(body, task_id, issue_ref, candidate):
    """Retain native v1 parsing and its character/format/provenance constraints."""
    owner = issue_ref.split('/')[0]
    comment = {'id': 1, 'body': body, 'user': {'login': owner}}
    check = parse_self_check(comment, task_id, owner, issue_ref)
    if not check:
        return None, ['native SELF-CHECK v1 for selected task is missing']
    gaps = []
    if check['status'] != 'PARSED' or check['nonconformant']:
        gaps.append('native self-check is not template-conformant')
    if check['candidate'] != candidate:
        gaps.append('self-check candidate identity mismatch')
    if check['claim'] != 'DONE':
        gaps.append('report is not a proposed bounded-task DONE claim')
    if any(p['prevents_done'] for p in check['pending']):
        gaps.append('pending obligation prevents task DONE')
    if 'Pending: none' in body and check['pending']:
        gaps.append('Pending none contradicts listed obligations')
    return check, gaps


def basis_gaps(lines, label, plan, criteria, criteria_sha256, candidate):
    basis = (f"Basis: plan {plan['plan_version']}; label {label['work']}@"
             f"{label['version']}:{label['label_sha']}; criteria sha256 {criteria_sha256}; "
             f"candidate {candidate}; source {criteria['source']}")
    gaps = []
    if lines.count(basis) != 1:
        gaps.append('Basis must bind exact plan, label, frozen criteria bytes, source and candidate')
    for field in FIELDS:
        matches = [x for x in lines if x.startswith(field + ': ')]
        if not matches or (field != 'Pending' and len(matches) != 1):
            gaps.append('missing or repeated native field: ' + field)
    return gaps


def witness(path_text, digest, root):
    """Read only a regular file inside the selected evidence directory."""
    relative = Path(path_text)
    if (relative.is_absolute() or '..' in relative.parts or '\\' in path_text
            or ':' in path_text or not SHA256.fullmatch(digest)):
        return False
    try:
        root = Path(root).resolve(strict=True)
        target = (root / relative).resolve(strict=True)
        target.relative_to(root)
        if not target.is_file():
            return False
        value = hashlib.sha256()
        with target.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                value.update(chunk)
        return value.hexdigest() == digest
    except (OSError, ValueError, RuntimeError):
        return False


def rows_gaps(lines, expected, evidence_root):
    rows, gaps, verified = {}, [], 0
    for line in (x for x in lines if x.startswith('Done-when: ')):
        row = ROW.fullmatch(line)
        if not row:
            gaps.append('done-when row lacks an exact ID, state or witness binding')
            continue
        key = row['id']
        if key in rows:
            gaps.append('duplicate done-when ID: ' + key)
        rows[key] = row['state']
        if row['state'] != 'MET':
            gaps.append(key + ' remains ' + row['state'])
        if witness(row['path'], row['digest'], evidence_root):
            verified += 1
        else:
            gaps.append(key + ' witness missing, unsafe or hash mismatch')
    for key in sorted(expected - set(rows)):
        gaps.append('missing done-when ID: ' + key)
    for key in sorted(set(rows) - expected):
        gaps.append('unexpected done-when ID: ' + key)
    return gaps, verified


def check_done(*, label, plan, task_id, issue_ref, candidate, criteria_text,
               criteria_sha256, body, repo, evidence_root):
    """Verify completion declarations. Calling it never publishes or approves anything."""
    label = require_standalone(label)
    gaps = identity_gaps(label, plan, task_id, issue_ref, candidate)
    criteria = parse_criteria_v1(criteria_text)
    if criteria['version'] != label['work']:
        gaps.append('frozen criteria work identity differs from selected label')
    if (not SHA256.fullmatch(criteria_sha256) or
            hashlib.sha256(criteria_text.encode('utf-8')).hexdigest() != criteria_sha256):
        gaps.append('frozen criteria bytes differ from supplied confirmed digest')
    lines = [x.rstrip() for x in body.splitlines() if x.strip()]
    _, problems = native_check(body, task_id, issue_ref, candidate)
    gaps.extend(problems)
    gaps.extend(basis_gaps(lines, label, plan, criteria, criteria_sha256, candidate))
    gaps.extend(local_candidate_gaps(repo, candidate))
    problems, verified = rows_gaps(lines, set(GROUPS) | set(criteria['criteria']), evidence_root)
    gaps.extend(problems)
    return {'mode': 'standalone', 'task_id': task_id, 'candidate': candidate,
            'issue_ref': issue_ref, 'plan': plan['plan_version'],
            'label': {k: label[k] for k in ('work', 'version', 'label_sha')},
            'self_check_sha256': hashlib.sha256(body.encode('utf-8')).hexdigest(),
            'criteria_sha256': criteria_sha256, 'declaration_consistent': not gaps,
            'witnesses_checked': verified, 'gaps': gaps,
            'verification': 'STRUCTURE_AND_LOCAL_BYTES_ONLY',
            'owner_accepted': False, 'independent_review_established': False,
            'limits': list(LIMITS)}
