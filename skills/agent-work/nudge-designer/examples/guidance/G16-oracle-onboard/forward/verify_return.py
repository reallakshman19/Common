"""Parent-defined contract checks, retained separately from the issued task."""
import importlib.util
from pathlib import Path
import sys


def check(path):
    spec = importlib.util.spec_from_file_location('candidate', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    untouched = {'mass': 23}
    accepted = {'part': 'explicitly accepted elsewhere'}
    workspace = {'other-model': dict(untouched), 'accepted': dict(accepted)}
    edits = {'zero': 0.0, 'positive': 4.25, 'unset': None}
    mod.save_drafts(workspace, 'model-A', edits)
    got = mod.load_drafts(workspace, 'model-A')
    assert got == {'zero': 0.0, 'positive': 4.25}, got
    assert 'absent' not in got and 'unset' not in got
    assert workspace['other-model'] == untouched
    assert workspace['accepted'] == accepted
    assert edits == {'zero': 0.0, 'positive': 4.25, 'unset': None}
    got['zero'] = 99
    assert mod.load_drafts(workspace, 'model-A')['zero'] == 0
    assert mod.load_drafts(workspace, 'unknown') == {}
    assert 'unknown' not in workspace
    mod.save_drafts(workspace, 'model-A', {'replacement': 7})
    assert mod.load_drafts(workspace, 'model-A') == {'replacement': 7}
    print('PASS: zero/nonzero, None/absence, model and acceptance isolation, '
          'input/copy isolation, unknown model and replacement semantics')


if __name__ == '__main__':
    check(Path(sys.argv[1]))
