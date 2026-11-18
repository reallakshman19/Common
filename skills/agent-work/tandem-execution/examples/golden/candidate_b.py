"""Synthetic C2: B preserves A's correction and separates dismissal from saved state."""
def merge(events):
    return list({e['occurrence_id']: e for e in events}.values())

def dismiss(saved, suggestions, target):
    return (list(saved),
            [s for s in suggestions if s['occurrence_id'] != target['occurrence_id']])
