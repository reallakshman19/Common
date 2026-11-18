"""Synthetic B1: independently fixes dismissal from C0, without importing A1."""
def merge(events):
    return list({e['url']: e for e in events}.values())

def dismiss(saved, suggestions, target):
    return (list(saved),
            [s for s in suggestions if s['occurrence_id'] != target['occurrence_id']])
