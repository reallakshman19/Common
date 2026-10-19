"""Synthetic B2 persistence operation; upstream validation is not represented."""


def save_drafts(workspace, model, edits):
    workspace[model] = {key: value for key, value in edits.items() if value}


def load_drafts(workspace, model):
    return dict(workspace.get(model, {}))
