# Supplied candidate C17 entrypoint fragment, read-only.
from legacy import inspect_sync


def on_inspect(originals):
    return inspect_sync(originals)
